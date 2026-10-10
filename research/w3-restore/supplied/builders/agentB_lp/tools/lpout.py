import sys, pickle, collections
sys.path.insert(0,'/home/claude/work/agentB/tools')
from base import *
L=pickle.load(open(sys.argv[1],'rb'))
ev=L['ev']; n=L['n']; dim=L['dim']; init=L['init']; chain=L['chain']
LPS={}
for key in LINEKEYS:
    for X in range(12):
        if (key,X) in DBM: LPS[lp_mask(key,X)]=(key,X)
def nm(r): return 'X' if r<v else ('Y' if r<2*v else 'H')
holders=collections.defaultdict(set)   # (key,Z) -> set of regs that hold exactly it at some time
gives=collections.defaultdict(list)
for e in ev:
    if e[7] in LPS: holders[LPS[e[7]]].add(e[1])
    if e[6] in LPS: gives[LPS[e[6]]].append(e)
print('outputs held',len(holders),'given',len(gives))
cnt=collections.Counter(len(x) for x in holders.values()); print('holders per output',sorted(cnt.items()))
pat=collections.Counter()
for o,es in gives.items():
    s=tuple(sorted('%s@%d'%(nm(e[1]),e[4]) for e in es))
    pat[s]+=1
for s,c in pat.most_common(30): print(c,s)
