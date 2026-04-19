REM Hello World example
DIM name$ AS STRING
DIM i AS INTEGER

PRINT "What is your name?"
INPUT name$
PRINT "Hello, "; name$; "!"

FOR i = 1 TO 5
    PRINT i; " squared = "; i * i
NEXT i

IF LEN(name$) > 4 THEN
    PRINT "That's a long name!"
ELSE
    PRINT "Short and sweet."
END IF

END
