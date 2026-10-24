"""Replay the width refinements and compact native computation.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import deque
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as v
import compact as compact
import quadratic as q


def saved(name, data, write):
    path = HERE / name
    encoded = json.dumps(data, indent=2, sort_keys=True)+"\n"
    if write:
        path.write_text(encoded, encoding="utf-8")
    else:
        v.need(path.read_text(encoding="utf-8") == encoded, "Committed advance receipt: "+name)


def modular_inverse(matrix, p):
    n = len(matrix)
    rows = [row[:] + [int(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        k = next(k for k in range(j, n) if rows[k][j])
        rows[k], rows[j] = rows[j], rows[k]
        scale = pow(rows[j][j], -1, p)
        rows[j] = [x*scale % p for x in rows[j]]
        for k in range(n):
            if k != j:
                scale = rows[k][j]
                rows[k] = [(x-scale*y) % p for x, y in zip(rows[k], rows[j])]
    return [row[n:] for row in rows]


def one_axis_certificate(group, write):
    p, root = 65537, 256
    v.need(all(p % d for d in range(2, 257)) and root*root % p == p-1, "Prime field")
    inner = v.c.gram(group)

    def reduce(z):
        def part(x):
            return x.numerator*pow(x.denominator, -1, p)
        return (part(z.real)+root*part(z.imag)) % p

    matrix = [[sum(pow(reduce(z), f, p) for f in range(5, 9)) % p for z in row] for row in inner]
    digest = hashlib.sha256(json.dumps([[[str(z) for z in row] for row in a] for a in group]).encode()).hexdigest()
    path = HERE / "ONE-AXIS-RANK.json"
    if write:
        inverse = modular_inverse(matrix, p)
    else:
        inverse = json.loads(path.read_text())["inverse"]
    v.need(type(inverse) is list and len(inverse) == 96 and all(type(row) is list and len(row) == 96 and
           all(type(x) is int and 0 <= x < p for x in row) for row in inverse), "Modular inverse shape")
    for i, row in enumerate(matrix):
        for j, column in enumerate(zip(*inverse)):
            v.need(sum(x*y for x, y in zip(row, column)) % p == int(i == j), "One-axis inverse product")
    certificate = {"prime": p, "image_of_i": root, "widths": [5, 6, 7, 8],
                   "group_sha256": digest, "rank": 96, "inverse": inverse}
    saved("ONE-AXIS-RANK.json", certificate, write)
    return {key: value for key, value in certificate.items() if key != "inverse"}


def check_forms(rng):
    count = 0
    units = (q.G(1), q.G("i"), q.G(-1), q.G("-i"))
    for m in range(8):
        for _ in range(80):
            phase = q.Phase(m)
            phase.constant = rng.randrange(4)
            phase.linear = [rng.randrange(4) for _ in range(m)]
            phase.cross = {(i, j) for i in range(m) for j in range(i+1, m) if rng.randrange(2)}
            equations = [rng.randrange(1 << (m+1)) for _ in range(rng.randrange(m+1))]
            expected = q.G(0)
            for x in range(1 << m):
                if any((e & 1) ^ (((e >> 1) & x).bit_count() % 2) for e in equations):
                    continue
                exponent = phase.constant+sum(a*((x >> i) & 1) for i, a in enumerate(phase.linear))
                exponent += 2*sum(((x >> i) & 1)*((x >> j) & 1) for i, j in phase.cross)
                expected = expected+units[exponent % 4]
            v.need(q.gauss_sum(phase, equations) == expected, "Exhaustive constrained quadratic sum")
            count += 1
    return count


def native_words():
    bank = {v.c.key(v.c.identity(2)): v.native.ident(1)}
    queue = deque(bank.values())
    generators = (v.native.cgate(1, 1), v.native.diag(1, (1,)))
    while queue:
        op = queue.popleft()
        for generator in generators:
            new = op.then(generator)
            label = v.c.key(v.source_matrix(new))
            if label not in bank:
                bank[label] = new
                queue.append(new)
    v.need(len(bank) == 96, "Native word group closure")
    return list(bank.values())


def check_native(rng):
    words = native_words()
    for n in (2, 3):
        for _ in range(16):
            op = v.native.ident(n)
            for _ in range(8):
                raw = [rng.randrange(1 << n) for _ in range(n)]
                rows = [sum(((raw[min(i, j)] >> max(i, j)) & 1) << j for j in range(n)) for i in range(n)]
                alpha = [((rows[i] >> i) & 1)+2*rng.randrange(2) for i in range(n)]
                source, target = rng.sample(range(n), 2)
                permutation = [1 << j for j in range(n)]
                permutation[target] ^= 1 << source
                op = op.then(v.native.diag(n, rows, alpha)).then(v.native.perm(n, permutation))
                op = op.then(v.native.cgate(n, rng.randrange(1 << n), rng.choice((-1, 1))))
                op = op.then(v.native.xgate(n, rng.randrange(1 << n)))
            words.append(op)
    entries, traces, partials = 0, 0, 0
    for op in words:
        matrix = v.source_matrix(op)
        paths = q.Paths(op.n, op.circuit)
        inverse = q.Paths(op.n, q.inverse_circuit(op.n, op.circuit))
        star = v.c.adjoint(matrix)
        d = 1 << op.n
        v.need(paths.trace() == sum((matrix[j][j] for j in range(d)), q.G(0)), "Native trace phase")
        traces += 1
        for x in range(d):
            for y in range(d):
                v.need(paths.entry(x, y) == matrix[x][y] and inverse.entry(x, y) == star[x][y], "Native entry phase")
                entries += 2
        for k in range(op.n+1):
            xp = [rng.randrange(2) for _ in range(k)]
            yp = [rng.randrange(2) for _ in range(op.n-k)]
            expected = sum((v.c.conjugate(matrix[x][y])*star[x][y]
                            for x in range(d) for y in range(d)
                            if all(((x >> j) & 1) == bit for j, bit in enumerate(xp)) and
                            all(((y >> j) & 1) == bit for j, bit in enumerate(yp))), q.G(0))
            v.need(q.partial_inner(paths, inverse, xp, yp) == expected, "Native partial inner product")
            partials += 1
    return {"native_words": len(words), "native_entries": entries, "native_traces": traces,
            "partial_inner_products": partials}


def check_programs(rng):
    count, witnesses, relations = 0, 0, 0
    for n in range(3):
        ops = {"I": v.native.ident(n), "iI": v.native.Op(n, v.native.identity(n), [("phase", 1)])}
        if n:
            ops.update(C=v.native.cgate(n, (1 << n)-1), H=v.native.hadamard(n, range(n)),
                       S=v.native.diag(n, tuple(1 << j for j in range(n))))
        for _ in range(16):
            program = []
            for _ in range(8):
                kind = rng.choice(("query", "apply", "add", "scale", "swap"))
                instruction = {"op": kind, "dst": rng.randrange(3)}
                if kind in ("query", "add", "swap"):
                    instruction["src"] = rng.randrange(3)
                if kind in ("query", "apply"):
                    instruction.update(symbol=rng.choice(list(ops)), inverse=bool(rng.randrange(2)))
                if kind in ("scale", "query", "add"):
                    instruction["coefficient"] = rng.choice(("1", "-1", "i", "1/2"))
                program.append(instruction)
            problem = {"axes": n, "roles": 3, "operators": {s: o.circuit for s, o in ops.items()},
                       "program": program, "reference": []}
            dense = v.example({s: v.source_matrix(o) for s, o in ops.items()}, program, axes=n)
            _, expected_entries = v.c.compile_difference(dense)
            expected = {(output, source): {v.c.key(a): coefficient for coefficient, a in terms}
                        for output, source, terms in expected_entries}
            actual = {}
            for output, source, coefficients, paths, _ in compact.residuals(problem):
                matrices = [tuple(tuple(path.entry(x, y) for y in range(1 << n)) for x in range(1 << n)) for path in paths]
                actual[output, source] = {v.c.key(a): coefficient for coefficient, a in zip(coefficients, matrices)}
            v.need(actual == expected, "Compact complete endpoint")
            certificate = compact.certify(problem)
            v.need(certificate["equivalent_at_all_positive_widths"] == (not expected), "Compact decision")
            if "failure" in certificate:
                f = certificate["failure"]
                w = f["witness"]
                value = v.independent.discrepancy(dense, f["output_role"], f["input_role"], w["output_tuple"], w["input_tuple"])
                v.need(value != 0 and str(value) == w["discrepancy"], "Compact literal witness")
                witnesses += 1
            count += 1
    for n in (1, 2, 3):
        ops = {"C": v.native.cgate(n, (1 << n)-1), "H": v.native.hadamard(n, range(n)),
               "phase": v.native.Op(n, v.native.identity(n), [("phase", n)])}
        cases = [([{"op": "apply", "dst": 2, "symbol": "C"}]*4, []),
                 ([{"op": "apply", "dst": 1, "symbol": "H"}]*2,
                  [{"op": "apply", "dst": 1, "symbol": "phase"}]),
                 ([{"op": "apply", "dst": 0, "symbol": "C"},
                   {"op": "apply", "dst": 0, "symbol": "C", "inverse": True}], [])]
        for program, reference in cases:
            problem = {"axes": n, "roles": 3, "operators": {s: o.circuit for s, o in ops.items()},
                       "program": program, "reference": reference}
            dense = v.example({s: v.source_matrix(o) for s, o in ops.items()}, program, reference, axes=n)
            v.need(compact.certify(problem)["equivalent_at_all_positive_widths"] and
                   v.c.certify(dense)["equivalent_at_all_positive_widths"], "Compact exact native relation")
            relations += 1
    phase_trap = {"axes": 1, "roles": 1, "operators": {"iI": [("phase", 1)]},
                  "program": [{"op": "apply", "dst": 0, "symbol": "iI"}],
                  "reference": [{"op": "scale", "dst": 0, "coefficient": "i"}]}
    norms = compact.certify(phase_trap)["failure"]["normalized_squared_norms"]
    v.need(norms[0] == "0" and Q(norms[1]) > 0, "Compact phase stays inside tensor")
    return {"complete_programs": count, "literal_witnesses": witnesses, "exact_native_relations": relations,
            "scalar_phase_traps": 1}


def verify(write=False):
    rng = random.Random(5376)
    code = {q.parity_sum(row for j, row in enumerate((255, 240, 204, 170)) if mask >> j & 1) for mask in range(16)}
    v.need(len(code) == 16 and all(x.bit_count() % 4 == 0 for x in code), "Doubly even code")
    for y in range(256):
        v.need(sum((-1)**((x & y).bit_count() % 2) for x in code) == 16*int(y in code), "Code Fourier invariant")
    h = v.source_matrix(v.native.hadamard(1, [0]))
    v.need(h == ((q.G("1/2+1/2i"), q.G("1/2+1/2i")),
                 (q.G("1/2+1/2i"), q.G("-1/2-1/2i"))) and v.c.power(h[0][0], 8) == q.G("1/16"),
           "Eight-copy native phase")
    previous = None
    for n in range(65):
        polynomial = v.c.cutoff_polynomial(n)
        norm = sum(abs(x) for x in polynomial)
        v.need(norm <= Q(77, 75) and sum(x for x in polynomial if x > 0) <= Q(76, 75), "Improved filter bound")
        descending = list(reversed(polynomial[1::4]))
        v.need(all((x > 0) == ((-1)**(j*(j+3)//2) == 1) for j, x in enumerate(descending)), "Filter coefficient signs")
        if n >= 2:
            v.need(norm < previous, "Filter norm decreases")
        previous = norm
    forms = check_forms(rng)
    rank_certificate = one_axis_certificate(v.group_one_axis(), write)
    native = check_native(rng)
    programs = check_programs(rng)
    large = []
    for n in (64, 65):
        h = v.native.hadamard(n, range(n))
        operators = {"H": h.circuit, "iI": [("phase", 1)]}
        if n == 64:
            program = [{"op": "query", "src": 0, "dst": 1, "symbol": "H"}]
            reference = []
        else:
            program = [{"op": "apply", "dst": 0, "symbol": "H"}]*2
            reference = [{"op": "apply", "dst": 0, "symbol": "iI"}]
        problem = {"axes": n, "roles": 2, "operators": operators, "program": program, "reference": reference}
        certificate = compact.certify(problem)
        v.need(certificate["equivalent_at_all_positive_widths"] == (n == 65), "Large native decision")
        if n == 64:
            v.need(certificate["failure"]["witness"] == {"width": 1, "output_tuple": [0], "input_tuple": [0],
                   "discrepancy": "1/4294967296"}, "Large literal Hadamard entry")
        saved(f"examples/native-{n}.json", problem, write)
        saved(f"examples/native-{n}.certificate.json", certificate, write)
        large.append({"axes": n, "base_dimension": str(1 << n), "equivalent": n == 65})
    controls = []
    for label, function in [
        ("singular permutation", lambda: q.Paths(2, [("P", [1, 1])])),
        ("diagonal parity", lambda: q.Paths(1, [("D", [1], [0])])),
        ("asymmetric diagonal", lambda: q.Paths(2, [("D", [2, 0], [0, 0])])),
        ("wrong C sign", lambda: q.Paths(1, [("C", 1, 0)])),
        ("unknown gate", lambda: q.Paths(1, [("H", 0)])),
        ("coordinate out of range", lambda: q.Paths(1, []).entry(2, 0)),
        ("invalid prefix", lambda: q.partial_inner(q.Paths(1, []), q.Paths(1, []), [2])),
        ("negative axes", lambda: q.Paths(-1, [])),
    ]:
        try:
            function()
        except ValueError:
            controls.append(label)
        else:
            raise ValueError("Accepted control: "+label)
    receipt = {"status": "PASS_CLIFFORD_ADVANCES_NO_NEW_KAPPA", "general_test_widths": "8n-3 through 8n+4 for n>=2",
               "stable_separation": "75/76", "filter_axis_counts": 65, "code_fourier_values": 256,
               "one_axis": rank_certificate, "exhaustive_quadratic_forms": forms,
               **native, **programs, "large_native_programs": large, "controls": controls}
    saved("ADVANCES-RESULT.json", receipt, write)
    print(receipt["status"])
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate the advance receipts")
    verify(parser.parse_args().write)
