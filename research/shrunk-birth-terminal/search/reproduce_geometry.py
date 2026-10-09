#!/usr/bin/env python3
"""Reproduce selected geometry from pinned source plus explicit move witnesses.

Chafik Boukhalfa with OpenAI Codex assistance, Apache-2.0. The immutable
producer retains PR117/125 and the other original notices. This reproduces
our selected endpoint optimization and finite legal placement edits, rather
than rerunning a heuristic search. It checks the entire resulting geometry
against a canonical digest of the independently audited selected fixture.

Descriptive provenance and timing metadata are excluded from that digest;
no equality of pickle bytes is claimed. The full rational physical word and
the final arithmetic are separately verified by the enclosing package.
"""
from pathlib import Path
from collections import Counter,defaultdict
from hashlib import sha256
import argparse,ast,gzip,importlib.util,json,os,pickle,sys,time

if sys.flags.optimize:raise RuntimeError('Assertions must be enabled')
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args();OUT=args.out.resolve();OUT.mkdir(parents=True,exist_ok=False)
start=time.monotonic();last=start;timings={}
def mark(name):
    global last
    now=time.monotonic();timings[name]=now-last;last=now
def read(path):return json.loads(path.read_text())
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def normalize(x):
    if isinstance(x,dict):return {str(k):normalize(v)for k,v in x.items()}
    if isinstance(x,(set,frozenset)):return [normalize(v)for v in sorted(x)]
    if isinstance(x,(list,tuple)):return [normalize(v)for v in x]
    return x
def canonical_geometry(g):
    geo={k:v for k,v in g.items()if k!='base_profile'}
    geo['bytarget']={k:sorted(v)for k,v in geo['bytarget'].items()if v}
    return json.dumps(normalize(geo),sort_keys=True,separators=(',',':')).encode()

imports=read(HERE/'IMPORTS.json')['files']
assert all(sha256((HERE/p).read_bytes()).hexdigest()==r['sha256']for p,r in imports.items())
RUNTIME=HERE/'original-runtime/repo/research/r12-logical-frames'
source=RUNTIME/'screen.py';tree=ast.parse(source.read_text(),filename=str(source))
main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
stage_assignments={'target':'carrier_matching','order':'frame_lifting',
                   'rng':'frame_endpoint_optimization','root_frame':'deferral_placement'}
body=[];seen=set();source_unchanged=sha256(source.read_bytes()).hexdigest()
def marker(name):return ast.Expr(ast.Call(ast.Name('_mark',ast.Load()),[ast.Constant(name)],[]))
for node in main.body:
    name=None
    if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
        name=stage_assignments.get(node.targets[0].id)
    if isinstance(node,ast.ImportFrom)and node.module=='r12_frame_opt':name='role_compilation'
    if isinstance(node,ast.FunctionDef)and node.name=='F0':name='source_values_and_phase_reach'
    if name:
        assert name not in seen;seen.add(name);body.append(marker(name))
    if isinstance(node,ast.Expr)and isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Attribute)and node.value.func.attr=='write_text':
        body.append(marker('F2_and_complete_profile'))
        body.append(ast.Return(ast.Call(ast.Name('locals',ast.Load()),[],[])));break
    body.append(node)
    if isinstance(node,ast.With):body.append(marker('graph_build_and_input_checks'))
assert seen==set(stage_assignments.values())|{'role_compilation','source_values_and_phase_reach'}
main.body=body;ast.fix_missing_locations(tree)
ns={'__file__':str(source),'__name__':'portable_selected_geometry','_mark':mark}
os.environ.update(R12_FRAME_MODE='both_endpoints',R12_FRAME_ROUNDS='8',R12_DEFER_MODE='original')
sys.path.insert(0,str(RUNTIME));exec(compile(tree,str(source)+' [read-only capture with timing markers]','exec'),ns)
d=ns['main']();adapter=load('selected_birth_checkpoint',HERE/'original-runtime/references/birth_checkpoint.py')
adapter.export_checkpoint(d,OUT);g=pickle.loads((OUT/'FRAMES.pkl').read_bytes())
mark('all_input_adapter')
pure=read(HERE/'recipe/expected-pure-geometry.json')
assert sha256(canonical_geometry(g)).hexdigest()==pure['canonical_geometry_sha256'],'Reproduced pure endpoint geometry changed'
inside=ns['sat_contained'];nondeg=ns['sat_nondeg'];basis=ns['sat_basis']
v,h=g['v'],g['h'];m=h*h;ext=m-h

def rebuild():
    bytarget=defaultdict(list);levels=defaultdict(set)
    for s,F in g['placed'].items():
        assert F==basis(F) and nondeg(F) and inside(F,g['U'][g['first'][s]])
        mask=g['reach'][s]
        while mask:
            b=mask&-mask;mask-=b;t=b.bit_length()-1
            assert all(not((x&g['tm'][t]).bit_count()&1)for x in F)
            bytarget[t].append(s);levels[t].add(len(F))
    for t,roles in bytarget.items():
        roles.sort(key=lambda s:(len(g['placed'][s]),s))
        assert all(inside(g['placed'][a],g['placed'][b])for a,b in zip(roles,roles[1:]))
    g['bytarget']=dict(bytarget);H=Counter()
    for s,ds in enumerate(g['chain_dims']):
        ds[0]=len(g['placed'].get(s,()))
        assert all(a<=b for a,b in zip(ds,ds[1:]))
        for a,b in zip(ds,ds[1:]):
            if b>a:H[b-a]+=2*v
        if s in g['terminal']and g['terminal'][s]>=len(g['roots'])-h:H[h-1]+=2*v
        H[h-ds[-1]]+=2*v;H[ext+ds[0]]+=2*v
    for t in range(v):
        ds=sorted(levels[t]|{0,h-1})
        for a,b in zip(ds,ds[1:]):H[b-a]+=2*v
    N=v*v;H[h-1]+=2*N;H[(h-1)**2]+=2*N;H[1]+=N;H.pop(0,None)
    g['histogram']=dict(sorted((r,n)for r,n in H.items()if n));p=g['base_profile']
    assert sum(r*n for r,n in H.items())==p['total_rank']==m*p['W']-p['deficit']
    p.update(child_multiplicities=g['histogram'],deferred_roles=len(g['placed']),
             deferred_dims=dict(Counter(map(len,g['placed'].values()))))

phase_inputs=[('prune','recipe/prune.json','recipe/protected-birth-matches.json.gz'),
              ('coordinates','recipe/coordinates.json','evidence/protected-prune/BIRTH_MATCHES.json.gz'),
              ('expansion','recipe/expansion.json','evidence/protected-coordinates/BIRTH_MATCHES.json.gz')]
for phase,recipe_path,match_path in phase_inputs:
    recipe=read(HERE/recipe_path)
    matches=json.loads(gzip.decompress((HERE/match_path).read_bytes()))
    protected={r['recipient']:tuple(r['birth_frame'])for r in matches['pairs']}
    assert all(g['placed'][s]==F for s,F in protected.items())
    if phase=='prune':
        for row in recipe['removed']:
            s=row['role'];assert s not in protected and len(g['placed'][s])==row['dimension']
            del g['placed'][s]
    else:
        for row in recipe['moves']:
            s=row['role'];assert s not in protected
            assert tuple(row['before'])==g['placed'].get(s,())
            if row['after']:g['placed'][s]=tuple(row['after'])
            else:g['placed'].pop(s,None)
    rebuild();assert all(g['placed'][s]==F for s,F in protected.items());mark(phase+'_recorded_moves_and_complete_frame_checks')
expected=read(HERE/'recipe/expected-geometry.json')
digest=sha256(canonical_geometry(g)).hexdigest();assert digest==expected['canonical_geometry_sha256'],'Entire selected geometry mismatch'
assert sha256(source.read_bytes()).hexdigest()==source_unchanged
(OUT/'FRAMES.pkl').write_bytes(pickle.dumps(g,protocol=4))
record=dict(status='PASS from-source graph and exact selected geometry regeneration',
    canonical_geometry_sha256=digest,selected_fixture_sha256=expected['selected_pickle_sha256'],
    reproduced_pickle_sha256=sha256((OUT/'FRAMES.pkl').read_bytes()).hexdigest(),
    original_runtime_imports_sha256=sha256((HERE/'IMPORTS.json').read_bytes()).hexdigest(),
    wrapper_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
    stage_seconds=timings,total_seconds=time.monotonic()-start,
    scalar_dirty_word_replay='Not repeated here; enclosing selected physical word has separate full exact rational source/dirty and reflection audits.',
    scope='All geometric keys regenerated and compared, excluding descriptive base_profile metadata. Pickle bytes may differ. Explicit recorded legal moves reproduce a selected witness; no heuristic-search or global-optimality claim.')
(OUT/'REPRODUCTION.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n');print(json.dumps(record,indent=2))
