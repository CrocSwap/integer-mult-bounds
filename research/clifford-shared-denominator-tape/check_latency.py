"""Independent prefix-tree and bounded-state proofs for quotient and rounded outputs."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from denominators import require

def v2(x):
    return (x & -x).bit_length()-1


def earliest(bits):
    # Collapse consecutive equal leaves for both children of every prefix.
    level=bits
    depth=(len(level)-1).bit_length()
    while len(level)>1 and all(a==b for a,b in zip(level[::2],level[1::2],strict=True)):
        depth-=1
        level=level[::2]
    return depth


def main():
    compared=0
    for d in range(3,64,2):
        k=d.bit_length()
        require(set(range(d))=={x%d for x in range(1<<k)}, "reachable residues")
        suffix=[(r<<k)//d for r in range(d)]
        require(len(set(suffix))==d,"zero suffix distinguishes every carry")
        # Independent distinguishability of simultaneous real/imaginary carries.
        require(len({(x,y) for x in suffix for y in suffix})==d*d,"paired state")
        h=(d-1)//2
        for n in range(2,11):
            limit=1<<n
            for j in range(n):
                span=d<<j
                first=span-h
                # A bit changes at every positive multiple of span displaced by h.
                for offset in (0,h):
                    cuts=range(span-offset,limit,span)
                    claimed=n-min(map(v2,cuts)) if cuts else 0
                    observed=earliest([((x+offset)//d>>j)&1 for x in range(limit)])
                    require(claimed==observed,("latency",d,n,j,offset))
                    compared+=1
                if 0<first<limit and j>v2(h):
                    require(earliest([((x+h)//d>>j)&1 for x in range(limit)])==n-v2(h),
                            "high-bit sharp delay")
    for d in (22742436009630709072767882717680300149753125,470624175):
        k=d.bit_length()
        for j in (12,100,1000):
            n=k+j
            h=(d-1)//2
            threshold=(d<<j)-h
            require(threshold<1<<n and ((threshold+h)//d>>j)&1 and
                    (((threshold-1+h)//d>>j)&1)==0,"literal decoder boundary")
            require(((threshold-1)^threshold).bit_length()==v2(h)+1,"common prefix length")
    print("PASS",compared,"floor and nearest prefix-tree depths; paired residues, literal 1000-bit delays.")


if __name__=="__main__":
    main()
