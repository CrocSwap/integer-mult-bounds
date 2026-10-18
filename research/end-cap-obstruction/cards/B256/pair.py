from plan import *
import itertools
w=load(__import__('os').environ['EO_ROOT']+'/work/o_cf0/FULL-WORD.json.gz');M=Model(w);P=M.P;NA=len(w['A'])
g0=NA+239
cur0={r:M.frame_at(r,g0) for r in (124,125,231,283,281,591)}
print({r:len(f) for r,f in cur0.items()}, {r:[t for t in (12,13,58) if inperp(f,t,P)] for r,f in cur0.items()})
ops={'r1':(125,231),'r2':(124,231),'r3':(124,283),'r4':(125,281),'a3':(591,283),'a1':(591,281),'W':(283,281)}
# value dependency: W (283+=281) must follow r3,a3 (they read v1) ; r4,a1 read 281 only (never written) any time
before={('r3','W'),('a3','W')}
names=list(ops);good=[]
for perm in itertools.permutations(names):
    pos={n:i for i,n in enumerate(perm)}
    if any(pos[a]>pos[b] for a,b in before): continue
    cur=dict(cur0)
    for n in perm:
        t,s=ops[n];F=G.basis(list(cur[t])+list(cur[s]));cur[t]=cur[s]=F
    ok12=inperp(cur[124],12,P);ok13=inperp(cur[125],13,P);ok58=inperp(cur[591],58,P)
    # reads of 231 other users want 231 ⊆ perp36/37: check
    ok231=inperp(cur[231],36,P) and inperp(cur[231],37,P)
    good.append((ok12,ok13,ok58,ok231,perm))
import collections
print(collections.Counter(g[:4] for g in good))
print([g for g in good if all(g[:3])][:5])
