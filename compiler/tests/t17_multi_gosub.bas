REM Multiple subroutines, called multiple times
DIM i AS INTEGER
FOR i = 1 TO 3
    GOSUB 200
NEXT i
GOSUB 300
END
200 PRINT "tick "; i
210 RETURN
300 PRINT "done"
310 RETURN
