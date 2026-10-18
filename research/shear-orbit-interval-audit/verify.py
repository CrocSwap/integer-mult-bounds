#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact audit by woklerx with substantial OpenAI Codex assistance."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product, permutations
from math import isqrt
import json, hashlib
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def require(ok, message):
    if not ok: raise ValueError(message)
def source_check():
    for row in json.loads((HERE/'EXTERNAL-SOURCES.json').read_text()):
        b=(HERE/row['local']).read_bytes()
        require(hashlib.sha256(b).hexdigest()==row['sha256'],'external source bytes')
        require(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'external Git blob')
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            require(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'live source bytes')
source_check()

def ceildiv(a,b): return -((-a)//b)
def witness(p,d,L,U,z):
    # All errors multiplied by d; convexity reduces all chronological k to endpoints.
    require(d>0 and L<=U and z>=0,'domain')
    bound=z if U==L else min(z,2*z//(U-L))
    for b in range(ceildiv(p-bound,d),(p+bound)//d+1):
        t=d*b-p
        low=max(ceildiv(-z-L*t,d),ceildiv(-z-U*t,d))
        high=min((z-L*t)//d,(z-U*t)//d)
        if low<=high: return low,b
    return None
def optimum(p,d,L,U):
    hi=max(abs(L*p),abs(U*p),abs(p))
    lo=-1
    while hi-lo>1:
        mid=(hi+lo)//2
        if witness(p,d,L,U,mid) is None: lo=mid
        else: hi=mid
    return hi,witness(p,d,L,U,hi)
def brute(p,d,L,U):
    # Complete box justified by the radius of a=b=0 and the k=0 extrapolation.
    z=max(abs(L*p),abs(U*p),abs(p))
    best=z
    for b in range(ceildiv(p-z,d),(p+z)//d+1):
        t=d*b-p
        for a in range(ceildiv(-z-L*t,d),(z-L*t)//d+1):
            cost=max([abs(d*b-p)]+[abs(d*a+k*t) for k in range(L,U+1)])
            best=min(best,cost)
    return best
checks=0; chronological=0
for d in range(2,10):
    for p in range(1,d):
        for L in range(-4,5):
            for U in range(L,7):
                z,w=optimum(p,d,L,U)
                require(z==brute(p,d,L,U),'interval oracle disagrees with full chronology')
                require(w is not None and (z==0 or witness(p,d,L,U,z-1) is None),'sharp threshold')
                a,b=w
                require(max([abs(d*b-p)]+[abs(d*a+k*(d*b-p)) for k in range(L,U+1)])==z,'attainment')
                checks+=1;chronological+=U-L+1
for K in range(1001):
    z,w=optimum(1,2,0,K)
    q=F(K,4);dist=min(q-q.numerator//q.denominator,1-(q-q.numerator//q.denominator))
    require(F(z,2)==max(F(1,2),q+dist),'PR1631 half-grid formula')
# Large offset/horizon is handled by feasibility, not a chronological scan.
large=(10**12+3,10**12+987)
z,w=optimum(1,3,*large)
require(witness(1,3,*large,z-1) is None,'large sharp threshold')
# An endpoint-only error rule omitting the transverse coordinate fails on K=0.
require(optimum(1,2,0,0)[0]==1,'transverse error required')
# Allowing a noninteger seed b would return zero, violating the grid contract.
require(optimum(1,2,0,70)[0]==36,'grid-integrality control')
# Replacing both endpoints by only U gives a false zero longitudinal radius.
require(optimum(1,2,0,8)[0]==4,'both endpoint constraints required')
receipt=json.loads(json.dumps({'status':'PASS_SHEAR_ORBIT_INTERVAL_AUDIT','rational_windows':checks,'chronological_positions':chronological,'half_grid_horizons':1001,'K70_grid_units':18,'large_window':list(large),'large_radius':str(F(z,3)),'large_attaining_seed':w,'controls':3,'no_new_kappa':True},sort_keys=True))
require(receipt==json.loads((HERE/'RESULT.json').read_text()),'committed audit receipt differs from recomputation')
print(json.dumps(receipt,sort_keys=True))
