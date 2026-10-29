"""Authenticate retained #4166 and canonical inputs before any inherited code.

The temporary cohort preserves original relative paths. Retained predecessor
bytes are an executable comparison dependency, never a substitute endpoint.
"""
from pathlib import Path
import hashlib, io, json, sys, tarfile, tempfile, types
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MANIFEST_SHA='88d325b06ecd88a129caceb40e7b953674b36cd1a7a578129869f3ab87fbf648'
EXTRA_INPUTS={
 'research/physical-complex-controller/production_native.py':'4c1f8f69212162bd297010c6e21a32e31755cbfe2e40f9935b8d87a9e4260d46',
 'research/physical-complex-controller/check_bounds.py':'697606202fbef8463f6ee736007b9630c55034246dcda17c23b03e97d270dcc7'}
_temporary=None
_inherited=None
def need(ok,why):
    if not ok: raise ValueError(why)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def unique(pairs):
    result={}
    for key,value in pairs:
        need(key not in result,'duplicate manifest key');result[key]=value
    return result
def parse(raw):return json.loads(raw,object_pairs_hook=unique)
def typed(value):
    if isinstance(value,dict):return ('dict',tuple((k,typed(v)) for k,v in sorted(value.items())))
    if isinstance(value,list):return ('list',tuple(map(typed,value)))
    return (type(value).__name__,value)
def module(name,path):
    result=types.ModuleType(name);result.__file__=str(path)
    sys.modules[name]=result
    exec(compile(path.read_bytes(),str(path),'exec'),result.__dict__)
    return result
def authenticated_inputs():
    raw=(HERE/'inputs/PR4166-MANIFEST.json').read_bytes()
    need(sha(raw)==MANIFEST_SHA,'retained manifest integrity')
    manifest=parse(raw);archive=(HERE/'inputs/PR4166.tar').read_bytes()
    need(sha(archive)==manifest['tar_sha256'],'retained archive integrity')
    expected={row['path']:row['sha256'] for row in manifest['files']}
    need(len(expected)==len(manifest['files']),'duplicate retained path')
    files={}
    with tarfile.open(fileobj=io.BytesIO(archive),mode='r:') as archive_file:
        for member in archive_file:
            if member.isdir():continue
            need(member.isfile() and member.name in expected and member.name not in files,
                 'unexpected or aliased retained member')
            need(not Path(member.name).is_absolute() and '..' not in Path(member.name).parts,
                 'unsafe retained path')
            with archive_file.extractfile(member) as stream: content=stream.read()
            need(sha(content)==expected[member.name],'retained member integrity')
            files[member.name]=content
    need(set(files)==set(expected),'missing retained member')
    sources=parse(files['research/qq16-caller-install/SOURCES.json'])
    for row in sources['files']:
        if row['usage']!='input':continue
        rel=row['path'];need(not Path(rel).is_absolute() and '..' not in Path(rel).parts,'input path')
        raw=(ROOT/rel).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        need(sha(raw)==row['sha256'] and blob==row['git_blob'],'canonical input integrity:'+rel)
        need(rel not in files,'canonical/retained collision');files[rel]=raw
    for rel,digest in EXTRA_INPUTS.items():
        raw=(ROOT/rel).read_bytes()
        need(sha(raw)==digest,'canonical input integrity:'+rel)
        need(rel not in files,'duplicate extra input');files[rel]=raw
    return files
def cold():
    global _temporary,_inherited
    need(_temporary is None,'one authenticated cohort per process')
    files=authenticated_inputs()
    _temporary=tempfile.TemporaryDirectory(prefix='qq16-protocol-')
    root=Path(_temporary.name)
    for rel,raw in files.items():
        path=root/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    package=root/'research/qq16-caller-install'
    sys.path.insert(0,str(package))
    _inherited=module('qq16_retained_runtime',package/'runtime.py')
    return _inherited.cold()
def predecessor():
    need(_temporary is not None,'cold cohort required')
    return Path(_temporary.name)/'research/qq16-caller-install'
def cleanup():
    global _temporary
    if _inherited is not None:_inherited.cleanup()
    if _temporary is not None:_temporary.cleanup();_temporary=None
