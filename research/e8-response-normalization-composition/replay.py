"""Fresh PR401 component replay on the source-bound improved ordinary word.
Unchanged upstream programs, explicit fresh phase provenance, no source edits.
Finite research evidence only. OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import gzip,json,os,subprocess,sys,time
import candidate
assert __debug__
sys.dont_write_bytecode=True
SRC,ORD,OUT=map(lambda p:Path(p).resolve(),sys.argv[1:]);assert not OUT.exists();OUT.mkdir(parents=True)
NATIVE=ORD/'work/complex-nine-native';P=OUT/'reconstruction'
sha=lambda p:sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def write(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
manifest=read(SRC/'MANIFEST.json')['files']
def inventory():return {p.relative_to(SRC).as_posix():sha(p)for p in SRC.rglob('*')if p.is_file()and p!=SRC/'MANIFEST.json'}
assert inventory()==manifest
assert sha(SRC/'MANIFEST.json')=='5ff08a6c7b051d227fcd516542b56718ae65bca93615acfe09cb8785d8e3f43c'
candidate.prepare(SRC,ORD/'candidate.json',P)
preflight=read(P/'PREFLIGHT.json');candidate=P/'candidate.json'
assert sha(candidate)==preflight['candidate_sha256']=='a93e9b7336157fc1ee42f75fc787de54c1aef480e293e11c16e9db790115ecbc'
ordinary=read(ORD/'VERIFICATION.json');assert ordinary['candidate_sha256']==sha(ORD/'candidate.json')and len(ordinary['stages'])==10
for stage in ordinary['stages']:assert sha(ORD/'logs'/(stage['stage']+'.log'))==stage['log_sha256']
gz=ORD/'work/pr361/complex/gcert1-e8-r783.json.gz';assert gzip.decompress(gz.read_bytes())==(ORD/'candidate.json').read_bytes()
prior=OUT/'fresh-prior-phase';prior.mkdir()
engine=SRC/'local/deps/clifford_exact.py';assert sha(engine)==sha(ORD/'work/odd-stages/clifford_exact.py')
review=read(NATIVE/'CLIFFORD-REVIEW.json');review.update(certificate_sha256=sha(gz),engine_sha256=sha(engine),fresh_original_review_sha256=sha(NATIVE/'CLIFFORD-REVIEW.json'),fresh_ordinary_admission_sha256=sha(ORD/'VERIFICATION.json'))
write(prior/'CLIFFORD-REVIEW.json',review);(prior/'CLIFFORD-RECIPES.json').write_bytes((NATIVE/'CLIFFORD-RECIPES.json').read_bytes())
assert sha(prior/'CLIFFORD-RECIPES.json')==review['recipe_sha256']
signed=ORD/'candidate.json';helper=SRC/'inputs/helper781.json'
canonical=lambda p:sha256(json.dumps(read(p),sort_keys=True,separators=(',',':')).encode()).hexdigest()
reuse=dict(status='FRESH_SOURCE_BOUND_LONG_WORD_PHASE_REPLAY',signed_baseline_raw_sha256=sha(signed),signed_baseline_canonical_sha256=canonical(signed),phase_audited_certificate_gzip_sha256=sha(gz),helper_baseline_raw_sha256=sha(helper),helper_baseline_canonical_sha256=canonical(helper),engine_sha256=sha(engine),prior_review_sha256=sha(prior/'CLIFFORD-REVIEW.json'),prior_recipes_sha256=sha(prior/'CLIFFORD-RECIPES.json'),scope='Fresh ordinary ten-stage admission and exact Gaussian phase replay, augmented only with verified certificate and engine hashes; original review bytes preserved and hashed.')
write(prior/'SOURCE-REUSE.json',reuse)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
for k in list(env):
    if k.startswith(('COMPLEX_','CX_'))or k=='PR315':env.pop(k,None)
stages=[]
def run(name,args):
    t=time.monotonic();print('RUN',name,flush=True)
    with(OUT/(name+'.log')).open('w')as log:subprocess.run(list(map(str,args)),env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    stages.append(dict(name=name,seconds=time.monotonic()-t,log_sha256=sha(OUT/(name+'.log'))));print('PASS',name,flush=True)
def py(name,path,*args):run(name,[sys.executable,'-B',path,*args])
py('local',SRC/'local/local_admit.py',candidate,OUT/'local','--helper-baseline',helper,'--signed-baseline',signed,'--deps',SRC/'local/deps','--prior-phase',prior)
py('independent-helper-tokens',Path(__file__).parent/'response_token_check.py',candidate,OUT/'local/LOCAL-PROGRAMS.json.gz',OUT/'INDEPENDENT-TOKENS.json')
exe=OUT/'phase-replay';run('compile-phase',[env.get('CXX','g++'),'-O2','-std=c++17','-I'+str(SRC/'architecture/deps'),SRC/'architecture/phase-replay.cpp','-o',exe])
py('phase',SRC/'architecture/phase.py',candidate,SRC/'local/deps',exe,OUT/'phase',SRC/'architecture/phase-replay.cpp')
template=NATIVE/'GLOBAL-TEMPLATE.json.gz';data=NATIVE/'DATA-PHASES.json'
py('banks',SRC/'architecture/banks.py',candidate,SRC/'inputs/bank-patterns.json',OUT/'phase/RESIDUALS.json',OUT/'local/LOCAL-PROGRAMS.json.gz',OUT/'local/RESULT.json',template,SRC/'local/deps',OUT/'banks',data)
py('bank-audit',SRC/'architecture/audit.py',OUT/'banks',candidate,OUT/'phase/RESIDUALS.json',OUT/'local/LOCAL-PROGRAMS.json.gz',template)
py('bridge',SRC/'architecture/bridge.py',OUT/'banks')
admission=read(OUT/'banks/ADMISSION.json');audit=read(OUT/'banks/INDEPENDENT-ADMISSION.json');bridge=read(OUT/'banks/BRIDGE.json')
assert audit['template_sha256']==admission['template_sha256']and audit['candidate_sha256']==sha(candidate)
assert(admission['live'],admission['physical'],admission['banks_per_stage'],admission['deficit'])==(14412,15203,748,2496)
assert inventory()==manifest
write(OUT/'RECEIPT.json',dict(status='PASS_FRESH_PR401_LONG_WORD_TRANSPLANT_LOCAL_PHASE_BANKS_AND_FINITE_INTERFACE',candidate_sha256=sha(candidate),source_manifest_sha256=sha(SRC/'MANIFEST.json'),source_unchanged=True,preflight_sha256=sha(P/'PREFLIGHT.json'),ordinary_admission_sha256=sha(ORD/'VERIFICATION.json'),stages=stages,output_sha256={str(p.relative_to(OUT)):sha(p)for p in [OUT/'local/RESULT.json',OUT/'INDEPENDENT-TOKENS.json',OUT/'phase/RESIDUALS.json',OUT/'banks/ADMISSION.json',OUT/'banks/INDEPENDENT-ADMISSION.json',OUT/'banks/BRIDGE.json']},scope='Finite changed construction checked with unchanged pinned PR401 components and fresh exact ordinary phases. No source program edits. The all-size compiler/window/dirty-bank/precision/restored-row/analytic interfaces remain conditional; no unconditional theorem.'))
print('PASS FRESH PR401 NORMALIZATION COMPONENTS',flush=True)
