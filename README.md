# basic-starter

Two independent retro-computing tools in one repo:

1. **Demoscene template** — a FreeBASIC demo with scene sequencer and visual effects
2. **BASIC compiler** — a Python 3 compiler that translates a BASIC dialect to C99 (zero dependencies)

---

## Demoscene Template

A minimal FreeBASIC demoscene framework with a scene sequencer, plasma effect, and 3D starfield.

### Dependency

```bash
# macOS
brew install freebasic
```

Or download `fbc` from [freebasic.net](https://www.freebasic.net/).

### Build & Run

```bash
make        # compile → ./demo
make run    # compile and launch
```

### Architecture

| File | Role |
|---|---|
| `src/demo.bi` | Shared init: `DemoInit()`, `DemoFlip()`, `DemoShutdown()`, sine LUT, `PIXEL(x,y)` macro |
| `src/effects/plasma.bi` | `Effect_Plasma(t)` — four-wave plasma |
| `src/effects/starfield.bi` | `Effect_Starfield_Init()` + `Effect_Starfield(dt)` — 3D starfield |
| `src/main.bas` | Entry point: includes everything, owns the scene table and main loop |

**Adding a new scene**: define `Sub Effect_Foo(t)` in a `.bi` file, `#include` it in `main.bas`, add a `CONST SCENE_FOO`, and append it to the `scenes()` array. `SCENE_DUR` controls seconds per scene. Effects write pixels via `PIXEL(x,y)` onto a 320×200 canvas; `DemoFlip()` stretch-blits at `DEMO_SCALE`× and page-flips.

---

## BASIC Compiler

`compiler/basicc.py` — a single-file compiler with no external dependencies. Parses a subset of classic BASIC and emits C99.

### Dependency

```bash
gcc   # or clang — only needed for -r (compile-and-run)
```

### Usage

```bash
python3 compiler/basicc.py source.bas              # print C to stdout
python3 compiler/basicc.py source.bas -o out.c    # write C file
python3 compiler/basicc.py source.bas -r          # compile and run

make bas-run FILE=compiler/examples/fibonacci.bas  # shorthand
make bas-to-c FILE=compiler/examples/fibonacci.bas
```

### Supported BASIC Syntax

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

**Variable naming**: `name$` → `const char*`, `name%` → `int`, others → `double`.

**Built-ins**: `SIN COS TAN SQR ABS INT SGN LOG EXP ATN RND LEN LEFT$ RIGHT$ MID$ STR$ VAL CHR$ ASC`.

**Note**: `GOSUB/RETURN` uses GCC/Clang label-as-value (`&&label` / `goto *ptr`) — GCC or Clang required.

### Examples

```bas
REM Fibonacci sequence
DIM a AS FLOAT
DIM b AS FLOAT
n = 20 : a = 0 : b = 1
FOR i = 1 TO n
    PRINT a
    c = a + b : a = b : b = c
NEXT i
END
```

See `compiler/examples/` for more: `hello.bas`, `fibonacci.bas`, `plasma_gen.bas`, and chapter-by-chapter walkthroughs.

### Test Suite

```bash
make test                                       # run all 20 tests
python3 compiler/tests/run_tests.py t05        # run tests matching pattern
```

Tests live in `compiler/tests/tNN_name.bas` + `tNN_name.expected`. To add a test: write the `.bas` file, run it with `-r` to verify, then redirect output to `.expected`.

**Coverage**: PRINT/suppress, arithmetic, variables, IF/ELSE, FOR/NEXT, WHILE, GOSUB, strings, DATA/READ/RESTORE, math functions, logical operators, nested loops, GOTO, float STEP, multi-subroutine, nested IF, compound WHILE, integration.

---

## Reference

`docs/ti_basic_guide.md` — a one-page TI-99/4A BASIC cheat sheet covering variables, operators, PRINT, INPUT, IF, loops, DATA, strings, math, CALL commands, colours, sound, and screen layout.
