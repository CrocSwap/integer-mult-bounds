#!/usr/bin/env python3
"""Offline replay of two frozen PR5383 stop certificates.

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
Frozen worker engines retain their exact bytes and predecessor attribution.
The inventory/Merkle design follows the retained independent PR5377 packet.
"""
from pathlib import Path, PurePosixPath
import argparse, gzip, hashlib, json, os, shutil, subprocess, sys, tempfile, time
HERE=Path(__file__).resolve().parent
MAIN='1ec1119972c9aefe42525172d07b332fcff81cb4'
HEAD='4bd6efa51a495a7c7b7754915cf0244e7e60969e'
MANIFEST_SHA='ae6a1b933c386feabc9bab3300163df41e94bd3ddeeff973955695d33d5b11c8'
CAPSULE_SHA='4f1c35140c37ec16dedec68270b0ec5564ff3b9a2a7de32086ddb79f6959b7e6'
CAP='evidence/campaign/09-capsule-cold/capsule-v1'
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw,kind='blob'):return hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def read(path):return json.loads(path.read_bytes())
def at(root,name):
    p=PurePosixPath(name);need(not p.is_absolute() and '..' not in p.parts and str(p)==name,'unsafe path')
    q=root
    for part in p.parts:q=q/part;need(not q.is_symlink(),'symlink path '+name)
    need(q.is_file(),'missing file '+name);return q

def inventory(root,manifest,complete=True):
    seen=set()
    for row in manifest['files']:
        name=row['path'];need(name not in seen,'duplicate path');seen.add(name)
        raw=at(root,name).read_bytes()
        need(len(raw)==row['bytes'] and sha(raw)==row['sha256'] and blob(raw)==row['git_blob'],'immutable byte guard '+name)
    if complete:
        actual={q.relative_to(root).as_posix() for folder in ['evidence','git-evidence'] for q in (root/folder).rglob('*') if q.is_file()}
        need(actual==seen-{'SOURCE-GUARDS.json'},'complete frozen inventory')
    return len(seen)

def obj(root,kind,oid):
    raw=at(root,'git-evidence/'+kind+'/'+oid).read_bytes();need(blob(raw,kind)==oid,'raw Git '+kind);return raw

def entries(raw):
    i=0;out={}
    while i<len(raw):
        j=raw.index(b' ',i);k=raw.index(b'\0',j);name=raw[j+1:k].decode()
        need(name not in out and k+21<=len(raw),'malformed Git tree')
        out[name]=(raw[i:j].decode(),raw[k+1:k+21].hex());i=k+21
    return out

def bindings(root):
    guards=read(root/'SOURCE-GUARDS.json')['rows'];need(len(guards)==36,'36 complete source bindings')
    for row in guards:
        raw=obj(root,'commit',row['commit']);head=raw.split(b'\n',1)[0].split();need(head[0]==b'tree','commit tree header');tree=head[1].decode()
        parts=row['path'].split('/')
        for i,part in enumerate(parts):
            mode,oid=entries(obj(root,'tree',tree))[part]
            if i==len(parts)-1:
                need(mode=='100644' and oid==row['git_blob'] and blob(at(root,row['local']).read_bytes())==oid,'raw source binding '+row['path'])
            else:need(mode=='40000','tree ancestor');tree=oid
    raw=at(root,CAP+'/IMMUTABLE-MANIFEST.json').read_bytes();need(sha(raw)==MANIFEST_SHA,'exact capsule manifest')
    manifest=json.loads(raw);need(manifest['candidate_head']==HEAD and manifest['canonical_main']==MAIN,'frozen source scope')
    need(len(manifest['rows'])==36,'source manifest row count')
    expected={(r['source_commit'],r['path'],r['git_blob'],CAP+'/'+r['capsule_path']) for r in manifest['rows']}
    need(expected=={(r['commit'],r['path'],r['git_blob'],r['local']) for r in guards},'manifest and raw Merkle coverage agree')
    return len(guards)

def launch(script):
    # The original engines use assertions. Always run them without -O and clear
    # inherited optimization, even if the wrapper itself is tested under -O.
    env=dict(os.environ);env.pop('PYTHONOPTIMIZE',None)
    env['PYTHONPYCACHEPREFIX']=str(script.parent/'private-bytecode')
    return subprocess.run([sys.executable,'-I','-W','error','-B',str(script)],cwd=script.parent,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=55)

def success(run,label):need(run.returncode==0,label+' failed: '+run.stderr[-2500:])
def stable(x):
    if isinstance(x,dict):return {k:stable(v) for k,v in x.items() if k not in ('runtime_seconds','max_rss_kib','feasibility_sha256','source_receipt_sha256')}
    if isinstance(x,list):return [stable(v) for v in x]
    return x

def replay(root,tmp):
    dst=tmp/'evidence';shutil.copytree(root/'evidence',dst)
    campaign=dst/'campaign';mode=campaign/'06-controller-modes';zero=campaign/'07-frozen-zero'
    started=time.monotonic();run=launch(mode/'reproduce.py');success(run,'562-controller replay')
    need('PASS: exact 562-entry endpoint/invoice table and all1683' in run.stdout,'controller replay complete')
    mode_seconds=round(time.monotonic()-started,3)
    started=time.monotonic();run=launch(zero/'census.py');success(run,'chronological row replay')
    old=read(root/'evidence/campaign/07-frozen-zero/RESULT-v2.json');fresh=read(zero/'RESULT-v2.json')
    # Compression streams are containers. The complete decompressed ordered row
    # certificates, and every stable proof-relevant receipt field, must agree.
    oldtrace=gzip.decompress((root/'evidence/campaign/07-frozen-zero/PAID-ROWS-v2.jsonl.gz').read_bytes())
    freshtrace=gzip.decompress((zero/'PAID-ROWS-v2.jsonl.gz').read_bytes())
    need(oldtrace==freshtrace,'complete decompressed paid-row trace differs')
    for receipt in [old,fresh]:receipt['row_trace'].pop('sha256');receipt['row_trace'].pop('bytes')
    need(stable(old)==stable(fresh),'full stable chronological receipt differs')
    need(fresh['census']['paid_rows']==3282 and fresh['new_paid_deletions']==0 and len(fresh['census']['existing_zero_retags'])==8,'frozen-zero claim')
    run=launch(zero/'check_certificates.py');success(run,'single-monomial certificates')
    need(stable(read(zero/'CERTIFICATE-CHECK-v1.json'))==stable(read(root/'evidence/campaign/07-frozen-zero/CERTIFICATE-CHECK-v1.json')),'full certificate receipt differs')
    certificate=read(zero/'CERTIFICATE-CHECK-v1.json')
    need(certificate['checked_paid_rows']==3282 and certificate['invertible_binary_source_generators']==72,'native-specialization certificate coverage')
    return dict(controller=dict(allocations=562,changed=561,negative_target_cases=1683,seconds=mode_seconds),zero=dict(paid_rows=3282,new_paid_deletions=0,seconds=round(time.monotonic()-started,3)),private_zero=zero)

def controls(root,tmp,manifest,zero):
    # Actual byte guard, with source available at the same literal packet path.
    row=next(r for r in manifest['files'] if r['path'].endswith('/snapshot/research/kappa-joint-relations-20261023/WORD.json.gz'))
    test=tmp/'tamper';p=test/row['path'];p.parent.mkdir(parents=True);p.write_bytes(at(root,row['path']).read_bytes()+b'!')
    try:inventory(test,{'files':[row]},False)
    except ValueError as e:need('immutable byte guard' in str(e),'tamper control wrong failure')
    else:raise ValueError('source tamper accepted')
    # Change only the certificate sign, retain the complete row, and refresh
    # trace-container guards. The semantic coefficient check must reject it.
    trace=zero/'PAID-ROWS-v2.jsonl.gz';rows=[json.loads(line) for line in gzip.decompress(trace.read_bytes()).splitlines()]
    rows[0]['independent_monomial_certificate'][2]*=-1
    payload=b''.join(json.dumps(r,sort_keys=True,separators=(',',':')).encode()+b'\n' for r in rows)
    trace.write_bytes(gzip.compress(payload,mtime=0));receipt=read(zero/'RESULT-v2.json');receipt['row_trace']['sha256']=sha(trace.read_bytes());receipt['row_trace']['bytes']=trace.stat().st_size
    (zero/'RESULT-v2.json').write_text(json.dumps(receipt))
    run=launch(zero/'check_certificates.py')
    need(run.returncode!=0 and 'selected coefficient is exactly one invertible monomial' in run.stderr,'forged singleton certificate wrong failure')
    return ['changed literal source bytes rejected by actual inventory guard','forged singleton coefficient rejected after refreshed trace hash','fresh frozen census executes preparation-sign corruption rejection','fresh frozen controller executes oriented-query mutation rejection']

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--integrity-only',action='store_true');args=parser.parse_args();start=time.monotonic()
    raw=(HERE/'CAPSULE.json').read_bytes();need(sha(raw)==CAPSULE_SHA,'capsule inventory hash');manifest=json.loads(raw)
    need(manifest['canonical_base']==MAIN and manifest['source_head']==HEAD,'packet source identity')
    count=inventory(HERE,manifest);bound=bindings(HERE)
    out=dict(status='PASS_FROZEN5383_SCOPED_CEILING_INTEGRITY',inventory_files=count,raw_merkle_source_paths=bound,head=HEAD)
    if not args.integrity_only:
        with tempfile.TemporaryDirectory(prefix='frozen5383-ceilings-') as folder:
            tmp=Path(folder);fresh=replay(HERE,tmp);out['controls']=controls(HERE,tmp,manifest,fresh.pop('private_zero'));out['fresh_replays']=fresh
        inventory(HERE,manifest);out.update(status='PASS_TWO_FROZEN5383_SCOPED_STOP_CERTIFICATES',target_savings=['.00302235','.00302666','.003026674765'],all_positive_tensor_widths_for_zero_census=True,new_kappa=None,selected_record_changed=False)
    out['seconds']=round(time.monotonic()-start,3);print(json.dumps(out,sort_keys=True,indent=2))
if __name__=='__main__':main()
