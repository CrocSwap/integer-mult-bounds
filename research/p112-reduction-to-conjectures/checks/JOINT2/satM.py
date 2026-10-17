# impl B: lib.py labels + roots/Off sets from JOINT/dpP.txt (gen.py), one-hot over precomputed maximal 7-flat masks, X by functionals. usage: satM.py data nx x1 tag
import sys,subprocess
fn_in,nx,x1,tag=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
tok=open(fn_in).read().split('\n')
P,NP,NG,_,_=map(int,tok[0].split()); lab=list(map(int,tok[1].split()))
OFF=[set(map(int,tok[2+q].split()[2:])) for q in range(NP)]
pairs=[(a,b) for a in range(P) for b in range(a+1,P)]
def par(x): return bin(x).count('1')&1
N=len(lab); masks=set()
for x in range(1,512):
    for y in range(x+1,512):
        masks.add(sum(1<<t for t in range(N) if not par(x&lab[t]) and not par(y&lab[t])))
ml=sorted(masks,key=lambda v:-bin(v).count('1'))
mx=[]
for v in ml:   # keep only maximal (bitmask subset test)
    if not any(v&o==v for o in mx): mx.append(v)
mx=[frozenset(t for t in range(N) if v>>t&1) for v in mx]
print('maximal masks',len(mx),file=sys.stderr)
nv=0; cl=[]
def new():
    global nv; nv+=1; return nv
def xorv(bits):
    cur=bits[0]
    for b in bits[1:]:
        z=new(); cl.extend([[-z,cur,b],[-z,-cur,-b],[z,-cur,b],[z,cur,-b]]); cur=z
    return cur
m=[[new() for _ in mx] for a in range(P)]
for a in range(P):   # exactly one: at least one + ladder AMO
    cl.append(list(m[a])); s=[new() for _ in mx]
    for i in range(len(mx)):
        cl.append([-m[a][i],s[i]])
        if i: cl.append([-s[i-1],s[i]]); cl.append([-m[a][i],-s[i-1]])
cin=[[None]*N for a in range(P)]
for a in range(P):
    for t in range(N):
        cin[a][t]=new()   # cin <=> t in selected mask
        cl.append([-cin[a][t]]+[m[a][i] for i,M in enumerate(mx) if t in M])
        for i,M in enumerate(mx):
            if t in M: cl.append([-m[a][i],cin[a][t]])
gs=[[new() for _ in range(9)] for _ in range(nx)]
for mm in range(1,1<<nx):   # independence
    sub=[gs[i] for i in range(nx) if mm>>i&1]
    if len(sub)==1: cl.append(list(sub[0])); continue
    cl.append([xorv([f[k] for f in sub]) for k in range(9)])
e=[new() for _ in range(N)]; free=[new() for _ in range(N)]
for t in range(N):
    for g in gs: cl.append([-e[t],free[t],-xorv([g[k] for k in range(9) if (lab[t]>>k)&1])])
if x1:
    for t in range(N):
        for u in range(t+1,N): cl.append([-free[t],-free[u]])
else:
    for t in range(N): cl.append([-free[t]])
for (a,b),off in zip(pairs,OFF):
    for t in off: cl.append([e[t],cin[a][t],cin[b][t]])
fn='satM_%s.cnf'%tag
with open(fn,'w') as f:
    f.write('p cnf %d %d\n'%(nv,len(cl)))
    for c in cl: f.write(' '.join(map(str,c))+' 0\n')
print('P',P,'nx',nx,'x1',x1,'vars',nv,'clauses',len(cl))
r=subprocess.run(['kissat',fn,fn.replace('.cnf','.drat')] if False else ['kissat',fn],capture_output=True,text=True)
print([l for l in r.stdout.split('\n') if l.startswith('s ')])
