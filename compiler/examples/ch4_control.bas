REM ============================================================
REM Chapter 4: Control Flow
REM IF-THEN-ELSE, GOTO, GOSUB/RETURN, FOR-NEXT, nested loops
REM ============================================================

DIM n AS INTEGER
DIM i AS INTEGER
DIM j AS INTEGER
DIM total AS FLOAT

REM --- IF / THEN / ELSE ---
PRINT "--- IF-THEN-ELSE ---"
n = 7
IF n MOD 2 = 0 THEN
    PRINT n; " is even"
ELSE
    PRINT n; " is odd"
END IF

REM --- GOTO: jump to labelled line ---
PRINT "--- GOTO ---"
GOTO 300
PRINT "this line is skipped"
300 PRINT "jumped here via GOTO 300"

REM --- GOSUB / RETURN ---
PRINT "--- GOSUB ---"
GOSUB 1000
PRINT "back from subroutine"

REM --- FOR-NEXT with STEP ---
PRINT "--- FOR-NEXT countdown ---"
FOR i = 10 TO 1 STEP -1
    PRINT i; " ";
NEXT i
PRINT

REM --- Nested loops: multiplication table ---
PRINT "--- 3x3 multiplication table ---"
FOR i = 1 TO 3
    FOR j = 1 TO 3
        PRINT i * j; "  ";
    NEXT j
    PRINT
NEXT i

REM --- Accumulator loop ---
total = 0
FOR i = 1 TO 100
    total = total + i
NEXT i
PRINT "Sum 1-100 = "; total

END

1000 REM --- Subroutine ---
1010 PRINT "inside subroutine"
1020 RETURN
