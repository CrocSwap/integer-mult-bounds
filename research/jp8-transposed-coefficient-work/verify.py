"""Exact inverse-transpose companion to PR811's positive coefficient work.

Ryan Haines, with substantial OpenAI Codex assistance. Apache-2.0.
The pinned forward constructor is retained verbatim in vendor/.
"""

import argparse
import copy
import gzip
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE / "vendor"))

import construct_seed31 as forward

WORK = forward.WORK
BASE = "c290b7b919790300e14004a75d8d24b55ca3c5b5"
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/"
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def load_inputs():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    require(pins["base_commit"] == BASE, "base pin mismatch")
    data = {}
    for path, expected in pins["payload_sha256"].items():
        raw = (ROOT / path).read_bytes()
        if path.endswith(".gz"):
            raw = gzip.decompress(raw)
        require(hashlib.sha256(raw).hexdigest() == expected, "source payload changed: " + path)
        if path.endswith((".json", ".json.gz")):
            data[path] = json.loads(raw)
    require(hashlib.sha256((HERE / "vendor/construct_seed31.py").read_bytes()).hexdigest()
            == pins["vendor_sha256"], "vendored forward constructor changed")
    spec = data[SPEC]["providers"]["jp8"]
    native = data[PROVIDER + "CANONICAL-WORD.json.gz"]
    programs = data[PROVIDER + "LOCAL-PROGRAMS.json.gz"]
    for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
        require(digest(data[PROVIDER + name]) == spec["artifact_semantic_sha256"][name],
                "historical SPEC binding failed")
    require((native["v"], native["R"], native["h"]) == (112, 492, 9), "dimensions changed")
    for orientation, events in programs.items():
        require(digest(events) == spec["program_hashes"][orientation], "program binding failed")
    return programs, native, spec


def dual_macro(op):
    require(op[0] == "add", "dual block contains a non-addition")
    return ["add", op[2], op[1], -op[3], op[4]]


def transpose(ops, source):
    """Transpose the cleared linear circuit; negate writes to original source."""
    result = []
    for op in reversed(ops):
        tag, target = op[:2]
        if tag in ("clear", "double", "halve"):
            require(target == WORK, "non-private clear/scale in forward block")
            result.append(list(op))
        else:
            require(tag in ("add", "sub"), "unsupported transposition primitive")
            require(target != source and target != op[2], "forward block writes source/aliases")
            new_target, new_source = op[2], target
            if new_target == source:
                tag = "sub" if tag == "add" else "add"
            result.append([tag, new_target, new_source])
    return result


class ExactMachine:
    """Literal primitive interpreter on arbitrary scalar input columns."""

    def __init__(self, registers=range(725)):
        self.rows = {r: {r: Q(1)} for r in registers}
        self.norm = {r: Q(1) for r in registers}
        self.prefix = Q(1)

    def run(self, ops):
        for op in ops:
            tag, target = op[:2]
            if tag == "clear":
                self.rows[target], self.norm[target] = {}, Q(0)
            elif tag == "copy":
                self.rows[target] = dict(self.rows[op[2]])
                self.norm[target] = self.norm[op[2]]
            elif tag in ("add", "sub"):
                source = op[2]
                require(source != target, "aliased primitive")
                sign = 1 if tag == "add" else -1
                for col, value in self.rows[source].items():
                    new = self.rows[target].get(col, Q(0)) + sign * value
                    if new:
                        self.rows[target][col] = new
                    else:
                        self.rows[target].pop(col, None)
                self.norm[target] += self.norm[source]
            else:
                require(tag in ("double", "halve", "neg"), "unknown primitive")
                factor = {"double": Q(2), "halve": Q(1, 2), "neg": Q(-1)}[tag]
                self.rows[target] = {c: factor * x for c, x in self.rows[target].items()}
                self.norm[target] *= abs(factor)
            self.prefix = max(self.prefix, self.norm[target])


def compare_boundary(f_events, b_events, block):
    start, stop = block["start"], block["stop"]
    for f, b in zip(f_events[start:stop], b_events[start:stop]):
        require(f[0] == b[0] == "scalar" and f[2] == b[2] == 1,
                "block crossed full-frame boundary")
        require(b[1] == dual_macro(f[1]), "backward block is not the scalar dual")
    source = f_events[start][1][2][1]
    primitive = forward.lower_block(f_events, block)
    companion = transpose(primitive, source)
    regs = {source, WORK} | {e[1][1][1] for e in f_events[start:stop]}
    reference, actual = ExactMachine(regs), ExactMachine(regs)
    for event in b_events[start:stop]:
        reference.run(forward.lower_macro(event[1]))
    actual.run(companion)
    require(actual.rows == reference.rows, "dirty-input companion boundary mismatch")
    require(not actual.rows[WORK], "companion private work survives")
    require(all(actual.norm[r] == reference.norm[r] for r in regs if r != WORK),
            "companion changed live positive envelope")
    require(len(primitive) == len(companion), "transposition changed cost")
    old = sum(len(forward.lower_macro(e[1])) for e in b_events[start:stop])
    return companion, {
        "start": start, "stop": stop, "common_backward_target": source,
        "forward_routes": block["routes"], "columns": len(regs),
        "forward_primitive_sha256": digest(primitive),
        "backward_primitives": companion,
        "backward_primitive_sha256": digest(companion),
        "real_primitives_before": 2 * old, "real_primitives_after": 2 * len(companion),
        "isolated_original_prefix": str(reference.prefix),
        "isolated_companion_prefix": str(actual.prefix),
    }


def full_replay(events, native, replacements, orientation):
    machine, index, count = ExactMachine(), 0, 0
    paid, non_scalar = Counter(), []
    while index < len(events):
        event = events[index]
        if index in replacements:
            stop, ops = replacements[index]
            require(not machine.rows[WORK], "work dirty at replacement boundary")
            for e in events[index:stop]:
                require(e[0] == "scalar" and e[2] == 1
                        and all(native["final"][r[1]] == 1 for r in e[1][1:3]),
                        "replacement touches a partial frame")
            index = stop
        else:
            ops = forward.lower_macro(event[1]) if event[0] == "scalar" else []
            if event[0] != "scalar":
                non_scalar.append(event)
                if event[0] == "climb":
                    paid[event[5]] += 1
                elif event[0] == "center":
                    paid[event[4]] += 1
                if event[0] in ("climb", "center", "adapter", "residual_adapter"):
                    require(not machine.rows[WORK], "work crosses an interface")
            index += 1
        machine.run(ops)
        count += len(ops)
    for r in range(716):
        expected = {r: Q(1)}
        if orientation == "forward" and 112 <= r < 224:
            expected[r - 112] = Q(1)
        elif orientation == "backward" and r < 112:
            expected[r + 112] = Q(-1)
        require(machine.rows[r] == expected, "complete shear endpoint mismatch")
    require(all(not machine.rows[r] for r in range(716, 725)), "private input leaked")
    require(dict(paid) == {int(k): v for k, v in native["local_profile"].items()},
            "paid recursive profile changed")
    require(machine.prefix < 2**192, "complete prefix exceeds inherited allowance")
    return {"columns": 725, "real_primitives": 2 * count,
            "prefix_l1": str(machine.prefix),
            "prefix_bits": machine.prefix.numerator.bit_length()
            - machine.prefix.denominator.bit_length() + 1,
            "non_scalar_sha256": digest(non_scalar),
            "paid_profile": {str(k): v for k, v in sorted(paid.items())}}


def reject(call, name):
    try:
        call()
    except (ValueError, KeyError):
        return name
    raise ValueError("negative control accepted: " + name)


def controls():
    f = [["phase", "full_frame_cleanup"],
         ["scalar", ["add", ["L", 1], ["L", 0], 1, 2], 1],
         ["scalar", ["add", ["L", 2], ["L", 0], -3, 2], 1]]
    b = [f[0]] + [["scalar", dual_macro(e[1]), 1] for e in f[1:]]
    block = forward.plan(f, True)[0]
    good, _ = compare_boundary(f, b, block)
    expected = ExactMachine([0, 1, 2, WORK])
    for event in b[1:]:
        expected.run(forward.lower_macro(event[1]))

    def check_ops(ops):
        actual = ExactMachine([0, 1, 2, WORK])
        actual.run(ops)
        require(actual.rows == expected.rows, "control endpoint/clearing mismatch")
        require(actual.prefix < 2**192, "control inherited prefix allowance")

    check_ops(good)
    cases = [("initial_clear", good[1:]), ("final_clear", good[:-1])]
    wrong_sign = copy.deepcopy(good)
    j = next(j for j, op in enumerate(good) if op[0] == "sub" and op[1] == 0)
    wrong_sign[j][0] = "add"
    cases.append(("missed_inverse_sign", wrong_sign))
    cases.append(("omitted_target_write", good[:j] + good[j + 1:]))
    cases.append(("forward_instead_of_reverse_order", list(reversed(good))))
    wrong_scale = copy.deepcopy(good)
    j = next(j for j, op in enumerate(good) if op[0] == "halve")
    wrong_scale[j][0] = "double"
    cases.append(("inverted_scale", wrong_scale))
    growth = good[:-1] + [["double", WORK]] * 200 + [["halve", WORK]] * 200 + good[-1:]
    cases.append(("endpoint_neutral_excess_growth", growth))
    result = [reject(lambda ops=ops: check_ops(ops), name) for name, ops in cases]
    bad = copy.deepcopy(b)
    bad[2][2] = 0
    result.append(reject(lambda: compare_boundary(f, bad, block), "frame_crossing"))
    bad = copy.deepcopy(b)
    bad[2][1][3] *= -1
    result.append(reject(lambda: compare_boundary(f, bad, block), "wrong_macro_dual"))
    result.append(reject(lambda: transpose([["add", 0, WORK]], 0), "forward_source_write"))
    return result


def equal_blocks(events):
    """Independent grouping for the historical equal-coefficient comparator."""
    phase, previous, blocks = None, None, []
    for index, event in enumerate(events):
        if event[0] == "phase":
            phase = event[1]
        current = forward.eligible(event, phase)
        if current is not None and current == previous:
            if blocks and blocks[-1]["stop"] == index:
                blocks[-1]["stop"] += 1
                blocks[-1]["routes"].append(["shift", 0])
            else:
                blocks.append({"start": index - 1, "stop": index + 1,
                               "routes": [["shift", 0]]})
        previous = current
    return blocks


def build():
    programs, native, spec = load_inputs()
    blocks = forward.plan(programs["forward"], True)
    certificate = {"schema": "jp8-transposed-private-work/1", "base_commit": BASE,
                   "assignment_seed": 25, "blocks": []}
    replacements = {"forward": {}, "backward": {}}
    for block in blocks:
        ops, item = compare_boundary(programs["forward"], programs["backward"], block)
        certificate["blocks"].append(item)
        replacements["forward"][block["start"]] = (block["stop"],
            forward.lower_block(programs["forward"], block))
        replacements["backward"][block["start"]] = (block["stop"], ops)
    result = {"schema": "jp8-transposed-private-work-replay/1", "base_commit": BASE,
              "negative_controls": controls(), "orientations": {},
              "certificate_sha256": digest(certificate), "blocks": len(blocks),
              "block_input_columns": sum(b["columns"] for b in certificate["blocks"])}
    for orientation in ("forward", "backward"):
        events = programs[orientation]
        row = full_replay(events, native, replacements[orientation], orientation)
        contract = spec["complete_contract"]["local"][orientation]
        original = 2 * sum(len(forward.lower_macro(e[1])) for e in events if e[0] == "scalar")
        require(original == contract["real_component_primitives"], "original count mismatch")
        require(row["prefix_l1"] == contract["prefix_l1"], "full positive prefix changed")
        row.update(original_real_primitives=original, saved_real_primitives=original-row["real_primitives"])
        result["orientations"][orientation] = row
        print(f"PASS_LITERAL_{orientation.upper()} columns=725 primitives={row['real_primitives']}",
              flush=True)
    contract = spec["complete_contract"]
    maximum = max(r["real_primitives"] for r in result["orientations"].values())
    result["unintegrated_budget"] = {
        "adapter_allowances": contract["local_adapters"], "compiler_charge": contract["compiler"],
        "original_local_bound": contract["local_primitive_bound"],
        "paired_candidate_local_bound": maximum + contract["local_adapters"] * contract["compiler"],
        "backward_only_local_bound": result["orientations"]["forward"]["original_real_primitives"]
        + contract["local_adapters"] * contract["compiler"],
        "new_kappa_claimed": False,
    }
    comparisons = {}
    for name, baseline in (("equal_magnitude", equal_blocks(programs["forward"])),
                           ("power_only", forward.plan(programs["forward"], False))):
        saved = sum(2 * (sum(len(forward.lower_macro(e[1])) for e in
                            programs["forward"][b["start"]:b["stop"]])
                         - len(forward.lower_block(programs["forward"], b))) for b in baseline)
        comparisons[name] = {"blocks": len(baseline), "backward_saved": saved,
                             "backward_primitives": 257280 - saved}
    result["comparators"] = comparisons
    grew = [b for b in certificate["blocks"] if Q(b["isolated_companion_prefix"])
            > Q(b["isolated_original_prefix"])]
    worst = max(grew, key=lambda b: Q(b["isolated_companion_prefix"])
                / Q(b["isolated_original_prefix"]))
    result["prefix_scope"] = {
        "isolated_growth_blocks": len(grew), "worst_start": worst["start"],
        "worst_ratio": str(Q(worst["isolated_companion_prefix"])
                           / Q(worst["isolated_original_prefix"])),
        "old_isolated_prefix": worst["isolated_original_prefix"],
        "new_isolated_prefix": worst["isolated_companion_prefix"],
    }
    fixture = [["phase", "full_frame_cleanup"]] + [
        ["scalar", ["add", ["L", r], ["L", 0], 1, 4], 1] for r in range(1, 5)]
    dual = [fixture[0]] + [["scalar", dual_macro(e[1]), 1] for e in fixture[1:]]
    _, witness = compare_boundary(fixture, dual, forward.plan(fixture, True)[0])
    require((witness["isolated_original_prefix"], witness["isolated_companion_prefix"])
            == ("2", "4"), "prefix counterexample changed")
    result["prefix_nonmonotonicity_witness"] = {"sources": 4, "coefficient": "-1/4",
                                               "old_prefix": "2", "transposed_prefix": "4"}
    return certificate, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    certificate, result = build()
    for name, obj in (("CERTIFICATE.json", certificate), ("EXPECTED.json", result)):
        if args.write:
            args.write.mkdir(parents=True, exist_ok=True)
            path = args.write / name
            require(not path.exists(), "refusing to replace output")
            if name == "CERTIFICATE.json":
                # One self-contained literal block per line keeps the review diff small.
                fields = ["  " + json.dumps(k) + ": " + json.dumps(v)
                          for k, v in obj.items() if k != "blocks"]
                fields.append('  "blocks": [\n' + ",\n".join(
                    "    " + json.dumps(b, separators=(",", ":")) for b in obj["blocks"])
                    + "\n  ]")
                path.write_text("{\n" + ",\n".join(fields) + "\n}\n")
            else:
                path.write_text(json.dumps(obj, indent=2) + "\n")
        else:
            require(json.loads((HERE / name).read_text()) == obj, name + " mismatch")
    b = result["orientations"]["backward"]
    print(f"PASS_JP8_TRANSPOSED_WORK backward_saved={b['saved_real_primitives']} "
          f"blocks={len(certificate['blocks'])} columns=725 controls={len(result['negative_controls'])}")


if __name__ == "__main__":
    main()
