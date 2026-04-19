REM FOR with various STEP values
DIM i AS INTEGER
FOR i = 0 TO 10 STEP 3
    PRINT i;
NEXT i
PRINT
FOR i = 10 TO 0 STEP -4
    PRINT i;
NEXT i
PRINT
REM STEP 0.5 (float loop var)
DIM f AS FLOAT
FOR f = 1 TO 2 STEP 0.5
    PRINT f;
NEXT f
PRINT
REM Loop that executes zero times
FOR i = 5 TO 1
    PRINT "never";
NEXT i
PRINT "done"
