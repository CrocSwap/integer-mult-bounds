"""KASYM ka5: verify the closed-form CHORD dual for the reduced LP (n=2k-2 roles D>=2, mains=2k, RC2_l l=3..k) in mpmath dps 60.
 q(D)=h(D)/D, h(D)=v2p-(8D+1)^s+8^s D ; chord l(D) through (2,q2),(k,qk); G=q-l
 S(D)=(k-1)G(D)/(k-D) (2<=D<=k-1), S(k)=T=(k-1)(qk-q2)/(k-2); w_l=S(l)-S(l-1); wm=q2-(qk-q2)/(k-2); M=v2p.
Checks: min w_l, wm; EXHAUSTIVE DP over all (D,P,mf), P any partition of D (parts<=D), phi computed from ROW DEFINITIONS; B vs HP(k).
usage ka5.py k.."""
import sys,mpmath as mp
mp.mp.dps=60
s=mp.mpf(99)/100;v2p=mp.mpf(17)**s-mp.mpf(16)**s;e8=mp.mpf(8)**s
def h(D):return v2p-(8*D+1)**s+e8*D
def q(D):return h(D)/D
def dual(k):
    q2,qk=q(2),q(k);sl=(qk-q2)/(k-2);T=(k-1)*sl;wm=q2-sl
    S={1:mp.mpf(0),2:mp.mpf(0),k:T}
    for D in range(3,k):S[D]=(k-1)*(q(D)-q2-sl*(D-2))/(k-D)
    w={l:S[l]-S[l-1] for l in range(3,k+1)}
    return w,wm,T
def check(k):
    w,wm,T=dual(k);n=2*k-2
    suf={};acc=mp.mpf(0)
    for l in range(k+1,1,-1):suf[l]=acc;acc+=w.get(l,0)   # suf[D]=sum_{l>D} w_l
    pre={0:mp.mpf(0)};acc=mp.mpf(0)
    for l in range(1,k+1):acc+=w.get(l,0);pre[l]=acc     # pre[x]=sum_{3<=l<=x} w_l
    M=None;arg=None
    for D in range(2,k+1):
        # piece score from row definitions: RC2_l deep (l<=D): L(k-L)/(k-1)[L<l]; shallow (l>D): (D^2-sum L^2)/(k-1)
        g=[None]+[-(8*L)**s+L*(k-L)*(pre[D]-pre[L])/(k-1)-suf[D]*L*L/(k-1) for L in range(1,D+1)]
        const=(8*D+1)**s+suf[D]*D*D/(k-1)
        for mf in (0,1):
            gg=list(g);gg[1]=gg[1]+mf*wm
            best=[mp.mpf(0)]+[None]*D
            for d in range(1,D+1):best[d]=max(best[d-L]+gg[L] for L in range(1,d+1))
            sc=best[D]+const
            if M is None or sc>M:M,arg=sc,(D,mf)
    B=n*M-2*k*sum(w.values())-2*k*wm
    HP=2*((k-2)*v2p+(8*k+1)**s-k*e8)
    print('k %d  min w_l %s  wm %s  max phi - v2p = %s at %s  104B/k = %s  HP = %s  B-HP = %s'%(k,mp.nstr(min(w.values()),6),mp.nstr(wm,6),mp.nstr(M-v2p,3),arg,mp.nstr(104*B/k,12),mp.nstr(104*HP/k,12),mp.nstr(B-HP,3)),flush=True)
if __name__=='__main__':
    for k in [int(a) for a in sys.argv[1:]]:check(k)
