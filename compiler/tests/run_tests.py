#!/usr/bin/env python3
"""Test runner for the BASIC compiler.

Usage:
    python3 compiler/tests/run_tests.py           # run all tests
    python3 compiler/tests/run_tests.py t05       # run tests matching pattern
"""

import os, sys, subprocess, difflib, glob

TESTS_DIR  = os.path.dirname(os.path.abspath(__file__))
COMPILER   = os.path.join(TESTS_DIR, '..', 'basicc.py')
PYTHON     = sys.executable

def run_test(bas_path: str) -> tuple[bool, str]:
    expected_path = bas_path.replace('.bas', '.expected')
    if not os.path.exists(expected_path):
        return None, f'no .expected file'

    with open(expected_path) as f:
        expected = f.read()

    result = subprocess.run(
        [PYTHON, COMPILER, bas_path, '-r'],
        capture_output=True, text=True
    )
    actual = result.stdout

    if result.returncode != 0:
        return False, f'compiler/runtime error:\n{result.stderr.strip()}'

    if actual == expected:
        return True, ''

    diff = ''.join(difflib.unified_diff(
        expected.splitlines(keepends=True),
        actual.splitlines(keepends=True),
        fromfile='expected', tofile='actual'
    ))
    return False, diff

def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else ''
    tests   = sorted(glob.glob(os.path.join(TESTS_DIR, 't*.bas')))
    if pattern:
        tests = [t for t in tests if pattern in os.path.basename(t)]

    if not tests:
        print('no tests found'); sys.exit(1)

    passed = failed = skipped = 0
    for path in tests:
        name = os.path.basename(path)
        ok, msg = run_test(path)
        if ok is None:
            print(f'  SKIP  {name}  ({msg})')
            skipped += 1
        elif ok:
            print(f'  PASS  {name}')
            passed += 1
        else:
            print(f'  FAIL  {name}')
            print(msg)
            failed += 1

    total = passed + failed + skipped
    print(f'\n{passed}/{total} passed', end='')
    if skipped: print(f'  {skipped} skipped', end='')
    if failed:  print(f'  {failed} FAILED', end='')
    print()
    sys.exit(0 if failed == 0 else 1)

if __name__ == '__main__':
    main()
