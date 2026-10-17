import sys,re,random
from geom import *
# format: n rep L1..L(n-1) pairs(i<j lex) | U ...
def parse(line):
    f=line.split('|')[0].split();n=int(f[0]);ri=int(f[1]);L=list(map(int,f[2:2+n-1]));pr=list(map(int,f[2+n-1:]))
    return n,ri,L,pr
def fmt(n,ri,L,pr): return ' '.join(map(str,[n,ri]+L+pr))
def checkN(line):
    n,ri,L,pr=parse(line);idx={};m=0
    for i in range(n):
        for j in range(i+1,n): idx[(i,j)]=pr[m];m+=1
    t=[typ[x] for x in pr]
    if any(gen[x] for x in t): return 'GEN',t
    pairs=[(x,y) for x in range(1,n) for y in range(x+1,n)];nv=(n-1)+len(pairs)
    M=[[Fr(0)]*nv for _ in range(8*len(pairs))]
    for pi,(x,y) in enumerate(pairs):
        vx=D4[idx[(0,x)]];vy=D4[idx[(0,y)]];vp=D4[idx[(x,y)]]
        for i in range(8):
            M[8*pi+i][x-1]=Fr(vx[i]);M[8*pi+i][y-1]=-Fr(vy[i]);M[8*pi+i][n-1+pi]=-Fr(vp[i])
    ns=nullspace(M,nv)
    if not ns: return 'NOSOL',t
    for _ in range(8):
        w=[sum(random.randint(1,9)*v[k] for v in ns) for k in range(nv)]
        if all(x!=0 for x in w): return 'OK',t,[str(x) for x in w[:n-1]]
    return 'ZEROCOMP',t
if __name__=='__main__':
    res={}
    mode=sys.argv[1]
    for line in sys.stdin:
        if mode=='from5':
            m=re.search(r'rep (\d+) La 0 b (\d+) c (\d+) d (\d+) e (\d+) \| ab (\d+) ac (\d+) ad (\d+) bc (\d+) bd (\d+) cd (\d+) ae (\d+) be (\d+) ce (\d+) de (\d+)',line)
            if not m: continue
            g=list(map(int,m.groups()));ri=g[0];L=g[1:5];ab,ac,ad,bc,bd,cd,ae,be,ce,de=g[5:]
            line2=fmt(5,ri,L,[ab,ac,ad,ae,bc,bd,be,cd,ce,de])+' | U'
        else: line2=line
        r=checkN(line2);res[r[0]]=res.get(r[0],0)+1
        if r[0] in ('OK','GEN'): print(line2.split('#')[0].strip()+'  #'+r[0])
    print(res,file=sys.stderr)
