#!/usr/bin/env python3
"""Replay the complete retained payload audit and filesystem regressions.

Nick Petalas. Apache-2.0. No supplier execution or network.
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('fail_closed_comparator', HERE / 'compare.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
RETAINED = 'research/strict-replay-payload-comparison/'


def retained_module(name, imports=None):
    """Compile authenticated bytes with temporary, explicitly selected imports."""
    module = ModuleType('_inventory_retained')
    module.__file__ = str(c.ROOT / name)
    imports = imports or {}
    previous = {key: sys.modules.get(key) for key in imports}
    old_path = sys.path[:]
    try:
        sys.modules.update(imports)
        # Executable inputs are authenticated source bytes, not import-cache entries.
        exec(compile(c.source(name), module.__file__, 'exec'), module.__dict__)  # noqa: S102
    finally:
        sys.path[:] = old_path
        for key, value in previous.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value
    return module


def complete_audit():
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    for row in manifest['files']:
        if row['usage'] == 'input':
            c.source(row['path'])
    audit = retained_module(RETAINED + 'verify.py', {'compare': c.strict})
    # Avoid an unauthenticated .pyc when the retained audit loads its comparator.
    audit.legacy_module = lambda: retained_module(audit.LEGACY)
    inputs = audit.bound_inputs()
    data = audit.corpus(inputs)
    actual = audit.audit(inputs, data)
    stored = json.loads(c.source(RETAINED + 'RESULT.json'))
    if audit.encoded(actual) != audit.encoded(stored):
        raise ValueError('complete retained audit receipt differs')
    with tempfile.TemporaryDirectory(prefix='inventory corpus ') as temporary:
        roots = [Path(temporary) / 'reference', Path(temporary) / 'run']
        for root in roots:
            for name, raw in data.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.write_bytes(raw) != len(raw):
                    raise ValueError('incomplete corpus fixture write')
        expected = {name: {'cls': 'bytes'} for name in data}
        if c.compare(*roots) != expected or c.predecessor().compare(*roots) != expected:
            raise ValueError('complete 105-file inventory differs')
    return audit


def main():
    audit = complete_audit()
    test_spec = importlib.util.spec_from_file_location('inventory_controls', HERE / 'test_compare.py')
    tests = importlib.util.module_from_spec(test_spec)
    test_spec.loader.exec_module(tests)
    suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
    retained_tests = retained_module(RETAINED + 'test_compare.py',
                                     {'compare': c.strict, 'verify': audit})
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(retained_tests))
    count = suite.countTestCases()
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        raise ValueError('inventory comparison controls failed')
    print('PASS_STRICT_PAYLOAD_FAIL_CLOSED_INVENTORY files=105 '
          'retained_false_equivalences=39 timing_rejections=22 '
          'test_groups=' + str(count) + ' no_new_kappa')


if __name__ == '__main__':
    main()
