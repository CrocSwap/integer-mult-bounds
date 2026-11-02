# SPDX-License-Identifier: Apache-2.0
"""Only new AST-extracted fixture functions; all operations remain fake."""
from pathlib import Path
import importlib.util
import sys
import unittest
ROOT = Path(__file__).resolve().parent
BLOCKED = {'epoch_schema_v5','epoch_copy_v5','parent_domain_v1','parent_closure_v1','parent_completion_v1','h25_parent_supervisor','group01_evidence_v1','v03_prefix_supervisor_v1','v03_prefix_derivation_v1','v03_integrated_constructor_v1','v03_integrated_constructor_v2'}

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def main():
    if BLOCKED & set(sys.modules):
        raise RuntimeError('archived module already imported')
    load('prefix_export_archive_checker', ROOT / 'verify.py').check()
    base = ROOT / 'unit05'
    proposal = load('prefix_new_supplied_fixture_runner', base / 'fixtures/run_proposal_pure_tests_v1.py')
    proposal.BASE = base
    proposal.IMPL = base / 'implementation'
    try:
        proposal.main()
    except SystemExit as result:
        if result.code != 0:
            raise
    orchestration = load('prefix_new_orchestration_fixture', base / 'fixtures/test_new_orchestration_v2.py')
    orchestration.BASE = base
    orchestration.IMPL = base / 'implementation'
    suite = unittest.defaultTestLoader.loadTestsFromModule(orchestration)
    if suite.countTestCases() != 13:
        raise RuntimeError('expected13new orchestration methods')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.testsRun != 13 or not result.wasSuccessful():
        return 1
    if BLOCKED & set(sys.modules):
        raise RuntimeError('archived runtime import boundary violated')
    print('PASS_PREFIX_SUPERVISION_NEW_FIXTURES methods=23 optimized=' + str(sys.flags.optimize), flush=True)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
