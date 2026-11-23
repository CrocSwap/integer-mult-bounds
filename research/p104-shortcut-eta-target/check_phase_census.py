"""Observe bounded phase-circuit calls in a fresh target compiler construction."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json,sys
root=Path(sys.argv[1]).resolve(); runtime=root/'runtime'
assert sha256((runtime/'installations.py').read_bytes()).hexdigest()=='5df81fddba26013b142195f5c3119491fa2f07b1e72c3616ae76e7d7ffbb0fd1'
sys.path.insert(0,str(runtime))
from upstream import install
install()
import phase_atlas
actual=phase_atlas.matrix_element
counts=Counter();max_gates=max_paths=0;max_n=0

def measure(circuit,n,source,target):
 global max_gates,max_paths,max_n
 paths=sum(g[0]=='C' for g in circuit)
 counts[(n,len(circuit),paths)]+=1
 max_gates=max(max_gates,len(circuit));max_paths=max(max_paths,paths);max_n=max(max_n,n)
 return actual(circuit,n,source,target)
phase_atlas.matrix_element=measure
from band_product import prepare_native
layers=prepare_native()
assert len(layers)==2 and len(layers[0])+len(layers[1])==7
assert max_n==9 and max_gates<128 and max_paths<128 and sum(counts.values())<2**20
print(json.dumps({'calls':sum(counts.values()),'max_qubits':max_n,'max_circuit_gates':max_gates,'max_path_variables':max_paths,
 'distinct_shapes':len(counts),'top_shapes':[{'qubits':n,'gates':l,'paths':p,'calls':v} for (n,l,p),v in counts.most_common(10)],
 'scope':'Instrumented finite constructor execution; recorded maxima do not by themselves prove a uniform compiler action bound.'},indent=2,sort_keys=True))
