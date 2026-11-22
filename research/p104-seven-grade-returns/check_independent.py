#!/usr/bin/env python3
"""Independent low-pivot and dual-trace audit of 999 rank-seven return screens."""
from collections import Counter,defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

SOURCE=Path(__file__).resolve().parent / 'pinned/strong-bit.json.gz'
WITNESS=Path(__file__).resolve().parent / 'SEVEN.json'
SHA='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'

def projector(frame):
    vec=frame['B']+frame['A'];n=8
    mat=[[Fraction(vec[j][i]) for j in range(n)]+[Fraction(i==j) for j in range(n)] for i in range(n)]
    for j in range(n):
        pivot=next(i for i in range(j,n) if mat[i][j])
        mat[j],mat[pivot]=mat[pivot],mat[j]
        den=mat[j][j];mat[j]=[x/den for x in mat[j]]
        for i in range(n):
            if i!=j and mat[i][j]:
                den=mat[i][j];mat[i]=[a-den*b for a,b in zip(mat[i],mat[j])]
    inv=[r[n:] for r in mat];d=frame['dim']
    return tuple(tuple(sum(Fraction(vec[k][i])*inv[k][j] for k in range(d)) for j in range(n)) for i in range(n))

def product(a,b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(8)) for j in range(8)) for i in range(8))

def basis(rows):
    b={}
    for x in rows:
        while x:
            p=x&-x
            if p not in b:b[p]=x;break
            x^=b[p]
    return b

def rank(rows):return len(basis(rows))

def contained(b,x):
    while x:
        p=x&-x
        if p not in b:return False
        x^=b[p]
    return True

def used(row,owner):
    op,i,*a=row
    return i==owner or (op in ('ADD','SWAP') and a[0]==owner)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('source',nargs='?',type=Path,default=SOURCE)
    parser.add_argument('witness',nargs='?',type=Path,default=WITNESS)
    args=parser.parse_args()
    raw=args.source.read_bytes();assert sha256(raw).hexdigest()==SHA
    g=json.loads(gzip.decompress(raw));receipt=json.loads(args.witness.read_text())
    n=g['public'];assert n==630
    p=g['program'];d={int(c):f['dim'] for c,f in g['frames'].items()}
    assert 1 not in g['start'] and not any(d[c]==1 for c in g['final'])
    moves=[(t,r) for t,r in enumerate(p) if r[0]=='MOVE']
    first_top=min(t for t,r in moves if r[3]==1);assert first_top==6908
    downs=[(t,r) for t,r in moves if d[r[2]]>d[r[3]]]
    assert len(downs)==27
    triples=[downs[i:i+3] for i in range(0,27,3)]
    retired=[]
    for block in triples:
        (a,ra),(b,rb),(c,rc)=block
        assert ra[3]==rb[2] and rb[3]==rc[2] and rc[3]==0
        x,y,z=ra[1],rb[1],rc[1]
        initial=[t for t,row in enumerate(p[:a+1]) if row[:2]==['INIT',x]]
        assert len(initial)==1
        start=initial[0]
        assert all(row[1] in (x,y,z) and row[0] in ('INIT','ADD','MOVE') for row in p[start:c+1])
        assert sum(row[0]=='MOVE' for row in p[start:c+1])==3
        for owner in (x,y):
            later=[row for row in p[c+1:] if used(row,owner)]
            assert len(later)==1 and later[0][0]=='CLEAR' and later[0][1]==owner
            retired.append(owner)
        assert p[a+1:b].count(['ADD',rb[1],ra[1],ra[3]])==1
        assert p[b+1:c].count(['ADD',rc[1],rb[1],rb[3]])==1
    assert len(retired)==len(set(retired))==18
    sites=sorted(c for c in d if d[c]==1);assert len(sites)==111
    eye=tuple(tuple(Fraction(i==j) for j in range(8)) for i in range(8))
    top=projector(g['frames']['1']);assert top==eye and d[1]==8
    for c in sites:
        frame=g['frames'][str(c)];assert frame['dim']==len(frame['B'])==1
        q=projector(frame)
        assert product(q,q)==q and sum(q[i][i] for i in range(8))==1
        assert product(q,top)==q and product(top,q)==q
    outbound={c:[t for t,r in moves if t>=first_top and r[2]==c] for c in sites}
    assert Counter(map(len,outbound.values()))=={0:2,1:109}
    assert Counter(d[p[x[0]][3]] for x in outbound.values() if x)=={0:8,6:20,7:81}
    fids=[block[-1][0] for block in triples]
    slots=sorted(set(fids)|{t for a in outbound.values() for t in a})
    bit={t:1<<i for i,t in enumerate(slots)}
    at=dict(enumerate(g['start']));value={i:1<<i for i in range(n)}
    noise={i:0 for i in range(n)};stock=defaultdict(list)
    for i,c in at.items():stock[c].append((value[i],0))
    root_pre={};return_payload={};return_noise={}
    for t,(op,i,*a) in enumerate(p):
        if op=='INIT':assert i not in at;at[i]=a[0];value[i]=noise[i]=0
        elif op=='ADD':
            j,c=a;assert at[i]==at[j]==c
            value[i]^=value[j];noise[i]^=noise[j]
        elif op=='MOVE':
            s,dest=a;assert at[i]==s
            if t in fids:
                root_pre[t]=tuple(stock[0]);return_payload[t]=value[i];return_noise[t]=noise[i]
            noise[i]^=bit.get(t,0)
            at[i]=dest;stock[dest].append((value[i],noise[i]))
        elif op=='SWAP':
            j,=a;at[i],at[j]=at[j],at[i];value[i],value[j]=value[j],value[i];noise[i],noise[j]=noise[j],noise[i]
        elif op=='CLEAR':assert at.pop(i)==a[0];value.pop(i);noise.pop(i)
        else:raise AssertionError(op)
    assert at==dict(enumerate(g['final']))
    assert [value[i] for i in range(n)]==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(n)]
    outputs=defaultdict(list)
    for i,c in at.items():outputs[c].append(i)
    seen={c:sum(0 for _ in ()) for c in stock}
    for c,rows in stock.items():
        seen[c]=0
        for _,e in rows:seen[c]|=e
    checked=set();root_count=ever_count=0
    def certify_pair(pair,first,other):
        assert pair is not None and len(pair)==2 and pair[0]!=pair[1]
        aa,bb=pair
        rows=stock[aa]+stock[bb]
        assert rank(x for x,e in rows)==len(rows)
        for c in pair:
            assert other is None or not seen[c]&other
            candidates=[i for i in outputs[c] if noise[i]&first]
            assert candidates
            lifted=basis(x|(e<<n) for x,e in stock[c])
            assert any(contained(lifted,value[i]|(noise[i]<<n)) for i in candidates)
    for record in receipt['classifications']:
        f=record['original_completed_return'];c=record['receiver_chart']
        assert (f,c) not in checked and f in fids and c in sites
        checked.add((f,c)); candidates=[x for x in outbound[c] if x!=f]
        departure=candidates[0] if candidates else None
        assert record['surviving_departure']==departure
        eb=bit[departure] if departure is not None else None
        certify_pair(record['two_immune_witnesses_for_root'],bit[f],eb)
        base=[x^(return_payload[f] if e&bit[f] else 0) for x,e in stock[0]]
        assert not contained(basis(base),return_payload[f])
        incoming=bool(eb and any(e&eb for x,e in root_pre[f]))
        reach=bool(eb and seen[0]&eb)
        original=bool(eb and return_noise[f]&eb)
        assert (incoming,reach,original)==(record['alternate_noise_reaches_root_preclock'],
             record['alternate_noise_ever_reaches_zero'],record['alternate_noise_reaches_missing_native_field'])
        assert not original
        if reach or original:certify_pair(record['two_immune_witnesses_for_departure'],eb,bit[f])
        assert record['status']=='excluded'
        root_count+=incoming;ever_count+=reach
    assert len(checked)==999 and root_count==28 and ever_count==64
    first=receipt['classifications'][0]
    pair=first['two_immune_witnesses_for_root']
    try:certify_pair([pair[0],pair[0]],bit[first['original_completed_return']],None)
    except AssertionError:pass
    else:raise AssertionError('duplicate terminal corruption was not rejected')
    print(json.dumps({'source_sha256':SHA,'witness_sha256':sha256(args.witness.read_bytes()).hexdigest(),
      'no_initial_public_field_at_top':True,'first_top_arrival':first_top,
      'no_rank1_final_public_outputs':True,'rank1_charts':111,
      'exact_projector_nesting_checked_for_all_111_rank1_destinations':True,
      'rank1_departures_after_first_top_arrival':{'0':2,'1':109},
      'departure_destination_dimensions':{'0':8,'6':20,'7':81},
      'removed_chain_intermediate_owners_with_only_final_clear':retired,
      'independently_checked_cases':len(checked),'line_departures_ever_reaching_zero':ever_count,
      'line_departures_reaching_zero_before_old_return':root_count,
      'no_line_departure_reaches_old_return_producer':True,
      'all_terminal_witnesses_checked_with_low_pivot_rank':True,
      'duplicate_terminal_mutation_rejected':True},sort_keys=True,indent=2))

if __name__=='__main__':main()
