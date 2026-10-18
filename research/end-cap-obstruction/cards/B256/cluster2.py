from plan import *
import random,json,sys
w=load(__import__('os').environ['EO_ROOT']+'/work/o_cf0/FULL-WORD.json.gz');M=Model(w);P=M.P;NA=len(w['A'])
g0=NA+239
regs=(124,125,148,149,231,283,281,299,297,591,471,483)
cur0={r:M.frame_at(r,g0) for r in regs}
ops={'r1':(125,231),'r2':(124,231),'r3':(124,283),'r4':(125,281),'a3':(591,283),'a1':(591,281),
     's1':(149,231),'s2':(148,231),'s3':(148,299),'s4':(149,297),'b9':(591,299),'b7':(591,297),
     'W1':(283,281),'W2':(299,297),'e1':(471,283),'e2':(483,299),'q1':(125,299),'q2':(149,283),'W3':(283,299),'z1':(124,483),'z2':(148,471)}
# precedence (a before b)
pre=[('r3','W1'),('a3','W1'),('W1','e1'),('W1','q2'),('e1','W3'),('q2','W3'),('s3','W2'),('b9','W2'),('W2','e2'),('W2','q1'),('W2','W3'),('e2','z1'),('e1','z2'),('W1','W3'),('q1','W3'),('e2','W3')]
# a(591,*) after W? absorption of 283 before W1, 299 before W2 — covered. 297,281 never written.
def run(perm):
    cur=dict(cur0)
    for n in perm:
        t,s=ops[n];F=G.basis(list(cur[t])+list(cur[s]));cur[t]=cur[s]=F
    return cur
def score(cur):
    return [inperp(cur[124],12,P),inperp(cur[125],13,P),inperp(cur[148],36,P),inperp(cur[149],37,P),inperp(cur[591],58,P),inperp(cur[591],63,P)]
names=list(ops)
def rand_topo(rng):
    rem=set(names);out=[]
    while rem:
        ok=[n for n in rem if not any(b==n and a in rem for a,b in pre)]
        n=rng.choice(sorted(ok));out.append(n);rem.remove(n)
    return out
rng=random.Random(int(sys.argv[1]) if len(sys.argv)>1 else 1);sols=[];best=0
for it in range(int(sys.argv[2]) if len(sys.argv)>2 else 5000):
    p=rand_topo(rng);c=score(run(p));s=sum(c)
    if s>best: best=s;print(best,c,p)
    if s==6: sols.append(p)
print('solutions',len(sols));json.dump(sols[:100],open('cluster2_sols.json','w'))
