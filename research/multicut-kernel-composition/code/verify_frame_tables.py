#!/usr/bin/env python3
"""Verify every added rational basis/annihilator table exactly.

The native containment checker consumes A, while the bank checker constructs
weighted charts from B. This checker binds both descriptions of each subspace.
"""
from array import array
from fractions import Fraction as Q
from pathlib import Path
import argparse, hashlib, json, sys

if not __debug__:raise SystemExit('assertions required')

def rank(rows,width=24):
    a=[list(map(Q,r)) for r in rows]
    assert all(len(r)==width for r in a)
    k=0
    for j in range(width):
        p=next((i for i in range(k,len(a)) if a[i][j]),None)
        if p is None:continue
        a[k],a[p]=a[p],a[k]
        scale=a[k][j];a[k]=[x/scale for x in a[k]]
        for i in range(k+1,len(a)):
            q=a[i][j]
            if q:a[i]=[x-q*y for x,y in zip(a[i],a[k])]
        k+=1
        if k==len(a):break
    return k

def verify(export,lead):
    export,lead=Path(export),Path(lead)
    original=json.loads((export/'frames.json').read_text())['frames']
    new_path=lead/'COHORT249-FRAMES.json'
    new=json.loads(new_path.read_text())
    assert not set(new)&set(original), 'new frame id collision'
    dimensions={}
    for key,frame in new.items():
        d=frame['dim'];B=frame['B'];A=frame['A']
        assert isinstance(d,int) and 0<=d<=24
        assert len(B)==d and len(A)==24-d, ('table lengths',key)
        assert rank(B)==d, ('B rank',key)
        assert rank(A)==24-d, ('A rank',key)
        assert all(sum(Q(x)*Q(y) for x,y in zip(a,b))==0 for a in A for b in B), ('A B transpose',key)
        gram=[[sum(Q(x)*Q(y) for x,y in zip(u,v))-sum(map(Q,u))*sum(map(Q,v))/9 for v in B] for u in B]
        assert rank(gram,d)==d, ('weighted Gram rank',key)
        dimensions[key]=d
    word=array('i');word.frombytes((lead/'COHORT249-RECORDS.bin').read_bytes())
    assert word.itemsize==4 and len(word)%6==0
    references=set()
    for j in range(len(word)//6):
        op,a,b,c,f,z=word[6*j:6*j+6]
        if op==0:references.update((str(b),str(c)))
        elif op==1:references.add(str(f))
        elif op in (2,3):references.update((str(c),str(f)))
        else:raise AssertionError('unknown opcode')
    assert references<=set(original)|set(new), 'unknown frame reference'
    return dict(status='PASS_EXACT_ADDED_FRAME_BASES_AND_ANNIHILATORS',
                frame_table_sha256=hashlib.sha256(new_path.read_bytes()).hexdigest(),
                added_frames=len(new),used_added_frames=len(references&set(new)),
                all_B_rank_equals_dimension=True,all_A_rank_equals_codimension=True,
                all_A_B_transpose_zero=True,all_weighted_Gram_nondegenerate=True,
                new_frame_ids_disjoint_from_original=True,
                dimensions=dimensions)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('export',type=Path);ap.add_argument('lead',type=Path)
    ap.add_argument('--output',type=Path)
    a=ap.parse_args();receipt=verify(a.export,a.lead)
    if a.output:
        assert not a.output.exists()
        a.output.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='dimensions'},sort_keys=True))

if __name__=='__main__':main()
