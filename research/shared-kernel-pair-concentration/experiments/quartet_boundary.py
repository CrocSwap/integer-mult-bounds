#!/usr/bin/env python3
"""Independent exact fixed-suffix quartet test; no supplier admission claim.

Reads Philippe Van Velzen's PR2853 words at the pinned commit. Implements
only rational row propagation; imports none of the supplier/audit engines.
OpenAI Codex assisted research, 2026-10-16. Apache-2.0.
"""
import argparse
import collections
from fractions import Fraction as F
import gzip
import hashlib
import itertools
import json
from pathlib import Path

QUARTETS = [(460,461,468,469), (462,463,470,471),
            (478,479,490,491), (480,481,492,493)]

def rref(matrix):
    a = [[F(x) for x in row] for row in matrix]
    rank = 0
    pivots = []
    for col in range(len(a[0])):
        pivot = next((i for i in range(rank,len(a)) if a[i][col]),None)
        if pivot is None:
            continue
        a[rank],a[pivot] = a[pivot],a[rank]
        q=a[rank][col]
        a[rank]=[x/q for x in a[rank]]
        for i in range(len(a)):
            if i!=rank:
                q=a[i][col]
                a[i]=[x-q*y for x,y in zip(a[i],a[rank])]
        pivots.append(col)
        rank+=1
    null=[]
    for col in set(range(len(a[0])))-set(pivots):
        x=[F(0)]*len(a[0]);x[col]=F(1)
        for i,p in enumerate(pivots):x[p]=-a[i][col]
        assert all(sum(u*v for u,v in zip(row,x))==0 for row in matrix)
        null.append(x)
    return rank,pivots,null

def propagate(w):
    columns=list(itertools.chain.from_iterable(QUARTETS))
    rows=collections.defaultdict(dict)
    for c in columns: rows[c][(c,())]=F(1)
    warp_hits=0
    def add(dst,src,q):
        for k,v in list(src.items()):
            v=rows[dst].get(k,F(0))+q*v
            if v:rows[dst][k]=v
            else:rows[dst].pop(k,None)
    def append_word(old,ops):
        result=list(old)
        for op in ops:
            if result and result[-1]==-op:result.pop()
            else:result.append(op)
        return tuple(result)
    def event(e):
        nonlocal warp_hits
        if e[0]=='add':add(e[1],rows[e[2]],F(e[3],e[4]))
        elif e[0]=='scale':rows[e[1]]={k:v*F(e[2],e[3]) for k,v in rows[e[1]].items() if v*F(e[2],e[3])}
        elif e[0]=='warp':
            if rows[e[1]]:warp_hits+=1
            out={}
            for (c,word),v in rows[e[1]].items():
                k=(c,append_word(word,[e[2]]));out[k]=out.get(k,F(0))+v
            rows[e[1]]={k:v for k,v in out.items() if v}
        else:raise ValueError(('unknown event',e))
    for c in w['initial_corrections']:
        assert not rows[c['source']], 'extend independent correction algebra before using other source sets'
    for e in w['precondition']:event(e)
    # Remove precisely the compensation reading the quartet sources.
    for e in w['compensation']:
        if not(e[0]=='add' and e[2] in columns):event(e)
    for e in w['A']+w['cut']:event(e)
    warps=collections.defaultdict(list)
    for op,rec in enumerate(w['warps'],1):warps[rec[0]].append(['warp',rec[1],op])
    for i in range(len(w['B'])+1):
        for e in warps[i]:event(e)
        if i<len(w['B']):event(w['B'][i])
    for e in w['restore']:event(e)
    # Every operator-valued target coefficient gets its own matrix row.
    labels=sorted({(t,word) for t in range(112,224) for c,word in rows[t]})
    matrix=[[rows[t].get((c,word),F(0)) for c in columns] for t,word in labels]
    return columns,labels,matrix,warp_hits

def main():
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    result={'scope':'fixed suffix after an arbitrary invertible preprocessing confined to the four quartet registers; not arbitrary interleaved gates, new receivers, frames or a new supplier','orientations':{}}
    for kind in ['base','extra']:
        path=a.package/f'new/borrow/words/BORROW-WORD-43{kind}.json.gz'
        raw=path.read_bytes();w=json.loads(gzip.decompress(raw))
        columns,labels,matrix,hits=propagate(w)
        records=[]
        for q in QUARTETS:
            indices=[columns.index(c) for c in q]
            m=[[row[i] for i in indices] for row in matrix]
            rank,pivots,null=rref(m)
            active=[(label,row) for label,row in zip(labels,m) if any(row)]
            # Proof-relevant controls: rank and kernel respond to perturbations.
            assert rank==3 and len(null)==1
            assert all(v[0]==1 and all(x==0 for x in v[1:]) for v in null)
            altered=[row[:] for row in m]+[[F(1),F(0),F(0),F(0)]]
            assert rref(altered)[0]==4
            zeroed=[[F(0)]*4 for row in m]
            assert rref(zeroed)[0]==0
            records.append({'quartet':q,'rank':rank,'nullity':4-rank,'pivots':pivots,'nullspace':[[str(x) for x in v] for v in null],'nonzero_rows':[{'target':lab[0],'operator_word':lab[1],'coefficients':[str(x) for x in row]} for lab,row in active]})
        result['orientations'][kind]={'source_sha256':hashlib.sha256(raw).hexdigest(),'warp_hits':hits,'quartets':records,'controls':{'fill_null_column':True,'erase_matrix':True}}
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: eight exact rank-three quartet maps; fixed-suffix nullity one. No kappa improvement.')

if __name__=='__main__':main()
