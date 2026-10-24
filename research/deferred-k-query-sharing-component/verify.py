#!/usr/bin/env python3
"""Byte-custody wrapper for the independent deferred-K component checker.
Chris R / Clear1nsight, substantial OpenAI Codex assistance; Apache-2.0.
No producer/native/phase/price evaluation is invoked here.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent
BASE='1a3ced60b2f7a46bc70280a04f2eeb8ca027c700'
PACKET_SHA='9f4578a8d85a16f1d19b4fe759a2d5aa17c9d84d4028f48940e85c9843f3ce8e'
CHECKER_SHA='dae704de19122deed696cfcdc6fb1479faac66cd42aa4d87d9c0285a30d38600'
Q_PROOF_SHA='fb60187fea8346539abb61a08b1c525825cc84bd7c2847eb44a7c9590f3abee3'
EXPECTED_SHA='15bdc61d48d082224865f212ea8471d3f323b511bf1af1afd18c16895b0a5db9'
INTEGRITY_SHA256='f4950e188b82592eacc65a39c85b71f84847b8df4f8ce0d3c0e2ac0a28005fba'

def require(ok,message):
    if not ok:raise ValueError(message)
def authenticate(data,digest):
    require(hashlib.sha256(data).hexdigest()==digest,'SHA256 authentication failed')
def load(name):return json.loads((ROOT/name).read_bytes())
def inventory():
    return {p.relative_to(ROOT).as_posix():dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mode=oct(p.stat().st_mode&0o777),bytes=p.stat().st_size) for p in sorted(ROOT.rglob('*')) if p.is_file()}

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
    for row in load('ORIGINS.json'):
        require(row['authority']=='canonical','unexpected Git origin authority')
        origin(row['proof'],(ROOT/row['retained']).read_bytes(),BASE,row['proof']['path'])
    local=load('LOCAL-ORIGINS.json')
    for row in local['files']:
        data=(ROOT/row['path']).read_bytes();require(len(data)==row['bytes'],'LOCAL path remap length failed');authenticate(data,row['sha256'])
    packet=ROOT/'DEFERRED-K-COMPONENT-v1.json';checker=ROOT/'verification/check_deferred_k_independent_v2.py'
    authenticate(packet.read_bytes(),PACKET_SHA);authenticate(checker.read_bytes(),CHECKER_SHA)
    expected_raw=(ROOT/'evidence/RESULT-NORMAL-v2.json').read_bytes();authenticate(expected_raw,EXPECTED_SHA)
    require(expected_raw==(ROOT/'evidence/RESULT-OPTIMIZED-v2.json').read_bytes(),'retained normal/O receipts differ')
    expected=json.loads(expected_raw)
    require(expected['status']=='PASS_LITERAL_DEFERRED_K_COMPONENT_UNDER_RETAINED_NATIVE_SOURCE_PREMISES','retained result status')
    require(expected['checker_sha256']==CHECKER_SHA and expected['overlay_packet_sha256']==PACKET_SHA,'retained checker/packet binding')
    require(len(expected['controls'])==12 and expected['paid_delta_vs_baseT_plus_currentQ120']=={'1':-8},'controls or exact saved occurrence count changed')
    require(expected['paid_each_direction']=={'1':2313,'2':412,'3':510,'4':127,'5':40},'paid source profile changed')
    require(expected['helpers']['inverse_helper_composition_claimed'] is False,'helper inverse composition overclaim')
    require(expected['complete_caller'] is False and expected['gain_claimed'] is False and expected['new_kappa'] is None,'component promoted to funded caller')
    require(expected['raw_native_tape_replayed'] is False and expected['source_phase_census_replayed'] is False,'retained premise promoted to new replay')
    # These controls test the wrapper's source/origin authentication, not mathematics.
    try:authenticate(packet.read_bytes()+b'MUTANT',PACKET_SHA)
    except ValueError:pass
    else:raise ValueError('changed packet source control survived')
    bad=load('ORIGINS.json')[0];bad['proof']['trees'][0]['oid']='0'*40
    try:origin(bad['proof'],(ROOT/bad['retained']).read_bytes(),BASE,bad['proof']['path'])
    except ValueError:pass
    else:raise ValueError('forged canonical origin control survived')
    if replay:
        with tempfile.TemporaryDirectory(prefix='deferred-k-independent-') as folder:
            receipt=Path(folder)/'fresh.json'
            proof=ROOT/'verification/inputs/outputs/kappa0033-race-20261024/plan/BALANCED-J-CURRENT-Q-FRAME-audit/REPORT-v1.md'
            argv=[sys.executable,'-I','-Werror','-B','-X','pycache_prefix='+str(Path(folder)/'cache')]+(['-O'] if sys.flags.optimize else [])+[str(checker),'--packet',str(packet),'--packet-sha256',PACKET_SHA,'--source-q-proof',str(proof),'--source-q-proof-sha256',Q_PROOF_SHA,'--output',str(receipt)]
            run=subprocess.run(argv,capture_output=True,text=True,timeout=30)
            print('FRESH_COMPONENT_EVIDENCE '+json.dumps(dict(command=argv,exit_code=run.returncode,receipt_utf8=receipt.read_text() if receipt.exists() else None,stdout=run.stdout,stderr=run.stderr),sort_keys=True))
            require(run.returncode==0 and not run.stderr,'independent component replay failed: '+run.stderr)
            require(json.loads(receipt.read_bytes())==expected,'full fresh component certificate differs; zero field exclusions')
    after=inventory();require(after==before,'package bytes or modes changed during replay')
    digest=lambda value:hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
    return dict(status='PASS_DEFERRED_K_COMPONENT_PACKAGE_UNDER_RETAINED_NATIVE_PREMISES',canonical_base=BASE,immutable_files=len(before),fresh_component_certificate=replay,optimized=bool(sys.flags.optimize),normal_O_entire_certificate_equality=True,excluded_certificate_fields=[],saved_H1_occurrences=8,paid_H1_includes_saving=2313,complete_caller=False,funded_kappa=None,full_physical_helper_owned_rawdual_emitted=False,native_or_phase_replayed=False,economic_certificate_replayed=False,pre_custody_sha256=digest(before),post_custody_sha256=digest(after),inputs_and_modes_unchanged=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--integrity-only',action='store_true');args=parser.parse_args()
    print(json.dumps(verify(not args.integrity_only),sort_keys=True))
