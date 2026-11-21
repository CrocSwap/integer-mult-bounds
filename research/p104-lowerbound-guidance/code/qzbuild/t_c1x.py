from qzfast import *
from qzexact import *
from qzword import assemble
import json, subprocess
d=Design(4,3,[{0,1},{0,1},{0,1,2},{0,1,2}],[('H',2),('H',0),('I',{0}),('I',{0}),('H',1),('I',{1}),('I',{1})],'C1')
S=Sys(d)
z=np.random.default_rng(2).normal(size=d.nv); z,nr=lm(S,z,it=400); print('res',nr)
# order: ab first, then v's then w's
n,m=d.n,d.m
order=list(range(2*n*m,d.nv))+list(range(0,n*m))+list(range(n*m,2*n*m))
z,fixed,vals=fix_all(S,z,order=order,verbose=False)
print('fixed',fixed.sum(),'of',d.nv)
free=[i for i in range(d.nv) if not fixed[i]]
print('free',free,[z[i] for i in free][:10])
ok,wf,C,_=exact_word(d,z,fixed,vals,path='w_c1design.json')
print('EXACT legal',ok,wf,len(C['events']))
