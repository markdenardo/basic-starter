REM GOTO forward and backward
DIM n AS INTEGER
n = 0
GOTO 30
10 PRINT "skipped"
20 GOTO 50
30 n = n + 1
40 IF n < 3 THEN GOTO 30
50 PRINT n
END
