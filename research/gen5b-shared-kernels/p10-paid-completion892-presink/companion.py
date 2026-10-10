"""Portable, strict evidence contract for the separate PR322/323 composition."""
from pathlib import Path
from functools import lru_cache
from collections import Counter
import gzip,hashlib,json,os,struct
HERE=Path(__file__).resolve().parent
INPUTS=Path(os.environ.get('P10C_INPUTS',str(HERE/'local-inputs/new'))).resolve()
BASE_INPUTS=Path(os.environ.get('P10C_BASE_INPUTS',str(HERE/'local-inputs/pr320'))).resolve()
OUTPUT=Path(os.environ.get('P10C_OUTPUT',str(HERE/'output'))).resolve()
BASE_OUTPUT=Path(os.environ.get('P10C_BASE_OUTPUT',str(OUTPUT/'base-paid'))).resolve()
BASE_CODE=HERE.parent/'p10-paid-completion892'
BASE_FILES_SHA='a97606376a6a42abe3c1aab1815da4ec1b2f82ea8b4648c859039491bcbb7aa5'
BASE_INPUT_MANIFEST=HERE.parent/'p10-updated1047/inputs.json'
BASE_FRAME=BASE_OUTPUT/'frame';BASE_ADMISSION=BASE_OUTPUT/'admission';BASE_LOWER=BASE_OUTPUT/'lowering';BASE_FULL=BASE_OUTPUT/'full-frame';BASE_BANK=BASE_OUTPUT/'bank/split_49_11'
EXPERIMENT,ADMISSION,LOWERING,AUDIT=[OUTPUT/x for x in ['experiment','admission','lowering','audit']]
SOURCE_PROVENANCE=HERE/'inputs.json'
WORD_SHA='25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739'
for folder in [EXPERIMENT,ADMISSION,LOWERING,AUDIT]:folder.mkdir(parents=True,exist_ok=True)
def require_assertions():
    if not __debug__:raise RuntimeError('Assertions must be enabled; run without -O.')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):
    path=Path(path);raw=path.read_bytes();return json.loads(gzip.decompress(raw)if path.suffix=='.gz'else raw)
def portable(value):
    if isinstance(value,dict):return {portable(k):portable(v)for k,v in value.items()}
    if isinstance(value,list):return [portable(v)for v in value]
    if isinstance(value,str):
        for root,label in [(BASE_OUTPUT,'$BASE_OUTPUT'),(OUTPUT,'$OUTPUT'),(BASE_INPUTS,'$BASE_INPUTS'),(INPUTS,'$INPUTS'),(HERE,'$PACKAGE'),(HERE.parent,'$AUTHORED')]:value=value.replace(str(root),label)
    return value

def verify_base_code():
    require_assertions();assert sha(BASE_CODE/'FILES.json')==BASE_FILES_SHA,'Frozen paid892 packet identity changed'
    manifest=read(BASE_CODE/'FILES.json')
    for name,row in manifest['files'].items():
        p=BASE_CODE/name;assert p.stat().st_size==row['bytes']and sha(p)==row['sha256'],name
    for name,digest in read(BASE_CODE/'dependencies.json').items():assert sha(BASE_CODE.parent/name)==digest,name
    return manifest

def base_canonical(value):
    if isinstance(value,dict):return {base_canonical(k):base_canonical(v)for k,v in sorted(value.items())if k not in ('seconds','elapsed_seconds','runtime_seconds')}
    if isinstance(value,list):return [base_canonical(v)for v in value]
    if isinstance(value,str):
        for root,label in [(BASE_OUTPUT,'$OUTPUT'),(BASE_INPUTS,'$INPUTS'),(BASE_CODE,'$PACKAGE'),(BASE_CODE.parent,'$AUTHORED')]:value=value.replace(str(root),label)
    return value

def verify_base():
    verify_base_code();expected=read(BASE_CODE/'expected/receipts.json')
    assert expected['word_sha256']==WORD_SHA and expected['receipt_count']==31
    for name,row in expected['receipts'].items():
        value=base_canonical(read(BASE_OUTPUT/name));raw=json.dumps(value,sort_keys=True,separators=(',',':')).encode()
        assert hashlib.sha256(raw).hexdigest()==row['sha256'],'Retained receipt changed: '+name
    for folder in [BASE_LOWER,BASE_FULL]:
        for name,digest in read(folder/'MANIFEST.json').items():assert sha(folder/name)==digest,name
    assert read(BASE_FRAME/'RESULT.json')['checker_sha256']==sha(BASE_CODE/'frame/build_local.py')
    assert read(BASE_FRAME/'VALIDATION.json')['checker_sha256']==sha(BASE_CODE/'frame/validate_local.py')
    assert read(BASE_FULL/'RESULT.json')['compiler_sha256']==sha(BASE_CODE/'lowering/bind_full_frames.py')
    return True

@lru_cache(None)
def source_pins():
    require_assertions();value=read(SOURCE_PROVENANCE)
    assert [r['head']for r in value['metadata']]==['8ce22e5e487e9d1017c26702adc09d5646565d0c','e51f5ffee8ab574e5b8249a4612411b2ca5f100d']
    for row in value['files']:
        assert not Path(row['label']).is_absolute()and '..'not in Path(row['label']).parts and not row['label'].endswith('.py')
        assert row['url']==f"https://raw.githubusercontent.com/{row['repository']}/{row['ref']}/{row['path']}"
    return value

def check_source_bytes(raw,row):
    require_assertions();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'],row['label']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['sha'],row['label']
def verify_sources():
    for row in source_pins()['files']:check_source_bytes((INPUTS/row['label']).read_bytes(),row)

def base_packing():
    data=read(BASE_CODE/'witnesses/packing.json');widths={}
    for role,t,bank,off,width,scale in struct.iter_unpack('>6I',gzip.decompress((BASE_BANK/'literal-assignments.bin.gz').read_bytes())):
        assert widths.setdefault(role,width)==width
    assert len(widths)==8221
    data['residual_census']={str(k):v for k,v in sorted(Counter(widths.values()).items())}
    return data
EXPERIMENT_FILES=['RESULT.json','BANK-RESULT.json','PRICE-RESULT.json','CASE-PRICES.json','CONTROLS.json','combined-events.json.gz','combined-frames.json.gz','combined-endpoints.json.gz','new-bank-assignments.bin.gz']
def freeze_experiment():
    value={'status':'HASH_BOUND_REGENERATED_EXPERIMENT','base_files_sha256':BASE_FILES_SHA,'source_manifest_sha256':sha(SOURCE_PROVENANCE),'artifacts':{n:sha(EXPERIMENT/n)for n in EXPERIMENT_FILES},'producer_hashes':{p.name:sha(p)for p in sorted((HERE/'experiment').glob('*.py'))}}
    (EXPERIMENT/'MANIFEST.json').write_text(json.dumps(value,indent=2)+'\n');verify_experiment()
def verify_experiment():
    verify_base();verify_sources();value=read(EXPERIMENT/'MANIFEST.json')
    assert value['base_files_sha256']==BASE_FILES_SHA and value['source_manifest_sha256']==sha(SOURCE_PROVENANCE)
    assert set(value['artifacts'])==set(EXPERIMENT_FILES)
    assert set(value['producer_hashes'])=={p.name for p in(HERE/'experiment').glob('*.py')}
    for name,digest in value['artifacts'].items():assert sha(EXPERIMENT/name)==digest,name
    for name,digest in value['producer_hashes'].items():assert sha(HERE/'experiment'/name)==digest,name
    return value

def child_env():
    return dict(os.environ,P10P_INPUTS=str(BASE_INPUTS),P10P_OUTPUT=str(BASE_OUTPUT),P10C_INPUTS=str(INPUTS),P10C_BASE_INPUTS=str(BASE_INPUTS),P10C_OUTPUT=str(OUTPUT),P10C_BASE_OUTPUT=str(BASE_OUTPUT))
