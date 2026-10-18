"""Integer-only block matrices and a separate complete dyadic prefix replay.

No imports from verify.py or the vendored constructor. Ryan Haines,
with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import copy
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = 724


def check(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def normalized(n, e):
    if n == 0:
        return 0, 0
    zeros = min(e, (n & -n).bit_length() - 1)
    return n >> zeros, e - zeros


def add_norm(a, b):
    e = max(a[1], b[1])
    return normalized((a[0] << (e - a[1])) + (b[0] << (e - b[1])), e)


def greater(a, b):
    return a[0] << b[1] > b[0] << a[1]


def fraction_text(pair):
    n, e = normalized(*pair)
    return str(n) if not e else f"{n}/{1 << e}"


def reg(pair):
    check(pair[0] in ("L", "C"), "invalid register tag")
    return pair[1] if pair[0] == "L" else 716 + pair[1]


def macro(op):
    tag, target = op[0], reg(op[1])
    if tag == "clear":
        return [["clear", target]]
    if tag == "copy":
        return [["copy", target, reg(op[2])]]
    if tag == "scale":
        a, b = abs(op[2]), abs(op[3])
        g = gcd(a, b)
        a, b = a // g, b // g
        check(a and a & (a - 1) == 0 and b & (b - 1) == 0, "non-dyadic scale")
        k = a.bit_length() - b.bit_length()
        return ([[("double" if k > 0 else "halve"), target]] * abs(k)
                + ([["neg", target]] if (op[2] < 0) != (op[3] < 0) else []))
    check(tag == "add", "unknown macro")
    source = reg(op[2])
    a, b = abs(op[3]), abs(op[4])
    g = gcd(a, b)
    a, b = a // g, b // g
    check(a and b & (b - 1) == 0 and source != target, "invalid add macro")
    result = [["clear", WORK], ["add", WORK, source]]
    for bit in format(a, "b")[1:]:
        result.append(["double", WORK])
        if bit == "1":
            result.append(["add", WORK, source])
    result += [["halve", WORK]] * (b.bit_length() - 1)
    negative = (op[3] < 0) != (op[4] < 0)
    return result + [["sub" if negative else "add", target, WORK], ["clear", WORK]]


def block_matrix(events, block, ops):
    word = events[block["start"]:block["stop"]]
    target = block["common_backward_target"]
    check(all(e[0] == "scalar" and e[2] == 1 and e[1][0] == "add"
              and e[1][1] == ["L", target] and e[1][2][0] == "L"
              and e[1][2][1] != target for e in word), "invalid fan-in block")
    regs = sorted({target, WORK} | {e[1][2][1] for e in word})
    pos = {r: i for i, r in enumerate(regs)}
    d = max(sum(o[0] == "halve" for o in ops),
            max(e[1][4].bit_length() - 1 for e in word))
    unit = 1 << d
    rows = {r: [unit * (i == pos[r]) for i in range(len(regs))] for r in regs}
    norms = {r: unit for r in regs}
    expected = copy.deepcopy(rows)
    old_target_norm, old_prefix = unit, unit
    for event in word:
        op = event[1]
        check(unit % op[4] == 0, "insufficient grid for reference coefficient")
        expected[target][pos[op[2][1]]] += op[3] * (unit // op[4])
        a, b = abs(op[3]), abs(op[4])
        g = gcd(a, b)
        a, b = a // g, b // g
        old_target_norm += a * (unit // b)
        old_prefix = max(old_prefix, a * unit, old_target_norm)
    expected[WORK] = [0] * len(regs)
    check(fraction_text((old_prefix, d)) == block["isolated_original_prefix"],
          "independent original isolated prefix mismatch")
    prefix = unit
    for instruction in ops:
        tag, out = instruction[:2]
        check(out in rows, "unknown block register")
        if tag == "clear":
            rows[out], norms[out] = [0] * len(regs), 0
        elif tag in ("add", "sub"):
            src = instruction[2]
            check(out != src, "aliased block update")
            sign = 1 if tag == "add" else -1
            rows[out] = [a + sign * b for a, b in zip(rows[out], rows[src])]
            norms[out] += norms[src]
        else:
            check(tag in ("double", "halve"), "unknown block primitive")
            if tag == "double":
                rows[out] = [2 * a for a in rows[out]]
                norms[out] *= 2
            else:
                check(all(a % 2 == 0 for a in rows[out]) and norms[out] % 2 == 0,
                      "integer-grid precision exhausted")
                rows[out] = [a // 2 for a in rows[out]]
                norms[out] //= 2
        prefix = max(prefix, norms[out])
    check(rows == expected, "independent matrix/clearing mismatch")
    check(fraction_text((prefix, d)) == block["isolated_companion_prefix"],
          "independent isolated prefix mismatch")
    return len(regs)


def prefix_replay(events, blocks):
    norm = {r: (1, 0) for r in range(725)}
    prefix, index, primitives = (1, 0), 0, 0
    starts = {b["start"]: b for b in blocks}
    check(len(starts) == len(blocks), "duplicate block starts")
    prior = 0
    for block in blocks:
        check(prior <= block["start"] < block["stop"] <= len(events), "block overlap/bounds")
        prior = block["stop"]
    while index < len(events):
        event = events[index]
        if index in starts:
            block = starts[index]
            ops, index = block["backward_primitives"], block["stop"]
        else:
            ops = macro(event[1]) if event[0] == "scalar" else []
            index += 1
        for instruction in ops:
            tag, target = instruction[:2]
            if tag == "clear":
                norm[target] = (0, 0)
            elif tag == "copy":
                norm[target] = norm[instruction[2]]
            elif tag in ("add", "sub"):
                norm[target] = add_norm(norm[target], norm[instruction[2]])
            elif tag == "halve":
                n, e = norm[target]
                norm[target] = normalized(n, e + 1)
            elif tag == "double":
                n, e = norm[target]
                norm[target] = normalized(2 * n, e)
            else:
                check(tag == "neg", "unknown norm primitive")
            if greater(norm[target], prefix):
                prefix = norm[target]
        primitives += len(ops)
    check(all(norm[r] == (0, 0) for r in range(716, 725)), "private norm not cleared")
    return {"real_primitives": 2 * primitives, "prefix_l1": fraction_text(prefix)}


def reject(call, name):
    try:
        call()
    except (ValueError, KeyError):
        return name
    raise ValueError("independent negative control accepted: " + name)


def build():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    data = {}
    for path, expected in pins["payload_sha256"].items():
        raw = (ROOT / path).read_bytes()
        if path.endswith(".gz"):
            raw = gzip.decompress(raw)
        check(hashlib.sha256(raw).hexdigest() == expected, "independent source pin")
        if path.endswith((".json", ".json.gz")):
            data[path] = json.loads(raw)
    programs = next(v for k, v in data.items() if k.endswith("LOCAL-PROGRAMS.json.gz"))
    spec = next(v for k, v in data.items() if k.endswith("/data/SPEC.json"))["providers"]["jp8"]
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    blocks = certificate["blocks"]
    events = programs["backward"]
    columns, saving, grew = 0, 0, 0
    for block in blocks:
        ops = block["backward_primitives"]
        check(digest(ops) == block["backward_primitive_sha256"], "backward primitive hash")
        columns += block_matrix(events, block, ops)
        old = 2 * sum(len(macro(e[1])) for e in events[block["start"]:block["stop"]])
        new = 2 * len(ops)
        check((old, new) == (block["real_primitives_before"], block["real_primitives_after"]),
              "independent block invoice mismatch")
        saving += old - new
        def parsed(s):
            parts = [int(p) for p in s.split("/")]
            return parts[0], parts[1].bit_length() - 1 if len(parts) == 2 else 0
        grew += greater(parsed(block["isolated_companion_prefix"]),
                        parsed(block["isolated_original_prefix"]))
    full = prefix_replay(events, blocks)
    original = spec["complete_contract"]["local"]["backward"]
    check(full["real_primitives"] == original["real_component_primitives"] - saving,
          "complete independent invoice mismatch")
    check(full["prefix_l1"] == original["prefix_l1"], "complete independent prefix changed")
    fixture = next(b for b in blocks if any(r[0] == "read" for r in b["forward_routes"]))
    ops = fixture["backward_primitives"]
    mutations = [("initial_clear", ops[1:]), ("final_clear", ops[:-1])]
    bad = copy.deepcopy(ops)
    j = next(j for j, op in enumerate(ops) if op[0] in ("add", "sub")
             and op[1] == fixture["common_backward_target"])
    bad[j][0] = "add" if bad[j][0] == "sub" else "sub"
    mutations.append(("inverse_sign", bad))
    mutations.append(("neutral_growth", ops[:-1] + [["double", WORK]] * 20
                      + [["halve", WORK]] * 20 + ops[-1:]))
    controls = [reject(lambda bad=bad: block_matrix(events, fixture, bad), name)
                for name, bad in mutations]
    return {"method": "independent integer block matrices and dyadic full-prefix recurrence",
            "certificate_sha256": digest(certificate), "blocks": len(blocks),
            "block_input_columns": columns, "real_saved": saving,
            "isolated_prefix_growth_blocks": grew, "complete_backward": full,
            "negative_controls": controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = build()
    if args.write:
        check(not args.write.exists(), "refusing to replace receipt")
        args.write.write_text(json.dumps(result, indent=2) + "\n")
    else:
        check(json.loads((HERE / "INDEPENDENT.json").read_text()) == result,
              "independent receipt mismatch")
    print(f"PASS_INDEPENDENT_TRANSPOSED_WORK blocks={result['blocks']} "
          f"columns={result['block_input_columns']} saved={result['real_saved']} "
          f"controls={len(result['negative_controls'])}")


if __name__ == "__main__":
    main()
