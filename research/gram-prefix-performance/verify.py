#!/usr/bin/env python3
"""Rebuild the selected frame fixture and run exact differential and rejection checks."""
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
if sys.flags.optimize:
    raise SystemExit('enabled assertions required by the pinned checker')
suite = unittest.defaultTestLoader.discover(str(HERE), pattern='test_*.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
print('PASS_GRAM_PREFIX_VERIFICATION')
