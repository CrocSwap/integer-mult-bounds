# SPDX-License-Identifier: Apache-2.0
"""Authenticate frozen #4167 and its entire source closure before execution."""
from pathlib import Path
import hashlib, io, json, sys, tarfile, tempfile, types
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MANIFEST_SHA='abea80414d41fce44a738dae8d1b10c9e1d901765552a56e69b60add286f43fb'
_temporary=None
_prior=None
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def unique(pairs):
    result={}
    for key,value in pairs:
        need(key not in result,'duplicate key');result[key]=value
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
    raw=(HERE/'inputs/PR4167-MANIFEST.json').read_bytes()
    need(sha(raw)==MANIFEST_SHA,'retained manifest integrity')
    manifest=parse(raw);archive=(HERE/'inputs/PR4167.tar').read_bytes()
    need(sha(archive)==manifest['archive_sha256'],'retained archive integrity')
    expected={r['path']:r['sha256'] for r in manifest['files']}
    need(len(expected)==len(manifest['files']),'duplicate retained path')
    files={}
    with tarfile.open(fileobj=io.BytesIO(archive),mode='r:') as t:
        for member in t:
            if member.isdir():continue
            need(member.isfile() and member.name in expected and member.name not in files,'retained member kind/path')
            need(not Path(member.name).is_absolute() and '..' not in Path(member.name).parts,'retained path')
            raw=t.extractfile(member).read()
            need(sha(raw)==expected[member.name],'retained content integrity')
            files[member.name]=raw
    need(set(files)==set(expected),'missing retained member')
    sources=parse(files['research/qq16-protocol-comparison/SOURCES.json'])
    for row in sources['files']:
        if row['usage']!='input':continue
        rel=row['path'];need(not Path(rel).is_absolute() and '..' not in Path(rel).parts,'canonical path')
        raw=(ROOT/rel).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        need(sha(raw)==row['sha256'] and blob==row['git_blob'],'canonical input integrity:'+rel)
        need(rel not in files,'canonical collision');files[rel]=raw
    return files
def cold():
    global _temporary,_prior
    need(_temporary is None,'one cold cohort per process')
    files=authenticated_inputs()
    _temporary=tempfile.TemporaryDirectory(prefix='qq16-history-')
    root=Path(_temporary.name)
    for rel,raw in files.items():
        path=root/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    _prior=module('qq16_protocol_runtime',root/'research/qq16-protocol-comparison/runtime.py')
    return _prior.cold()
def predecessor():
    need(_temporary is not None,'cold cohort required')
    return Path(_temporary.name)/'research/qq16-protocol-comparison'
def cleanup():
    global _temporary
    if _prior is not None:_prior.cleanup()
    if _temporary is not None:_temporary.cleanup();_temporary=None
