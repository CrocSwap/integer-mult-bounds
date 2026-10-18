from pathlib import Path
import sys,importlib.util,unittest
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D/'scripts'))
def load(rel,name):
 s=importlib.util.spec_from_file_location(name,D/rel);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
b=load('tests/test_parity_side_basis_cache.py','edge_binary')
j=load('tests/test_joint_frames_cleared_product.py','edge_joint')
suite=unittest.TestSuite([b.ParitySideBasisCacheTests('test_warm_cache_does_not_admit_noninteger_equal_keys'),b.ParitySideBasisCacheTests('test_warm_cache_preserves_boolean_row_type'),j.JointFramesClearedProductTests('test_empty_inner_and_ragged_shapes_retain_reference_semantics'),j.JointFramesClearedProductTests('test_experiment_comparison_rejects_wrong_candidate_after_baseline')])
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():raise SystemExit(1)
old=b.load_baseline();new=b.bpf
for vector in [1,3]:
 if old.contains(iter((1,2)),vector) is not False:raise ValueError('Unexpected historical generator behavior')
 if new.contains(iter((1,2)),vector)!=old.contains((1,2),vector):raise ValueError('New one-shot span membership differs')
print('PASS_FRAME_EDGE_CONTROLS four_tests; contains(one_shot) corrects historical iterator exhaustion; not universal old-API equality')
