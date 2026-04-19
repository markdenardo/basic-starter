REM Nested IF/ELSE/END IF
DIM x AS INTEGER
DIM y AS INTEGER
x = 5
y = 10
IF x < y THEN
    IF x > 3 THEN
        PRINT "x in (3,y)"
    ELSE
        PRINT "x <= 3"
    END IF
ELSE
    PRINT "x >= y"
END IF
REM single-line nested
IF x > 0 THEN IF y > 0 THEN PRINT "both positive"
