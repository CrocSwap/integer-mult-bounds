"""Emit the actual unnormalised capture and check each scalar prefix."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
PINS = {
    "section": (
        LANES / "coherent-port/section-entry-20261020/SECTION.json",
        "23568099ea426947015eca86f7d86742a4758f33327e725b047441daab7c8bd7",
    ),
    "response": (
        LANES / "new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json",
        "5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c",
    ),
    "constants": (
        HERE / "centre-constants-normal/CENTRE-CONSTANTS.json",
        "9f45130ccde5bf1624bf051f4b10023411d6f35f0ac99bd6ab13572d4c530368",
    ),
    "code": (
        HERE / "unnormalised-final-normal/UNNORMALISED-CODE.json",
        "8dd0706ad41a843c9e74346b181389712a81ba6f354fdd019688e2d6b094908e",
    ),
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sparse(rows):
    result = []
    for row in rows:
        entries = row.items() if isinstance(row, dict) else enumerate(row)
        result.append({int(j): F(x) for j, x in entries if F(x)})
    return result


def unit(n):
    return [{i: F(1)} for i in range(n)]


def add(a, b, coefficient):
    out = a.copy()
    for j, value in b.items():
        out[j] = out.get(j, F(0)) + coefficient * value
        if not out[j]:
            del out[j]
    return out


def multiply(a, b):
    out = []
    for row in a:
        target = {}
        for j, value in row.items():
            target = add(target, b[j], value)
        out.append(target)
    return out


def inverse_word(word):
    answer = []
    for gate in reversed(word):
        kind = gate[0]
        if kind == "ADD":
            answer.append(gate[:3] + [-gate[3]])
        elif kind == "SCALE2":
            answer.append(gate[:2] + [-gate[2]])
        elif kind == "MULTIPLY_ODD":
            answer.append(["DIVIDE_ODD"] + gate[1:])
        elif kind == "DIVIDE_ODD":
            answer.append(["MULTIPLY_ODD"] + gate[1:])
        else:
            need(kind == "NEG", "Known invertible gate")
            answer.append(gate[:])
    return answer


def linear_add(target, source, value):
    need(target != source and value, "Distinct nonzero scatter")
    sign = 1 if value > 0 else -1
    absolute = abs(value)
    exponent = 0
    while absolute > 1 and absolute.denominator == 1 and absolute.numerator % 2 == 0:
        absolute /= 2
        exponent += 1
    while absolute < 1 and absolute.numerator == 1 and absolute.denominator % 2 == 0:
        absolute *= 2
        exponent -= 1
    need(absolute == 1, "Actual scatter coefficient is a signed binary power")
    out = [["SCALE2", source, 1 if exponent > 0 else -1]] * abs(exponent)
    out += [["ADD", target, source, sign]]
    out += [["SCALE2", source, -1 if exponent > 0 else 1]] * abs(exponent)
    return out


def selected_minor_word(selected):
    word = []
    for i in range(0, 16, 2):
        x, y = selected[i:i + 2]
        word += [["ADD", x, y, 1], ["SCALE2", y, 1],
                 ["ADD", y, x, -1], ["NEG", y]]
    permutation = [0, 12, 1, 14, 5, 11, 3, 9, 7, 15, 2, 4, 10, 13, 6, 8]
    current = list(range(16))
    for i, desired in enumerate(permutation):
        j = current.index(desired)
        if i == j:
            continue
        x, y = selected[i], selected[j]
        word += [["ADD", x, y, 1], ["ADD", y, x, -1],
                 ["ADD", x, y, 1], ["NEG", y]]
        current[i], current[j] = current[j], current[i]
    for i in (1, 5, 7, 9, 12, 14, 15, *range(16, 30)):
        word.append(["NEG", selected[i]])
    for target, source in ((1, 0), (9, 8), (13, 12)):
        word += linear_add(selected[target], selected[source], F(2))
    return word


def relabel(word, selected):
    result = []
    for gate in word:
        copy = gate[:]
        copy[1] = selected[copy[1]]
        if copy[0] == "ADD":
            copy[2] = selected[copy[2]]
        result.append(copy)
    return result


def height(value, p):
    denominator, answer = value.denominator, 0
    while denominator % p == 0:
        denominator //= p
        answer += 1
    return answer


def replay(word, initial=None, exact_divisions=False):
    state = unit(640)
    if initial is not None:
        state[:112] = [row.copy() for row in initial]
    stored = max(sum(abs(x) for x in row.values()) for row in state)
    operand = stored
    heights = {p: max(height(x, p) for row in state for x in row.values())
               for p in (2, 3, 5)}
    exact_count = Counter()
    for gate in word:
        kind, target = gate[:2]
        need(0 <= target < 112, "Only data fields are written")
        if kind == "ADD":
            source, sign = gate[2:]
            need(0 <= source < 112 and source != target and sign in (-1, 1),
                 "Unit ADD on data fields")
            operand = max(operand, sum(abs(x) for x in state[target].values())
                          + sum(abs(x) for x in state[source].values()))
            state[target] = add(state[target], state[source], sign)
        elif kind == "NEG":
            state[target] = {j: -x for j, x in state[target].items()}
        else:
            need(kind in ("SCALE2", "MULTIPLY_ODD", "DIVIDE_ODD"), "Known scalar gate")
            if kind == "SCALE2":
                need(gate[2] in (-1, 1), "One-bit binary scale")
                factor = F(2) ** gate[2]
            else:
                factor = F(gate[2])
                need(factor in (3, 5), "Actual odd factor")
                if kind == "DIVIDE_ODD":
                    if exact_divisions:
                        need(all(x.denominator % gate[2] and x.numerator % gate[2] == 0
                                 for x in state[target].values()), "Exact valid-code division")
                        exact_count[str(gate[2])] += 1
                    factor = 1 / factor
            state[target] = {j: factor * x for j, x in state[target].items()}
        stored = max(stored, sum(abs(x) for x in state[target].values()))
        for p in heights:
            heights[p] = max(heights[p], max((height(x, p) for x in state[target].values()), default=0))
    need(state[112:] == unit(640)[112:], "All 528 other roles remain arbitrary and unchanged")
    need(all(j < 112 for row in state[:112] for j in row), "No other baseline enters data")
    return state[:112], {"max_stored_row_l1": str(stored), "max_ADD_operand_l1": str(operand),
                        "denominator_heights": heights,
                        "checked_exact_complex_divisions": dict(sorted(exact_count.items()))}


def invoice(word):
    counts = Counter(gate[0] for gate in word)
    scans = Counter((gate[0], gate[2]) for gate in word
                    if gate[0] in ("MULTIPLY_ODD", "DIVIDE_ODD"))
    return {"old_real_scalar_units": 8 * counts["ADD"] + 2 * (counts["SCALE2"] + counts["NEG"]),
            "gate_counts": dict(sorted(counts.items())),
            "real_fixed_odd_scans": {kind + "_" + str(p): 2 * count
                                     for (kind, p), count in sorted(scans.items())},
            "new_owned_fields": 0, "native_children": 0, "maps_inside_common_chart": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    sources, pins = {}, {}
    for name, (path, digest) in PINS.items():
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == digest, "Pinned source " + name)
        sources[name] = json.loads(raw)
        pins[name] = {"path": str(path), "sha256": digest}
    section, response = sources["section"], sources["response"]
    selected, ordinary = section["selected_carriers"], section["ordinary_carriers"]
    u, v = sparse(response["correction_U"]), sparse(response["correction_V"])
    constants = sources["constants"]["families"]["rank30"]["words"]
    word = selected_minor_word(selected)
    minor_target = unit(112)
    for i, p in enumerate(selected):
        minor_target[p] = {selected[j]: x for j, x in sparse(section["minor_inverse"])[i].items()}
    need(replay(word)[0] == minor_target, "Literal actual selected minor inverse")
    boundaries = {"minor_inverse": len(word)}
    for p in ordinary:
        for j, value in sorted(u[p].items()):
            word += linear_add(p, selected[j], -value)
    boundaries["complement"] = len(word)
    word += relabel(constants["B0"], selected)
    boundaries["B0"] = len(word)
    for i, row in enumerate(v):
        for p in ordinary:
            if p in row:
                word += linear_add(selected[i], p, row[p])
    boundaries["capture"] = len(word)
    inverse = inverse_word(word)
    target = sparse(sources["code"]["capture"])
    inverse_target = sparse(sources["code"]["decode"])
    actual, forward_bounds = replay(word)
    need(actual == target, "All 640 capture columns")
    actual, inverse_bounds = replay(inverse)
    need(actual == inverse_target, "All 640 generic decode columns")
    actual, valid_bounds = replay(inverse, target, True)
    need(actual == unit(112), "Exact valid-code decode")
    need(replay(word, inverse_target)[0] == unit(112), "Other inverse order")
    chains = {}
    for label in ("G0", "G0_inverse"):
        middle = relabel(constants[label], selected)
        full = word + middle + inverse
        actual, bounds = replay(full, exact_divisions=True)
        if label == "G0":
            expected = sparse(response["response"])
        else:
            h_inverse = unit(112)
            for i, p in enumerate(selected):
                h_inverse[p] = {selected[j]: x for j, x in sparse(section["H_inverse"])[i].items()}
            expected = multiply(inverse_target, multiply(h_inverse, target))
        need(actual == expected, "Complete capture/action/decode chain " + label)
        chains[label] = {"invoice": invoice(full), "prefix_bounds": bounds}
    payload = {"source_pins": pins, "selected_carriers": selected, "ordinary_carriers": ordinary,
               "capture": word, "decode": inverse, "capture_boundaries": boundaries}
    raw = (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode()
    (args.out / "CAPTURE-WORD.json").write_bytes(raw)
    receipt = {"status": "PASS_ACTUAL_UNNORMALISED_CAPTURE_WORD", "source_pins": pins,
               "payload_sha256": sha256(raw).hexdigest(), "all_input_columns": 640,
               "unchanged_other_roles": 528,
               "capture": {"invoice": invoice(word), "prefix_bounds": forward_bounds},
               "generic_decode": {"invoice": invoice(inverse), "prefix_bounds": inverse_bounds},
               "valid_decode": valid_bounds, "complete_scalar_chains": chains,
               "scope": "Literal common-chart scalar code only. No physical source views or native controller."}
    (args.out / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])
    print(json.dumps({k: receipt[k] for k in ("capture", "generic_decode", "valid_decode", "complete_scalar_chains")},
                     sort_keys=True))


if __name__ == "__main__":
    main()
