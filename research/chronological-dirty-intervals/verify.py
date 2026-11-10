#!/usr/bin/env python3
"""Exact finite corroboration, @CubeJerry + OpenAI Codex, Apache-2.0.

No predecessor code, symbolic package, squarefree quotient or float is used.
The all-size proof is PROOF.md, not extrapolation from this finite program.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INTERVAL_SIZES = (1, 2, 3, 5, 8, 11, 16)
MAX_N = 64


def need(ok, message):
    if not ok:
        raise ValueError(message)


def envelope(h):
    need(isinstance(h, int) and 0 <= h <= 10000, "height capacity")
    return h*h//2+h+2


def scratch_bound(h):
    return (h+1)*(h+1)//2


def add(a, b):
    out = a.copy()
    for word, coefficient in b.items():
        out[word] = out.get(word, 0)+coefficient
        if not out[word]:
            del out[word]
    return out


def multiply_poly(a, b):
    out = {}
    for u, c in a.items():
        for v, d in b.items():
            word = u+v
            out[word] = out.get(word, 0)+c*d
            if not out[word]:
                del out[word]
    return out


def identity(d):
    return [[{(): 1} if i == j else {} for j in range(d)] for i in range(d)]


def multiply(a, b):
    d = len(a)
    out = [[{} for _ in range(d)] for _ in range(d)]
    for i, row in enumerate(a):
        for j, left in enumerate(row):
            if left:
                for k, right in enumerate(b[j]):
                    if right:
                        out[i][k] = add(out[i][k], multiply_poly(left, right))
    return out


def row_mass(row):
    return sum(abs(c) for entry in row for c in entry.values())


def forward(matrix, event):
    x, y, factor, sign = event
    out = [row.copy() for row in matrix]
    out[y] = [add(a, {(factor,)+word: sign*c for word, c in b.items()})
              for a, b in zip(matrix[y], matrix[x])]
    return out


def inverse_prefix(matrix, event):
    x, y, factor, sign = event
    out = [row.copy() for row in matrix]
    for row in out:
        row[x] = add(row[x], {word+(factor,): -sign*c for word, c in row[y].items()})
    return out


def emit(n, sign=1, start=0, source=0, target=1, depth=0):
    need(isinstance(n, int) and 1 <= n <= MAX_N, "factor count capacity")
    need(sign in (-1, 1), "word sign")
    events = []
    stack = [(start, n, source, target, depth, sign)]
    while stack:
        lo, count, x, y, level, direction = stack.pop()
        if count == 1:
            events.append((x, y, lo, direction))
            continue
        left = count//2
        z = level+2
        children = [(lo, left, x, z, level+1, 1),
                    (lo+left, count-left, z, y, level+1, 1),
                    (lo, left, x, z, level+1, -1),
                    (lo+left, count-left, z, y, level+1, -1)]
        if direction == -1:
            children = [(*child[:-1], -child[-1]) for child in reversed(children)]
        stack.extend(reversed(children))
    return events


def prefixes(events, d):
    p, q = identity(d), identity(d)
    result = [(p, q)]
    for event in events:
        p, q = forward(p, event), inverse_prefix(q, event)
        result.append((p, q))
    return result


def check_entries(matrix):
    need(all(len(p) <= 1 and all(abs(c) == 1 for c in p.values())
             for row in matrix for p in row), "prefix unit-entry invariant")


def check_scratch_pairs(matrix):
    d = len(matrix)
    need(all(matrix[i][i] == {(): 1} for i in range(d)), "identity diagonal")
    need(not any(matrix[i][j] and matrix[j][i]
                 for i in range(2, d) for j in range(i+1, d)), "opposite scratch support")


def check_source_occupancy(matrix):
    occupied = [bool(matrix[i][0]) for i in range(1, len(matrix))]
    need(not any(a and b for a, b in zip(occupied, occupied[1:])),
         "adjacent inverse source occupancy")


def prefix_census():
    from scalar_oracle import prefix
    boundaries, identities = 0, 0
    maxima = {}
    for n in range(1, MAX_N+1):
        h = (n-1).bit_length()
        events = emit(n)
        need(emit(n, -1) == [(x, y, f, -s) for x, y, f, s in reversed(events)],
             "literal negative word")
        data = prefixes(events, h+2)
        for t, (p, q) in enumerate(data):
            boundaries += 1
            for matrix in (p, q):
                check_entries(matrix)
                check_scratch_pairs(matrix)
                need(matrix[0] == identity(h+2)[0], "protected source")
                need(all(matrix[i][1] == ({(): 1} if i == 1 else {})
                         for i in range(h+2)), "unread target")
            check_source_occupancy(q)
            mass = sum(row_mass(row) for row in q[2:])
            need(mass <= scratch_bound(h), "inverse scratch mass")
            maxima[str(h)] = max(maxima.get(str(h), 0), mass)
            if t in {0, 1, len(events)//2, len(events)-1, len(events)}:
                need(multiply(p, q) == identity(h+2), "prefix inverse identity")
                negatives = tuple(i for i in range(n) if i % 3 == 1)
                evaluated = [[sum(c*(-1)**sum(f in negatives for f in word)
                                  for word, c in entry.items()) for entry in row] for row in p]
                need(prefix(n, t, negatives) == evaluated, "independent scalar/formal prefix agreement")
                identities += 1
        endpoint = identity(h+2)
        endpoint[1][0] = {tuple(range(n-1, -1, -1)): 1}
        need(data[-1][0] == endpoint, "full arbitrary-dirty endpoint")
    return {"factor_counts": [1, MAX_N], "positive_prefix_boundaries": boundaries,
            "sampled_inverse_identities": identities,
            "maximum_inverse_scratch_mass_by_height": maxima}


def interval_census():
    results, total = [], 0
    for n in INTERVAL_SIZES:
        h = (n-1).bit_length()
        best = 0
        for sign in (1, -1):
            events = emit(n, sign)
            for a in range(len(events)):
                matrix = identity(h+2)
                for event in events[a:]:
                    matrix = forward(matrix, event)
                    mass = max(map(row_mass, matrix))
                    need(mass <= envelope(h), "sharp interval envelope")
                    need(all(len(word) == len(set(word)) for row in matrix
                             for entry in row for word in entry), "squarefree surviving word")
                    best = max(best, mass)
                    total += 1
        results.append({"n": n, "h": h, "maximum": best, "bound": envelope(h)})
    return {"both_orientations_nonempty_intervals": total, "cases": results}


def shear(d, x, y, polynomial):
    out = identity(d)
    out[y][x] = polynomial
    return out


def adjust(matrix, i, j, polynomial):
    out = [row.copy() for row in matrix]
    out[i][j] = add(out[i][j], polynomial)
    return out


def phase_census():
    counts = {name: 0 for name in ("01", "12", "23", "02", "13", "03")}
    for n in (2, 3, 4, 5, 8, 11, 16):
        d = (n-1).bit_length()+2
        mid = n//2
        left = emit(mid, start=0, source=0, target=2, depth=1)
        right = emit(n-mid, start=mid, source=2, target=1, depth=1)
        ls, rs = prefixes(left, d), prefixes(right, d)
        parent = prefixes(emit(n), d)
        u, ui = ls[-1]
        v, vi = rs[-1]
        ab = {tuple(range(n-1, -1, -1)): 1}
        b = {tuple(range(mid-1, -1, -1)): 1}
        a = {tuple(range(n-1, mid-1, -1)): 1}
        lu, lv = len(left), len(right)
        cuts_l = range(lu+1) if n <= 5 else sorted({0, 1, lu//2, lu-1, lu})
        cuts_r = range(lv+1) if n <= 5 else sorted({0, 1, lv//2, lv-1, lv})
        for name in counts:
            first = cuts_l if name[0] in "02" else cuts_r
            second = cuts_l if name[1] in "02" else cuts_r
            for ac in first:
                for bc in second:
                    pa, pai = (ls if name[0] in "02" else rs)[ac]
                    pb, pbi = (ls if name[1] in "02" else rs)[bc]
                    times = (ac, lu+ac, 2*lu+lv-ac, 2*(lu+lv)-ac)
                    ends = (bc, lu+bc, 2*lu+lv-bc, 2*(lu+lv)-bc)
                    s, t = times[int(name[0])], ends[int(name[1])]
                    actual = multiply(parent[t][0], parent[s][1])
                    reverse = multiply(parent[s][0], parent[t][1])
                    if name == "01":
                        predicted = multiply(pb, multiply(u, pai))
                        backward = multiply(multiply(pa, ui), pbi)
                    elif name == "12":
                        predicted = multiply(multiply(pb, ui), multiply(v, pai))
                        backward = multiply(multiply(pa, vi), multiply(u, pbi))
                    elif name == "23":
                        predicted = multiply(multiply(pb, vi), pai)
                        backward = multiply(pa, multiply(v, pbi))
                    elif name == "02":
                        predicted, backward = multiply(pb, pai), multiply(pa, pbi)
                        row, backrow = multiply(u, pai)[2], multiply(u, pbi)[2]
                        for j in range(d):
                            predicted = adjust(predicted, 1, j, multiply_poly(a, row[j]))
                            backward = adjust(backward, 1, j, multiply_poly({w: -c for w, c in a.items()}, backrow[j]))
                    elif name == "13":
                        predicted, backward = multiply(pb, pai), multiply(pa, pbi)
                        col, backcol = multiply(pb, vi), multiply(pa, vi)
                        for i in range(d):
                            predicted = adjust(predicted, i, 0, multiply_poly(col[i][2], {w: -c for w, c in b.items()}))
                            backward = adjust(backward, i, 0, multiply_poly(backcol[i][2], b))
                    else:
                        predicted = adjust(multiply(pb, pai), 1, 0, ab)
                        backward = adjust(multiply(pa, pbi), 1, 0, {w: -c for w, c in ab.items()})
                    need(predicted == actual and backward == reverse, "phase identity "+name)
                    counts[name] += 2
    return {"both_orders_identity_checks": counts,
            "all_child_cuts_n": [2, 3, 4, 5], "five_child_cuts_n": [8, 11, 16]}


def controls():
    passed = []
    def rejects(name, fn):
        try:
            fn()
        except ValueError:
            passed.append(name)
        else:
            raise ValueError("control accepted: "+name)
    bad = identity(4)
    bad[2][0] = {(0,): -1}
    bad[3][0] = {(1,): -1}
    rejects("adjacent_source_bits", lambda: check_source_occupancy(bad))
    bad_pair = identity(4)
    bad_pair[2][3], bad_pair[3][2] = {(0,): 1}, {(1,): 1}
    rejects("reciprocal_scratch_entries", lambda: check_scratch_pairs(bad_pair))
    oversized = identity(3)
    oversized[2][0] = {(0,): 2}
    rejects("oversized_prefix_entry", lambda: check_entries(oversized))
    for value in (0, 65):
        rejects("factor_count_"+str(value), lambda value=value: emit(value))
    rejects("invalid_sign", lambda: emit(2, 0))
    rejects("invalid_height", lambda: envelope(-1))
    positive = prefixes(emit(8), 5)[6][0]
    need(sum(row_mass(r) for r in positive[2:]) == 9 > scratch_bound(3),
         "positive-prefix countercontrol")
    passed.append("inverse_direction_is_essential")
    events = emit(4)
    wrong = [(x, y, f, -s) for x, y, f, s in events]
    need(prefixes(events+wrong, 4)[-1][0] != identity(4), "wrong inverse order control")
    passed.append("wrong_inverse_order")
    altered = events.copy()
    x, y, f, s = altered[5]
    altered[5] = (x, y, f, -s)
    need(prefixes(altered, 4)[-1][0] != prefixes(events, 4)[-1][0], "restoration mutation")
    passed.append("changed_leaf_sign")
    need(multiply_poly({(0,): 1}, {(1,): 1}) != multiply_poly({(1,): 1}, {(0,): 1}),
         "noncommuting control")
    need(multiply_poly({(0,): 1}, {(0,): 1}) == {(0, 0): 1}, "no squarefree quotient")
    passed.extend(["factor_order_retained", "repeated_factor_retained"])
    return passed


def literal_witnesses():
    cases = []
    for h in range(1, 7):
        n = 1 << h
        negatives = {n-(1 << k)-1 for k in range(h-1)}
        a, b = 3*4**(h-1)//5, (4**h+2)//3
        matrix = identity(h+2)
        for event in emit(n)[a:b]:
            matrix = forward(matrix, event)
        row = [sum(c*(-1)**sum(f in negatives for f in word)
                   for word, c in entry.items()) for entry in matrix[1]]
        expected = [(-1)**(h-1)*(1+h//2), 1]
        expected += [j*(-1)**(h+j) for j in range(1, h+1)]
        need(row == expected, "literal lower-family row")
        need(row_mass(matrix[1]) == sum(map(abs, row)) == envelope(h),
             "literal scalar attainment of free coefficient mass")
        cases.append({"h": h, "n": n, "cuts": [a, b], "target_row": row})
    return cases


def certificate():
    from scalar_oracle import verify_witnesses
    return {"schema_version": 1,
            "claim": "finite corroboration of the scoped written sharp-envelope proof",
            "prefixes": prefix_census(), "intervals": interval_census(),
            "phase_formulas": phase_census(), "scalar_witnesses": verify_witnesses(),
            "literal_witnesses": literal_witnesses(),
            "controls": controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="explicit authoring output; default is read-only")
    args = parser.parse_args()
    result = certificate()
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        expected = json.loads((HERE/"CERTIFICATE.json").read_text())
        need(result == expected, "committed mathematical certificate mismatch")
    bindings = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(HERE.iterdir()) if p.is_file() and p.suffix in (".py", ".md", ".json")}
    print(json.dumps({"status": "PASS_CHRONOLOGICAL_DIRTY_INTERVALS", "bindings": bindings,
                      "prefix_boundaries": result["prefixes"]["positive_prefix_boundaries"],
                      "intervals": result["intervals"]["both_orientations_nonempty_intervals"]}, sort_keys=True))


if __name__ == "__main__":
    main()
