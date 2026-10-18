"""Exact regression for the repaired colour helper; no new F-star theorem."""
from pathlib import Path
from itertools import product
import hashlib, importlib.util, json, platform, subprocess, sys, time
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');pkg=P/'sources/2869/research/fstar-entry-class-scope-seed63d5f999'
def need(x,msg):
    if not x:raise ValueError(msg)
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def acyclic(pred,vertices):
    remaining=set(vertices)
    while remaining:
        roots=[v for v in remaining if not any(pred[v]>>u&1 for u in remaining)]
        if not roots:return False
        remaining.difference_update(roots)
    return True
def brute(pred,allowed):
    for colours in product(range(3),repeat=len(pred)):
        if not all(allowed[v]>>c&1 for v,c in enumerate(colours)):continue
        if all(acyclic(pred,[v for v,c in enumerate(colours) if c==j]) for j in range(3)):return True
    return False
start=time.monotonic();m=load(pkg/'verify.py','fixed_fstar')
old=load(P/'prior-revisions/2869-original/research/fstar-entry-class-scope-seed63d5f999/verify.py','old_fstar')
crown=[168,84,162,81,138,69,42,21]
need(old.chi_le3_backtrack(crown,8)==(False,False),'baseline control')
need(brute(crown,[7]*8) and m.chi_le3_backtrack(crown,8)==(True,False),'crown fix')
count=0
edges=[(u,v) for u in range(3) for v in range(3) if u!=v]
for bits in range(1<<len(edges)):
    pred=[0]*3
    for i,(u,v) in enumerate(edges):
        if bits>>i&1:pred[v]|=1<<u
    # Cache legal assignments once; compare all nonempty colour-list choices.
    valid=[cols for cols in product(range(3),repeat=3) if all(acyclic(pred,[v for v,c in enumerate(cols) if c==j]) for j in range(3))]
    for allowed in product(range(1,8),repeat=3):
        expected=any(all(allowed[v]>>c&1 for v,c in enumerate(cols)) for cols in valid)
        need(m.chi_le3_backtrack(pred,3,allowed=list(allowed),budget=10000)==(expected,False),'small-graph/list decision')
        count+=1
need(count==21952,'coverage')
need(m.chi_le3_backtrack(crown,8,budget=0)==(None,True),'budget0')
need(m.chi_le3_backtrack(crown,8,budget=1)==(None,True),'budget1')
need(m.chi_le3_backtrack([0],1,allowed=[0])==(False,False),'empty list')
source=json.loads((pkg/'SOURCES.json').read_text());bindings=[]
for rec in source['files']:
    if rec['usage']!='input':continue
    spec=source['base_commit']+':'+rec['path'];raw=subprocess.check_output(['git','show',spec],cwd=R)
    need(raw==(pkg.parents[1]/rec['path']).read_bytes(),'input bytes')
    need(hashlib.sha256(raw).hexdigest()==rec['sha256'],'input hash');bindings.append(rec['path'])
# Authenticate the copied numerical fixtures against their credited sources.
fixture_sources=[
 ('tied_min.json','98da76c2839ba38538b510420dec54546ccabf0b','research/three-total-classical-configs/data/tied_min.json'),
 ('cex_min_1.json','98da76c2839ba38538b510420dec54546ccabf0b','research/three-total-classical-configs/data/cex_min_1.json'),
 ('cex_min_1.B22.json','7aed56bd440a3d8cbca8028cf2cbd0888c07d9b3','research/fstar-proof-lemmas-seed3096ed3f/data/cex_min_1.B22.json'),
 ('cex_min_1.witness.json','7aed56bd440a3d8cbca8028cf2cbd0888c07d9b3','research/fstar-proof-lemmas-seed3096ed3f/data/cex_min_1.witness.json'),
]
fixture_bindings=[]
for name,commit,path in fixture_sources:
    raw=subprocess.check_output(['git','show',commit+':'+path],cwd=R)
    need(raw==(pkg/'data'/name).read_bytes(),'original fixture bytes')
    fixture_bindings.append(dict(name=name,commit=commit,path=path,sha256=hashlib.sha256(raw).hexdigest()))
# All regenerated scientific fields must match the author certificate. This
# comparison is run only AFTER the full repaired primary command has completed.
head=json.loads((P/'2869.json').read_text())['headRefOid'];rel='research/fstar-entry-class-scope-seed63d5f999/CERTIFICATE.json'
original=json.loads(subprocess.check_output(['git','show',head+':'+rel],cwd=R))
fresh=json.loads((pkg/'CERTIFICATE.json').read_text());need(original==fresh,'complete regenerated scientific certificate differs')
detail=dict(original_fixture_bindings=fixture_bindings,crown_baseline_false_negative_reproduced=True,all_three_vertex_directed_graphs_and_nonempty_lists=count,budget_controls=2,empty_list_control=True,original_input_bindings=bindings,complete_certificate_semantic_equality=True)
log=P/'check-2869-supplement.log';log.write_text(json.dumps(dict(status='PASS',**detail),sort_keys=True)+'\n')
d=dict(number=2869,head=head,status='passed',seconds=time.monotonic()-start,commands=[dict(argv=[sys.executable,str(Path(__file__).resolve())],exit_code=0)],input_sha256={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),pkg/'verify.py',pkg/'CERTIFICATE.json',pkg/'SOURCES.json']},log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),environment=dict(python=sys.version,platform=platform.platform()),details=detail,scope='Source-bound exact regression for general colour helper and full certificate equality; no census/CP-SAT optimality or general F-star claim.')
(P/'check-2869-supplement.json').write_text(json.dumps(d,indent=2)+'\n');print('2869 PASS colouring regression and complete scientific certificate comparison',flush=True)
