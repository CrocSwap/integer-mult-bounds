"""Turn the loop's literal per-child assignment into PR505-format roles (whole owners, chronological offsets).
Usage: nominate2.py LOOP.json PLAN.json RETIMED_VARIANT OUT-OWNERS.json.gz OUT-PLAN.json"""
import gzip,json,sys
from collections import Counter,defaultdict
LOOP,PLAN,RET,OUTO,OUTP=sys.argv[1:6]
agg=json.load(open(LOOP));plan=json.load(open(PLAN));order=[tuple(o)for o in plan['order']]
assert not agg['fails'],agg['fails']
canon=json.loads(gzip.decompress(open(RET+'/split-centres/CANONICAL-WORD.json.gz','rb').read()))
R=560;V=120;widths=[9-len(canon['frames'][canon['start'][240+h]])for h in range(R)]
assert Counter(widths)=={int(k):v for k,v in agg['widths'].items()}
sides={int(k):v for k,v in plan['sides'].items()};pairs={int(k):v for k,v in plan['pairs'].items()}
bywidth=defaultdict(list)
for h,w in enumerate(widths):bywidth[w].append(h)
pending={t:{w:list(bywidth[w])for w in bywidth}for t in range(72)}
roles=[]
for key,a in sorted(agg['assign'].items()):
    i,orp=map(int,key.split(','));perport=defaultdict(list)
    for t,w,p in a:perport[p].append((t,w))
    for p,lst in perport.items():
        assert len({t for t,w in lst})==len(lst),'two roles of one call on one port'
        off=0
        for t,w in sorted(lst):
            h=pending[t][w].pop();stg,rep=order[t]
            roles.append(dict(owner_replica=orp,child=i,port=p,time=t,width=w,offset=off,stage=stg,replica=rep,helper=h,copy=orp*V+p,family=orp*960+(2*pairs[i]+sides[i])*V+p));off+=w
assert all(not any(pending[t].values())for t in range(72)),'unplaced helpers'
assert len(roles)==40320 and len({(r['stage'],r['replica'],r['helper'])for r in roles})==40320
roles.sort(key=lambda r:(r['time'],r['helper']))
open(OUTO,'wb').write(gzip.compress(json.dumps(roles,separators=(',',':')).encode(),mtime=0))
out=dict(plan);out['baseline_widths']=widths;out['status']='AGGREGATE_CPSAT_WITH_NOMINATION_CUTS';
for k in('numeric_saving','solver_status','gap','profile','patterns','stage_assignments','selected','variants','source_local_profile','source_provider'):out.pop(k,None)
out['aggregate']=dict(status=agg['status'],objective=agg['objective'],bound=agg['bound'],cuts=len(agg['cuts']))
json.dump(out,open(OUTP,'w'),indent=1);print('roles',len(roles),'written; remainders',agg['remainders'])
