# Print LP module of a line in lattice terms: frames as s{S} (span) or P{A} (Phi), events.
import sys, pickle, collections
sys.path.insert(0,'/home/claude/work/agentB/tools')
from lattice import *
L=pickle.load(open(sys.argv[1],'rb'))
ev=L['ev']; n=L['n']; dim=L['dim']; init=L['init']; chain=L['chain']
key=(int(sys.argv[2]),int(sys.argv[3]))
Xs=line_blocks(key)
FZ={Z:kernel_rows(phi_ann(key,[Z])) for Z in Xs}
blockrows={X:[chi(i) for i in items(DBM[(key,X)])] for X in Xs}
mods=pickle.load(open('lpmods.pkl','rb'))['modregs'][key]
lab_of={}
def flabel(f):
    if f in lab_of: return lab_of[f]
    d=dim[f]
    if d==0: s='0'
    elif d==24: s='FULL'
    else:
        B=FR()[str(f)]['B']
        A=[Z for Z in Xs if contains(FZ[Z],B)]
        inb=[X for X in Xs if contains(B,blockrows[X])]
        hx=lambda Ss: ''.join('%x'%x for x in Ss)
        if d==2*len(inb)+1 and inb: s='s{%s}'%hx(inb)
        elif d==23-2*len(A) and A: s='P{%s}'%hx(A)
        else: s='d%d[A=%s,S=%s]'%(d,hx(A),hx(inb))
    lab_of[f]=s; return s
LM=LINEMASK[key]
blocks={X:DBM[(key,X)] for X in Xs}
def bl(m):
    m2=m&LM
    full=sorted(X for X,bm in blocks.items() if bm&m2==bm)
    part=[X for X,bm in blocks.items() if bm&m2 and bm&m2!=bm]
    s='{%s}'%''.join('%x'%X for X in full)
    if part: s+='+p%d'%len(part)
    ext=popc(m&~LM)
    if ext: s+='+ext%d'%ext
    return s
def nm(r): return 'X%d'%r if r<v else ('Y%d'%(r-v) if r<2*v else 'H%d'%r)
evr=collections.defaultdict(list)
for e in ev:
    if e[6]&LM or e[7]&LM:
        evr[e[1]].append(e)
        if e[2]!=e[1]: evr[e[2]].append(e)
for r in sorted(mods,key=lambda r:min(e[0] for e in evr[r])):
    c=chain[r]
    D=sum(g(c[i][2]-c[i-1][2]) for i in range(1,len(c)) if c[i][2]>c[i-1][2])
    print('%s sig%d D=%.1f  %s'%(nm(r),dim[init[r]],D,' -> '.join('%s(%d)'%(flabel(x[1]),x[2]) for x in c)))
    for e in evr[r]:
        if e[1]==r: print('     %-14s += %-7s %s -> %s'%(flabel(e[3]),nm(e[2]),bl(e[6]),bl(e[7])))
        else: print('     %-14s -> %-7s gives %s'%(flabel(e[3]),nm(e[1]),bl(e[6])))
