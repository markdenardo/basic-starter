REM ============================================================
REM Chapter 7: A Complete Demo Program
REM Combines: DATA, subroutines, loops, strings, math, control.
REM Architecture: init (100s), main (200-800), end (900), subs (1000+)
REM ============================================================

DATA "C4",262,"D4",294,"E4",330,"F4",349,"G4",392,"A4",440,"B4",494,"C5",523

100 DIM note$ AS STRING
110 DIM freq AS FLOAT
120 DIM i AS INTEGER
130 DIM tries AS INTEGER
140 DIM secret AS FLOAT
150 DIM guess AS FLOAT
160 GOSUB 1000

200 REM Scale player
210 PRINT "--- Musical Scale ---"
220 FOR i = 1 TO 8
230 READ note$, freq
240 PRINT note$; " ("; freq; " Hz)  CALL SOUND(300,"; freq; ",5)"
250 NEXT i

300 REM Number guessing game (binary search)
310 PRINT
320 PRINT "--- Number Guessing Game (1-10) ---"
330 secret = INT(RND(1) * 10) + 1
340 tries = 0
350 GOSUB 2000
360 PRINT "Number was "; secret; ". Solved in "; tries; " tries."

400 REM String manipulator
410 PRINT
420 GOSUB 3000

500 REM Prime sieve
510 PRINT
520 PRINT "--- Primes to 30 ---"
530 GOSUB 4000

900 END

REM --- Init subroutine ---
1000 PRINT "================================"
1010 PRINT "  TI-99/4A BASIC Demo Chapter 7"
1020 PRINT "================================"
1030 PRINT
1040 RETURN

REM --- Binary-search guessing game ---
2000 guess = 5
2010 WHILE guess <> secret
2020 tries = tries + 1
2030 IF guess < secret THEN
2040 PRINT "  "; guess; " too low"
2050 guess = guess + INT((secret - guess) / 2) + 1
2060 ELSE
2070 PRINT "  "; guess; " too high"
2080 guess = guess - INT((guess - secret) / 2) - 1
2090 END IF
2100 WEND
2110 tries = tries + 1
2120 PRINT "  "; guess; " correct!"
2130 RETURN

REM --- String operations ---
3000 DIM w$ AS STRING
3010 PRINT "--- String Operations ---"
3020 w$ = "DEMOSCENE"
3030 PRINT "Word:    "; w$
3040 PRINT "Length:  "; LEN(w$)
3050 PRINT "Reverse: ";
3060 FOR i = LEN(w$) TO 1 STEP -1
3070 PRINT MID$(w$, i, 1);
3080 NEXT i
3090 PRINT
3100 PRINT "A-H via CHR$: ";
3110 FOR i = 65 TO 72
3120 PRINT CHR$(i);
3130 NEXT i
3140 PRINT
3150 RETURN

REM --- Trial-division prime sieve ---
4000 DIM n AS INTEGER
4010 DIM d AS INTEGER
4020 DIM isPrime AS INTEGER
4030 FOR n = 2 TO 30
4040 isPrime = 1
4050 d = 2
4060 WHILE d * d <= n AND isPrime = 1
4070 IF n MOD d = 0 THEN isPrime = 0
4080 d = d + 1
4090 WEND
4100 IF isPrime = 1 THEN PRINT n; " ";
4110 NEXT n
4120 PRINT
4130 RETURN
