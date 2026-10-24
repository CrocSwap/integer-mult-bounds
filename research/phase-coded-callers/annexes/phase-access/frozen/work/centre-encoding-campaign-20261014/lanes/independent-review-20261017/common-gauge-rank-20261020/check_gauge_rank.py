#!/usr/bin/env python3
"""Check common cover gauges and the actual four-line geometry."""

from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES / "bridge-access-20261017/permutation-cycle-20261020/CYCLE64-PROGRAMS.json"
SOURCE_SHA = "e9dadd6bc2aa58065b0079126944dd198238fb91ad55cb992d4ddf574e3989e2"
PREDECESSOR = LANES / "coherent-port/coupled-m1-terminal-20261018/AFFINE-GAUGE.md"
PREDECESSOR_SHA = "c287019ae240fbe8ad80f0170f8d90a9964ec6db3050e5a1ea9314a6c270e0ec"


def need(ok, label):
    if not ok:
        raise ValueError(label)


def basis(values):
    pivots, result = {}, []
    for value in values:
        x = value
        while x:
            k = x.bit_length()
            if k not in pivots:
                pivots[k] = x
                result.append(value)
                break
            x ^= pivots[k]
    return result


def multiply(columns, x):
    answer = 0
    for i, c in enumerate(columns):
        if x >> i & 1:
            answer ^= c
    return answer


def inverse(columns):
    values = {multiply(columns, x): x for x in range(1 << len(columns))}
    need(len(values) == 1 << len(columns), "Invertible address basis")
    return [values[1 << i] for i in range(len(columns))]


def transpose(columns):
    return [sum(((c >> i) & 1) << j for j, c in enumerate(columns))
            for i in range(len(columns))]


def common_gauge(n, lines):
    differences = [lines[0] ^ q for q in lines[1:]]
    u = basis(differences)
    columns = basis(u + [1 << i for i in range(n)])
    inv = inverse(columns)
    inv_t, columns_t = transpose(inv), transpose(columns)
    r = len(u)
    mask = (1 << r) - 1

    def w(item):
        x, z = item
        x, z = multiply(inv, x), multiply(columns_t, z)
        x, z = (x & ~mask) | (z & mask), (z & ~mask) | (x & mask)
        return multiply(columns, x), multiply(inv_t, z)

    # This phase-free Walsh has square one in binary phase space.
    image_x = []
    for i in range(n):
        need(w(w((1 << i, 0))) == (1 << i, 0), "Walsh square on X")
        need(w(w((0, 1 << i))) == (0, 1 << i), "Walsh square on Z")
        image_x.append(w((0, 1 << i))[0])
    need(len(basis(image_x)) == r, "Common gauge has the claimed rank")
    for a, b in zip(lines, lines[1:] + lines[:1]):
        for i in range(n):
            x, z = w((0, 1 << i))
            x ^= a if (z & a).bit_count() % 2 else 0
            x ^= b if (z & b).bit_count() % 2 else 0
            need(w((x, z))[0] == 0, "Conjugated ratio preserves computational Z")
    return columns, r


def rotate(pair, power):
    a, b = pair
    return [(a, b), (-b, a), (-a, -b), (b, -a)][power % 4]


def exact_state(events, start):
    values, power = {start: (1, 0)}, 0
    for kind, arg, sign in events:
        if kind == "P":
            values = {multiply(arg, x): c for x, c in values.items()}
        elif kind == "S":
            values = {x: rotate(c, sign * ((x & arg).bit_count() % 2))
                      for x, c in values.items()}
        else:
            need(kind == "C", "Exact circuit grammar")
            new = {}
            for x, (a, b) in values.items():
                for y, c in [(x, (a - sign * b, b + sign * a)),
                             (x ^ arg, (a + sign * b, b - sign * a))]:
                    old = new.get(y, (0, 0))
                    new[y] = old[0] + c[0], old[1] + c[1]
            values = {x: c for x, c in new.items() if c != (0, 0)}
            power += 1
    while power and all(a % 2 == b % 2 == 0 for a, b in values.values()):
        values = {x: (a // 2, b // 2) for x, (a, b) in values.items()}
        power -= 1
    return values, power


def main():
    need(sha256(PREDECESSOR.read_bytes()).hexdigest() == PREDECESSOR_SHA,
         "Parallel minimum-rank proof pin")
    raw = SOURCE.read_bytes()
    need(sha256(raw).hexdigest() == SOURCE_SHA, "Actual orbit payload pin")
    packet = json.loads(raw)
    ranks = []
    for record in packet["records"]:
        lines = record["cycle_lines"]
        need(len(lines) == 4, "Four orbit lines")
        need(all((a & b).bit_count() % 2 == (i == j)
                 for i, a in enumerate(lines) for j, b in enumerate(lines)),
             "Actual orthonormal quadruple")
        ranks.append(len(basis([lines[0] ^ q for q in lines[1:]])))
    need(ranks == [3] * 32, "All actual difference ranks")
    cases = 0
    for n in range(1, 5):
        points = list(range(1, 1 << n))
        for size in range(1, min(4, len(points)) + 1):
            for chosen in combinations(points, size):
                common_gauge(n, list(chosen))
                cases += 1
    columns, r = common_gauge(4, [1, 2, 4, 8])
    need(r == 3, "Canonical rank-three gauge")
    events = [("P", inverse(columns), 0)]
    for i in range(r):
        events.extend([("S", 1 << i, 1), ("C", 1 << i, 1), ("S", 1 << i, 1)])
    events.append(("P", columns, 0))
    adjoint = [(kind, inverse(arg) if kind == "P" else arg, -sign)
               for kind, arg, sign in reversed(events)]
    monomials = []
    for i in range(4):
        a, b = 1 << i, 1 << ((i + 1) % 4)
        history = adjoint + [("C", b, -1), ("C", a, 1)] + events
        table = []
        for x in range(16):
            state, power = exact_state(history, x)
            need(power == 0 and len(state) == 1, "Exact monomial column")
            y, phase = next(iter(state.items()))
            need(phase in [(1, 0), (0, 1), (-1, 0), (0, -1)], "Gaussian-unit phase")
            table.append([y, [(1, 0), (0, 1), (-1, 0), (0, -1)].index(phase)])
        need(len({y for y, _ in table}) == 16, "Exact address bijection")
        monomials.append(table)
    receipt = {
        "status": "PASS_EXACT_COMMON_GAUGE_RANK",
        "actual_source_sha256": SOURCE_SHA,
        "parallel_derivation_sha256": PREDECESSOR_SHA,
        "actual_orbits": len(ranks),
        "actual_difference_ranks": ranks,
        "small_exact_symplectic_cases": cases,
        "canonical_gauge_native_rank": r,
        "canonical_basis_columns": columns,
        "canonical_exact_monomials": monomials,
        "scope": "A single common cover Clifford conjugation. Joint field circuits remain outside this theorem.",
    }
    output = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode()
    (HERE / "CHECKS.json").write_bytes(output)
    print(receipt["status"])
    print("receipt_sha256=" + sha256(output).hexdigest())


if __name__ == "__main__":
    main()
