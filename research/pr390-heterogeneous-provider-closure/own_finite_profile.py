"""Own exact integer verifier; reads data, never imports source programs."""
import json
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def check_profile():
    p=json.loads((ROOT/'PROFILE.json').read_text())
    h={int(r):n for r,n in p['global']['histogram'].items()}
    u={int(r):n for r,n in p['global']['integer_root_upper'].items()}
    assert h=={1:630027,2:173088,3:150912,4:31392,5:61920,6:95616,
               7:16704,8:29952,9:2304,16:15360,32:15360,48:15360}
    m,W,B=73,58899,1<<32
    target=m*(1<<32768)
    tests=[]
    for r in sorted(h):
        assert r*u[r]**1024>=target
        assert r*(u[r]-1)**1024<target
        tests.append({'rank':r,'root_upper':u[r],'upper_inequality':True,
                      'preceding_integer_fails':True})
    mu=Fraction(sum(h[r]*r*u[r] for r in h),W*m*B)
    eps=1-mu
    assert mu<1
    assert [mu.numerator,mu.denominator]==p['global']['moment_upper']
    assert [eps.numerator,eps.denominator]==p['global']['moment_gap']
    assert sum(h.values())==p['global']['children']==1237995
    assert sum(r*n for r,n in h.items())==p['global']['rank_mass']==4289643
    assert m*W-sum(r*n for r,n in h.items())==p['global']['deficit']==9984
    G=1<<(36*36)
    for j in range(1,37):G*=(1<<(2*j))-1
    L=G*W;R=G*(W+793);a=(L-1).bit_length();B0=16*(a+m+10)**2
    boundary=288*(240+2+480)+15360+W
    Mpass=8*sum(h.values())+4*boundary
    Spass=288*165748+4*69120+8*15360+4*793*288
    E=1+Mpass+Spass+16*sum(h.values())
    A=(1<<24)*(m+1)**6*(R+1)*(G*(E+W+(W+793))+1)+(1<<(m*m+20))*(m+1)**6
    assert (Mpass,Spass,E)==(11032740,49048320,79888981)
    assert (a,B0,A.bit_length())==(p['global']['a'],p['global']['B0'],p['global']['A_bits'])
    return {'status':'OWN_INTEGER_PROFILE_PASS','integer_root_checks':tests,
      'moment_upper':[mu.numerator,mu.denominator],
      'moment_gap':[eps.numerator,eps.denominator],
      'a':a,'B0':B0,'A_bits':A.bit_length(),
      'Mpass':Mpass,'Spass':Spass,'E':E,
      'scope':'Exact finite arithmetic only; no all-size physical, RAM or Lean proof by execution.'}

if __name__=='__main__':
    print(json.dumps(check_profile(),indent=2))
