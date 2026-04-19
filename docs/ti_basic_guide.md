# TI-99/4A BASIC — One-Page Reference

*Based on C. Regena's "Programmer's Reference Guide to the TI-99/4A" (1983, Compute! Publications)*

---

## Program Structure

Every statement begins with a **line number** (1–32767). Lines execute in order; type `RUN` to start, `LIST` to view, `NEW` to clear.

```basic
100 REM This is a comment
110 PRINT "HELLO"
120 END
```

---

## Variables & Types

| Kind | Name rule | Example | Default |
|---|---|---|---|
| Numeric | 1–15 chars, A–Z, 0–9 | `SCORE`, `X1` | 0 |
| String | ends with `$` | `NAME$`, `A$` | `""` |

Operators: `+  -  *  /  ^` (power) · `DIV` (integer ÷) · `MOD` (remainder)  
Relational: `=  <  >  <=  >=  <>` · Logical: `AND  OR  NOT`

---

## Input / Output

```basic
PRINT "Score: "; SCORE              :: semicolon = no space
PRINT TAB(10); "centered"           :: tab to column
INPUT "Your name? ": NAME$          :: prompts, then waits
CALL KEY(0, K, S)                   :: S=1 if key pressed; K=keycode
```

---

## Control Flow

```basic
IF X > 10 THEN 200 ELSE 300         :: branch to line numbers
IF X > 10 THEN PRINT "BIG"          :: inline action

GOTO 500                            :: unconditional jump
GOSUB 1000 :: RETURN                :: call subroutine

ON N GOTO 100, 200, 300             :: jump to Nth line
```

---

## Loops

```basic
FOR I = 1 TO 10 STEP 2              :: STEP defaults to 1
  PRINT I                           :: (indent is cosmetic only)
NEXT I

WHILE X < 100  :: X = X + 1  :: WEND     :: TI Extended BASIC only
```

---

## Data

```basic
READ NAME$, SCORE                   :: pulls next values from DATA
DATA "Alice", 95, "Bob", 82         :: stored anywhere in program
RESTORE                             :: rewind data pointer to start

DIM A(10), B$(5)                    :: declare arrays (1-based index)
DIM GRID(8,8)                       :: 2D array
```

---

## String Functions

| Function | Returns |
|---|---|
| `LEN(A$)` | length in characters |
| `SEG$(A$, start, len)` | substring (1-based) |
| `POS(A$, B$, start)` | position of B$ in A$, 0 if not found |
| `STR$(N)` | number → string |
| `VAL(A$)` | string → number |
| `CHR$(N)` | ASCII code → character |
| `ASC(A$)` | character → ASCII code |

---

## Math Functions

`ABS` `INT` `SGN` `SQR` · `SIN` `COS` `TAN` `ATN` · `LOG` `EXP` · `RND` · `RANDOMIZE`

```basic
X = INT(RND * 6) + 1               :: random die roll 1–6
```

---

## Screen & Color (CALL commands)

```basic
CALL CLEAR                          :: erase screen
CALL SCREEN(color)                  :: background: 1=transparent … 16=white
CALL COLOR(charset, fg, bg)         :: sets color for a character set
```
Colors 1–16: transparent, black, med-green, lt-green, dk-blue, lt-blue, dk-red, cyan, med-red, lt-red, dk-yellow, lt-yellow, dk-green, magenta, gray, white.

---

## Graphics Characters

```basic
CALL HCHAR(row, col, charcode, reps)  :: draw char horizontally
CALL VCHAR(row, col, charcode, reps)  :: draw char vertically
CALL GCHAR(row, col, VAR)             :: read char at position into VAR
CALL CHAR(code, "hex-pattern")        :: define custom 8×8 glyph
```
Screen is **24 rows × 32 columns**. Standard chars: 32–127. Custom: 128–143.  
Pattern is 16 hex digits → 8 rows of 8 bits, e.g. `"3C66C3C3C3663C00"` = circle.

---

## Sound

```basic
CALL SOUND(dur, freq1, vol1, freq2, vol2, freq3, vol3, noise, nvol)
```
- `dur`: milliseconds (negative = play in background)
- `freq`: 110–44733 Hz (musical range); negative = noise type
- `vol`: 0 (loudest) → 30 (silent)

```basic
100 CALL SOUND(500, 440, 5)          :: 500ms, A4, medium volume
110 CALL SOUND(250, 262, 3, 330, 3)  :: C + E chord, louder
```

---

## Program Template

```basic
100 REM === INIT ===
110 CALL CLEAR :: CALL SCREEN(2)
120 GOSUB 1000

200 REM === MAIN LOOP ===
210 CALL KEY(0, K, S)
220 IF S = 0 THEN 210
230 IF K = 27 THEN 900
240 GOSUB 2000
250 GOTO 210

900 END

1000 REM --- Setup subroutine ---
1010 RETURN

2000 REM --- Game logic subroutine ---
2010 RETURN
```
