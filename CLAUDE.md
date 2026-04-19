# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projects

Two independent tools share this repo:

1. **Demoscene template** (`src/`) — FreeBASIC demo with scene sequencer and effects
2. **BASIC compiler** (`compiler/`) — Python 3 compiler: BASIC → C99 (zero dependencies)
3. **Reference docs** (`docs/`) — TI-99/4A BASIC one-page guide

---

## Demoscene Template

### Dependency
FreeBASIC compiler (`fbc`). Download from freebasic.net.

### Commands
```bash
make          # compile → ./demo
make run      # compile and launch
```

### Architecture

| File | Role |
|---|---|
| `src/demo.bi` | Shared init: `DemoInit()`, `DemoFlip()`, `DemoShutdown()`, sine LUT, `PIXEL(x,y)` macro |
| `src/effects/plasma.bi` | `Effect_Plasma(t)` — four-wave plasma |
| `src/effects/starfield.bi` | `Effect_Starfield_Init()` + `Effect_Starfield(dt)` — 3D starfield |
| `src/main.bas` | Entry point: `#include`s everything, owns scene table and main loop |

**Scene sequencer**: `scenes()` array maps index → effect ID. `SCENE_DUR` sets seconds per scene. Add a new effect by defining `Sub Effect_Foo(t)` in a `.bi` file, `#include` it, add a `CONST SCENE_FOO`, and append to `scenes()`.

**Pixel buffer**: effects write to `demoPixels` via `PIXEL(x,y)` or row pointers. Canvas is `DEMO_W × DEMO_H` (320×200). `DemoFlip()` stretch-blits at `DEMO_SCALE`× and page-flips.

---

## BASIC Compiler

### Commands
```bash
make test                                          # run test suite (20 tests)
python3 compiler/basicc.py source.bas             # print C to stdout
python3 compiler/basicc.py source.bas -o out.c   # write C file
python3 compiler/basicc.py source.bas -r          # compile and run (needs gcc)
make bas-run FILE=compiler/examples/fibonacci.bas
```

### Supported BASIC syntax
```
DIM x AS INTEGER | FLOAT | STRING
LET x = expr  /  x = expr
PRINT expr [; expr ...] [;]        trailing ; suppresses newline
INPUT ["prompt";] var
IF expr THEN ... [ELSE ...] END IF  (block)
IF expr THEN stmt [ELSE stmt]       (single-line)
FOR var = expr TO expr [STEP expr] ... NEXT [var]
WHILE expr ... WEND
DATA val [, val ...]  /  READ var [, var ...]  /  RESTORE
GOTO linenum  /  GOSUB linenum ... RETURN
END  /  REM comment
```

Variable naming: `name$` → `const char*`, `name%` → `int`, others → `double`.

Built-ins: `SIN COS TAN SQR ABS INT SGN LOG EXP ATN RND LEN LEFT$ RIGHT$ MID$ STR$ VAL CHR$ ASC`.

### Architecture (`compiler/basicc.py` — single file, stdlib only)

| Class | Responsibility |
|---|---|
| `tokenize()` | Regex lexer; strips REM; handles `_` line-continuation; `$`/`%` suffixes |
| `Parser` | Recursive descent; `is_kw_ahead()` for line-number-prefixed block terminators |
| `CodeGen` | Two-pass: `scan()` pre-declares vars and collects `DATA`, then `stmts()` emits C99 |

`DATA/READ`: all `DATA` values are pre-collected into `static const char* _DATA[]`; `READ` calls `atof()` for numeric targets, direct assignment for strings.

`GOSUB/RETURN`: uses GCC/Clang label-as-value (`&&label` / `goto *ptr`) — GCC/Clang only.

Line numbers are optional except as targets for `GOTO`/`GOSUB`.

### Test suite
```bash
make test                                  # run all 20 tests
python3 compiler/tests/run_tests.py t05   # run tests matching pattern
```
Tests live in `compiler/tests/tNN_name.bas` + `tNN_name.expected`. To add a test: write the `.bas` file, run it once with `-r` to verify output, then redirect that output to `.expected`.

Current coverage: PRINT/suppress, arithmetic, variables, IF/ELSE, FOR/NEXT, WHILE, GOSUB, strings, DATA/READ/RESTORE, math functions, logical operators, nested loops, GOTO, float STEP, multi-subroutine, nested IF, compound WHILE, integration.

---

## Reference
`docs/ti_basic_guide.md` — one-page TI-99/4A BASIC cheat sheet (variables, operators, PRINT, INPUT, IF, loops, DATA, strings, math, CALL commands, colours, sound, screen layout).
