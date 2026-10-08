"""Exact rational moment enclosure; adapted from retained PR18/29 arithmetic."""
from fractions import Fraction as Q
def log_upper(value):
    value = Q(value)
    assert value >= 1
    power = 0
    while value > 2:
        value /= 2
        power += 1
    def series(x):
        z = (x-1)/(x+1)
        return 2*sum((z**(2*j+1)/(2*j+1) for j in range(24)), Q(0)) + 2*z**49/(49*(1-z*z))
    scaled = (power*series(Q(2)) + series(value))*10**12
    return Q(-(-scaled.numerator//scaled.denominator), 10**12)

def moment_search(m,W,rows,denominator=10**12):
 weights={t:Q(t*n,m*W) for t,n in rows.items() if n}
 logs={t:log_upper(Q(m,t)) for t in weights}
 def bound(a):
  result=Q()
  for t,w in weights.items():
   u=a*logs[t];assert 0<=u<1
   result+=w*(1+u+u*u/(2*(1-u/3)))
  return result
 lo,hi=0,denominator//10000
 assert bound(Q(lo,denominator))<1<=bound(Q(hi,denominator))
 while hi-lo>1:
  mid=(lo+hi)//2
  if bound(Q(mid,denominator))<1:lo=mid
  else:hi=mid
 a=Q(lo,denominator);upper=bound(a)
 return dict(saving=a,moment_upper=upper,strict_gap=1-upper,next_grid=Q(hi,denominator),next_moment_upper=bound(Q(hi,denominator)),logarithm_upper_bounds=logs,grid=denominator)
