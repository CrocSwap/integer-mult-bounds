"""Exact two/three omission exclusion via transported transvections. Apache-2.0."""
import gzip,hashlib,itertools,json,math,sys
from pathlib import Path
from collections import defaultdict
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
def need(x,m):
    if not x:raise ValueError(m)
def replay(gates,n,omit=()):
    r=[1<<i for i in range(n)];omit=set(omit)
    for i,(d,s) in enumerate(gates):
        if i not in omit:r[d]^=r[s]
    return r
def row_action(v,rows):
    out=0
    while v:
        bit=v&-v;out^=rows[bit.bit_length()-1];v^=bit
    return out
def triple_relations(factors):
    groups=[defaultdict(dict),defaultdict(dict)]
    for i,(u,v) in enumerate(factors):
        need(v not in groups[0][u],'duplicate transvection')
        groups[0][u][v]=i;groups[1][v][u]=i
    result=set();checks=0
    for gs in groups:
        for d in gs.values():
            for (a,i),(b,j) in itertools.combinations(d.items(),2):
                checks+=1;k=d.get(a^b)
                if k is not None:result.add(tuple(sorted((i,j,k))))
    return sorted(result),checks
def trows(u,v,n):return [(1<<i)^(v if u>>i&1 else 0) for i in range(n)]
def compose(a,b):return [row_action(r,b) for r in a]
def rank(rows):
    b={}
    for x in rows:
        while x:
            k=x.bit_length()-1
            if k in b:x^=b[k]
            else:b[k]=x;break
    return len(b)
def run():
    for f in json.loads((H/'SOURCES.json').read_text())['files']:
        if f['usage']=='input':need(hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'],'source')
    w=json.loads(gzip.decompress((ROOT/'research/r439-helper-stars-seed19/candidate.json.gz').read_bytes()))
    n=2*w['v']+w['R'];need(n==661,'columns');g=[(d,s) for f,d,ss in w['D'] for s in ss];need(len(g)==5563,'gate domain')
    r=[1<<i for i in range(n)];incoming=[]
    for d,s in g:incoming.append(r[s]);r[d]^=r[s]
    baseline=r;inv=replay(g[::-1],n);need(compose(baseline,inv)==[1<<i for i in range(n)],'inverse')
    col=[1<<i for i in range(n)];out=[0]*len(g)
    for i in range(len(g)-1,-1,-1):d,s=g[i];out[i]=col[d];col[s]^=col[d]
    factors=[(u,row_action(v,inv)) for u,v in zip(out,incoming)]
    for i,(u,v) in enumerate(factors):need(u and v and not((u&v).bit_count()%2),'nontrivial involution')
    need(len(set(factors))==len(g),'all transported transvections distinct')
    triples,work=triple_relations(factors);need(not triples,'three-deletion circuit improvement found')
    raw_triples,raw_work=triple_relations(list(zip(out,incoming)));need(raw_triples==triples and raw_work==work,'invertible covector transport preserves census')
    # Independently replay every literal single omission, corroborating every factor.
    for i,(u,v) in enumerate(zip(out,incoming)):
        mutant=replay(g,n,(i,));need(all((a^b)==(v if u>>j&1 else 0) for j,(a,b) in enumerate(zip(baseline,mutant))),'literal factor '+str(i))
    # Different engine: all ordered distinct 3D transvection pairs and dense rank of product-I.
    ts=[(u,v) for u in range(1,8) for v in range(1,8) if not((u&v).bit_count()%2)];count=0
    for a,b in itertools.permutations(ts,2):
        product=compose(trows(*a,3),trows(*b,3));rr=rank([x^(1<<i) for i,x in enumerate(product)])
        need((rr==1)==(a[0]==b[0] or a[1]==b[1]),'rank-one product classification');count+=1
    planted=[(1,2),(1,4),(1,6)];need(triple_relations(planted)[0]==[(0,1,2)],'planted neutral triple')
    product=[1<<i for i in range(3)]
    for a in planted:product=compose(trows(*a,3),product)
    need(product==[1,2,4],'planted literal cancellation')
    try:triple_relations([(1,2),(1,2)])
    except ValueError:pass
    else:raise ValueError('duplicate-pair control')
    # Full literal multi-omission witnesses are corroboration, not exhaustive pair/triple enumeration.
    selected=[(0,1),(220,221),(526,5036),(5341,5562),(0,221,5036),(220,527,5342),(100,2000,5500)]
    for omission in selected:need(replay(g,n,omission)!=baseline,'literal multiple-omission control')
    digest=hashlib.sha256(json.dumps([[str(u),str(v)] for u,v in factors],separators=(',',':')).encode()).hexdigest()
    return dict(status='PASS_THREE_OMISSION_EXCLUSION',gates=len(g),columns=n,pairs_covered=math.comb(len(g),2),triples_covered=math.comb(len(g),3),neutral_pairs=0,neutral_triples=0,group_pair_checks=work,factor_sha256=digest,literal_single_replays=len(g),independent_small_pairs=count,planted_controls=2,literal_multi_controls=len(selected),new_kappa=False)
if __name__=='__main__':
    x=run();p=H/'CERTIFICATE.json'
    if '--write' in sys.argv:p.write_text(json.dumps(x,indent=2)+'\n')
    else:need(x==json.loads(p.read_text()),'receipt')
    print(x['status'],json.dumps(x,sort_keys=True))
