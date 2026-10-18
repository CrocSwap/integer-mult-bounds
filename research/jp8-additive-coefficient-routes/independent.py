"""Independent integer-grid enumeration and dirty-input block replay.

Imports neither the constructor nor its verifier. No Fraction arithmetic.
Ryan Haines, with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = 724


def check(condition, message):
    if not condition:
        raise ValueError(message)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def rational(text):
    pieces = text.split("/")
    return int(pieces[0]), int(pieces[1]) if len(pieces) == 2 else 1


def magnitude(op):
    a, b = abs(op[3]), op[4]
    g = gcd(a, b)
    check(a > 0 and b > 0 and b & (b - 1) == 0, "invalid dyadic coefficient")
    return a // g, b // g


def label(pair):
    a, b = pair
    return str(a) if b == 1 else f"{a}/{b}"


def shift_int(value, power):
    if power >= 0:
        return value << power
    divisor = 1 << -power
    check(value % divisor == 0, "integer-grid precision exhausted")
    return value // divisor


def enumerate_square(pair, limit, unit):
    a_num, a_den = rational(pair["from"])
    b_num, b_den = rational(pair["to"])
    a, b = a_num * unit // a_den, b_num * unit // b_den
    cap = max(a, b_num * unit)
    found = []
    for u in range(-limit, limit + 1):
        middle = shift_int(a, u) + unit
        for v in range(-limit, limit + 1):
            endpoint = shift_int(middle, v)
            if endpoint == b and max(a, middle, b) <= cap:
                found.append([abs(u) + 1 + abs(v), u, v])
    return sorted(found)


def shifts(target, power):
    return [["double" if power > 0 else "halve", target]] * abs(power)


def block_program(events, block):
    word = events[block["start"]:block["stop"]]
    check(len(word) >= 2 and len(block["routes"]) == len(word) - 1,
          "bad block geometry")
    source = word[0][1][2][1]
    a, b = magnitude(word[0][1])
    ops = [["clear", WORK], ["add", WORK, source]]
    for digit in format(a, "b")[1:]:
        ops.append(["double", WORK])
        if digit == "1":
            ops.append(["add", WORK, source])
    ops += shifts(WORK, -(b.bit_length() - 1))
    for j, event in enumerate(word):
        check(event[0] == "scalar" and event[2] == 1, "non-full-frame block")
        op = event[1]
        check(op[0] == "add" and op[1][0] == op[2][0] == "L"
              and op[2][1] == source and op[1][1] != source, "source/frame violation")
        if j:
            route = block["routes"][j - 1]
            if route[0] == "shift":
                check(len(route) == 2, "malformed shift")
                ops += shifts(WORK, route[1])
            else:
                check(route[0] == "read" and len(route) == 3, "malformed read")
                ops += shifts(WORK, route[1])
                ops.append(["add", WORK, source])
                ops += shifts(WORK, route[2])
        ops.append(["add" if op[3] > 0 else "sub", op[1][1], WORK])
    return ops + [["clear", WORK]]


def evaluate_block(events, block, ops, unit):
    word = events[block["start"]:block["stop"]]
    source = word[0][1][2][1]
    regs = sorted({source, WORK} | {e[1][1][1] for e in word})
    positions = {r: i for i, r in enumerate(regs)}
    rows = {r: [unit * (i == positions[r]) for i in range(len(regs))] for r in regs}
    expected = copy.deepcopy(rows)
    norms = {r: unit for r in regs}
    reference_norms = dict(norms)
    cap = unit
    for event in word:
        op = event[1]
        a, b = magnitude(op)
        q = a * unit // b * (1 if op[3] > 0 else -1)
        expected[op[1][1]][positions[source]] += q
        reference_norms[op[1][1]] += abs(q)
        cap = max(cap, a * unit, reference_norms[op[1][1]])
    expected[WORK] = [0] * len(regs)
    prefix = unit
    for instruction in ops:
        tag, target = instruction[:2]
        check(target in rows, "unknown integer target")
        if tag == "clear":
            rows[target], norms[target] = [0] * len(regs), 0
        elif tag in ("add", "sub"):
            src = instruction[2]
            check(target != src, "aliased integer operation")
            sign = 1 if tag == "add" else -1
            rows[target] = [x + sign * y for x, y in zip(rows[target], rows[src])]
            norms[target] += norms[src]
        else:
            check(tag in ("double", "halve"), "unknown integer primitive")
            k = 1 if tag == "double" else -1
            rows[target] = [shift_int(x, k) for x in rows[target]]
            norms[target] = shift_int(norms[target], k)
        prefix = max(prefix, norms[target])
    check(rows == expected, "independent block endpoint/clearing mismatch")
    check(prefix <= cap, "independent block prefix excursion")
    check(all(norms[r] == reference_norms[r] for r in regs if r != WORK),
          "independent live-envelope mismatch")
    return len(regs)


def expect_rejection(call, name):
    try:
        call()
    except ValueError:
        return name
    raise ValueError("independent negative control accepted: " + name)


def build():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    inputs = {}
    for name, expected in sources["payload_sha256"].items():
        data = (ROOT / name).read_bytes()
        if name.endswith(".gz"):
            data = gzip.decompress(data)
        check(hashlib.sha256(data).hexdigest() == expected, "independent source pin")
        if name.endswith("LOCAL-PROGRAMS.json.gz"):
            inputs = json.loads(data)
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    check(certificate["exponent_limit"] == 16, "route domain changed")
    receipt = {"method": "integer-grid exhaustive square plus dirty-input block matrices",
               "certificate_sha256": digest(certificate), "orientations": {}}
    for orientation in ("forward", "backward"):
        cert = certificate["orientations"][orientation]
        pairs = cert["distinct_pairs"]
        denom_bits = max((rational(p[k])[1].bit_length() - 1
                          for p in pairs for k in ("from", "to")), default=0)
        unit = 1 << (denom_bits + 32)
        for pair in pairs:
            actual = enumerate_square(pair, 16, unit)
            check(actual == pair["one_read_routes"], "incomplete or incorrect route census")
        events = inputs[orientation]
        previous, phase = None, None
        observed = Counter()
        for event in events:
            if event[0] == "phase":
                phase = event[1]
            current = None
            if (phase == "full_frame_cleanup" and event[0] == "scalar"
                    and event[2] == 1 and event[1][0] == "add"):
                op = event[1]
                q = magnitude(op)
                if op[1][0] == op[2][0] == "L" and op[1] != op[2] and q != (1, 1):
                    current = (op[2][1], q)
            if previous and current and previous[0] == current[0]:
                observed[(label(previous[1]), label(current[1]))] += 1
            previous = current
        check(observed == {(p["from"], p["to"]): p["occurrences"] for p in pairs},
              "omitted source-pair coverage")
        columns, old, new, fixture = 0, 0, 0, None
        for block in cert["blocks"]:
            ops = block_program(events, block)
            check(digest(ops) == block["primitive_sha256"], "independent primitive hash")
            columns += evaluate_block(events, block, ops, unit)
            for event in events[block["start"]:block["stop"]]:
                a, b = magnitude(event[1])
                old += a.bit_length() + a.bit_count() + b.bit_length() + 1
            new += len(ops)
            if fixture is None and any(r[0] == "read" for r in block["routes"]):
                fixture = (block, ops)
        controls = []
        if fixture:
            block, ops = fixture
            mutations = [("initial_clear", ops[1:]), ("final_clear", ops[:-1])]
            wrong_sign = copy.deepcopy(ops)
            j = next(j for j, o in enumerate(ops) if o[0] in ("add", "sub") and o[1] != WORK)
            wrong_sign[j][0] = "sub" if wrong_sign[j][0] == "add" else "add"
            mutations.append(("target_sign", wrong_sign))
            growth = ops[:-1] + [["double", WORK]] * 32 + [["halve", WORK]] * 32 + ops[-1:]
            mutations.append(("endpoint_neutral_growth", growth))
            for name, bad in mutations:
                controls.append(expect_rejection(
                    lambda bad=bad, es=events, b=block, scale=unit:
                    evaluate_block(es, b, bad, scale), name))
        receipt["orientations"][orientation] = {
            "distinct_pairs": len(pairs), "exponent_pairs_checked": 1089 * len(pairs),
            "blocks": len(cert["blocks"]), "block_input_columns": columns,
            "real_primitives_saved": 2 * (old - new), "negative_controls": controls}
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    receipt = build()
    if args.write:
        check(not args.write.exists(), "refusing to replace existing independent receipt")
        args.write.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    else:
        check(receipt == json.loads((HERE / "INDEPENDENT.json").read_text()),
              "independent committed receipt mismatch")
    f = receipt["orientations"]["forward"]
    print(f"PASS_INDEPENDENT_ADDITIVE_ROUTES pairs={f['distinct_pairs']} "
          f"exponent_pairs={f['exponent_pairs_checked']} "
          f"saved={f['real_primitives_saved']} controls={len(f['negative_controls'])}")


if __name__ == "__main__":
    main()
