#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Path-only adapter for exact frozen NEW pure fixture, after archive checks."""
from pathlib import Path
import importlib.util
import sys
import unittest

PACKAGE = Path(__file__).resolve().parent


def load_new(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    load_new('prefix_derivation_static_preservation', PACKAGE / 'verify.py').main()
    fixture = load_new('prefix_derivation_new_pure_fixture', PACKAGE / 'fixtures/test_derivation_pure_v2.py')
    fixture.IMPL = PACKAGE / 'implementation'
    fixture.ORIGINAL = PACKAGE / 'snapshot/variant_driver_v1.py.txt'
    suite = unittest.defaultTestLoader.loadTestsFromModule(fixture)
    if suite.countTestCases() != 8:
        raise RuntimeError('expected exactly eight frozen NEW pure derivation methods')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    print('PASS_EXACT_EIGHT_NEW_PURE_DERIVATION_METHODS optimized=' + str(sys.flags.optimize), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
