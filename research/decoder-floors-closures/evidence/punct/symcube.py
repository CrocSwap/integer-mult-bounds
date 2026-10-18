"""PUNCT6 symmetry-reduced cube split of rkd_T_P.cnf. Stab(F*) on lines = W_J (reflections in lines of F*; -1 acts trivially on lines).
Level 1: s1 = first line outside F*. Solution S, option o of s1 -> g in Stab(F*,s1) maps (S,o) to (gS,g o), still a solution of the same CNF
(frames, card, bad-ness are W-invariant, F* fixed). So WLOG o in a set of orbit reps. Cubes: [S_s1] and [z_rep] for each rep.
usage: symcube.py typ P  -> cube/s_T_P_{name}.cnf, prints list. (optionally 2nd level for the S_s1 cube: depth 2 splits line s2.)"""
import sys, numpy as np
sys.path.insert(0,'/Users/mason/repo_clones/intmult-work/cards/PUNCT4')
from p4lib import G, FLATREP, L
from sympy.combinatorics import Permutation, PermutationGroup
typ,P=int(sys.argv[1]),int(sys.argv[2])
flat=FLATREP[typ][1]
idx={}
for t in range(120): idx[tuple(L[t])]=t; idx[tuple(-L[t])]=t
def refl(r):
    p=[]
    for t in range(120):
        v=L[t]-2*(L[t]@L[r])//(L[r]@L[r])*L[r] if (2*(L[t]@L[r]))%(L[r]@L[r])==0 else None
        assert v is not None
        p.append(idx[tuple(v)])
    return p
gens=[Permutation(refl(r)) for r in range(120) if flat[r]]
Wj=PermutationGroup(gens); print('|W_J| =',Wj.order())
out=[s for s in range(120) if not flat[s]]
fn=f'cnf/rkd_{typ}_{P}.cnf'
lines=open(fn).read().split('\n'); hdr=lines[0].split(); nv=int(hdr[2]); cl=[l for l in lines[1:] if l.strip()]
zset={}
for l in cl:
    v=[int(x) for x in l.split()[:-1]]
    if len(v)==2 and v[0]<0 and v[0]<-120: zset.setdefault(-v[0],set()).add(v[1]-1)
heads=[[int(x) for x in l.split()[:-1]] for l in cl if len(l.split())>5 and int(l.split()[0])>0 and int(l.split()[0])<=120]
head={h[0]-1:h[1:] for h in heads}
def orbit_reps(group,s):
    st=group.stabilizer(s)
    zs=head[s]; sets={frozenset(zset[z]):z for z in zs}
    seen=set(); reps=[]
    for fs,z in sets.items():
        if fs in seen: continue
        reps.append(z); orb={fs}; fr=[fs]
        while fr:
            x=fr.pop()
            for g in st.generators:
                y=frozenset(g(t) for t in x)
                if y not in orb: orb.add(y); fr.append(y)
        assert all(o in sets for o in orb)
        seen|=orb
    return st,reps
def write(name,units):
    open(f'cube/{name}.cnf','w').write(f'p cnf {nv} {len(cl)+len(units)}\n'+'\n'.join(cl+[f'{u} 0' for u in units])+'\n')
s1=out[0]
st,reps=orbit_reps(Wj,s1)
print('s1',s1,'|Stab|',st.order(),'options',len(head[s1]),'orbit reps',len(reps))
names=[]
write(f's_{typ}_{P}_in',[s1+1]); names.append(f's_{typ}_{P}_in')
for z in reps:
    n=f's_{typ}_{P}_z{z}'; write(n,[z]); names.append(n)
# depth 2 on the S_{s1} cube: split on s2 (first out line != s1), modulo st
if len(sys.argv)>3:
    s2=[s for s in out if s!=s1][int(sys.argv[3])]
    st2,reps2=orbit_reps(st,s2) if False else (None,None)
open(f'cube/s_{typ}_{P}.list','w').write('\n'.join(names)+'\n'); print(len(names),'cubes')
