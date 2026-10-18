# B179 gate: replay A exactly; per S1 stopper find plane-jump op, courier u, other registers holding the l2 piece.
exec(open((__import__('os').environ['HM_ROOT']+'/cards/B98c/work/gate.py')).read().split("good=[")[0])
import pickle
NR=716
R=[({i:Q(1)} if i<112 else {}) for i in range(NR)]
C=list(d['start'])
ops=d['A']
log=[]   # (i, t, s, q, framebefore_t, frame_after_t)
rowsnap={}  # op index -> row of source (copy) for add
for i,e in enumerate(ops):
    if e[0]=='scale':
        t=e[1];q=Q(e[2],e[3]);R[t]={j:q*x for j,x in R[t].items()}
        log.append((i,t,None,q,C[t],e[4]));C[t]=e[4]
    else:
        t,s=e[1],e[2];q=Q(e[3],e[4]);f=e[5]
        rowsnap[i]=dict(R[s])
        row=R[t]
        for j,x in R[s].items():
            z=row.get(j,Q(0))+q*x
            if z:row[j]=z
            else:row.pop(j,None)
        log.append((i,t,s,q,C[t],f,C[s]));C[t]=f;C[s]=f
bad=[r for r in range(NR) if R[r]!=rows0[r]]
print('end rows mismatch vs rows0:',len(bad),bad[:10])
pickle.dump((log,rowsnap,C),open('replayA.pkl','wb'))
