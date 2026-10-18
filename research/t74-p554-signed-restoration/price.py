#!/usr/bin/env python3
"""Exact arithmetic replay of the source-bound T74 profile; not physical admission.
Uses the unchanged credited multicold engines. Apache-2.0, AI-assisted.
"""
import hashlib,importlib.util,json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
P=Path(__file__).resolve().parent
PINS={'moment':'81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482','base_two_moment':'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098','outer':'c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c'}
def need(x,label):
    if not x:raise ValueError(label)
def load(n):
    p=P/'vendor'/(n+'.py');need(hashlib.sha256(p.read_bytes()).hexdigest()==PINS[n],n+' pin')
    sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def main():
    need(__debug__,'Retained outer engine assertions required; do not use -O for price.py')
    M,B,A=[load(n) for n in PINS]
    rec=json.loads((P/'RECIPE.json').read_text());H=Counter({48:22748})
    for pid,n in [('gauge44',249),('extra',417)]:
        H.update({int(r):n*v for r,v in rec['words'][pid]['report_updates']['local_profile'].items()})
    need(sum(r*n for r,n in H.items())==4816512==73*66304-23680,'complex mass')
    raw=(P/'inputs/PR589-EXPECTED.json').read_bytes();need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()=='e293ddc557742637f9f679f083a1a282d87b1b13','bit record')
    bit=json.loads(raw)['nine'];BH={int(r):n for r,n in bit['profile'].items()};c=Q(bit['bit_lower'])
    endpoints=[]
    for label,hh,m,ww,bad,z in [('bit',BH,64,bit['bit']['live'],True,c),('complex',H,73,66304,False,None),('conservative',H,73,66304,True,None)]:
        if z is None:z=Q(M.certify(hh,m,ww,bad)['lower'])
        for x,accept in [(z,True),(z+Q(1,10**24),False)]:
            l,u=M.moment(hh,m,ww,x,bad);ll,uu=B.moment(m,ww,list(hh.items()),x)
            if bad:
                sl,su=B.moment(m,ww,[(1,32*m*m*sum(hh.values()))],x);ll+=sl/10**16;uu+=su/10**16
            need((u<1 and uu<1) if accept else (l>1 and ll>1),label+' two-engine bracket')
        endpoints.append(z)
    answer=[]
    for b in endpoints[1:]:
        eta=beta=Q(1,10**24);s=min(c,(1-beta)*b)-Q(1,10**27);chain=[Q(384599,10**10)]
        for _ in range(7):
            old=chain[-1];a=s*(1-s+old);gap=min(s-a,1-a-s,1-a-s*(1-old),1-s)
            need(old<a<s<1-a and gap>0,'bootstrap')
            ceil=lambda z:-(-z.numerator//z.denominator)
            cutoff=max(ceil(36/gap**2),ceil(2*(4+2048)/gap))
            need(cutoff*gap**2>=36 and cutoff*gap>=2*(4+2048),'charged cutoff');chain.append(a)
        q=chain[-1]*(1-2*eta);ticks=(1-eta)*q/(1+q)*10**18;k=Q((ticks.numerator-1)//ticks.denominator,10**18)
        bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
        out=A.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta)
        need(len(out['strict_constraints'])==47 and all(v>0 for v in out['strict_constraints'].values()),'47 outer constraints')
        for kk,ee,be in [(k+Q(1,10**18),eta,beta),(k,Q(0),beta),(k,eta,Q(0)),(k,eta,Q(1))]:
            try:A.assembly(chain[-1],b,bridge,kk,eta=ee,beta=be)
            except AssertionError:pass
            else:raise ValueError('outer mutant accepted')
        answer.append(k)
    need(answer[0]==Q(838469055511219,500000000000000000),'published kappa')
    need(endpoints[1]==Q(335950991225108904267,200000000000000000000000),'complex endpoint')
    print('PASS_P554_PRICE kappa=0.001676938111022438 complex='+str(endpoints[1])+' conservative='+str(answer[1])+' outer=47+47 controls=8')
if __name__=='__main__':main()
