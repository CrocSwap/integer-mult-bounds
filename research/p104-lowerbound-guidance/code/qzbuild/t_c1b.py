from qzfast import *
from qzword import assemble
from qzfloat import ftest
d=Design(4,3,[{0,1},{0,1},{0,1,2},{0,1,2}],[('H',2),('H',0),('I',{0}),('I',{0}),('H',1),('I',{1}),('I',{1})],'C1')
S=Sys(d)
z=np.random.default_rng(2).normal(size=d.nv); z,nr=lm(S,z,it=400); print('res',nr)
V,W,ab=d.unpack(z)
C=assemble(d,[list(x) for x in V],[list(x) for x in W],[list(x) for x in ab],Z=0.0,O=1.0,conv=float)
print('events',len(C['events']),'float replay err',ftest(C))
from qzfloat import freplay
import numpy as np
for q in (1,-1,1j):
    for D in (np.ones(3), np.array([1.3,1,1]),np.array([1,1.3,1]),np.array([1,1,1.3])):
        print(q, D, '%.2e'%freplay(C,q,D))
