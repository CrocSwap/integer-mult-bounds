#!/usr/bin/env python3
"""Exact time/precision certificate consuming independently checked physical edges."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json,sys
# Copyright 2026 Zhihao Chen (jacklightChen), Apache-2.0.
# Phase source-frame extension and complete physical audit. Source-frame
# freedom is inspired by eumemic's Claude-assisted PR #13; the retained
# producer is from PR #7 and whole-residual recursion is icekylinx's PR #10.
# Research assistance is recorded in the repository contribution notice.
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
sys.path.insert(0,str(REPO/'scripts'))
from batched_bit_rank_moment import rational_log_bounds

def logs(x):
 x=Q(x);k=0
 while x>2:x/=2;k+=1
 a,b=rational_log_bounds(x);c,d=rational_log_bounds(Q(2))
 return a+k*c,b+k*d

def run():
 physical=json.loads((HERE/'complex-physical.json').read_text())
 operator=json.loads((HERE/'complex-controls.json').read_text())
 assert physical['source_shift'] and physical['independent_histogram_matches']
 for name,digest in physical['source_sha256'].items():
  assert hashlib.sha256((REPO/'scripts'/name).read_bytes()).hexdigest()==digest, 'Producer changed: rerun physical audit and applicable finite checks'
 assert operator['all_binary_addresses_certified_by_additivity']
 h=operator['h'];m=operator['m'];W=physical['W'];D=physical['D'];s=physical['s']
 hist={int(k):v for k,v in physical['global_histogram'].items()}
 assert sum(r*n for r,n in hist.items())==s==W*m-D
 assert max(hist)==m-h and min(hist)>0
 a=Q(18,10**6);eta=Q(D,W*m)
 bounds={r:logs(Q(m,r)) for r in hist}
 weights={r:Q(r*n,W*m) for r,n in hist.items()}
 assert sum(weights.values())==1-eta
 assert all(0<a*upper<1 for lower,upper in bounds.values())
 upper=sum((weights[r]/(1-a*bounds[r][1]) for r in hist),Q())
 assert upper<1
 q=m+6*h+h*h-h;M=m-h;rho=Q(2)
 theta_bound=Q(M*M+(q-M)**2,m*m);theta=Q(9999,10000)
 assert theta_bound<theta<1
 assert Q(physical['squared_path_moment'])<=theta_bound
 E=64*(W+m+1)**3;Cdep=10000*(E+16*m+1)
 assert 36*W**3+4*s+4*W+8*m+4<E
 assert Cdep*(1-theta)>=E and Cdep>=8*(2*m)**(rho-1)
 beta=Q(1,1000);zeta=Q(1,10000);C1=rho-(rho-1)*beta+zeta
 raw=128*m*(1+1/zeta)*Cdep;C0=-(-raw.numerator//raw.denominator)
 assert m*(1+1/zeta)*Cdep+18<=C0
 return dict(status='CONDITIONAL COMPLEX-LAYER INTERFACE SAVING 18e-6; NOT AN INTEGER-MULTIPLICATION CLAIM',
  h=h,m=m,W=W,s=s,D=D,a_c=a,sigma=1-a,eta=eta,
  child_counts=hist,logarithm_bounds=bounds,rank_mass_weights=weights,
  moment_upper=upper,strict_moment_gap=1-upper,
  guard=dict(rho=rho,q=q,M=M,theta_bound=theta_bound,theta=theta,
    E=E,Cdep=Cdep,beta=beta,zeta=zeta,C1=C1,C0=C0),
  independent_physical_path_envelope=dict(rank=physical['global_maximum_rank_path_envelope'],
    squared_rank=physical['global_maximum_squared_rank_path_envelope'],
    normalized_square=physical['squared_path_moment']),
  phase_interface=dict(all_addresses=True,coordinate_checks=operator['coordinate_basis_values_checked'],
    residual_basis_size=operator['new_residual_rank'],
    negative_directions=operator['negative_directional_kernels'],
    arbitrary_auxiliary_inputs_restored_logically=True,physical_auxiliary_endpoint='C_I'),
  regression_scope='Only changed interfaces were newly tested. Retained scalar maps, local labels, common gate frames and dirty scratch identity are unchanged; previous full PR7 checks are dependencies.',
  dependencies=['PR7 finite PairedComplex28 circuit and its complete frame verification',
   'PR10 whole-residual sign wrapper and mixed-width fixed-tape implementation',
   'Our complete complex edge-rank audit (all residuals)',
   "eumemic's PR13 source-frame freedom, transferred here to arbitrary invertible phase frames"],
  source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [
    HERE/'complex_physical.py',HERE/'complex_controls.py',HERE/'complex-physical.json',HERE/'complex-controls.json']},
  publication_assessment='A complete new complex-interface proof and certificate are supplied in this folder. This module supplies only the complex interface. The accompanying bit proof and exact final assembly are separate dependencies.')

def js(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [js(v) for v in x]
 return x
if __name__=='__main__':
 result=run();(HERE/'complex-certificate.json').write_text(json.dumps(js(result),indent=2)+'\n')
 print('PASS complex layer saving:',result['a_c'],'moment gap:',float(result['strict_moment_gap']))
 print('Guard C1:',result['guard']['C1'])
