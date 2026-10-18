#!/usr/bin/env python3
"""Replay selected source bindings and complete retained regression suites.

Nick Petalas. Apache-2.0. No circuit replay or network access.
"""
import importlib.machinery
import json
import unittest
from fractions import Fraction
from pathlib import Path
from types import ModuleType
from unittest import mock

HERE = Path(__file__).resolve().parent


def local_module(name):
    module = ModuleType('_selected_inventory_' + name.replace('.', '_'))
    module.__file__ = str(HERE / name)
    exec(compile((HERE / name).read_bytes(), module.__file__, 'exec'), module.__dict__)  # noqa: S102
    return module


c = local_module('check.py')
TESTS = ('tests/test_selected_result.py', 'tests/test_selected_inventory_links.py',
         'tests/test_selected_proof_binding.py')


def retained_tests(name, engine):
    """Run unchanged tests with one explicitly selected checker implementation."""
    module = ModuleType('_selected_inventory_retained')
    module.__file__ = str(c.ROOT / name)
    original = importlib.machinery.SourceFileLoader.get_code

    def source_code(loader, fullname):
        if Path(loader.path).resolve() == c.ROOT / c.PREDECESSOR:
            return compile(c.source(c.PREDECESSOR), loader.path, 'exec')
        return original(loader, fullname)

    # The retained tests import the original checker at module initialization.
    # Authenticate that executable source too, rather than using a cached pyc.
    with mock.patch.object(importlib.machinery.SourceFileLoader, 'get_code', source_code):
        exec(compile(c.source(name), module.__file__, 'exec'), module.__dict__)  # noqa: S102
    module.checker = engine
    return unittest.defaultTestLoader.loadTestsFromModule(module)


def main():
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    for row in manifest['files']:
        if row['usage'] == 'input':
            c.source(row['path'])
    record = json.loads(c.source('certificates/selected-result.json'))
    expected = Fraction(836330098538459, 500000000000000000)
    for engine in (c.predecessor(), c.checker):
        if engine.check(record) != expected:
            raise ValueError('complete selected source binding differs')
    suite = unittest.TestSuite()
    for engine in (c.predecessor(), c.checker):
        for name in TESTS:
            suite.addTests(retained_tests(name, engine))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(local_module('test_inventory.py')))
    count = suite.countTestCases()
    if count != 59:
        raise ValueError('expected all 26 retained groups per engine plus 7 new groups')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise ValueError('selected inventory controls failed')
    print('PASS_SELECTED_INVENTORY_FAIL_CLOSED tests=' + str(count)
          + ' skipped=' + str(len(result.skipped))
          + ' selected_files=1579 no_new_kappa')


if __name__ == '__main__':
    main()
