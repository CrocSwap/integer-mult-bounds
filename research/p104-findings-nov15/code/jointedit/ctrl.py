import jl, scan2, pricekit as pk, sys
W=pk.load('inputs/ATTACK/STACK7616/best7616.json.gz'); M=jl.Word(W)
found=None
for m in sorted(M.mains):
    o=M.path(m)
    for P,N in zip(o,o[1:]):
        Pops=[i for i in M.ops[m] if M.tag[i]==P]
        if not Pops: continue
        i=Pops[-1]; e=M.ev[i]
        if e[0]!='ADD': continue
        p=e[2] if e[1]==m else e[1]
        if p>=M.n: continue
        for G in range(len(M.sp)):
            if M.legal(P,G) and M.legal(G,N):
                ov={i:(M.key[i],G)}
                if M.cost(M.path(m,ov)) is not None and M.cost(M.path(p,ov)) is not None:
                    found=(m,i,P,G,N,p); break
        if found: break
    if found: break
print('control edit',found)
m,i,P,G,N,p=found
W2=M.rebuild({i:(M.key[i],G)})
r=pk.replay(W2); print('replay ok',r['ok'],r['problems'][:3])
r0=pk.replay(W); print('rows equal', r['rows']==r0['rows'])
print('kappa ctrl',pk.kstr(jl.kappa(W2)['kappa'],14))
M2=jl.Word(W2); res=scan2.scan_main(M2,m)
for x in res: print(x['m'],x['G'],x['P'],x['X'],x['N'],x['d'],x['slid'])
