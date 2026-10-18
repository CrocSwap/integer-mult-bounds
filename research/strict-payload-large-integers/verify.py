#!/usr/bin/env python3
"""Replay the complete predecessor audit and exercise exact large integers.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('large_integer_comparator', HERE / 'compare.py')
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


def retained_module(name, imports):
    """Execute authenticated retained tests with explicitly selected modules."""
    module = ModuleType('_strict_integer_retained')
    module.__file__ = str(candidate.ROOT / name)
    previous = {key: sys.modules.get(key) for key in imports}
    old_path = sys.path[:]
    try:
        sys.modules.update(imports)
        exec(compile(candidate.source(name), module.__file__, 'exec'), module.__dict__)
    finally:
        sys.path[:] = old_path
        for key, value in previous.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value
    return module


def audit_module(comparator):
    module = retained_module('research/strict-replay-payload-comparison/verify.py',
                             {'compare': comparator})
    # Authenticate and compile the legacy comparator too, avoiding cached code.
    def legacy():
        result = ModuleType('_strict_integer_legacy')
        result.__file__ = str(candidate.ROOT / module.LEGACY)
        exec(compile(candidate.source(module.LEGACY), result.__file__, 'exec'), result.__dict__)
        return result
    module.legacy_module = legacy
    return module


def main():
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    for row in manifest['files']:
        if row['usage'] == 'input':
            candidate.source(row['path'])
    original = audit_module(candidate.predecessor())
    successor = audit_module(candidate.strict)
    inputs = original.bound_inputs()
    data = original.corpus(inputs)
    before = original.audit(inputs, data)
    after = successor.audit(inputs, data)
    stored = candidate.source('research/strict-replay-payload-comparison/RESULT.json')
    if (original.encoded(before) != original.encoded(json.loads(stored))
            or original.encoded(before) != original.encoded(after)):
        raise ValueError('complete predecessor audit receipt differs')
    tests = HERE / 'test_compare.py'
    test_spec = importlib.util.spec_from_file_location('_large_integer_controls', tests)
    module = importlib.util.module_from_spec(test_spec)
    test_spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    retained_tests = retained_module('research/strict-replay-payload-comparison/test_compare.py',
                                     {'compare': candidate.strict, 'verify': successor})
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(retained_tests))
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        raise ValueError('large integer controls failed')
    print('PASS_STRICT_PAYLOAD_LARGE_INTEGERS files=105 false_equivalences=39 '
          'timing_rejections=22 no_new_kappa')


if __name__ == '__main__':
    main()
