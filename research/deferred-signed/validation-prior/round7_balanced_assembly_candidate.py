#!/usr/bin/env python3
"""Arithmetic bridge candidate only: physical/analytic applicability is separate.
Uses pinned icekylinx PR36 assembly, derived from Zhihao Chen PR23; Apache-2.0.
"""
import sys,json,hashlib
from pathlib import Path
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'swapnil-round7/independent/complex-twostage'))
from producer import NStar3,compile_roles
sys.path.insert(0,str(HERE/'integration/scripts'))
from structured_bulk_assembly import assembly,halving,js

def main():
    c=NStar3(24);k=compile_roles(c);v=len(c.triples);N=v*v;R=k['size'];m=576;W=2*N+2*v*R
    L=sum(int(len(ins)==2)+len(outs)-1 for n,ins,outs in k['gates'])
    C=sum(4 if 23 not in S else 1+len([i for i in range(23) if i not in S]) for S in c.triples)
    word=4*L+2*v+2*len(c.pieces)+2*C
    # Literal scalar updates in both stages, plus center-copy overhead and
    # a conservative four scalar groups per rank-one endpoint correction.
    G=2*v*word+4*24*v+4*N
    s=119453132304;r=552
    E=64*(W+m+G+1)**3;charge=2*G*W*W+8*s+4*W+4+32*m
    B=s+E;C0=32*m*B*B;assert charge<E and 2*B*(m-r)>=s+E
    bit=json.loads((HERE/'round7-literal-ledger/result.json').read_text());bh={int(t):n for t,n in bit['histogram'].items()}
    bm=529;bW=108516254;br=max(bh)
    db,dc=halving(bm,br),halving(m,r);co=bW.bit_length()*db+W.bit_length()*dc
    degree=1000*((co*51)//25000+1)
    bridge=dict(bit=dict(m=bm,W=bW,maxchild=br,halving_degree=db),complex=dict(m=m,W=W,s=s,maxchild=r,halving_degree=dc),
      semantic=dict(E=E,literal_charge=charge,strict_literal_gap=E-charge,B=B,C0=C0,C1=1),rows=dict(coefficient=co,degree=degree,degree_gap=Q(degree)-Q(co*51,25)))
    ab=Q(31987,500000000);ac=Q(36926111,500000000000);eta=Q(1,10**8)
    q=ab*(1-2*eta);cc=q*(1+eta);eps=(1-eta)/(1+cc+q)
    upper=eps*q;kap=Q((upper*10**12).__floor__(),10**12)
    cert=assembly(ab,ac,bridge,kap,eta=eta,beta=Q(1,10));assert kap>Q(1,16384)
    rejected=False
    try:assembly(ab,ac,bridge,kap+Q(1,10**12),eta=eta,beta=Q(1,10))
    except AssertionError:rejected=True
    assert rejected
    out=dict(candidate_kappa=kap,dyadic_gap=kap-Q(1,16384),literal_word_events=word,scalar_group_bound=G,
      scalar_coefficient_max=Q(19,2),bridge=bridge,assembly=cert,next_grid_rejected=rejected,
      strict_constraint_count=len(cert['strict_constraints']),margin_count=len(cert['margins']),
      source_assembly_sha256=hashlib.sha256((HERE/'integration/scripts/structured_bulk_assembly.py').read_bytes()).hexdigest(),
      status='Arithmetic candidate only. New complex literal/phase checks, full h24 physical accounting, finite bridge applicability and inherited analytic/tape conditions require integration proof before a multiplication claim.',new_multiplication_bound=False)
    (HERE/'round7-balanced-assembly-candidate.json').write_text(json.dumps(js(out),indent=2)+'\n')
    print(json.dumps(js({k:out[k] for k in ['candidate_kappa','dyadic_gap','literal_word_events','scalar_group_bound','strict_constraint_count','margin_count','next_grid_rejected','new_multiplication_bound']}),indent=2))
if __name__=='__main__':main()
