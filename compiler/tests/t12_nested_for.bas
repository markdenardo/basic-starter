REM Nested FOR loops
DIM i AS INTEGER
DIM j AS INTEGER
DIM sum AS FLOAT
sum = 0
FOR i = 1 TO 3
    FOR j = 1 TO 3
        sum = sum + 1
    NEXT j
NEXT i
PRINT sum
REM Nested IF inside FOR
FOR i = 1 TO 5
    IF i MOD 2 = 0 THEN
        PRINT i; "even";
    ELSE
        PRINT i; "odd";
    END IF
NEXT i
PRINT
