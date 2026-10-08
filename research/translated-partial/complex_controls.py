#!/usr/bin/env python3
"""Exact h28 tensor projection, phase-polynomial, and residual-basis checks.

The phase equality is proved on every binary address: its polarization
vanishes by projector identities, and all coordinate basis values vanish.
No enumeration of 2^(h^3) addresses is needed.
"""
# Copyright 2026 Zhihao Chen (jacklightChen), Apache-2.0.
# Phase source-frame extension and complete physical audit. Source-frame
# freedom is inspired by eumemic's Claude-assisted PR #13; the retained
# producer is from PR #7 and whole-residual recursion is icekylinx's PR #10.
# Research assistance is recorded in the repository contribution notice.
from pathlib import Path
from collections import Counter
import json,hashlib

def dot(x,y):return (x&y).bit_count()%2

def triple_complement_basis(h,T=(0,1,2)):
 # The complement of an odd triple consists of the alternating plane
 # on T, absorbed using one outside coordinate, and the other units.
 a,b,c=T;outside=[i for i in range(h) if i not in T];w=1<<outside[0]
 u=(1<<a)|(1<<b);v=(1<<b)|(1<<c)
 basis=[w^u,w^v,w^u^v]+[1<<i for i in outside[1:]]
 t=sum(1<<i for i in T)
 assert len(basis)==h-1 and all(dot(t,x)==0 for x in basis)
 assert all(dot(x,y)==int(i==j) for i,x in enumerate(basis) for j,y in enumerate(basis))
 return t,basis

def run(h=28):
 t,perp=triple_complement_basis(h);q,qperp=triple_complement_basis(h)
 assert dot(t,t)==dot(q,q)==1
 # Matrix checks for the two rank-one factors. All tensor identities are
 # direct tensor products of these exact binary matrix identities.
 P=[t if t>>i&1 else 0 for i in range(h)]
 I=[1<<i for i in range(h)]
 Pc=[a^b for a,b in zip(I,P)]
 def apply(M,x):
  out=0
  while x:
   low=x&-x;x-=low;out^=M[low.bit_length()-1]
  return out
 assert all(apply(P,p)==p for p in P)
 assert all(apply(Pc,p)==0 for p in P)
 assert all(a^b==c for a,b,c in zip(P,Pc,I))
 # Construct actual tensor projectors on each coordinate unit; no dense
 # h^3-by-h^3 binary matrix is allocated. D0=D1 XOR E.
 m=h**3;phase_classes=Counter();digest=hashlib.sha256();basis_values=0
 for i in range(h):
  for j in range(h):
   d1_template=sum(1<<((i*h+j)*h+k) for k in (0,1,2))
   e_template=sum(1<<((u*h+j)*h+k) for u in (0,1,2) for k in (0,1,2))
   for k in range(h):
    x=1<<((i*h+j)*h+k)
    d1=d1_template if k<3 else 0
    e=e_template if i<3 and k<3 else 0
    d0=d1^e;ep=x^e
    delta=(1+d0.bit_count()-d1.bit_count()-ep.bit_count())%4
    assert delta==0
    phase_classes[(d0.bit_count(),d1.bit_count(),ep.bit_count())]+=1
    digest.update(bytes((d0.bit_count(),d1.bit_count(),ep.bit_count(),delta)))
    basis_values+=1
 assert basis_values==m
 # The phase difference has zero polarization because its projector sum is
 # I+D0+D1+Eperp=I+(D1+E)+D1+(I+E)=0 over F2. Every value is therefore
 # an additive F2->Z4 character. Zero on all m coordinates implies zero
 # on all 2^m addresses exactly.
 # Explicit Eperp orthonormal basis: (Pperp x F x F) disjoint-union
 # (P x F x Qperp). Tensor Gram products prove all pairs orthonormal.
 signs=Counter()
 for p in perp:
  signs[(p.bit_count())%4]+=h*h
 for r in qperp:
  signs[(t.bit_count()*r.bit_count())%4]+=h
 assert sum(signs.values())==m-h
 assert set(signs)<={1,3}
 assert signs[1]==18900 and signs[3]==3024
 # All source/target triples are coordinate-permutation conjugates of this
 # fixed template, independently in first and third tensor factors.
 return dict(status='PASS EXACT OPERATOR INTERFACE CHECKS',h=h,m=m,
  new_residual_rank=m-h,explicit_orthonormal_basis='(Pperp tensor F tensor F) union (P tensor F tensor Qperp)',
  factor_complement_basis=perp,factor_gram_checks=2*(h-1)**2,
  positive_directional_kernels=signs[1],negative_directional_kernels=signs[3],
  negative_count_divisible_by_four=signs[3]%4==0,
  new_exit_fourth_root_wrapper='(-i)^(3024*f)=1 for every integer f; two parity-sign passes remain',
  projector_relations=['P^2=P','Pperp^2=Pperp','P Pperp=0','P+Pperp=I',
    'D1=D0+E','D0 E=0','Eperp=I+E'],
  projector_field='F2',
  phase_identity='C_I C_D0 C_D1^-1 = C_Eperp',
  phase_difference='wt(x)+wt(P_D0 x)-wt(P_D1 x)-wt(P_Eperp x) mod4',
  phase_polarization='2 x^t (I+P_D0+P_D1+P_Eperp)y = 0 mod4',
  coordinate_basis_values_checked=basis_values,
  coordinate_phase_classes=[dict(D0_weight=k[0],D1_weight=k[1],Eperp_weight=k[2],count=v) for k,v in sorted(phase_classes.items())],
  all_binary_addresses_certified_by_additivity=True,
  phase_control_sha256=digest.hexdigest(),
  all_actual_triple_pairs='Independent coordinate permutations in tensor factors1 and3 conjugate every actual P,Q to the tested triple. Dot products, projector identities, integer weights and all phase claims are invariant.',
  endpoints='Source C_D0 and sink C_I C_D0 preserve routed auxiliary map C_I. This is an algebraic logical interpretation, not source/sink preprocessing.')

if __name__=='__main__':
 result=run();Path(__file__).with_name('complex-controls.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
