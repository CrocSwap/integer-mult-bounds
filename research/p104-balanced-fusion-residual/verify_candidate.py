#!/usr/bin/env python3
"""Independent 630-row, transpose, history and clear audit of the fused word."""
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json

SOURCE=Path(__file__).resolve().parent / 'pinned/strong-bit.json.gz'
CHANGED=Path(__file__).resolve().parent / 'pinned/ONE-RESIDUAL.json.gz'
A='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
B='7fa5589301124788237a569c3c0bbc0783f70efd840b15238300b8a2d5ab1cd7'

def load(path,digest):
    b=path.read_bytes();assert sha256(b).hexdigest()==digest
    return json.loads(gzip.decompress(b))

def basis(rows):
    piv={}
    for v in rows:
        while v:
            p=v&-v
            if p not in piv:piv[p]=v;break
            v^=piv[p]
    return piv

def contains(piv,v):
    while v:
        p=v&-v
        if p not in piv:return False
        v^=piv[p]
    return True

def separating_input(stock,target):
    # Direct row reduction of the system stock*x=0, target*x=1.
    piv={}
    for row,rhs in [(r,0) for r in stock]+[(target,1)]:
        while row:
            p=row&-row
            if p not in piv:piv[p]=(row,rhs);break
            r,b=piv[p];row^=r;rhs^=b
        else:assert rhs==0
    x=0
    for p in sorted(piv,reverse=True):
        row,rhs=piv[p]
        if rhs^((row&x).bit_count()&1):x|=p
    assert all((r&x).bit_count()%2==0 for r in stock) and (target&x).bit_count()%2==1
    return x

def forward(g,omit_last=False):
    n=g['public'];at=dict(enumerate(g['start']));v={i:1<<i for i in at};history=defaultdict(list);clears={};moves=[]
    for i,c in at.items():history[c].append(v[i])
    for t,row in enumerate(g['program']):
        if omit_last and t==len(g['program'])-1:continue
        op,i,*a=row
        if op=='INIT':assert i not in at and i>=n;at[i]=a[0];v[i]=0
        elif op=='ADD':j,c=a;assert i!=j and at[i]==at[j]==c;v[i]^=v[j]
        elif op=='MOVE':s,c=a;assert at[i]==s;at[i]=c;history[c].append(v[i]);moves.append((i,s,c))
        elif op=='SWAP':j,=a;at[i],at[j]=at[j],at[i];v[i],v[j]=v[j],v[i]
        elif op=='CLEAR':assert i>=n and at.pop(i)==a[0] and i not in clears;clears[i]=(a[0],v.pop(i))
        else:raise AssertionError(op)
    assert at==dict(enumerate(g['final']))
    return [v[i] for i in range(n)],clears,history,moves

def reverse(g):
    n=g['public'];at=dict(enumerate(g['final']));v={i:1<<i for i in at}
    for op,i,*a in reversed(g['program']):
        if op=='CLEAR':assert i not in at;at[i]=a[0];v[i]=0
        elif op=='INIT':assert at.pop(i)==a[0];v.pop(i)
        elif op=='ADD':j,c=a;assert at[i]==at[j]==c;v[j]^=v[i]
        elif op=='MOVE':s,t=a;assert at[i]==t;at[i]=s
        elif op=='SWAP':j,=a;at[i],at[j]=at[j],at[i];v[i],v[j]=v[j],v[i]
        else:raise AssertionError(op)
    assert at==dict(enumerate(g['start']))
    return [v[i] for i in range(n)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('native',nargs='?',type=Path,default=SOURCE);ap.add_argument('changed',nargs='?',type=Path,default=CHANGED);args=ap.parse_args()
    g=load(args.native,A);h=load(args.changed,B);assert set(g)==set(h) and all(g[k]==h[k] for k in g if k!='program')
    native,old,ns,nm=forward(g);changed,new,cs,cm=forward(h)
    target=[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(630)]
    assert native==target
    wrong=[i for i in range(630) if changed[i]!=target[i]]
    assert wrong==[130] and changed[130]^target[130]==1<<38
    assert len(basis(changed))==630
    transpose=[sum(((changed[j]>>i)&1)<<j for j in range(630)) for i in range(630)]
    assert reverse(h)==transpose
    assert list(old)==list(new) and all(old[i][0]==new[i][0] for i in old)
    changed_clears=[i for i in old if old[i]!=new[i]]
    assert changed_clears==[2241,2242,2252,2477,2898,3317,3318] and all(x[1] for x in new.values())
    assert nm.count((2241,0,509))==1 and nm.count((2252,509,1))==1 and cm.count((2252,0,1))==1
    expect=[x for x in nm if x not in ((2241,0,509),(2252,509,1))];expect.insert(nm.index((2252,509,1))-1,(2252,0,1));assert cm==expect
    stock=cs[544];assert not contains(basis(stock),target[130]);w=separating_input(stock,target[130])
    damaged,_,_,_=forward(h,True);bad=[i for i in range(630) if damaged[i]!=changed[i]];assert bad
    print(json.dumps({'source_sha256':A,'candidate_sha256':B,'forward_target_rows_correct':629,
       'only_wrong_output':130,'error_input_coordinate':38,'candidate_operator_rank':len(basis(changed)),
       'transpose_matches_independently_reconstructed':True,'native_clear_count':len(old),'candidate_clear_count':len(new),
       'changed_clear_owners':changed_clears,'all_candidate_clears_nonzero':True,
       'all_other_ordered_move_incidences_unchanged':True,'chart544_history_rank':len(basis(stock)),
       'chart544_target_not_in_history_span':True,'chart544_separating_input_support':[i for i in range(630) if w>>i&1],
       'last_add_corruption_changes_outputs':bad},indent=2,sort_keys=True))

if __name__=='__main__':main()
