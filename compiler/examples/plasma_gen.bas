REM Generate a plasma colour table and print as CSV
REM Demonstrates math builtins: SIN, SQR, INT

DIM x AS INTEGER
DIM y AS INTEGER
DIM v AS FLOAT
DIM r AS INTEGER
DIM g AS INTEGER
DIM b AS INTEGER

FOR y = 0 TO 7
    FOR x = 0 TO 7
        v = SIN(x * 0.8) + SIN(y * 0.6) + SIN((x + y) * 0.5)
        r = INT((v / 3.0 + 1.0) * 127.5)
        g = INT((SIN(v * 1.5) + 1.0) * 63.5)
        b = INT((1.0 - (v / 3.0 + 1.0)) * 127.5)
        PRINT r; ","; g; ","; b; "  ";
    NEXT x
    PRINT
NEXT y

END
