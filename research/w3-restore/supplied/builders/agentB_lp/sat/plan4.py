# Plan for designs with optional sigma>0 fresh registers (meet4 JSON). Exchange-based groups; dirt tracked.
import json, sys, math
g=lambda r: r*math.log(120/r) if r>0 else 0.0
def make_plan(path,mode='exch'):
    D=json.load(open(path)); n=10
    regs=[d['r'] for d in D]; byr={d['r']:d for d in D}
    T=max(h[0] for h in D[0]['hist'])
    sig={r:bool(byr[r].get('sig',False)) for r in regs}
    K0={}
    for r in regs:
        if byr[r]['R']: K0[r]=frozenset([r])
        elif sig[r]: K0[r]=frozenset(int(c) for c in byr[r]['hist'][0][1])
        else: K0[r]=frozenset()
    K=dict(K0)
    C={r:(frozenset([r]) if byr[r]['R'] else (frozenset(['d%d'%r]) if sig[r] else frozenset())) for r in regs}
    rounds=[]
    for t in range(1,T+1):
        edges=[(r,s) for r in regs for s in byr[r]['hist'][t][4]]
        par={r:r for r in regs}
        def f(x):
            while par[x]!=x: par[x]=par[par[x]]; x=par[x]
            return x
        if mode=='sat':
            for r in regs:
                for s in byr[r]['hist'][t][3]: par[f(r)]=f(s)
        else:
            for r,s in edges: par[f(r)]=f(s)
        comps={}
        for r in regs:
            if mode=='sat':
                if byr[r]['hist'][t][3]: comps.setdefault(f(r),[]).append(r)
            elif any(r in e for e in edges): comps.setdefault(f(r),[]).append(r)
        groups=[]; newC=dict(C)
        for root,mem in comps.items():
            KU=frozenset().union(*[K[r] for r in mem])
            adds=[(r,s) for (r,s) in edges if r in mem]
            for r in mem: K[r]=KU
            for r,s in adds: newC[r]=newC[r]^C[s]
            groups.append(dict(K=sorted(KU),members=sorted(mem),adds=adds))
        C=newC; rounds.append(groups)
    ok=True
    for r in regs:
        d=byr[r]
        if d['tgt'] in K[r] or d['tgt'] in K0[r]: ok=False; print('target contaminated',r)
        if not frozenset(x for x in C[r] if isinstance(x,int))<=K[r]: ok=False; print('content outside',r)
    for z in range(n):
        O=[r for r in regs if byr[r]['role']=='O' and byr[r]['tgt']==z][0]
        M=[r for r in regs if byr[r]['role']=='M' and byr[r]['tgt']==z][0]
        if C[O]^C[M]!=frozenset(range(n))-{z}: ok=False; print('bad final',z,sorted(map(str,C[O]^C[M])))
    total=0; per={}
    for r in regs:
        d=byr[r]; seq=[]
        for t,groups in enumerate(rounds,1):
            for gr in groups:
                if r in gr['members']:
                    if not seq or seq[-1]!=tuple(gr['K']): seq.append(tuple(gr['K']))
        if d['R']: dims=[3]
        elif sig[r]: dims=[2*len(K0[r])+1]
        else: dims=[0]
        for Kk in seq:
            dm=2*len(Kk)+1
            if dm>dims[-1]: dims.append(dm)
        tail=[21,22,24] if d['role']=='O' else [21,24]
        for dm in tail:
            if dm>dims[-1]: dims.append(dm)
        c=sum(g(dims[i]-dims[i-1]) for i in range(1,len(dims)))
        per[r]=(c,dims,seq); total+=c
    info={r:dict(R=byr[r]['R'],role=byr[r]['role'],tgt=byr[r]['tgt'],sig=sig[r],K0=sorted(K0[r])) for r in regs}
    return dict(n=n,regs=regs,info=info,rounds=rounds,per=per,total=total,ok=ok)
if __name__=='__main__':
    P=make_plan(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else 'exch')
    print('ok',P['ok'],'total %.1f'%P['total'])
    for r in P['regs']: print(r,P['info'][r],'%.1f'%P['per'][r][0],P['per'][r][1])
    for t,gr in enumerate(P['rounds'],1):
        print('round',t)
        for x in gr: print('   K=%s members=%s adds=%s'%(''.join(map(str,x['K'])),x['members'],x['adds']))
