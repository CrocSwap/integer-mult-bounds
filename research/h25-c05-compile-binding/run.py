#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Cold path adapter: execute only new frozen pure fixture code."""
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
    load_new('binding_archive_integrity', PACKAGE / 'verify.py').verify()
    load_new('compile_binding_v1', PACKAGE / 'compile_binding_v1.py')
    fixture = load_new('binding_new_pure_fixture', PACKAGE / 'test_compile_binding_v1.py')
    fixture.REFERENCE = PACKAGE / 'snapshot/areas'
    fixture.HERE = PACKAGE
    suite = unittest.defaultTestLoader.loadTestsFromModule(fixture)
    if suite.countTestCases() != 28:
        raise RuntimeError('expected exactly 28 new pure fixture methods')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    print('PASS_FROZEN_BINDING_PURE_TESTS methods=28 optimized=' + str(sys.flags.optimize), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
