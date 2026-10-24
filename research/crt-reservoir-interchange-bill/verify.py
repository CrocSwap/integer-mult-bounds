#!/usr/bin/env python3
"""Price the #4174 reservoir exchange with the #4100 BIT.md ordinary callee.

PROOF.md is the argument. This script checks its finite facts:

A. On small Placement fixtures, three literal field-exchange calls realize
   the #4174 placement permutation in every order, and the same three calls
   restore every dirty record. Payload is moved, not just positions.
B. Every #4174 plan on the minimal layout (p = 1310720, ell = 21) and on the
   production layout (p = 9240576, ell = 24) is three disjoint width-H pairs
   inside the reservoir, so placement plus restoration is six width-H calls.
C. BIT.md section 4's wrapper, evaluated exactly at radix width E: every
   E < 311309 takes the elementary branch and E = 311309 takes the body.
   In binary this is H < 27706412. Both layouts are elementary.
D. On that elementary range, E <= H^(1-a2), so the CRT.md per-call bill
   V H^(1-a) is met by the elementary stage alone.
E. The literal call pads the volume by (q^E/2^H)^2: in (2^33, 2^34) at the
   minimal layout and in (2^73, 2^74) at the production layout.

Rejection controls check that mutated claims fail. No new kappa is claimed.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
import types
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "crt-reservoir-interchange-bill"
ALLOCATOR = "research/crt-reservoir-placement/allocator.py"

Q = 2 ** 89 - 1
M = 269241600                       # the integer factor of K(w)
C = Fraction(8667, 5000000)
A2 = C * (1 - C * C)                # BIT.md a2
E_MIN = 311309                      # first radix width on the body branch
H_MIN = 27706412                    # first binary width on the body branch
J = (0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 6)  # j(D), D <= 19

PHRASES = {
    "research/unconditional-batched-crt/BIT.md": (
        "exchanges two complete equal e-bit binary address fields, with arbitrary "
        "complete preceding, intervening and following fields, in O(V e^(1-a2)) "
        "time and O(V) visited space.",
        "It preserves its borrowed input, returns a distinct owned output, fixes "
        "every spectator, erases its work and returns its heads.",
        "q=2^89-1,",
        "c=8667/5000000,",
        "a2=c(1-c^2)=0.001733394791695384296.",
        "Let W=28416, N=|GL_64(F_q)| and",
        "K(w)=269241600 N q^(4096(w-1)),",
        "D(n)=0 (n<64), D(n)=1+D(42 floor(n/64)) (n>=64).",
        "At a root choose w=ceil(e^c)",
        "On original radix width e compute stock=K(w)^D(e) and the least k with "
        "q^k>=stock before removing borrowed digits. If 2k>=e or the body width "
        "is below64, use the elementary algorithm.",
        "Otherwise write e=k+nw+ell with 0<=ell<w.",
        "initially a=0 from elementary q-digit swaps.",
        "Finally embed each 2^e binary field into q^E, E=ceil(log_q(2^e)); each "
        "ratio is <q.",
        "This changes volume by <q^2",
    ),
    "research/unconditional-batched-crt/CRT.md": (
        "The ordinary interchange used below is supplied by BIT.md.",
        "where an already completed ordinary interchange costs O(V h^(1-a)),",
        "G=64(ell+ceil(log2(p+2))), B=2^G, K=64G,",
        "r_max=floor(L/(100G)), H=r_max G.",
        "Move them into two front positions and one back position using a fixed "
        "number of paid equal-H interchanges.",
        "Three disjoint source/destination exchanges suffice.",
        "hence twelve paid H-bit exchanges.",
        "It costs O(V H^(1-a)+V).",
    ),
    "research/crt-reservoir-placement/PROOF.md": (
        "The placement invoice is at most six width-`H` ordinary exchanges per "
        "batch, in addition to the switch's own operations.",
        "Each exchange is a coordinate translation on its two blocks and identity "
        "elsewhere; their product `P` is an involution.",
    ),
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def must_fail(thunk, message: str) -> None:
    """A rejection control: the mutated claim must raise or return False."""
    try:
        result = thunk()
    except (ValueError, SystemExit):
        return
    need(result is False, "control accepted: " + message)


def pins_and_phrases() -> dict[str, bytes]:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    data = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row["sha256"], "pin " + row["path"])
            data[row["path"]] = raw
    for path, phrases in PHRASES.items():
        text = " ".join(data[path].decode("utf-8").split())
        for phrase in phrases:
            need(phrase in text, f"{path}: {phrase[:60]}")
    return data


def load_allocator(raw: bytes):
    """Execute the authenticated bytes, never a cached module."""
    module = types.ModuleType("crt_reservoir_allocator")
    module.__file__ = str(ROOT / ALLOCATOR)
    sys.modules[module.__name__] = module
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


# ---------------------------------------------------------------- part A

def interchange(payload: list[int], length: int, first, second, reverse=False) -> list[int]:
    """One ordinary call: exchange two equal complete address fields.

    Physical position v is integer bit length-1-v (#4174 convention). The
    record at address x moves to the address with the two fields swapped,
    bit for bit in order. All other fields are spectators.
    """
    width = first[1] - first[0]
    need(width == second[1] - second[0], "unequal fields")
    pairs = []
    for t in range(width):
        u = first[0] + (width - 1 - t if reverse else t)
        pairs.append((length - 1 - u, length - 1 - (second[0] + t)))
    out = [0] * len(payload)
    for x, record in enumerate(payload):
        y = x
        for bu, bv in pairs:
            if ((x >> bu) ^ (x >> bv)) & 1:
                y ^= (1 << bu) | (1 << bv)
        out[y] = record
    return out


def placement_permutation(placement, length: int) -> list[int]:
    """Address map induced by Placement.map_position (bit at v moves to P(v))."""
    image = []
    for x in range(1 << length):
        y = 0
        for v in range(length):
            if (x >> (length - 1 - v)) & 1:
                y |= 1 << (length - 1 - placement.map_position(v))
        image.append(y)
    return image


def dirty(length: int) -> list[int]:
    return [(x * 0x9E3779B1 + 12345) % 1000003 for x in range(1 << length)]


def part_a(allocator) -> int:
    # Adjacent aligned sources as #4174 builds them, and scattered sources.
    fixtures = ((12, 2, ((4, 6), (6, 8), (8, 10))),
                (14, 2, ((8, 10), (4, 6), (10, 12))))
    checked = 0
    for length, width, sources in fixtures:
        placement = allocator.Placement(length, width, sources)
        need(len(placement.swaps) == 3, "three swaps")
        start = dirty(length)
        target = placement_permutation(placement, length)
        expected = [0] * len(start)
        for x, record in enumerate(start):
            expected[target[x]] = record
        for order in itertools.permutations(placement.swaps):
            state = start
            for first, second in order:            # placement: three calls
                state = interchange(state, length, first, second)
            need(state == expected, "three calls realize P in every order")
            for first, second in order:            # restoration: same three calls
                state = interchange(state, length, first, second)
            need(state == start, "six calls restore every dirty record")
            checked += 1
        # Controls: a dropped restoration call, or a reversing exchange, fail.
        def dropped():
            state = start
            for first, second in placement.swaps:
                state = interchange(state, length, first, second)
            for first, second in placement.swaps[:2]:
                state = interchange(state, length, first, second)
            return state == start
        must_fail(dropped, "five calls restore")
        def reversed_call():
            state = start
            for first, second in placement.swaps:
                state = interchange(state, length, first, second, reverse=True)
            return state == expected
        must_fail(reversed_call, "bit-reversing exchange realizes P")
    must_fail(lambda: allocator.Placement(12, 2, ((2, 4), (6, 8), (8, 10))),
              "a source overlapping destination T")
    return checked


# ---------------------------------------------------------------- part B

def disjoint(a, b) -> bool:
    return a[1] <= b[0] or b[1] <= a[0]


def part_b(allocator, p: int, ell: int, widths) -> tuple:
    layout = allocator.Layout(p, ell, widths)
    L, H = layout.L, layout.H
    plans = calls = 0
    for plan in allocator.iter_plans(layout):
        swaps = plan.swaps
        need(len(swaps) == 3, "three pairs")
        need(tuple(d for _, d in swaps) == ((0, H), (H, 2 * H), (L - H, L)),
             "destinations u, t, b")
        blocks = [b for pair in swaps for b in pair]
        need(all(b[1] - b[0] == H for b in blocks), "every field has width H")
        need(all(disjoint(x, y) for x, y in itertools.combinations(blocks, 2)),
             "six blocks pairwise disjoint")
        lo, hi = plan.reservoir_interval
        for source, _ in swaps:
            need(lo <= source[0] and source[1] <= hi, "source inside reservoir")
            for dep in plan.dependencies:
                need(disjoint(source, dep.own_interval)
                     and disjoint(source, dep.left_interval), "source omitted by controls")
        for v in plan.cuts:
            for u in (v - 1, v):
                if 0 <= u < L:
                    need(plan.map_position(plan.map_position(u)) == u, "involution")
        plans += 1
        calls += 2 * len(swaps)
    return layout, plans, calls


# ---------------------------------------------------------------- part C

def depth(n: int) -> int:
    return 0 if n < 64 else 1 + depth(42 * (n // 64))


def gl_order() -> int:
    q64 = Q ** 64
    order = 1
    power = 1
    for _ in range(64):
        order *= q64 - power
        power *= Q
    return order


def stock_digits(dep: int) -> int:
    """j(D): least j with q^j >= (269241600 N / q^4096)^D."""
    j = 0
    while Q ** j < M ** dep:
        j += 1
    # (M (1 - 2/q))^D < (M N/q^4096)^D, so q^(j-1) is still too small.
    need(j == 0 or Q ** (j - 1 + dep) < (M * (Q - 2)) ** dep, f"j({dep}) is exact")
    return j


def wrapper(E: int, table) -> tuple[int, int, int, str]:
    """Return (w, D, k, branch) for BIT.md section 4 at radix width E."""
    need(1 <= E < 1 << 576, "w formula range")
    w = 1 if E == 1 else 2                   # E^c in (1, 2] for 2 <= E < 2^576
    dep = depth(E)
    k = (4096 * w * dep + table[dep]) if dep else 0
    if 2 * k >= E or (E - k) // w < 64:
        return w, dep, k, "elementary"
    return w, dep, k, "body"


def radix_width(H: int) -> int:
    """Least E with q^E >= 2^H, for 1 <= H < 89 * 2^88 (PROOF.md lemma)."""
    need(1 <= H < 89 << 88, "radix lemma range")
    return H // 89 + 1


def part_c() -> dict:
    N = gl_order()
    q4096 = Q ** 4096
    need(N < q4096 and N * Q > q4096 * (Q - 2), "1 - 2/q < N/q^4096 < 1")
    need(1 < M < Q and M * (Q - 2) > Q, "4096 < log_q(269241600 N) < 4097")
    table = tuple(stock_digits(dep) for dep in range(20))
    need(table == J, "j(D) table")
    need(576 * 8667 <= 5000000, "E < 2^576 gives E^c <= 2, so w = 2")
    branches = [wrapper(E, table)[3] for E in range(1, E_MIN + 1)]
    need(all(b == "elementary" for b in branches[:-1]), "every E < 311309 elementary")
    need(branches[-1] == "body", "E = 311309 is body")
    need(wrapper(E_MIN, table)[:3] == (2, 19, 155654), "body entry values")
    need(all(depth(E) >= 1 for E in range(64, 16387)), "D >= 1 on [64, 16386]")
    for H in list(range(1, 3000)) + [10752, 15360]:
        E = radix_width(H)
        need(Q ** E >= 2 ** H and Q ** (E - 1) < 2 ** H, f"radix width at H={H}")
    need(radix_width(H_MIN - 1) == E_MIN - 1 and radix_width(H_MIN) == E_MIN, "H_MIN")
    need(radix_width(1458353) == 16386 and radix_width(1458354) == 16387, "robust edge")
    return {"table": table}


def layout_branch(layout, table) -> tuple:
    E = radix_width(layout.H)
    return (E,) + wrapper(E, table)


# ---------------------------------------------------------------- part D

def part_d() -> None:
    need(A2 < Fraction(1, 500), "a2 < 1/500")
    need(H_MIN < 2 ** 25, "H_MIN < 2^25")
    # For 89 <= H < 2^25: E <= 2H/89 and H^a2 < 2^(25/500) <= 89/2.
    need(Fraction(89, 2) ** 500 > 2 ** 25, "2^(1/20) < 89/2")
    for H in range(1, 89):
        need(radix_width(H) == 1, "E = 1 below 89")
    for H in range(89, 20000):
        need(89 * radix_width(H) <= 2 * H, "E <= 2H/89")
    # Floating sanity only; the inequality above is the proof.
    need(radix_width(10752) <= 10752 ** float(1 - A2), "minimal layout ratio")


# ---------------------------------------------------------------- part E

def padding_bits(H: int) -> tuple[int, int]:
    """(lo, hi) with 2^lo < (q^E / 2^H)^2 < 2^hi for the literal BIT call."""
    E = radix_width(H)
    square = Q ** (2 * E)
    lo = 2 * (89 * E - H) - 1
    need(2 ** (lo + 2 * H) < square < 2 ** (lo + 1 + 2 * H), f"padding at H={H}")
    return lo, lo + 1


def part_e() -> None:
    need(padding_bits(10752) == (33, 34), "minimal padding (2^33, 2^34)")
    need(padding_bits(15360) == (73, 74), "production padding (2^73, 2^74)")
    must_fail(lambda: 2 ** (33 + 2 * 10752) >= Q ** 242, "minimal padding below 2^33")
    must_fail(lambda: 2 ** (73 + 2 * 15360) >= Q ** 346, "production padding below 2^73")


# ---------------------------------------------------------------- main

def controls(table) -> int:
    count = 0
    for thunk, message in (
        (lambda: wrapper(E_MIN - 1, table)[3] == "body", "body one digit early"),
        (lambda: radix_width(H_MIN - 1) >= E_MIN, "binary body one bit early"),
        (lambda: wrapper(121, table)[2] == 8192, "stock without the 269241600 N factor"),
        (lambda: wrapper(173, table)[1] == 1, "D(173) = 1"),
        (lambda: gl_order() >= Q ** 4096, "N >= q^4096"),
    ):
        must_fail(thunk, message)
        count += 1
    # Dropping j(D) moves the first body width, so the sharp claim depends on it.
    first = next(E for E in range(1, E_MIN + 1)
                 if wrapper(E, (0,) * 20)[3] == "body")
    need(first != E_MIN, "j(D) matters for E_MIN")
    return count + 1


def main() -> None:
    data = pins_and_phrases()
    allocator = load_allocator(data[ALLOCATOR])
    orders = part_a(allocator)
    minimal, m_plans, m_calls = part_b(allocator, 1310720, 21, (20,) * 65536)
    need((minimal.L, minimal.G, minimal.r_max, minimal.H) == (1310720, 2688, 4, 10752),
         "minimal layout")
    need((m_plans, m_calls) == (131072, 786432), "minimal plan and call counts")
    widths = tuple(24 - (i % 2) for i in range(65536))
    production, p_plans, p_calls = part_b(allocator, 6 * sum(widths), 24, widths)
    need((production.p, production.H, p_plans, p_calls) == (9240576, 15360, 104864, 629184),
         "production layout")
    table = part_c()["table"]
    need(layout_branch(minimal, table) == (121, 2, 1, 8193, "elementary"), "minimal branch")
    need(layout_branch(production, table) == (173, 2, 2, 16385, "elementary"),
         "production branch")
    need(100 * H_MIN == 2770641200 and minimal.H <= minimal.L // 100, "caller threshold")
    part_d()
    part_e()
    count = controls(table) + 2
    print(f"PASS_CRT_RESERVOIR_INTERCHANGE_BILL orders={orders} "
          f"minimal_plans={m_plans} minimal_calls={m_calls} "
          f"production_plans={p_plans} E_min={E_MIN} H_min={H_MIN} "
          f"minimal=(H=10752,E=121,k=8193,elementary,pad=2^33..2^34) "
          f"controls={count + 5}")


if __name__ == "__main__":
    main()
