REM WHILE with compound condition and nested WHILE
DIM n AS INTEGER
DIM m AS INTEGER
n = 1
WHILE n <= 16 AND n <> 8
    n = n * 2
WEND
PRINT n
REM Nested WHILE
n = 0
m = 0
WHILE n < 3
    m = 0
    WHILE m < 3
        m = m + 1
    WEND
    n = n + 1
WEND
PRINT n; m
