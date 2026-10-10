import sys, pickle, collections
sys.path.insert(0,'/home/claude/work/agentB/tools')
from base import *
L=pickle.load(open(sys.argv[1],'rb'))
ev=L['ev']; n=L['n']; dim=L['dim']; init=L['init']; chain=L['chain']
blockof={}
for (key,X),bm in DBM.items(): blockof[bm]=(key,X)
def pureline(m):
    # returns key if m is nonempty union of full blocks of a single line
    if m==0: return None
    for key,lm in LINEMASK.items():
        if m&~lm==0:
            for (k2,X),bm in DBM.items():
                if k2==key and (bm&m) and (bm&m)!=bm: return None
            return key
    return None
# find module registers per line: registers (helpers) that at some time hold pure-line content
memo={}
def pl(m):
    if m in memo: return memo[m]
    r=pureline(m); memo[m]=r; return r
modregs=collections.defaultdict(set); regline={}
for e in ev:
    if e[1]>=2*v:
        k=pl(e[7])
        if k is not None:
            modregs[k].add(e[1]); regline.setdefault(e[1],set()).add(k)
multi=[r for r,s in regline.items() if len(s)>1]
print('module regs',len(regline),'multi-line regs',len(multi))
def pathD(r):
    c=chain[r]; return sum(g(c[i][2]-c[i-1][2]) for i in range(1,len(c)) if c[i][2]>c[i-1][2])
# classify
cat=collections.Counter(); catD=collections.Counter(); chains=collections.Counter()
for r in regline:
    c=[x[2] for x in chain[r]]
    s=dim[init[r]]
    if s>0: t='sig%d'%s
    elif len(c)>1 and c[1]==1: t='plane(start1)'
    elif len(c)>1 and c[1]==3: t='blockcopy(start3)'
    else: t='other(start%d)'%(c[1] if len(c)>1 else -1)
    cat[t]+=1; catD[t]+=pathD(r)
    chains[(t,tuple(c))]+=1
for t in cat: print(t,cat[t],'D %.0f'%catD[t],'avg %.1f'%(catD[t]/cat[t]))
print('total D %.0f'%sum(catD.values()))
for (t,c),k in chains.most_common(40): print(k,t,c,'%.1f'%sum(g(c[i]-c[i-1]) for i in range(1,len(c)) if c[i]>c[i-1]))
pickle.dump(dict(modregs=dict(modregs),regline=regline),open('lpmods.pkl','wb'))
