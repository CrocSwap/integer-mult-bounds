"""Independent binary-frame, selected-edge and complete paid-profile replay.

Copyright 2026 Rohan Arun. Apache-2.0. Prepared with OpenAI Codex assistance.
Uses the inherited PR104 carrier eligibility contract, independently reconstructed
from the complete PR108 producer binary rather than the matcher's edge export.
"""
import struct
from collections import Counter
from functools import lru_cache
from pathlib import Path

def require(condition, message):
    if not condition: raise ValueError(message)

def echelon(vectors):
    pivots={}
    for value in vectors:
        while value:
            p=value.bit_length()-1
            if p in pivots:value^=pivots[p]
            else:pivots[p]=value;break
    return tuple(pivots[p] for p in sorted(pivots,reverse=True))

def contains(basis, value):
    for pivot in basis:
        if value&(1<<(pivot.bit_length()-1)):value^=pivot
    return value==0

@lru_cache(None)
def frame(h,kind,core,cover,rank):
    coords=[i for i in range(h)if cover>>i&1]
    if kind==1:
        if core.bit_count()==3:
            require(core==cover and rank==1,'Singleton frame');basis=[core]
        else:
            require(core.bit_count()==2,'Shared-pair frame')
            basis=[core|(1<<i) for i in coords if not core>>i&1]
    elif kind==2:basis=[1<<i for i in coords]
    elif kind==3:
        require(core.bit_count()==1,'Center normal')
        a=core.bit_length()-1;other=[i for i in range(h)if i!=a]
        basis=[1<<a]+[(1<<other[0])|(1<<i)for i in other[1:]]
    else:raise ValueError('Frame type')
    require(len(basis)==rank and len(echelon(basis))==rank,'Frame rank')
    gram=[sum(((x&y).bit_count()%2)<<j for j,y in enumerate(basis))for x in basis]
    require(len(echelon(gram))==rank,'Nondegenerate frame')
    return echelon(basis)

def load(prefix):
    data=Path(str(prefix)+'.bin').read_bytes();offset=0
    def take(code,n):
        nonlocal offset
        fmt='<'+str(n)+code;values=struct.unpack_from(fmt,data,offset);offset+=struct.calcsize(fmt);return values
    h,v,n,q=take('I',4);flat=take('I',2*n);args=list(zip(flat[::2],flat[1::2]))
    core=take('Q',n);cover=take('Q',n);roots=take('I',q);kind=take('I',q);active=take('B',n)
    require(offset==len(data),'Binary trailing bytes')
    labels=Path(str(prefix)+'.labels').read_bytes();require(len(labels)==5*n,'Label length')
    ranks=struct.unpack_from('<'+str(n)+'I',labels);types=labels[4*n:]
    return dict(h=h,v=v,n=n,q=q,args=args,core=core,cover=cover,roots=roots,kind=kind,active=active,ranks=ranks,types=types)

def read_links(path):
    links=[]
    for line in Path(path).read_text().splitlines():
        fields=line.split();require(len(fields)==2,'Link syntax');links.append(tuple(map(int,fields)))
    return links

def replay(g,links):
    h,v,n,q=(g[k]for k in ('h','v','n','q'));args,core,cover,roots,kind,active,ranks,types=(g[k]for k in ('args','core','cover','roots','kind','active','ranks','types'))
    require((h,v)==(24,2024),'Selected dimension')
    frames={x:frame(h,types[x],core[x],cover[x],ranks[x]) for x in range(1,n)if active[x]}
    use_lists=[[] for _ in range(n)];c=0
    for x in frames:
        if args[x][0]:
            c+=1
            for side,y in enumerate(args[x]):
                require(y in frames and y<x,'Topological addition')
                require(all(contains(frames[x],b)for b in frames[y]),'Operand inclusion')
                use_lists[y].append(2*x+side)
    for j,x in enumerate(roots):
        require(x in frames,'Active root');use_lists[x].append((1<<31)|j)
    uses=[u for items in use_lists for u in items];hist=Counter();loss=0
    for x in frames:
        degree=len(use_lists[x]);require(degree>0,'Unused active node');r=ranks[x]
        if args[x][0]:
            hist[r]+=degree-1;hist[h-r]+=1
            for y in args[x]:hist[r-ranks[y]]+=1
        else:hist[1]+=degree
    for x,k in zip(roots,kind):
        r=ranks[x]
        if k:hist[r]+=1;hist[h]+=1;loss+=r
        else:hist[h-1-r]+=1;hist[1]+=1
    donors=set();targets=set()
    for x,j in links:
        require(0<x<n and 0<=j<len(uses),'Link range')
        require(x in frames and args[x][0]!=0,'Addition donor')
        require(x not in donors and j not in targets,'Matching uniqueness')
        e=uses[j];output=bool(e>>31);target=roots[e&0x7fffffff]if output else e//2
        value=target if output else args[target][e&1]
        require(value in args[x],'Shared operand')
        later=n+(e&0x7fffffff)if output else target
        require((ranks[x],x)<(ranks[target],later),'Strict carrier order')
        require(all(contains(frames[target],b)for b in frames[x]),'Exact carrier frame inclusion')
        ru,rv,rt=ranks[x],ranks[value],ranks[target]
        require(rt>=ru>=rv,'Carrier ranks')
        hist[h-ru]-=1;hist[rv]-=1;hist[rt-rv]-=1;hist[rt-ru]+=1
        donors.add(x);targets.add(j)
    require(all(r>=0 and count>=0 for r,count in hist.items()),'Nonnegative paid histogram')
    R=c+q-len(links);require(sum(r*count for r,count in hist.items())==h*R+2*loss,'Complete rank mass')
    return dict(h=h,v=v,c=c,q=q,R=R,loss=loss,matched=len(links),histogram=[hist[r]for r in range(h+1)])
