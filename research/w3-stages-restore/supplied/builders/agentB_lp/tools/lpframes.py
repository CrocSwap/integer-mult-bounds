import sys, pickle, collections
sys.path.insert(0,'/home/claude/work/agentB/tools')
from frames import *
L=pickle.load(open(sys.argv[1],'rb'))
ev=L['ev']; n=L['n']; dim=L['dim']; init=L['init']; chain=L['chain']
key=(int(sys.argv[2]),int(sys.argv[3]))
x,y=key
Zs=[X for (k2,X) in DBM if k2==key]
def targets_of(key,Z):
    x,y=key
    out=[]
    for z in (2*Z,2*Z+1):
        for (a,b) in ((x,y^1),(x^1,y)):
            out.append(idx[tuple(sorted((a,b,z)))])
    return out
FZ={Z:kernel_rows([ann_vec_of_target(t) for t in targets_of(key,Z)]) for Z in Zs}
mods=pickle.load(open('lpmods.pkl','rb'))['modregs'][key]
fr_seen=set()
for r in mods:
    for (k,f,d) in chain[r]:
        if 0<d<24: fr_seen.add(f)
res=[]
for f in sorted(fr_seen,key=lambda f:dim[f]):
    B=FR()[str(f)]['B']
    A=[Z for Z in Zs if contains(FZ[Z],B)]
    # which blocks' spans are inside f
    inb=[X for X in Zs if contains(B,[chi(i) for i in items(DBM[(key,X)])])]
    res.append((f,dim[f],''.join('%x'%Z for Z in A),''.join('%x'%X for X in inb),23-2*len(A)))
for r_ in res: print('frame %d dim %d  within F_Z for Z in {%s}  contains blocks {%s}  Phi-dim %d'%r_)
