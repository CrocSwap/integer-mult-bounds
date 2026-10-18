"""E7 (alpha-perp, 63 lines): 7-frames, min hitting set (kissat+drat-trim for the UNSAT bound), z-set sizes for the codim-2 check."""
import sys, itertools, subprocess; sys.path.insert(0,'.')
from anal import *
a=0; K0=[t for t in ORTH[a]]; Km=sum(1<<t for t in K0)
frames=[]
def rec(cl,cand):
    if len(cl)==7: frames.append(tuple(cl)); return
    for i,t in enumerate(cand):
        rec(cl+[t],[s for s in cand[i+1:] if G[t,s]==0])
rec([],K0); print('7-frames in E7:',len(frames))
# codim-2 check data: for z killing rad (Om(z,16)=0) not in U_K0^perp, |K0 cap O_z|
perp=set(z for z in range(512) if (Km & OZ[z])==0)
sz=sorted(set(bin(Km&OZ[z]).count('1') for z in range(1,512) if z not in perp and Om(z,16)==0))
print('|K0 cap O_z| values (z killing rad):',sz)
# max lines of E7 in a rank-5 subspace: from rank-5 K0-cap-F sets (lower bound) -- report
from flats import TYPES, MASKS
best=0
for m in MASKS:
    s=Km&m
    c=bin(s).count('1')
    if c>best and c<=36 and span_rank(bits(s))==5: best=c
print('max |E7 cap F| of rank 5 among K0-cap-F:',best)
# min hitting set of frames: CNF "|S'|<=k and every frame hit"
from pysat.card import CardEnc, EncType
for k in range(8,13):
    cls=[[t+1 for t in f] for f in frames]
    top=63
    vm={t:i+1 for i,t in enumerate(K0)}
    cls=[[vm[t] for t in f] for f in frames]
    enc=CardEnc.atmost(lits=list(range(1,64)),bound=k,top_id=63,encoding=EncType.seqcounter)
    allc=cls+enc.clauses; nv=max(63,enc.nv)
    fn=f'cnf/e7hit_{k}.cnf'; import os; os.makedirs('cnf',exist_ok=True)
    with open(fn,'w') as f:
        f.write(f'p cnf {nv} {len(allc)}\n'); [f.write(' '.join(map(str,c))+' 0\n') for c in allc]
    r=subprocess.run(['kissat','-q',fn,f'cnf/e7hit_{k}.drat','--no-binary'],capture_output=True,text=True)
    st='SAT' if r.returncode==10 else ('UNSAT' if r.returncode==20 else str(r.returncode))
    ver=''
    if st=='UNSAT':
        v=subprocess.run(['/Users/mason/repo_clones/intmult-work/tmp_dratchk/drat-trim/drat-trim',fn,f'cnf/e7hit_{k}.drat'],capture_output=True,text=True,timeout=1200)
        ver='VERIFIED' if 's VERIFIED' in v.stdout else 'NOT VERIFIED'
    print('frame hitting with <=',k,'punctures:',st,ver,flush=True)
    if st=='SAT': break
