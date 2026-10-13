"""float screen of skel.X (same profile), for exploration only"""
import sys, math
sys.path.insert(0,'/Users/joelpulikkan/imb-main/research/format-limits/scripts')
from skel import profile
from fractions import Fraction as Fr
def Xf(s,h,k,x):
    prof,m,D=profile(s,h,k,Fr(x))
    if D<=0: return None
    m=float(m); D=float(D)
    F=lambda q: sum(float(z)*float(r)*((m/float(r))**q-1) for r,z in prof.items())
    lo,hi=0.0,0.5
    for _ in range(100):
        mid=(lo+hi)/2
        if F(mid)>=D: hi=mid
        else: lo=mid
    return hi
def Xstar(h,k,x,S=range(3,40,2)):
    best=(None,0.0)
    for s in S:
        r=Xf(s,h,k,x)
        if r and r>best[1]: best=(s,r)
    return best
if __name__=='__main__':
    for h in (3,4,5,6,7,8,9):
        print(h,[ (str(x),Xstar(h,1,x)) for x in (Fr(2,5),Fr(1,2),Fr(3,5),Fr(2,3),Fr(3,4),Fr(4,5),Fr(9,10))])
