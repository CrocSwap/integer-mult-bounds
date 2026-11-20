"""Compare the block construction with the Gaussian on original padded coordinates."""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"certified-gaussian-recovery"))

from fractions import Fraction
from gaussian_pages import require
from gauged_circulants import build_circulant
from intervals import Interval, exp_negative, pi_interval


def position(s,t,j):
    return (2*t*j+s)//(2*s)


def source_term(kind,s,t,alpha,k,j,h,grid):
    rho=Fraction(t,s)
    beta=rho*j-position(s,t,j)
    if kind=="broad":
        return exp_negative(pi_interval(grid)*((h+beta)/rho/alpha)**2)/alpha
    return exp_negative(pi_interval(grid)*(alpha**2*((h+beta)**2-beta**2)))


def fixture(kind,s,t,alpha,B,W,q):
    grid=q+70
    holes=set(range(t))-{position(s,t,j) for j in range(s)}
    selected={position(s,t,j):j for j in range(s)}
    edge=frozenset(i for i in range(t)
                   if any(k in holes for k in range(i//B*B,i//B*B+B))
                   or i%B<W or (B-1-i%B)<W)
    blocks={}
    bad=[]
    for start in range(0,t,B):
        if any(i in holes for i in range(start,start+B)):
            try:
                build_circulant(s,t,alpha,start,B,W,q,kind)
            except ValueError:
                bad.append(start)
            else:
                raise ValueError("bad block was accepted")
        else:
            blocks[start//B]=build_circulant(s,t,alpha,start,B,W,q,kind)
    max_error=wrong=0
    e_pairs=matches=0
    for i in range(t):
        for j in range(t):
            bi,bj=i//B,j//B
            jei=blocks[bi].entry(i%B,j%B) if bi==bj and bi in blocks else Fraction(int(i==j),1)
            h=next((v for v in range(-W,W+1) if (i+v)%t==j),None)
            # independent global signed-distance truncation with arbitrary hole columns
            if j not in selected or (kind=="narrow" and i not in selected):
                exact=Interval.rational(int(i==j),grid)
            elif h is None:
                exact=Interval.rational(0,grid)
            else:
                exact=source_term(kind,s,t,alpha,i,selected[j],h,grid)
            if bi==bj and bi in blocks and h is not None and j-i==h:
                # The global reference uses the SAME rational gauge products for these entries.
                ref=jei
                permuted=blocks[bi].entry(j%B,i%B)
                wrong=max(wrong,abs(permuted-Fraction(exact.lo,1<<grid))-Fraction(exact.hi-exact.lo,1<<grid))
            else:
                ref=Fraction((exact.lo+exact.hi)*(1<<q)//(2*(1<<grid)),1<<q)
            diff=max(abs(ref-Fraction(exact.lo,1<<grid)),abs(ref-Fraction(exact.hi,1<<grid)))
            bound=blocks[bi].row_defect if bi in blocks and bi==bj and h is not None and j-i==h else Fraction(2,1<<q)
            require(diff<=bound,"direct original-coordinate exponent outside generated bound")
            max_error=max(max_error,diff)
            if ref!=jei:
                require(i in edge and j in edge,"difference escaped E x E")
                e_pairs+=1
            else:
                matches+=1
    require(len(blocks)>=1 and bad and wrong>Fraction(1,10000),"nontrivial scope and sign controls")
    print(kind,s,t,"pure, bad",len(blocks),len(bad),"equal, corrected pairs",matches,e_pairs,
          "largest error",float(max_error),"transpose error lower",float(wrong))
    return len(blocks),len(bad),matches,e_pairs


if __name__=="__main__":
    for s,t in ((31,32),(61,64)):
        for kind in ("broad","narrow"):
            fixture(kind,s,t,2,8,2,112)
