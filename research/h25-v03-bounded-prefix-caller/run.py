#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run exactly frozen NEW-only controls with package/owned-fixture path bindings."""
from pathlib import Path
import importlib.util
import json
import sys
import tempfile
from types import ModuleType
import unittest

PACKAGE = Path(__file__).resolve().parent


def need(ok, message):
    if ok is not True:
        raise RuntimeError(message)


def main():
    spec = importlib.util.spec_from_file_location('bounded_caller_export_integrity', PACKAGE / 'verify.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    checker.main()
    fixture_path = PACKAGE / 'archive/unit07/fixtures/caller_new_controls_v1.py'
    # No original source is imported. The exact frozen fixture itself controls
    # extraction of only NEW prefix/helpers and NEW fake-base subclass code.
    fixture = ModuleType('bounded_caller_frozen_new_controls')
    fixture.__file__ = str(fixture_path)
    exec(compile(fixture_path.read_bytes(), str(fixture_path), 'exec', dont_inherit=True, optimize=sys.flags.optimize), fixture.__dict__)
    need(fixture.UNIT == PACKAGE / 'archive/unit07' and fixture.F == PACKAGE / 'archive', 'fixture relative path binding')
    need(fixture.CALLER == PACKAGE / 'archive/unit07/implementation/run_queue4_prefix_v2.py', 'fixture caller binding')
    need(not fixture.BLOCKED.intersection(sys.modules), 'original runtime module present')
    adapter = json.loads((PACKAGE / 'PATH-ADAPTER-v1.json').read_bytes())
    translations = {original: PACKAGE / relative for original, relative in adapter['exact_source_translations'].items()}
    real_path = Path
    with tempfile.TemporaryDirectory(prefix='bounded-caller-replay-', dir='/tmp') as temporary:
        scratch = real_path(temporary)
        need(not scratch.is_relative_to(PACKAGE), 'scratch inside package')
        def path_binding(value, *extra):
            if type(value) is not str or extra:
                raise RuntimeError('one exact path string; no extra components')
            if value in translations:
                return translations[value]
            if not value.startswith('/') or not all(32 <= ord(c) < 127 for c in value) or any(p in ('', '.', '..') for p in value.split('/')[1:]):
                raise RuntimeError('canonical absolute path required')
            candidate = real_path(value)
            if not candidate.is_relative_to(scratch):
                raise RuntimeError('unknown host path outside owned scratch')
            return candidate
        for original, target in translations.items():
            need(path_binding(original) == target, 'source origin translation')
            for altered in ((original, 'extra'), (original + '/extra',)):
                try:
                    path_binding(*altered)
                except RuntimeError:
                    pass
                else:
                    raise RuntimeError('source path extra-component bypass')
        for unknown in ('/etc/passwd', '/home/d3lerium/unmapped-source', '/tmp/unowned-caller-replay', temporary + '/../outside'):
            try:
                path_binding(unknown)
            except RuntimeError:
                pass
            else:
                raise RuntimeError('unknown host path accepted')
        need(path_binding(str(scratch / 'owned')) == scratch / 'owned', 'owned path binding')
        print('PASS_PATH_BINDINGS exact_sources=' + str(len(translations)) + ' extra_components=REFUSED unknown_host_paths=REFUSED', flush=True)
        # Path binding only: frozen algorithms and expected values are untouched.
        # This adapter is not a Python sandbox; the source-authenticated fixture
        # supplies the closed NEW-only extraction/execution boundary.
        fixture.Path = path_binding
        previous_tempdir = tempfile.tempdir
        tempfile.tempdir = str(scratch)
        try:
            suite = unittest.defaultTestLoader.loadTestsFromModule(fixture)
            need(suite.countTestCases() == 11, 'exact eleven frozen NEW methods required')
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            if not result.wasSuccessful():
                return 1
        finally:
            tempfile.tempdir = previous_tempdir
    need(not fixture.BLOCKED.intersection(sys.modules), 'original runtime module after replay')
    # Authenticate the final packet again after owned-file cleanup; no new log,
    # pycache or fixture output may have appeared inside it.
    checker.main()
    print('PASS_ELEVEN_FROZEN_NEW_CALLER_METHODS optimized=' + str(sys.flags.optimize) + ' original_runtime_executed=False', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
