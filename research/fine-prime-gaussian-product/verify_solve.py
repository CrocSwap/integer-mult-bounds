"""Compare the physical line schedule with independent exact matrices."""
from fractions import Fraction as F
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from itertools import product
from random import Random


from condensed import CyclicBand
from crt_route import Banks
from fine_ring import Tape, Trace
from sparse_tapes import coefficient_tape, multiply_line, solve_line, export_field


def check(actual, expected, message):
    if actual != expected:
        raise AssertionError(message)


def invert(mat):
    a = [list(row) + [F(i == j) for j in range(len(mat))] for i,row in enumerate(mat)]
    n = len(a)
    for j in range(n):
        q = a[j][j]
        a[j] = [x/q for x in a[j]]
        for i in range(n):
            if i != j:
                z = a[i][j]
                a[i] = [u-z*v for u,v in zip(a[i],a[j])]
    return [row[n:] for row in a]


def matrices(n,w):
    rng = Random(1021*n+w)
    a = [[F(0)]*n for _ in range(n)]
    r = [[F(0)]*n for _ in range(n)]
    for i,j in product(range(n),repeat=2):
        if min((i-j)%n,(j-i)%n) <= w:
            a[i][j] = F(rng.randrange(-2,4),64)
            r[i][j] = F(rng.randrange(-2,5),32)
        if i == j:
            a[i][i] = F(1)+sum(abs(x) for x in a[i])
    return a,r


def apply_matrix(mat, value):
    return [tuple(sum(v * x[j] for v,x in zip(row, value)) for j in (0,1)) for row in mat]


def sparse_pages():
    cases = products = 0
    worst = 0
    for n in [1, 2, 3, 4, 7, 11, 16, 23]:
        for w in sorted({0, min(2,n//2), n//2}):
            a,r = matrices(n,w)
            trace = Trace()
            owner = Banks(trace)
            p = 32
            rhs = [((i*105+46) << 20, (200-i*11)<<22) for i in range(n)]
            line = Tape(p+12,trace)
            for x in rhs:
                line.append(x)
            a_page = CyclicBand([enumerate(row) for row in a],w).factor(p)
            r_page = CyclicBand([enumerate(row) for row in r],w).apply_page(p)
            lo = coefficient_tape(a_page.forward,owner)
            up = coefficient_tape(a_page.backward,owner)
            rp = coefficient_tape(r_page.coefficients,owner)
            x = export_field(solve_line(line,lo,up,a_page.width,1<<p,owner))
            y = export_field(multiply_line(line,rp,r_page.offsets,1<<p,owner))
            for actual,expected in [(x,apply_matrix(invert(a),rhs)), (y,apply_matrix(r,rhs))]:
                worst=max(worst,max(abs(v-q) for av,ev in zip(actual,expected) for v,q in zip(av,ev)))
            owner.close()
            line.release()
            check(trace.live,0,"sparse primitive retained a tape")
            cases += 1
            products += trace.scalar_products
    if worst >= 32:
        raise AssertionError("excess grid error")
    print("physical cyclic pages", cases, "signed word products", products, "largest independent error <", int(worst)+1, "work-grid units")


if __name__=="__main__":
    sparse_pages()
