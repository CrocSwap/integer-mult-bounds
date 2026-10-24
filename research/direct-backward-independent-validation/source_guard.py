#!/usr/bin/env python3
"""Authenticate real package bytes and offline Git membership before any engine runs."""
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path, PurePosixPath

MAIN='1ec1119972c9aefe42525172d07b332fcff81cb4'
HEAD='174fb211493b43a42210434083e9702b4fb7a2ce'
REVIEW='787efce72a908f92b8a8b4ebb677a6fdb7729e33'
ASSUMPTIONS=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery']

def require(ok,message):
    if not ok:raise ValueError(message)

def regular(root,relative):
    parts=PurePosixPath(relative).parts
    require(parts and not relative.startswith('/') and all(p not in ('','.','..') for p in parts) and str(PurePosixPath(relative))==relative,'Noncanonical input path: '+relative)
    here=root
    for part in parts:
        here=here/part
        require(not here.is_symlink(),'Symlink input component: '+str(here))
    require(here.is_file(),'Missing regular input: '+relative)
    require(here.stat().st_nlink==1,'Hardlinked input alias: '+relative)
    return here

def oid(kind,raw):
    return hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def tree_entries(raw):
    entries={};i=0
    while i<len(raw):
        split=raw.index(b' ',i);zero=raw.index(b'\0',split)
        require(zero+21<=len(raw),'Truncated Git tree')
        name=raw[split+1:zero].decode('utf8')
        require(name and '/' not in name and name not in ('.','..') and name not in entries,'Invalid Git tree name')
        entries[name]=(raw[i:split].decode(),raw[zero+1:zero+21].hex());i=zero+21
    require(i==len(raw),'Truncated Git tree')
    return entries

def check(root):
    root=Path(root).absolute()
    for p in [root,*root.parents]:require(not p.is_symlink(),'Symlink package ancestor: '+str(p))
    claims=json.loads(regular(root,'CLAIMS.json').read_bytes())
    manifest=json.loads(regular(root,'SOURCE-BINDINGS.json').read_bytes())
    require(claims['canonical_main']==manifest['canonical_main']==MAIN,'Wrong canonical main')
    require(claims['selected_baseline']=='.0030217758' and claims['selected_kappa']=='15108879/5000000000','Wrong selected baseline')
    require(claims['same_selected_assumptions_required'] is True,'Changed retained assumptions scope')
    require([x['id'] for x in claims['assumptions']]==ASSUMPTIONS,'Missing retained assumption')
    require(all(claims[k] is False for k in ('new_unconditional_or_Lean_theorem','uniform_word_materialized','selected_record_changed','selection_authorized')),'Wrong scope flags')
    require(len(claims['candidates'])==1,'Exactly one independent-review target required')
    c=claims['candidates'][0]
    require((c['pr'],c['head'],c['package'],c['kappa'])==(5398,HEAD,'research/kappa-backward-controller-20261023','302728823/100000000000'),'Wrong candidate identity')
    require(Fraction(c['decimal'])==Fraction(c['kappa']),'Wrong decimal headline')
    require(claims['gains']=={name:str(Fraction(c['kappa'])-Fraction(value)) for name,value in [('selected','.0030217758'),('PR5387','.003026674765'),('PR5392','.00302725')]},'Wrong derived gain claim')
    require(not any(key.startswith('gain_') for key in claims),'Undeclared gain claim field')
    require(claims['reused_review']=={'pr':5396,'head':REVIEW},'Wrong reused review')
    priorclaims=json.loads(regular(root,'capsule/reuse/5396/CLAIMS.json').read_bytes())
    require(claims['assumptions']==priorclaims['assumptions'],'Changed literal retained premise statements')
    rows=manifest['files'];paths=[x['path'] for x in rows]
    require(len(paths)==len(set(paths)),'Duplicate binding')
    actual=set()
    for p in root.rglob('*'):
        require(not p.is_symlink(),'Symlink anywhere in package: '+str(p))
        require(p.name!='__pycache__' and p.suffix not in ('.pyc','.pyo'),'Bytecode cache in frozen package')
        if p.is_file():actual.add(p.relative_to(root).as_posix())
    require(actual==set(paths)|{'verify.py','SOURCE-BINDINGS.json'},'Missing or undeclared package files')
    digests={}
    for row in rows:
        raw=regular(root,row['path']).read_bytes()
        require(len(raw)==row['bytes'],'Wrong byte count: '+row['path'])
        digest=hashlib.sha256(raw).hexdigest()
        require(digest==row['sha256'],'Changed working bytes: '+row['path'])
        if row.get('git_blob'):require(oid('blob',raw)==row['git_blob'],'Wrong original Git blob: '+row['path'])
        if row.get('payload_sha256'):require(hashlib.sha256(gzip.decompress(raw)).hexdigest()==row['payload_sha256'],'Wrong gzip payload: '+row['path'])
        if row.get('git_object_type'):require(oid(row['git_object_type'],raw)==row['git_object_sha1'],'Wrong raw Git object: '+row['path'])
        digests[row['path']]=digest
    allowed=set(manifest['allowed_source_commits'])
    require({MAIN,HEAD,REVIEW}.issubset(allowed),'Missing pinned source commits')
    def membership(row):
        require(row['origin_commit'] in allowed,'Unrecognized source head')
        raw=regular(root,row['commit_object']).read_bytes()
        require(oid('commit',raw)==row['origin_commit'],'Wrong source commit')
        first=raw.split(b'\n',1)[0].split();require(len(first)==2 and first[0]==b'tree','Commit root tree missing')
        current=first[1].decode();parts=PurePosixPath(row['origin_path']).parts
        require(str(PurePosixPath(row['origin_path']))==row['origin_path'] and all(x not in ('.','..') for x in parts),'Noncanonical origin path')
        require(len(parts)==len(row['tree_objects']),'Wrong membership depth')
        for part,treepath in zip(parts,row['tree_objects']):
            raw=regular(root,treepath).read_bytes();require(oid('tree',raw)==current,'Wrong membership tree')
            entries=tree_entries(raw);require(part in entries,'Missing tree member');mode,current=entries[part]
        require(mode in ('100644','100755') and mode==row['git_mode'] and current==row['git_blob'],'Wrong Git file membership')
    for row in rows:
        if row.get('origin_commit'):membership(row)
        for label in ('declared_source_origin','original_source_origin'):
            if row.get(label):
                require(row[label]['git_blob']==row['git_blob'],'Original source is a different blob')
                membership(row[label])
    for name,digest in manifest['frozen_engines'].items():require(digests.get(name)==digest,'Changed frozen engine: '+name)
    base='capsule/repository/research/kappa-backward-controller-20261023/'
    for name in ('native.py','WITNESS.json'):
        require(regular(root,base+name).read_bytes()==regular(root,'capsule/reuse/5383/'+name).read_bytes(),'Changed reused supplier '+name)
    payload=gzip.decompress(regular(root,'capsule/reuse/5383/WORD.json.gz').read_bytes())
    require(hashlib.sha256(payload).hexdigest()=='2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d','Wrong reused literal supplier')
    result=json.loads(regular(root,base+'RESULT.json').read_bytes())
    require(result['arithmetic']['kappa']==c['kappa'],'Author claim record has wrong endpoint')
    sources=json.loads(regular(root,base+'SOURCES.json').read_bytes())
    verify=json.loads(regular(root,base+'VERIFY.json').read_bytes())
    require(sources['base_commit']==MAIN and len(verify['inputs'])==11,'Wrong candidate runtime source closure')
    for row in sources['files']:
        raw=regular(root,'capsule/repository/'+row['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest()==row['sha256'] and oid('blob',raw)==row['git_blob'],'Candidate SOURCES mismatch: '+row['path'])
    require(set(verify['inputs'])=={r['path'] for r in sources['files'] if r['usage']=='input'},'Wrong declared runtime source set')
    selected=json.loads(regular(root,'capsule/repository/certificates/selected-result.json').read_bytes())
    require(Fraction(selected['kappa'])==Fraction(claims['selected_kappa']),'Selected provenance changed')
    return {'status':'PASS_ACTUAL_WORKING_INPUT_BINDINGS','files':len(rows),'digests':digests,'candidate_head':HEAD,'reused_review_head':REVIEW}
