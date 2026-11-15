import jl, scan3, pricekit as pk
from collections import Counter
W=pk.load('inputs/ATTACK/STACK7616/best7616.json.gz'); M=jl.Word(W)
for STAY in (False,True):
    scan3.STAY=STAY; c=Counter()
    for m in sorted(M.mains):
        o=M.path(m)
        for gi in range(1,len(o)-1):
            P,G,N=o[gi-1],o[gi],o[gi+1]; Gops=[i for i in M.ops[m] if M.tag[i]==G]; cache={}
            miss=sum(1 for i in Gops if not scan3.opts_for(M,m,i,[P,N],M.ops[m],cache))
            c[min(miss,3)]+=1
            c['stayopts']+=sum(1 for i in Gops for x in scan3.opts_for(M,m,i,[P,N],M.ops[m],cache) if x[4])
    print('STAY',STAY,sorted(c.items(),key=str))
