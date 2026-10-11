"""Exact bit coarse saving of a PR249-format p=10 word + #315 outer assembly (our p10bs copies of #315's engines), bit-bound path.
Profile: 5 x local children (MOVE ranks, COPY ranks) + 2v x {2h-2, h-1, 2h+2, 4}; W = 4v + sum_helpers (h - sigma)/h; x12 normalization (T=60).
usage: price.py WORD [b]"""
import sys,json,importlib.util,collections,numpy as np
from fractions import Fraction as Q
P=__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'engines')+'/'
def load(n):
    s=importlib.util.spec_from_file_location('pp_'+n,P+n+'.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
moment=load('moment');other=load('base_two_moment');outer=load('outer')
d=sys.argv[1];b=Q(sys.argv[2]) if len(sys.argv)>2 else Q(876248285600677,10**18)
st=json.load(open(d+'/249-states.json'));fr=json.load(open(d+'/frames.json'))['frames'];dim={int(k):len(x['B']) for k,x in fr.items()}
rec=np.fromfile(d+'/249-records.bin',dtype='<i4').reshape(-1,6);v,n,h=st['v'],st['n'],20
Hc=collections.Counter();m_=rec[(rec[:,0]==0)&(rec[:,4]>0)];Hc.update(m_[:,4].tolist());Hc.update(rec[rec[:,0]==2][:,5].tolist())
resid=sum(dim[st['final'][str(r)]]-dim[st['initial'][str(r)]] for r in range(2*v,n))  # residual width = endpoint - sigma (endpoint FULL unless restored early)
prof=collections.Counter({j:5*c for j,c in Hc.items()})
for j in (2*h-2,h-1,2*h+2,4): prof[j]+=2*v
T=12;m=100;norm={int(k):int(c)*T for k,c in prof.items() if c};Wn=Q(4*v*h+resid,h)*T;assert Wn.denominator==1;Wn=int(Wn)
mass=sum(k*c for k,c in norm.items());assert m*Wn-mass==T*(4*v-5*h*(h-2)),('deficit',m*Wn-mass);print('local H',dict(sorted(Hc.items())));print('resid',resid,'W',Wn,'deficit',m*Wn-mass)
root=moment.certify(dict(norm),m,Wn,True);c=Q(int(Q(root['lower'])*10**18),10**18)
bm=moment.moment(norm,m,Wn,c,True);nb=moment.moment(norm,m,Wn,c+Q(1,10**18),True);assert bm[1]<1<nb[0]
fb=32*m*m*sum(norm.values());_,up=other.moment(m,Wn,list(norm.items()),c);_,bad=other.moment(m,Wn,[(1,fb)],c)
lo,_=other.moment(m,Wn,list(norm.items()),c+Q(1,10**18));blo,_=other.moment(m,Wn,[(1,fb)],c+Q(1,10**18))
assert up+Q(1,10**16)*bad<1<lo+Q(1,10**16)*blo
grid=Q(1,10**18);eta=Q(1,10**12);beta=Q(1,10**9);cap=(1-beta)*b
sv=min(c,Q(((cap-grid)*10**18).__floor__(),10**18));binding='bit' if sv==c else 'complex'
chain=[Q(384599,10**10)]
for _ in range(3):
    a=(1-sv)*sv+sv*chain[-1];assert chain[-1]<a<sv<1-a;chain.append(a)
bit=chain[-1]
bridge=dict(proof='PROOF.md',representation='Exact powers with source-bound finite overcharges',semantic=dict(G=dict(base=2,exponent=30000),E=dict(base=2,exponent=100000),B_upper=dict(base=2,exponent=100001),C0=dict(base=2,exponent=210000),C1=1,strict_literal_gap=1,induction_gap_lower=1),rows=dict(coefficient=20161,degree=10**6,suffix_slope=4*10**6,degree_gap=Q(10**6)-Q(51*20161,25)))
q=bit*(1-2*eta);mn=(1-eta)*q/(1+q);t=mn*10**18;k=Q((t.numerator-1)//t.denominator,10**18)
asm=outer.assembly(bit,b,bridge,k,eta=eta,beta=beta);assert len(asm['strict_constraints'])==47 and min(asm['strict_constraints'].values())>0
try: outer.assembly(bit,b,bridge,k+Q(1,10**18),eta=eta,beta=beta);raise SystemExit('ADJACENT ADMITTED')
except AssertionError: pass
print('bit coarse c =',c,float(c),'| b =',b,'| binding',binding)
print('KAPPA =',k,'=','%.15e'%float(k),'| vs #352 801083628465007/10^18: %+.4f%%'%(100*(float(k)/8.01083628465007e-4-1)))
json.dump(dict(word=d,local=dict(sorted(Hc.items())),resid=resid,W=Wn,bit_coarse=str(c),b=str(b),binding=binding,kappa=str(k),kappa_float=float(k)),open(d+'/kappa.json','w'),indent=1)
