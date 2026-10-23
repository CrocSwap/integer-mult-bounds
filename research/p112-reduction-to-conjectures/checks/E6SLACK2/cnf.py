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
with open(out,'w') as f:
    f.write("p cnf %d %d\n"%(nv,len(cl)))
    for c in cl: f.write(" ".join(map(str,c))+" 0\n")
print(nv,len(cl))
