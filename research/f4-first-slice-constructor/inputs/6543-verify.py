#!/usr/bin/env python3
"""Construct exact first-success slices; bounded prime-field reference.

New source-bound construction by ToikY with substantial OpenAI Codex assistance.
Threshold/attainment: Nick Petalas/6451; raw-pencil lineage retained in README.
Bareiss, Frobenius and Berlekamp methods are classical. Apache-2.0.
"""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
PIN = "457cd888ff00f2ac9726027b77b2ba5714f10cc92e533e87db7a778e490c930e"
PENCILS_PIN = "955e6a7de7dbff3727829d1e3489c954a3197701dd37fcc859744a8d725aaff3"
PRIMES = (2, 3, 5, 1000003)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "duplicate JSON key")
        out[key] = value
    return out


def strict_load(raw):
    def bad(value):
        raise ValueError("nonfinite JSON " + value)
    return json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=bad)


def authenticate(root=ROOT):
    manifest = (root / "SOURCE-PINS.json").read_bytes()
    need(hashlib.sha256(manifest).hexdigest() == PIN, "source manifest")
    data = strict_load(manifest)
    need(data["schema_version"] == 1 and len(data["files"]) == 2, "source schema")
    for item in data["files"]:
        path = root / item["path"]
        need(not path.is_symlink(), "source symlink")
        raw = path.read_bytes()
        need(len(raw) == item["bytes"], "source length")
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source digest")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw)
        need(blob.hexdigest() == item["git_blob"], "source git blob")
    return data


def trim(a, q):
    out = [x % q for x in a]
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return tuple(out or [0])


def add(a, b, q):
    return trim([(a[i] if i < len(a) else 0) +
                 (b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b)))], q)


def neg(a, q):
    return trim([-x for x in a], q)


def sub(a, b, q):
    return add(a, neg(b, q), q)


def mul(a, b, q):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % q
    return trim(out, q)


def divmod_poly(a, b, q):
    need(b != (0,), "zero polynomial divisor")
    rest = list(trim(a, q))
    quotient = [0] * max(1, len(rest) - len(b) + 1)
    inverse = pow(b[-1], -1, q)
    while tuple(rest) != (0,) and len(rest) >= len(b):
        k = len(rest) - len(b)
        c = rest[-1] * inverse % q
        quotient[k] = c
        for j, value in enumerate(b):
            rest[k + j] = (rest[k + j] - c * value) % q
        rest = list(trim(rest, q))
    return trim(quotient, q), tuple(rest)


def exact_div(a, b, q):
    quotient, remainder = divmod_poly(a, b, q)
    need(remainder == (0,), "nonexact Bareiss division")
    return quotient


def monic(a, q):
    need(a != (0,), "zero monic polynomial")
    return trim([x * pow(a[-1], -1, q) for x in a], q)


def gcd(a, b, q):
    while b != (0,):
        a, b = b, divmod_poly(a, b, q)[1]
    return monic(a, q)


def modpow(a, exponent, h, q):
    out = (1,)
    a = divmod_poly(a, h, q)[1]
    while exponent:
        if exponent & 1:
            out = divmod_poly(mul(out, a, q), h, q)[1]
        a = divmod_poly(mul(a, a, q), h, q)[1]
        exponent >>= 1
    return out


def input_check(q, a, b):
    need(type(q) is int and q in PRIMES, "unsupported prime")
    need(type(a) is list and type(b) is list, "matrix arrays")
    n = len(a)
    need(n <= 17 and len(b) == n, "matrix dimension")
    for matrix in (a, b):
        for row in matrix:
            need(type(row) is list and len(row) == n, "square matrix")
            need(all(type(x) is int and 0 <= x < q for x in row), "field entry")
    return n


def determinant(matrix, q):
    n = len(matrix)
    work = [row[:] for row in matrix]
    out = 1
    for k in range(n):
        pivot = next((i for i in range(k, n) if work[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            work[pivot], work[k] = work[k], work[pivot]
            out = -out
        value = work[k][k]
        out = out * value % q
        inverse = pow(value, -1, q)
        for i in range(k + 1, n):
            scale = work[i][k] * inverse % q
            for j in range(k + 1, n):
                work[i][j] = (work[i][j] - scale * work[k][j]) % q
    return out % q


def bareiss(a, b, q, trace):
    n = len(a)
    if n == 0:
        return (1,)
    work = [[trim([b[i][j], a[i][j]], q) for j in range(n)] for i in range(n)]
    previous, sign = (1,), 1
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if work[i][k] != (0,)), None)
        if pivot is None:
            return (0,)
        if pivot != k:
            work[pivot], work[k] = work[k], work[pivot]
            sign = -sign
            trace["polynomial_row_swaps"] += 1
        value = work[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = sub(mul(value, work[i][j], q),
                                mul(work[i][k], work[k][j], q), q)
                work[i][j] = exact_div(numerator, previous, q)
                trace["exact_polynomial_divisions"] += 1
            work[i][k] = (0,)
        previous = value
    return trim([sign * x for x in work[-1][-1]], q)


def kernel(matrix, q):
    work = [row[:] for row in matrix]
    pivots, row = [], 0
    cols = len(work[0]) if work else 0
    for col in range(cols):
        pivot = next((i for i in range(row, len(work)) if work[i][col]), None)
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        inv = pow(work[row][col], -1, q)
        work[row] = [x * inv % q for x in work[row]]
        for i in range(len(work)):
            if i != row and work[i][col]:
                scale = work[i][col]
                work[i] = [(x - scale * y) % q for x, y in zip(work[i], work[row])]
        pivots.append(col)
        row += 1
        if row == len(work):
            break
    basis = []
    for col in range(cols):
        if col not in pivots:
            vector = [0] * cols
            vector[col] = 1
            for i, pivot in enumerate(pivots):
                vector[pivot] = -work[i][col] % q
            basis.append(vector)
    return basis


def one_factor(polynomial, degree, q, trace):
    current = monic(polynomial, q)
    while len(current) - 1 > degree:
        m = len(current) - 1
        columns = [modpow((0,) * j + (1,), q, current, q) for j in range(m)]
        matrix = [[((columns[j][i] if i < len(columns[j]) else 0) - (i == j)) % q
                   for j in range(m)] for i in range(m)]
        basis = kernel(matrix, q)
        vector = next((trim(v, q) for v in basis if any(v[1:])), None)
        need(vector is not None, "Berlekamp nonconstant fixed vector")
        trace["berlekamp_kernel_dimensions"].append(len(basis))
        factor = None
        for c in range(q):
            candidate = gcd(current, sub(vector, (c,), q), q)
            trace["berlekamp_scalar_trials"] += 1
            if 1 < len(candidate) < len(current):
                factor = candidate
                break
        need(factor is not None, "Berlekamp proper split")
        current = factor
        trace["berlekamp_splits"] += 1
    need(len(current) == degree + 1, "factor degree")
    return current


def trace_new():
    return {"polynomial_row_swaps": 0, "exact_polynomial_divisions": 0,
            "base_element_trials": 0, "frobenius_degrees": [],
            "largest_dense_degree": 0, "berlekamp_kernel_dimensions": [],
            "berlekamp_scalar_trials": 0, "berlekamp_splits": 0}


def choose_slice(a, b, q, trace):
    if determinant(a, q):
        return 1, True, (0, 1), None, None
    f = bareiss(a, b, q, trace)
    need(f != (0,), "nonregular pencil")
    for c in range(min(q, len(a) + 1)):
        trace["base_element_trials"] += 1
        if evaluate(f, (c,), (0, 1), q) != (0,):
            return 1, False, (0, 1), (c,), f
    n = len(a)
    need(q < n, "base failure dimension")
    for e in range(2, n + 1):
        power = q ** e
        need(power < n * n, "dense Frobenius size")
        frobenius = [0] * (power + 1)
        frobenius[1], frobenius[power] = -1 % q, 1
        frobenius = tuple(frobenius)
        divisor = gcd(f, frobenius, q)
        trace["frobenius_degrees"].append([e, len(divisor) - 1])
        trace["largest_dense_degree"] = power
        if len(divisor) - 1 < power:
            missing = exact_div(frobenius, divisor, q)
            h = one_factor(missing, e, q, trace)
            return e, False, h, (0, 1), f
    raise ValueError("UNKNOWN degree cap")


def evaluate(f, x, h, q):
    out = (0,)
    for value in reversed(f):
        out = add(divmod_poly(mul(out, x, q), h, q)[1], (value,), q)
    return out


def emul(x, y, h, q):
    return divmod_poly(mul(x, y, q), h, q)[1]


def inverse_matrix(matrix, h, q):
    n = len(matrix)
    work = [row[:] + [(int(i == j),) for j in range(n)]
            for i, row in enumerate(matrix)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if work[i][k] != (0,)), None)
        need(pivot is not None, "singular returned slice")
        work[k], work[pivot] = work[pivot], work[k]
        inverse = modpow(work[k][k], q ** (len(h) - 1) - 2, h, q)
        work[k] = [emul(x, inverse, h, q) for x in work[k]]
        for i in range(n):
            if i != k:
                scale = work[i][k]
                work[i] = [sub(x, emul(scale, y, h, q), q)
                           for x, y in zip(work[i], work[k])]
    return [row[n:] for row in work]


def product(a, b, h, q):
    n = len(a)
    out = [[(0,) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                out[i][j] = add(out[i][j], emul(a[i][k], b[k][j], h, q), q)
    return out


def irreducible(h, q):
    e = len(h) - 1
    if e == 1:
        return True
    x = divmod_poly((0, 1), h, q)[1]
    power = x
    for j in range(1, e + 1):
        power = modpow(power, q, h, q)
        if j <= e // 2 and gcd(h, sub(power, x, q), q) != (1,):
            return False
    return power == x


def canonical_element(x, e, q):
    need(type(x) in (list, tuple) and 1 <= len(x) <= e, "field element length")
    need(all(type(v) is int and 0 <= v < q for v in x), "field element coefficient")
    need(tuple(x) == trim(x, q), "noncanonical field element")
    return tuple(x)


def validate_answer(q, a, b, answer):
    n = input_check(q, a, b)
    e, infinity = answer["e"], answer["infinity"]
    need(type(e) is int and 1 <= e <= max(1, n), "answer degree")
    need(type(infinity) is bool, "infinity boolean")
    h = answer["field_modulus"]
    need(type(h) in (list, tuple) and len(h) == e + 1, "field modulus degree")
    need(all(type(v) is int and 0 <= v < q for v in h) and h[-1] == 1,
         "field modulus coefficients")
    h = tuple(h)
    need(irreducible(h, q), "reducible field modulus")
    alpha = None if infinity else canonical_element(answer["alpha"], e, q)
    need(not infinity or (e == 1 and answer["alpha"] is None), "infinity degree")
    expected = [[(a[i][j],) if infinity else
                 add(emul(alpha, (a[i][j],), h, q), (b[i][j],), q)
                 for j in range(n)] for i in range(n)]
    actual, inverse = [], []
    for key, out in (("slice", actual), ("inverse", inverse)):
        matrix = answer[key]
        need(type(matrix) is list and len(matrix) == n, "witness matrix dimension")
        for row in matrix:
            need(type(row) is list and len(row) == n, "witness square matrix")
            out.append([canonical_element(x, e, q) for x in row])
    need(actual == expected, "literal slice binding")
    identity = [[(int(i == j),) for j in range(n)] for i in range(n)]
    need(product(actual, inverse, h, q) == identity, "right inverse")
    need(product(inverse, actual, h, q) == identity, "left inverse")
    if e > 1:
        need(q < n and q ** e < n * n, "answer dense bound")
        need(determinant(a, q) == 0, "earlier infinity success")
        f = bareiss(a, b, q, trace_new())
        for j in range(1, e):
            p = [0] * (q ** j + 1)
            p[1], p[-1] = -1 % q, 1
            need(len(gcd(f, tuple(p), q)) - 1 == q ** j, "earlier affine success")
    return True


def construct(q, a, b):
    input_check(q, a, b)
    trace = trace_new()
    e, infinity, h, alpha, _ = choose_slice(a, b, q, trace)
    answer = assemble(q, a, b, e, infinity, h, alpha, trace)
    validate_answer(q, a, b, answer)
    return answer


def assemble(q, a, b, e, infinity, h, alpha, trace):
    n = len(a)
    matrix = [[(a[i][j],) if infinity else
               add(emul(alpha, (a[i][j],), h, q), (b[i][j],), q)
               for j in range(n)] for i in range(n)]
    answer = {"e": e, "infinity": infinity, "field_modulus": h,
              "alpha": alpha, "slice": matrix,
              "inverse": inverse_matrix(matrix, h, q), "trace": trace}
    answer = json.loads(json.dumps(answer))
    return answer


def decode_matrix(code, q, n, diagonal=False):
    out = [[0] * n for _ in range(n)]
    positions = [(i, i) for i in range(n)] if diagonal else list(itertools.product(range(n), repeat=2))
    for i, j in positions:
        out[i][j], code = code % q, code // q
    need(code == 0, "matrix decode overflow")
    return out


def census(q, n, diagonal=False):
    count = q ** (n if diagonal else n * n)
    digest, by_degree, singular = hashlib.sha256(), {}, 0
    for acode in range(count):
        a = decode_matrix(acode, q, n, diagonal)
        for bcode in range(count):
            b = decode_matrix(bcode, q, n, diagonal)
            try:
                answer = construct(q, a, b)
                status = answer["e"]
                by_degree[status] = by_degree.get(status, 0) + 1
            except ValueError as exc:
                need(str(exc) == "nonregular pencil", "unexpected census failure: " + str(exc))
                status, singular = 0, singular + 1
            digest.update(bytes([status]))
    return {"q": q, "n": n, "shape": "diagonal" if diagonal else "all",
            "cases": count * count, "singular": singular,
            "first_degree_counts": {str(k): v for k, v in sorted(by_degree.items())},
            "degree_sha256": digest.hexdigest()}


def named_inputs():
    raw = (ROOT / "PENCILS.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PENCILS_PIN, "frozen raw pencils")
    data = strict_load(raw)
    need(data["schema_version"] == 1 and len(data["pencils"]) == 17, "pencil schema")
    return data["pencils"]


def rejects(function, *args):
    try:
        function(*args)
    except (ValueError, TypeError, KeyError):
        return True
    raise ValueError("negative control accepted")


def controls(fixtures):
    by_name = {f["name"]: f for f in fixtures}
    good = by_name["binary-first-2"]
    tests = {}
    for name, change in (("wrong_inverse", "inverse"), ("wrong_slice", "slice")):
        bad = copy.deepcopy(good["answer"])
        bad[change][0][0] = [1] if bad[change][0][0] == [0] else [0]
        tests[name] = rejects(validate_answer, good["q"], good["A"], good["B"], bad)
    bad = copy.deepcopy(good["answer"])
    bad["field_modulus"] = [0, 0, 1]
    tests["reducible_modulus"] = rejects(validate_answer, 2, good["A"], good["B"], bad)
    bad = copy.deepcopy(good["answer"])
    bad["e"] = True
    tests["boolean_degree"] = rejects(validate_answer, 2, good["A"], good["B"], bad)
    tests["boolean_entry"] = rejects(construct, 2, [[True]], [[0]])
    tests["nonregular"] = rejects(construct, 2, [[0]], [[0]])
    tests["nonsquare"] = rejects(construct, 2, [[1, 0]], [[1]])
    tests["unsupported_prime"] = rejects(construct, 4, [[1]], [[1]])
    tests["duplicate_json"] = rejects(strict_load, '{"x":1,"x":2}')
    tests["nonfinite_json"] = rejects(strict_load, '{"x":NaN}')
    row = by_name["row-pivot"]["answer"]["trace"]
    need(row["polynomial_row_swaps"] > 0, "row-swap fixture bypassed")
    large = by_name["large-q-constant"]["answer"]["trace"]
    need(large["largest_dense_degree"] == 0, "large-q dense expansion")
    tests["large_q_no_dense"] = True
    tests["actual_polynomial_row_swap"] = True
    tests.update(mathematical_controls(by_name))
    return tests


def mathematical_controls(by_name):
    good = by_name["binary-first-2"]
    later = assemble(2, good["A"], good["B"], 3, False, (1, 1, 0, 1),
                     (0, 1), trace_new())
    rejected = rejects(validate_answer, 2, good["A"], good["B"], later)
    fixture = by_name["nonmonotone"]
    f = bareiss(fixture["A"], fixture["B"], 2, trace_new())
    p = tuple([0, 1] + [0] * 14 + [1])
    need(len(gcd(f, p, 2)) == 17, "nonmonotone degree4 failure")
    need(fixture["answer"]["e"] == 3, "nonmonotone first degree")
    fixture = by_name["infinity-only"]
    f = bareiss(fixture["A"], fixture["B"], 2, trace_new())
    need(all(evaluate(f, (c,), (0, 1), 2) == (0,) for c in (0, 1)),
         "infinity-only affine failure")
    need(fixture["answer"]["infinity"], "infinity-only chosen")
    need(by_name["binary-first-4"]["answer"]["trace"]["berlekamp_splits"] > 0,
         "Berlekamp split unexercised")
    return {"valid_later_slice_not_first": rejected, "nonmonotone_degree4_failure": True,
            "affine_failure_infinity_success": True, "actual_berlekamp_split": True}


def source_control():
    with tempfile.TemporaryDirectory(prefix="pencil-source-control-") as folder:
        root = Path(folder)
        (root / "inputs").mkdir()
        (root / "SOURCE-PINS.json").write_bytes((ROOT / "SOURCE-PINS.json").read_bytes())
        data = strict_load((ROOT / "SOURCE-PINS.json").read_bytes())
        for item in data["files"]:
            (root / item["path"]).write_bytes((ROOT / item["path"]).read_bytes())
        path = root / data["files"][0]["path"]
        raw = bytearray(path.read_bytes())
        raw[0] ^= 1
        path.write_bytes(raw)
        return rejects(authenticate, root)


def receipt():
    authenticate()
    frozen = named_inputs()
    domains = [census(q, n) for q, n in ((2, 0), (2, 1), (2, 2),
                                        (3, 1), (3, 2), (5, 1))]
    domains.append(census(2, 3, True))
    fixtures = []
    for item in frozen:
        q, a, b = item["q"], item["A"], item["B"]
        answer = construct(q, a, b)
        need(answer["e"] == item["expected_first_degree"], "named expected degree")
        fixtures.append({"name": item["id"], "q": q, "A": a, "B": b, "answer": answer})
    checks = controls(fixtures)
    checks["source_corruption"] = source_control()
    return {"schema_version": 1, "source_manifest_sha256": PIN,
            "pencils_sha256": PENCILS_PIN,
            "domains": domains, "fixtures": fixtures, "controls": checks}


def same_type_tree(actual, expected):
    need(type(actual) is type(expected), "receipt value type")
    if type(expected) is dict:
        need(actual.keys() == expected.keys(), "receipt keys")
        for key in expected:
            same_type_tree(actual[key], expected[key])
    elif type(expected) is list:
        need(len(actual) == len(expected), "receipt list length")
        for left, right in zip(actual, expected):
            same_type_tree(left, right)
    else:
        need(actual == expected, "receipt value")


def main():
    need(sys.argv[1:] in ([], ["--emit"]), "unsupported arguments")
    result = receipt()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        retained = strict_load((ROOT / "RESULT.json").read_bytes())
        same_type_tree(retained, result)
        print("PASS_PENCIL_FIRST_SLICE_CONSTRUCTOR")


if __name__ == "__main__":
    main()
