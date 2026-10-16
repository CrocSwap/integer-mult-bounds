"""Source-bound newline portability for two frozen generated parent artifacts.

Only line-ending bytes may change, only in an execution copy. Native/checker
code and mathematical JSON bytes are preserved. Full byte comparison after
canonical newline conversion never parses or equates mathematical values.
"""
import hashlib,json,os,shutil
from pathlib import Path

PARENT_MANIFEST='b8dba5524f8603e1848c73a8dd675404a0d3d9eed3b0285e9f0cfccde38fd15f'
ARTIFACTS=('outer/LEDGER.json','outer/INDEPENDENT.json')

def require(ok,message):
    if not ok:raise ValueError(message)

def digest(data):return hashlib.sha256(data).hexdigest()

def canonical_newlines(data):
    require(type(data) is bytes,'newline comparison requires bytes')
    result=data.replace(b'\r\n',b'\n')
    require(b'\r' not in result,'lone carriage return is forbidden')
    return result

def same_artifact_bytes(left,right):
    """Equality of every byte, permitting only CRLF versus LF substitution."""
    return canonical_newlines(left)==canonical_newlines(right)

def native_newlines(data,newline):
    require(newline in (b'\n',b'\r\n'),'unsupported native newline convention')
    return canonical_newlines(data).replace(b'\n',newline)

def snapshot(root):
    root=Path(root).resolve();result={}
    for p in root.rglob('*'):
        require(not p.is_symlink() and p.resolve().is_relative_to(root),'linked execution source is forbidden')
        if p.is_file():result[p.relative_to(root).as_posix()]=digest(p.read_bytes())
    return result

def authenticate_original(parent):
    parent=Path(parent).resolve();raw=(parent/'MANIFEST.json').read_bytes()
    require(digest(raw)==PARENT_MANIFEST,'wrong frozen parent manifest')
    pins=json.loads(raw);actual=snapshot(parent)
    require(len(pins)==381 and len(actual)==382,'incomplete frozen parent')
    require(set(actual)==set(pins)|{'MANIFEST.json'},'frozen parent membership differs')
    require(all(actual[n]==h for n,h in pins.items()),'frozen parent artifact hash differs')
    return raw,pins,actual

def expected_transform(parent,newline):
    raw,pins,original=authenticate_original(parent);derived=dict(pins);changes={};manifest=raw
    for name in ARTIFACTS:
        before=(parent/name).read_bytes();after=native_newlines(before,newline)
        require(same_artifact_bytes(before,after),'normalization changed non-newline bytes')
        if before!=after:
            old=pins[name];new=digest(after)
            token=('"'+name+'": "'+old+'"').encode('ascii')
            replacement=('"'+name+'": "'+new+'"').encode('ascii')
            require(manifest.count(token)==1,'manifest artifact token is not unique')
            manifest=manifest.replace(token,replacement);derived[name]=new
            changes[name]={'original_sha256':old,'derived_sha256':new,
                'original_bytes':len(before),'derived_bytes':len(after),
                'canonical_sha256':digest(canonical_newlines(before)),
                'original_CRLF_count':before.count(b'\r\n'),'derived_CRLF_count':after.count(b'\r\n')}
    require(json.loads(manifest)==derived,'derived manifest changes exceed permitted entries')
    changed_keys={n for n in pins if pins[n]!=derived[n]}
    require(changed_keys==set(changes)<=set(ARTIFACTS),'unpermitted manifest entry change')
    wanted=dict(original);wanted.update({n:d['derived_sha256'] for n,d in changes.items()});wanted['MANIFEST.json']=digest(manifest)
    return original,manifest,wanted,changes

def prepare_parent(parent,execution_directory):
    """Return frozen original when host-matching, otherwise a bound work copy."""
    parent=Path(parent).resolve();execution_directory=Path(execution_directory).resolve()
    require(not execution_directory.exists(),'portable execution copy already exists')
    require(not execution_directory.is_relative_to(parent),'execution copy must be outside frozen parent')
    newline=os.linesep.encode('ascii');original,manifest,wanted,changes=expected_transform(parent,newline)
    if changes:
        shutil.copytree(parent,execution_directory)
        for name in changes:
            (execution_directory/name).write_bytes(native_newlines((parent/name).read_bytes(),newline))
        (execution_directory/'MANIFEST.json').write_bytes(manifest)
        executed=execution_directory
    else:executed=parent
    receipt={'schema':'source-bound-newline-execution-copy/1','adapter_sha256':digest(Path(__file__).read_bytes()),
        'original_parent':str(parent),'execution_parent':str(executed),'native_newline_hex':newline.hex(),
        'original_manifest_sha256':PARENT_MANIFEST,'execution_manifest_sha256':digest(manifest),
        'original_files':original,'execution_files':wanted,'changed_artifacts':changes,
        'transformation':'Only CRLF/LF substitution in two allowed generated JSON artifacts; lone CR rejected. Only their manifest SHA256 values change. All other bytes remain exact.',
        'scope':'Format-only derived execution source; no new mathematical result or evidence reuse.'}
    verify_parent(parent,executed,receipt)
    return executed,receipt

def verify_parent(parent,executed,receipt):
    """Recompute the permitted transform, binding both sources before/after."""
    parent=Path(parent).resolve();executed=Path(executed).resolve()
    require(receipt['schema']=='source-bound-newline-execution-copy/1','unknown portability receipt')
    require(receipt['adapter_sha256']==digest(Path(__file__).read_bytes()),'portability adapter changed')
    require(receipt['original_parent']==str(parent) and receipt['execution_parent']==str(executed),'execution path binding differs')
    newline=os.linesep.encode('ascii')
    require(receipt['native_newline_hex']==newline.hex(),'host newline convention changed')
    original,manifest,wanted,changes=expected_transform(parent,newline)
    require(receipt['original_files']==original and receipt['execution_files']==wanted,'portability source inventory differs')
    require(receipt['changed_artifacts']==changes,'portability transform differs')
    require(receipt['original_manifest_sha256']==PARENT_MANIFEST and receipt['execution_manifest_sha256']==digest(manifest),'portability manifest binding differs')
    require((executed/'MANIFEST.json').read_bytes()==manifest,'derived manifest bytes differ')
    observed=snapshot(executed)
    require(observed==wanted,'execution source bytes changed')
    require((executed==parent)==(not changes),'unnecessary or missing derived execution copy')
    return {'status':'PASS_EXACT_ORIGINAL_AND_EXECUTION_SOURCE_BINDING',
        'original_manifest_sha256':original['MANIFEST.json'],
        'execution_manifest_sha256':observed['MANIFEST.json'],
        'original_tree_sha256':digest(json.dumps(original,sort_keys=True,separators=(',',':')).encode()),
        'execution_tree_sha256':digest(json.dumps(observed,sort_keys=True,separators=(',',':')).encode()),
        'original_file_count':len(original),'execution_file_count':len(observed)}
