"""KASYM ka4: 'flat singleton-hub' dual for the reduced LP: all (D,1^D,mf=1) tight at M=v2p, sigma free. Check w>=0 and DP max."""
import sys,numpy as np
s=.99;v2p=17**s-16**s
def dual(k,sig):
    # unknowns: wm, T. R(D)=v2p-(8D+1)^s+D*8^s-sig*D(D-1)/2-D*wm ; D=k: k*T=R(k); D=2: S(2)=0 => R(2)=2T/(k-1)
    h=lambda D:v2p-(8*D+1)**s+D*8**s-sig*D*(D-1)/2
    # k T = h(k) - k wm ; h(2) - 2 wm = 2T/(k-1)
    A=np.array([[k,k],[2,2/(k-1)]]);b=np.array([h(k),h(2)]);wm,T=np.linalg.solve(A,b)
    S=np.zeros(k+1)
    for D in range(3,k):S[D]=(h(D)-D*wm-D*(D-1)*T/(k-1))*(k-1)/(D*(k-D))
    S[k]=T;w=np.diff(S)[2:]  # w_l = S(l)-S(l-1) for l=3..k
    return wm,T,S
def check(k,sig):
    wm,T,S=dual(k,sig);w=np.zeros(k+2);w[3:k+1]=S[3:k+1]-S[2:k]
    M=-1e9;arg=None
    for D in range(2,k+1):
        Lm=min(D,k-2);Ls=np.arange(1,Lm+1,dtype=float)
        Wsh=w[D+1:k+1].sum();Wdeep=np.array([w[int(x)+1:D+1].sum() for x in Ls])
        g=-(8*Ls)**s-sig*Ls*Ls/2+Wdeep*Ls*(k-Ls)/(k-1)-Wsh*Ls*Ls/(k-1);g[0]+=max(wm,0)
        const=(8*D+1)**s+sig*D*D/2+Wsh*D*D/(k-1)
        best=np.full(D+1,-np.inf);best[0]=0;ar=np.zeros(D+1,int)
        for d in range(1,D+1):
            m=min(d,Lm);c=best[d-np.arange(1,m+1)]+g[:m];i=int(c.argmax());best[d]=c[i];ar[d]=i+1
        if best[D]+const>M:
            M=best[D]+const;P=[];d=D
            while d>0:P.append(int(ar[d]));d-=ar[d]
            arg=(D,tuple(sorted(P)))
    n=2*k-2;B=n*M-sig*k*(k-1)-2*k*T-2*k*wm
    return wm,T,w[3:k+1].min(),M-v2p,arg,104*B/k
for k in [int(a) for a in sys.argv[1:]]:
    for sig in [0.0,0.0005/k,0.05/k,0.1/k,0.15/k]:
        wm,T,wmin,ex,arg,c=check(k,sig);print(k,'sig*k %.3f wm %.4f T %.4f minw %.2e M-v2p %.2e arg %s c %.4f'%(sig*k,wm,T,wmin,ex,str(arg)[:40],c))
