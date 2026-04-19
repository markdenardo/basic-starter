REM Combined: DATA-driven table with functions and control flow
DATA 1,1,2,3,5,8,13,21,34,55
DIM prev AS FLOAT
DIM curr AS FLOAT
DIM nxt AS FLOAT
DIM i AS INTEGER
DIM even_sum AS FLOAT
DIM odd_sum AS FLOAT
even_sum = 0
odd_sum = 0
FOR i = 1 TO 10
    READ curr
    IF INT(curr) MOD 2 = 0 THEN
        even_sum = even_sum + curr
    ELSE
        odd_sum = odd_sum + curr
    END IF
NEXT i
PRINT even_sum
PRINT odd_sum
RESTORE
GOSUB 100
END
100 READ prev
110 READ curr
120 FOR i = 3 TO 10
130     READ nxt
140     IF nxt <> prev + curr THEN PRINT "bad fib at "; i
150     prev = curr
160     curr = nxt
170 NEXT i
180 PRINT "fib ok"
190 RETURN
