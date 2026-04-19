#!/usr/bin/env python3
"""live.py — BASIC live coding tool. Auto-runs on keypress, syntax highlighted, file I/O."""

import os, sys, re, tempfile, subprocess
import tkinter as tk
from tkinter import filedialog

COMPILER = os.path.join(os.path.dirname(__file__), 'compiler', 'basicc.py')
DEBOUNCE_MS = 600

KEYWORDS = [
    'DIM','AS','INTEGER','FLOAT','STRING','LET','PRINT','INPUT',
    'IF','THEN','ELSE','END','FOR','TO','STEP','NEXT','WHILE','WEND',
    'GOTO','GOSUB','RETURN','DATA','READ','RESTORE','REM','AND','OR','NOT','MOD',
]
BUILTINS = [
    'SIN','COS','TAN','SQR','ABS','INT','SGN','LOG','EXP','ATN','RND',
    'LEN','STR\\$','VAL','CHR\\$','ASC','LEFT\\$','RIGHT\\$','MID\\$',
]

KW_RE  = re.compile(r'\b(' + '|'.join(KEYWORDS) + r')\b',  re.IGNORECASE)
BI_RE  = re.compile(r'\b(' + '|'.join(BUILTINS) + r')\b',  re.IGNORECASE)
NUM_RE = re.compile(r'\b\d+(\.\d+)?\b')
STR_RE = re.compile(r'"[^"]*"')
REM_RE = re.compile(r'(^\s*\d*\s*)(REM\b.*)', re.IGNORECASE)
LNO_RE = re.compile(r'^\d+')


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('BASIC Live')
        self.root.configure(bg='#1e1e1e')
        self._file: str | None = None
        self._job: str | None = None

        self._menu()
        self._layout()
        self._tags()
        self.editor.bind('<KeyRelease>', self._on_key)
        for seq in ('<Control-r>', '<Command-r>'):
            self.root.bind(seq, lambda _e: self._run())
        for seq in ('<Control-o>', '<Command-o>'):
            self.root.bind(seq, lambda _e: self._open())
        for seq in ('<Control-s>', '<Command-s>'):
            self.root.bind(seq, lambda _e: self._save())
        for seq in ('<Control-S>', '<Command-S>'):
            self.root.bind(seq, lambda _e: self._save_as())

    # ── Menu ──────────────────────────────────────────────────────────────────

    def _menu(self):
        bar = tk.Menu(self.root)
        fm = tk.Menu(bar, tearoff=0)
        fm.add_command(label='Open…',    command=self._open,    accelerator='Ctrl+O')
        fm.add_command(label='Save',     command=self._save,    accelerator='Ctrl+S')
        fm.add_command(label='Save As…', command=self._save_as, accelerator='Ctrl+Shift+S')
        bar.add_cascade(label='File', menu=fm)
        rm = tk.Menu(bar, tearoff=0)
        rm.add_command(label='Run Now',  command=self._run,     accelerator='Ctrl+R')
        bar.add_cascade(label='Run', menu=rm)
        self.root.config(menu=bar)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _pane(self, col, label_text):
        f = tk.Frame(self.root, bg='#252526')
        f.grid(row=1, column=col, sticky='nsew',
               padx=(8 if col == 0 else 0, 0 if col == 0 else 8), pady=(0, 8))
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)
        lbl = tk.Label(f, text=label_text, anchor='w',
                       font=('Menlo', 11, 'bold'), bg='#252526', fg='#cccccc')
        lbl.grid(row=0, column=0, sticky='w', padx=8, pady=(6, 4))
        return f, lbl

    def _text_widget(self, parent, row, **kw):
        t = tk.Text(parent, wrap='none', font=('Menlo', 13),
                    bg='#1e1e1e', fg='#d4d4d4', insertbackground='white',
                    selectbackground='#264f78', relief='flat',
                    borderwidth=0, padx=10, pady=8, **kw)
        t.grid(row=row, column=0, sticky='nsew')
        sb = tk.Scrollbar(parent, command=t.yview, bg='#3c3c3c', troughcolor='#252526')
        sb.grid(row=row, column=1, sticky='ns')
        t.configure(yscrollcommand=sb.set)
        return t

    def _layout(self):
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

        # Toolbar row
        toolbar = tk.Frame(self.root, bg='#333333', height=36)
        toolbar.grid(row=0, column=0, columnspan=2, sticky='ew')
        toolbar.grid_propagate(False)
        tk.Label(toolbar, text='BASIC Live', font=('Menlo', 12, 'bold'),
                 bg='#333333', fg='#ffffff').pack(side='left', padx=12, pady=6)
        tk.Button(toolbar, text='▶  Run', command=self._run,
                  font=('Menlo', 11), bg='#0e639c', fg='white',
                  activebackground='#1177bb', activeforeground='white',
                  relief='flat', padx=10, pady=2).pack(side='right', padx=8, pady=4)

        # Separator between panes
        sep = tk.Frame(self.root, bg='#3c3c3c', width=1)
        sep.grid(row=1, column=0, columnspan=2, sticky='ns',
                 padx=(self.root.winfo_reqwidth() // 2, 0))

        ef, _   = self._pane(0, 'BASIC — write code here')
        of, lbl = self._pane(1, 'Output')
        self._out_label = lbl

        self.editor = self._text_widget(ef, 1, undo=True)
        self.output = self._text_widget(of, 1, state='disabled')
        self.output.configure(fg='#9cdcfe')
        self.root.geometry('1200x740')

        # Pre-load fibonacci example
        example = open(os.path.join(os.path.dirname(__file__),
                       'compiler', 'examples', 'fibonacci.bas')).read()
        self.editor.insert('1.0', example)
        self._highlight()
        self.root.after(100, self._run)

    # ── Syntax highlighting ───────────────────────────────────────────────────

    def _tags(self):
        self.editor.tag_configure('kw',      foreground='#569cd6')
        self.editor.tag_configure('builtin', foreground='#dcdcaa')
        self.editor.tag_configure('string',  foreground='#ce9178')
        self.editor.tag_configure('comment', foreground='#6a9955', font=('Menlo', 13, 'italic'))
        self.editor.tag_configure('number',  foreground='#b5cea8')
        self.editor.tag_configure('linenum', foreground='#555555')

    def _highlight(self):
        e = self.editor
        for tag in ('kw', 'builtin', 'string', 'comment', 'number', 'linenum'):
            e.tag_remove(tag, '1.0', 'end')

        src = e.get('1.0', 'end')
        for i, line in enumerate(src.splitlines(), 1):
            def tag(name, m):
                e.tag_add(name, f'{i}.{m.start()}', f'{i}.{m.end()}')

            rem = REM_RE.match(line)
            if rem:
                e.tag_add('comment', f'{i}.{rem.start(2)}', f'{i}.{len(line)}')
                continue

            for m in STR_RE.finditer(line): tag('string',  m)
            for m in KW_RE.finditer(line):  tag('kw',      m)
            for m in BI_RE.finditer(line):  tag('builtin', m)
            for m in NUM_RE.finditer(line): tag('number',  m)
            lno = LNO_RE.match(line)
            if lno: tag('linenum', lno)

    # ── Auto-run (debounced) ──────────────────────────────────────────────────

    def _on_key(self, _event=None):
        self._highlight()
        if self._job:
            self.root.after_cancel(self._job)
        self._job = self.root.after(DEBOUNCE_MS, self._run)

    # ── Run ───────────────────────────────────────────────────────────────────

    def _run(self):
        self._job = None
        code = self.editor.get('1.0', 'end-1c').strip()
        if not code:
            return

        with tempfile.NamedTemporaryFile(suffix='.bas', mode='w', delete=False) as f:
            f.write(code)
            tmp = f.name

        try:
            r = subprocess.run(
                [sys.executable, COMPILER, tmp, '-r'],
                capture_output=True, text=True, timeout=10,
            )
            body = r.stdout
            if r.stderr.strip():
                body += '\n\n--- stderr ---\n' + r.stderr.strip()
            ok = r.returncode == 0
        except subprocess.TimeoutExpired:
            body, ok = '[timed out after 10s]', False
        finally:
            os.unlink(tmp)

        self.output.configure(state='normal')
        self.output.delete('1.0', 'end')
        self.output.insert('end', body)
        self.output.configure(state='disabled')

        self._out_label.configure(
            text='Output',
            fg='#858585' if ok else '#f44747',
        )

    # ── File I/O ──────────────────────────────────────────────────────────────

    def _open(self):
        path = filedialog.askopenfilename(
            filetypes=[('BASIC files', '*.bas'), ('All files', '*.*')])
        if not path:
            return
        with open(path) as f:
            src = f.read()
        self.editor.delete('1.0', 'end')
        self.editor.insert('1.0', src)
        self._file = path
        self.root.title(f'BASIC Live — {os.path.basename(path)}')
        self._highlight()
        self._run()

    def _save(self):
        if self._file:
            with open(self._file, 'w') as f:
                f.write(self.editor.get('1.0', 'end-1c'))
        else:
            self._save_as()

    def _save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.bas',
            filetypes=[('BASIC files', '*.bas'), ('All files', '*.*')])
        if not path:
            return
        with open(path, 'w') as f:
            f.write(self.editor.get('1.0', 'end-1c'))
        self._file = path
        self.root.title(f'BASIC Live — {os.path.basename(path)}')


if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()
