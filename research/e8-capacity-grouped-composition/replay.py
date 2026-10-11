"""Fresh capacity215 plus fifteen entrance enlargements on the frozen208 word.
Unchanged PR421/423 constructors, source-bound PR422/421/424 selections and native422 T64 configuration.
Finite research evidence only. OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import gzip,json,os,subprocess,sys,time
import capacity,capacity_source,replicas64,enlarge,enlargement_source,enlarged_runtime,refine
assert __debug__
sys.dont_write_bytecode=True
SRC,S409,PARENT,ORD,OUT,PKG=map(lambda p:Path(p).resolve(),sys.argv[1:]);assert not OUT.exists();OUT.mkdir(parents=True)
sys.path.insert(0,str(PKG));import prefix_source,runtime_adapt,propagation_source
NATIVE=ORD/'work/complex-nine-native';P=OUT/'reconstruction'
sha=lambda p:sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def write(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
BASESRC=PARENT/'source411';SRC416=SRC
def inventory():
 prefix_source.check(PKG,BASESRC,PARENT/'parent/native/pr410')
 propagation_source.check(PKG,PARENT/'normalization/reconstruction/propagation/native')
 return runtime_adapt.check(BASESRC,SRC416,PARENT/'normalization/reconstruction/propagation/native')
inventory()
original=PARENT/'normalization/reconstruction/candidate.json'
assert sha(original)==capacity.SOURCE
P.mkdir();intermediate,capacity_receipt=capacity.run(Path(__file__).parent,original,P/'capacity')
fourteen,enlargement_receipt=enlarge.run(Path(__file__).parent,intermediate,P/'enlargement')
final,refinement_receipt=refine.run(Path(__file__).parent,fourteen,intermediate,P/'enlargement/native',P/'refinement')
candidate=P/'candidate.json';candidate.write_bytes(final.read_bytes())
preflight=dict(source_sha256=capacity.SOURCE,intermediate215_sha256=sha(intermediate),intermediate14_sha256=sha(fourteen),candidate_sha256=sha(candidate),capacity=capacity_receipt,enlargement=enlargement_receipt,refinement=refinement_receipt)
write(P/'PREFLIGHT.json',preflight)
NAT=P/'capacity/native';ENL=P/'enlargement/native';SOURCE409=S409.parent
SRC=enlarged_runtime.overlay(SRC416,ENL,OUT/'source423')
S409,replica_receipt=replicas64.prepare(SOURCE409,OUT/'source409-T64',NAT/'CONFIG422.json')
write(OUT/'REPLICA64.json',replica_receipt)
local_adapter,bank_adapter=enlarged_runtime.prepare(SRC,S409,OUT/'runtime')
assert sha(candidate)==preflight['candidate_sha256']=='c7e071e34bd37d14e7969dbc895206b550ec9e172e68b5633b2e927a3b0c2dfd'
packing=Path(__file__).parent/'patterns-enlarged-T64.json';assert sha(packing)=='42af6fa4bb74ad406e72055f6874f371702df989169553ac97292cd5a2c720aa'
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
py('local',local_adapter,candidate,OUT/'local','--helper-baseline',helper,'--signed-baseline',signed,'--deps',SRC/'local/deps','--prior-phase',prior,'--frame-baseline',intermediate)
py('coefficient-words',SRC/'local/coefficient_words.py',SRC/'local',OUT/'local')
py('independent-helper-tokens',Path(__file__).parent/'response_token_check.py',candidate,OUT/'local/LOCAL-PROGRAMS.json.gz',OUT/'INDEPENDENT-TOKENS.json')
exe=OUT/'phase-replay';run('compile-phase',[env.get('CXX','g++'),'-O2','-std=c++17','-I'+str(SRC/'architecture/deps'),SRC/'architecture/phase-replay.cpp','-o',exe])
py('phase',SRC/'architecture/phase.py',candidate,SRC/'local/deps',exe,OUT/'phase',SRC/'architecture/phase-replay.cpp')
BANK=S409.parent/'e8-response-bank64';config=S409/'CONFIG.json'
assert read(config)['replicas']==64
py('expand',S409/'expand.py',OUT/'expanded')
template=OUT/'expanded/PRIOR.json.gz';data=S409.parent/'e8-shared-donor-chains/architecture/inputs/DATA-PHASES.json'
assert read(data)==read(NATIVE/'DATA-PHASES.json')
py('banks',bank_adapter,candidate,packing,OUT/'phase/RESIDUALS.json',OUT/'local/LOCAL-PROGRAMS.json.gz',OUT/'local/RESULT.json',template,SRC/'local/deps',OUT/'banks',data,config)
py('bank-audit',BANK/'audit.py',OUT/'banks',candidate,OUT/'phase/RESIDUALS.json',OUT/'local/LOCAL-PROGRAMS.json.gz',template,config)
py('bridge',BANK/'bridge.py',OUT/'banks',config)
admission=read(OUT/'banks/ADMISSION.json');audit=read(OUT/'banks/INDEPENDENT-ADMISSION.json');bridge=read(OUT/'banks/BRIDGE.json')
assert audit['template_sha256']==admission['template_sha256']and audit['candidate_sha256']==sha(candidate)
assert(admission['live'],admission['physical'],admission['banks_per_stage'],admission['deficit'])==(114135,114926,5855,19968)
inventory();capacity_source.check(Path(__file__).parent,NAT);enlargement_source.check(Path(__file__).parent,ENL);enlarged_runtime.check(SRC416,SRC,ENL);assert replica_receipt==replicas64.check(SOURCE409,OUT/'source409-T64',NAT/'CONFIG422.json')
write(OUT/'RECEIPT.json',dict(status='PASS_FRESH_ENLARGED215_RECOMPUTED_RESPONSE_LOCAL_PHASE_T64_BANKS_AND_FINITE_INTERFACE',candidate_sha256=sha(candidate),source_manifest_sha256=sha(SRC/'MANIFEST.json'),derived_runtime_inventory_sha256=enlarged_runtime.check(SRC416,SRC,ENL)['derived_inventory_sha256'],derived_runtime_verified=True,source_adaptations_sha256=sha(OUT/'runtime/ADAPTATIONS.json'),preflight_sha256=sha(P/'PREFLIGHT.json'),ordinary_admission_sha256=sha(ORD/'VERIFICATION.json'),stages=stages,output_sha256={str(p.relative_to(OUT)):sha(p)for p in [OUT/'local/RESULT.json',OUT/'local/RECOMPUTED-K.json',OUT/'local/RESPONSE-CONTROLS.json',OUT/'local/COEFFICIENT-WORDS.json',OUT/'INDEPENDENT-TOKENS.json',OUT/'phase/RESIDUALS.json',OUT/'banks/ADMISSION.json',OUT/'banks/INDEPENDENT-ADMISSION.json',OUT/'banks/BRIDGE.json']},scope='Finite grouped215 construction checked with unchanged PR421 constructor plus PR422/421 selections on fresh frozen208, then unchanged PR423 constructor with updated422 thirteen-enlargement selection and only424 gauge838, followed by our gauge891 four-dimension witness using the same constructor. The native423 checker adds actual A/B frame reversion controls against fresh215; the inherited PR411 quarter/eighth compiler remains unchanged, a target-specific omission control and a strict recomputed-response bank contract. The native409 source is copied and only CONFIG is replaced byte-for-byte with native422 CONFIG; score labels are provenance only. Both adapters are byte-bound; prior Gaussian phases are fresh. All nongauged helper response is newly recomputed and executed. The all-size compiler/window/dirty-bank/precision/restored-row/analytic interfaces remain conditional; no unconditional theorem.'))
print('PASS FRESH ENLARGED215 COMPONENTS',flush=True)
