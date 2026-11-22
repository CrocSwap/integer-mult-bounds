#!/usr/bin/env python3
"""Independent low-pivot audit of the fixed hinge/late-sender linear screen."""
from collections import Counter,defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip,json

SOURCE=Path(__file__).resolve().parent / 'pinned/strong-bit.json.gz'
SHA='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
L=(1<<630)-1

def insert(b,v):
    while v:
        p=v&-v
        if p not in b:b[p]=v;return
        v^=b[p]

def bas(rows):
    b={}
    for v in rows:insert(b,v)
    return b

def rem(b,v):
    for p in sorted(b):
        if v&p:v^=b[p]
    return v

def span(rows):
    out={0}
    for r in rows:out|={x^r for x in out}
    return out

def invertible(rows):
    M=[[Fraction(v) for v in row] for row in rows]
    for j in range(8):
        p=next(i for i in range(j,8) if M[i][j])
        M[p],M[j]=M[j],M[p]
        for i in range(j+1,8):
            q=M[i][j]/M[j][j];M[i]=[a-q*b for a,b in zip(M[i],M[j])]
    return True

def main():
    raw=SOURCE.read_bytes();assert sha256(raw).hexdigest()==SHA;g=json.loads(gzip.decompress(raw));p=g['program'];D={int(i):s['dim'] for i,s in g['frames'].items()}
    up4=[(t,r[1],r[2],r[3]) for t,r in enumerate(p) if r[0]=='MOVE' and D[r[3]]-D[r[2]]==4]
    pair=[(a,b) for a in up4 for b in up4 if a[0]<b[0] and a[3]==b[2]]
    assert pair==[((7112,2241,0,509),(7210,2252,509,1))]
    at=dict(enumerate(g['start']));v={i:1<<i for i in at};stock=defaultdict(list)
    for i,c in at.items():stock[c].append(v[i])
    patch={7110:['INIT',2241,509],7111:None,7112:None,
           7208:['INIT',2252,0],7209:['ADD',2252,626,0],7210:['MOVE',2252,0,1],21250:None}
    for t,row in enumerate(p):
        if t==7110:hinge=stock[509][:]
        if t==7122:v[2242]^=1<<630
        if t==21256:pre={c:tuple(rows) for c,rows in stock.items()}
        row=patch.get(t,row)
        if row is None:continue
        op,i,*a=row
        if op=='INIT':assert i not in at;at[i]=a[0];v[i]=0
        elif op=='ADD':j,c=a;assert at[i]==at[j]==c;v[i]^=v[j]
        elif op=='MOVE':
            s,d=a;assert at[i]==s;at[i]=d
            if t==21260:v[i]=1<<631
            stock[d].append(v[i])
        elif op=='SWAP':j,=a;at[i],at[j]=at[j],at[i];v[i],v[j]=v[j],v[i]
        elif op=='CLEAR':assert at.pop(i)==a[0];v.pop(i)
        else:raise AssertionError(op)
    assert at==dict(enumerate(g['final']))
    assert len(hinge)==len(bas(hinge))==12
    target=[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(630)]
    w=bas(target[i] for i,c in enumerate(g['final']) if c==1)
    top=bas(x&L for x in stock[1]);assert len(w)==505 and len(top)==504
    assert all(rem(w,x)==0 for x in top.values())
    tagged=bas(stock[1]);assert len(tagged)==505 and rem(tagged,1<<630)==0
    assert all(not (x>>631) for x in stock[1])
    gs=span(hinge);assert len(gs)==4096
    valid=[r for r in gs if rem(w,r)==0 and rem(top,r)!=0];assert len(valid)==512
    early=[x for x in stock[544] if not x>>631&1];assert len(early)==3 and stock[544][-1]==1<<631
    early_codes=span(early);assert len(early_codes)==8
    zero=bas(pre[0]);lines=[c for c,d in D.items() if d==1]
    assert len(lines)==111 and all(not any(r>>630 for r in pre.get(c,())) for c in [0]+lines)
    possible={c:span(rem(zero,r) for r in pre.get(c,())) for c in lines}
    hit=Counter();without_late=0
    for h in valid:
        for x in early_codes:
            need=target[130]^(x&L)^(h if x>>630&1 else 0)
            if not need:without_late+=1
            q=rem(zero,need)
            for c in lines:
                if q in possible[c]:hit[c]+=1
    assert without_late==0 and hit=={21:512}
    assert g['start'][19]==21 and g['final'][130]==544
    # The rank-one image of 21 adds an eighth dimension to 544's rank-seven
    # image. Thus 21 is not a subspace of 544, a necessary condition for a
    # legal 1->7 nested transfer; no projector-gauge convention can change it.
    assert invertible(g['frames']['544']['B']+g['frames']['21']['B'])
    print(json.dumps({'source_sha256':SHA,'unique_ordered_4_plus_4_pair':pair[0],
      'hinge_history_rank':len(bas(hinge)),'linear_hinge_codes':len(gs),
      'complete_top_codes':len(valid),'rank1_late_senders':len(lines),
      'possible_sender_and_counts':dict(hit),'successful_nested_senders':0,
      'chart21_image_not_in_chart544_image':True,'codes_requiring_no_new_late_receipt':without_late,
      'scope':'fixed remaining native operations; one linear 2242 hinge; one linear 0->c->544 late rebind; full native preclock histories granted'},sort_keys=True,indent=2))

if __name__=='__main__':main()
