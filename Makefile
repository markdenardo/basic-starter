BINARY  := demo
SRC     := src/main.bas
FBC     := fbc
PYTHON  := python3
BASICC  := compiler/basicc.py

.PHONY: all run clean compiler-test

# ── Demo ─────────────────────────────────────────────────────────────────────

all: $(BINARY)

$(BINARY): $(SRC) src/demo.bi src/effects/plasma.bi src/effects/starfield.bi
	$(FBC) $(SRC) -o $(BINARY)

run: $(BINARY)
	./$(BINARY)

# ── BASIC compiler ───────────────────────────────────────────────────────────

# Compile a .bas file to C:   make bas-to-c FILE=compiler/examples/hello.bas
bas-to-c:
	$(PYTHON) $(BASICC) $(FILE) -o $(FILE:.bas=.c)

# Compile and run a .bas file: make bas-run FILE=compiler/examples/fibonacci.bas
bas-run:
	$(PYTHON) $(BASICC) $(FILE) -r

compiler-test:
	$(PYTHON) $(BASICC) compiler/examples/fibonacci.bas -r
	echo "Alice" | $(PYTHON) $(BASICC) compiler/examples/hello.bas -r
	$(PYTHON) $(BASICC) compiler/examples/plasma_gen.bas -r

test:
	$(PYTHON) compiler/tests/run_tests.py

# ── Clean ────────────────────────────────────────────────────────────────────

clean:
	rm -f $(BINARY) compiler/examples/*.c
