# LEANTHIN lt5: CLOSED-FORM dual (KASYM chord dual + leaf multipliers mu, nu) -> certs/closed_k{k}.json (lt3 format), then lt3 verifies it exactly.
#   y_DEEP = wm ; y_{RC2,l,c=1} = w_l/(k-1) (l=3..k) ; mu (LEAFAVG) = (1-v1)/(k-1) ; nu (LC) = 1-v2p-k*mu ; all other rows 0.
import sys,json,os
import mpmath as mp
mp.mp.dps=70
s=mp.mpf(99)/100; v2p=mp.mpf(17)**s-mp.mpf(16)**s; v1=mp.mpf(9)**s-mp.mpf(8)**s; e8=mp.mpf(8)**s
def h(D): return v2p-(8*D+1)**s+e8*D
def q(D): return h(D)/D
def closed(k):
    q2,qk=q(2),q(k); sl=(qk-q2)/(k-2); T=(k-1)*sl; wm=q2-sl
    S={1:mp.mpf(0),2:mp.mpf(0),k:T}
    for D in range(3,k): S[D]=(k-1)*(q(D)-q2-sl*(D-2))/(k-D)
    w={l:S[l]-S[l-1] for l in range(3,k+1)}
    mu=(1-v1)/(k-1); nu=1-v2p-k*mu
    return wm,w,mu,nu
def HQ2(k):
    F=2*k-2+2*((8*k+1)**s-k*e8-1)-(1-v1)*k*k/(k-1)-(k-4)*(1-v2p)
    return 104*F/k
if __name__=='__main__':
    S_=110; os.makedirs('certs',exist_ok=True)
    for k in map(int,sys.argv[1:]):
        wm,w,mu,nu=closed(k)
        assert wm>=0 and mu>=0 and nu>=0 and min(w.values())>=0, (k,wm,mu,nu,min(w.values()))
        rows=[(l,c) for c in range(1,min(3,k-1)+1) for l in range(2,k+1)]
        y=[0,0]+[0]*len(rows)+[0,0,0,0]
        dy=lambda x:int(mp.floor(x*mp.mpf(2)**S_))
        y[1]=dy(wm)
        for i,(l,c) in enumerate(rows):
            if c==1 and l>=3: y[2+i]=dy(w[l]/(k-1))
        nr=len(rows); y[2+nr+1]=dy(mu); y[2+nr+2]=dy(nu)
        json.dump({'k':k,'S':S_,'y':[str(t) for t in y],'float_chat':float(HQ2(k))},open(f'certs/closed_k{k}.json','w'))
        print(k,'wm',mp.nstr(wm,6),'mu',mp.nstr(mu,6),'nu',mp.nstr(nu,6),'minw',mp.nstr(min(w.values()),5),'HQ2',mp.nstr(HQ2(k),12),flush=True)
