"""Check the actual clique codes and their exact odd-grid interface."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
ROOT = LANES.parents[2]
PINS = {
    "flags": (
        LANES / "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json",
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585",
    ),
    "response": (
        LANES / "new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json",
        "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
    ),
    "native_extension": (
        LANES / "new-core-transfer-20261017/low-displacement-20261020/odd16-normal-v2/EXTENSION-PROGRAM.json.gz",
        "7160a8764f0b12131e30dd1ca90a28b781b9dd99e8eb2f1935b8592aaf48037b",
    ),
    "streams": (
        ROOT / "upstream/build/sections/02-streams.tex",
        "606c80db61cad13aa0c3b6060dc4b88dbbe7ac60cdd831aa93f28d908fd09dab",
    ),
    "layers": (
        ROOT / "upstream/build/sections/05-layers.tex",
        "20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594",
    ),
    "retained_odd_grid": (
        LANES / "interface-proof/rational-decoder/sources/notes/stopped-product-complex.tex",
        "4738089103a4b263b3b0ef458f5ef35519c696f1ea871ae79e508d3720f5870a",
    ),
    "signed_scan_proof": (
        LANES / "independent-review-20261017/odd-grid-a8-20261017/A8-ODD-GRID.md",
        "e0210105ba6c6246f1f84c8ce2d92cfd07aa6cc8a161ca27d7fcc8e0183cfb01",
    ),
}
SMALL = [
    [1, 5, 19, 54, 64, 73, 82, 83],
    [3, 4, 22, 50, 60, 69, 80, 84],
    [6, 35, 38, 39, 40, 77, 85, 86],
    [8, 12, 45, 88, 103, 107, 108, 109],
    [17, 29, 30, 56, 58, 67, 93, 95],
    [18, 32, 34, 49, 65, 68, 98, 101],
    [24, 26, 28, 48, 66, 75, 96, 97],
    [23, 31, 33, 55, 59, 74, 100, 102],
]


def need(value, label):
    if not value:
        raise ValueError(label)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def dense(rows):
    return [[F(row.get(str(j), 0)) for j in range(len(rows))] for row in rows]


def multiply(a, b):
    out = [[F(0) for _ in b[0]] for _ in a]
    for i, row in enumerate(a):
        for k, value in enumerate(row):
            if value:
                out[i] = [x + value * y for x, y in zip(out[i], b[k])]
    return out


def height(value, prime):
    denominator = value.denominator
    answer = 0
    while denominator % prime == 0:
        denominator //= prime
        answer += 1
    return answer


def matrix_height(a, prime):
    return max(height(x, prime) for row in a for x in row)


def modular_rank(matrix, prime):
    rows = [[x.numerator * pow(x.denominator, -1, prime) % prime for x in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = pow(rows[rank][column], -1, prime)
        rows[rank] = [x * scale % prime for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            factor = rows[i][column]
            if factor:
                rows[i] = [(x - factor * y) % prime for x, y in zip(rows[i], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def pair_word(pair, inverse=False):
    p, q = pair["ports"]
    (a, b), (c, d) = pair["matrix"]
    need(a * d == -b * c and {a, b, c, d} <= {-1, 1}, "Signed Hadamard pair")
    word = []
    if a == -1:
        word.append(["NEG", p])
    if b == -1:
        word.append(["NEG", q])
    word.extend([["ADD", p, q, 1], ["NEG", q], ["SCALE2", q, 1], ["ADD", q, p, 1]])
    if c * a == -1:
        word.append(["NEG", q])
    if not inverse:
        return word
    out = []
    for gate in reversed(word):
        if gate[0] == "ADD":
            out.append(gate[:3] + [-gate[3]])
        elif gate[0] == "SCALE2":
            out.append(gate[:2] + [-gate[2]])
        else:
            out.append(gate[:])
    return out


def block_word(block, inverse):
    pivot = block[-1]
    rest = block[:-1]
    word = [["ADD", p, pivot, -1] for p in rest]
    if inverse:
        word.extend(["ADD", pivot, p, 1] for p in rest)
        word.extend([["DIVIDE_ODD", pivot, len(rest)], ["NEG", pivot]])
    else:
        word.extend([["MULTIPLY_ODD", pivot, len(rest)], ["NEG", pivot]])
        word.extend(["ADD", pivot, p, -1] for p in rest)
    word.extend(["ADD", p, pivot, 1] for p in rest)
    return word


def apply_gate(rows, gate):
    kind, target = gate[:2]
    if kind == "ADD":
        source, coefficient = gate[2:]
        rows[target] = [x + coefficient * y for x, y in zip(rows[target], rows[source])]
    elif kind == "NEG":
        rows[target] = [-x for x in rows[target]]
    else:
        factor = F(2) ** gate[2] if kind == "SCALE2" else F(gate[2])
        if kind == "DIVIDE_ODD":
            factor = 1 / factor
        need(kind in {"SCALE2", "MULTIPLY_ODD", "DIVIDE_ODD"}, "Known gate")
        rows[target] = [factor * x for x in rows[target]]


def replay(word, initial):
    rows = [row[:] for row in initial]
    norm = max(sum(abs(x) for x in row) for row in rows)
    levels = {p: matrix_height(rows, p) for p in (2, 5, 7)}
    for gate in word:
        need(0 <= gate[1] < 112, "Only data fields are changed")
        if gate[0] == "ADD":
            need(0 <= gate[2] < 112 and gate[1] != gate[2], "Only data sources are read")
        apply_gate(rows, gate)
        row = rows[gate[1]]
        norm = max(norm, sum(abs(x) for x in row))
        for p in levels:
            levels[p] = max(levels[p], max(height(x, p) for x in row))
    return rows, {"max_stored_row_l1": str(norm), "max_denominator_heights": levels}


def invoice(word):
    counts = Counter(g[0] for g in word)
    odd = Counter((g[0], g[2]) for g in word if g[0] in {"MULTIPLY_ODD", "DIVIDE_ODD"})
    return {
        "old_real_scalar_units": 8 * counts["ADD"] + 2 * (counts["NEG"] + counts["SCALE2"]),
        "gate_counts": dict(sorted(counts.items())),
        "real_fixed_odd_scans": {f"{kind}_{divisor}": 2 * count for (kind, divisor), count in sorted(odd.items())},
        "native_children": 0,
        "owned_fields": 0,
        "maps_inside_common_chart": 0,
    }


def signed_divide(numerator, width, divisor):
    raw = numerator % (1 << width)
    result = carry = 0
    for bit in range(width):
        b = (raw >> bit) & 1
        a = (b - carry) % 2
        result |= a << bit
        carry = (carry + divisor * a - b) // 2
        need(0 <= carry < divisor, "Division carry range")
    n_sign = int(numerator < 0)
    q_sign = (result >> (width - 1)) & 1
    valid = carry == divisor * q_sign - n_sign
    quotient = result - q_sign * (1 << width)
    return valid, quotient


def signed_multiply(numerator, width, multiplier):
    raw = numerator % (1 << width)
    result = carry = 0
    for bit in range(width):
        total = multiplier * ((raw >> bit) & 1) + carry
        result |= (total % 2) << bit
        carry = total // 2
        need(0 <= carry < multiplier, "Multiplication carry range")
    n_sign = int(numerator < 0)
    q_sign = (result >> (width - 1)) & 1
    valid = carry == multiplier * n_sign - q_sign
    product = result - q_sign * (1 << width)
    return valid, product


def typed_fixtures():
    n = 16
    codes = [identity(n)]
    inverse_codes = [identity(n)]
    for inverse in (False, True):
        c = identity(n)
        for block in (list(range(6)), list(range(6, 14))):
            for gate in block_word(block, inverse):
                apply_gate(c, gate)
        codes.append(c)
    inverse_codes += [codes[2], codes[1]]
    state = identity(n)
    semantic = identity(n)
    old_type = 0
    maximum = {5: 0, 7: 0}
    for step in range(96):
        new_type = step % 3
        a = identity(n)
        target, source = step % 14, (step * 5 + 3) % 14
        if target == source:
            source = (source + 1) % 14
        a[target][source] = F(-1 if step % 2 else 1, 2)
        child = multiply(codes[new_type], multiply(a, inverse_codes[old_type]))
        state = multiply(child, state)
        semantic = multiply(a, semantic)
        need(state == multiply(codes[new_type], semantic), "Matching typed endpoints telescope")
        for prime in maximum:
            maximum[prime] = max(maximum[prime], matrix_height(state, prime))
            need(maximum[prime] <= 1, "No height per completed sibling")
        need(state[14:] == identity(n)[14:], "Arbitrary spectator rows remain fixed")
        old_type = new_type
    mismatch = identity(n)
    for _ in range(8):
        mismatch = multiply(codes[2], mismatch)
    need(matrix_height(mismatch, 5) == matrix_height(mismatch, 7) == 8,
         "Mismatched rational endpoints accumulate height")
    return {
        "completed_siblings": 96,
        "typed_max_odd_heights": maximum,
        "mismatched_repeat_count": 8,
        "mismatched_odd_heights": {5: 8, 7: 8},
        "arbitrary_spectator_roles": 2,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    sources = {}
    source_pins = {}
    for label, (path, digest) in PINS.items():
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == digest, "Source pin " + label)
        source_pins[label] = {"path": str(path), "sha256": digest}
        if path.suffix == ".json":
            sources[label] = json.loads(raw)
        elif label == "native_extension":
            raw = gzip.decompress(raw)
            digest = "d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4"
            need(sha256(raw).hexdigest() == digest, "Native extension payload pin")
            source_pins[label]["payload_sha256"] = digest
            sources[label] = json.loads(raw)
    flags, response = sources["flags"], sources["response"]
    native = sources["native_extension"]
    need(native["kind"] == "odd-grid-rank16"
         and native["schema"] == "low-displacement-native-extension-v1", "Native extension type")
    native_model = native["model"]
    large = flags["cyclic_carriers"]
    need(len(large) == 8 and all(len(x) == 6 for x in large), "Eight actual six-mode blocks")
    signs = {}
    for item in response["vertex_assignments"]:
        vertex = item["vertex"]
        order, diagonal = item["ordered_carriers_a_b_c"], item["signs"]
        need(set(order) == set(large[vertex]) and set(diagonal) <= {-1, 1}, "Actual signed mode assignment")
        signs.update(zip(order, diagonal))
    need(len(signs) == 48, "Every large mode has one sign")
    need(native_model["vertex_assignments"] == response["vertex_assignments"]
         and native_model["small_cliques"] == SMALL, "Native extension uses the same signed blocks")
    need(sorted(p for row in large + SMALL for p in row) == list(range(112)), "Complete disjoint port partition")
    maximal = {tuple(x) for x in response["maximal_small_cliques"]}
    need(all(tuple(x) in maximal for x in SMALL), "Every eight-clique is in the pinned certificate")
    a = identity(112)
    for pair in flags["pair_codes"]:
        p, q = pair["ports"]
        for row, target in zip(pair["matrix"], (p, q)):
            a[target] = [F(0)] * 112
            a[target][p], a[target][q] = map(F, row)
    a_inverse = [list(row) for row in zip(*a)]
    for p in flags["affected_ports"]:
        a_inverse[p] = [x / 2 for x in a_inverse[p]]
    need(multiply(a_inverse, a) == identity(112), "Actual pair basis is a dyadic unit")
    expected = []
    words = {}
    checks = {}
    for inverse in (False, True):
        name = "inverse" if inverse else "forward"
        word = [g for pair in flags["pair_codes"] for g in pair_word(pair)]
        word += [["NEG", p] for p in sorted(signs) if signs[p] == -1]
        word += [g for block in large + SMALL for g in block_word(block, inverse)]
        word += [["NEG", p] for p in sorted(signs) if signs[p] == -1]
        word += [g for pair in reversed(flags["pair_codes"]) for g in pair_word(pair, True)]
        words[name] = word
        mode = identity(112)
        for block in large + SMALL:
            scale = F(1, len(block) - 1) if inverse else F(1)
            for p in block:
                for q in block:
                    mode[p][q] -= scale * signs.get(p, 1) * signs.get(q, 1)
        target = multiply(a_inverse, multiply(mode, a))
        native_key = "response_inverse" if inverse else "response"
        need(target == dense(native_model[native_key]), "Scalar word matches the frozen native response")
        actual, bounds = replay(word, identity(114))
        need([row[:112] for row in actual[:112]] == target, "Actual word has the stated clique endpoint")
        need(all(row[112:] == [F(0), F(0)] for row in actual[:112]), "No borrowed baseline leaks")
        need(actual[112:] == identity(114)[112:], "Arbitrary owned and borrowed values are unchanged")
        levels = bounds["max_denominator_heights"]
        need(levels[5] <= int(inverse) and levels[7] <= int(inverse), "One odd level per complete inverse")
        expected.append(target)
        checks[name] = {"invoice": invoice(word), "prefix_bounds": bounds}
        grid = 35 * 2 ** levels[2]
        fixed = [[x * grid for x in row] for row in identity(114)]
        for gate in word:
            if gate[0] == "DIVIDE_ODD":
                need(all(x.denominator == 1 and x.numerator % gate[2] == 0 for x in fixed[gate[1]]),
                     "Exact grid divisibility before every odd scan")
            apply_gate(fixed, gate)
            need(all(x.denominator == 1 for x in fixed[gate[1]]), "All stored grid numerators stay integral")
        need(fixed == [[x * grid for x in row] for row in actual], "Integer-grid replay agrees")
    need(multiply(expected[0], expected[1]) == multiply(expected[1], expected[0]) == identity(112),
         "Both complete inverse orders")
    square = multiply(expected[0], expected[0])
    need([[square[i][j] + 11 * expected[0][i][j] + 23 * F(i == j) for j in range(112)]
          for i in range(112)] == [[35 * x for x in row] for row in expected[1]],
         "Exact polynomial inverse")
    syndrome_checks = {}
    for prime, blocks in ((5, large), (7, SMALL)):
        syndromes = [[sum(signs.get(p, 1) * a[p][j] for p in block) for j in range(112)] for block in blocks]
        need(modular_rank(syndromes, prime) == 8, "Eight independent syndrome rows")
        image_rows = multiply(syndromes, expected[0])
        need(all(x.numerator % prime == 0 for row in image_rows for x in row), "Every encoded value has zero syndrome")
        need(modular_rank(expected[0], prime) == 104, "Exact image codimension")
        syndrome_checks[prime] = {"rank": 8, "image_rank": 104, "rows": [[str(x) for x in row] for row in syndromes]}
    valid = identity(114)
    valid[:112] = [row + [F(0), F(0)] for row in expected[0]]
    valid = [[4 * x for x in row] for row in valid]
    for gate in words["inverse"]:
        if gate[0] == "DIVIDE_ODD":
            need(all(x.denominator == 1 and x.numerator % gate[2] == 0 for x in valid[gate[1]]),
                 "Valid-code division needs no odd root scale")
        apply_gate(valid, gate)
        need(all(x.denominator == 1 for x in valid[gate[1]]), "Valid-code prefixes stay on a binary grid")
    need(valid == [[4 * x for x in row] for row in identity(114)], "Exact valid-code decode")
    division_cases = 0
    for divisor in (5, 7, 35, 2145):
        for width in range(2, 13):
            for numerator in range(-(1 << (width - 1)), 1 << (width - 1)):
                valid, quotient = signed_divide(numerator, width, divisor)
                need(valid == (numerator % divisor == 0), "Signed exact-division acceptance")
                if valid:
                    need(quotient * divisor == numerator, "Signed quotient")
                valid, product = signed_multiply(numerator, width, divisor)
                exact_product = numerator * divisor
                need(valid == (-(1 << (width - 1)) <= exact_product < (1 << (width - 1))),
                     "Signed multiplication overflow test")
                if valid:
                    need(product == exact_product, "Signed product")
                division_cases += 1
    for block in (large[0], SMALL[0]):
        divisor = len(block) - 1
        inverse_approx = [[F(i == j) - F((256 // divisor), 256) for j in block] for i in block]
        forward = [[F(i == j) - 1 for j in block] for i in block]
        need(multiply(forward, inverse_approx) != identity(len(block)), "Rounded inverse fails exact restoration")
    payload = {"pair_codes": flags["pair_codes"], "six_mode_blocks": large, "mode_signs": signs,
               "eight_cliques": SMALL, "words": words}
    payload_raw = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode()
    (args.out / "CLIQUE-CODES.json").write_bytes(payload_raw)
    receipt = {
        "status": "PASS_EXACT_CLIQUE_CODES_AND_TYPED_GRID_FIXTURES",
        "source_pins": source_pins,
        "payload_sha256": sha256(payload_raw).hexdigest(),
        "checks": checks,
        "all_data_columns": 112,
        "arbitrary_untouched_formal_columns": 2,
        "division_cases": division_cases,
        "multiplication_cases": division_cases,
        "syndrome_checks": syndrome_checks,
        "valid_code_odd_root_scale": 1,
        "native_response_binding": "Both scalar endpoints equal the pinned native model. Native words and phases are not replayed here.",
        "typed_fixtures": typed_fixtures(),
        "scope": "Common-frame scalar codes only. Native phase, routed access, complete typed controller and supplier remain unproved.",
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])
    print(json.dumps(checks, sort_keys=True))


if __name__ == "__main__":
    main()
