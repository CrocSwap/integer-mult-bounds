"""Separate exact checks for critical mass, phase cutoffs and the block producer."""

from fractions import Fraction as Q
from functools import cache
from itertools import product
from math import isqrt
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from interchange import Port, atom_width, block_word, fixed_block_word


def require(ok, label):
    if not ok:
        raise ValueError(label)


def tree_checks():
    # sqrt ranks 1, 4 and 9 give an exactly critical profile at 1/2.
    entries = ((1, Q(1)), (4, Q(3,4)), (9, Q(1,2)))
    mass = sum(weight for _, weight in entries)
    require(sum(isqrt(r)*c for r,c in entries) == 4 and mass > 1, "critical moment")
    @cache
    def visit(n):
        if n < 16:
            return Q(0), Q(1)
        branches = [(weight,visit(rank*(n//16))) for rank,weight in entries]
        return 1+sum(c*pair[0] for c,pair in branches), sum(c*pair[1] for c,pair in branches)
    for n in range(1, 2050):
        internal, leaves = visit(n)
        require(leaves == 1+(mass-1)*internal and leaves**2 <= n, "critical tree mass")
    # Two body factors per ordinary root compound on e_(j+1)=e_j^2.
    width = 4
    cost = isqrt(width)
    for _ in range(12):
        next_width = width**2
        cost = 2*isqrt(next_width//width)*cost
        width = next_width
    require(cost == 4096*isqrt(width), "critical constant loss")


def geometry_checks():
    # Use a different calculation from the stream routing code.
    count = 0
    for p,g,s in product((1,2,5,19,41), repeat=3):
        for e in (16,31,64):
            for u in (1,2,3):
                active = 3**(2*u)
                U = p*g*s*active
                parent = max(3**(2*e), (U+2)//3)
                J = 12
                largest = max(p,g,s)
                slab = (U//largest)*(-(-largest//min(largest,J)))
                require(2*slab <= parent, "failed geometric volume bound")
                count += 1
    require(3**(2*8) == 3**6*3**6*3**(2*2), "width-only counterexample")
    # Repeatedly scanning an uncontracted parent for many short requests is expensive.
    for V in (256,512,1024,2048):
        requests = V//64
        require(requests*64 == V and V*requests == V**2//64, "parking counterexample")
    return count


def width_checks():
    # Exact logarithms for the threshold imposed by one high matrix.
    H = 296630000000000
    require(Q(2*H,1)/(1-Q(99,100)) == 59326000000000000, "A stock threshold")
    require((1-Q(1,250))/(1-Q(99,100)) == Q(498,5), "threshold ratio")
    # The final neutral block can contain a fixed fraction of the main block.
    for m in (2,4,11):
        t = Q(2*m+1, 2)
        e = int(t**10000)
        # t^9999-1 <= ceil(e^(9999/10000)) <= t^9999+1 follows by the mean value theorem.
        bound = t**9999
        require((m+Q(1,3))*(bound+1) < e < (m+Q(2,3))*(bound-1),
                "ragged neutral remainder")
    # Probe the shipped issuer at the actual exponent without allocating q^(2e) bits.
    for e in (3000,4000,7000):
        u = atom_width(e,9999,10000)
        require(u < e and (u-1)**10000 < e**9999 <= u**10000, "integer atom rule")
        full = Port(2,e,2,3,5)
        issuer = block_word(9999,10000)(full, None)
        start = 0
        for request in issuer:
            length = min(u,e-start)
            child = request.port
            require(child.width == length and child.volume == full.volume, "complete block request")
            require(child.prefix == 2*2**start and child.gap == 3*2**(e-length)
                    and child.suffix == 5*2**(e-start-length), "ragged boundary address")
            start += length
        require(start == e and e % u > 0, "missing remainder")


def fixed_count_checks():
    checked = 0
    for e in range(2, 514):
        for k in (2, 3, 7):
            port = Port(2, e, 1, 3, 2)
            token = object()
            issuer = fixed_block_word(k)(port, token)
            widths = []
            try:
                request = next(issuer)
                while True:
                    width = request.port.width
                    require(request.source is token and request.port.volume == port.volume,
                            "fixed block lost the previous complete return")
                    require(0 < width < e and request.port.gap >= 2, "missing free spectator")
                    widths.append(width)
                    token = object()
                    request = issuer.send(token)
            except StopIteration as end:
                require(end.value is token, "last block output was discarded")
            require(len(widths) <= k and sum(widths) == e and max(widths) == (e+k-1)//k,
                    "incomplete fixed-count decomposition")
            require(((max(widths)+2)//3) == (e+3*k-1)//(3*k), "composed ceiling")
            checked += 1
    return checked


if __name__ == "__main__":
    tree_checks()
    shapes = geometry_checks()
    width_checks()
    fixed = fixed_count_checks()
    print(f"PASS_WIDTH_BOUNDS tree_widths=2049 volume_shapes={shapes} block_policies=3 "
          f"fixed_count_shapes={fixed}")
