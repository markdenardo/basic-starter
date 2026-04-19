#!/usr/bin/env python3
"""basicc — compile a simple BASIC dialect to C99.

Usage:
    basicc.py source.bas             # print C to stdout
    basicc.py source.bas -o out.c    # write C file
    basicc.py source.bas -r          # compile and run (requires gcc)

Supported syntax:
    DIM x AS INTEGER | FLOAT | STRING
    LET x = expr  /  x = expr
    PRINT expr [; expr ...] [;]      trailing ; suppresses newline
    INPUT ["prompt";] var
    IF expr THEN ... [ELSE ...] END IF   (block form)
    IF expr THEN stmt [ELSE stmt]        (single-line form)
    FOR var = expr TO expr [STEP expr] ... NEXT [var]
    WHILE expr ... WEND
    GOTO linenum
    GOSUB linenum ... RETURN
    DATA val [, val ...]  /  READ var [, var ...]  /  RESTORE
    END  /  REM ...
    Line numbers are optional; required only for GOTO/GOSUB targets.
"""

import re, sys, os, subprocess, tempfile
from dataclasses import dataclass, field
from typing import Any, Optional

# ══════════════════════════════════════════════════════════════════════════════
# Tokens
# ══════════════════════════════════════════════════════════════════════════════

TT_NUM = 'NUM'; TT_STR = 'STR'; TT_IDENT = 'IDENT'
TT_KW  = 'KW';  TT_OP  = 'OP';  TT_NL    = 'NL'; TT_EOF = 'EOF'

KEYWORDS = {
    'LET','PRINT','INPUT','FOR','TO','STEP','NEXT','IF','THEN','ELSE',
    'END','WHILE','WEND','DIM','AS','INTEGER','FLOAT','STRING','REM',
    'AND','OR','NOT','MOD','GOTO','GOSUB','RETURN','FUNCTION','SUB',
    'READ','DATA','RESTORE',
}

@dataclass
class Token:
    type: str
    value: Any
    line: int

def tokenize(src: str) -> list:
    tokens, line, i = [], 1, 0
    src = src.replace('\r\n', '\n').replace('\r', '\n')
    while i < len(src):
        c = src[i]
        if c == '\n':
            if not tokens or tokens[-1].type != TT_NL:
                tokens.append(Token(TT_NL, '\n', line))
            line += 1; i += 1; continue
        if c in ' \t':
            i += 1; continue
        # line continuation
        if c == '_' and i+1 < len(src) and src[i+1] == '\n':
            i += 2; line += 1; continue
        # string literal
        if c == '"':
            j = i + 1
            while j < len(src) and src[j] != '"' and src[j] != '\n':
                j += 1
            tokens.append(Token(TT_STR, src[i+1:j], line))
            i = j + 1; continue
        # number
        m = re.match(r'\d+\.?\d*([eE][+-]?\d+)?', src[i:])
        if m:
            raw = m.group()
            val = float(raw) if ('.' in raw or 'e' in raw.lower()) else int(raw)
            tokens.append(Token(TT_NUM, val, line))
            i += len(raw); continue
        # identifier / keyword
        m = re.match(r'[A-Za-z_][A-Za-z0-9_]*[\$%]?', src[i:])
        if m:
            word = m.group(); up = word.upper()
            if up in KEYWORDS:
                if up == 'REM':
                    j = i + len(word)
                    while j < len(src) and src[j] != '\n': j += 1
                    tokens.append(Token(TT_NL, '\n', line))
                    i = j
                else:
                    tokens.append(Token(TT_KW, up, line))
                    i += len(word)
            else:
                tokens.append(Token(TT_IDENT, word, line))
                i += len(word)
            continue
        # two-char operators
        if i+1 < len(src) and src[i:i+2] in ('<>', '<=', '>='):
            tokens.append(Token(TT_OP, src[i:i+2], line)); i += 2; continue
        # single-char
        if c in '+-*/\\^=<>(),;:':
            tokens.append(Token(TT_OP, c, line)); i += 1; continue
        raise SyntaxError(f'line {line}: unexpected character {c!r}')
    tokens.append(Token(TT_EOF, None, line))
    return tokens

# ══════════════════════════════════════════════════════════════════════════════
# AST
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Num:   value: Any
@dataclass
class Str:   value: str
@dataclass
class Var:   name: str
@dataclass
class BinOp: op: str; left: Any; right: Any
@dataclass
class UnOp:  op: str; operand: Any
@dataclass
class Call:  name: str; args: list

@dataclass
class LetStmt:   var: str; expr: Any
@dataclass
class PrintStmt: items: list; newline: bool = True
@dataclass
class InputStmt: prompt: Optional[str]; var: str
@dataclass
class IfStmt:    cond: Any; then_body: list; else_body: list
@dataclass
class ForStmt:   var: str; start: Any; stop: Any; step: Any; body: list
@dataclass
class WhileStmt: cond: Any; body: list
@dataclass
class GotoStmt:  target: int
@dataclass
class GosubStmt: target: int
@dataclass
class ReturnStmt: pass
@dataclass
class EndStmt:    pass
@dataclass
class DimStmt:   var: str; typ: str
@dataclass
class LabelStmt:   number: int        # line-number label for GOTO/GOSUB
@dataclass
class ReadStmt:    vars: list          # READ var [, var ...]
@dataclass
class DataStmt:    values: list        # DATA val [, val ...] (Num or Str nodes)
@dataclass
class RestoreStmt: pass

@dataclass
class Program:
    stmts: list

# ══════════════════════════════════════════════════════════════════════════════
# Parser
# ══════════════════════════════════════════════════════════════════════════════

class Parser:
    def __init__(self, tokens):
        self.tok = tokens
        self.pos = 0

    def peek(self):        return self.tok[self.pos]
    def at_end(self):      return self.peek().type == TT_EOF

    def consume(self, typ=None, val=None):
        t = self.tok[self.pos]
        if typ and t.type != typ:
            raise SyntaxError(f'line {t.line}: expected {typ}, got {t.type} ({t.value!r})')
        if val is not None and t.value != val:
            raise SyntaxError(f'line {t.line}: expected {val!r}, got {t.value!r}')
        self.pos += 1
        return t

    def skip_nl(self):
        while self.peek().type == TT_NL: self.pos += 1

    def is_kw(self, *words): return self.peek().type == TT_KW and self.peek().value in words
    def is_op(self, *ops):   return self.peek().type == TT_OP and self.peek().value in ops

    def is_kw_ahead(self, *words):
        """True if the next keyword (skipping an optional leading line number) is one of words."""
        offset = 1 if (self.tok[self.pos].type == TT_NUM and isinstance(self.tok[self.pos].value, int)) else 0
        t = self.tok[self.pos + offset] if self.pos + offset < len(self.tok) else None
        return t is not None and t.type == TT_KW and t.value in words

    def skip_opt_linenum(self):
        if self.peek().type == TT_NUM and isinstance(self.peek().value, int):
            self.consume()

    # ── top-level ─────────────────────────────────────────────────────────────

    def parse(self):
        self.skip_nl()
        stmts = []
        while not self.at_end():
            stmts.extend(self.parse_line())
            self.skip_nl()
        return Program(stmts)

    def parse_line(self):
        # Optional leading line number
        linenum = None
        if self.peek().type == TT_NUM and isinstance(self.peek().value, int):
            linenum = self.consume().value

        stmts = []
        if linenum is not None:
            stmts.append(LabelStmt(linenum))

        if self.peek().type not in (TT_NL, TT_EOF):
            stmts.append(self.parse_stmt())
            while self.is_op(':'):
                self.consume()
                if self.peek().type not in (TT_NL, TT_EOF):
                    stmts.append(self.parse_stmt())

        if self.peek().type == TT_NL:
            self.consume()
        return stmts

    def parse_stmt(self):
        t = self.peek()
        if t.type == TT_KW:
            kw = t.value
            if kw == 'LET':   self.consume(); return self.parse_assign()
            if kw == 'PRINT': self.consume(); return self.parse_print()
            if kw == 'INPUT': self.consume(); return self.parse_input()
            if kw == 'FOR':   return self.parse_for()
            if kw == 'IF':    return self.parse_if()
            if kw == 'WHILE': return self.parse_while()
            if kw == 'DIM':   return self.parse_dim()
            if kw == 'GOTO':
                self.consume()
                return GotoStmt(self.consume(TT_NUM).value)
            if kw == 'GOSUB':
                self.consume()
                return GosubStmt(self.consume(TT_NUM).value)
            if kw == 'RETURN': self.consume(); return ReturnStmt()
            if kw == 'END':
                self.consume()
                if self.is_kw('IF', 'SUB', 'FUNCTION'): self.consume()
                return EndStmt()
            if kw in ('NEXT', 'WEND'): self.consume(); return None
            if kw == 'READ':
                self.consume()
                vs = [self.consume(TT_IDENT).value]
                while self.is_op(','): self.consume(); vs.append(self.consume(TT_IDENT).value)
                return ReadStmt(vs)
            if kw == 'DATA':
                self.consume()
                vals = [self.parse_primary()]
                while self.is_op(','): self.consume(); vals.append(self.parse_primary())
                return DataStmt(vals)
            if kw == 'RESTORE':
                self.consume(); return RestoreStmt()

        # Assignment without LET
        if t.type == TT_IDENT:
            nxt = self.tok[self.pos+1] if self.pos+1 < len(self.tok) else None
            if nxt and nxt.type == TT_OP and nxt.value == '=':
                return self.parse_assign()

        return LetStmt('__discard__', self.parse_expr())

    def parse_assign(self):
        var = self.consume(TT_IDENT).value
        self.consume(TT_OP, '=')
        return LetStmt(var, self.parse_expr())

    def parse_print(self):
        items, newline = [], True
        while self.peek().type not in (TT_NL, TT_EOF) and not self.is_op(':') and not self.is_kw('ELSE'):
            items.append(self.parse_expr())
            if self.is_op(';', ','):
                sep = self.consume().value
                if self.peek().type in (TT_NL, TT_EOF) or self.is_op(':'):
                    newline = False; break
        return PrintStmt(items, newline)

    def parse_input(self):
        prompt = None
        if self.peek().type == TT_STR:
            prompt = self.consume().value
            if self.is_op(';', ','): self.consume()
        var = self.consume(TT_IDENT).value
        return InputStmt(prompt, var)

    def parse_for(self):
        self.consume(TT_KW, 'FOR')
        var = self.consume(TT_IDENT).value
        self.consume(TT_OP, '=')
        start = self.parse_expr()
        self.consume(TT_KW, 'TO')
        stop = self.parse_expr()
        step = None
        if self.is_kw('STEP'): self.consume(); step = self.parse_expr()
        if self.peek().type == TT_NL: self.consume()
        body = self.parse_block('NEXT')
        return ForStmt(var, start, stop, step, body)

    def parse_if(self):
        self.consume(TT_KW, 'IF')
        cond = self.parse_expr()
        self.consume(TT_KW, 'THEN')
        # single-line
        if self.peek().type != TT_NL:
            then = [self.parse_stmt()]
            els = []
            if self.is_kw('ELSE'): self.consume(); els = [self.parse_stmt()]
            return IfStmt(cond, then, els)
        # block form
        self.consume(); self.skip_nl()
        then_body, else_body = [], []
        target = then_body
        while not self.at_end():
            if self.is_kw_ahead('ELSE'):
                self.skip_opt_linenum(); self.consume()
                if self.peek().type == TT_NL: self.consume()
                self.skip_nl()
                target = else_body; continue
            if self.is_kw_ahead('END'):
                self.skip_opt_linenum(); self.consume()
                if self.is_kw('IF'): self.consume()
                break
            target.extend(self.parse_line())
            self.skip_nl()
        return IfStmt(cond, then_body, else_body)

    def parse_while(self):
        self.consume(TT_KW, 'WHILE')
        cond = self.parse_expr()
        if self.peek().type == TT_NL: self.consume()
        body = self.parse_block('WEND')
        return WhileStmt(cond, body)

    def parse_dim(self):
        self.consume(TT_KW, 'DIM')
        var = self.consume(TT_IDENT).value
        typ = 'FLOAT'
        if self.is_kw('AS'):
            self.consume()
            typ = self.consume(TT_KW).value
        return DimStmt(var, typ)

    def parse_block(self, term):
        stmts = []
        self.skip_nl()
        while not self.at_end():
            if self.is_kw_ahead(term):
                self.skip_opt_linenum(); self.consume()
                if term == 'NEXT' and self.peek().type == TT_IDENT: self.consume()
                break
            stmts.extend(self.parse_line())
            self.skip_nl()
        return stmts

    # ── expressions ───────────────────────────────────────────────────────────

    def parse_expr(self):   return self.parse_or()
    def parse_or(self):
        n = self.parse_and()
        while self.is_kw('OR'): self.consume(); n = BinOp('OR', n, self.parse_and())
        return n
    def parse_and(self):
        n = self.parse_not()
        while self.is_kw('AND'): self.consume(); n = BinOp('AND', n, self.parse_not())
        return n
    def parse_not(self):
        if self.is_kw('NOT'): self.consume(); return UnOp('NOT', self.parse_not())
        return self.parse_cmp()
    def parse_cmp(self):
        n = self.parse_add()
        if self.is_op('=','<>','<','>','<=','>='):
            op = self.consume().value; n = BinOp(op, n, self.parse_add())
        return n
    def parse_add(self):
        n = self.parse_mul()
        while self.is_op('+', '-'): op = self.consume().value; n = BinOp(op, n, self.parse_mul())
        return n
    def parse_mul(self):
        n = self.parse_pow()
        while self.is_op('*','/','\\') or self.is_kw('MOD'):
            op = self.consume().value; n = BinOp(op, n, self.parse_pow())
        return n
    def parse_pow(self):
        n = self.parse_unary()
        if self.is_op('^'): self.consume(); n = BinOp('^', n, self.parse_pow())
        return n
    def parse_unary(self):
        if self.is_op('-'): self.consume(); return UnOp('-', self.parse_unary())
        if self.is_op('+'): self.consume(); return self.parse_unary()
        return self.parse_primary()
    def parse_primary(self):
        t = self.peek()
        if t.type == TT_NUM: self.consume(); return Num(t.value)
        if t.type == TT_STR: self.consume(); return Str(t.value)
        if t.type == TT_IDENT:
            self.consume()
            if self.is_op('('):
                self.consume()
                args = []
                if not self.is_op(')'):
                    args.append(self.parse_expr())
                    while self.is_op(','): self.consume(); args.append(self.parse_expr())
                self.consume(TT_OP, ')')
                return Call(t.value, args)
            return Var(t.value)
        if self.is_op('('):
            self.consume(); n = self.parse_expr(); self.consume(TT_OP, ')'); return n
        raise SyntaxError(f'line {t.line}: unexpected token {t.value!r}')

# ══════════════════════════════════════════════════════════════════════════════
# Code Generator  (→ C99)
# ══════════════════════════════════════════════════════════════════════════════

BUILTIN_FN = {
    'SIN':'sin','COS':'cos','TAN':'tan','SQR':'sqrt','ABS':'fabs',
    'INT':'floor','SGN':'_bas_sgn','LOG':'log','EXP':'exp',
    'ATN':'atan','RND':'_bas_rnd','LEN':'_bas_len',
    'LEFT$':'_bas_left','RIGHT$':'_bas_right','MID$':'_bas_mid',
    'STR$':'_bas_str','VAL':'atof','CHR$':'_bas_chr','ASC':'_bas_asc',
}

class CodeGen:
    def __init__(self):
        self.out   = []        # final lines
        self.body  = []        # main() body lines
        self.ind   = 1         # current indent level inside main()
        self.vars  = {}        # name -> c_type
        self.needs_input_buf = False
        self.has_gosub = False
        self.data_items = []   # (value_str, is_string) collected from DATA stmts

    # ── helpers ───────────────────────────────────────────────────────────────

    def emit(self, s=''):
        self.body.append('    ' * self.ind + s)

    def ctype(self, name):
        if name.endswith('$'): return 'const char*'
        if name.endswith('%'): return 'int'
        return 'double'

    def cname(self, name):
        return name.replace('$', '_s').replace('%', '_i')

    def declare(self, name, typ=None):
        if name in self.vars or name == '__discard__': return
        self.vars[name] = typ or self.ctype(name)

    # ── expressions ───────────────────────────────────────────────────────────

    def expr(self, node) -> str:
        if isinstance(node, Num):
            if isinstance(node.value, int): return f'{node.value}.0'
            return repr(float(node.value))
        if isinstance(node, Str):
            esc = node.value.replace('\\','\\\\').replace('"','\\"')
            return f'"{esc}"'
        if isinstance(node, Var):
            self.declare(node.name)
            return self.cname(node.name)
        if isinstance(node, Call):
            fn = BUILTIN_FN.get(node.name.upper(), self.cname(node.name))
            args = ', '.join(self.expr(a) for a in node.args)
            return f'{fn}({args})'
        if isinstance(node, UnOp):
            op = {'NOT': '!', '-': '-'}[node.op]
            return f'({op}{self.expr(node.operand)})'
        if isinstance(node, BinOp):
            l, r = self.expr(node.left), self.expr(node.right)
            if node.op == '^':   return f'pow({l}, {r})'
            if node.op == 'MOD': return f'fmod({l}, {r})'
            if node.op == '\\':  return f'(double)((long long)({l}) / (long long)({r}))'
            table = {'=':'==','<>':'!=','AND':'&&','OR':'||',
                     '+':'+','-':'-','*':'*','/':'/',
                     '<':'<','>':'>','<=':'<=','>=':'>='}
            return f'({l} {table[node.op]} {r})'
        raise ValueError(f'unknown node: {node}')

    # ── statements ────────────────────────────────────────────────────────────

    def stmts(self, lst):
        for s in lst:
            if s is not None: self.stmt(s)

    def stmt(self, node):
        if isinstance(node, LabelStmt):
            # Labels must be at indent 1 (labels can't be indented in C)
            self.body.append(f'    L{node.number}:;')

        elif isinstance(node, LetStmt):
            if node.var == '__discard__':
                self.emit(f'{self.expr(node.expr)};'); return
            self.declare(node.var)
            self.emit(f'{self.cname(node.var)} = {self.expr(node.expr)};')

        elif isinstance(node, PrintStmt):
            for item in node.items:
                is_str = (isinstance(item, Str) or
                          (isinstance(item, Var) and item.name.endswith('$')) or
                          (isinstance(item, Call) and item.name.upper().endswith('$')))
                if is_str:
                    self.emit(f'printf("%s", {self.expr(item)});')
                else:
                    self.emit(f'printf("%g ", (double)({self.expr(item)}));')
            if node.newline:
                self.emit('printf("\\n");')

        elif isinstance(node, InputStmt):
            self.needs_input_buf = True
            self.declare(node.var)
            cn = self.cname(node.var)
            if node.prompt: self.emit(f'printf("{node.prompt}"); fflush(stdout);')
            if self.vars.get(node.var) == 'const char*':
                self.emit(f'scanf("%255s", _ibuf); {cn} = _ibuf;')
            else:
                self.emit(f'scanf("%lf", &{cn});')

        elif isinstance(node, IfStmt):
            self.emit(f'if ({self.expr(node.cond)}) {{')
            self.ind += 1; self.stmts(node.then_body); self.ind -= 1
            if node.else_body:
                self.emit('} else {')
                self.ind += 1; self.stmts(node.else_body); self.ind -= 1
            self.emit('}')

        elif isinstance(node, ForStmt):
            self.declare(node.var)
            cv = self.cname(node.var)
            start = self.expr(node.start)
            stop  = self.expr(node.stop)
            step  = self.expr(node.step) if node.step else '1.0'
            sv = f'_step_{cv}'
            self.emit(f'{{ double {sv} = {step}; {cv} = {start};')
            self.emit(f'while (({sv}>0 && {cv}<={stop}) || ({sv}<0 && {cv}>={stop})) {{')
            self.ind += 1; self.stmts(node.body)
            self.emit(f'{cv} += {sv};')
            self.ind -= 1; self.emit('} }')

        elif isinstance(node, WhileStmt):
            self.emit(f'while ({self.expr(node.cond)}) {{')
            self.ind += 1; self.stmts(node.body); self.ind -= 1
            self.emit('}')

        elif isinstance(node, GotoStmt):
            self.emit(f'goto L{node.target};')

        elif isinstance(node, GosubStmt):
            self.has_gosub = True
            self.emit(f'_ret[_rsp++] = &&_after_{node.target}_{id(node)};')
            self.emit(f'goto L{node.target};')
            self.body.append(f'    _after_{node.target}_{id(node)}:;')

        elif isinstance(node, ReturnStmt):
            self.has_gosub = True
            self.emit('goto *_ret[--_rsp];')

        elif isinstance(node, DimStmt):
            tmap = {'INTEGER':'int','FLOAT':'double','STRING':'const char*'}
            self.declare(node.var, tmap.get(node.typ, 'double'))

        elif isinstance(node, EndStmt):
            self.emit('return 0;')

        elif isinstance(node, DataStmt):
            pass  # values collected during scan; no runtime code emitted

        elif isinstance(node, ReadStmt):
            for var in node.vars:
                self.declare(var)
                cn = self.cname(var)
                typ = self.vars.get(var, self.ctype(var))
                if typ == 'const char*':
                    self.emit(f'{cn} = _DATA[_dp % _DATA_LEN]; _dp++;')
                else:
                    self.emit(f'{cn} = atof(_DATA[_dp % _DATA_LEN]); _dp++;')

        elif isinstance(node, RestoreStmt):
            self.emit('_dp = 0;')

    # ── pre-scan ──────────────────────────────────────────────────────────────

    def scan(self, stmts):
        for s in stmts:
            if s is None: continue
            if isinstance(s, LetStmt) and s.var != '__discard__':
                self.declare(s.var); self._scan_expr(s.expr)
            elif isinstance(s, DimStmt):
                tmap = {'INTEGER':'int','FLOAT':'double','STRING':'const char*'}
                self.declare(s.var, tmap.get(s.typ, 'double'))
            elif isinstance(s, (PrintStmt,)):
                for i in s.items: self._scan_expr(i)
            elif isinstance(s, InputStmt): self.declare(s.var)
            elif isinstance(s, ForStmt):
                self.declare(s.var)
                for e in [s.start, s.stop, s.step]:
                    if e: self._scan_expr(e)
                self.scan(s.body)
            elif isinstance(s, IfStmt):
                self._scan_expr(s.cond)
                self.scan(s.then_body); self.scan(s.else_body)
            elif isinstance(s, WhileStmt):
                self._scan_expr(s.cond); self.scan(s.body)
            elif isinstance(s, DataStmt):
                for v in s.values:
                    if isinstance(v, Str): self.data_items.append((v.value, True))
                    else: self.data_items.append((repr(float(v.value if isinstance(v.value, float) else int(v.value))), False))
            elif isinstance(s, ReadStmt):
                for var in s.vars: self.declare(var)

    def _scan_expr(self, n):
        if isinstance(n, Var): self.declare(n.name)
        elif isinstance(n, BinOp): self._scan_expr(n.left); self._scan_expr(n.right)
        elif isinstance(n, UnOp): self._scan_expr(n.operand)
        elif isinstance(n, Call):
            for a in n.args: self._scan_expr(a)

    # ── generate ──────────────────────────────────────────────────────────────

    def generate(self, prog: Program) -> str:
        self.scan(prog.stmts)
        self.stmts(prog.stmts)
        if not self.body or not self.body[-1].strip().startswith('return'):
            self.emit('return 0;')

        header = [
            '#include <stdio.h>',
            '#include <math.h>',
            '#include <stdlib.h>',
            '#include <string.h>',
            '',
            'static double _bas_sgn(double x){return x>0?1:(x<0?-1:0);}',
            'static double _bas_rnd(double x){(void)x;return(double)rand()/RAND_MAX;}',
            'static int    _bas_len(const char*s){return(int)strlen(s);}',
            'static int    _bas_asc(const char*s){return(int)(unsigned char)s[0];}',
            'static const char* _bas_chr(double n){static char b[2];b[0]=(char)(int)n;b[1]=0;return b;}',
            'static const char* _bas_str(double n){static char b[64];snprintf(b,64,"%g",n);return b;}',
            'static const char* _bas_left(const char*s,double n)'
                '{static char b[256];int l=(int)n;strncpy(b,s,l);b[l]=0;return b;}',
            'static const char* _bas_right(const char*s,double n)'
                '{static char b[256];int len=strlen(s),l=(int)n;'
                'strncpy(b,s+(len>l?len-l:0),l);b[l]=0;return b;}',
            'static const char* _bas_mid(const char*s,double pos,double n)'
                '{static char b[256];int p=(int)pos-1;int l=(int)n;'
                'if(p<0)p=0;strncpy(b,s+p,l);b[l]=0;return b;}',
            '',
            'int main(void) {',
        ]

        decls = []
        for name, typ in sorted(self.vars.items()):
            cn = self.cname(name)
            if typ == 'const char*': decls.append(f'    {typ} {cn} = "";')
            elif typ == 'int':       decls.append(f'    {typ} {cn} = 0;')
            else:                    decls.append(f'    {typ} {cn} = 0.0;')
        if self.needs_input_buf:
            decls.append('    char _ibuf[256];')
        if self.has_gosub:
            decls.append('    void* _ret[256]; int _rsp = 0;')
        if self.data_items:
            esc = lambda s: s.replace('\\','\\\\').replace('"','\\"')
            items_str = ', '.join(f'"{esc(v)}"' for v, _ in self.data_items)
            header.insert(-1, f'static const char* _DATA[] = {{{items_str}}};')
            header.insert(-1, f'static int _DATA_LEN = {len(self.data_items)};')
            decls.append('    int _dp = 0;')

        return '\n'.join(header + decls + [''] + self.body + ['}', ''])

# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def compile_file(path: str) -> str:
    with open(path) as f: src = f.read()
    tokens = tokenize(src)
    ast    = Parser(tokens).parse()
    return CodeGen().generate(ast)

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(0)

    src_path  = args[0]
    out_path  = None
    run_mode  = False

    i = 1
    while i < len(args):
        if args[i] == '-o' and i+1 < len(args):
            out_path = args[i+1]; i += 2
        elif args[i] == '-r':
            run_mode = True; i += 1
        else:
            i += 1

    try:
        c_code = compile_file(src_path)
    except (SyntaxError, ValueError) as e:
        print(f'basicc: {e}', file=sys.stderr); sys.exit(1)

    if run_mode:
        with tempfile.NamedTemporaryFile(suffix='.c', delete=False, mode='w') as tf:
            tf.write(c_code); tmp_c = tf.name
        bin_path = tmp_c.replace('.c', '')
        ret = subprocess.run(['gcc', '-O2', '-o', bin_path, tmp_c, '-lm'], capture_output=True, text=True)
        os.unlink(tmp_c)
        if ret.returncode != 0:
            print(ret.stderr, file=sys.stderr); sys.exit(1)
        subprocess.run([bin_path])
        os.unlink(bin_path)
        return

    if out_path:
        with open(out_path, 'w') as f: f.write(c_code)
        print(f'wrote {out_path}')
    else:
        print(c_code, end='')

if __name__ == '__main__':
    main()
