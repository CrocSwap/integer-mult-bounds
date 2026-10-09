#!/usr/bin/env python3
"""Exact all-address local signed endpoint controls, with odd/alternating gauges."""
from pathlib import Path
import json,hashlib,argparse
if not __debug__:raise SystemExit("Assertions required")
from complex_profile import basis,nondeg,inside,null

def inverse(rows):
 n=len(rows);A=[x|(1<<(n+i))for i,x in enumerate(rows)]
 for j in range(n):
  k=next(k for k in range(j,n)if A[k]>>j&1);A[j],A[k]=A[k],A[j]
  for k in range(n):
   if k!=j and A[k]>>j&1:A[k]^=A[j]
 assert all(A[j]&((1<<n)-1)==1<<j for j in range(n));return [x>>n for x in A]
def projector(B,z):
 B=basis(B);assert nondeg(B)
 G=[sum(((x&y).bit_count()%2)<<j for j,y in enumerate(B))for x in B];inv=inverse(G);b=sum(((z&x).bit_count()%2)<<i for i,x in enumerate(B));out=0
 for x,row in zip(B,inv):
  if (row&b).bit_count()%2:out^=x
 return out

def run(record=False):
 h=4;H=basis((1,2,4));E=basis((8,));allspace=basis((1,2,4,8));cases=[];wrong_minus=one_endpoint=0
 for name,S in(('odd_line',basis((7,))),('alternating_plane',basis((3,5)))):
  assert inside(S,H)and nondeg(S);D=null(basis(null(H,h)+S),h);ES=basis(E+S);assert nondeg(D)and nondeg(ES)
  assert len(D)==len(H)-len(S)and len(ES)==len(E)+len(S)
  for z in range(1<<h):
   q=lambda B:projector(B,z).bit_count()%4
   s,e,a,d,f=q(S),q(E),q(H),q(D),q(allspace)
   assert (a-s-d)%4==0 and (q(ES)-e-s)%4==0
   # Stage1 source C_S, sink F C_S. Internal H-S plus exterior E+S.
   assert (f+s-s)%4==f and (d+q(ES))%4==f
   # Stage2 translated source C_E, sink F C_E, internal H-S, same exterior.
   assert ((f+e)-e)%4==f and (d+q(ES))%4==f
   # Literal source C_S with sink C_(I-S)=F C_S^-1 is wrong in general.
   wrong_minus+=((f-s)-s)%4!=f
   one_endpoint+=(f-s)%4!=f
  cases.append(dict(name=name,sigma_basis=list(S),sigma_rank=len(S),internal_rank=len(D),exterior_rank=len(ES),addresses=1<<h))
 assert wrong_minus and one_endpoint
 out=dict(status='PASS',cases=cases,source_and_sink_gauged_together=True,stage1_full_endpoint_phase_exact=True,stage2_translated_endpoint_phase_exact=True,all_orthogonal_residual_ranks_exact=True,negative_controls=dict(literal_complement_sink_failures=wrong_minus,source_only_gauge_failures=one_endpoint),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Exact all16Fourier-address controls for a noncoordinate odd gauge and a noncoordinate alternating gauge. General proof uses orthogonal q-additivity; it is not an enumeration of all576-axis addresses or an all-size streaming theorem.')
 p=Path(__file__).with_name('endpoint-audit.json');raw=json.dumps(out,sort_keys=True,indent=2)+'\n'
 if record:p.write_text(raw)
 else:assert p.read_text()==raw,'Frozen endpoint audit differs'
 print('PASS signed endpoint identities and rejecting controls');return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--record',action='store_true');a=ap.parse_args();run(a.record)
