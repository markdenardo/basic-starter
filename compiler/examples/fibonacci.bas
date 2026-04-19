REM Fibonacci sequence
DIM a AS FLOAT
DIM b AS FLOAT
DIM c AS FLOAT
DIM n AS INTEGER

n = 20
a = 0
b = 1

PRINT "Fibonacci sequence:"
FOR i = 1 TO n
    PRINT a
    c = a + b
    a = b
    b = c
NEXT i

END
