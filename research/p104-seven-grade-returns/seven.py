"""All nine native feedback paths, replaced by one sink-to-line MOVE and local decoding."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import gzip,json,sys
from pathlib import Path


def rank(vecs):
    b={}
    for v in vecs:
        while v:
            p=v.bit_length()
            if p not in b:b[p]=v;break
            v^=b[p]
    return len(b)


def source(path):
    raw=Path(path).read_bytes();assert sha256(raw).hexdigest()=='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326';j=gzip.decompress(raw);assert sha256(j).hexdigest()=='b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69';return json.loads(j)


def run(g):
    n=g['public'];D={int(j):s['dim'] for j,s in g['frames'].items()};P=g['program'];L=(1<<n)-1;M=[(k,r) for k,r in enumerate(P) if r[0]=='MOVE'];top=min(k for k,r in M if r[3]==1);assert top==6908
    ds=[k for k,r in M if D[r[2]]>D[r[3]]];fids=ds[2::3];assert len(fids)==9 and all(P[k][3]==0 for k in fids)
    sites=sorted(c for c,d in D.items() if d==1);out={c:[k for k,r in M if k>=top and r[2]==c] for c in sites};assert len(sites)==111 and max(map(len,out.values()))==1 and all(D[c]!=1 for c in g['final'])
    ids=list(sorted(set(fids)|set(k for slots in out.values() for k in slots)));idx={k:i for i,k in enumerate(ids)};ch=dict(enumerate(g['start']));v={j:1<<j for j in ch};stock=defaultdict(list);p0={};fv={}
    for j,c in ch.items():stock[c].append(v[j])
    for k,r in enumerate(P):
        op,d,*a=r
        if op=='MOVE':
            assert ch[d]==a[0]
            if k in fids:p0[k]=list(stock[0]);fv[k]=v[d]
            if k in idx:v[d]^=1<<(n+idx[k]);
            ch[d]=a[1];stock[a[1]].append(v[d]);
        elif op=='ADD':s,c=a;assert ch[d]==ch[s]==c;v[d]^=v[s]
        elif op=='INIT':assert d not in ch;ch[d],v[d]=a[0],0
        elif op=='CLEAR':assert ch.pop(d)==a[0];del v[d]
        elif op=='SWAP':s,=a;ch[d],ch[s]=ch[s],ch[d];v[d],v[s]=v[s],v[d]
        else:raise ValueError(op)
    assert ch==dict(enumerate(g['final'])) and [v[i]&L for i in range(n)]==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(n)]
    chart_fields={c:[x&L for x in vecs] for c,vecs in stock.items()};reach={k:{c for c,vs in stock.items() if any(x>>(n+idx[k])&1 for x in vs)} for k in ids};odd={k:{ch[i] for i,x in v.items() if x>>(n+idx[k])&1} for k in ids}
    def witnesses(first,other):
        cs=sorted(odd[first]-(reach[other] if other is not None else set()),key=lambda c:(len(chart_fields[c]),c))
        for a,b in combinations(cs,2):
            tot=len(chart_fields[a])+len(chart_fields[b])
            if rank(chart_fields[a]+chart_fields[b])==tot:return [a,b]
        return None
    records=[];passed=Counter()
    for f in fids:
        base=[(s&L)^((fv[f]&L) if s>>(n+idx[f])&1 else 0) for s in stock[0]];assert rank(base+[fv[f]&L])==rank(base)+1
        for c in sites:
            o=next((k for k in out[c] if k!=f),None)
            pair=witnesses(f,o);inroot=o is not None and any(x>>(n+idx[o])&1 for x in p0[f]);inold=o is not None and bool(fv[f]>>(n+idx[o])&1);ever=o is not None and 0 in reach[o];sensitive=ever or inold;second=witnesses(o,f) if sensitive else None
            status='excluded' if pair and (not sensitive or second) else 'open';passed[status]+=1
            records.append({'original_completed_return':f,'receiver_chart':c,'surviving_departure':o,'two_immune_witnesses_for_root':pair,'alternate_noise_reaches_root_preclock':inroot,'alternate_noise_reaches_missing_native_field':inold,'alternate_noise_ever_reaches_zero':ever,'two_immune_witnesses_for_departure':second,'status':status})
    assert len(records)==999 and passed=={'excluded':999}
    assert sum(r['alternate_noise_ever_reaches_zero'] for r in records)==64 and sum(r['alternate_noise_reaches_root_preclock'] for r in records)==28 and not any(r['alternate_noise_reaches_missing_native_field'] for r in records)
    return {'root_first_informative_arrival_clock':top,'rank1_charts':len(sites),'departures_after_top_awakens':dict(Counter(len(x) for x in out.values())),'late_outgoing_dimensions':dict(Counter(D[P[x[0]][3]] for x in out.values() if x)),'candidates':len(records),'verdict':dict(passed),'classifications':records}

if __name__=='__main__':
    print(json.dumps(run(source(sys.argv[1])),indent=2,sort_keys=True))
