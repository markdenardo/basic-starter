REM ============================================================
REM Chapter 5: Built-in Functions
REM Math functions, string functions, RND
REM ============================================================

DIM x AS FLOAT
DIM a$ AS STRING
DIM i AS INTEGER

REM --- Math functions ---
PRINT "--- Math ---"
PRINT "ABS(-7)   = "; ABS(-7)
PRINT "INT(3.9)  = "; INT(3.9)
PRINT "INT(-3.9) = "; INT(-3.9)
PRINT "SGN(-5)   = "; SGN(-5)
PRINT "SQR(144)  = "; SQR(144)
PRINT "2^10      = "; 2^10

PRINT "--- Trig (radians) ---"
x = 3.14159265 / 4
PRINT "SIN(pi/4) = "; SIN(x)
PRINT "COS(pi/4) = "; COS(x)
PRINT "ATN(1)*4  = "; ATN(1)*4

PRINT "--- Log / Exp ---"
PRINT "LOG(1)    = "; LOG(1)
PRINT "EXP(1)    = "; EXP(1)
PRINT "EXP(LOG(5))="; EXP(LOG(5))

REM --- Random numbers ---
PRINT "--- RND (5 dice rolls) ---"
FOR i = 1 TO 5
    PRINT INT(RND(1) * 6) + 1; " ";
NEXT i
PRINT

REM --- String functions ---
PRINT "--- Strings ---"
a$ = "HELLO WORLD"
PRINT "Original:  "; a$
PRINT "LEN:       "; LEN(a$)
PRINT "LEFT$(6):  "; LEFT$(a$, 6)
PRINT "RIGHT$(5): "; RIGHT$(a$, 5)
PRINT "MID$(7,5): "; MID$(a$, 7, 5)

PRINT "--- Conversion ---"
PRINT "STR$(3.14): "; STR$(3.14)
PRINT "VAL('42'): "; VAL("42")
PRINT "ASC('A'):  "; ASC("A")
PRINT "CHR$(65):  "; CHR$(65)

END
