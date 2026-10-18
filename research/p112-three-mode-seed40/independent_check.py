#!/usr/bin/env python3
"""Code-disjoint finite-premise check: Euclidean roots, rational flats, erasures.

No primary/predecessor code imports; proposed transport/certificate witnesses
are data and are checked. Same AI-assisted author, not independent human review.
Hanson Sun (@bbMisk), substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
TRIPLE=(2,4,5)


def check(ok, message):
    if not ok: raise ValueError(message)


def rank_sets(rows, ceiling=None):
    pivots={}
    for original in rows:
        row=set(original)
        while row:
            first=min(row)
            if first not in pivots:
                pivots[first]=row
                if ceiling is not None and len(pivots)==ceiling: return len(pivots)
                break
            row.symmetric_difference_update(pivots[first])
    return len(pivots)


def echelon(rows):
    a=[list(map(Fraction,row)) for row in rows if any(row)]
    cursor=0
    for j in range(3):
        found=next((i for i in range(cursor,len(a)) if a[i][j]),None)
        if found is None: continue
        a[cursor],a[found]=a[found],a[cursor]
        value=a[cursor][j];a[cursor]=[v/value for v in a[cursor]]
        for i in range(len(a)):
            if i!=cursor:
                value=a[i][j];a[i]=[v-value*w for v,w in zip(a[i],a[cursor])]
        cursor+=1
    return tuple(tuple(row) for row in a[:cursor])


def build():
    roots=set()
    for i,j in combinations(range(8),2):
        for sign in (-1,1):
            row=[0]*8;row[i]=2;row[j]=2*sign;roots.add(tuple(row))
    for signs in product((-1,1),repeat=7):
        if sum(v==-1 for v in signs)%2==0: roots.add((1,)+signs)
    frame=[]
    for j in range(4):
        for sign in (1,-1):
            row=[0]*8;row[2*j]=2;row[2*j+1]=2*sign;frame.append(tuple(row))
    check(len(roots)==120 and set(frame)<=roots,'root/frame enumeration')
    roots=sorted(roots-set(frame))
    x=[[sum(a*b for a,b in zip(row,f))//4 for f in frame] for row in roots]
    gram=[[sum(a*b for a,b in zip(r,s))//4 for s in roots] for r in roots]
    b=[{j for j,g in enumerate(row) if (g+1)%2} for row in gram]
    check(len(roots)==112 and all(sum(v*v for v in row)==8 for row in roots),'root norms')
    check(all(sum(a*c for a,c in zip(x[i],x[j]))==2*gram[i][j]
              for i in range(112) for j in range(112)),'XX^T identity')
    check(rank_sets(b)==9,'binary pairing rank')
    # Echelon pivot columns give an injective projection of the full row space.
    pivots={}
    for original in b:
        row=set(original)
        while row:
            j=min(row)
            if j in pivots: row.symmetric_difference_update(pivots[j])
            else: pivots[j]=row;break
    columns=set(pivots)
    short=[row & columns for row in b]
    check(len(columns)==9 and rank_sets(short)==9,'injective full-row projection')
    return roots,x,b,short


def flats(x):
    projected=[tuple(row[k] for k in TRIPLE) for row in x]
    directions=sorted(set(echelon([row]) for row in projected if any(row)))
    known={()};pending=[()]
    while pending:
        current=pending.pop()
        for direction in directions:
            new=echelon(current+direction)
            if len(new)<=2 and new not in known:
                known.add(new);pending.append(new)
    inventory={}
    for flat in known:
        support=frozenset(i for i,row in enumerate(projected)
                          if len(echelon(flat+(row,)))>len(flat))
        check(support not in inventory,'duplicate proper-flat support')
        inventory[support]=len(flat)
    check(len(directions)==13 and len(inventory)==39,'proper-flat enumeration')
    return inventory


def compute(certificate):
    roots,x,b,short=build()
    source=json.loads((HERE/'SOURCES.json').read_text())
    check(source['base_commit']==certificate['base_commit'],'base binding')
    for row in source['files']:
        if row['usage']=='input':
            data=(HERE.parents[1]/row['path']).read_bytes()
            check(hashlib.sha256(data).hexdigest()==row['sha256'],'source drift: '+row['path'])
    rowbits=[sum(1<<i for i in r) for r in b]
    digest=hashlib.sha256(json.dumps({'roots':roots,'X':x,'B':rowbits},sort_keys=True).encode()).hexdigest()
    check(digest==certificate['geometry_sha256'],'geometry differs from primary certificate')
    inventory=flats(x)
    listed=[]
    for row in certificate['strata']:
        coeff=row['coefficient']
        support=frozenset(i for i,r in enumerate(x) if sum(r[k]*a for k,a in zip(TRIPLE,coeff)))
        check(sum(1<<i for i in support)==int(row['support'],16),'coefficient/support binding')
        check(len(support)==row['size'],'support size binding')
        check(rank_sets(short[i] for i in support)==row['span'],'support span binding')
        listed.append(support)
    check(len(listed)==39 and set(listed)==set(inventory),'incomplete support-stratum certificate')
    def rho(A,C): return rank_sets(b[i]&C for i in A)
    coordinate_costs=[rho({i for i,row in enumerate(x) if row[k]},
                          {i for i,row in enumerate(x) if row[k]}) for k in range(8)]
    check(coordinate_costs==certificate['coordinate_copy_costs']==[8]*8,'coordinate COPY costs')
    table=[[rho(s,t) for t in listed] for s in listed]
    check(table==certificate['unmodified_pairing_table'],'pairing table mismatch')
    check(min(v for row in table for v in row)==8,'original COPY pairing floor')
    universe=set(range(112));odd=[universe-row for row in b]
    hist=Counter();deletions=Counter();exceptional=[];restore_checks=0
    # An ordering unrelated to the primary pivot scheme accelerates rank-nine
    # completion. Stopping only at a proved undeleted upper bound is exact.
    order=sorted(range(112),key=lambda i:hashlib.sha256(str(roots[i]).encode()).digest())
    support_rows=[([i for i in order if i in s],rank_sets(short[i] for i in s)) for s in listed]
    for beta,gamma in combinations(range(112),2):
        deleted=odd[beta]&odd[gamma]
        deletions[len(deleted)]+=1
        for index,(indices,before) in enumerate(support_rows):
            survivors=[i for i in indices if i not in deleted]
            after=rank_sets((short[i] for i in survivors),before)
            hist[before,after]+=1
            if after!=before:
                check(before==9 and after==8 and len(deleted)==24,'unexpected span loss')
                check(deleted<=listed[index],'exception erases irrelevant rows')
                common=universe.copy()
                for i in deleted: common.intersection_update(odd[i])
                check(common=={beta,gamma},'exception has extra common odd anchors')
                for i in deleted:
                    check(rank_sets([short[j] for j in survivors]+[short[i]])==9,
                          'proper subset of exceptional deletion loses span')
                    restore_checks+=1
                check(all(rho(set(survivors),s)==8 for s in listed),'exceptional pairing floor')
                exceptional.append({'stratum':index,'anchors':[beta,gamma],'erasure':sorted(deleted)})
    check(sum(hist.values())==39*6216 and len(exceptional)==4 and restore_checks==96,'erasure coverage')
    expected=[{k:e[k] for k in ('stratum','anchors','erasure')} for e in certificate['exceptions']]
    check(sorted(exceptional,key=lambda e:e['stratum'])==sorted(expected,key=lambda e:e['stratum']),
          'exception inventory mismatch')
    # Proposed coordinate permutations are checked as complete signed root maps.
    lookup={max(tuple(row),tuple(-v for v in row)):i for i,row in enumerate(x)}
    seen=set();pairing_checks=0
    for record in certificate['triple_transports']:
        p=record['permutation'];check(sorted(p)==list(range(8)),'invalid permutation')
        dest=tuple(sorted(p[j] for j in TRIPLE));check(list(dest)==record['destination'],'wrong destination')
        check(dest not in seen,'duplicate triple');seen.add(dest)
        mapping=[];signs=[]
        for row in x:
            new=[row[p.index(j)] for j in range(8)]
            key=max(tuple(new),tuple(-v for v in new))
            check(key in lookup,'not a root map')
            j=lookup[key];mapping.append(j);signs.append(1 if new==x[j] else -1)
        check(len(set(mapping))==112,'nonbijective line map')
        check(hashlib.sha256(json.dumps([mapping,signs]).encode()).hexdigest()==record['line_map_sha256'],
              'line-map digest mismatch')
        for i in range(112):
            check({mapping[j] for j in b[i]}==b[mapping[i]],'transport pairing mismatch')
            pairing_checks+=112
    check(seen==set(combinations(range(8),3)),'missing triple transports')
    # Literal integer compensation, without a matrix-inverse implementation.
    e=certificate['exceptions'][0];coeff=e['coefficient']
    check(coeff[0]==1,'integer fixture coefficient convention')
    U=set(e['erasure']);V=set(e['anchors'])
    w=[sum(row[j]*a for j,a in zip(TRIPLE,coeff)) for row in x]
    u=[w[i] if i in U else 0 for i in range(112)];v=[int(i in V) for i in range(112)]
    D=[[w[i]-u[i],row[TRIPLE[1]],row[TRIPLE[2]],u[i]] for i,row in enumerate(x)]
    T=[[row[TRIPLE[0]],row[TRIPLE[1]]-coeff[1]*row[TRIPLE[0]],
        row[TRIPLE[2]]-coeff[2]*row[TRIPLE[0]],v[i]+row[TRIPLE[0]]] for i,row in enumerate(x)]
    omission=[]
    for i in range(112):
        for j in range(112):
            goal=sum(x[i][k]*x[j][k] for k in TRIPLE)+u[i]*v[j]
            check(sum(a*c for a,c in zip(D[i],T[j]))==goal,'integer compensation identity')
            if j in b[i] and sum(D[i][k]*T[j][k] for k in range(3))!=goal: omission.append([i,j])
    check(bool(omission),'compensation omission was not detected')
    ranks=[rho({i for i in range(112) if D[i][k]}, {i for i in range(112) if T[i][k]}) for k in range(4)]
    primary_fixture=next(r for r in certificate['fixtures'] if r['name']=='exceptional_cancellation')
    check(ranks==primary_fixture['replacement_ranks'],'integer fixture COPY mismatch')
    # Scope controls: known false stronger statements and an algebraic rank check.
    check(rank_sets([{0,1},{1,2},{0,2}])==2,'rank control')
    axis={i for i,row in enumerate(x) if row[TRIPLE[0]]}
    losses=[j for j in range(112) if rank_sets(short[i] for i in axis-odd[j])<8]
    check(bool(losses),'singleton boundary control')
    return {'schema_version':1,'geometry_sha256':digest,'proper_flats':39,
            'flat_dimension_counts':dict(sorted(Counter(inventory.values()).items())),
            'anchor_pairs':6216,'span_checks':39*6216,
            'span_dimensions':[[a,c,n] for (a,c),n in sorted(hist.items())],
            'maximal_erasure_size_counts':dict(sorted(deletions.items())),
            'exceptions':sorted(exceptional,key=lambda e:e['stratum']),
            'single_row_restoration_checks':restore_checks,
            'original_pairing_checks':39*39,'exceptional_pairing_checks':4*39,
            'transport_pairing_entries':pairing_checks,
            'integer_fixture':{'entries':112*112,'ranks':ranks,'omission_first_failure':omission[0]},
            'controls':['rank-two-dependent-triangle','false-span-preservation-has-four-counterexamples',
                        'every-proper-exceptional-deletion-restores-span','singleton-premise-boundary',
                        'omitted-compensation-changes-constrained-entry'],
            'scope':'Finite geometric premises independently recomputed; quantified GL(4,C) theorem is written mathematics.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--certificate',type=Path,default=HERE/'CERTIFICATE.json')
    p.add_argument('--check',type=Path,default=HERE/'INDEPENDENT.json')
    p.add_argument('--write',type=Path)
    args=p.parse_args()
    result=compute(json.loads(args.certificate.read_text()))
    # Canonical JSON normalizes integer dictionary keys for comparison.
    result=json.loads(json.dumps(result))
    if args.write:args.write.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:check(result==json.loads(args.check.read_text()),'independent receipt mismatch')
    print('PASS_INDEPENDENT_THREE_MODE strata=39 erasures=6216 span_checks=242424 exceptions=4 restored=96 COPY=64')


if __name__=='__main__':main()
