"""Sharp T29 capacity16 projection, exact whole-helper invoices. Apache-2.0."""
import hashlib,itertools,json,sys
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
WIDTHS=(4,5,7,8,9);PRICE=dict(zip(WIDTHS,(-1,-20,-8,-2,4)));BONUS={8:2,16:4,32:8,48:-13}
QUOTAS={8:19488,16:12992,32:12992,48:12992};DEMAND={4:20880,5:8352,7:14094,8:31842,9:56376};PROFILE={0:49770,1:4,2:1,48:8689}
# Counts are affine in t,e: constant, t coefficient, e coefficient.
ROWS=[(8,(8,),(11202,0,0)),(8,(4,4),(8286,0,0)),(16,(9,7),(4824,2,1)),(16,(8,8),(8168,-2,-1)),(32,(9,9,9,5),(8352,0,0)),(32,(9,9,9,4),(4,0,0)),(32,(9,9,8,4),(1,0,0)),(32,(9,9,7,7),(4635,-1,-1)),(32,(9,8,8,7),(0,0,1)),(32,(8,8,8,8),(0,1,0)),(48,(),(8689,0,0)),(48,(9,9,9,9,8,4),(4303,0,0))]
def need(x,m):
    if not x:raise ValueError(m)
def patterns():
    out=[];upper={}
    for cap in BONUS:
        for cs in itertools.product(*(range(cap//w+1) for w in WIDTHS)):
            mass=sum(c*w for c,w in zip(cs,WIDTHS))
            if mass<=cap:
                remainder=cap-mass;score=BONUS[cap]+sum(c*PRICE[w] for c,w in zip(cs,WIDTHS));out.append((cap,cs,remainder,score));upper[remainder]=max(score,upper.get(remainder,-10**9))
    return out,upper
def witness(x):
    need(type(x) is int and 4824<=x<=12992,'outside exact range');t,e=divmod(x-4824,2)
    return [(cap,ws,a+b*t+c*e) for cap,ws,(a,b,c) in ROWS if a+b*t+c*e]
def invoice(entries,upper):
    caps=Counter();widths=Counter();ranks=Counter();score=0
    for cap,ws,n in entries:
        need(type(n) is int and n>0 and cap in BONUS and all(w in PRICE for w in ws) and sum(ws)<=cap,'legal whole-helper bin')
        price=BONUS[cap]+sum(PRICE[w] for w in ws);r=cap-sum(ws);need(price==upper[r],'zero-slack tight pattern')
        caps[cap]+=n;ranks[r]+=n;score+=n*price
        for w in ws:widths[w]+=n
    need(dict(caps)==QUOTAS and dict(widths)==DEMAND and dict(ranks)==PROFILE and score==-112868,'full invoice')
    return score
def run():
    for pin in json.loads((H/'SOURCES.json').read_text())['files']:
        if pin['usage']=='input':need(hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()==pin['sha256'],'source hash')
    bins,upper=patterns();need(len(bins)==1163,'complete bin census')
    tight=[p for p in bins if p[2] in PROFILE and p[3]==upper[p[2]]]
    need(sum(QUOTAS[c]*BONUS[c] for c in QUOTAS)+sum(DEMAND[w]*PRICE[w] for w in DEMAND)==sum(PROFILE[r]*upper[r] for r in PROFILE)==-112868,'zero aggregate price slack forces every bin tight')
    need(all(p[0]==32 and not p[1][2] and not p[1][1] for p in tight if p[2] in(1,2)),'five low positive-rank bins use32 and no fives or sevens')
    fives=[p for p in tight if p[1][1]];need(len(fives)==1 and fives[0][0]==32 and fives[0][1]==(0,1,0,0,3),'forced five bins')
    sixteen=[p for p in tight if p[0]==16 and p[1][2]];need(len(sixteen)==1 and sixteen[0][1]==(0,0,1,0,1),'only16 seven pattern')
    need(all(p[1][2]<=2 for p in tight if p[0]==32),'at most two sevens in32')
    need(all(not p[1][2] for p in tight if p[0] not in(16,32)),'no sevens elsewhere')
    free32=12992-8352-4-1;lo=14094-2*free32;hi=12992;need((lo,hi)==(4824,12992),'sharp necessary endpoints')
    # Independent coefficient ledger proves every quota/demand/profile identity symbolically.
    polynomial={}
    for cap,ws,coeff in ROWS:
        features={('cap',cap):1,('rank',cap-sum(ws)):1,('score',0):BONUS[cap]+sum(PRICE[w] for w in ws)}
        for w,n in Counter(ws).items():features['width',w]=n
        for key,n in features.items():polynomial[key]=tuple(a+n*b for a,b in zip(polynomial.get(key,(0,0,0)),coeff))
    targets={**{('cap',k):v for k,v in QUOTAS.items()},**{('width',k):v for k,v in DEMAND.items()},**{('rank',k):v for k,v in PROFILE.items()},('score',0):-112868}
    need(set(polynomial)==set(targets) and all(polynomial[k]==(v,0,0) for k,v in targets.items()),'symbolic invoice coefficients')
    digest=hashlib.sha256();cases=0
    for x in range(lo,hi+1):
        w=witness(x);invoice(w,upper);need(sum(n for cap,ws,n in w if cap==16 and ws==(9,7))==x,'projection');digest.update(json.dumps(w,separators=(',',':')).encode());cases+=1
    for x in(lo-1,hi+1,True):
        try:witness(x)
        except ValueError:pass
        else:raise ValueError('bad projection accepted')
    bad=witness(4825);cap,ws,n=bad[0];bad[0]=(cap,ws,n+1)
    try:invoice(bad,upper)
    except ValueError:pass
    else:raise ValueError('changed width invoice accepted')
    return {'status':'PASS_T29_CAPACITY_PROJECTION','range':[lo,hi],'all_integer_values_attained':cases,'patterns_enumerated':len(bins),'tight_patterns':len(tight),'all_witnesses_sha256':digest.hexdigest(),'samples':{str(x):witness(x) for x in(lo,lo+1,8001,hi-1,hi)},'symbolic_equalities':len(polynomial),'controls':4,'new_kappa':False}
if __name__=='__main__':
    result=json.loads(json.dumps(run()));p=H/'CERTIFICATE.json'
    if '--write' in sys.argv:p.write_text(json.dumps(result,indent=2)+'\n')
    else:need(result==json.loads(p.read_text()),'receipt')
    print(result['status'],'all8169 integers attained')
