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

S=1<<256; BITS=96
def sqrt_up(n):
    r=isqrt(n);return r+(r*r<n)
def power(x,t):
    # Outward fixed-point repeated radicals; no logarithms or predecessor pricing.
    require(0<x<=1 and 0<=t<=1,'power domain')
    if t==0:return F(1),F(1)
    if t==1:return x,x
    a=(t.numerator<<BITS)//t.denominator
    def dyadic(k):
        if k==(1<<BITS):return x,x
        lo=x.numerator*S//x.denominator;hi=-((-x.numerator*S)//x.denominator)
        plo=phi=S
        for i in range(1,BITS+1):
            lo=isqrt(lo*S);hi=sqrt_up(hi*S)
            if (k>>(BITS-i))&1:
                plo=plo*lo//S;phi=-((-phi*hi)//S)
        return F(plo,S),F(phi,S)
    low=dyadic(a+(F(a,1<<BITS)<t))[0]
    high=dyadic(a)[1]
    return low,high
# Exact perfect-square calibrations check outward containment at the first radical position.
calibrations=0
for k in range(2,20):
    for j in range(1,k):
        lo,hi=power(F(j*j,k*k),F(1,2));require(lo<=F(j,k)<=hi,'square calibration');calibrations+=1
source=json.loads((ROOT/'research/complex-local-word-ceiling/RESULT.json').read_text())
local={int(k):v for k,v in source['selected']['local_profile_per_call'].items()}
N=source['selected']['calls']; W=source['selected']['live'];m=source['model']['m'];R=source['model']['idle_rank_cap']
M=72*W+64*N-N*sum(r*n for r,n in local.items())
require((N,W,m,R,M)==(144,14336,73,51,237024),'selected invoice')
prior=json.loads((HERE/'references/pr1685-RESULT.json').read_text()); rows=[]
for old in prior['rows']:
    a=F(old['a']);prices={r:power(F(r,m),1-a) for r in set(local)|{1,3,7,16,27,32,48,51}}
    Llo=N*sum(n*prices[r][0] for r,n in local.items());Lhi=N*sum(n*prices[r][1] for r,n in local.items())
    clo,chi=(x/R for x in prices[R]);caps={};bounds={}
    for K in [1,3,7,16,32,48]:
        nlo=W-Lhi-M*chi;nhi=W-Llo-M*clo
        dlo=prices[K][0]/K-chi;dhi=prices[K][1]/K-clo
        require(0<dlo<=dhi and 0<nlo<=nhi,'positive interval division')
        lo=nlo/dhi;hi=nhi/dlo
        require(lo.numerator//lo.denominator==hi.numerator//hi.denominator,'integer cap unresolved')
        caps[str(K)]=hi.numerator//hi.denominator
        bounds[str(K)]=[str(lo),str(hi)]
    require(caps==old['certified_integer_mass_caps'],'independent radical cap disagreement')
    q,s=divmod(M,R)
    ilo=Llo+q*prices[R][0]+prices[s][0];ihi=Lhi+q*prices[R][1]+prices[s][1]
    require(ilo<ihi and ihi<W,'integer relaxation is below one at audited exponents')
    rows.append({'a':str(a),'caps':caps,'integer_moment_interval':[str(ilo/W),str(ihi/W)]})
# Independent unbounded integer-partition DP: all mass <=100, caps 2..12.
dp_cases=0;edges=0
for cap in range(2,13):
    prices={r:power(F(r,cap+1),F(1,2)) for r in range(1,cap+1)}
    dp=[(F(0),F(0),())]
    for mass in range(1,101):
        candidates=[(dp[mass-r][0]+prices[r][0],dp[mass-r][1]+prices[r][1],tuple(sorted((*dp[mass-r][2],r)))) for r in range(1,min(cap,mass)+1)]
        edges+=len(candidates)
        chosen=min(candidates,key=lambda c:c[1])
        for c in candidates:
            require(c[2]==chosen[2] or chosen[1]<c[0],'distinct DP histogram order unresolved')
        dp.append(chosen)
        q,s=divmod(mass,cap)
        expected=tuple(sorted([cap]*q+([s] if s else [])))
        require(chosen[2]==expected,'independently optimized DP histogram disagrees')
        dp_cases+=1
# Exact boundary controls: all partitions tie at a=0; convex prices reverse concentration.
require(F(1,73)+F(2,73)==F(3,73),'linear boundary')
require(F(1,73)**2+F(2,73)**2<F(3,73)**2,'convex wrong-exponent control')
require(rows[-1]['caps']['48']==1603 and rows[-1]['caps']['48']<1604,'first excluded mass')
require(divmod(M,R)==(4647,27) and 4647*51+27==M,'integer optimal inventory')
# Changing the paid local rank-one count changes the bound, even if idle mass is held fixed.
a=F(169,100000);p1=power(F(1,73),1-a);require(p1[0]>0,'paid local omission control')
receipt=json.loads(json.dumps({'status':'PASS_IDLE_STABILITY_RADICAL_AUDIT','rows':rows,'square_calibrations':calibrations,'integer_dp_cases':dp_cases,'integer_dp_transitions':edges,'optimum':{'51':4647,'27':1},'controls':4,'no_predecessor_pricing_import':True,'no_new_kappa':True},sort_keys=True))
require(receipt==json.loads((HERE/'RESULT.json').read_text()),'committed audit receipt differs from recomputation')
print(json.dumps(receipt,sort_keys=True))
