"""Complex coarse saving b of a gcert/1 certificate (Sussman's E8 unit): Sussman's gx.check1 (exact scalar identity) and gxcore
mirror, a flipped-sign control, then the five-stage profile (5 x blocks + 2v x (2h-2, h-1, 2h+2, 4)), m = 5h, W = 4v + R, and
the largest 10^-18 grid b with the 10^-16 fallback by both rational engines (next point excluded).
usage: complex_b.py CERT.json.gz GXDIR"""
import sys,gzip,json,copy,importlib.util
from fractions import Fraction as Q
from collections import Counter
cert=json.load(gzip.open(sys.argv[1]));sys.path.insert(0,sys.argv[2]);import gx,gxcore
P=__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'engines')+'/'
def load(n):
    s=importlib.util.spec_from_file_location('cb_'+n,P+n+'.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M=load('moment');B2=load('base_two_moment')
st={};gx.check1(cert,scalar=True,stats=st)
h,v,R,N,cst=cert['h'],cert['v'],cert['R'],cert['N'],cert['cst']
Hinv=Counter()
for w in cert['blocks'].values():
    for r,n in w.items(): Hinv[int(r)]+=n
mir=gxcore.mirror(gxcore.normal(copy.deepcopy(cert)));assert mir['hist']==dict(Hinv),'gxcore histogram'
g=next(g for g in cert['A'] if g[0] in('out','in') and g[3]);c2=copy.deepcopy(cert)
for gg in c2['A']:
    if gg[0] in('out','in') and gg[3]: t,a,b=gg[3][0];gg[3][0]=[t,-a,b];break
try: gx.check1(c2,scalar=True);raise SystemExit('flipped sign accepted')
except AssertionError as e: assert str(e).startswith('E5'),str(e)
H={r:5*n for r,n in Hinv.items()}
for r in (2*h-2,h-1,2*h+2,4): H[r]=H.get(r,0)+2*v
m=5*h;W=4*v+R;mass=sum(r*n for r,n in H.items())
print('cert h %d v %d R %d N %d cst %d ext %s | m %d W %d deficit %d (4v-5cst %d) | gx PASS, gxcore PASS, flip rejected E5'%(h,v,R,N,cst,cert.get('ext'),m,W,m*W-mass,4*v-5*cst))
fb=32*m*m*sum(H.values());root=M.certify(H,m,W,True);b=Q(int(Q(root['lower'])*10**18),10**18)
cm=M.moment(H,m,W,b,True);nx=M.moment(H,m,W,b+Q(1,10**18),True);assert cm[1]<1<nx[0]
_,up=B2.moment(m,W,list(H.items()),b);_,bu=B2.moment(m,W,[(1,fb)],b);lo,_=B2.moment(m,W,list(H.items()),b+Q(1,10**18));bl,_=B2.moment(m,W,[(1,fb)],b+Q(1,10**18))
assert up+Q(1,10**16)*bu<1<lo+Q(1,10**16)*bl
print('complex b =',b,float(b))
