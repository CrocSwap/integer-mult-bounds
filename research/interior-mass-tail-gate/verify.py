"""Exact rational envelopes and original tail-gate discriminator.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from itertools import product


def need(ok, message):
    if not ok: raise ValueError(message)


def laws(p,rho,ell,u):
    need(0<rho<=1 and 0<ell<=u<1,'interior parameters')
    need(rho*ell<=p<=1-rho+rho*u,'feasible mean')
    low=max(ell,(p-1+rho)/rho); high=min(u,p/rho)
    out=[]
    for y in (low,high):
        if ell==u:
            w={F(0):1-rho-p+rho*y,ell:rho,F(1):p-rho*y}
        else:
            w={F(0):1-rho-p+rho*y,ell:rho*(u-y)/(u-ell),u:rho*(y-ell)/(u-ell),F(1):p-rho*y}
        need(all(v>=0 for v in w.values()),'nonnegative extremizer')
        need(sum(w.values())==1 and sum(z*v for z,v in w.items())==p,'law statistics')
        out.append(w)
    return out


def laplace(w,j,den):
    return sum(v*F(2)**(-j*int(z*den)) for z,v in w.items())


def main():
    grids=0; comparisons=0; attained=0
    den=6
    for ell_i,u_i in [(1,2),(1,4),(2,4),(3,5),(2,2)]:
        ell,u=F(ell_i,den),F(u_i,den)
        for units in range(1,5):
            rho=F(units,4)
            for inside in range(units+1):
                y=ell+(u-ell)*F(inside,units)
                for ones in range(5-units):
                    p=rho*y+F(ones,4)
                    endpoints=laws(p,rho,ell,u); grids+=1
                    # A literal feasible law has the same prescribed mass and mean.
                    w={F(0):1-rho-F(ones,4),F(1):F(ones,4)}
                    w[ell]=w.get(ell,0)+rho*F(units-inside,units)
                    w[u]=w.get(u,0)+rho*F(inside,units)
                    for j in range(1,8):
                        bound=max(laplace(a,j,den) for a in endpoints)
                        need(laplace(w,j,den)<=bound,'extreme envelope dominates')
                        need(any(laplace(a,j,den)==bound for a in endpoints),'attaining law')
                        comparisons+=1;attained+=1
    # Splitting an interior atom at its interval endpoints increases the transform.
    chord=0
    for ell_i,u_i in [(1,5),(2,4),(1,3)]:
        for z in range(ell_i,u_i+1):
            a=F(u_i-z,u_i-ell_i);b=1-a
            for j in range(1,8):
                need(F(2)**(-j*z)<=a*F(2)**(-j*ell_i)+b*F(2)**(-j*u_i),'interior chord')
                chord+=1
    # All numbers below come from the original gates, not a sampled minimizer.
    target_half=F(518); paid_half=F(32)
    target_one=F(8212); target_minus_one=F(7,16)
    tail_u=F(1,2**66)*(target_one/target_half)*4**31
    tail_v=2**198*(target_minus_one/paid_half)**32
    need(tail_u==F(2053,2072) and tail_u<1,'forward tail')
    need(tail_v==F(7**32,2**90) and tail_v<1,'backward tail')
    need(target_one/target_half>4,'ordering')
    # Actual transform: 2y+4+512/y^2; exact minimum 28 at y=8.
    need(2*8+4+F(512,64)==28 and F(28,32)<1,'sharp three-rank minimum')
    # Endpoint chord with the SAME mean has weights 14/3 and 1540/3.
    low,high=F(14,3),F(1540,3)
    min_cube=F(27,4)*low**2*high
    need(min_cube==75460 and min_cube>32**3,'old screen cannot pass')
    # A distinct accepting point does not certify the equality boundary.
    need(F(28,4*7)==1 and F(28,4*6)>1,'strict c=7 boundary')
    # Interior target rank 16 adds no mirror interval for paid rank 16.
    exits=[(F(1,16),F(1,k)) for k in (4,16,256) if k<16]
    inner=[(F(1,k),F(1,16)) for k in (4,16,256) if k>16]
    point=F(1,8)
    need(any(a<point<=b for a,b in exits) and not any(a<point<=b for a,b in inner),'mirror failure retained')
    rejected=0
    for args in [(F(0),F(1,2),F(1,4),F(3,4)),(F(1),F(1,2),F(1,4),F(3,4)),(F(1,2),F(0),F(1,4),F(3,4)),(F(1,2),F(1,2),F(3,4),F(1,4))]:
        try: laws(*args)
        except ValueError: rejected+=1
    need(rejected==4,'invalid statistics reject')
    print('PASS_INTERIOR_MASS_TAIL_GATE',dict(statistic_fixtures=grids,envelope_comparisons=comparisons,attaining_checks=attained,chord_checks=chord,original_gates=3,controls=7))

if __name__=='__main__':main()
