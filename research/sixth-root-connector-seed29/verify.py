#!/usr/bin/env python3
"""Exact sixth-root connector census and free-operator checks, standard library.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor implementation is imported. See README.md for the reduction.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "ef5f39403610d231a0c27e8a6b4f08c10209bcd6"
ZERO, ONE = (0, 0), (1, 0)
# a+b*omega, where omega**2+omega+1=0. No complex floats or finite field.
UNITS = ((1, 0), (-1, 0), (0, 1), (0, -1), (-1, -1), (1, 1))
PAIRS = ((0, 1), (2, 3), (4, 5))
TRIPLES = ((0, 2, 4), (1, 3, 5))
M = ((1, 1, 1), (1, 1, -1), (1, -1, 0))
NAMES = ("B0", "B1", "B2", "A0", "A1", "A2")
PREDECESSOR = "research/weighted-signed-connector-seed58/CERTIFICATE.json"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def neg(x):
    return (-x[0], -x[1])


def mul(x, y):
    a, b = x
    c, d = y
    return (a * c - b * d, a * d + b * c - b * d)


def inverse_unit(x):
    return next(y for y in UNITS if mul(x, y) == ONE)


def pin_inputs():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    require(pins["base_commit"] == BASE, "wrong source base")
    inputs = [x for x in pins["files"] if x["usage"] == "input"]
    require({x["path"] for x in inputs} == {
        PREDECESSOR,
        "research/weighted-signed-connector-seed58/README.md",
        "research/weighted-signed-connector-seed58/NOTICE.md",
        "research/signed-connector-obstruction/README.md",
        "research/signed-connector-obstruction/NOTICE.md",
    }, "source inventory")
    for source in inputs:
        data = (ROOT / source["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == source["sha256"],
                "source drift: " + source["path"])
    return json.loads((ROOT / PREDECESSOR).read_text())


def balanced_families():
    # Include repetition when establishing completeness of the phase multisets.
    found = {}
    for n in (2, 3):
        zero = []
        for ids in itertools.combinations_with_replacement(range(6), n):
            total = ZERO
            for u in ids:
                total = add(total, UNITS[u])
            if total == ZERO:
                zero.append(ids)
        found[str(n)] = [list(x) for x in zero]
        require(tuple(zero) == (PAIRS if n == 2 else TRIPLES),
                "incomplete zero-sum phase families")
    require(mul((0, 1), (0, 1)) == (-1, -1), "omega square")
    require((3, 0) != ZERO, "characteristic zero")
    return found


def census(extra):
    """Enumerate distinct phase-labelled tokens in all chronological orders.

    Pack three Eisenstein integers in base 32 for exact addition/hash checks.
    Each prefix coordinate has magnitude <=3; comparing two prefixes and one
    target uses digits of magnitude <=7<16. Highest-digit dominance proves
    injectivity. independent_check.py uses six explicit coordinates instead.
    """
    powers = [32 ** i for i in range(6)]
    step = {(j, u): sum(UNITS[u][k] * powers[2 * j + k] for k in (0, 1))
            for j in range(3) for u in range(6)}
    targets = [tuple(sum(c * UNITS[u][k] * powers[2 * j + k]
                          for j, c in enumerate(row) for k in (0, 1))
                     for u in range(6)) for row in M]
    hist = Counter()
    families = [TRIPLES if j == extra else PAIRS for j in range(3)]
    for assignment in itertools.product(*families):
        tokens = tuple((j, u) for j, phases in enumerate(assignment) for u in phases)
        for word in itertools.permutations(tokens):
            q = 0
            vertices = {0}
            for token in word:
                q += step[token]
                vertices.add(q)
            require(q == 0, "enumerated nonclosed source word")
            mask = 0
            for i, shifts in enumerate(targets):
                if any(p + delta in vertices for delta in shifts for p in vertices):
                    mask |= 1 << i
            hist[mask] += 1
    return {"paths": sum(hist.values()),
            "row_coverage_histogram": [hist[i] for i in range(8)],
            "feasible": hist[7]}


def identity():
    return [{(j, ()): ONE} for j in range(7)]


def execute(word, initial=None):
    """Free noncommutative operators; keep seven independent dirty rows."""
    state = identity() if initial is None else [dict(row) for row in initial]
    for kind, j, phase in word:
        phase = tuple(phase)
        require(kind in ("A", "B") and type(j) is int and 0 <= j < 3
                and phase in UNITS, "invalid query")
        source, target = (j, 6) if kind == "B" else (6, 3 + j)
        for (origin, operators), coefficient in list(state[source].items()):
            key = (origin, operators + (kind + str(j),))
            value = add(state[target].get(key, ZERO), mul(phase, coefficient))
            if value == ZERO:
                state[target].pop(key, None)
            else:
                state[target][key] = value
    return state


def wanted(matrix):
    state = identity()
    for i, row in enumerate(matrix):
        for j, c in enumerate(row):
            value = (c, 0) if isinstance(c, int) else tuple(c)
            if value != ZERO:
                state[3 + i][(j, ("B" + str(j), "A" + str(i)))] = value
    return state


def inverse(word):
    return [(kind, j, neg(phase)) for kind, j, phase in reversed(word)]


def phase_gauge(word, gamma):
    inv = inverse_unit(gamma)
    return [(kind, j, mul(phase, gamma if kind == "B" else inv))
            for kind, j, phase in word]


def orbit_replay(signed_words):
    seen = set()
    maps = 0
    gamma = UNITS[29 % 6]
    for rp, cp in itertools.product(itertools.permutations(range(3)), repeat=2):
        for rs, cs in itertools.product(itertools.product((-1, 1), repeat=3), repeat=2):
            matrix = tuple(tuple(rs[i] * cs[j] * M[rp[i]][cp[j]]
                                 for j in range(3)) for i in range(3))
            if matrix in seen:
                continue
            seen.add(matrix)
            for repeated, original in signed_words.items():
                word = []
                for kind, old_j, sign in original:
                    p, signs = (rp, rs) if kind == "A" else (cp, cs)
                    j = p.index(old_j)
                    word.append((kind, j, (sign * signs[j], 0)))
                repeat_j = (rp if repeated[0] == "A" else cp).index(int(repeated[1]))
                repeat_name = repeated[0] + str(repeat_j)
                counts = Counter(kind + str(j) for kind, j, _ in word)
                require(counts == Counter({name: 4 if name == repeat_name else 2
                                           for name in NAMES}), "repair multiplicity")
                for variant in (word, phase_gauge(word, gamma)):
                    state = execute(variant)
                    require(state == wanted(matrix), "free-operator identity")
                    require(execute(inverse(variant), state) == identity(), "literal inverse")
                    maps += 1
    require(len(seen) == 288, "obstruction orbit size")
    return {"matrices": len(seen), "forward_maps": maps, "inverse_maps": maps,
            "seed_matrix": sorted(seen)[29], "nonreal_gauge": gamma}


def semantic_controls(signed_words):
    checks = 0
    for original in signed_words.values():
        word = [(kind, j, (sign, 0)) for kind, j, sign in original]
        for i, (kind, j, phase) in enumerate(word):
            variants = [word[:i] + word[i + 1:]]
            variants += [word[:i] + [(kind, j, u)] + word[i + 1:]
                         for u in UNITS if u != phase]
            for changed in variants:
                require(execute(changed) != wanted(M), "undetected semantic mutation")
                checks += 1
    # Odd-length, fully restored nonreal maps ARE legal in this alphabet.
    odd = [("B", 0, ONE), ("A", 0, ONE), ("B", 0, (0, 1)),
           ("A", 0, (-1, 0)), ("B", 0, (-1, -1))]
    target = [[ZERO for _ in range(3)] for _ in range(3)]
    target[0][0] = (0, -1)
    require(execute(odd) == wanted(target), "valid odd phase word rejected")
    require(execute(inverse(odd), execute(odd)) == identity(), "odd word inverse")
    checks += 2
    # Use the nonreal-output fixture here: reversing and conjugating a closed
    # word with a real output happens to invert its endpoint, despite not
    # being the literal gatewise inverse. It is not a valid failure control.
    wrong = [(k, j, inverse_unit(u)) for k, j, u in reversed(odd)]
    require(execute(wrong, execute(odd)) != identity(), "wrong inverse undetected")
    checks += 1
    return {"checks": checks, "odd_restored_word": odd, "odd_target": [0, -1]}


def price_checks(signed_words):
    fixtures = [[16, 28, 40, 52, 4, 10], [1] * 6]
    fixtures += [[Fraction(1, 7) if j == i else j + 2 for j in range(6)]
                 for i in range(6)]
    minima = []
    for prices in fixtures:
        costs = [sum(prices[NAMES.index(k + str(j))] for k, j, _ in word)
                 for word in signed_words.values()]
        lower = 2 * sum(prices) + 2 * min(prices)
        require(min(costs) == lower, "weighted attaining repair")
        minima.append(str(lower))
    require(minima[0] == "308" and minima[1] == "14", "known price fixture")
    return {"fixtures": len(fixtures), "minima": minima}


def replay():
    predecessor = pin_inputs()
    require(tuple(map(tuple, predecessor["matrix"])) == M, "predecessor target")
    families = balanced_families()
    cases = {"12": census(None)}
    # Seed 29 chooses source 2 first; all three cases are completed.
    for extra in (29 % 3, 0, 1):
        cases["13_B" + str(extra)] = census(extra)
    require(cases["12"]["paths"] == 19440, "12-call coverage")
    require(all(cases["13_B" + str(j)]["paths"] == 90720 for j in range(3)),
            "13-call coverage")
    require(all(x["feasible"] == 0 for x in cases.values()), "short solution found")
    return {"status": "PASS_SIXTH_ROOT_CONNECTOR", "base_commit": BASE,
            "seed": 29, "zero_sum_families": families, "census": cases,
            "source_paths": sum(x["paths"] for x in cases.values()),
            "orbit": orbit_replay(predecessor["witnesses"]),
            "controls": semantic_controls(predecessor["witnesses"]),
            "prices": price_checks(predecessor["witnesses"]),
            "minimum_queries": 14, "new_kappa": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    actual = replay()
    expected = json.loads(args.certificate.read_text())
    require(json.loads(json.dumps(actual)) == expected, "certificate mismatch")
    print("PASS_SIXTH_ROOT_CONNECTOR source_paths=291600 minimum=14 "
          "orbit=288 free_maps=6912 controls=507 no_new_kappa")


if __name__ == "__main__":
    main()
