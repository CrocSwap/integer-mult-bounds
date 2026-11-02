#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Only fixture path bindings change; frozen algorithms/assertions stay exact."""
from pathlib import Path
import ast
import importlib.util
import json
import sys
import tempfile
from types import ModuleType
import unittest

PACKAGE = Path(__file__).resolve().parent


def main():
    spec = importlib.util.spec_from_file_location('entry_export_archive_check', PACKAGE / 'verify.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    checker.main()
    fixture_path = PACKAGE / 'fixtures/test_bootstrap_new_v1.py'
    raw = fixture_path.read_bytes()
    tree = ast.parse(raw, filename=str(fixture_path))
    frozen_functions = [ast.dump(n, include_attributes=True) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]
    bases = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'BASE']
    if len(bases) != 1:
        raise RuntimeError('unique fixture BASE path initializer required')
    original = bases[0].value
    if not (isinstance(original, ast.Call) and isinstance(original.func, ast.Name) and original.func.id == 'Path' and len(original.args) == 1 and isinstance(original.args[0], ast.Constant) and type(original.args[0].value) is str and not original.keywords):
        raise RuntimeError('only fixture path initializer may be rebound')
    bases[0].value = ast.copy_location(ast.Call(func=ast.Name(id='Path', ctx=ast.Load()), args=[ast.Constant(str(PACKAGE))], keywords=[]), original)
    ast.fix_missing_locations(tree)
    if frozen_functions != [ast.dump(n, include_attributes=True) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))]:
        raise RuntimeError('fixture function/class/assertion AST changed')
    fixture = ModuleType('entry_export_new_fixture')
    fixture.__file__ = str(fixture_path)
    exec(compile(tree, str(fixture_path), 'exec', dont_inherit=True, optimize=sys.flags.optimize), fixture.__dict__)
    if Path(fixture.m.__file__).resolve() != (PACKAGE / 'implementation/predecessor_entry.py').resolve():
        raise RuntimeError('nonlocal NEW entry source')
    graph = json.loads((PACKAGE / 'SOURCE-GRAPH-v1.json').read_bytes())
    paths = {row['copy_path']: PACKAGE / 'prerequisites' / Path(row['copy_path']).name for row in graph['modules']}
    real_path = Path
    def fixture_path_binding(value, *parts):
        if type(value) is not str or parts:
            raise RuntimeError('fixture paths require one exact string and no extra parts')
        if value in paths:
            return paths[value]
        if not value.startswith('/') or not all(32 <= ord(c) < 127 for c in value) or any(part in ('', '.', '..') for part in value.split('/')[1:]):
            raise RuntimeError('fixture path must be canonical absolute spelling')
        candidate = real_path(value)
        if not (candidate.is_relative_to(PACKAGE) or candidate.is_relative_to(scratch)):
            raise RuntimeError('unmapped host path outside explicit package/scratch roots')
        return candidate
    with tempfile.TemporaryDirectory(prefix='.entry-export-fixture-', dir=Path.cwd()) as temporary:
        scratch = Path(temporary)
        (scratch / 'fixtures').mkdir()
        (scratch / 'SOURCE-GRAPH-v1.json').write_bytes((PACKAGE / 'SOURCE-GRAPH-v1.json').read_bytes())
        fixture.BASE = scratch
        fixture.Path = fixture_path_binding
        for historical, mapped in paths.items():
            if fixture_path_binding(historical) != mapped:
                raise RuntimeError('historical input mapping failed')
            try:
                fixture_path_binding(historical, 'extra-child')
            except RuntimeError:
                pass
            else:
                raise RuntimeError('historical path extra-part bypass')
        for refused in ('/home/d3lerium/not-a-mapped-copy', '/etc/passwd', '/tmp/unowned-entry-fixture', str(scratch) + '/../outside'):
            try:
                fixture_path_binding(refused)
            except RuntimeError:
                pass
            else:
                raise RuntimeError('unmapped host path accepted')
        owned = str(scratch / 'fixtures' / 'new-owned-file')
        if fixture_path_binding(owned) != real_path(owned):
            raise RuntimeError('owned fixture path refused')
        print('PASS_ADAPTER_PATH_BOUNDARY exact_mappings=15 extra_parts_refused=15 unknown_paths_refused=4 owned_path=PASS', flush=True)
        suite = unittest.defaultTestLoader.loadTestsFromModule(fixture)
        if suite.countTestCases() != 12:
            raise RuntimeError('exact twelve frozen NEW methods required')
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            return 1
    print('PASS_TWELVE_FROZEN_NEW_ENTRY_METHODS optimized=' + str(sys.flags.optimize), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
