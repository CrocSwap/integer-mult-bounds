"""Closed live-working-byte input loader. Apache-2.0; OpenAI Codex assistance.
No Git old-blob fallback: a missing or changed working input fails before modules run.
"""
from pathlib import Path,PurePosixPath
import gzip,hashlib,json,subprocess,tempfile,os
ROOT=None;ROWS={};READS=set()
def need(ok,message):
    if not ok:raise ValueError(message)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def safe(root,name):
    rel=PurePosixPath(name)
    need(str(rel)==name and not rel.is_absolute() and all(x not in ('','..','.') for x in rel.parts),'canonical input path '+name)
    p=root
    for part in rel.parts:
        p=p/part;need(not p.is_symlink(),'symlink input rejected '+name)
    need(p.is_file(),'missing live input '+name)
    return p
def check_bytes(root,row):
    p=safe(root,row['path']);b=p.read_bytes()
    need(digest(b)==row['sha256'],'changed live input '+row['path'])
    need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'live blob mismatch '+row['path'])
    return b
def bootstrap(root,manifest):
    global ROOT,ROWS
    ROOT=Path(root).resolve();data=json.loads(Path(manifest).read_bytes())
    ROWS={r['path']:r for r in data['files'] if r['usage']=='input'}
    need(len(ROWS)==sum(r['usage']=='input' for r in data['files']),'duplicate live input')
    for row in ROWS.values():check_bytes(ROOT,row)
    # Only declared historical pins are resolved through Git; live data never is.
    git=['git','--no-replace-objects','-c','advice.graftFileDeprecated=false','-C',str(ROOT)]
    env=os.environ.copy();env['GIT_NO_REPLACE_OBJECTS']='1';env['GIT_GRAFT_FILE']=os.devnull;env['GIT_NO_LAZY_FETCH']='1'
    # Canonical blob identity AND working-byte identity are both required.
    tree=subprocess.check_output(git+['ls-tree','-rz',data['base_commit'],'--',*sorted(ROWS)],env=env)
    actual={}
    for record in tree.split(b'\0'):
        if not record:continue
        meta,name=record.split(b'\t',1);mode,kind,blob=meta.split();actual[name.decode()] = (mode.decode(),kind.decode(),blob.decode())
    for name,row in ROWS.items():
        need(actual.get(name)==('100644','blob',row['git_blob']) or actual.get(name)==('100755','blob',row['git_blob']),'declared live pin does not match canonical stored tree '+name)
    for pin in sorted({data['base_commit'],*data.get('source_commits',[])}):
        need(subprocess.run(git+['merge-base','--is-ancestor',pin,'HEAD'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env).returncode==0,'source commit not canonical-history reachable '+pin)
    return {'live_inputs_prechecked':len(ROWS),'base_commit':data['base_commit'],'source_commits':data.get('source_commits',[])}
def raw(name):
    need(ROOT is not None and name in ROWS,'undeclared external read '+name);READS.add(name)
    return check_bytes(ROOT,ROWS[name])
def js(name):
    b=raw(name);return json.loads(gzip.decompress(b) if name.endswith('.gz') else b)
def corruption_control():
    name=next(iter(ROWS));row=ROWS[name]
    with tempfile.TemporaryDirectory(prefix='4610-live-control-') as d:
        base=Path(d);p=base/name;p.parent.mkdir(parents=True);p.write_bytes(raw(name)+b'corrupt')
        try:check_bytes(base,row)
        except ValueError as e:return {'mutated_working_input_rejected_before_execution':str(e)}
        raise ValueError('corrupt live working input accepted')
def final_recheck():
    for row in ROWS.values():check_bytes(ROOT,row)
    if LOCAL_ROOT is not None:
        for name in LOCAL_ROWS:local(name)
    return {'proof_relevant_live_reads':sorted(READS),'stable_pre_post_live_inputs':len(ROWS)}

LOCAL_ROOT=None;LOCAL_ROWS={}
def local_bootstrap(package):
    global LOCAL_ROOT,LOCAL_ROWS
    LOCAL_ROOT=Path(package);manifest=LOCAL_ROOT/'LOCAL-INPUTS.json'
    need(manifest.is_file(),'DRAFT: paid catalogue LOCAL-INPUTS.json not yet finalized')
    LOCAL_ROWS={row['path']:row for row in json.loads(manifest.read_bytes())['files']}
    need('PAID-CATALOG.jsonl.gz' in LOCAL_ROWS,'missing complete paid catalogue pin')
    for name in LOCAL_ROWS:local(name)
    return {'package_data_inputs_prechecked':sorted(LOCAL_ROWS)}
def local(name):
    need(LOCAL_ROOT is not None and name in LOCAL_ROWS,'undeclared package data input '+name)
    row=LOCAL_ROWS[name];raw=safe(LOCAL_ROOT,name).read_bytes()
    need(digest(raw)==row['sha256'],'changed package data input '+name)
    if row.get('decompressed_sha256'):need(digest(gzip.decompress(raw))==row['decompressed_sha256'],'changed package data payload '+name)
    return raw
