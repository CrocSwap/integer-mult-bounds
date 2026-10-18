# Generalised robust-cover DP (necessary conditions only => valid lower bound on cost(T)).
# Pieces sorted by weight desc (capacities monotone in weight). For k=1..d: deleting the d-k heaviest
# pieces leaves a span meeting D in >=k dims, so the rest must cover >= NL - N(8-k) lines
# (N(r) = max lines in an r-dim real subspace); k=1 uses exact small-cover feasibility.
import sys
def run(unit):
    if unit=='P112':
        g={1:1,2:2,3:4,4:8,5:12,6:20,7:36}; G={1:1,2:2,3:4,4:8,5:12,6:20,7:32}
        NL=112; N={0:0,1:1,2:3,3:6,4:12,5:20,6:36,7:59}; Wmax=7
        def k1(ws):
            # rest must cover Off(h): N(f_i) (56, cover>=14, 3 x w6 possible) or Off(r) (53, >=15, >=3 pieces, not all <=6)
            # or |Off|>=70 (count with g)
            W=sum(ws); sG=sum(G[w] for w in ws); sg=sum(g[w] for w in ws)
            nf= W>=14 and sG>=56
            nr= W>=15 and sG>=53 and len(ws)>=3 and not (len(ws)==3 and max(ws)<=6)
            no= W>=14 and sg>=70
            return nf or nr or no
        pairrule=True
    else:
        g={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}; G={1:1,2:2,3:4,4:8,5:12,6:20,7:32,8:56}
        NL=120; N={0:0,1:1,2:3,3:6,4:12,5:20,6:36,7:63}; Wmax=8
        E8x=eval(sys.argv[2]) if len(sys.argv)>2 else {}
        def k1(ws):
            W=sum(ws); sG=sum(G[w] for w in ws); sg=sum(g[w] for w in ws)
            has8=8 in ws
            root= sG>=57 and ((has8 and W>=9) or (not has8 and W>=E8x.get('smin',9) and len(ws)>=E8x.get('npc',2)
                     and not (len(ws)==3 and max(ws)<=6 and E8x.get('no6',False))))
            other= sg>=78 and W>=9
            return root or other
        pairrule=False
    def ok(ws,d):
        a=len(ws)
        if a<d: return False
        if pairrule and d>=2 and a<d+2: return False
        if not k1(ws[d-1:]): return False
        for k in range(2,d+1):
            if sum(g[w] for w in ws[d-k:]) < NL-N[8-k]: return False
        if d==8 and sum(g[w] for w in ws)+a<2*NL: return False
        if d==7 and sum(g[w] for w in ws)+3*a<2*(NL-1): return False
        return True
    Ws=list(range(Wmax,0,-1))
    for d in range(1,9):
        bc=[90,None]
        def rec(i,cnt,wt):
            if wt>=bc[0]: return
            if i==len(Ws):
                ws=sorted([w for w in Ws for _ in range(cnt[w])],reverse=True)
                if ok(ws,d): bc[0]=wt;bc[1]=dict((w,c) for w,c in cnt.items() if c)
                return
            w=Ws[i]
            for c in range(0,(bc[0]-wt)//w+1):
                cnt[w]=c; rec(i+1,cnt,wt+c*w)
            cnt[w]=0
        rec(0,{w:0 for w in Ws},0)
        if unit=='P112': print('P112 eps-free d',d,'DP',bc,'=> cost_w >=',64-8*d+bc[0],flush=True)
        else: print('E8 d8',d,'DP',bc,'=> E8 >=',72-9*d+bc[0],'P112 >=',72-9*d+bc[0]-8,flush=True)
run(sys.argv[1])
