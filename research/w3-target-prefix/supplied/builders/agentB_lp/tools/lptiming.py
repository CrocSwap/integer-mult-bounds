import sys, pickle, collections
sys.path.insert(0,'/home/claude/work/agentB/tools')
from base import *
L=pickle.load(open(sys.argv[1],'rb'))
ev=L['ev']; n=L['n']; dim=L['dim']; init=L['init']; chain=L['chain']
mods=pickle.load(open('lpmods.pkl','rb'))['modregs']
rows=[]
for key in LINEKEYS[:132]:
    regs=mods[key]
    LM=LINEMASK[key]
    # plane registers: chains starting with step to 1
    planes=[r for r in regs if len(chain[r])>1 and chain[r][1][2]==1]
    # time plane complete: last event where plane reg receives into dim-3 frame with content = one full block
    comp=[]
    for r in planes:
        ks=[e[0] for e in ev if e[1]==r and e[4]<=3]
        comp.append(max(ks) if ks else -1)
    firstmod=min(e[0] for e in ev if (e[1] in regs or e[2] in regs) and e[4]>=3 and ((e[1] not in planes) or e[4]>3) and (e[6]&LM) and e[6]&~LM==0 and popc(e[6])>=4)
    lastfwd=max(e[0] for e in ev if (e[1] in regs or e[2] in regs) and e[4]<24)
    rows.append((key,max(comp),firstmod,lastfwd))
rows.sort(key=lambda x:x[2])
for r in rows[:5]+rows[-5:]: print(r)
print('lines where planes complete after first module event:',sum(1 for r in rows if r[1]>r[2]))
print('min first',min(r[2] for r in rows),'max lastfwd',max(r[3] for r in rows), 'max planecomplete',max(r[1] for r in rows))
