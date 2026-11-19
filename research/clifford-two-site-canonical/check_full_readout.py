"""Full-group controls from the 12+1 decoder, symmetry, and direct rotated matrix elements."""
import json
from pathlib import Path
import subprocess
import sys
from fractions import Fraction
from double_readout import P, prepare
from flag_weights import weight
from check_double import sym


def full_checks():
    left = sym((17, 34, 129))
    right = sym((1, 131, 68, 65))
    count = 0
    numerator_gains = 0
    for S, L, R in ((P.IDENTITY, P.IDENTITY, P.IDENTITY),
                    (sym((17, 34, 68, 136)), P.IDENTITY, P.IDENTITY),
                    (sym((17, 32, 54, 99)), left, right)):
        r, c = 3, 4
        terms = [(r^1,c^3,(2,-1)), (r,c^2,(1,3)), (r^6,c,(0,7)), (r,c,(1,0))]
        first = prepare(S,r,c,[(i,k,r,c,g) for i,k,g in terms],weight,L,R)
        second = prepare(S,r,c,[(r,c,i,k,g) for i,k,g in terms],weight,L,R)
        for p in (0,16,55,127,194,241):
            expected = P.coefficient(S,p,r,c,terms,L,R)
            P.require(first(p)==second(p)==expected, "failed independently computed 12+1 limit")
            numerator_gains += int(expected != (0,0))
            count += 1
        terms2 = [(r^1,c^2,r^6,c^12,(1,3)), (r^1,c^7,r^2,c,(3,8)),
                  (r,c^2,r^6,c^12,(Fraction(1,3),1))]
        direct = prepare(S,r,c,terms2,weight,L,R)
        other = prepare(S,r,c,[(m,n,i,k,v) for i,k,m,n,v in terms2],weight,L,R)
        for p in (0,15,61,111,155,240):
            P.require(direct(p)==other(p),"independent singleton exchange")
    P.require(numerator_gains and count==18,"vacuous canonical controls")
    print("PASS 18 predecessor canonical limits in both singleton orders and 18 genuine pair exchanges.")

    query = [(1,0,0,1,(1,0))]
    got = prepare(P.IDENTITY,0,0,query,weight)(0)
    expected = Fraction(3639905331779, 47774121329355220800000)
    P.require(got == (expected,0), "identity coefficient of two changing sites")
    here = Path(__file__).resolve().parent
    run = subprocess.run([sys.executable, "-E", "-s", "-W", "error", "-B",
                          str(here/"double_readout.py"), str(here/"example.json")],
                         check=True, capture_output=True, text=True)
    P.require(json.loads(run.stdout) == [[str(expected),"0"],[str(-expected),"0"],["0","0"]],
              "published command and all three example outputs")
    print("Full-group canonical readout for E00^11, E10, E01 at the identity:", *got)


if __name__ == '__main__':
    full_checks()
