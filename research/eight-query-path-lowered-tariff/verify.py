"""Exact eight-query row of the mutable-source invoice (path-lowered even-subset class).

Model, tariff and word builder come from research/mutable-source-789q-invoice/model.py,
a pinned live input (Wentao Li; alphabet of PR1898). A path-lowered word is a closed
connector prefix walk 0 = w_0, w_1, ..., w_Q = 0 in F2^5 with nonzero edges, even-subset
readouts R over its slot values, and X = sum over edges of 2 * (weight(edge) - 1).
Tariff (b, a, x) = (38, 2, 2): 38 Q + 2 R + 2 X.

Checks, all standard library:
  1. R census over every set of 5, 6 or 7 nonzero connector values (readout floors).
  2. XOR parity lemma X >= 2 * max(0, 10 - Q), exhaustive controls in F2^2, F2^3, F2^4.
  3. Exhaustive X-floor layers at Q = 6..10 (each coordinate in exactly two edges); the
     Q = 10 layer is a cross-check against the earlier ten-query results, not a new claim.
  4. Literal dirty-row replay of the witness words with the pinned model.
  5. Set-based readout and edge-cost formulas against the pinned model on random walks.
"""
from __future__ import annotations

import hashlib
import importlib.util
import random
import sys
from collections import Counter
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "research" / "mutable-source-789q-invoice" / "model.py"
MODEL_SHA256 = "6696b01837e526f365576c6e35367fa8a1494f5bd3f49af7fe38c52366668c13"
FULL = 32
INF = 99
ENDPOINT = 436  # six-query endpoint tariff at (b, a, x) = (38, 2, 2)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_model():
    data = MODEL_PATH.read_bytes()
    need(hashlib.sha256(data).hexdigest() == MODEL_SHA256, "pinned model.py bytes changed")
    spec = importlib.util.spec_from_file_location("mutable_source_789q_model", MODEL_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def weight(x):
    return x.bit_count()


def readout(values):
    """Total even-subset readout count for the nonzero connector values (zero slot is free).

    s[m] is the least number of distinct values with XOR m; the zero slot repairs parity,
    so mask m costs 2 * ceil(s[m] / 2).  None when some mask is uncovered.
    """
    s = [INF] * FULL
    s[0] = 0
    for v in values:
        new = s[:]
        for m in range(FULL):
            if s[m] < INF and new[m ^ v] > s[m] + 1:
                new[m ^ v] = s[m] + 1
        s = new
    total = 0
    for m in range(1, FULL):
        if s[m] >= INF:
            return None
        total += 2 * ((s[m] + 1) // 2)
    return total


def walk_x(closed):
    return sum(2 * (weight(a ^ b) - 1) for a, b in zip(closed, closed[1:]))


def walk_r(closed):
    return readout(sorted({v for v in closed if v}))


def census(k):
    """Spectrum of R over all k-subsets of nonzero F2^5 values that cover every mask."""
    spectrum = Counter()
    for values in combinations(range(1, FULL), k):
        r = readout(values)
        if r is not None:
            spectrum[r] += 1
    return spectrum


def x_floor(q):
    return 2 * max(0, 10 - q)


def check_parity_lemma_small():
    """Exhaustive control of the generic lemma X >= 2 * max(0, 2n - Q) in F2^n.

    A walk covers when its visited values span F2^n.  Equality must be attained at
    every Q from n + 1 to 2n, and the walk cost must be even-congruent as stated.
    """
    checked = 0
    for n, qmax in ((2, 6), (3, 7), (4, 6)):
        size = 1 << n
        for q in range(n + 1, qmax + 1):
            best = None
            for tail in product(range(size), repeat=q - 1):
                closed = (0,) + tail + (0,)
                if any(a == b for a, b in zip(closed, closed[1:])):
                    continue
                span = {0}
                for v in closed:
                    span |= {s ^ v for s in span}
                if len(span) != size:
                    continue
                x = sum(2 * (weight(a ^ b) - 1) for a, b in zip(closed, closed[1:]))
                floor = 2 * max(0, 2 * n - q)
                need(x >= floor, f"parity lemma fails n={n} q={q} walk={closed}")
                need(x % 4 == (2 * q) % 4, f"parity class fails n={n} q={q} walk={closed}")
                best = x if best is None else min(best, x)
                checked += 1
            if q <= 2 * n:
                need(best == 2 * (2 * n - q), f"floor not attained n={n} q={q}: {best}")
            else:
                # Beyond Q = 2n the weight total must be even and at least Q, so X >= 2 (Q mod 2).
                need(best == 2 * (q % 2), f"parity floor not attained n={n} q={q}: {best}")
    return checked


def layer(q):
    """Every closed q-edge walk whose edges are nonzero and use each coordinate exactly twice.

    These are exactly the walks with X = 2 * (10 - q).  Returns (walks, spectrum, example)
    where the spectrum counts walks by R (None: the visited values do not cover) and
    example maps R to the first walk found in depth-first order.
    """
    spectrum = Counter()
    example = {}
    cache = {}
    counts = [0] * 5
    walk = [0]
    total = 0

    def rec(position, current, visited, used):
        nonlocal total
        if position == q:
            need(current == 0 and all(c == 2 for c in counts), "layer closure invariant")
            total += 1
            key = frozenset(visited)
            if key not in cache:
                cache[key] = readout(sorted(key))
            r = cache[key]
            spectrum[r] += 1
            example.setdefault(r, tuple(walk))
            return
        remaining = q - position - 1
        for d in range(1, FULL):
            if any(d >> j & 1 and counts[j] == 2 for j in range(5)):
                continue
            new_used = used + weight(d)
            if new_used + remaining > 10 or new_used + 5 * remaining < 10:
                continue
            for j in range(5):
                if d >> j & 1:
                    counts[j] += 1
            nxt = current ^ d
            added = nxt != 0 and nxt not in visited
            if added:
                visited.add(nxt)
            walk.append(nxt)
            rec(position + 1, nxt, visited, new_used)
            walk.pop()
            if added:
                visited.discard(nxt)
            for j in range(5):
                if d >> j & 1:
                    counts[j] -= 1

    rec(0, 0, set(), 0)
    return total, spectrum, example


def layer_walk_count(q):
    """Closed-form count of layer walks: 5 coordinates choose position pairs covering all q edges."""
    from math import comb

    return sum((-1) ** i * comb(q, i) * comb(q - i, 2) ** 5 for i in range(q + 1))


def check_model_agreement(model, rng):
    """Set-based readout and edge-cost formulas against the pinned model."""
    checked = 0
    for q in (6, 7, 8, 9):
        for _ in range(1500):
            while True:
                mid = [rng.randrange(FULL) for _ in range(q - 1)]
                closed = [0] + mid + [0]
                if all(a != b for a, b in zip(closed, closed[1:])):
                    break
            slots = tuple(closed[:-1])
            expected = model.min_even_subset_R(slots)
            need(walk_r(closed) == expected, f"readout formula differs on {closed}")
            need(walk_x(closed) == model.path_X(closed), f"edge cost differs on {closed}")
            checked += 1
    return checked


def replay(model, closed):
    """Literal dirty-row replay of the path-lowered word; returns (Q, R, X, tariff)."""
    word = model.path_word(list(closed))
    counts = model.check_identity(word)
    inv = model.invoice(word)
    need(inv["Q"] == counts["Q"] and inv["R"] == counts["R"] and inv["X"] == counts["X"], "invoice counts")
    need(inv["tariff"] == 38 * inv["Q"] + 2 * inv["R"] + 2 * inv["X"], "tariff formula")
    need(model.rank_increments(list(closed)) == 5, "increments do not span")
    return inv["Q"], inv["R"], inv["X"], inv["tariff"]


def main():
    model = load_model()
    out = []

    # 1. Readout census over all connector-value sets of size 5, 6 and 7.
    spectra = {k: census(k) for k in (5, 6, 7)}
    need(dict(spectra[5]) == {96: 83328}, f"size-5 spectrum {dict(spectra[5])}")
    need(dict(spectra[6]) == {82: 97216, 88: 486080}, f"size-6 spectrum {dict(spectra[6])}")
    need(dict(spectra[7]) == {74: 416640, 80: 1180480, 84: 833280}, f"size-7 spectrum {dict(spectra[7])}")
    need(sum(spectra[7].values()) == 2430400 and sum(spectra[6].values()) == 583296, "set counts")
    out.append("census R: size5 {96}, size6 {82,88}, size7 {74,80,84}; sets 83328/583296/2430400")

    # 2. Parity lemma controls.
    checked = check_parity_lemma_small()
    out.append(f"parity lemma controls: {checked} covering walks in F2^2..F2^4")

    # 3. Exhaustive X-floor layers.
    layers = {}
    for q in range(6, 11):
        walks, spectrum, example = layer(q)
        need(walks == layer_walk_count(q) == sum(spectrum.values()), f"layer count q={q}")
        layers[q] = (walks, spectrum, example)
    expect_min = {6: 96, 7: 82, 8: 74, 9: 70, 10: 64}
    for q, (walks, spectrum, example) in layers.items():
        covering = [r for r in spectrum if r is not None]
        need(min(covering) == expect_min[q], f"layer minimum q={q}: {min(covering)}")
        out.append(
            f"layer Q={q} X={x_floor(q)}: walks={walks} min R={min(covering)} "
            f"at {spectrum[min(covering)]} walks; example {example[min(covering)]}"
        )
    need(layers[8][1][74] == 30240 and layers[7][1][82] == 40320 and layers[6][1][96] == 155520, "attaining counts")
    need(layers[10][1][64] == 2640 and layers[9][1][70] == 28080, "attaining counts q=9,10")
    need(62 not in layers[10][1], "R=62 occurs in the X=0 layer at Q=10")

    # 4. Floors are attained simultaneously at Q = 6, 7, 8.
    floors = {6: (96, 8), 7: (82, 6), 8: (74, 4)}
    for q, (r_floor, x_floor_q) in floors.items():
        need(x_floor(q) == x_floor_q, f"X floor q={q}")
        need(min(r for r in layers[q][1] if r is not None) == r_floor, f"R floor attained q={q}")
    # Walks with repeated prefix values or zero revisits cannot reach R = 74.
    need(min(spectra[6]) == 82 and min(spectra[5]) == 96, "repeated-value layers")

    # 5. Replays with the pinned model.
    witness8 = layers[8][2][74]
    need(replay(model, witness8) == (8, 74, 4, 460), f"witness8 replay {witness8}")
    fixed8 = (0, 4, 20, 24, 9, 1, 3, 2, 0)
    need(replay(model, fixed8) == (8, 74, 4, 460), "fixed witness replay")
    champion7 = (0, 1, 2, 6, 12, 24, 16, 0)
    need(replay(model, champion7) == (7, 82, 6, 442), "seven-query champion replay")
    word6 = model.minimum_word_6q()
    inv6 = model.invoice(word6)
    need((inv6["Q"], inv6["R"], inv6["X"], inv6["tariff"]) == (6, 96, 8, ENDPOINT), "six-query endpoint")
    need(model.check_identity(word6)["Q"] == 6, "six-query word replay")
    witness9 = layers[9][2][70]
    need(replay(model, witness9) == (9, 70, 2, 486), f"Q=9 X-floor witness {witness9}")
    # Cross-check at ten queries: the read-only repair (64 readouts, no source XOR) of the earlier
    # lineage is the X = 0 layer, and R = 62 does not occur there, so it needs X >= 4 (the four-X path).
    witness10 = layers[10][2][64]
    need(replay(model, witness10) == (10, 64, 0, 508), f"X=0 walk at Q=10 {witness10}")
    ten = [0, 4, 5, 1, 3, 7, 6, 14, 28, 16, 0]
    need(replay(model, ten)[:3] == (10, 62, 4), "four-X ten-query path")
    out.append(
        f"replays: Q=8 {witness8} and {fixed8} -> R=74 X=4 tariff 460; "
        f"Q=7 champion 442; Q=6 endpoint 436; Q=9 {witness9} -> R=70 X=2 tariff 486"
    )
    out.append(
        f"cross-check Q=10: X=0 layer minimum R=64 ({witness10}, tariff 508), R=62 absent from that "
        "layer, four-X path (R=62, X=4, tariff 512) replays"
    )

    # 6. Tariff table and exact crossovers.
    def f(q, r, x, b=38, a=2, c=2):
        return b * q + a * r + c * x

    need(f(8, 74, 4) == 460 and f(7, 82, 6) == 442 and f(6, 96, 8) == 436, "tariff table")
    need(f(9, 62, 2) == 470 and f(9, 70, 2) == 486, "Q=9 floor and attained value")
    need(f(10, 64, 0) == 508 and f(10, 62, 4) == 512, "Q=10 cross-check values")
    need(f(8, 74, 4) - ENDPOINT == 24, "gap to the endpoint")
    # f8 < f7 iff b < 8a + 2x; f7 < f6 iff b < 14a + 2x; f8 < f6 iff b < 11a + 2x.
    for b, a, c in product(range(1, 40), range(1, 8), range(1, 8)):
        need((f(8, 74, 4, b, a, c) < f(7, 82, 6, b, a, c)) == (b < 8 * a + 2 * c), "f8 vs f7")
        need((f(7, 82, 6, b, a, c) < f(6, 96, 8, b, a, c)) == (b < 14 * a + 2 * c), "f7 vs f6")
        need((f(8, 74, 4, b, a, c) < f(6, 96, 8, b, a, c)) == (b < 11 * a + 2 * c), "f8 vs f6")
    out.append("tariff (38,2,2): Q=6 436, Q=7 442, Q=8 460 (exact); Q=9 in [470, 486]; Q>=10 > 460")

    # 7. Pinned model agreement on random walks (seeded).
    checked = check_model_agreement(model, random.Random(20261103))
    out.append(f"model agreement: {checked} seeded random walks (readout and edge cost)")

    for line in out:
        print(line)
    print(
        "PASS_EIGHT_QUERY_PATH_LOWERED_TARIFF Q8=(R74,X4) tariff=460 "
        "floors_attained_Q6_Q7_Q8 Q9_in_470_486 no_new_kappa"
    )


if __name__ == "__main__":
    main()
