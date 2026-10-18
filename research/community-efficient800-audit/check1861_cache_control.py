import importlib.util,json,pathlib
root=pathlib.Path('/tmp/pr-efficient800/sources/1861')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
v=load('new1861',root/'scripts/binary_phase_frames.py');old=load('old1861',root/'research/parity-side-basis-cache/baseline.py')
v._basis_cached.cache_clear()
try:old.basis((1.0,))
except AssertionError:pass
else:raise AssertionError('baseline unexpectedly accepted')
try:v.basis((1.0,))
except AssertionError:pass
else:raise AssertionError('cold cache unexpectedly accepted')
assert v.basis((1,))==(1,)
assert v.basis((1.0,))==(1,)
print(json.dumps({'baseline_rejects_float':True,'new_cold_cache_rejects_float':True,'new_warm_cache_accepts_float':True,'reason':'Tuple cache key equality bypasses validation inside cached function.'}))
