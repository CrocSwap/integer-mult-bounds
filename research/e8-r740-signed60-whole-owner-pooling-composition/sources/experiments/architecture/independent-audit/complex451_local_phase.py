from pathlib import Path
import json,gzip,importlib.util,sys,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2];S=R/'experiments/architecture'/sys.argv[1];D=S/'split-centres';src=R/'experiments/architecture/complex-centre-eight-global/work/odd-stages/clifford_exact.py';spec=importlib.util.spec_from_file_location('independent_clifford',src);C=importlib.util.module_from_spec(spec);sys.modules[spec.name]=C;spec.loader.exec_module(C)
c=json.load(gzip.open(D/'CANONICAL-WORD.json.gz','rt'));recipes=json.load(open(D/'CLIFFORD-RECIPES.json'));n=c['h'];ops=[C.canonical_frame(n,U) for U in c['frames']]
def mon(r):return C.diag(n,r['quadratic_rows'],r['linear_Z4']).then(C.perm(n,r['matrix_rows'])).then(C.xgate(n,r['offset'])).then(C.Op(n,C.identity(n),[('phase',r['phase'])]))
def compiled(r):
 if r['rank']==0:return mon(r['left'])
 return mon(r['right']).then(C.fourier(n,range(r['rank']))).then(mon(r['left']))
for rec in recipes['children']:
 target=ops[rec['old']].adjoint().then(ops[rec['new']]);got=compiled(rec);assert got.tab==target.tab and got.zero_state()==target.zero_state();assert rec['rank']==abs(len(c['frames'][rec['new']])-len(c['frames'][rec['old']]))
for rec in recipes['endpoint_adapters']:
 q=c['ports'][rec['port']];old=C.cgate(n,q) if rec['role']=='source' else C.cgate(n,q).adjoint().then(C.fourier(n));target=old.adjoint().then(ops[rec['frame']]);got=compiled(rec);assert got.tab==target.tab and got.zero_state()==target.zero_state() and rec['rank']==0
out={'status':'PASS_INDEPENDENT_EXPORTED_LOCAL_PHASE_RECIPE_RECONSTRUCTION','children':len(recipes['children']),'endpoint_adapters':len(recipes['endpoint_adapters']),'canonical_frames':len(ops),'method':'Reconstruct supplied monomial/C_r/monomial recipes without calling lower_child; compare exact signed Pauli tableau and integer Gaussian-dyadic zero-state. Tableau equality fixes projective Clifford; zero-state equality fixes global phase.','scope':'Uses pinned exactClifford arithmetic as retained foundation; independently verifies actual exported recipes including globalphase. Physical all-size generalized lifting/compiler/precision remains conditional.','pins':{f:hashlib.sha256((D/f).read_bytes()).hexdigest() for f in ('CANONICAL-WORD.json.gz','CLIFFORD-RECIPES.json')}}
(P/(sys.argv[1].upper()+'-PHASE-RECIPES.json')).write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['children'])
