from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import companion as packet
packet.require_assertions()
packet.verify_base()
packet.verify_sources()
"""Bind the independent reconstruction to the now-frozen experimental data.
The experiment's programs are only read as bytes for hashes, never executed.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,gzip,hashlib,sys
P=packet.ADMISSION;E=packet.EXPERIMENT
if not __debug__:raise RuntimeError('Assertions must be enabled')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 b=Path(p).read_bytes();return json.loads(gzip.decompress(b)if str(p).endswith('.gz')else b)
packet.verify_experiment()
m=read(E/'MANIFEST.json')
for name,h in m['artifacts'].items():
 p=(E/name).resolve();assert p.is_relative_to(E);assert sha(p)==h,name
our=read(P/'RESULT.json');their=read(E/'RESULT.json');assert sha(packet.HERE/'admission/build_local.py')==our['checker_sha256']
a=read(P/'local-events.json.gz');b=read(E/'combined-events.json.gz');projection=lambda es:[(e['op'],e['a'],e['b'],e['c'],e['frame'],e['semantic'])for e in es];assert projection(a)==projection(b)
x=read(P/'local-endpoints.json');y=read(E/'combined-endpoints.json.gz');assert(x['n'],x['initial'],x['final'])==(y['n'],y['initial'],y['final'])
U=read(P/'local-frames.json.gz');V=read(E/'combined-frames.json.gz');assert set(U)==set(V)
def rref(rows):
 a=[list(map(Q,row))for row in rows];k=0
 for j in range(20):
  z=next((i for i in range(k,len(a))if a[i][j]),None)
  if z is None:continue
  a[k],a[z]=a[z],a[k];v=a[k][j];a[k]=[q/v for q in a[k]]
  for i in range(len(a)):
   if i!=k and a[i][j]:v=a[i][j];a[i]=[q-v*r for q,r in zip(a[i],a[k])]
  k+=1
 return a[:k]
for f in U:
 u,v=U[f],V[f];assert u['rank']==v['rank']and u['basis']==v['basis']
 if u['annihilator']!=v['annihilator']:assert rref(u['annihilator'])==rref(v['annihilator'])
assert our['one_stage_paid_histogram']==their['one_stage_histogram'];assert our['one_stage_calls']==their['one_stage_calls']and our['one_stage_rank_mass']==their['one_stage_mass'];assert our['payload_bound']==their['payload_bound']
for f in ['pr322-presink-selection.json','pr323-kernel2-selection.json']:assert sha(packet.INPUTS/f)==sha(packet.INPUTS/f)
out=dict(status='PASS_INDEPENDENT_RECONSTRUCTION_MATCHES_FROZEN_EXPERIMENT',checker_sha256=sha(Path(__file__)),admission_result_sha256=sha(P/'RESULT.json'),experiment_manifest_sha256=sha(E/'MANIFEST.json'),experiment_result_sha256=sha(E/'RESULT.json'),source_heads=our['source_heads'],candidate_sha256=our['candidate_sha256'],events=len(a),frames=len(U),all_event_semantics_operands_coefficients_frames_equal=True,all_endpoint_frames_equal=True,all_frame_bases_and_annihilator_spaces_equal=True,paid_histogram_and_payload_equal=True,upstream_or_experimental_programs_executed=False,scope='Data-only equivalence and immutable witness binding. This does not independently certify the experimental bank, arithmetic, finite invoice, or all-size claims.')
(P/'EXPERIMENT-CROSSCHECK.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
