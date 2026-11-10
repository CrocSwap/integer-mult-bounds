"""Independent dense circuit oracle for four frozen frame1094 native maps.

The compiler, producer, primary verifier and author native checker are never
imported.  Expected maps use dense P/D/C circuit action; compiled recipes use
a separate direct monomial and positive-child expansion.
"""
from copy import deepcopy
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
WIDTH, SIZE = 9, 512
RECIPE_CANONICAL_SHA256 = "b33e9ad1eb25daf857d144ac75bb09ea60b2d6eb5a22605e78e71999491b9335"
PINS = {
    "WORD.json.gz": ("0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928", "03ea7690285d4cda72815f962d5710ab96e08490"),
    "clifford_exact.py": ("2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962", "166841a037f069249f6f7f6dedb89248812f59e2"),
    "integration-source.py": ("7201df8e32f5c99f7403150e8664042322037906088bc754c67293a241368597", "b7be846b10c4c54a4e1558d7b563bc8c3a170223"),
    "native-channel-PROOF.md": ("5d743145d389ffdfaffc66096fa7e32c7155b18f73d74755403151d0435bb94c", "a69311b74f74a2f8e8f411c1451baacd9bacddce"),
    "NOTICE": ("6c5f4a452f7d65ef8ca0980992dce279938b0a1139f6c067f91de78bf8ecb7bd", "e6cae17f778e8e31b7c294ff2890c545978931c0"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, lower, upper, label):
    require(type(value) is int and lower <= value < upper, label)
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def authenticate():
    for name, (digest, blob) in PINS.items():
        raw = (HERE / "sources" / name).read_bytes()
        require(sha256(raw).hexdigest() == digest, "Exact source SHA256: " + name)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob,
                "Exact source Git blob: " + name)
    raw_word = (HERE / "sources" / "WORD.json.gz").read_bytes()
    word = json.loads(gzip.decompress(raw_word))
    records = json.loads((HERE / "RECIPES.json").read_bytes())
    require(sha256((canonical(records) + "\n").encode()).hexdigest() == RECIPE_CANONICAL_SHA256,
            "Exact canonical compiled-recipe payload pin")
    return word, records


def parity(value):
    return bin(value).count("1") % 2


def multiply(matrix, address):
    return sum(parity(row & address) << j for j, row in enumerate(matrix))


def invert(matrix):
    """High-to-low Gauss-Jordan elimination, independent of source helpers."""
    require(type(matrix) in (list, tuple) and len(matrix) == WIDTH, "Nine binary matrix rows")
    for row in matrix:
        integer(row, 0, SIZE, "Binary matrix row")
    rows = [row | (1 << (WIDTH + i)) for i, row in enumerate(matrix)]
    for column in reversed(range(WIDTH)):
        candidates = [r for r in range(column + 1) if rows[r] & (1 << column)]
        require(candidates, "Invertible binary monomial matrix")
        pivot = candidates[-1]
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for r in range(WIDTH):
            if r != column and rows[r] & (1 << column):
                rows[r] ^= rows[column]
    require([row & (SIZE - 1) for row in rows] == [1 << r for r in range(WIDTH)],
            "Independent binary inverse identity")
    return tuple(row >> WIDTH for row in rows)


def completion(vectors):
    require(type(vectors) is list and len(vectors) <= WIDTH, "Native frame basis")
    span, columns = {0}, []
    for index, vector in enumerate(vectors + [1 << j for j in range(WIDTH)]):
        integer(vector, 1, SIZE, "Native frame vector")
        if vector in span:
            require(index >= len(vectors), "Independent declared frame basis")
            continue
        columns.append(vector)
        span |= {x ^ vector for x in tuple(span)}
    require(len(columns) == WIDTH and len(span) == SIZE, "Canonical basis completion")
    return tuple(columns)


def phase_value(quadratic, linear, address):
    total = sum(linear[i] for i in range(WIDTH) if address & (1 << i))
    for i in range(WIDTH):
        for j in range(i + 1, WIDTH):
            if address & (1 << i) and address & (1 << j):
                total += 2 * ((quadratic[i] >> j) & 1)
    return total % 4


def rotate(value, exponent):
    real, imaginary = value
    return ((real, imaginary), (-imaginary, real), (-real, -imaginary),
            (imaginary, -real))[exponent % 4]


def gaussian_mul(left, right):
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c


def adjoint(circuit):
    result = []
    for gate in reversed(circuit):
        if gate[0] == "P":
            result.append(("P", invert(gate[1])))
        elif gate[0] == "D":
            result.append(("D", gate[1], tuple(-x % 4 for x in gate[2])))
        else:
            require(gate[0] == "C", "Known expected circuit gate")
            result.append(("C", gate[1], -gate[2]))
    return result


def native_circuit(vectors):
    """Construct the declared canonical chart as an actual P/D/C circuit."""
    completion_columns = completion(vectors)
    rank = len(vectors)
    if rank in (0, WIDTH):
        return [("C", 1 << j, 1) for j in range(rank)]
    matrix = tuple(sum(((vector >> i) & 1) << j
                       for j, vector in enumerate(completion_columns)) for i in range(WIDTH))
    inverse = invert(matrix)
    dual_columns = tuple(sum(((row >> j) & 1) << i for i, row in enumerate(inverse))
                         for j in range(WIDTH))
    quadratic = tuple((1 << i) ^ sum(parity(dual_columns[i] & dual_columns[j]) << j
                                    for j in range(WIDTH)) for i in range(WIDTH))
    linear = tuple((quadratic[i] >> i) & 1 for i in range(WIDTH))
    chart = [("P", matrix), ("D", quadratic, linear)]
    return adjoint(chart) + [("C", 1 << j, 1) for j in range(rank)] + chart


def normalize(vector, denominator):
    while denominator and all(a % 2 == 0 and b % 2 == 0 for a, b in vector):
        vector = [(a // 2, b // 2) for a, b in vector]
        denominator -= 1
    return vector, denominator


def dense_circuit_column(circuit, basis):
    vector, denominator = [(0, 0)] * SIZE, 0
    vector[basis] = (1, 0)
    for gate in circuit:
        tag = gate[0]
        result = [(0, 0)] * SIZE
        if tag == "P":
            for address, value in enumerate(vector):
                result[multiply(gate[1], address)] = value
        elif tag == "D":
            result = [rotate(value, phase_value(gate[1], gate[2], address))
                      for address, value in enumerate(vector)]
        else:
            require(tag == "C" and gate[2] in (-1, 1), "Expected positive or inverse C gate")
            direction, sign = gate[1:]
            for address in range(SIZE):
                identity_part = gaussian_mul((1, sign), vector[address])
                translated_part = gaussian_mul((1, -sign), vector[address ^ direction])
                result[address] = (identity_part[0] + translated_part[0],
                                   identity_part[1] + translated_part[1])
            denominator += 1
        vector = result
    return normalize(vector, denominator)


def monomial(record):
    require(type(record) is dict and set(record) == {
        "matrix_rows", "quadratic_rows", "linear_Z4", "offset", "phase"}, "Exact monomial fields")
    matrix, quadratic, linear = record["matrix_rows"], record["quadratic_rows"], record["linear_Z4"]
    invert(matrix)
    require(type(quadratic) is list and type(linear) is list
            and len(quadratic) == len(linear) == WIDTH, "Monomial phase dimensions")
    for i in range(WIDTH):
        integer(quadratic[i], 0, SIZE, "Quadratic binary row")
        integer(linear[i], 0, 4, "Quadratic Z4 coefficient")
        require(linear[i] % 2 == ((quadratic[i] >> i) & 1), "Quadratic diagonal parity")
        require(all(((quadratic[i] >> j) & 1) == ((quadratic[j] >> i) & 1)
                    for j in range(WIDTH)), "Symmetric quadratic phase")
    integer(record["offset"], 0, SIZE, "Monomial offset")
    integer(record["phase"], 0, 4, "Absolute monomial phase")
    return tuple((multiply(matrix, x) ^ record["offset"],
                  (phase_value(quadratic, linear, x) + record["phase"]) % 4)
                 for x in range(SIZE))


def recipe_tables(record):
    require(type(record) is dict and set(record) == {"rank", "left", "right"}, "Exact compiled recipe fields")
    rank = integer(record["rank"], 1, WIDTH + 1, "Positive compiled child rank")
    return rank, monomial(record["right"]), monomial(record["left"])


def recipe_column(tables, basis, sign=1):
    """Direct monomial/child/monomial kernel, separate from circuit action."""
    rank, right, left = tables
    address, right_phase = right[basis]
    vector = [(0, 0)] * SIZE
    for mask in range(1 << rank):
        value = (1, 0)
        for bit in range(rank):
            value = gaussian_mul(value, (1, -sign if mask & (1 << bit) else sign))
        target, left_phase = left[address ^ mask]
        require(vector[target] == (0, 0), "Injective direct recipe output addresses")
        vector[target] = rotate(value, right_phase + left_phase)
    return normalize(vector, rank)


def entries(vector):
    return [[address, value[0], value[1]] for address, value in enumerate(vector) if value != (0, 0)]


def column_line(basis, column):
    vector, denominator = column
    return (canonical({"input": basis, "denominator_exponent": denominator,
                       "entries": entries(vector)}) + "\n").encode("ascii")


def first_difference(expected, actual, basis):
    left, ld = expected
    right, rd = actual
    denominator = max(ld, rd)
    for address, (a, b) in enumerate(zip(left, right)):
        a = [x << (denominator - ld) for x in a]
        b = [x << (denominator - rd) for x in b]
        if a != b:
            return {"input": basis, "output": address, "denominator_exponent": denominator,
                    "expected": a, "actual": b}
    return None


def footprint(word, records):
    require(type(word["public"]) is int and word["public"] == 770
            and word["frames"][1094] == [7, 9, 35, 66, 400], "Exact frame1094 source binding")
    require(len(word["frames"]) == 1095, "One literal terminal frame1094")
    paid = []
    for index, event in enumerate(word["program"]):
        if event[0] == "MOVE" and 1094 in event[2:4]:
            require(type(event[4]) is bool and not event[4], "Frame1094 paid public transport")
            paid.append((index, event[1], event[2], event[3]))
    require(paid == [(12917, 703, 712, 1094), (12930, 704, 714, 1094),
                     (12932, 704, 1094, 127)], "All literal frame1094 paid uses")
    main = set(word["live"]) | {r + 112 for r in word["live"]}
    helpers = [r for r in range(770) if r not in main and word["final"][r] == 1094]
    require(helpers == [703] and word["initial"][703] == 3, "Exact helper703 frame1094 job")
    require(type(records["schema_version"]) is int and records["schema_version"] == 1,
            "Recipe payload schema")
    require(records["word_sha256"] == PINS["WORD.json.gz"][0]
            and records["compiler_sha256"] == PINS["clifford_exact.py"][0], "Recipe source claims")
    require(type(records["tasks"]) is list and len(records["tasks"]) == 4, "Four bound native tasks")
    expected = {(712, 1094): ("move", [703], [12917]), (714, 1094): ("move", [704], [12930]),
                (1094, 127): ("move", [704], [12932]), (3, 1094): ("helper", [703], [])}
    seen = set()
    for task in records["tasks"]:
        a = integer(task["source_frame"], 0, 1095, "Task source frame")
        b = integer(task["target_frame"], 0, 1095, "Task target frame")
        require((a, b) in expected and (a, b) not in seen, "Unique actual task endpoint pair")
        seen.add((a, b))
        kind, roles, indices = expected[a, b]
        require(canonical([task["kind"], task["roles"], task["event_indices"]])
                == canonical([kind, roles, indices]), "Exact literal task footprint")
        require(type(task["id"]) is str, "Task identifier")
        require(type(task["recipe"]["rank"]) is int and task["recipe"]["rank"]
                == abs(len(word["frames"][b]) - len(word["frames"][a])), "Literal native rank")
    return paid


def run():
    word, records = authenticate()
    paid = footprint(word, records)
    results, controls = [], []
    for task in records["tasks"]:
        a, b = task["source_frame"], task["target_frame"]
        expected_circuit = adjoint(native_circuit(word["frames"][a])) + native_circuit(word["frames"][b])
        tables = recipe_tables(task["recipe"])
        actual_digest, expected_digest = sha256(), sha256()
        nonzero = 0
        first_expected = None
        for basis in range(SIZE):
            expected = dense_circuit_column(expected_circuit, basis)
            actual = recipe_column(tables, basis)
            difference = first_difference(expected, actual, basis)
            require(difference is None, "Exact native matrix mismatch: " + task["id"] + " " + canonical(difference))
            expected_digest.update(column_line(basis, expected))
            actual_digest.update(column_line(basis, actual))
            nonzero += len(entries(actual[0]))
            if basis == 0:
                first_expected = expected
        require(expected_digest.hexdigest() == actual_digest.hexdigest(), "Matching full matrix digests")
        results.append({"id": task["id"], "source_frame": a, "target_frame": b,
                        "rank": tables[0], "columns": SIZE, "coefficient_comparisons": SIZE * SIZE,
                        "nonzero_coefficients": nonzero, "matrix_sha256": actual_digest.hexdigest()})
        bad = deepcopy(task["recipe"])
        bad["left"]["phase"] = (bad["left"]["phase"] + 1) % 4
        phase_difference = first_difference(first_expected, recipe_column(recipe_tables(bad), 0), 0)
        inverse_difference = first_difference(first_expected, recipe_column(tables, 0, sign=-1), 0)
        require(phase_difference is not None and inverse_difference is not None,
                "Phase-only and inverse-child faults change actual matrix entries")
        controls.append({"id": task["id"], "phase_only_fault": phase_difference,
                         "inverse_child_fault": inverse_difference})
    return {"schema_version": 1, "status": "PASS",
            "scope": "four source-bound width-one frame1094 native matrices with absolute phase",
            "method": "independent dense P/D/C circuit action versus direct compiled monomial/child kernels",
            "literal_paid_uses": [list(row) for row in paid], "tasks": results,
            "columns": 4 * SIZE, "coefficient_comparisons": 4 * SIZE * SIZE,
            "phase_sensitive_controls": controls,
            "limits": ["Only these four frozen recipe instantiations at binary width nine are checked.",
                       "No fresh generic compiler or all-tensor-width native theorem is proved.",
                       "Other native maps, whole-word composition, caller contacts and erasure remain outside this oracle.",
                       "No pricing, kappa, uniform compiler or rounded multiplication admission is claimed."]}


if __name__ == "__main__":
    require(sys.argv[1:] in ([], ["--emit"]), "Usage: oracle.py [--emit]")
    result = run()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        retained = json.loads((HERE / "ORACLE.json").read_bytes())
        require(canonical(result) == canonical(retained), "Exact typed retained ORACLE.json receipt")
        print("PASS independent dense native columns and retained receipt")
