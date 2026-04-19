REM Logical operators: AND, OR, NOT
PRINT 1 AND 1
PRINT 1 AND 0
PRINT 0 OR 1
PRINT 0 OR 0
PRINT NOT 0
PRINT NOT 1
REM Compound conditions
DIM x AS INTEGER
x = 5
IF x > 3 AND x < 10 THEN PRINT "in range" ELSE PRINT "out"
IF x < 3 OR x > 4 THEN PRINT "either" ELSE PRINT "neither"
IF NOT (x = 5) THEN PRINT "not five" ELSE PRINT "is five"
