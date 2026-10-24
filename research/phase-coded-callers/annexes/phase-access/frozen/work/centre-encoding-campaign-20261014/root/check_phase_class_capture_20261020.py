"""Check paired centre codes on the actual rank-sixteen response."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LANES = ROOT.parent / "lanes"
PINS = {
    "capture": (
        "bridge-access-20261017/rank16-capture-20261020/run-normal/CAPTURE.json",
        "cd6d621140290c73a771e1d6c531d2ffa00ae278e5b4e39b4ad9ff1ae00cc888",
    ),
    "pairs": (
        "independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json",
        "3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585",
    ),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def source(key):
    name, pin = PINS[key]
    raw = (LANES / name).read_bytes()
    need(sha256(raw).hexdigest() == pin, "Source pin: " + key)
    return json.loads(raw)


def ident(n):
    return [{i: F(1)} for i in range(n)]


def add(row, other, coefficient):
    for column, value in other.items():
        new = row.get(column, F(0)) + coefficient * value
        if new:
            row[column] = new
        else:
            row.pop(column, None)


def product(a, b):
    result = []
    for row in a:
        out = {}
        for j, value in row.items():
            add(out, b[j], value)
        result.append(out)
    return result


def encoded(a):
    return [{str(j): str(c) for j, c in row.items()} for row in a]


def decoded(a):
    return [{int(j): F(c) for j, c in row.items()} for row in a]


def inverse_word(word):
    result = []
    for op, target, source, c in reversed(word):
        if op in ("fixed_multiply", "fixed_divide"):
            new_op = "fixed_divide" if op == "fixed_multiply" else "fixed_multiply"
            result.append([new_op, target, source, c])
        else:
            result.append([op, target, source, str(-F(c) if op == "add" else 1 / F(c))])
    return result


def replay(word, n=112):
    rows = ident(n)
    largest = F(1)
    for op, target, source, coefficient in word:
        coefficient = F(coefficient)
        need(0 <= target < 112, "Only the data bank is changed")
        if op == "add":
            need(source != target and 0 <= source < 112, "An off-diagonal ADD")
            add(rows[target], rows[source], coefficient)
        else:
            need(op in ("scale", "fixed_multiply", "fixed_divide") and coefficient,
                 "An invertible scalar operation")
            if op == "fixed_divide":
                coefficient = 1 / coefficient
            rows[target] = {j: coefficient * c for j, c in rows[target].items()}
        largest = max(largest, sum(map(abs, rows[target].values())))
    return rows, largest


def invoice(word):
    old = multiply = divide = 0
    for op, _, _, coefficient in word:
        if op == "fixed_multiply":
            multiply += 2
        elif op == "fixed_divide":
            divide += 2
        else:
            coefficient = F(coefficient)
            a, b = abs(coefficient.numerator), coefficient.denominator
            need(a and not b & (b - 1), "A dyadic coefficient")
            if op == "scale":
                need(not a & (a - 1), "A dyadic unit")
                old += 2 * (abs(a.bit_length() - b.bit_length()) + (coefficient < 0))
            else:
                old += 2 * (1 + a.bit_length() + a.bit_count() + b.bit_length())
    return {
        "old_real_scalar_units": old, "real_fixed_three_multiplication_scans": multiply,
        "real_fixed_three_division_scans": divide, "owned_fields": 0,
        "native_children_inside_common_chart": 0,
    }


def unit_word(pairs):
    result = []
    for pair in pairs:
        a, b = pair["ports"]
        (aa, ab), (ba, bb) = pair["matrix"]
        need(abs(aa) == abs(ab) == abs(ba) == abs(bb) == 1, "Signed pair")
        need(aa * bb == -ab * ba, "Hadamard determinant")
        if aa != 1:
            result.append(["scale", a, None, str(aa)])
        result.extend([
            ["add", a, b, str(ab)],
            ["scale", b, None, str(2 * bb)],
            ["add", b, a, str(ba * aa)],
        ])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    capture, pairs = source("capture"), source("pairs")["pair_codes"]
    labels = capture["ports"]
    space = [0]
    for basis in [30, 45, 75, 384]:
        space += [x ^ basis for x in space]
    need(len(set(space)) == 16, "The root space has dimension four")
    need(all((x & y).bit_count() % 2 == 0 for x in space for y in space),
         "The root space is isotropic")
    classes = [min(q ^ r for r in space) for q in labels]
    need(all(classes[a] == classes[b] for a, b in (p["ports"] for p in pairs)),
         "The physical pair code preserves phase classes")

    h_word = unit_word(pairs)
    h = replay(h_word)[0]
    hi = replay(inverse_word(h_word))[0]
    pairing_word, reduced_word, groups = [], [], []
    active = []
    s = ident(112)
    k_matrix = ident(112)
    for original in capture["groups"]:
        ports, signs = original["ports"], original["signs"]
        sign = dict(zip(ports, signs))
        partition = {}
        for port in ports:
            partition.setdefault(classes[port], []).append(port)
        same_class_pairs = [sorted(value) for _, value in sorted(partition.items())]
        need(all(len(pair) == 2 for pair in same_class_pairs), "Every class has two modes")
        local_active = []
        for a, b in same_class_pairs:
            # The first output is the signed sum; the second is a difference.
            if sign[a] != 1:
                pairing_word.append(["scale", a, None, str(sign[a])])
            pairing_word.extend([
                ["add", a, b, str(sign[b])],
                ["scale", b, None, str(-2 * sign[b])],
                ["add", b, a, "1"],
            ])
            local_active.append(a)
        m = len(local_active)
        p = local_active[0]
        active += local_active
        for a in local_active[1:]:
            reduced_word.append(["add", a, p, "1"])
        reduced_word.append(["scale", p, None, str(-(m - 2))])
        for a in local_active[1:]:
            reduced_word.append(["add", p, a, "1"])
        if m == 3:
            reduced_word.extend([
                ["fixed_divide", p, None, "3"],
                ["scale", p, None, "2"],
            ])
        else:
            need(m == 4, "Only the actual reduced block sizes")
            reduced_word.append(["scale", p, None, "1/2"])
        for a in local_active[1:]:
            reduced_word.append(["add", a, p, "-1"])
        selected = set(same_class_pairs[0])
        u = {a: F(sign[a] * (2 * int(a in selected) - 1)) for a in ports}
        v = {a: F(2 * sign[a], len(ports)) - F(sign[a] * int(a in selected), 2)
             for a in ports}
        for a, value in u.items():
            add(s[a], v, value)
        for a in selected:
            add(k_matrix[a], {b: F(sign[b]) for b in selected},
                -F(len(ports) * sign[a], 2))
        groups.append({
            "ports": ports, "signs": signs, "pairs": same_class_pairs,
            "active_sum_carriers": local_active, "centre_pair": sorted(selected),
            "block_size": len(ports), "reduced_size": m,
            "rank_one_determinant": str(F(8, len(ports)) - 2),
        })

    t_word = h_word + pairing_word
    t, _ = replay(t_word)
    ti, _ = replay(inverse_word(t_word))
    pmat = replay(pairing_word)[0]
    pmi = replay(inverse_word(pairing_word))[0]
    reduced = replay(reduced_word)[0]
    need(product(pmat, product(s, pmi)) == reduced, "The exact reduction to class sums")
    inactive = set(range(112)) - set(active)
    need(len(active) == len(inactive) == 56, "The two sets each have 56 coordinates")
    need(all(reduced[j] == {j: F(1)} for j in inactive), "All differences are fixed")
    need(all(not (set(reduced[j]) & inactive) for j in active), "No difference is read")

    word = t_word + reduced_word + inverse_word(t_word)
    inverse = inverse_word(word)
    c, growth = replay(word, 640)
    ci, inverse_growth = replay(inverse, 640)
    need(product(c, ci) == product(ci, c) == ident(640), "Both inverse orders")
    need(all(c[j] == ci[j] == {j: F(1)} for j in range(112, 640)),
         "All 528 other roles are unchanged")
    need(c[:112] == product(hi, product(s, h)), "The physical rank-one code")
    response = decoded(capture["response"])
    centre = product(c[:112], product(response, ci[:112]))
    need(centre == product(hi, product(k_matrix, h)), "The actual response")
    need(all(classes[i] == classes[j] for i, row in enumerate(centre) for j in row),
         "The output response stays in each phase class")
    need(all(classes[i] == classes[j] for i, row in enumerate(t) for j in row),
         "The full reduction stays in each phase class")

    # This is a formal phase test. The exponent difference labels each block.
    # Equal class labels make every T coefficient commute with the class phase.
    def formal_conjugate(matrix):
        return [
            {(j, classes[i], classes[j]): value for j, value in row.items()}
            for i, row in enumerate(matrix)
        ]
    need(formal_conjugate(centre) == [
        {(j, classes[j], classes[j]): value for j, value in row.items()}
        for row in centre
    ], "The centre action has no nontrivial class-phase ratio")

    payload = {
        "source_pins": PINS, "phase_space_basis": [30, 45, 75, 384],
        "classes": classes, "groups": groups, "active_sum_carriers": active,
        "code": encoded(c[:112]), "inverse_code": encoded(ci[:112]),
        "centre_response": encoded(centre), "reduction": encoded(t),
        "reduced_code": encoded(reduced),
        "scalar_word": word, "inverse_scalar_word": inverse,
        "reduction_word": t_word, "reduced_code_word": reduced_word,
    }
    raw = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode()
    (args.out / "PAIRED-CODE.json").write_bytes(raw)
    receipt = {
        "status": "PASS_ACTUAL_PHASE_CLASS_CAPTURE",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_sha256": sha256(raw).hexdigest(), "source_pins": PINS,
        "arbitrary_columns": 640, "unchanged_other_roles": 528,
        "active_class_sums": len(active),
        "code_prefix_norm": str(growth), "inverse_prefix_norm": str(inverse_growth),
        "literal_scalar_operations": len(word),
        "code_invoice": invoice(word), "inverse_invoice": invoice(inverse),
        "reduction_invoice": invoice(t_word),
        "reduced_code_invoice": invoice(reduced_word),
        "conditional_native_phase_calls": 2 * len(active),
        "scope": (
            "Exact scalar code and phase-class reduction. The 112-call bound assumes "
            "paid monomial phase alignment and rank-one phases in a carried common "
            "frame. It does not implement frame preparation/removal or a supplier."
        ),
    }
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
