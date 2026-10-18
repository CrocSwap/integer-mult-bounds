from pathlib import Path
import importlib.util,json,hashlib
f=Path('/tmp/pr-efficient800/sources/1763/research/even-target-cnot-census/verify.py')
spec=importlib.util.spec_from_file_location('pr1763',f);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
w=[(g,1,1)for g in[v.B_IDX,v.A_IDX,v.B_IDX,v.A_IDX]]
actual=v.formal_word_value(w,1)
assert v.formal_is_target(actual,1)
assert not v.layer_ok_even_target(w,1)
assert v.layer_sums(w,1)['sum_ba']==1
print(json.dumps({'counterexample':'r=1, N_i=[1], word=baba=(ba)^2=ab','formal_target':True,'claimed_necessary_layer':False,'sums':v.layer_sums(w,1),'verifier_sha256':hashlib.sha256(f.read_bytes()).hexdigest()}))
