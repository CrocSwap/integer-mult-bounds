"""Check the square-axis controller, direct CRT character and resource powers."""

from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
from math import gcd, isqrt, prod
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from heterogeneous_crt import HeterogeneousCRT, local_switch_row
from square_geometry import (controller_shape, number_of_axes, production_widths,
                             select_squares, square_interval, widths)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def square_families():
    rows = 0
    maximum_classes = 0
    geometries = ((2, 18), (4, 24), (8, 32), (16, 32), (32, 40),
                  (64, 40), (128, 48), (256, 52), (512, 56))
    for (d, ell), controller in product(geometries, (widths, production_widths)):
        length = d * ell - d // 2
        ws = controller(length, d)
        require(sum(ws) == length and ws[0] == max(ws) <= 2 * min(ws), "dyadic widths")
        maximum_classes = max(maximum_classes, len(set(ws)))
        sides = select_squares(ws)
        require(sides is not None, "square construction failed")
        prior = []
        for i, r in enumerate(sides):
            b = isqrt(r)
            t = 1 << ws[i]
            lo, hi = square_interval(ws[i], d, i)
            require(b >= 3 and b % 2 == 1 and b*b == r and lo <= b <= hi, "invalid base")
            require(all(gcd(r, v*v) == 1 for v in prior), "noncoprime squares")
            require(all(x % 2 == 0 or any(gcd(x, v) > 1 for v in prior)
                        for x in range(lo,b)), "skipped eligible base")
            gap = Fraction(t-r, t)
            lower = 8*d if i % 2 == 0 else 32*d
            require(Fraction(1,lower) <= gap <= Fraction(2,lower), "relative deficit")
            # These sizes fall outside the old narrow deficit condition.
            p = 6*(sum(ws)+1)
            require(gap > Fraction(1, 2*p*p), "still in old fine interval")
            prior.append(b)
        S, T = prod(sides), 1 << sum(ws)
        require(4*S >= 3*T and S < T, "padded volume")
        if d <= 4:
            print("square axes",tuple(ws),"bases",tuple(prior),"valid/padded",f"{S}/{T}")
        rows += d
    require(select_squares((4,4)) is None, "small geometry must take fallback")
    require(controller_shape(1) == (0,0,0,0) and controller_shape(741503)[2] == 0, "finite branch")
    require(maximum_classes > 4, "controller did not use heterogeneous targets")
    print("composite axes =", rows, "largest family =", d, "maximum width classes =", maximum_classes)


def elementary_sieve():
    primes = [2,3,5,7,11,13,17,19]
    count = 0
    for m in range(1, len(primes)+1):
        selected = primes[:m]
        factors = prod(selected)
        reciprocal = Fraction(1)
        for q in selected:
            reciprocal *= Fraction(q-1,q)
        require(reciprocal >= Fraction(1,m+1), "Euler lower bound")
        for start in (0, 1, 23, 244, 32761):
            for length in (15, 64, 127):
                true = sum(gcd(i,factors)==1 for i in range(start+1,start+length+1))
                for k in (1, 3, 5):
                    partial = 0
                    for j in range(min(k,m)+1):
                        sign = (-1)**j
                        for subset in combinations(selected,j):
                            v = prod(subset)
                            partial += sign*((start+length)//v-start//v)
                    require(partial <= true, "Bonferroni lower bound")
                    count += 1
    print("exact interval truncations =",count)


def paid_widths():
    k = Fraction("0.00387992803556")
    q = k + 3*Fraction(1,10**14)
    a = k + 4*Fraction(1,10**14)
    ordinary = Fraction("0.003879928035646")
    # 3^5 < 2^8 proves Karatsuba's exponent is below 8/5.
    require(3**5 < 2**8 and 0 < k < q < a < ordinary < Fraction(2,5), "time powers")
    for shift in (16, 64, 512, 2048):
        L = 1 << shift
        p = 6*(L + shift)
        s = (p+1).bit_length()
        d = number_of_axes(p,L)
        if not d:
            continue
        w0, rem = divmod(L,d)
        h = max(1,d//s)
        selected_span = 2*h*128*(4*s+6)
        require(w0 >= (1<<16)*s**3 and w0 <= 2*(1<<16)*s**3, "prime-free width")
        require(2*(selected_span+1)*s*s < L, "no complete suffix outside moved positions")
        require((d+h-1)//h <= 2*s, "extra packs")
        for width in {w0,w0+bool(rem)}:
            K = 128*(4*s+6)
            for j in {0,1,K-1,K,width//2,width-1}:
                rho = min(j,K-1)
                require(0 <= j-rho and j-rho+K <= width, "invalid high-bit window")
    print("strict saving margins", str(q-k), str(a-k), str(ordinary-k))


def schedule_checks(source_root):
    path = source_root / "research/unconditional-batched-crt/check_batched_crt.py"
    spec = spec_from_file_location("square_check_benes", path)
    source = module_from_spec(spec)
    spec.loader.exec_module(source)
    decoded = 0
    for maximum in range(1, 33):
        for width in range(1, maximum + 1):
            rows = [(g, local_switch_row(maximum, width, g)) for g in range(2 * maximum - 1)]
            active = [(g, row) for g, row in rows if row is not None]
            require([row for _, row in active] == list(range(2 * width - 1)), "row missing")
            for global_row, row in active:
                global_bit = min(global_row, 2 * maximum - 2 - global_row)
                local_bit = min(row, 2 * width - 2 - row)
                require(global_bit == local_bit, "local switch has a different physical bit")
            decoded += len(rows)
    print("heterogeneous row decisions =", decoded)

    # Check every valid or dirty padded address. The widths differ by more
    # than one bit. The reference computes a whole modular shift directly.
    small_sides = (17, 9, 2, 7)
    small_widths = (5, 4, 2, 3)
    test = HeterogeneousCRT(small_sides, small_widths, source.benes)
    small = 0
    for point in product(*(range(1 << w) for w in small_widths)):
        dest = test.route(point)
        require(dest == source.balanced(point, small_sides), "full forward map")
        require(test.route(point, True) == source.balanced(point, small_sides, reverse=True),
                "full inverse map")
        require(test.route(dest, True) == point, "unrestored dirty coordinate")
        small += 1

    # Use genuine coprime-square sides of four different widths.
    large_sides = (121, 49, 9, 25)
    large_widths = (7, 6, 4, 5)
    test = HeterogeneousCRT(large_sides, large_widths, source.benes)
    rng = Random(524927)
    large = 0
    for _ in range(1024):
        point = tuple(rng.randrange(1 << width) for width in large_widths)
        dest = test.route(point)
        require(dest == source.balanced(point, large_sides), "four square CRT forward")
        require(test.route(dest, True) == point, "four square CRT inverse")
        large += 1
    # A dyadic true side has no padded hole of its own.
    exact_side = HeterogeneousCRT((4, 9), (2, 4), source.benes)
    for point in product(range(4), range(16)):
        destination = exact_side.route(point)
        require(destination == source.balanced(point, (4, 9))
                and exact_side.route(destination, True) == point, "full dyadic side")
    print("heterogeneous CRT full addresses =", small, "four-square samples =", large)


def coordinate_checks():
    # This finite prime field is an independent exact oracle for characters.
    # It is used only in this small test.
    sides = (9,25)
    physical = (16,32)
    S = prod(sides)
    modulus = 1801
    require(all(modulus % r for r in range(2,isqrt(modulus)+1)), "coefficient modulus")
    gen = next(v for v in range(2,modulus) if all(pow(v,(modulus-1)//q,modulus)!=1 for q in (2,3,5)))
    root = pow(gen,(modulus-1)//S,modulus)
    mu = [pow(prod(sides[:i]),-1,r) for i,r in enumerate(sides)]
    unit = sum((S//r)*m*m for r,m in zip(sides,mu)) % S
    old_unit = sum((S//r)*m*m*t for r,m,t in zip(sides,mu,physical)) % S
    require(gcd(unit,S)==1 and old_unit!=unit, "character mutation")
    positions = list(product(*(range(t) for t in physical)))
    def coord(j):
        return tuple(j*m%r for m,r in zip(mu,sides))
    require(len({coord(k) for k in range(S)}) == S, "physical bijection")
    def axes(a, sign):
        for i,r in enumerate(sides):
            w = pow(root,sign*(S//r),modulus)
            src = a
            a = {}
            for point in positions:
                if point[i] >= r:
                    a[point] = src[point]
                else:
                    total = 0
                    for j in range(r):
                        index = (j,point[1]) if i == 0 else (point[0],j)
                        total += pow(w,j*point[i],modulus)*src[index]
                    a[point] = total*pow(r,-1,modulus) % modulus
        return a
    def deposit(values, dirty):
        a = {v: ((17*v[0]+57*v[1]+19) % modulus if dirty else 0) for v in positions}
        for j in range(S):
            a[coord(j)] = values.get(j,0)
        return a
    e = axes(deposit({1:1},False),1)
    require(all(e[coord(k)] == pow(root,k*unit,modulus)*pow(S,-1,modulus)%modulus for k in range(S)), "direct character")
    require(e[coord(1)] != pow(root,old_unit,modulus)*pow(S,-1,modulus)%modulus, "old geometry factor survived")
    original = deposit({1:1}, True)
    dirt = axes(original,1)
    require(all(e[coord(j)]==dirt[coord(j)] for j in range(S)), "dirty hole leaked")
    require(any(dirt[v]!=original[v] for v in positions if any(x>=r for x,r in zip(v,sides))), "dirty complement was pointwise identity")
    A = {0:3,1:1,2:2}
    B = {0:2,2:3}
    f, g = [axes(deposit(dig,True),1) for dig in (A,B)]
    h = axes({v:f[v]*g[v]%modulus for v in positions},-1)
    c = [S*S*h[coord(j)]%modulus for j in range(S)]
    require(c[:5]==[6,2,13,3,6] and not any(c[5:]), "physical square CRT convolution")
    require(sum(v*4**i for i,v in enumerate(c))==(3+4+2*16)*(2+3*16),"integer value")
    try:
        pow(9,-1,15)
    except ValueError:
        pass
    else:
        raise ValueError("noncoprime control accepted")
    print("composite CRT character",unit,"old-factor mutant",old_unit,"ring modulus",modulus,"coefficients",c[:5])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    square_families()
    elementary_sieve()
    paid_widths()
    schedule_checks(args.source_root)
    coordinate_checks()
    print("PASS_PRIME_FREE_DIRECT_OUTER")
