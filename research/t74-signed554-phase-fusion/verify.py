"""Fresh native admission and conditional classical-matrix outer composition.

No native reuse flags. All execution happens outside the immutable package.
"""
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
assert __debug__, 'assertions required'
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);args=ap.parse_args()
work=args.work.resolve();assert not work.exists() and not work.is_relative_to(P)
def rd(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pins=rd(P/'MANIFEST.json');actual={p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p!=P/'MANIFEST.json'}
assert actual==set(pins),'package file inventory'
for rel,h in pins.items():assert sha(P/rel)==h,rel
for rel,h in rd(P/'SOURCE-PINS.json')['files'].items():assert sha(P/rel)==h,rel
work.mkdir();(work/'tmp').mkdir()
# The unchanged predecessor tools rewrite copies of their input receipts.
# Stage a byte-identical writable view, keeping the publication source immutable.
source=P;P=work/'source';shutil.copytree(source,P,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
for f in P.rglob('*'):f.chmod(0o755 if f.is_dir() else 0o644)
P.chmod(0o755)
for rel,h in pins.items():assert sha(P/rel)==h,rel
env=dict(os.environ,TMPDIR=str(work/'tmp'),PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
for key in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD','WITNESS_SPEC'):env.pop(key,None)
stages=[]
def run(name,script,*argv,cwd=None):
    start=time.monotonic();log=work/(name+'.log')
    with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,argv)],cwd=cwd or work,env=env,stdout=f,stderr=subprocess.STDOUT)
    stages.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)))
    (work/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n')
    assert r.returncode==0,(name,log.read_text()[-5000:]);print('PASS',name,flush=True)
V=P/'vendor/pr1319'
run('literal-signed-recipe',P/'check_recipe.py','--out',work/'RECIPE-CONTROLS.json')
run('retained-parent',V/'vendor/pr1297/verify.py','--work',work/'parent')
assert rd(work/'parent/RESULT.json')['status']=='PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION'
run('reconstruct-owners',V/'reconstruct.py','--out',work/'rebuilt-owners')
for n in ('OWNERS.json.gz','DISPATCH.json'):assert rd(work/'rebuilt-owners'/n)==rd(P/'data'/n),n
for n in ('ORDER.json','PROFILE.json'):assert rd(work/'rebuilt-owners'/n)==rd(V/n),n
run('lift-parent',V/'lift_parent.py','--owners',work/'rebuilt-owners','--out',work/'rebuilt-parent')
for n in ('GLOBAL-TEMPLATE.json.gz','CONSTRUCTION.json'):assert rd(work/'rebuilt-parent'/n)==rd(P/'data'/n),n
# Gzip streams differ across Python/zlib versions; the owner payload was
# compared above. Normalize only its two explicitly checked container hashes.
rebuilt=rd(work/'rebuilt-parent/PLAN.json');expected=rd(V/'PLAN.json')
for plan,owners in [(rebuilt,work/'rebuilt-owners/OWNERS.json.gz'),(expected,V/'OWNERS.json.gz')]:
    h=sha(owners);assert plan['assignment_sha256']==plan['replica_lift']['owners_file_sha256']==h
    plan['assignment_sha256']=plan['replica_lift']['owners_file_sha256']='PAYLOAD_COMPARED_ABOVE'
assert rebuilt==expected
layout=work/'parent/layout';src=layout/'joint1148-round45/source';native={}
for name in ('gauge44','extra'):
    word=P/f'inputs/{name}-word.json.gz';dest=work/('native-'+name)
    run('independent-raw-'+name,src/'research/gauge44-slots/independent/audit_local.py','--word',word,'--main',src,'--output',work/('INDEPENDENT-'+name+'.json'))
    run('leaver-premise-'+name,V/'vendor/pr1297/premise/premise_check.py',word)
    run('fresh-native-'+name,src/'research/k8-eight-ends/replay_native.py',word,dest,cwd=layout)
    assert rd(dest/'local/FULL-WORD.json.gz')==rd(word)
    steps=rd(dest/'STEPS.json');assert [x['step']for x in steps]==['native','ledgers','local-replay','wrappers','phases'] and all(x['exit_code']==0 for x in steps)
    native[name]=dest
run('rebind',P/'vendor/pr1625/rebind.py',V,native['gauge44']/'local',native['extra']/'local',work/'data')
stable=('LOCAL-CHECKS.json','CLIFFORD-RECIPES.json','RESIDUAL-ADAPTERS.json')
def view(plan):
    plan=json.loads(json.dumps(plan))
    for desc in plan['provider_registry'].values():desc['artifact_sha256']={n:h for n,h in desc['artifact_sha256'].items() if n in stable}
    return plan
assert view(rd(work/'data/PLAN.json'))==view(rd(P/'data/PLAN.json'))
assert rd(work/'data/PROFILE.json')==rd(P/'data/PROFILE.json')
for n in ('PLAN.json','SPEC.json'):shutil.copy2(P/'data'/n,work/'data'/n)
runtime=layout/'packing74-signed554';runtime.mkdir();(runtime/'inputs').mkdir()
for n in ('replay.py','freeze_spec.py','audit_mixed.py','independent_core.py','geometry_controls.py'):shutil.copy2(V/n,runtime/n)
for n in ('code','construction'):shutil.copytree(V/n,runtime/n)
shutil.copy2(V/'inputs/PR589-EXPECTED.json',runtime/'inputs/PR589-EXPECTED.json')
shutil.copytree(native['extra'],runtime/'native-extra')
run('strict-t74',runtime/'replay.py','--data',work/'data','--work',work/'strict','--local',native['gauge44']/'local')
strict=rd(work/'strict/RESULT.json');spec=rd(P/'data/SPEC.json');supplier=rd(P/'outer/SUPPLIER.json')
assert strict['status']=='PASS_STRICT_MIXED_T74_EXACT_FILL' and strict['kappa']==supplier['expected']['kappa']==spec['expected']['kappa']
assert strict['independent']['profile']==supplier['expected']['global_profile']==spec['expected']['global_profile']
assert supplier['expected']['complex_lower']==spec['expected']['complex_lower']
run('geometry',runtime/'geometry_controls.py','--source',src/'research/complex-k492-owner-repair/vendor/multicold','--strict',work/'strict','--out',work/'GEOMETRY-CONTROLS.json')
assert len(rd(work/'GEOMETRY-CONTROLS.json')['rejected'])==6
run('original-outer-evidence',P/'vendor/pr1673/verify.py')
shutil.copytree(P/'outer',work/'outer')
run('composed-outer-ledger',work/'outer/check_outer.py')
run('separate-balance-derivation',work/'outer/independent_balance.py','--out',work/'BALANCE.json')
strassen=rd(work/'outer/FRONTIER-FUSION-ARITHMETIC.json');old_balance=rd(work/'BALANCE.json')
assert strassen['rows']['strassen']['kappa']['rational']==old_balance['kappa']=='20965020084289/12500000000000000'
run('classical-matrix-ledger',work/'outer/check_classical.py')
run('separate-classical-balance',work/'outer/independent_classical.py','--out',work/'CLASSICAL-BALANCE.json')
outer=rd(work/'outer/CLASSICAL-BOUNDARY-ARITHMETIC.json');balance=rd(work/'CLASSICAL-BALANCE.json')
assert outer['rows']['classical_matrix_12_5']['kappa']['rational']==balance['kappa']
from fractions import Fraction
claim=Fraction('0.001677641731343354');assert claim<Fraction(balance['kappa'])
ind=dict(strict['independent']);ind.pop('input_sha256')
math=dict(status='PASS_FRESH_SIGNED554_T74_CLASSICAL_MATRIX_COMPOSITION',kappa=str(claim),kappa_decimal='0.001677641731343354',traditional_kappa=strict['kappa'],manifest_sha256=sha(P/'MANIFEST.json'),independent=ind,recipe=rd(work/'RECIPE-CONTROLS.json'),balance=balance,outer=outer['rows']['classical_matrix_12_5'],outer_controls=outer['rejecting_controls']['classical_matrix_12_5'],native_reuse=False,scope='Conditional composition with PR1673 outer theorem. All inherited all-size compiler, common-label, mutable-source, hosting, precision C1=1, fixed-tape, prime-packing, equal-chunk interchange, exact-recovery and analytic assumptions remain. The established Le Gall 2014 bound omega<2.3728639 supplies a fixed matrix exponent 12/5 via PR1673 effective stability lemma; no omega<=9/4 premise is used.')
(work/'MATH.json').write_text(json.dumps(math,sort_keys=True,indent=2)+'\n')
(work/'RESULT.json').write_text(json.dumps(dict(status=math['status'],kappa=math['kappa'],kappa_decimal=math['kappa_decimal'],math_sha256=sha(work/'MATH.json'),stages=stages),indent=2)+'\n')
print(math['status'],math['kappa_decimal'],flush=True)
