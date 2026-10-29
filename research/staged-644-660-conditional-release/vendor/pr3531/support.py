# SPDX-License-Identifier: Apache-2.0
# Bootstrap extraction adapted from dataisfire PR3361 with OpenAI Codex assistance.
import ast,hashlib,json,textwrap,types
from pathlib import Path
from fractions import Fraction as Q

def need(ok,why):
    if not ok:raise ValueError(why)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())
def save(path,value):path.write_bytes((json.dumps(value,indent=2,sort_keys=True)+'\n').encode())
def load(path,name):
    m=types.ModuleType(name);m.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m

def authenticate(root,package):
    global ROOT,SUPPLIER,BASE
    ROOT=root;SUPPLIER=ROOT/'research/gmx-t74-borrow43-handoff';BASE=ROOT/'research/coupled-carrier-cap740'
    need(sha(package/'SOURCES.json')=='30fc7635c08820a54f4b34485cbbfc154cacd97c6a484b52f182c77a9bc45189','complete source manifest and usage classes')
    for item in read(package/'SOURCES.json')['files']:
        if item['usage']=='input':need(sha(ROOT/item['path'])==item['sha256'],'source drift: '+item['path'])
    need(sha(package/'vendor/PR3361-CLAIM.json')=='43aadbe1181516c97ea7f12c65e65ee757df08ead084a9cbbd48a46ed6c59089','exact local baseline claim')
    manifest=read(BASE/'MANIFEST.json')
    need({p.relative_to(BASE).as_posix():sha(p) for p in BASE.rglob('*') if p.is_file() and p!=BASE/'MANIFEST.json'}==manifest,'complete supplier inventory')
def bootstrap(C):
    source=(SUPPLIER/'code/assemble.py').read_text()
    node=next(n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.FunctionDef) and n.name=='_outer_witness_raw')
    body=textwrap.dedent('\n'.join(source.splitlines()[node.lineno-1:node.end_lineno])+'\n')
    E=ROOT/'research/adaptive-kernel-demotion/vendor/engines/outer.py'
    need(sha(E)=='c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c','47-row engine')
    env=dict(Q=Q,mpz=int,hashlib=hashlib,PAYLOAD=2048,c=Q('0.001733427039589844234749'),
             SPEC=dict(outer_refinement=dict(endpoint_digits=35,grid_digits=29,margin_digits=39,bootstrap_steps=12)),
             A=load(E,'retained_assembly'))
    exec(compile(body,'<retained _outer_witness_raw>','exec'),env)
    k,cuts,outer,controls=env['_outer_witness_raw'](C)
    need(len(outer['strict_constraints'])==47 and all(v>0 for v in outer['strict_constraints'].values()),'all47 bootstrap constraints')
    need(len(cuts)==13 and len(controls)==4,'12 steps and four original controls')
    return dict(legacy_balanced_kappa=str(k),cutoffs=cuts,controls=controls,
                strict_constraints={n:str(v) for n,v in outer['strict_constraints'].items()})
