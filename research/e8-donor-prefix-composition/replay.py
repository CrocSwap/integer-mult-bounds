"""Fresh protected donor-prefix replay on enlarged204 with recomputed dirty response.
Pinned PR411 leaf overlay and two explicit adapters; fresh phase provenance.
Finite research evidence only. OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import gzip,json,os,subprocess,sys,time
import reconstruct,prefix_source,runtime_adapt,propagate,propagation_source
assert __debug__
sys.dont_write_bytecode=True
SRC,S409,PARENT,ORD,OUT,PKG=map(lambda p:Path(p).resolve(),sys.argv[1:]);assert not OUT.exists();OUT.mkdir(parents=True)
NATIVE=ORD/'work/complex-nine-native';P=OUT/'reconstruction'
sha=lambda p:sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def write(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
BASESRC=SRC
def inventory():return prefix_source.check(Path(__file__).parent,BASESRC,PARENT/'native/pr410')
inventory()
original=PARENT/'normalization/reconstruction/candidate.json'
assert sha(original)==reconstruct.SOURCE
c,preflight=reconstruct.build(read(original));P.mkdir()
(P/'prefix-word.json').write_bytes(reconstruct.encode(c));write(P/'PREFIX-RECONSTRUCTION.json',preflight)
final,prop=propagate.run(Path(__file__).parent,P/'prefix-word.json',P/'propagation')
(P/'candidate.json').write_bytes(final.read_bytes());write(P/'PREFLIGHT.json',dict(source_sha256=reconstruct.SOURCE,candidate_sha256=prop['candidate_sha256'],prefix=preflight,propagation=prop))
NAT=P/'propagation/native';SRC=runtime_adapt.overlay(BASESRC,NAT,OUT/'source416')
local_adapter,bank_adapter=runtime_adapt.prepare(SRC,S409,OUT/'runtime')
preflight=read(P/'PREFLIGHT.json');candidate=P/'candidate.json'
assert sha(candidate)==preflight['candidate_sha256']=='eedfb5796c8b2b5b202a1e7fee2785b6b23cd1f017794d3f8ddb19c87bd0a384'
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
py('local',local_adapter,candidate,OUT/'local','--helper-baseline',helper,'--signed-baseline',signed,'--deps',SRC/'local/deps','--prior-phase',prior)
py('coefficient-words',SRC/'local/coefficient_words.py',SRC/'local',OUT/'local')
py('independent-helper-tokens',Path(__file__).parent/'response_token_check.py',candidate,OUT/'local/LOCAL-PROGRAMS.json.gz',OUT/'INDEPENDENT-TOKENS.json')
exe=OUT/'phase-replay';run('compile-phase',[env.get('CXX','g++'),'-O2','-std=c++17','-I'+str(SRC/'architecture/deps'),SRC/'architecture/phase-replay.cpp','-o',exe])
py('phase',SRC/'architecture/phase.py',candidate,SRC/'local/deps',exe,OUT/'phase',SRC/'architecture/phase-replay.cpp')
BANK=S409.parent/'e8-response-bank64';config=S409/'CONFIG.json'
assert read(config)['replicas']==32
py('expand',S409/'expand.py',OUT/'expanded')
template=OUT/'expanded/PRIOR.json.gz';data=S409.parent/'e8-shared-donor-chains/architecture/inputs/DATA-PHASES.json'
assert read(data)==read(NATIVE/'DATA-PHASES.json')
py('banks',bank_adapter,candidate,NAT/'PATTERNS.json',OUT/'phase/RESIDUALS.json',OUT/'local/LOCAL-PROGRAMS.json.gz',OUT/'local/RESULT.json',template,SRC/'local/deps',OUT/'banks',data,config)
py('bank-audit',BANK/'audit.py',OUT/'banks',candidate,OUT/'phase/RESIDUALS.json',OUT/'local/LOCAL-PROGRAMS.json.gz',template,config)
py('bridge',BANK/'bridge.py',OUT/'banks',config)
admission=read(OUT/'banks/ADMISSION.json');audit=read(OUT/'banks/INDEPENDENT-ADMISSION.json');bridge=read(OUT/'banks/BRIDGE.json')
assert audit['template_sha256']==admission['template_sha256']and audit['candidate_sha256']==sha(candidate)
assert(admission['live'],admission['physical'],admission['banks_per_stage'],admission['deficit'])==(57189,57980,2941,9984)
inventory();runtime_adapt.check(BASESRC,SRC,NAT);propagation_source.check(Path(__file__).parent,NAT)
write(OUT/'RECEIPT.json',dict(status='PASS_FRESH_PROPAGATED_PREFIX208_RECOMPUTED_RESPONSE_LOCAL_PHASE_BANKS_AND_FINITE_INTERFACE',candidate_sha256=sha(candidate),source_manifest_sha256=sha(SRC/'MANIFEST.json'),derived_runtime_inventory_sha256=runtime_adapt.check(BASESRC,SRC,NAT)['derived_inventory_sha256'],derived_runtime_verified=True,source_adaptations_sha256=sha(OUT/'runtime/ADAPTATIONS.json'),preflight_sha256=sha(P/'PREFLIGHT.json'),ordinary_admission_sha256=sha(ORD/'VERIFICATION.json'),stages=stages,output_sha256={str(p.relative_to(OUT)):sha(p)for p in [OUT/'local/RESULT.json',OUT/'local/RECOMPUTED-K.json',OUT/'local/RESPONSE-CONTROLS.json',OUT/'local/COEFFICIENT-WORDS.json',OUT/'INDEPENDENT-TOKENS.json',OUT/'phase/RESIDUALS.json',OUT/'banks/ADMISSION.json',OUT/'banks/INDEPENDENT-ADMISSION.json',OUT/'banks/BRIDGE.json']},scope='Finite donor-prefix and propagated208 construction checked using four exact PR411 leaves over pinned PR410, one exact PR416 local checker overlay, unchanged PR416 propagation constructor with corrected PR418 relations, a target-specific omission control and a strict recomputed-response bank contract. Both adapters are byte-bound; prior Gaussian phases are fresh. Protected raw blocks are unchanged; nongauged helper response is newly recomputed and executed. The all-size compiler/window/dirty-bank/precision/restored-row/analytic interfaces remain conditional; no unconditional theorem.'))
print('PASS FRESH PROPAGATED PREFIX208 COMPONENTS',flush=True)
