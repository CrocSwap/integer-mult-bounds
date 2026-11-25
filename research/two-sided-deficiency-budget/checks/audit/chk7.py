# exact level-2 negatives needed for (4,5),(4,6): covers of S=P112\E6 by three w6 pieces + tail. Own search.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('BX_DATA', os.path.join(HERE, '..', '..', 'data', 'data.json'))
WORK = os.environ.get('BX_WORK', '.')
exec(open(os.path.join(HERE,'chk6.py')).read().split('tab=Counter()')[0])
import itertools
cnt=lambda A: np.bitwise_count(A[...,0]).astype(np.int32)+np.bitwise_count(A[...,1])
toi=lambda a: int(a[0])|(int(a[1])<<64); tom=lambda m: np.array([m&(2**64-1),m>>64],dtype=np.uint64)
TS=set()
for a in A2:
    a=np.array(a); TS.add(sum(1<<t for t in np.nonzero(~((L@a.T)==0).all(axis=1))[0].tolist()))
print('#targets',len(TS),flush=True)
def quad(Rm):
    pts=[t for t in range(112) if Rm>>t&1]; s=set(LAB[t] for t in pts)
    return any((LAB[a]^LAB[b]^LAB[c]) in s and len({LAB[a],LAB[b],LAB[c],LAB[a]^LAB[b]^LAB[c]})==4 for a,b,c in itertools.combinations(pts,3))
def tail(Rm,n3,n2):  # n3<=1 here
    r=bin(Rm).count('1')
    if r<=2*n2+3*n3: return True
    return n3==1 and r==2*n2+4 and quad(Rm)
stat=Counter(); bad=[]
for S in TS:
    s=tom(S); nS=bin(S).count('1')
    I6=cnt(M[3]&s); P6=[toi(x) for x in np.unique(M[3][I6>=18]&s,axis=0)]
    for mode in ('A','B','C'):
        if mode in 'AC' and nS!=78: continue
        tailcap={'A':12+6,'B':12+8,'C':8+4+6}[mode]
        for P,Q,Rr in itertools.combinations_with_replacement(P6,3):
            U=P|Q|Rr; R=S&~U; r=bin(R).count('1')
            if r>tailcap: continue
            stat[(mode,'triples')]+=1
            Rm=tom(R)
            if mode in 'AB':
                if int(cnt(M[4]&Rm).max())>=r-(6 if mode=='A' else 8): bad.append((mode,S,P,Q,Rr))
            else:
                # 4-flat piece: need |R∩U4|>=r-10 and tail(R\U4,1,3); 4-flats = codim5; use: lines of R in any 4-flat => enumerate subsets via 5-flats' sub-flats is costly; brute: candidate 4-flat sets = maximal R∩U4
                pts=[t for t in range(112) if R>>t&1]; found=False
                for k in range(max(0,r-10),9):
                    for sub in itertools.combinations(pts,k):
                        b=[]
                        for t in sub:
                            x=LAB[t]
                            for y in b: x=min(x,x^y)
                            if x: b.append(x)
                        if len(b)<=4 and tail(R&~sum(1<<t for t in sub),1,3): found=True; break
                    if found: break
                if found: bad.append((mode,S,P,Q,Rr))
    stat['targets']+=1
print(dict(stat),'COVERS FOUND:',len(bad),[b[0] for b in bad[:5]])
