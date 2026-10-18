#!/usr/bin/env python3
"""Exact X4 dyadic forest prices; prepared with OpenAI Codex, Apache-2.0."""
import gzip, hashlib, json, tarfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier799-audit/integrated799-replay.tar.gz'
MEMBER = 'native/local/CANONICAL-WORD.json.gz'
ARCHIVE_SHA = '70dfdfcf2ff95352c6020ee9dfca6dca9032b33c10daed3f3dc574c014f4e2cb'
WORD_SHA = '1c0e9da767d4418f70016af599e4a447a3f7777acabe930318459c0fbbd260aa'

def require(ok, message):
    if not ok: raise ValueError(message)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':')).encode()

def sha(x): return hashlib.sha256(x).hexdigest()

def cost(x):
    x=Q(x)
    if not x: return 0
    a,d=abs(x.numerator),x.denominator
    require(d & (d-1)==0, 'non-dyadic price')
    return 3+a.bit_length()-1+bin(a).count('1')+d.bit_length()-1

def load(archive_path=None):
    path=Path(archive_path) if archive_path else ROOT/ARCHIVE
    require(sha(path.read_bytes())==ARCHIVE_SHA,'archive hash')
    with tarfile.open(path,'r:gz') as archive:
        entries=[x for x in archive.getmembers() if x.name==MEMBER]
        require(len(entries)==1 and entries[0].isfile(),'ambiguous source member')
        payload=gzip.decompress(archive.extractfile(entries[0]).read())
    require(sha(payload)==WORD_SHA,'word hash')
    word=json.loads(payload)
    require((word['v'],word['R'],word['h'])==(112,504,9),'dimensions')
    rows={t:{} for t in range(112,224)}
    require(len(word['compensation'])==6320,'panel length')
    for op in word['compensation']:
        require(len(op)==6 and op[0]=='add' and all(type(v) is int for v in op[1:]),'typed scalar')
        _,t,s,n,d,frame=op
        require(t in rows and 224<=s<728 and frame==0,'panel shape')
        require(word['start'][t]==word['start'][s]==0,'panel frame')
        require(d>0 and d&(d-1)==0 and 4*n%d==0,'quarter grid')
        a=4*n//d
        require(0<abs(a)<=4 and s not in rows[t],'coefficient premise')
        rows[t][s]=a
    require(len(set().union(*(set(r) for r in rows.values())))==216,'helper support')
    return rows

def histograms(rows):
    groups={}
    for i in sorted(rows):
        for j in sorted(rows):
            if i==j: continue
            h=Counter((rows[i].get(s,0),rows[j].get(s,0)) for s in rows[i].keys()|rows[j].keys())
            key=tuple(sorted((a,b,n) for (a,b),n in h.items()))
            groups.setdefault(key,[]).append((i,j))
    return groups

def census(rows):
    groups=histograms(rows)
    alphabet=sorted({(a,b) for h in groups for a,b,_ in h})
    fallback={}
    for h in groups:
        fallback[h]=min(0,*(8+sum(n*(cost(Q(a-sign*b,4))-cost(Q(a,4))) for a,b,n in h) for sign in (-1,1)))
    records=[]
    for tick in range(-543,544):
        if not tick: continue
        q=Q(tick,8)
        table={(a,b):cost(Q(a,4)-q*Q(b,4))-cost(Q(a,4)) for a,b in alphabet}
        boundary=2*cost(q)
        minimum=10**9; maximum=-10**9; negative=zero=0; witness=None
        dominance_min=10**9; dominance_witness=None; dominance_negative=dominance_zero=0
        for h,pairs in groups.items():
            margin=boundary+sum(n*table[a,b] for a,b,n in h)
            if margin<minimum or (margin==minimum and pairs[0]<witness): minimum,witness=margin,pairs[0]
            difference=margin-fallback[h]
            if difference<dominance_min or (difference==dominance_min and pairs[0]<dominance_witness): dominance_min,dominance_witness=difference,pairs[0]
            dominance_negative+=len(pairs)*(difference<0); dominance_zero+=len(pairs)*(difference==0)
            maximum=max(maximum,margin)
            negative+=len(pairs)*(margin<0); zero+=len(pairs)*(margin==0)
        records.append({'numerator':q.numerator,'denominator':q.denominator,'min_margin':minimum,'max_margin':maximum,'negative_edges':negative,'zero_edges':zero,'witness':list(witness),'min_dominance_margin':dominance_min,'dominance_witness':list(dominance_witness),'strict_improvement_dominance':dominance_negative,'dominance_zero_edges':dominance_zero})
    return {'ordered_pairs':sum(map(len,groups.values())), 'histogram_classes':len(groups), 'coefficients':len(records),'cases':len(records)*sum(map(len,groups.values())), 'records':records}

def signed_unit_floor(rows):
    def rowprice(row):return sum(cost(Q(a,4)) for a in row.values())
    edges=[(rowprice(rows[i]),-1,i,0) for i in sorted(rows)]
    for i in sorted(rows):
        for j in sorted(rows):
            if j>=i:break
            for sign in (-1,1):
                w=8+sum(cost(Q(rows[i].get(s,0)-sign*rows[j].get(s,0),4)) for s in rows[i].keys()|rows[j].keys())
                edges.append((w,j,i,sign))
    parent={i:i for i in [-1,*rows]}
    def root(i):
        while parent[i]!=i: i=parent[i]
        return i
    selected=[]
    for w,i,j,s in sorted(edges):
        a,b=root(i),root(j)
        if a!=b:parent[a]=b;selected.append([w,i,j,s])
    require(len(selected)==112,'spanning tree')
    return {'cost':sum(e[0] for e in selected),'edges':selected,'graph_edges':len(edges)}
