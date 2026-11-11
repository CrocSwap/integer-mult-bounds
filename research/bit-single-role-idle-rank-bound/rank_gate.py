"""Whole-stock rank obstruction to a single relocated BIT idle."""
from collections import Counter
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from time import monotonic

HERE=Path(__file__).resolve().parent
PIN='757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b'


def residue(a,b):
    d=b.bit_length()-1
    while a and a.bit_length()-1>=d:
        a ^= b << (a.bit_length()-1-d)
    return a


def multiply(a,b):
    z=0
    while b:
        if b&1:
            z^=a
        a<<=1
        b>>=1
    return residue(z,0x11b)


def run():
    deadline=monotonic()+18
    assert all(residue(0x11b,b) for b in range(2,32))
    products=[bytes(multiply(a,b) for b in range(256)) for a in range(256)]
    raw=(HERE/'EFREE-CALLER.json.gz').read_bytes()
    assert sha256(raw).hexdigest()==PIN
    word=json.loads(gzip.decompress(raw))
    n=word['roles']
    def xor(row,other):
        return bytes(a^b for a,b in zip(row,other,strict=True))
    def forward(values,omit):
        rows=[bytes(i==j for j in range(n)) for i in range(n)]
        for t,(op,*args) in enumerate(word['events']):
            if t in omit:
                continue
            if op=='ADD' or op=='QUERY':
                d,s=args
                rows[d]=xor(rows[d],rows[s])
            elif op=='SWAP':
                d,s=args
                rows[d],rows[s]=rows[s],rows[d]
            elif op=='LOCAL':
                stage,s,d=args
                rows[d]=xor(rows[d],rows[s])
                row=products[values[stage-1]]
                rows[s]=bytes(map(row.__getitem__,rows[s]))
                rows[d]=bytes(map(row.__getitem__,rows[d]))
            elif op=='IDLE_ONE':
                d,stages=args
                scale=1
                for s in stages:
                    scale=products[scale][values[s-1]]
                rows[d]=bytes(map(products[scale].__getitem__,rows[d]))
            else:
                raise ValueError(op)
        return rows
    def rank_two(rows):
        pivot=next((r for r in rows if any(r)),None)
        if pivot is None:
            return 0
        i=next(i for i,v in enumerate(pivot) if v)
        for r in rows:
            if any(products[pivot[i]][v]!=products[r[i]][u] for u,v in zip(pivot,r,strict=True)):
                return 2
        return 1
    assert rank_two([b'\x01\x00',b'\x00\x01'])==2
    assert rank_two([b'\x01\x00',b'\x03\x00'])==1
    assert rank_two([bytes(2),bytes(2)])==0
    probe=tuple(range(2,20))
    orig=forward(probe,set())
    for i,d in enumerate(word['diagonal']):
        scale=1
        for stage in d['stages']:
            scale=products[scale][probe[stage-1]]
        assert orig[i]==bytes(scale if i==j else 0 for j in range(n))
    idles={t:set(e[2]) for t,e in enumerate(word['events']) if e[0]=='IDLE_ONE'}
    pairs=[(i,j) for i,j in combinations(idles,2) if not idles[i]&idles[j]]
    assert len(pairs)==256
    counts=Counter()
    unresolved=[]
    for i,j in pairs:
        if monotonic()>=deadline:
            break
        changed=forward(probe,{i,j})
        rk=rank_two([xor(a,b) for a,b in zip(orig,changed,strict=True)])
        counts[rk]+=1
        if rk<2:
            unresolved.append([i,j,rk])
    return {'caller_sha256':PIN,'field_polynomial':hex(0x11b),'q':1,
            'stage_probe':probe,'disjoint_scope':len(pairs),'rank_counts':dict(counts),
            'unresolved':unresolved,'unvisited':len(pairs)-sum(counts.values()),
            'physical_sites':0}


if __name__=='__main__':
    print(json.dumps(run(),sort_keys=True,indent=2))
