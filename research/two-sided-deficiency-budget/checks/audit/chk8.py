# fast exact level-2 check. Modes: A=(4,4,4,3,0^3)@78, C=(4,4,4,2,1,0^3)@78, B80=(4,4,4,3,0^4)@80 [all need 3 disjoint 20-pieces], B78=(4,4,4,3,0^4)@78
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('BX_DATA', os.path.join(HERE, '..', '..', 'data', 'data.json'))
WORK = os.environ.get('BX_WORK', '.')
import sys
exec(open(os.path.join(HERE,'chk7.py')).read().split('stat=Counter()')[0])
mode_set=sys.argv[1]; lim=int(sys.argv[2]) if len(sys.argv)>2 else 10**9
def rk(sub):
    b=[]
    for t in sub:
        x=LAB[t]
        for y in b: x=min(x,x^y)
        if x: b.append(x)
    return len(b)
def tailC(R):   # R = 8 in a 4-flat + zero-sum quad + 3 pairs, |R|=18 exactly -> need rank-4 8-subset and quad in rest
    pts=[t for t in range(112) if R>>t&1]
    for sub in itertools.combinations(pts,8):
        if rk(sub)<=4 and tail(R&~sum(1<<t for t in sub),1,3): return True
    return False
def pieces(S,thr=18):
    s=tom(S); I6=cnt(M[3]&s); P=np.unique(M[3][I6>=thr]&s,axis=0); return P,cnt(P)
def disjoint_triples(P20,first=False):   # all i<j<k with pairwise disjoint pieces (vectorised); returns (triples, #disjoint pairs)
    def disj(i):
        q=P20[i]; js=np.nonzero(((P20[:,0]&q[0])==0)&((P20[:,1]&q[1])==0))[0]; return js[js>i]
    trip=[]; npairs=0
    for i in range(len(P20)):
        Ji=disj(i); npairs+=len(Ji)
        for j in Ji:
            for k in np.intersect1d(Ji,disj(j)):
                trip.append((i,int(j),int(k)))
                if first: return trip,npairs
    return trip,npairs
def pair_triples(S,P):   # B78 logic: triples of pieces (sizes >=18) whose union covers all but a small remainder; returns (remainders, #pairs with union>=38)
    ints=[toi(x) for x in P]; out=[]; npairs=0
    for i in range(len(P)):
        js=np.nonzero(cnt(P[i]|P)>=38)[0]; js=js[js>=i]; npairs+=len(js)
        for j in js:
            U=ints[i]|ints[j]; Rest=tom(S&~U); need=bin(S&~U).count('1')-20
            ks=np.nonzero(cnt(P&Rest)>=need)[0]; ks=ks[ks>=j]
            for k in ks: out.append(S&~(U|ints[k]))
    return out,npairs
# POSITIVE CONTROL: the full P112 (not inside a complement of E6) has 20-line 6-flat pieces and disjoint triples of them; both finders must find them.
Pf,szf=pieces((1<<112)-1); P20f=Pf[szf==20]
ctl_t,ctl_p=disjoint_triples(P20f,first=True)
print('control: 20-line pieces in P112',len(P20f),'disjoint pairs seen before the first triple',ctl_p,'triple found',len(ctl_t),flush=True)
assert len(P20f)>0 and ctl_p>0 and len(ctl_t)>0, 'positive control failed (disjoint-triple finder)'
i0,j0,k0=ctl_t[0]; Sctl=toi(P20f[i0])|toi(P20f[j0])|toi(P20f[k0]); Pc,_=pieces(Sctl)
rem,pc=pair_triples(Sctl,Pc)
print('control: |S|=%d, pieces %d, pair finder: pairs %d, covering triples %d'%(bin(Sctl).count('1'),len(Pc),pc,len(rem)),flush=True)
assert len(rem)>0 and pc>0, 'positive control failed (pair finder)'
stat=Counter(); bad=0; done=0
for S in sorted(TS):
    nS=bin(S).count('1')
    if done>=lim: break
    if mode_set in ('A','C') and nS!=78: continue
    if mode_set=='B80' and nS!=80: continue
    if mode_set=='B78' and nS!=78: continue
    done+=1
    P,sz=pieces(S)
    if mode_set in ('A','C','B80'):
        P20=P[sz==20]; ints=[toi(x) for x in P20]
        trip,npairs=disjoint_triples(P20); stat['pieces20']+=len(P20); stat['disjoint_pairs']+=npairs
        for i,j,k in trip:
            stat['disjoint20triples']+=1; R=S&~(ints[i]|ints[j]|ints[k])
            if mode_set in ('A','B80'):
                if int(cnt(M[4]&tom(R)).max())>=bin(R).count('1')-(6 if mode_set=='A' else 8): bad+=1
            else:
                if tailC(R): bad+=1
    else:
        rems,npairs=pair_triples(S,P); stat['pieces18+']+=len(P); stat['pairs_union38']+=npairs
        for R in rems:
            stat['triples']+=1
            if int(cnt(M[4]&tom(R)).max())>=bin(R).count('1')-8: bad+=1
npc=stat['pieces20'] if mode_set in ('A','C','B80') else stat['pieces18+']
npp=stat['disjoint_pairs'] if mode_set in ('A','C','B80') else stat['pairs_union38']
print(mode_set,'targets',done,'pieces enumerated',npc,'pairs enumerated',npp,dict(stat),'COVERS FOUND',bad,flush=True)
assert done>0 and npc>0, 'non-vacuity assertion failed (no targets/pieces enumerated); the finders are validated by the positive control above'
