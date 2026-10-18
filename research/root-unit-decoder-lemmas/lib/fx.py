import math
def idle_slots(K,a):
    sl=[]
    if 2*K-2>0: sl.append(a*(2*K-2))
    for p in range(1,K):
        sl+=[2*p*a,a]
        if 2*K-2*p-2>0: sl.append(a*(2*K-2*p-2))
    return sl
def slots(s,h,x,k=1):
    K=(s-1)//2; a=h-k; m=k+s*a; S=[]
    S.append((a,2*s*a)); S.append((h,s*x))
    for r in idle_slots(K,a): S.append((max(r,h),2*r))
    return [(c,ms) for c,ms in S if c<m and ms>0], m, (s-1)*k-s*x
def Xf(s,h,x,k=1):
    S,m,D=slots(s,h,x,k)
    if D<=0: return 0.0
    f=lambda q: sum(ms*((m/c)**q-1) for c,ms in S)-D
    lo,hi=0.0,0.5
    for _ in range(80):
        mid=(lo+hi)/2
        if f(mid)<0: lo=mid
        else: hi=mid
    return hi
def best(h,x,ss=range(3,41,2)):
    return max((Xf(s,h,x),s) for s in ss)
