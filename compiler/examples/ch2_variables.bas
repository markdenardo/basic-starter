REM ============================================================
REM Chapter 2: Variables & Operators
REM Numeric vars, string vars, expressions, operator precedence
REM ============================================================

DIM score AS FLOAT
DIM name$ AS STRING
DIM radius AS FLOAT

REM Numeric variables
score = 100
score = score + 50 - 10
PRINT "Score: "; score

REM Operator precedence: ^ before */ before +-
REM 2^3*4 = 32  (8*4)
PRINT "2^3*4 = "; 2^3*4
REM 10 MOD 3 = 1
PRINT "10 MOD 3 = "; 10 MOD 3
REM Integer division
PRINT "10/3 = "; 10/3
PRINT "INT(10/3) = "; INT(10/3)

REM Relational expressions (1=true, 0=false in our compiler)
PRINT "5 > 3 is "; 5 > 3
PRINT "5 < 3 is "; 5 < 3
PRINT "5 = 5 is "; 5 = 5

REM String variables
name$ = "BASIC"
PRINT "Language: "; name$
PRINT "Length: "; LEN(name$)

REM Math function
radius = 5
PRINT "Area of circle r=5: "; 3.14159 * radius^2

END
