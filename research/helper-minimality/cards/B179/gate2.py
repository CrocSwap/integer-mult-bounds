exec(open((__import__('os').environ['HM_ROOT']+'/cards/B179/gate.py')).read().split("bad=[")[0])
def spanset(basis):
    s={0}
    for b in basis: s|={x^b for x in s}
    return s
# need start-of-run state to find jumps: replay again with checks per op
R2=[({i:Q(1)} if i<112 else {}) for i in range(NR)]
C2=list(d['start'])
st=d['start']
# stoppers per block via blockscan logic, using end-of-A cur
cur=C  # end-of-A frames
info={}
for bn,rr in blocks.items():
    scr=list(rr); cols=sorted({j for r in scr for j in rows0[r]})
    if len(cols)!=8: continue
    vec={l:F.fr[st[l]][0] for l in cols}
    def hull(pts):
        sp=spanset([vec[p] for p in pts]); return frozenset(l for l in cols if vec[l] in sp)
    regsb=cols+scr
    Bd={r:frozenset(l for l in cols if vec[l] in spanset(F.fr[cur[r]])) for r in regsb}
    H={r:hull(rows0[r].keys()) if rows0[r] else frozenset() for r in regsb}
    planes=[r for r in regsb if len(H[r])==4 and Bd[r]==H[r]]
    info[bn]=(cols,scr,planes,vec,H,Bd)
stop={z:bn for bn,(c,s,p,vec,H,Bd) in info.items() for z in p}
seen={}
jumps={}   # z -> (opidx, partner, frame_before_z, frame_after, rowpartner, role)
def pts(fid,cols,vec):
    sp=spanset(F.fr[fid]);return frozenset(l for l in cols if vec[l] in sp)
snapshots={}
for i,e in enumerate(ops):
    if e[0]=='scale':
        t=e[1];q=Q(e[2],e[3]);R2[t]={j:q*x for j,x in R2[t].items()};C2[t]=e[4];continue
    t,s,q,f=e[1],e[2],Q(e[3],e[4]),e[5]
    for z,oth in ((t,s),(s,t)):
        if z in stop and z not in jumps:
            bn=stop[z];cols,scr,pl,vec,H,Bd=info[bn]
            pa=pts(f,cols,vec)
            if pa>=H[z] and len(pts(C2[z],cols,vec))<=2 and pts(C2[z],cols,vec)<=H[z] or (pa>=H[z] and len(pts(C2[z],cols,vec))<4 and z not in jumps and False):
                jumps[z]=(i,oth,C2[z],f,dict(R2[oth]),'z=target' if z==t else 'z=source')
                snapshots[z]=([dict(r) for r in R2],list(C2))
    row=R2[t]
    for j,x in R2[s].items():
        zz=row.get(j,Q(0))+q*x
        if zz:row[j]=zz
        else:row.pop(j,None)
    C2[t]=f;C2[s]=f
print('stoppers',len(stop),'with jump found',len(jumps))
def prop(a,b):
    if not a or not b or set(a)!=set(b):return False
    k=next(iter(a));r=a[k]/b[k]
    return all(a[j]==r*b[j] for j in a)
res=[]
from itertools import combinations
for z,(i,u,fz,fa,ru,role) in sorted(jumps.items()):
    bn=stop[z];cols,scr,pl,vec,H,Bd=info[bn]
    Rs,Cs=snapshots[z]
    # holders of l2 piece (proportional to partner row, before op), other than z,u
    holders=[r for r in range(NR) if r not in(z,u) and prop(Rs[r],ru)]
    ok=[r for r in holders if F.sub(fz,Cs[r]) and F.sub(Cs[r],fa)]    # frame within [frame z before, plane]
    low=[r for r in holders if F.sub(Cs[r],fa)]
    # does u hold a nonzero row?
    res.append((bn,z,i,u,role,len(pts(fz,cols,vec)),len(ru),len(holders),len(low),len(ok),[(r,len(pts(Cs[r],cols,vec))) for r in holders][:6]))
for r in res: print(r)
print('count ok>0:',sum(1 for r in res if r[9]>0),'holders>0:',sum(1 for r in res if r[7]>0),'low>0:',sum(1 for r in res if r[8]>0),'of',len(res))
print('--- escape 2: point holders')
n_any=n_all=0;n_noclimb=0
for z,(i,u,fz,fa,ru,role) in sorted(jumps.items()):
    Rs,Cs=snapshots[z]
    per=[]
    for j in ru:
        h=[r for r in range(NR) if r not in(z,u) and set(Rs[r])=={j}]
        per.append(h)
    anyh=all(per)
    lowh=all([r for r in h if F.sub(Cs[r],fa)] for h in per)
    nocl=all([r for r in h if F.sub(Cs[r],fa) and F.sub(fz,Cs[r])] for h in per)
    n_any+=anyh;n_all+=lowh;n_noclimb+=nocl
    if anyh and z in list(jumps)[:6]: print(z,per)
print('all columns have a pure point holder:',n_any,'inside plane:',n_all,'no-climb (frame>=z frame):',n_noclimb,'of',len(jumps))
