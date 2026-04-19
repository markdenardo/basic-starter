REM ============================================================
REM Chapter 3: Graphics & Sound
REM TI-99/4A CALL commands simulated as text output.
REM On real hardware these draw to the 24x32 character screen.
REM ============================================================
REM  CALL CLEAR              -- erase screen
REM  CALL SCREEN(n)          -- set background colour 1-16
REM  CALL COLOR(set,fg,bg)   -- colour a character set
REM  CALL HCHAR(r,c,ch,rep)  -- draw char horizontally
REM  CALL VCHAR(r,c,ch,rep)  -- draw char vertically
REM  CALL CHAR(code,"hex")   -- define custom 8x8 glyph
REM  CALL SOUND(ms,hz,vol)   -- play tone
REM ============================================================

DIM i AS INTEGER
DIM j AS INTEGER
DIM col AS INTEGER

PRINT "--- Text box (simulating CALL HCHAR) ---"
FOR i = 1 TO 5
    FOR j = 1 TO 20
        IF i = 1 OR i = 5 THEN
            PRINT "*";
        ELSE
            IF j = 1 OR j = 20 THEN
                PRINT "*";
            ELSE
                PRINT " ";
            END IF
        END IF
    NEXT j
    PRINT
NEXT i

PRINT
PRINT "--- Colour palette (16 colours) ---"
DATA "transparent","black","med-green","lt-green","dk-blue","lt-blue"
DATA "dk-red","cyan","med-red","lt-red","dk-yellow","lt-yellow"
DATA "dk-green","magenta","gray","white"
DIM colname$ AS STRING
FOR i = 1 TO 16
    READ colname$
    PRINT i; ": "; colname$
NEXT i

PRINT
PRINT "--- Sound frequencies (musical notes) ---"
DATA "C4",262,"D4",294,"E4",330,"F4",349,"G4",392,"A4",440,"B4",494
DIM note$ AS STRING
DIM freq AS FLOAT
FOR i = 1 TO 8
    READ note$, freq
    PRINT note$; " = "; freq; " Hz   CALL SOUND(300,"; freq; ",5)"
NEXT i

END
