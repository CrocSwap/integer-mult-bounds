#!/usr/bin/env python3
"""Independent exact-projector audit of the eight-contact index obstruction.

Requires the authenticated #8027 scalar machine and the architect's small
combinatorial witness; uses no code from either producer.
"""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import collections
import gzip
import json
import sys

P = Path(__file__).resolve().parent / 'pinned/strong-bit.json.gz'
W = Path(__file__).resolve().parent / 'INDEX-WITNESS.json'

def projector(frame):
    vec = frame['B'] + frame['A']
    n=8
    z=[[Fraction(vec[j][i]) for j in range(n)] + [Fraction(i==j) for j in range(n)] for i in range(n)]
    for j in range(n):
        p=next(i for i in range(j,n) if z[i][j])
        z[j],z[p]=z[p],z[j]
        den=z[j][j]
        z[j]=[a/den for a in z[j]]
        for i in range(n):
            if i!=j and z[i][j]:
                factor=z[i][j]
                z[i]=[a-factor*b for a,b in zip(z[i],z[j])]
    inv=[r[n:] for r in z]
    dim=frame['dim']
    return tuple(tuple(sum(Fraction(vec[k][i])*inv[k][j] for k in range(dim)) for j in range(n)) for i in range(n))

def matmul(a,b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(8)) for j in range(8)) for i in range(8))

def le(a,b):
    return matmul(a,b)==a and matmul(b,a)==a

def rank(rows):
    piv={}
    for v in rows:
        while v:
            k=v.bit_length()-1
            if k not in piv:
                piv[k]=v
                break
            v^=piv[k]
    return len(piv)

def native(g):
    val={i:1<<i for i in range(g['public'])}
    at=dict(enumerate(g['start']))
    down=[]; moves=[]; clears=0
    dims={int(c): f['dim'] for c,f in g['frames'].items()}
    for clock,(op,r,*args) in enumerate(g['program']):
        if op=='INIT':
            assert r not in at
            at[r]=args[0]; val[r]=0
        elif op=='ADD':
            s,c=args; assert at[r]==at[s]==c
            val[r]^=val[s]
        elif op=='MOVE':
            s,t=args; assert at[r]==s
            moves.append((clock,s,t))
            if dims[s]>dims[t]:down.append((clock,r,s,t,val[r]))
            at[r]=t
        elif op=='SWAP':
            s,=args
            at[r],at[s]=at[s],at[r]
            val[r],val[s]=val[s],val[r]
        elif op=='CLEAR':
            c,=args; assert at.pop(r)==c and r>=g['public']
            val.pop(r); clears+=1
        else: raise AssertionError(op)
    assert at==dict(enumerate(g['final']))
    assert [val[i] for i in range(g['public'])] == [(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(g['public'])]
    return down,moves,clears

def check_witness(side,C,F,E):
    assert len(C)==8 and len(set(C))==8
    assert all(j not in side[i] for i in C for j in C)
    assert len(F)==len(set(F))==4 and set(F)<=set(C)
    assert len(E)==5 and len({tuple(sorted(e)) for e,_ in E})==5
    assert len({i for _,i in E})==5 and not set(C)&{i for _,i in E}
    for e,i in E:
        assert len(e)==2 and set(e)<=set(F)
        assert side[i]&set(C)==set(e)
    for e,i in E:
        for f,j in E:
            if i!=j and set(e)&set(f):assert j not in side[i]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('source',nargs='?',type=Path,default=P)
    parser.add_argument('witness',nargs='?',type=Path,default=W)
    args=parser.parse_args()
    raw=args.source.read_bytes(); assert sha256(raw).hexdigest()=='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
    g=json.loads(gzip.decompress(raw)); w=json.loads(args.witness.read_text())
    assert g['public']==630
    start=g['start'][:111]; target=g['final'][111:222]
    assert all(g['frames'][str(c)]['dim']==1 for c in start)
    assert all(g['frames'][str(c)]['dim']==7 for c in target)
    allcharts=set(start+target)
    down,moves,clears=native(g)
    allcharts.update(c for _,a,b in moves for c in (a,b))
    Q={c:projector(g['frames'][str(c)]) for c in sorted(allcharts)}
    for q in Q.values():assert matmul(q,q)==q
    side=[{j for j in range(111) if le(Q[start[j]],Q[target[i]])} for i in range(111)]
    assert all(i not in side[i] for i in range(111))
    assert all((j in side[i])==(i in side[j]) for i in range(111) for j in range(111))
    C=w['clique']; F=w['four']; E=[(tuple(e),i) for e,i in w['outs']]
    check_witness(side,C,F,E)
    # A wrong geometrical claim with otherwise valid-looking endpoint/edge sizes
    # must fail; as must an outsider on two adjacent nuisance edges.
    bad_E=list(E)
    old_edge,old_receiver=bad_E[0]
    replacement=next(x for x in F if x not in old_edge)
    bad_E[0]=((old_edge[0],replacement),old_receiver)
    try:check_witness(side,C,F,bad_E)
    except AssertionError:pass
    else:raise AssertionError('a false endpoint incidence escaped the witness audit')
    bad_C=list(C); bad_C[-1]=bad_C[0]
    try:check_witness(side,bad_C,F,E)
    except AssertionError:pass
    else:raise AssertionError('a repeated clique port escaped the witness audit')
    dims={int(c):v['dim'] for c,v in g['frames'].items()}
    for _,a,b in moves:
        if dims[a]<=dims[b]:assert le(Q[a],Q[b])
        else: assert le(Q[b],Q[a])
    assert len(down)==27 and clears==3433
    ends=[row for row in down if row[3]==0]
    assert len(ends)==9
    masks=[row[4]&((1<<111)-1) for row in ends]
    assert masks==[sum(1<<i for i in b) for b in w['broadcast']]
    assert rank(masks)==9
    for i,sel in enumerate(w['w']):
        code=0
        for j,m in enumerate(masks):
            if sel>>j&1:code^=m
        assert {j for j in range(111) if (code^(1<<i))>>j&1}<=side[i]
    result={
        'archive_sha256':sha256(raw).hexdigest(),
        'witness_sha256':sha256(args.witness.read_bytes()).hexdigest(),
        'frame_projectors_checked':len(Q), 'native_legal_moves_checked':len(moves),
        'native_downward_moves':len(down), 'native_chain_terminal_clocks':[r[0] for r in ends],
        'retained_receipt_rows_restricted_to_head_inputs_rank':rank(masks),
        'all_111_index_decoders_verified':True,
        'self_side_observation_absent_for_all_111':True,
        'side_matrix_symmetric':True, 'clique':C, 'four':F, 'five_edges':E,
        'corruption_controls':{'bad_endpoint_incidence_rejected':True,'repeated_clique_port_rejected':True},
        'native_private_clears':clears,
    }
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
