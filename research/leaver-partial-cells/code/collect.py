"""Collect each variant: cold44 profile delta vs baseline, cold-end pairing, native/local-replay outcome,
coefficient (L1 prefix) bits, and the κ of #1005's global profile plus 72 x delta (ideal rank-48 packing)."""
import json,gzip,os,sys
from collections import Counter
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from price_delta import price
OUT=sys.argv[1];rd=lambda p:json.loads(gzip.decompress(open(p,'rb').read()))
def prof(d):
    w=rd(f'{OUT}/{d}/cold44/FULL-WORD.json.gz');c=json.load(open(f'{OUT}/{d}/cold44/CONSTRUCTION.json'))
    return Counter({int(k):v for k,v in w['report']['local_profile'].items()}),[b['pairing_rank'] for b in c['blocks']],w['report']['R']
def bits(d):
    p=f'{OUT}/{d}.prefix'
    if not os.path.exists(p):return None
    return {('backward' if 'True' in l else 'forward'):int(l.split()[2]) for l in open(p) if l.startswith('PREFIX')}
def stage(d):
    log=open(f'{OUT}/{d}.log').read() if os.path.exists(f'{OUT}/{d}.log') else ''
    passed=[l.split()[1] for l in log.splitlines() if l.startswith('PASS ')]
    fail=None
    for name in ('native','ledgers','local-replay','wrappers'):
        lp=f'{OUT}/{d}/{name}.log'
        if os.path.exists(lp) and name not in passed:
            fail=(name,[l for l in open(lp).read().splitlines() if 'Error' in l][-1:]);break
    return passed,fail
H0,P0,R0=prof('base');res={'baseline':dict(R=R0,pairing=P0,profile=dict(H0),bits=bits('base'),kappa=price({},tag='base'))}
for d in ('v1-yy-entering','v2-two-kept','v3-fresh-all16','v3-fresh-4567','v3-fresh-one'):
    if not os.path.exists(f'{OUT}/{d}/cold44/FULL-WORD.json.gz'):res[d]=dict(status='no cold44 word',stage=stage(d));continue
    H,Pr,R=prof(d);dd=Counter(H);dd.subtract(H0);dd={k:v for k,v in sorted(dd.items()) if v}
    res[d]=dict(R=R,helpers_removed=R0-R,pairing=Pr,delta_per_call=dd,bits=bits(d),stage=stage(d),kappa_ideal_packing=price(dd,tag=d))
json.dump(res,open(f'{OUT}/RESULTS.json','w'),indent=1);print(json.dumps(res,indent=1))
