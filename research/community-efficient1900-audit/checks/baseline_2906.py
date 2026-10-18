from pathlib import Path
import importlib.util,unittest
P=Path('/tmp/pr-efficient1900');f=P/'combined-2906/tests/test_exit_cleanup_macos.py';s=importlib.util.spec_from_file_location('native_observer',f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.RUNNER=P/'baseline-runner2906.py'
r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(m))
expected={'test_cleanup_denial_cannot_report_success','test_cleanup_finishes_before_next_queued_module','test_failure_stops_exited_leaders_child_and_grandchild','test_success_stops_exited_leaders_child_and_grandchild'}
if r.testsRun!=6 or r.errors or r.skipped or {t._testMethodName for t,_ in r.failures}!=expected:raise RuntimeError('baseline falsification differs')
print('PASS_BASELINE_FALSIFICATION exactly_four_expected_failures no_skip no_error')
