from pathlib import Path
from fractions import Fraction as Q
import json,gzip,hashlib,importlib.util
P=Path('pr378-donor-screen');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
price=json.load(open(P/'signed25-donor-screen.json'));integration=json.load(open(P/'signed25-integration.json'));bitpath=Path('pr386-phase-screen/fresh/COMBINED.json');bit=json.load(open(bitpath))
raw=gzip.decompress((P/'signed25-bound-template.json.gz').read_bytes());assert hashlib.sha256(raw).hexdigest()==integration['template_sha256'];t=json.loads(raw)
assert price['candidate_sha256']==integration['candidate_sha256']==sha(P/'signed25-donor-candidate.json.gz')
assert price['profile']==integration['paid_profile'] and bit['two_rational_engines'] and bit['next_bit_grid_rejected']
b=Q(price['conditional_component_coarse']);c=Q(bit['bit_coarse']);assert b<c
assert bit['finite']['row_coefficient']<20161 and integration['invoice']['row']<20161 and int(bit['finite']['two_level_coefficient'])<1<<30000
spec=importlib.util.spec_from_file_location('candidate_refine',P/'refine_candidate.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);r=mod.refine(b,c)
saving=Q(r['degraded_bit_saving']);old=Q(384599,10**10);cuts=[]
def ceilq(q):return -((-q.numerator)//q.denominator)
for raw in r['bootstrap_chain'][1:]:
 z=Q(raw);gap=min(saving-z,1-z-saving,1-z-saving*(1-old),1-saving);assert gap>0
 cutoff=max(1,ceilq(36/gap**2),ceilq(2*(4+(int(bit['finite']['two_level_coefficient'])-1).bit_length())/gap))
 assert Q(cutoff)*gap**2>=36 and Q(cutoff)*gap>=2*(4+(int(bit['finite']['two_level_coefficient'])-1).bit_length())
 cuts.append(dict(gap=str(gap),log2_cutoff=str(cutoff)));old=z
reported=Q('0.001001090245731051');r.update(status='PASS_CANDIDATE_EXACT_OUTER_ASSEMBLY_PENDING_STANDALONE_REPLAY',finite_bootstraps=cuts,reported395_kappa=str(reported),difference_from_reported395=str(Q(r['kappa'])-reported),input_pins={str(f):sha(f) for f in [P/'signed25-donor-screen.json',P/'signed25-integration.json',bitpath,P/'refine_candidate.py',Path('pr370-e8-screen/code/pricing/outer.py')]},scope='Candidate arithmetic from reconstructed signed25 donor emission and source-bound checked386 bit. Six-round grid ceiling only, no global optimality. Retains all-size local recursive-child, Clifford/common-grid/tape/bank/precision and analytic interfaces. No Lean theorem. Publication requires standalone replay and novelty check.')
assert Q(r['kappa'])>reported
(P/'signed25-assembly.json').write_text(json.dumps(r,indent=2));print(r['status'],r['kappa'],r['difference_from_reported395'])
