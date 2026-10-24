#!/usr/bin/env python3
"""Portable byte-custody and exact-certificate replay; no pricing engine.
Chris R / Clear1nsight, with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent
BASE='1a3ced60b2f7a46bc70280a04f2eeb8ca027c700'
PUBLIC_MODEL='fe4c345778554ec5c02368b1ddf2f6918eeb0df5'
INTEGRITY_SHA256='8e2ae40d94cce2dafbaf0fbca41fd4a167fece1e94f8be8bdabd1a49f7d4c0f8'

def require(ok,message):
    if not ok:raise ValueError(message)
def authenticate(data,digest):
    require(hashlib.sha256(data).hexdigest()==digest,'SHA256 authentication failed')
def load(name):return json.loads((ROOT/name).read_bytes())
def inventory():return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.rglob('*')) if p.is_file()}

def object_id(kind, data):
    return hashlib.sha1(kind.encode()+b' '+str(len(data)).encode()+b'\0'+data).hexdigest()

def origin(proof, raw, expected_commit, expected_path):
    require(proof['commit'] == expected_commit and proof['path'] == expected_path, 'origin identity changed')
    commit = base64.b64decode(proof['commit_bytes_base64'], validate=True)
    require(object_id('commit',commit)==expected_commit, 'raw commit hash failed')
    require(commit.startswith(b'tree '), 'commit tree header missing')
    child = commit.splitlines()[0][5:].decode('ascii')
    parts = expected_path.split('/')
    require(len(parts)==len(proof['trees']), 'origin tree depth mismatch')
    for part, row in zip(parts,proof['trees']):
        tree=base64.b64decode(row['bytes_base64'],validate=True)
        require(row['oid']==child==object_id('tree',tree), 'raw tree hash failed')
        require(row['component']==part, 'path component mismatch')
        entries={}; cursor=0
        while cursor<len(tree):
            space=tree.index(b' ',cursor); zero=tree.index(b'\0',space)
            name=tree[space+1:zero].decode('utf-8'); mode=tree[cursor:space]
            require(name not in entries and zero+21<=len(tree),'malformed tree')
            entries[name]=(mode,tree[zero+1:zero+21].hex());cursor=zero+21
        require(part in entries,'path component absent')
        mode,child=entries[part]
        require(mode in ((b'100644',b'100755') if part==parts[-1] else (b'40000',)), 'unexpected object mode')
    require(child==proof['blob']==object_id('blob',raw),'original Git blob failed')
    require(len(raw)==proof['bytes'],'source byte count mismatch')
    authenticate(raw,proof['sha256'])

def verify(replay=True):
    before=inventory();raw=(ROOT/'INTEGRITY.json').read_bytes();authenticate(raw,INTEGRITY_SHA256);declaration=json.loads(raw)
    require(set(before)=={r['path'] for r in declaration['files']}|{'INTEGRITY.json','verify.py'},'package inventory differs')
    for row in declaration['files']:
        p=ROOT/row['path'];require(p.is_file() and not p.is_symlink(),'immutable file missing or aliased')
        data=p.read_bytes();require(len(data)==row['bytes'],'input length mismatch');authenticate(data,row['sha256'])
    authorities={'canonical':BASE,'public5418':PUBLIC_MODEL}
    for row in load('ORIGINS.json'):origin(row['proof'],(ROOT/row['retained']).read_bytes(),authorities[row['authority']],row['proof']['path'])
    model=load('MODEL.json');public=load('public5418/MODEL.json')
    targets=Counter(public['helper_upper_bound']);targets.update(public['hypothetical_main_upper_bound'])
    require(model['P0']==public['paid_lower_bound'] and model['T0']==dict(targets),'public baseline profile differs')
    require(model['all240H25_hypothetical'] and not model['actual_future_ledger_checked'] and model['R0_upper_is_explicit_conditional_premise'],'conditional theorem scope changed')
    raw_public=(ROOT/'public5418/MODEL.json').read_bytes()
    try:authenticate(raw_public+b'MUTANT',hashlib.sha256(raw_public).hexdigest())
    except ValueError:pass
    else:raise ValueError('changed public model control survived')
    bad=load('ORIGINS.json')[0];bad['proof']['trees'][0]['oid']='0'*40
    try:origin(bad['proof'],(ROOT/bad['retained']).read_bytes(),authorities[bad['authority']],bad['proof']['path'])
    except ValueError:pass
    else:raise ValueError('forged origin control survived')
    if replay:
        with tempfile.TemporaryDirectory(prefix='robust-tail-integers-') as folder:
            receipt=Path(folder)/'fresh.json'
            argv=[sys.executable,'-I','-B','-X','pycache_prefix='+str(Path(folder)/'cache')]+(['-O'] if sys.flags.optimize else [])+[str(ROOT/'check_envelope.py'),'--receipt',str(receipt)]
            run=subprocess.run(argv,capture_output=True,text=True,timeout=30)
            print('FRESH_INTEGER_ENVELOPE_EVIDENCE '+json.dumps({'command':argv,'exit_code':run.returncode,'receipt_utf8':receipt.read_text() if receipt.exists() else None,'stdout':run.stdout,'stderr':run.stderr},sort_keys=True))
            require(run.returncode==0 and not run.stderr,'integer envelope verification failed: '+run.stderr)
            value=json.loads(receipt.read_bytes())
            require(value['status']=='PASS_STATIC_RATIONAL_INTEGER_PROFILE_ENVELOPE','unexpected exact certificate status')
            require(len(value['negative_controls'])==9,'missing domain/model countercontrol')
            require(value['R0_upper_assumed'] and not value['actual_future_mixed_budget_verified'],'conditional budget promoted to verification')
            require(value['all240H25_hypothetical'] and not value['rank_bound_is_ambient_certificate'] and not value['compiler_admitted'] and value['funded_kappa'] is None,'envelope scope overclaim')
    after=inventory();require(after==before,'source/package bytes changed during replay')
    digest=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
    return dict(status='PASS_CONDITIONAL_INTEGER_PROFILE_ENVELOPE_PACKAGE',canonical_base=BASE,
        public_model_origin=PUBLIC_MODEL,immutable_files=len(before),fresh_integer_certificate=replay,optimized=bool(sys.flags.optimize),
        R0_upper_assumed=True,actual_future_mixed_budget_verified=False,all240H25_hypothetical=True,
        physical_data_included=False,rank_bound_is_ambient_certificate=False,compiler_admitted=False,funded_kappa=None,
        pre_custody_sha256=digest(before),post_custody_sha256=digest(after),inputs_unchanged=True,
        universal_coverage='Written quantified proof; finite certificate checks do not enumerate future profiles.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--integrity-only',action='store_true');a=p.parse_args()
    print(json.dumps(verify(not a.integrity_only),sort_keys=True))
