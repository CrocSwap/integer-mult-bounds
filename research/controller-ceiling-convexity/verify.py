#!/usr/bin/env python3
"""Source-bound, Git-free replay of the scoped independent PR5405 ceiling check.
Chris R / Clear1nsight, with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
BASE = '1ec1119972c9aefe42525172d07b332fcff81cb4'
SOURCE = '314b56a6c0056c2358538f072c6fde9d365be44d'
MANIFEST_SHA256 = 'c928a9865a08f3944e62aa608e99877d7df76d5226023225de32a4922766d8bf'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def authenticate(data, digest):
    require(hashlib.sha256(data).hexdigest() == digest, 'SHA256 authentication failed')

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

def stable(receipt):
    return {k:v for k,v in receipt.items() if k!='environment'}

def verify(replay=True):
    inventory_bytes=(ROOT/'INTEGRITY.json').read_bytes()
    authenticate(inventory_bytes,MANIFEST_SHA256)
    inventory=json.loads(inventory_bytes)
    for row in inventory['files']:
        path=ROOT/row['path']
        require(not path.is_symlink() and path.is_file(),'missing or aliased immutable file '+row['path'])
        raw=path.read_bytes();require(len(raw)==row['bytes'],'input byte count changed')
        authenticate(raw,row['sha256'])
    source=(ROOT/'original/PROOF.md').read_bytes()
    origin(json.loads((ROOT/'origins/PR5405-PROOF.json').read_bytes()),source,SOURCE,'research/global-query-controller-ceiling/PROOF.md')
    origin(json.loads((ROOT/'origins/PR5405-NOTICE.json').read_bytes()),(ROOT/'original/source/NOTICE.md').read_bytes(),SOURCE,'research/global-query-controller-ceiling/source/NOTICE.md')
    require(source+b'\n'==(ROOT/'numerical/inputs/5405-PROOF.md').read_bytes(),'monitor +LF representation bridge failed')
    for row in json.loads((ROOT/'origins/CANONICAL.json').read_bytes()):
        origin(row['proof'],(ROOT/row['retained']).read_bytes(),BASE,row['path'])
    # Actual bad bytes and a forged Merkle branch must fail the same validators.
    try: authenticate(source+b'MUTANT',hashlib.sha256(source).hexdigest())
    except ValueError: pass
    else: raise ValueError('changed-source control survived')
    bad=json.loads((ROOT/'origins/PR5405-PROOF.json').read_bytes());bad['trees'][0]['oid']='0'*40
    try: origin(bad,source,SOURCE,'research/global-query-controller-ceiling/PROOF.md')
    except ValueError: pass
    else: raise ValueError('forged-origin control survived')
    freeze=json.loads((ROOT/'audit/FREEZE.json').read_bytes())
    require(freeze['status']=='PASS_SCOPED_FIXED_FAMILY_CEILING','audit freeze does not pass')
    authenticate((ROOT/'numerical/FINAL-MANIFEST-v3.json').read_bytes(),freeze['numeric_manifest_sha256'])
    for row in freeze['audit_files']:
        authenticate((ROOT/'audit'/row['path']).read_bytes(),row['sha256'])
    for row in json.loads((ROOT/'numerical/FINAL-MANIFEST-v3.json').read_bytes())['files']:
        authenticate((ROOT/'numerical'/row['path']).read_bytes(),row['sha256'])
    reference=json.loads((ROOT/'numerical/receipts/arithmetic-v3.json').read_bytes())
    optimized=json.loads((ROOT/'numerical/receipts/arithmetic-v3-optimized.json').read_bytes())
    require(stable(reference)==stable(optimized),'frozen normal/O outputs differ')
    require(reference['status']=='PASS_SCOPED_ARITHMETIC','wrong frozen acceptance status')
    if replay:
        with tempfile.TemporaryDirectory(prefix='controller5405-') as folder:
            receipt=Path(folder)/'fresh.json'
            argv=[sys.executable,'-I','-B']+(['-O'] if sys.flags.optimize else [])+[str(ROOT/'numerical/check_ceiling.py'),'--receipt',str(receipt)]
            done=subprocess.run(argv,capture_output=True,text=True,timeout=60)
            require(done.returncode==0,'independent arithmetic replay failed: '+done.stderr)
            require(not done.stderr,'arithmetic replay emitted stderr')
            require(stable(json.loads(receipt.read_bytes()))==stable(reference),'fresh proof-relevant output differs')
    return {'status':'PASS_CONTROLLER_CEILING_CONVEXITY','source_head':SOURCE,'canonical_main':BASE,
            'immutable_files':len(inventory['files']),'fresh_arithmetic':replay,'optimized':bool(sys.flags.optimize),
            'scope':'equation-(1) fixed invoice family; .00302728825 <= kappa < 1',
            'origin_controls':['changed source rejected','forged Merkle branch rejected'],
            'scientific_controls':len(reference['negative_controls']),
            'not_claimed':['physical/native/compiler admission','global optimum','kappa gain','PR5402 transfer','formal kernel','human review']}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--integrity-only',action='store_true');args=ap.parse_args()
    print(json.dumps(verify(not args.integrity_only),sort_keys=True))
