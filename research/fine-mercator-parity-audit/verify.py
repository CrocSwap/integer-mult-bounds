#!/usr/bin/env python3
"""Exact parity audit of the PR1479/PR1485 finer-constant Mercator engine.

The vendored ``fine_mercator.logarithm`` claims an outward enclosure of log(x).
Its inner alternating series stops after n = LOGN-1 = 799, an odd partial sum,
which lies *above* log(1+z); the returned ``(s, s+t/LOGN)`` therefore uses an
upper bound as its lower end. This script proves that with exact rationals,
shows that every input used by the pinned T74 complex check survives the
2^-800 floor, checks a one-constant repair and runs controls.

All decisions use fractions.Fraction. The oracle is a separately written
2*atanh((y-1)/(y+1)) enclosure on 1 <= y <= 2 with a positive-term tail bound.
Pass --search to rediscover the three integer counterexamples (slower).
"""
from fractions import Fraction as F
from pathlib import Path
import hashlib, json, sys, types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VENDOR = {
    'fine_mercator': ('vendor/pr1479/fine_mercator.py',
                      '47d60aa6760c246db8c64d704b2f725e3a4eca9d3871a0580524f16151ff45e8'),
    'fine_moment': ('vendor/pr1479/fine_moment.py',
                    '82c06ab9d752777409b8e5c7a1ae5d63e9958aae781477ad4cd44da13d0e21f1'),
}
RETAINED = 'research/complex-allcold/engines/moment.py'
M = 73                             # complex width in both PRs' check_moment
COUNTEREXAMPLES = (43, 189, 352)   # first three integers >= 2 (see --search)
ORACLE_TERMS = 700                 # z <= 1/3: tail below 9^-700 < 2^-2200


def need(cond, msg):
    if not cond:
        raise SystemExit('FAIL: ' + msg)


def load(name, path, source):
    mod = types.ModuleType(name)
    exec(compile(source, str(path), 'exec'), mod.__dict__)
    return mod


def unit_log(y):
    need(1 <= y <= 2, 'oracle range')
    z = (y-1)/(y+1); s = F(0); p = z
    for j in range(ORACLE_TERMS):
        s += p/(2*j+1); p *= z*z
    return 2*s, 2*(s+p/((2*ORACLE_TERMS+1)*(1-z*z)))


LN2 = unit_log(F(2))


def oracle(x):
    need(x >= 1, 'oracle domain')
    k = 0
    while x > 2:
        x /= 2; k += 1
    lo, hi = unit_log(x)
    return lo+k*LN2[0], hi+k*LN2[1]


def violations(engine, xs):
    """False lower ends, false upper ends and the least valid lower margin."""
    bad_lo, bad_hi, margin = [], [], None
    for x in xs:
        lo, hi = engine(x)
        L, U = oracle(x)
        need(U-L < F(1, 2**1500), 'oracle width')
        if lo > U: bad_lo.append(x)
        if hi < L: bad_hi.append(x)
        if lo <= L:
            margin = L-lo if margin is None else min(margin, L-lo)
    return bad_lo, bad_hi, margin


def main():
    search = '--search' in sys.argv
    for name, (rel, digest) in VENDOR.items():
        need(hashlib.sha256((HERE/rel).read_bytes()).hexdigest() == digest, 'vendored pin ' + name)
    pins = {f['path']: f['sha256'] for f in json.loads((HERE/'SOURCES.json').read_text())['files']}
    need(hashlib.sha256((ROOT/RETAINED).read_bytes()).hexdigest() == pins[RETAINED], 'retained pin')

    mf_src = (HERE/VENDOR['fine_mercator'][0]).read_text()
    MF = load('fine_mercator', HERE/VENDOR['fine_mercator'][0], mf_src)
    BF = load('fine_moment', HERE/VENDOR['fine_moment'][0], (HERE/VENDOR['fine_moment'][0]).read_text())
    RM = load('retained_moment', ROOT/RETAINED, (ROOT/RETAINED).read_text())
    need(MF.LOGN == 800, 'audited engine has LOGN = 800')
    need('for n in range(1, LOGN)' in mf_src and 'return s, s+t/LOGN' in mf_src, 'audited loop shape')

    # 1. Inner series: the 799-term (odd) partial sum at z = 1/2 exceeds log(3/2);
    #    including the omitted negative n = 800 term restores a lower bound.
    z = F(1, 2); t = z; s = F(0)
    for n in range(1, MF.LOGN):
        s += (t if n & 1 else -t)/n; t *= z
    L32, U32 = oracle(F(3, 2))
    need(s > U32, 'odd partial sum lies above log(3/2)')
    need(s - t/MF.LOGN < L32, 'next negative term gives a lower bound')

    # 2. Exported function: exact false lower ends that survive the 2^-800 floor.
    ce = [F(n) for n in COUNTEREXAMPLES]
    bad_lo, bad_hi, _ = violations(MF.logarithm, ce)
    need(bad_lo == ce and not bad_hi, 'exact false lower bounds at 43, 189, 352')

    # 3. Inputs of the pinned T74 complex check: log(73/r), 0 < r < 73, and the
    #    surcharge log(73). Every lower end is valid there (floor absorbs the error).
    used = [F(M, r) for r in range(1, M)] + [F(M)]
    bad_lo, bad_hi, margin = violations(MF.logarithm, used)
    need(not bad_lo and not bad_hi and margin > 0, 'pinned inputs survive the floor')
    for engine in (BF.log_bounds, RM.logarithm):
        a, b, _ = violations(engine, used + ce)
        need(not a and not b, 'companion and retained engines valid')

    # 4. Repair: LOGN = 801 sums n <= 800 (even partial sum, below log); the
    #    returned upper end s+z^801/801 is then the correct next-term bound.
    fixed = load('fine_mercator_801', 'fine_mercator_801.py', mf_src.replace('LOGN = 800', 'LOGN = 801', 1))
    need(fixed.LOGN == 801, 'repair applied')
    a, b, _ = violations(fixed.logarithm, used + ce + [F(3, 2), F(4, 3), F(2)])
    need(not a and not b, 'repaired engine valid')

    # 5. Control: the oracle comparison detects a deliberately raised lower end.
    raised = lambda x: (oracle(x)[1] + F(1, 2**900), oracle(x)[1] + F(1, 2**899))
    need(violations(raised, [F(2)])[0] == [F(2)], 'oracle control detects false lower')
    if search:
        found = []
        for n in range(2, 4097):
            if violations(MF.logarithm, [F(n)])[0]:
                found.append(n)
                if len(found) == len(COUNTEREXAMPLES): break
        need(tuple(found) == COUNTEREXAMPLES, 'search reproduces counterexamples')

    print(json.dumps({
        'status': 'PASS_FINE_MERCATOR_PARITY_AUDIT',
        'audited_blob': '29699092d4e66677d50d400a89e4763e476ef7e1',
        'audited_heads': {'PR1479': '0a211a4608d2c3d295f8bb94b12ca446714186ab',
                          'PR1485': 'da38a09c5b2c2418d405773ac398378ab92ccf54'},
        'inner_excess_over_log_3_2_times_2^800': float((s-U32)*2**800),
        'false_lower_bounds': [str(n) for n in COUNTEREXAMPLES],
        'pinned_inputs_checked': len(used),
        'pinned_min_floor_margin_times_2^800': float(margin*2**800),
        'repair': 'LOGN = 801',
        'search_run': search,
    }, indent=1))


if __name__ == '__main__':
    main()
