REM String functions: edge cases and comparisons
DIM s$ AS STRING
s$ = ""
PRINT LEN(s$)
s$ = "Z"
PRINT ASC(s$)
PRINT CHR$(ASC(s$) + 1)
REM MID$ at start and end
s$ = "ABCDE"
PRINT MID$(s$, 1, 1)
PRINT MID$(s$, 5, 1)
PRINT MID$(s$, 2, 3)
REM LEFT$/RIGHT$ full length
PRINT LEFT$(s$, 5)
PRINT RIGHT$(s$, 5)
REM Numeric string round-trip
PRINT VAL(STR$(3.14))
