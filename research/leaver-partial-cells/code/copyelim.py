import pickle,json,sys,math
from collections import Counter,defaultdict
from fractions import Fraction as Q
sys.path.insert(0,sys.path[0])
from rawframes import basis,inside,hyper,FULL
v=120
def replay(W,P,nreg,check=True):
    used=set()
    for e in W:
        used.add(e[1])
        if e[0]=='add':used.add(e[2])
    cur=[(p,) for p in P]+[()]*(nreg-len(P));H=Counter();bad=[]
    for k,e in enumerate(W):
        regs=(e[1],e[2]) if e[0]=='add' else (e[1],)
        G=basis(list(e[-1])+[x for r in regs for x in cur[r]])
        for r in regs:
            if v<=r<2*v and not inside(G,hyper(P[r-v])):bad.append((k,r));
            dr=len(G)-len(cur[r])
            if dr:H[dr]+=1
            cur[r]=G
    for r in range(nreg):
        if r>=2*v and r not in used:continue
        T=hyper(P[r-v]) if v<=r<2*v else FULL
        if not inside(cur[r],T):bad.append(('final',r));continue
        dr=len(T)-len(cur[r])
        if dr:H[dr]+=1
    return H,bad
def rows_of(W,nreg):
    rows=[{r:Q(1)} if r<v else {} for r in range(nreg)]
    for e in W:
        if e[0]=='add':
            t,s,q=e[1],e[2],Q(e[3],e[4])
            for j,x in list(rows[s].items()):
                z=rows[t].get(j,Q(0))+q*x
                if z:rows[t][j]=z
                else:rows[t].pop(j,None)
        else:
            t,q=e[1],Q(e[2],e[3]);rows[t]={j:q*x for j,x in rows[t].items()}
    return rows
# price: excess cost of a profile delta at b (κ-proxy): sum dH_r * r*((73/r)^b-1)  (lower is better)
def fee(dH,b=0.0016741854766740864):
    return sum(n*r*((73/r)**b-1) for r,n in dH.items())
def copies(W):
    """helpers born by a single copy h += 1*a (h empty)."""
    born={};out=[]
    first={}
    for k,e in enumerate(W):
        for r in ((e[1],e[2]) if e[0]=='add' else (e[1],)):
            first.setdefault(r,k)
    for k,e in enumerate(W):
        if e[0]=='add' and e[1]>=2*v and first[e[1]]==k and Q(e[3],e[4])==1:out.append((e[1],e[2],k))
    return out
def try_elim(W,h,a,kc):
    """remove copy event kc (h+=a); redirect reads of h to a, moving each read to just after kc if a is written
    between kc and the read. Readers must be Y targets (commutative adds) and h must have no other writes."""
    ev=[(k,e) for k,e in enumerate(W) if k!=kc and (e[1]==h or (e[0]=='add' and e[2]==h))]
    if any(e[1]==h for k,e in ev):return None,'h written'
    if any(not (v<=e[1]<2*v) for k,e in ev):return None,'non-Y reader'
    wa=[k for k,e in enumerate(W) if e[1]==a and k>kc]
    moves={}
    for k,e in ev:
        nxt=min([x for x in wa],default=10**9)
        if nxt<k:
            # Y reader e[1] must not be a source in (kc,k)
            y=e[1]
            if any(ee[0]=='add' and ee[2]==y for ee in W[kc:k]):return None,'Y read between'
            moves[k]=kc  # place right after the copy position
        else:moves[k]=None
    NW=[];pend=defaultdict(list)
    for k,e in ev:
        if moves[k] is not None:pend[moves[k]].append(['add',e[1],a,e[3],e[4],[]])
    for k,e in enumerate(W):
        if k==kc:
            NW.extend(pend[kc]);continue
        if k in moves:
            if moves[k] is None:NW.append(['add',e[1],a,e[3],e[4],[]])
            continue
        NW.append(e)
    return NW,'ok'
if __name__=='__main__':
    d=pickle.load(open(sys.argv[1],'rb'));P=json.load(open(sys.argv[2]))['binary_ports']
    W=[list(e) for e in d['A']+d['B']];n=240+d['NH']
    # strip stored frames of target reads so joins are minimal? keep stored frames (they are minimal joins for reads)
    H0,b0=replay(W,P,n);assert not b0
    R0=rows_of(W,n)
    res=[]
    for h,a,kc in copies(W):
        NW,why=try_elim(W,h,a,kc)
        if NW is None:res.append((h,a,kc,why,None));continue
        H,b=replay(NW,P,n)
        if b:res.append((h,a,kc,'frame %s'%(b[:1],),None));continue
        R=rows_of(NW,n)
        if any(R[r]!=R0[r] for r in range(v,2*v)):res.append((h,a,kc,'Y rows differ',None));continue
        dH=Counter(H);dH.subtract(H0);dH={r:x for r,x in dH.items() if x}
        res.append((h,a,kc,'OK',dH))
    c=Counter(x[3].split(' ')[0] for x in res);print(c)
    ok=[x for x in res if x[4] is not None]
    for x in sorted(ok,key=lambda x:fee(x[4]))[:40]:print(x[0],x[1],x[2],x[4],'%.5f'%fee(x[4]))
    pickle.dump(res,open(sys.argv[3],'wb'))
