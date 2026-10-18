import sys,pickle,collections
sys.path.insert(0,__import__('os').environ['EO_ROOT']+'/cards/B251')
from ev import *
res=pickle.load(open('resp.pkl','rb'));Yev=pickle.load(open('yevp.pkl','rb'))
Y,adj=pickle.load(open('graph.pkl','rb'))
Ls=build_events()[1]
def members(b):
    s={0}
    for x in b:s|={y^x for y in s}
    m=0
    for y in s:m|=1<<y
    return m
mm={}
def mem(b):
    if b not in mm:mm[b]=members(b)
    return mm[b]
FULLM=(1<<512)-1
inc=[]
for k,ev,col,chi,nh,carr in res:
    if k==():continue
    for c in range(chi):
        evs=[a for a in ev if col[a]==c]
        t=[Yev[a][0] for a in evs]
        L=0;cap=FULLM
        for a in evs:
            L|=mem(Y[a][0] and Ls[Y[a][0]]) if False else 0
        Lb=[]
        for a in evs:Lb+=list(Ls[Yev[a][0]])
        Lbasis=B(Lb)
        for a in evs:
            cap&=mem(end[Yev[a][2][1]])
        inc.append(dict(first=min(t),last=max(t),Lm=mem(Lbasis),cap=cap,k=k,chi=chi,nh=len([r for r in nh if r<224 or r in w['centers']]),
                        car=sorted({Yev[a][2][2] for a in evs}),tg=sorted({Yev[a][2][1] for a in evs}),Ldim=len(Lbasis)))
print(len(inc),'incarnations; L not inside own cap:',sum(1 for i in inc if i['Lm']&~i['cap']))
pickle.dump(inc,open('inc.pkl','wb'))
