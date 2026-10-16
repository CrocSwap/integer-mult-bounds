from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import companion as packet
packet.require_assertions()
packet.verify_base()
packet.verify_sources()
"""Independent small verifier of emitted completion and copied-work projectors.
Reads compiler output as inert data. No emitter or upstream module imported.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter
import copy,gzip,hashlib,json
if not __debug__:raise RuntimeError('Assertions required')
P=packet.LOWERING
O=packet.LOWERING;L=packet.ADMISSION
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.name.endswith('.gz') else b)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frames=read(L/'local-frames.json.gz');copies=read(O/'copied-work-projector-overrides.json');phases=read(O/'extended-phases.json')
def check_copy(r):
 old=frames[str(r['old_frame'])]['rank'];new=frames[str(r['new_frame'])]['rank']
 diff=(new-old)*(-1 if r['complement'] else 1)
 assert (old,new,r['rank'])==(18,0,18)
 assert r['difference_orientation']*diff==18
 assert r['difference_orientation']==(1 if r['complement'] else -1)
 assert r['family']==658255
for r in copies:check_copy(r)
assert len(copies)==100 and Counter(x['stage'] for x in copies)=={s:20 for s in range(5)}
bad=copy.deepcopy(next(x for x in copies if not x['complement']));bad['difference_orientation']=1
try:check_copy(bad)
except AssertionError:copy_negative=True
else:raise AssertionError('negative projector accepted')
def check_completion(r):
 s=r['stage'];support=list(range(80,100));assert r['rank']==20 and r['support']==[80,100]
 assert r['family']==230400+(s+1)*85571-1
 assert r['Q_entries']==[[j,j,1] for j in support]
 U=[[0]*20 for _ in range(200)];V=[[0]*200 for _ in range(20)]
 for i,j,v in r['U_entries']:U[i][j]+=v
 for i,j,v in r['V_entries']:V[i][j]+=v
 assert all(sum(V[i][k]*U[k][j] for k in range(200))==-2*int(i==j) for i in range(20) for j in range(20))
 D=[[int(i==j)+sum(U[i][k]*V[k][j] for k in range(20)) for j in range(200)] for i in range(200)]
 want=list(range(200))
 for j in support:want[j],want[199-j]=want[199-j],want[j]
 assert D==[[int(want[i]==j) for j in range(200)] for i in range(200)]
 pi=r['permutation'];inv=r['inverse_permutation'];assert sorted(pi)==sorted(inv)==list(range(100))
 assert all(inv[pi[j]]==j for j in range(100)) and {pi[j] for j in support}==set(range(20))
 assert r['instructions'][0]['matrix']==inv and r['instructions'][2]['matrix']==pi
 for k in(0,1,2,3):assert r['instructions'][k]['family']==r['family']
 assert r['fees']=={'route_movements':2,'selectors':2*(658254+59900),'wrappers':80008,'matrix_preparation':1024000000,'paid_child':1,'all_edge_fallback':320000,'bad_fraction':'1/10^16'}
 return True
cs=[x for x in phases if x['kind']=='paid_bank_completion']
for x in cs:check_completion(x)
assert len(cs)==5
mut=copy.deepcopy(cs[0]);mut['V_entries'][0][2]=1
try:check_completion(mut)
except AssertionError:completion_negative=True
else:raise AssertionError('wrong V coefficient accepted')
out={'status':'PASS_INDEPENDENT_EMITTED_PROJECTOR_AND_DIRECTION_CONTROLS','emitter_result_sha256':sha(O/'RESULT.json'),
 'checker_sha256':sha(Path(__file__)),'positive_copied_work_descriptors':100,'negative_forward_copy_direction_rejected':copy_negative,
 'exact200column_completion_projectors':5,'all_VU_minus2I_checked':True,'wrong_completion_coefficient_rejected':completion_negative,
 'same_bank_route_conjugation_checked':True,'all_completion_fees_checked':True}
(P/'PROJECTOR-CONTROLS.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps(out,indent=2))
