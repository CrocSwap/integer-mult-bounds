#!/usr/bin/env python3
"""Independent-endpoint replay of the exact proposed scalar word, no optimizer.

Apache-2.0; substantial OpenAI Codex assistance. The native interpreters are
credited retained dependencies, not newly independent implementations here.
"""
from collections import defaultdict
from copy import deepcopy
from hashlib import sha256
from fractions import Fraction
from pathlib import Path
import json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from construct import construct,T
sys.path.insert(0,str(ROOT/'research/warp-interface-20261022'))
from warp_merge import F

def climbs(word):
    result=defaultdict(list)
    for e in word:
        if e[0]=='climb':result[e[2]].append(e[3:])
    return dict(result)

def main():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        F.need(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'Pinned source '+row['path'])
    old,new,history=construct();c=new['canonical']
    F.need(c==old['canonical'],'All helper/main boundaries, native maps and frame registry are unchanged')
    V=F.load(ROOT/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py','trace_cao_rows')
    X=F.load(ROOT/'research/kappa-rebuild/complex/native_extensions.py','trace_cao_literal')
    result={'status':'PASS_CAO_151_MACROS_SAME_COMPLETE_PAID_PROFILE','new_kappa':None,'directions':{}}
    for d,p in new['programs'].items():
        original=old['programs'][d];b=d=='backward'
        F.need(climbs(p)==climbs(original),'Every chronological per-owner transport is unchanged')
        F.need([e for e in p if e[0] not in ('climb','scalar')]==[e for e in original if e[0] not in ('climb','scalar')],'Native warps, centers, adapters and phases are unchanged')
        F.need(sum(e[0]=='scalar' for e in original)-sum(e[0]=='scalar' for e in p)==151,'Exactly151 removed scalar macros')
        rows,rec=X.literal_replay(V,c,p,b)
        F.need(all(rows['L',r]==V.expected(('L',r),[],b,False) for r in range(632)),'All632 arbitrary independent endpoint columns')
        F.need(Fraction(rec['max_formal_prefix_l1']) < 2**192,
               'Retained formal prefix magnitude envelope')
        rebound=deepcopy(c);rebound['R']=len(c['start'])-2*c['v'];rebound['local_profile']={int(k):v for k,v in rec['paid_profile'].items()}
        second=V.replay(p,rebound,[],b,False)
        _,baseline=X.literal_replay(V,c,original,b)
        wrong=deepcopy(p);e=next(e for e in wrong if T.is_add(e));e[1][3]*=-1
        rejected=False
        try:
            badrows,_=X.literal_replay(V,c,wrong,b)
            rejected=any(badrows['L',r]!=V.expected(('L',r),[],b,False) for r in range(632))
        except (ValueError,AssertionError):rejected=True
        F.need(rejected,'A scalar coefficient sign corruption is rejected')
        result['directions'][d]={'removed_scalar_macros':151,'real_scalar_allowance_before':baseline['real_scalar_allowance'],'real_scalar_allowance_after':rec['real_scalar_allowance'],'saved_allowance':baseline['real_scalar_allowance']-rec['real_scalar_allowance'],'paid':rec['paid_profile'],'owned_center_cleared':rec['arbitrary_owned_C0_cleared'],'all632_two_interpreters':True,'unchanged_ordered_climbs':True,'wrong_scalar_sign_rejected':True,'payload_sha256':sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
        result['directions'][d]['max_formal_prefix_l1']=rec['max_formal_prefix_l1']
        result['directions'][d]['max_denominator']=rec['max_denominator']
        print('PASS',d,result['directions'][d]['saved_allowance'],flush=True)
    print(json.dumps(result,sort_keys=True))
    return result
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=json.loads(json.dumps(main()));path=HERE/'VERIFICATION.json'
    if args.write:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:F.need(result==json.loads(path.read_text()),'Exact deterministic committed receipt')
    print('PASS_DETERMINISTIC_CAO_TRACE_RECEIPT')
