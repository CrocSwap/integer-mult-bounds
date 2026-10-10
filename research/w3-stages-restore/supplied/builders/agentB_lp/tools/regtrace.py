import sys, pickle, collections
sys.path.insert(0,'/home/claude/work/agentB/tools')
from base import *
L=pickle.load(open(sys.argv[1],'rb'))
ev=L['ev']; n=L['n']; dim=L['dim']; init=L['init']; chain=L['chain']
# generic content descriptor: express as LP outputs, LP blocks, faces etc. relative to nothing (global)
LPS={}
for key in LINEKEYS:
    for X in range(12):
        if (key,X) in DBM: LPS[lp_mask(key,X)]=(key,X)
def gdesc(m):
    if m==0: return '0'
    if m in LPS: return 'LP%s/%d'%(LPS[m][0],LPS[m][1])
    # line restricted
    for key,lm in LINEMASK.items():
        if m&~lm==0:
            Xs=sorted(X for (k2,X),bm in DBM.items() if k2==key and bm&m==bm)
            rest=m
            for X in Xs: rest&=~DBM[(key,X)]
            return 'line%s blocks{%s}%s'%(key,''.join('%x'%X for X in Xs),'+%d'%popc(rest) if rest else '')
    return '%d items'%popc(m)
def nm(r): return 'X%d'%r if r<v else ('Y%d'%(r-v) if r<2*v else 'H%d'%r)
regs=[int(x) for x in sys.argv[2:]]
evr=collections.defaultdict(list)
for e in ev:
    evr[e[1]].append(e)
    if e[2]!=e[1]: evr[e[2]].append(e)
for r in regs:
    print('%s sig%d chain %s'%(nm(r),dim[init[r]],[(c[0],c[2]) for c in chain[r]]))
    for e in evr[r]:
        if e[1]==r: print('   k=%d @d%-2d += %-7s %s  -> %s'%(e[0],e[4],nm(e[2]),gdesc(e[6]),gdesc(e[7])))
        else: print('   k=%d @d%-2d -> %-7s gives %s'%(e[0],e[4],nm(e[1]),gdesc(e[6])))
