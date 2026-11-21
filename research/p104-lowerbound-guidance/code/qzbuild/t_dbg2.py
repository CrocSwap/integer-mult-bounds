from qzfast import *
from qzword import *
d=Design(4,3,[{0,1},{0,1},{0,1,2},{0,1,2}],[('H',2),('H',0),('I',{0}),('I',{0}),('H',1),('I',{1}),('I',{1})],'C1')
S=Sys(d)
z=np.random.default_rng(2).normal(size=d.nv); z,nr=lm(S,z,it=400)
V,W,ab=d.unpack(z)
print(np.abs(V).max(),np.abs(W).max(),ab)
C=assemble(d,[list(x) for x in V],[list(x) for x in W],[list(x) for x in ab],Z=0.0,O=1.0,conv=float)
P=np.eye(4)
for e in C['events']:
    M=np.eye(4); op=e[0]
    if op=='ADD': M[e[1],e[2]]+=e[3]
    elif op=='SCALE': M[e[1],e[1]]=e[2]
    elif op=='HOST': s,t,a,b=e[2],e[3],e[4],e[5]; M[s,t]=a;M[t,s]=b;M[t,t]=1+a*b
    P=M@P
    if op in('HOST','IDLE_ONE'): print(op, np.round(P,3).tolist())
print(np.round(P,6))
