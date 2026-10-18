from fractions import Fraction as Q
from decimal import Decimal, localcontext
import json,importlib.util,gzip
from pathlib import Path

def need(x,label):
 if not x:raise RuntimeError(label)
def decimal(q):
 with localcontext()as ctx:
  ctx.prec=65
  return str(Decimal(q.numerator)/Decimal(q.denominator))
def encode(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):encode(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [encode(v)for v in x]
 return x
def price(H,bit,M,B,A,bad=False):
    cert=M.certify(H,73,14336,bad);b=Q(cert['lower']);intervals=[]
    for z,accept in [(b,True),(b+Q(1,10**24),False)]:
        i=M.moment(H,73,14336,z,bad);j=B.moment(73,14336,list(H.items()),z)
        if bad:
            c=B.moment(73,14336,[(1,32*73*73*sum(H.values()))],z)
            j=(j[0]+c[0]/10**16,j[1]+c[1]/10**16)
        need(i[1]<1 and j[1]<1 if accept else i[0]>1 and j[0]>1,'two rational moment signs')
        intervals.append({'b':z,'accepted':accept,'mercator':[v-1 for v in i],'base_two':[v-1 for v in j]})
    eta=beta=Q(1,10**24);s=min(bit,(1-beta)*b)-Q(1,10**27)
    need(0<s<bit and s<(1-beta)*b,'strict common saving')
    a=Q(384599,10**10);cuts=[]
    ceil=lambda x:-(-x.numerator//x.denominator)
    for _ in range(7):
        old=a;a=(1-s)*s+s*old;gap=min(s-a,1-a-s,1-a-s*(1-old),1-s)
        need(old<a<s<1-a and gap>0,'bootstrap gap')
        cut=max(ceil(36/gap**2),ceil(2*(4+512)/gap))
        need(cut*gap**2>=36 and cut*gap>=2*(4+512),'charged finite cutoff')
        cuts.append({'a':a,'gap':gap,'cutoff_log2':cut})
    q=a*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin*10**18
    k=Q((ticks.numerator-1)//ticks.denominator,10**18)
    bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
    outer=A.assembly(a,b,bridge,k,eta=eta,beta=beta)
    need(len(outer['strict_constraints'])==47 and all(v>0 for v in outer['strict_constraints'].values()),'47 strict outer inequalities')
    controls=[]
    for name,kk,ee,be in [('next_grid',k+Q(1,10**18),eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),('unit_beta',k,eta,Q(1))]:
        try:A.assembly(a,b,bridge,kk,eta=ee,beta=be)
        except AssertionError:controls.append(name)
        else:raise RuntimeError('outer control accepted: '+name)
    return {'complex_lower':b,'kappa':k,'kappa_decimal':decimal(k),'moment_checks':intervals,'outer_constraints':outer['strict_constraints'],'outer_controls':controls,'bootstrap':cuts}

