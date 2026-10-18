#!/usr/bin/env python3
"""Rebuild the finite premises without importing primary or predecessor code.

Direct Euclidean roots, rational flat closure, and full pairing-row elimination.
Hanson Sun, substantial OpenAI Codex assistance. Apache-2.0.
This and verify.py have the same AI-assisted author, not independent human review.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
COORDINATES = (2,4,5)


def check(ok, message):
    if not ok:
        raise ValueError(message)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',', ':')).encode()).hexdigest()


def reduce_binary(vectors):
    pivots={}
    for v in vectors:
        while v:
            bit=v & -v
            if bit in pivots:
                v ^= pivots[bit]
            else:
                pivots[bit]=v
                break
    return tuple(pivots[b] for b in sorted(pivots))


def dot(a,b):
    return sum(u*v for u,v in zip(a,b))


def rref(vectors):
    rows=[list(map(Fraction,v)) for v in vectors]
    used=0
    for col in range(3):
        pivot=next((i for i in range(used,len(rows)) if rows[i][col]),None)
        if pivot is None:
            continue
        rows[used],rows[pivot]=rows[pivot],rows[used]
        divisor=rows[used][col]
        rows[used]=[v/divisor for v in rows[used]]
        for i in range(len(rows)):
            if i!=used:
                scalar=rows[i][col]
                rows[i]=[v-scalar*w for v,w in zip(rows[i],rows[used])]
        used+=1
    return tuple(tuple(r) for r in rows[:used])


def geometry():
    all_roots=set()
    for i,j in combinations(range(8),2):
        for a,b in product((-2,2),repeat=2):
            r=[0]*8;r[i]=a;r[j]=b
            all_roots.add(tuple(r))
    all_roots.update(r for r in product((-1,1),repeat=8) if r.count(-1)%2==0)
    check(len(all_roots)==240,'240 doubled E8 roots')
    frame=[]
    for i in range(0,8,2):
        for s in (2,-2):
            r=[0]*8;r[i]=2;r[i+1]=s;frame.append(tuple(r))
    roots=sorted({max(r,tuple(-v for v in r)) for r in all_roots}-set(frame))
    check(len(roots)==112,'112 live lines')
    check(all(dot(r,r)==8 for r in roots),'root norms')
    check(all(dot(r,f)%4==0 for r in roots for f in frame),'integral coordinate entries')
    x=[[dot(r,f)//4 for f in frame] for r in roots]
    check(all(dot(r,s)%4==0 for r in roots for s in roots),'integral Gram entries')
    matrix=[[(1+dot(r,s)//4)%2 for s in roots] for r in roots]
    rows=[sum(value<<j for j,value in enumerate(row)) for row in matrix]
    check(len(set(rows))==112 and all(rows),'distinct nonzero pairing rows')
    check(len(reduce_binary(rows))==9,'nondegenerate label realization')
    check(all(dot(x[i],x[j])==dot(roots[i],roots[j])//2 for i in range(112) for j in range(112)),
          'coordinate decoder identity')
    return roots,x,matrix,rows


def enumerate_supports(x):
    projected=[tuple(r[k] for k in COORDINATES) for r in x]
    directions={rref([v]) for v in projected if any(v)}
    check(len(directions)==13,'13 projective directions')
    normals=[v[0] for v in sorted(directions)]
    flats={()};todo=[()]
    while todo:
        flat=todo.pop()
        for n in normals:
            candidate=rref([*flat,n])
            if len(candidate)<3 and candidate not in flats:
                flats.add(candidate);todo.append(candidate)
    check(Counter(map(len,flats))=={0:1,1:13,2:25},'complete rational flat closure')
    supports=set()
    for flat in flats:
        outside=[i for i,v in enumerate(projected) if len(rref([*flat,v]))>len(flat)]
        supports.add(sum(1<<i for i in outside))
    check(len(supports)==39,'distinct supports of proper flats')
    return supports,projected


def check_receipt(cert):
    roots,x,matrix,rows=geometry()
    check(cert['triple']==list(COORDINATES),'triple identity')
    check(cert['geometry']=={'ports':112,'label_rank':9,'roots_sha256':fingerprint(roots),
                             'coordinates_sha256':fingerprint(x),'pairing_sha256':fingerprint(matrix)},
          'geometry receipt binding')
    complete,projected=enumerate_supports(x)
    saved=cert['strata']
    supports=[int(s['support_hex'],16) for s in saved]
    check(len(saved)==len(set(supports))==39 and set(supports)==complete,'support coverage')
    code={0}
    for row in reduce_binary(rows): code |= {v^row for v in list(code)}
    check(len(code)==512,'complete dual code')
    singleton_cases=0;pair_counts=Counter();slice_counts=Counter();orig_counts=Counter();distances=Counter()
    for record,support in zip(saved,supports):
        actual=sum(1<<i for i,v in enumerate(projected) if dot(v,record['coefficient']))
        check(actual==support,'coefficient-to-support binding')
        members=[i for i in range(112) if support>>i&1]
        full=reduce_binary(rows[i] for i in members)
        weights=Counter((support&c).bit_count() for c in code)
        distance=min(w for w in weights if w);distances[distance]+=1
        check(distance>=12 and record['minimum_erasure']==distance,'erasure minimum')
        check(record['erasure_spectrum']=={str(k):v for k,v in weights.items()},'erasure spectrum')
        check(record['span']==len(full),'support span')
        original=[len(reduce_binary(r&t for r in full)) for t in supports]
        check(min(original)>=8,'original pairing minimum')
        check(record['original_pair_ranks']==''.join(map(str,original)),'original pairing table')
        orig_counts.update(original)
        dimensions=[];table=[]
        for j in range(112):
            # Direct deletion check: equal dimensions of nested spans prove equality.
            check(len(reduce_binary(rows[i] for i in members if i!=j))==len(full),'singleton erasure')
            singleton_cases+=1
            surviving=reduce_binary(rows[i] for i in members if matrix[i][j])
            dimensions.append(len(surviving));slice_counts[len(surviving)]+=1
            values=[len(reduce_binary(r&t for r in surviving)) for t in supports]
            check(min(values)>=7,'one-anchor pairing minimum')
            pair_counts.update(values);table.append(''.join(map(str,values)))
        check(record['survivor_dimensions']==''.join(map(str,dimensions)),'survivor dimensions')
        check(record['survivor_pair_ranks']==table,'full survivor pairing table')
    summary=cert['summary']
    for key,counts in [('erasure_distance_counts',distances),('original_pair_counts',orig_counts),
                       ('survivor_dimension_counts',slice_counts),('survivor_pair_counts',pair_counts)]:
        check(summary[key]=={str(k):v for k,v in counts.items()},'aggregate '+key)
    check(summary['survivor_pair_cases']==sum(pair_counts.values())==170352,'pairing case count')
    check(summary['minimum_erasure']==min(distances)==12,'distance summary')
    check(summary['minimum_survivor_pair_rank']==min(pair_counts)==7,'pair minimum summary')
    check(summary['sharp_whole_copy_sum']==64,'claimed floor')
    targets=set();lookup={max(tuple(r),tuple(-v for v in r)):i for i,r in enumerate(x)}
    for transport in cert['transports']:
        p=transport['permutation']
        check(sorted(p)==list(range(8)),'coordinate permutation')
        target=tuple(sorted(p[k] for k in COORDINATES))
        check(list(target)==transport['target'] and target not in targets,'triple transport uniqueness')
        targets.add(target);indices=[];signs=[]
        for r in x:
            image=[r[p.index(k)] for k in range(8)]
            normalized=max(tuple(image),tuple(-v for v in image))
            check(normalized in lookup,'transport root image')
            i=lookup[normalized];indices.append(i);signs.append(1 if image==x[i] else -1)
        check(len(set(indices))==112,'transport line bijection')
        check(all(matrix[i][j]==matrix[indices[i]][indices[j]] for i in range(112) for j in range(112)),
              'transport preserves pairing')
        check(transport['signed_map_sha256']==fingerprint([indices,signs]),'transport digest')
    check(targets==set(combinations(range(8),3)),'all 56 coordinate triples')
    # Separate integer derivation of the decisive cancellation/compensation example.
    y=[[r[k] for k in COORDINATES] for r in x]
    u=[r[0] if matrix[i][0]==0 else 0 for i,r in enumerate(y)]
    d=[[r[0]-u[i],r[1],r[2],u[i]] for i,r in enumerate(y)]
    t=[[r[0],r[1],r[2],r[0]+(i==0)] for i,r in enumerate(y)]
    check(all(dot(d[i],t[j])==dot(y[i],y[j])+u[i]*(j==0) for i in range(112) for j in range(112)),
          'independent compensation identity')
    costs=[]
    for k in range(4):
        target_mask=sum(1<<i for i in range(112) if t[i][k])
        costs.append(len(reduce_binary(rows[i]&target_mask for i in range(112) if d[i][k])))
    check(costs==[7,8,8,7],'independent compensation costs')
    check(any(matrix[i][j] and dot(d[i][:3],t[j][:3])!=dot(y[i],y[j])
              for i in range(112) for j in range(112)),'compensation omission control')
    check(sum(1 for r in costs if r>=8)==2,'stronger per-child assertion is false')
    # The bilinear rank oracle must distinguish a rank-one full block from two rows.
    check(len(reduce_binary([3,3]))==1 and len(reduce_binary([1,2]))==2,'binary rank controls')
    print('PASS_INDEPENDENT_SINGLETON_THREE_MODE pairings=170352 singleton_erasures='+str(singleton_cases)
          +' transports=56 compensation_entries=12544')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate',type=Path,default=HERE/'CERTIFICATE.json')
    args=parser.parse_args()
    check_receipt(json.loads(args.certificate.read_text()))


if __name__=='__main__': main()
