"""Check the trace proof, native source and literal tensor failures.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter, deque
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def source_integrity():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    pairs = {"fields.py": "research/universal-dirty-certificates/fields.py",
             "clifford_exact.py": "research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py"}
    for local, original in pairs.items():
        record = next(item for item in sources["files"] if item["path"] == original)
        need(hashlib.sha256((HERE / "vendor" / local).read_bytes()).hexdigest() == record["sha256"], "Frozen source: "+local)


source_integrity()
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))
import certify as c
import check_witness as independent
import clifford_exact as native
G = c.G


def source_matrix(op):
    columns = []
    for j in range(1 << op.n):
        values, exponent = op.zero_state(j)
        columns.append([G.pair(Q(a, 1 << exponent), Q(b, 1 << exponent)) for a, b in values])
    return tuple(tuple(column[i] for column in columns) for i in range(1 << op.n))


def example(operators, program, reference=(), axes=1, roles=3):
    return {"axes": axes, "roles": roles, "operators": {name: [[str(x) for x in row] for row in a] for name, a in operators.items()},
            "program": list(program), "reference": list(reference)}


def group_one_axis():
    generators = [native.cgate(1, 1), native.diag(1, (1,))]
    bank = {c.key(c.identity(2)): (c.identity(2), native.ident(1))}
    queue = deque(bank.values())
    edges = 0
    while queue:
        a, op = queue.popleft()
        for generator in generators:
            product = c.multiply(source_matrix(generator), a)
            label = c.key(product)
            edges += 1
            if label not in bank:
                following = product, op.then(generator)
                bank[label] = following
                queue.append(following)
    need(len(bank) == 96 and edges == 192, "Complete group closure")
    for a, op in bank.values():
        need(a == source_matrix(op), "Literal native word phase")
        c.validate_operator(a, 1)
    return [a for a, _ in bank.values()]


def kron(a, b):
    return tuple(tuple(x*y for x in row_a for y in row_b) for row_a in a for row_b in b)


def dense_tensor_norm(terms, width):
    d = len(terms[0][1])**width
    out = [[G(0) for _ in range(d)] for _ in range(d)]
    for coefficient, a in terms:
        tensor = ((G(1),),)
        for _ in range(width):
            tensor = kron(tensor, a)
        for i in range(d):
            for j in range(d):
                out[i][j] = out[i][j]+coefficient*tensor[i][j]
    return sum(c.norm2(z) for row in out for z in row)/d


def dense_program(problem, instructions, width):
    d, r = (1 << problem["axes"])**width, problem["roles"]
    count = d*r
    rows = [[[G(int(i == role*d+j)) for i in range(count)] for j in range(d)] for role in range(r)]
    lifted = {}
    for name, encoded in problem["operators"].items():
        a = tuple(tuple(G(x) for x in row) for row in encoded)
        tensor = ((G(1),),)
        for _ in range(width):
            tensor = kron(tensor, a)
        lifted[name, False], lifted[name, True] = tensor, independent.star(tensor)
    for op in instructions:
        kind, dst = op["op"], op["dst"]
        src = op.get("src", dst)
        if kind == "swap":
            rows[dst], rows[src] = rows[src], rows[dst]
        elif kind == "scale":
            rows[dst] = [[G(op["coefficient"])*x for x in row] for row in rows[dst]]
        else:
            image = rows[src]
            if kind in ("apply", "query"):
                a = lifted[op["symbol"], op.get("inverse", False)]
                image = [[sum((a[j][k]*rows[src][k][i] for k in range(d)), G(0)) for i in range(count)] for j in range(d)]
            if kind == "apply":
                rows[dst] = image
            else:
                rows[dst] = [[x+G(op.get("coefficient", 1))*y for x, y in zip(a, b)] for a, b in zip(rows[dst], image)]
    return rows


def independent_residual(problem):
    bank = independent.matrices(problem)
    d, r = 1 << problem["axes"], problem["roles"]
    result = {}
    for input_role in range(r):
        left = independent.word_endpoint(problem, problem["program"], input_role)
        right = independent.word_endpoint(problem, problem["reference"], input_role)
        for output in range(r):
            row = {}
            for sign, words in [(1, left[output]), (-1, right[output])]:
                for word, coefficient in words.items():
                    a = independent.evaluate_word(word, bank, d)
                    c.accumulate(row, (output, input_role, c.key(a)), coefficient*sign)
            result.update(row)
    return result


def verify(write=False):
    rng = random.Random(20261023)
    group = group_one_axis()
    C, S = source_matrix(native.cgate(1, 1)), source_matrix(native.diag(1, (1,)))
    H, I = source_matrix(native.hadamard(1, [0])), c.identity(2)
    phase_i = tuple(tuple(G("i")*z for z in row) for row in I)
    need(c.multiply(H, H) == phase_i, "Source Hadamard phase")
    operators = {"C": C, "S": S, "H": H, "iI": phase_i}
    zero_axis = example({str(k): ((c.power(G("i"), k),),) for k in range(4)},
                        [{"op": "query", "src": 0, "dst": 1, "symbol": str(k), "coefficient": "1/4"}
                         for k in range(4)], axes=0, roles=2)
    zero_certificate = c.certify(zero_axis)
    need(not zero_certificate["equivalent_at_all_positive_widths"], "Zero-axis scalar group")
    need(zero_certificate["failure"]["normalized_squared_norms"] == ["0", "0", "0", "1"], "Zero-axis scalar group")
    independent.check(zero_axis, zero_certificate)
    need(c.certify(example({}, [], axes=0, roles=1))["equivalent_at_all_positive_widths"], "Empty zero-axis program")
    polynomial_values = 0
    for n in range(13):
        polynomial = c.cutoff_polynomial(n)
        need(len(polynomial) == 8*n+5 and polynomial[0] == 0 and sum(polynomial) == 1, "Polynomial endpoints")
        need(sum(abs(b) for b in polynomial) < Q(8, 7), "Coefficient norm")
        need(sum(b for b in polynomial if b > 0) < Q(15, 14), "Positive coefficient mass")
        alphabet = [G(0)] + [c.power(G("i"), k)*c.power(G("1+1i"), d)/(1 << n) for d in range(2*n+1) for k in range(4)]
        for z in alphabet:
            value = G(0)
            for b in reversed(polynomial):
                value = value*z+b
            need(value == int(z == 1), "Trace-filter value")
            polynomial_values += 1
    source_columns = 192
    native_fixtures = []
    for n in range(1, 5):
        for q in range(1, 1 << n):
            for sign in (-1, 1):
                a = source_matrix(native.cgate(n, q, sign))
                first, second = G.pair(Q(1, 2), Q(sign, 2)), G.pair(Q(1, 2), Q(-sign, 2))
                expected = tuple(tuple(first if i == j else second if i == (j ^ q) else G(0) for j in range(1 << n)) for i in range(1 << n))
                need(a == expected, "Source C column formula")
                c.validate_operator(a, n)
                source_columns += 1 << n
                if n <= 3:
                    native_fixtures.append((n, a))
    for sign in (-1, 1):
        op = native.cgate(9, 173, sign)
        for j in range(512):
            values, den = op.zero_state(j)
            expected = [(0, 0)]*512
            expected[j], expected[j ^ 173] = (1, sign), (1, -sign)
            need(den == 1 and values == expected, "Nine-axis source column")
            source_columns += 1
    entangling_trace_cases = 0
    for n in (2, 3):
        for _ in range(24):
            op = native.ident(n)
            for _ in range(4):
                source_axis, target_axis = rng.sample(range(n), 2)
                rows = [1 << j for j in range(n)]
                rows[target_axis] ^= 1 << source_axis
                phase_rows = tuple(1 << j if j == target_axis else 0 for j in range(n))
                op = op.then(native.cgate(n, rng.randrange(1, 1 << n), rng.choice([-1, 1])))
                op = op.then(native.diag(n, phase_rows)).then(native.perm(n, rows))
            a = source_matrix(op)
            need(tuple(c.validate_operator(a, n)) == op.tab, "Entangling source tableau")
            trace = sum((a[j][j] for j in range(1 << n)), G(0))
            fixed_sum = 0
            for x in range(1 << n):
                for z in range(1 << n):
                    phase = (x & z).bit_count() % 4
                    u, v, p = native.apply(op.tab, (x, z, phase))
                    if (u, v) == (x, z):
                        need((p-phase) % 4 in (0, 2), "Hermitian Pauli sign")
                        fixed_sum += 1 if p == phase else -1
            need(c.norm2(trace) == fixed_sum, "Pauli conjugation trace identity")
            alphabet = [G(0)] + [c.power(G("i"), k)*c.power(G("1+1i"), d) for d in range(2*n+1) for k in range(4)]
            need(trace in alphabet, "Entangling trace alphabet")
            native_fixtures.append((n, a))
            source_columns += 1 << n
            entangling_trace_cases += 1
    dense_norm_cases = 0
    for n in (1, 2):
        pool = group if n == 1 else list({c.key(a): a for k, a in native_fixtures if k == n}.values())
        for _ in range(12):
            selected = rng.sample(pool, 4)
            terms = [(G(rng.choice([-2, -1, "i", "1/2", "1/2-1/2i"])), a) for a in selected]
            inner = c.gram(selected)
            for width in range(1, 4 if n == 1 else 3):
                need(c.energy([x for x, _ in terms], inner, width) == dense_tensor_norm(terms, width), "Independent dense norm")
                dense_norm_cases += 1
            result = c.analyze(n, terms)
            w = result["witness"]
            need(c.tensor_entry([x for x, _ in terms], selected, w["output_tuple"], w["input_tuple"]) == G(w["discrepancy"]) != 0, "Tensor entry")
    differential_cases = literal_witnesses = full_column_cases = 0
    for trial in range(72):
        instructions = []
        for _ in range(8):
            kind = rng.choice(["add", "query", "apply", "scale", "swap"])
            op = {"op": kind, "dst": rng.randrange(3)}
            if kind in ("add", "query", "swap"):
                op["src"] = rng.randrange(3)
            if kind in ("query", "apply"):
                op.update(symbol=rng.choice(list(operators)), inverse=bool(rng.randrange(2)))
            if kind in ("add", "query", "scale"):
                op["coefficient"] = rng.choice([-1, 0, 1, "1/2", "i"])
            instructions.append(op)
        problem = example(operators, instructions, instructions if trial % 3 == 0 else [])
        _, differences = c.compile_difference(problem)
        observed = {(o, i, c.key(a)): x for o, i, terms in differences for x, a in terms}
        need(observed == independent_residual(problem), "Signed-word complete endpoint")
        differential_cases += 1
        if trial < 12:
            for width in (1, 2):
                left = dense_program(problem, problem["program"], width)
                right = dense_program(problem, problem["reference"], width)
                lookup = {(o, i): terms for o, i, terms in differences}
                d = 2**width
                for o in range(3):
                    for i in range(3):
                        terms = lookup.get((o, i), [])
                        for x in range(d):
                            for y in range(d):
                                xt = [(x >> k) & 1 for k in reversed(range(width))]
                                yt = [(y >> k) & 1 for k in reversed(range(width))]
                                value = c.tensor_entry([a for a, _ in terms], [b for _, b in terms], xt, yt)
                                need(value == left[o][x][i*d+y]-right[o][x][i*d+y], "Full tensor program column")
                full_column_cases += 1
        if trial < 24:
            certificate = c.certify(problem)
            if not certificate["equivalent_at_all_positive_widths"]:
                independent.check(problem, certificate)
                literal_witnesses += 1
    positive = example(operators, [{"op": "apply", "dst": 1, "symbol": "H"}]*2,
                       [{"op": "apply", "dst": 1, "symbol": "iI"}])
    need(c.certify(positive)["equivalent_at_all_positive_widths"], "Native relation")
    phase_trap = example(operators, positive["program"], [{"op": "scale", "dst": 1, "coefficient": "i"}])
    phase_certificate = c.certify(phase_trap)
    need(phase_certificate["failure"]["first_nonzero_width"] == 2, "Phase outside tensor")
    independent.check(phase_trap, phase_certificate)
    reynolds = example({str(i): a for i, a in enumerate(group)},
                       [{"op": "query", "src": 0, "dst": 1, "symbol": str(i), "coefficient": "1/96"} for i in range(96)], roles=2)
    reynolds_certificate = c.certify(reynolds)
    norms = reynolds_certificate["failure"]["normalized_squared_norms"]
    need(norms == ["0"]*7+["15/256", "0", "0", "0", "155/4096"], "Reynolds norm sequence")
    independent.check(reynolds, reynolds_certificate)
    need(independent.discrepancy(reynolds, 1, 0, [0]*8, [0]*8) == G("5/24"), "Reynolds entry")
    for f, expected in enumerate(norms, 1):
        rank = sum((c.power(sum((a[i][i] for i in range(2)), G(0)), f) for a in group), G(0))/96
        need(rank.imag == 0 and rank.real.denominator == 1 and rank/(2**f) == G(expected), "Projector rank")
    controls = []
    def reject(label, function):
        try:
            function()
        except (ValueError, KeyError, TypeError, ZeroDivisionError):
            controls.append(label)
            return
        raise ValueError("Accepted control: "+label)
    bad = json.loads(json.dumps(reynolds_certificate))
    bad["failure"]["witness"]["discrepancy"] = "0"
    reject("wrong witness value", lambda: independent.check(reynolds, bad))
    bad_width = json.loads(json.dumps(reynolds_certificate))
    bad_width["failure"]["witness"]["width"] = 7
    reject("wrong witness width", lambda: independent.check(reynolds, bad_width))
    for field, value in [("schema", "other"), ("problem_sha256", "0"*64), ("axes", 2), ("cutoff", 13)]:
        altered = json.loads(json.dumps(reynolds_certificate))
        altered[field] = value
        reject("wrong certificate "+field, lambda altered=altered: independent.check(reynolds, altered))
    for label, matrix in [("nonunitary", [[2, 0], [0, 2]]), ("continuous rational phase", [["3/5+4/5i", 0], [0, "3/5+4/5i"]]),
                          ("wrong shape", [[1]]), ("floating scalar", [[1.0, 0], [0, 1]])]:
        invalid = example({"C": C}, [])
        invalid["operators"]["C"] = matrix
        reject(label, lambda invalid=invalid: c.certify(invalid))
    toffoli = [[int(i == (j ^ (4 if j & 3 == 3 else 0))) for j in range(8)] for i in range(8)]
    invalid = {"axes": 3, "roles": 1, "operators": {"T": toffoli}, "program": [], "reference": []}
    reject("non-Clifford dyadic unitary", lambda: c.certify(invalid))
    for op in [{"op": "apply", "dst": 3, "symbol": "C"}, {"op": "apply", "dst": 0, "symbol": "missing"},
               {"op": "apply", "dst": 0, "symbol": "C", "inverse": 1}, {"op": "add", "src": 0, "dst": 1, "coefficient": 0.5},
               {"op": "query", "dst": 0, "symbol": "C"}, {"op": "apply", "dst": 0, "symbol": "C", "phase": 0}]:
        reject("invalid instruction "+str(len(controls)), lambda op=op: c.certify(example(operators, [op])))
    helper = example(operators, [{"op": "query", "src": 0, "dst": 2, "symbol": "C"}])
    helper_certificate = c.certify(helper)
    need(helper_certificate["failure"]["output_role"] == 2, "Dirty helper return")
    independent.check(helper, helper_certificate)
    controls.append("omitted helper return detected")
    order = example(operators, [{"op": "apply", "dst": 0, "symbol": "C"}, {"op": "apply", "dst": 0, "symbol": "S"}],
                    [{"op": "apply", "dst": 0, "symbol": "S"}, {"op": "apply", "dst": 0, "symbol": "C"}])
    independent.check(order, c.certify(order))
    controls += ["noncommuting order detected", "phase outside tensor detected"]
    receipt = {"status": "PASS_CLIFFORD_TENSOR_GRAM_NO_NEW_KAPPA", "cutoff": "8n+4", "separation": "14/15",
               "one_axis_group_order": 96, "closure_edges": 192,
               "trace_histogram": dict(sorted(Counter(str(sum((a[i][i] for i in range(2)), G(0))) for a in group).items())),
               "polynomial_values": polynomial_values, "native_source_columns": source_columns,
               "entangling_trace_cases": entangling_trace_cases,
               "dense_norm_cases": dense_norm_cases, "complete_endpoint_comparisons": differential_cases,
               "full_tensor_programs": full_column_cases, "random_literal_witnesses": literal_witnesses,
               "zero_axis_cases": 2,
               "reynolds": reynolds_certificate["failure"], "controls": controls}
    files = {"RESULT.json": receipt, "examples/native-relation.json": positive, "examples/phase-trap.json": phase_trap,
             "examples/phase-trap.certificate.json": phase_certificate, "examples/reynolds.json": reynolds,
             "examples/reynolds.certificate.json": reynolds_certificate}
    for name, data in files.items():
        path = HERE / name
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        else:
            need(json.loads(path.read_text()) == data, "Committed result mismatch: "+name)
    print(receipt["status"])
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate the receipt and examples")
    verify(parser.parse_args().write)
