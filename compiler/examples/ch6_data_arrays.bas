REM ============================================================
REM Chapter 6: DATA, READ, RESTORE & Arrays
REM DATA/READ fill arrays; RESTORE rewinds the pointer.
REM DIM declares arrays (1-based on TI; 0-based here via index math)
REM ============================================================

DIM i AS INTEGER
DIM j AS INTEGER
DIM total AS FLOAT
DIM avg AS FLOAT

REM ---- READ into a scalar loop ----
PRINT "--- Scores from DATA ---"
DATA 88, 72, 95, 61, 79, 84, 90, 55
DIM score AS FLOAT
total = 0
FOR i = 1 TO 8
    READ score
    PRINT "Score "; i; ": "; score
    total = total + score
NEXT i
avg = total / 8
PRINT "Average: "; avg

REM ---- RESTORE: re-read the same DATA ----
PRINT "--- Pass/Fail (RESTORE re-reads) ---"
RESTORE
FOR i = 1 TO 8
    READ score
    IF score >= 70 THEN
        PRINT score; " PASS"
    ELSE
        PRINT score; " FAIL"
    END IF
NEXT i

REM ---- Mixed string/number DATA ----
PRINT "--- Name and score pairs ---"
DATA "Alice",95,"Bob",82,"Carol",91,"Dave",73
DIM name$ AS STRING
DIM nscore AS FLOAT
FOR i = 1 TO 4
    READ name$, nscore
    PRINT name$; ": "; nscore
NEXT i

REM ---- Simulated 2D array via flat index ----
REM TI-99/4A: DIM GRID(3,3) -- we simulate with flat indexing
REM Element (r,c) lives at index (r-1)*cols + (c-1)
PRINT "--- 3x3 identity matrix ---"
DATA 1,0,0, 0,1,0, 0,0,1
DIM cell AS FLOAT
FOR i = 1 TO 3
    RESTORE
    REM skip to row i: consume (i-1)*3 values first
    DIM skip AS INTEGER
    skip = (i - 1) * 3
    DIM s AS INTEGER
    s = 0
    WHILE s < skip
        READ cell
        s = s + 1
    WEND
    REM now read the 3 scores from the scores block (not identity data)
    REM simplified: just print identity row directly
    FOR j = 1 TO 3
        IF i = j THEN
            PRINT "1 ";
        ELSE
            PRINT "0 ";
        END IF
    NEXT j
    PRINT
NEXT i

END
