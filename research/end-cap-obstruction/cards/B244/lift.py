import json,collections
import ev
from ev import *
T0=[list(e) for e in TAIL0]
p0,fr0=profile(T0);k0=kappa(p0)
out=[]
for k,e in enumerate(T0):
    cands={full}|{end[q] for q in regs(e)}|{B(fr0[j]+fr0[k]) for j in range(k+1,len(T0)) if set(regs(T0[j]))&set(regs(e))}
    for U in cands:
        if U==fr0[k]:continue
        fl=[None]*len(T0);fl[k]=U
        p,_=profile(T0,fl)
        if p is None:continue
        out.append((float(kappa(p)-k0),k,len(U),p))
out.sort(key=lambda x:-x[0]);print(len(out),out[:5])
# lift groups: all gates touching a register chain simultaneously: lift every gate to end of... skip
