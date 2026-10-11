from kern3 import *
def rand_plan(col,first,C,cand,Es,rnd):
    R=len(col);free=set(range(R));groups=[]
    Eorder=Es[:]
    while True:
        opts=[]
        for E in Eorder:
            G=[h for h in cand[E] if h in free]
            if len(G)<2:continue
            rk=np.linalg.matrix_rank(C[:,G]);pv=len(G)-rk
            if pv>0:opts.append((pv,E,G))
        if not opts:break
        # pick randomly weighted by pivots
        tot=sum(o[0] for o in opts);x=rnd.random()*tot;acc=0
        for o in opts:
            acc+=o[0]
            if acc>=x:pick=o;break
        pv,E,G=pick
        donors=[];rows=np.zeros((v,0));Gs=G[:];rnd.shuffle(Gs)
        for h in Gs:
            c=C[:,h:h+1]
            if np.linalg.matrix_rank(np.hstack([rows,c]))>rows.shape[1]:rows=np.hstack([rows,c]);donors.append(h)
        pivots=[h for h in G if h not in donors]
        groups.append((E,donors,pivots));free-=set(G)
    # completion: free helpers that can pivot onto existing classes
    for h in sorted(free):
        for gi,(E,donors,pivots) in enumerate(groups):
            if not span(E)<=span(first[h]):continue
            M=np.hstack([C[:,donors],C[:,h:h+1]])
            if np.linalg.matrix_rank(M)==len(donors):pivots.append(h);free.discard(h);break
    return groups
if __name__=='__main__':
    w=load();w['R']=w['report']['R'];col,first=setup(w);R=len(col)
    cand={}
    for h,F in first.items():
        for E in subspaces(F):cand.setdefault(E,[]).append(h)
    C=np.zeros((v,R))
    for h in range(R):
        for t,x in col[h].items():C[t,h]=float(x)
    Es=[E for E,G in cand.items() if len(G)>=2 and len(G)-np.linalg.matrix_rank(C[:,G])>0]
    best=0;bg=None
    for seed in range(300):
        rnd=random.Random(seed);g=rand_plan(col,first,C,cand,Es,rnd)
        tot=sum(len(p)*len(E) for E,d,p in g)
        if tot>best:best=tot;bg=g;print(seed,tot,[(E[0],len(d),len(p)) for E,d,p in g],flush=True)
    import pickle;pickle.dump(bg,open('kern4_best.pkl','wb'))
