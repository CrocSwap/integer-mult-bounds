#!/usr/bin/env python3
"""Portable verification for explicit fixed-profile standalone-tail theorem.
Chris R / Clear1nsight, substantial OpenAI Codex assistance; Apache-2.0.
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
BASE='d277c97824e50782da6adbc486ca3c76c8fc687e'
INTEGRITY_SHA256='33afdac76077f8f056e426343d02e37800414d735c6bc9c72f6c2010e4ffa7ce'
ORIGINAL_LOCAL_RECEIPT='c40de7675b9a85e621f8e60e42c4337ac31b1192490fd05c708eb2192c6155bb'

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
    before=inventory();raw=(ROOT/'INTEGRITY.json').read_bytes();authenticate(raw,INTEGRITY_SHA256)
    declaration=json.loads(raw)
    require(set(before)=={r['path'] for r in declaration['files']}|{'INTEGRITY.json','verify.py'},'package inventory differs')
    for row in declaration['files']:
        p=ROOT/row['path'];require(p.is_file() and not p.is_symlink(),'input missing or aliased')
        data=p.read_bytes();require(len(data)==row['bytes'],'input byte count changed');authenticate(data,row['sha256'])
    for row in load('ORIGINS.json'):
        origin(row['proof'],(ROOT/row['retained']).read_bytes(),BASE,row['proof']['path'])
    expected=load('ORIGINAL-PRICE-PROJECTION.json')
    require(expected['original_LOCAL_receipt_sha256']==ORIGINAL_LOCAL_RECEIPT,'original local receipt anchor changed')
    model=load('MODEL.json')
    require(model['canonical_base']==BASE and model['all240_main_targets_unearned'] is True,'model scope changed')
    require(not model['physical_derivation_admitted'] and model['funded_kappa'] is None,'hypothesis promoted to admission')
    require(expected['fixed_paid']==model['paid_lower_bound'] and expected['retained_helpers']==model['helper_upper_bound'],'projection/model profile mismatch')
    require(expected['unearned_main']==model['hypothetical_main_upper_bound'],'optimistic target hypothesis differs')
    # Fail-closed byte and source-origin controls run without any numerical engine.
    library=(ROOT/'independent_powers.py').read_bytes()
    try:authenticate(library+b'MUTANT',hashlib.sha256(library).hexdigest())
    except ValueError:pass
    else:raise ValueError('library byte mutation survived')
    bad=load('ORIGINS.json')[0];bad['proof']['trees'][0]['oid']='0'*40
    try:origin(bad['proof'],(ROOT/bad['retained']).read_bytes(),BASE,bad['proof']['path'])
    except ValueError:pass
    else:raise ValueError('forged origin survived')
    signed_preflight='not_run_in_integrity_only_mode'
    if replay:
        preargv=[sys.executable,'-I','-B']+(['-O'] if sys.flags.optimize else [])+[str(ROOT/'compare_recursive_invoices.py'),str(ROOT/'BASELINE-INVOICE.json'),str(ROOT/'WITH-TAIL-INVOICE.json')]
        pre=subprocess.run(preargv,capture_output=True,text=True,timeout=30)
        print('SIGNED_INVOICE_PREFLIGHT_EVIDENCE '+json.dumps({'command':preargv,'exit_code':pre.returncode,'stdout':pre.stdout,'stderr':pre.stderr},sort_keys=True))
        require(pre.returncode==0 and not pre.stderr,'official signed-invoice preflight failed')
        preflight=json.loads(pre.stdout)
        require(preflight['classification']=='uniformly_worse' and preflight['signed_net_delta']=={'17':8} and preflight['delta_targets']=={},'unexpected declared invoice delta')
        signed_preflight=preflight['classification']
        with tempfile.TemporaryDirectory(prefix='abstract-tail-price-') as folder:
            receipt=Path(folder)/'fresh.json'
            argv=[sys.executable,'-I','-B','-X','pycache_prefix='+str(Path(folder)/'cache')]+(['-O'] if sys.flags.optimize else [])+[str(ROOT/'abstract_price.py'),'--receipt',str(receipt)]
            done=subprocess.run(argv,capture_output=True,text=True,timeout=30)
            print('FRESH_ABSTRACT_PRICE_EVIDENCE '+json.dumps({'command':argv,'exit_code':done.returncode,'receipt_utf8':receipt.read_text() if receipt.exists() else None,'stdout':done.stdout,'stderr':done.stderr},sort_keys=True))
            require(done.returncode==0 and not done.stderr,'abstract price check failed: '+done.stderr)
            fresh=json.loads(receipt.read_bytes())
            require(fresh['status']=='PASS_EXPLICIT_PROFILE_AND_DECLARED_STANDALONE_TAIL_BOUND','unexpected abstract result')
            for key in ('fixed_paid','retained_helpers','unearned_main','conditional_targets','points'):
                require(fresh[key]==expected[key],'abstract/original mathematical pricing differs: '+key)
            require(len(fresh['negative_controls'])==4 and all(r['observed']==r['expected'] for r in fresh['negative_controls']),'model controls incomplete')
            require(fresh['funded_kappa'] is None and not fresh['physical_derivation_admitted'],'abstract result overclaims admission')
    after=inventory();require(after==before,'source/package bytes changed during verification')
    custody=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
    return dict(status='PASS_EXPLICIT_PROFILE_STANDALONE_TAIL_PACKAGE',canonical_base=BASE,
        fresh_abstract_price=replay,optimized=bool(sys.flags.optimize),immutable_files=len(before),
        original_price_projection_only=True,private_physical_word_included=False,signed_invoice_preflight=signed_preflight,
        theorem_domain='.0033 <= C < 1',cost_hypothesis='eight independently paid whole H17 jobs',
        all240H25_unearned=True,physical_derivation_admitted=False,funded_kappa=None,
        pre_custody_sha256=custody(before),post_custody_sha256=custody(after),inputs_unchanged=True,
        excludes=['universal decoder/circuit barrier','rank minimality','fusion obstruction','new kappa admission','native/compiler/precision/outer replay'])

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--integrity-only',action='store_true');a=ap.parse_args()
    print(json.dumps(verify(not a.integrity_only),sort_keys=True))
