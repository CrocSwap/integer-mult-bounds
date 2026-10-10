import sys, pickle, collections
sys.path.insert(0,'/home/claude/work/agentB/tools')
from base import *
L=pickle.load(open(sys.argv[1],'rb'))
ev=L['ev']; n=L['n']; dim=L['dim']; init=L['init']; chain=L['chain']
key=(int(sys.argv[2]),int(sys.argv[3]))
LM=LINEMASK[key]
blocks={X:bm for (k2,X),bm in DBM.items() if k2==key}
def bl(m):
    m2=m&LM
    full=sorted(X for X,bm in blocks.items() if bm&m2==bm)
    part=[X for X,bm in blocks.items() if bm&m2 and bm&m2!=bm]
    s='{%s}'%''.join('%x'%X for X in full)
    if part: s+='+p%d'%len(part)
    ext=popc(m&~LM)
    if ext: s+='+ext%d'%ext
    return s
def pure(m):
    if m==0 or m&~LM: return False
    return all((bm&m)==0 or (bm&m)==bm for bm in blocks.values())
regs=set()
for e in ev:
    if pure(e[7]) and e[1]>=2*v: regs.add(e[1])
def nm(r): return 'X%d'%r if r<v else ('Y%d'%(r-v) if r<2*v else 'H%d'%r)
def pathD(r):
    c=chain[r]; return sum(g(c[i][2]-c[i-1][2]) for i in range(1,len(c)) if c[i][2]>c[i-1][2])
evr=collections.defaultdict(list)
for e in ev:
    if e[6]&LM or e[7]&LM:
        evr[e[1]].append(e)
        if e[2]!=e[1]: evr[e[2]].append(e)
tot=0
for r in sorted(regs,key=lambda r:min(e[0] for e in evr[r])):
    D=pathD(r); tot+=D
    print('%s sig%d chain %s D=%.1f'%(nm(r),dim[init[r]],[(c[2]) for c in chain[r]],D))
    for e in evr[r]:
        if e[1]==r: print('   k=%d @d%-2d f%d += %-7s %s  -> %s'%(e[0],e[4],e[3],nm(e[2]),bl(e[6]),bl(e[7])))
        else: print('   k=%d @d%-2d f%d -> %-7s gives %s'%(e[0],e[4],e[3],nm(e[1]),bl(e[6])))
print('regs',len(regs),'total D %.1f'%tot)
