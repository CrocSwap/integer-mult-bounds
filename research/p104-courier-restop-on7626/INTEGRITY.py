#!/usr/bin/env python3
"""Adapted #7626 artifact integrity contract; no scientific replay."""
import hashlib,json,os,stat
from pathlib import Path, PurePosixPath
MAP_SHA='a4a9586ebfd244ba080320d2afa5d4de9359f0193d0d5f59598c6c18cd6576af'
PIN_COUNT=int('564')
FREEZE='cd123ca067099d282cc78d73fe8d10d8afbe3bb10c29235db82ef4c3affc0b44'
CONTINUATION_FREEZE='9c2f245aa3c562def8ae9704e53606f2da98b9b060213b49db5b37ecec38b6fa'
CANDIDATE='b80b6e74bff87c8d8160c5e121dac7c68df0827a7061847b896075417a346238'
def need(v,m):
    if not v: raise ValueError(m)
def sha(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def unique_object(pairs):
    obj={}
    for key,value in pairs:
        need(key not in obj,'duplicate JSON key '+key)
        obj[key]=value
    return obj
def parse_json(data): return json.loads(data,object_pairs_hook=unique_object)
def safe(s):
    need(type(s) is str and s and not s.startswith('/') and '\\' not in s and '\x00' not in s, 'invalid path')
    parts=s.split('/')
    need(all(x not in ('','.','..') for x in parts) and str(PurePosixPath(s))==s, 'noncanonical path')
    return Path(*parts)
def check_ancestors(path):
    path=Path(os.path.abspath(path))
    for node in reversed((path, *path.parents)):
        st=node.lstat();need(not stat.S_ISLNK(st.st_mode),'symlink ancestor')
    return path
def unique_names(paths):
    seen={};files=set()
    for value in paths:
        p=safe(value);need(value not in files,'duplicate path');files.add(value)
        for i in range(1,len(p.parts)+1):
            piece='/'.join(p.parts[:i]);alias=piece.casefold()
            need(alias not in seen or seen[alias]==piece,'case alias')
            seen[alias]=piece
    for value in files:
        parts=safe(value).parts
        for i in range(1,len(parts)):
            need('/'.join(parts[:i]) not in files,'file/directory conflict')
    return True
def verify():
    p=check_ancestors(Path(__file__).absolute().parent)
    pins=parse_json((p/'PINS.json').read_bytes());need(pins['schema']=='contact7624-pins/v1' and len(pins['files'])==PIN_COUNT,'pin schema/count')
    unique_names(list(pins['files'])+['PINS.json'])
    actual=set()
    for f in p.rglob('*'):
        st=f.lstat();need(not stat.S_ISLNK(st.st_mode),'symlink')
        if stat.S_ISREG(st.st_mode):
            need(st.st_nlink==1,'hardlinked package file')
            if f!=p/'PINS.json': actual.add(f.relative_to(p).as_posix())
        else: need(stat.S_ISDIR(st.st_mode),'nonregular package object')
    need(actual==set(pins['files']),'inventory')
    for name,row in pins['files'].items():
        b=(p/safe(name)).read_bytes();need(len(b)==row['bytes'] and sha(b)==row['sha256'] and blob(b)==row['git_blob'],'pin '+name)
    mb=(p/'EXPORT-MAP.json').read_bytes();need(sha(mb)==MAP_SHA,'fixed map digest')
    m=parse_json(mb);need(m['schema']=='contact7624-offline-export/v1' and m['candidate_canonical_sha256']==CANDIDATE and m['freeze_sha256']==FREEZE,'map identity')
    rows=m['files'];need(type(rows) is list and rows and len({x['original_path'] for x in rows})==len(rows),'map path uniqueness')
    unique_names([x['portable_path'] for x in rows]+['MATERIALIZED.json'])
    frozen=[x for x in rows if 'frozen_input' in x['origins']]
    need(len(frozen)==m['frozen_file_count']==450 and sum(x['bytes'] for x in frozen)==m['frozen_byte_count']==49494600,'frozen denominator')
    for x in rows:
        safe(x['portable_path']);b=(p/safe(x['package_path'])).read_bytes();need(len(b)==x['bytes'] and sha(b)==x['sha256'] and blob(b)==x['git_blob'],'mapped bytes')
    # Link the copied original freeze's rows to the mapped frozen paths, not merely counts.
    fr=[x for x in rows if x['portable_path'].endswith('kappa-swarm30-20261116/fullqualification/controller/FREEZE.json')]
    need(len(fr)==1,'freeze source map');fb=(p/safe(fr[0]['package_path'])).read_bytes();need(sha(fb)==FREEZE,'freeze digest')
    expected=parse_json(fb)['files'];index={x['original_path']:x for x in frozen}
    need(set(index)=={x['path'] for x in expected},'frozen path set')
    for row in expected: need(index[row['path']]['sha256']==row['sha256'] and index[row['path']]['bytes']==row['bytes'],'frozen input binding')
    continuation=[x for x in rows if 'continuation_frozen_input' in x['origins']]
    need(len(continuation)==m['continuation_file_count']==603 and sum(x['bytes'] for x in continuation)==m['continuation_byte_count']==87657814 and m['continuation_freeze_sha256']==CONTINUATION_FREEZE, 'continuation denominator')
    cm=[x for x in rows if x['portable_path'].endswith('kappa-swarm30-20261116/signed-completion/controller/FREEZE.json')]
    need(len(cm)==1,'continuation freeze path'); cb=(p/safe(cm[0]['package_path'])).read_bytes();need(sha(cb)==CONTINUATION_FREEZE,'continuation freeze bytes')
    cindex={x['original_path']:x for x in continuation}; cexpected=parse_json(cb)['files']
    need(set(cindex)=={x['path'] for x in cexpected} and len(cexpected)==603, 'continuation source paths')
    for row in cexpected: need(cindex[row['path']]['sha256']==row['sha256'] and cindex[row['path']]['bytes']==row['bytes'], 'continuation source pin')
    need(set(index)<=set(cindex), 'original closure contained')
    im=[x for x in rows if x['portable_path'].endswith('kappa-swarm30-20261116/signed-completion/controller/INTERRUPTED-EVIDENCE.json')]
    need(len(im)==1,'interrupted inventory path');ib=(p/safe(im[0]['package_path'])).read_bytes()
    need(sha(ib)=='e862e0d55a98c09fa0d8ebec3470cd4938a79fbbead534e7a6d8f421d414157a','interrupted inventory pin')
    evidence=parse_json(ib)['evidence'];need(len(evidence)==m['interrupted_evidence_count']==44 and len({x['path'] for x in evidence})==44,'interrupted evidence count')
    for row in evidence: need(row['path'] in cindex and cindex[row['path']]['sha256']==row['sha256'] and cindex[row['path']]['bytes']==row['bytes'], 'interrupted evidence bytes')
    # Reuse #7626 nested path custody: both old groups must be fully present
    # in this 450-file mapping, with their original byte pins intact.
    for suffix,key,count in (('compose7624_completion/FREEZE.json','files',104),('compose7624_completion/run/case/RETAINED-PASSED.json','evidence',14)):
        matches=[x for x in frozen if x['portable_path'].endswith(suffix)]
        need(len(matches)==1,'nested metadata mapping '+suffix)
        nested=parse_json((p/safe(matches[0]['package_path'])).read_bytes())[key]
        need(type(nested) is list and len(nested)==count and len({x['path'] for x in nested})==count, 'nested denominator')
        for row in nested:
            need(row['path'] in index and index[row['path']]['sha256']==row['sha256'], 'nested byte pin '+row['path'])
    return {'status':'PASS_ARTIFACT_INTEGRITY_ONLY','scientific_code_executed':False,'frozen_inputs':450,'continuation_frozen_inputs':603,'interrupted_records':44,'files_checked':PIN_COUNT}
if __name__=='__main__': print(json.dumps(verify(),sort_keys=True))
