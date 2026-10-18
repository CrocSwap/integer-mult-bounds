import os
"""Solve partial cells from the ported base word state (own rows applied, entrance frames included)."""
import sys,json,gzip,time;sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from pipeline import *
from template import zcopy
import template as TP
rd=lambda p:json.loads(gzip.decompress(open(p,'rb').read()))
def restr(x):
    if x<120:return x-8
    if x<240:return 112+(x-120-8)
    return 224+(x-240)
def gk_basis(F):return basis(list(F))
def ported_state(PW,upto,skip=()):
    Pp=PW['ports'];Rr=PW['report']['R'];nreg=224+Rr
    cur={r:((Pp[r],) if r<112 else ((basis(PW['start_extra'][str(r)]) if str(r) in PW.get('start_extra',{}) else ()) if r>=224 else ())) for r in range(nreg)}
    lev={int(t):basis(E) for t,E in PW.get('target_levels',{}).items()}
    for e in PW['A']:
        for r in ([e[1]]+([e[2]] if e[0]=='add' else [])):cur[r]=basis(e[-1])
    for t in range(112):cur[112+t]=lev.get(t,())
    for e in PW['B'][:upto]:
        if e[0]=='add' and (e[1],e[2]) in skip:continue
        for r in ([e[1]]+([e[2]] if e[0]=='add' else [])):cur[r]=basis(e[-1])
    return cur
def setup(d,W,n,PW,key):
    K=key_parts(d,W,key);dele=segment(d,W,K);sym,bad=symbolic(W,K,dele,n);assert not bad
    own={t:d['own_rows'][t][0] for t in K['targets']}
    atoms=K['atoms'];Ys=[v+t for t in K['targets']]
    zc=zcopy(W,K);z=atoms[4]
    ownset={(v+t,own[t]) for t in K['targets']}
    k0=next(k for k in dele if not (W[k][0]=='add' and (W[k][1],W[k][2]) in ownset))
    g0=W[k0];kz=next(i for i,e in enumerate(PW['B']) if e[0]=='add' and e[1]==restr(g0[1]) and e[2]==restr(g0[2]) and e[3]==g0[3] and e[4]==g0[4])
    # end of segment in ported word: last gate touching any atom/target/copy among deleted ones -> approximate by last read of copies/targets
    imgs={(restr(W[k][1]),restr(W[k][2]),W[k][3],W[k][4]) for k in dele if W[k][0]=='add'}
    kend=max(i for i,e in enumerate(PW['B']) if e[0]=='add' and (e[1],e[2],e[3],e[4]) in imgs)
    import os
    skip={(restr(v+t),restr(own[t])) for t in K['targets']} if os.environ.get('PCELL_MOVEOWN') else set()
    c0=ported_state(PW,kz,skip);cE=ported_state(PW,kend+1)
    Pp=PW['ports']
    hyp=lambda t:perpP(Pp[t])
    return K,dele,sym,own,c0,cE,kz,kend
_pc={}
def perpP(p):
    if p not in _pc:_pc[p]=basis([x for x in range(1,512) if (x&p).bit_count()%2==0])
    return _pc[p]
def solve_key(d,W,n,PW,key,nh=1,L=20,tl=600,maxh=1):
    K,dele,sym,own,c0,cE,kz,kend=setup(d,W,n,PW,key)
    atoms=K['atoms'];Ys=[v+t for t in K['targets']];na=5;ny=4
    Pp=PW['ports']
    regsR=[restr(x) for x in atoms]+[restr(y) for y in Ys]
    allT=list(range(112))
    pat={}
    for t in allT:
        hp=perpP(Pp[t]);k2=tuple(0 if inside(c0[x],hp) else 1 for x in regsR)
        pat.setdefault(k2,[]).append(t)
    ownT=[y-v-8 for y in Ys]
    okF=lambda F,ts:all(inside(F,perpP(Pp[t])) for t in ts)
    others=[ts for k2,ts in pat.items() if any(k2) and not any(t in ownT for t in ts)]
    keep=[ts for ts in others if okF(cE[restr(K['M'])],ts) or any(okF(cE[restr(y)],ts) for y in Ys)]
    bits=[[t] for t in ownT]+keep
    tm=lambda F:sum(1<<b for b,ts in enumerate(bits) if any(not inside(F,perpP(Pp[t])) for t in ts))
    zc=zcopy(W,K)
    hregs=[zc]+([[c for c in K['copies'] if c!=zc][int(os.environ.get('PCELL_H2','0'))]] if nh>1 else [])
    zreaders=[K['targets'].index(t) for t in K['targets'] if any(e[0]=='add' and e[1]==v+t and e[2]==zc for e in W)]
    # role order y0..y3 = targets ordered by own atom a1,a0,a3,a2
    want=[atoms[1],atoms[0],atoms[3],atoms[2]];order=[next(t for t in K['targets'] if own[t]==w) for w in want]
    Ys=[v+t for t in order];regsR=[restr(x) for x in atoms]+[restr(y) for y in Ys];ownT=[t-8 for t in order]
    hroles={}
    for hi,hr in enumerate(hregs):
        hroles[hi]=[order.index(t) for t in K['targets'] if any(e[0]=='add' and e[1]==v+t and e[2]==hr for e in W)]
    zroles=hroles[0]
    bits=[[t] for t in ownT]+keep
    T0=[tm(c0[x]) for x in regsR[:na]]+[tm(c0[restr(h)]) for h in hregs]+[tm(c0[x]) for x in regsR[na:]]
    gm=lambda s:sum(1<<j for j in s)
    ai={a:i for i,a in enumerate(atoms)}
    S0Y=[0]*4 if os.environ.get('PCELL_MOVEOWN') else [1<<ai[own[t]] for t in order]
    goalY=[gm(sym[y]) for y in Ys];Mg=gm(sym[K['M']])
    later={x for e in W[dele[-1]+1:] for x in ((e[1],e[2]) if e[0]=='add' else (e[1],))}
    hosts=[i for i,a in enumerate(atoms) if a==K['M'] or a not in later]
    t=time.time()
    st,sol=solve(na,ny,goalY,Mg,hosts,T0,L=L,time_limit=tl,yy=False,ne=len(bits)-ny,hostallow=tm(cE[restr(K['M'])]),Yallow=[tm(cE[restr(y)]) for y in Ys],nh=nh,maxh=maxh,S0Y=S0Y,hreads=hroles)
    names=['a%d'%i for i in range(na)]+['h%d'%i for i in range(nh)]+['y%d'%i for i in range(ny)]
    return st,(None if not sol else [(names[a],names[b]) for a,b in sol]),dict(hregs=hregs,hroles=hroles,zroles=zroles,order=order,T0=T0,S0Y=S0Y,goalY=goalY,Mg=Mg,hosts=hosts,nbits=len(bits),secs=time.time()-t,targets=K['targets'],own=own)
if __name__=='__main__':
    d,P,W,n=load(__import__('os').environ['PC_CENSUS'],__import__('os').environ['PC_PROTO'])
    PW=rd(__import__('os').environ['PC_PORTED'])
    key=eval(sys.argv[1]);nh=int(sys.argv[3]) if len(sys.argv)>3 else 1;st,sol,info=solve_key(d,W,n,PW,key,tl=float(sys.argv[2]),nh=nh,maxh=nh)
    print(key,st,info);print('SOL',sol)
