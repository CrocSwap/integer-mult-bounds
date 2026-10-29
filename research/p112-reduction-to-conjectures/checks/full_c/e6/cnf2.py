import sys
# usage: cnf.py cand out.cnf budget comp...   (cover 84 points; at most count[w] pieces of dim w; <=budget free points)
cand,out,B=sys.argv[1],sys.argv[2],int(sys.argv[3]); comp=list(map(int,sys.argv[4:]))
cnt={w:comp.count(w) for w in set(comp)}
N=84; cl=[]; nv=0; byp=[[] for _ in range(N)]; vs={w:[] for w in cnt}
for ln in open(cand):
    w,hi,lo=map(int,ln.split()); m=(hi<<64)|lo
    if w not in cnt: continue
    nv+=1; vs[w].append(nv)
    for p in range(N):
        if m>>p&1: byp[p].append(nv)
free=[]
for p in range(N):
    nv+=1; free.append(nv); byp[p].append(nv)
def atmost(xs,k):
    global nv
    n=len(xs)
    if k>=n: return
    if k==0:
        for x in xs: cl.append([-x])
        return
    s=[[0]*(k+1) for _ in range(n)]
    for i in range(n):
        for j in range(1,k+1): nv+=1; s[i][j]=nv
    for i in range(n):
        cl.append([-xs[i],s[i][1]])
        if i>0:
            for j in range(1,k+1): cl.append([-s[i-1][j],s[i][j]])
            for j in range(2,k+1): cl.append([-xs[i],-s[i-1][j-1],s[i][j]])
            cl.append([-xs[i],-s[i-1][k]])
for w in cnt: atmost(vs[w],cnt[w])
atmost(free,B)
for p in range(N): cl.append(byp[p])
off={}; o=0
for w in sorted(cnt): off[w]=vs[w][0]-1
roots=[l.split() for l in open(out.split('.')[0]+'.root').read().split('\n')[1:] if l.strip()]
cases=[('R%s_%s'%(w,i),off[int(w)]+int(i)+1) for w,i in roots]
if B>0: cases.append(('free',free[0] if False else None))
p0=int(open(out.split('.')[0]+'.root').readline())
body="".join(" ".join(map(str,c))+" 0\n" for c in cl)
base=out.split('.')[0]
for name,v in cases:
    if v is None: v=free[p0]
    with open('%s_%s.cnf'%(base,name),'w') as f:
        f.write("p cnf %d %d\n"%(nv,len(cl)+1)); f.write(body); f.write("%d 0\n"%v)
print(base,len(cases),'cases')
