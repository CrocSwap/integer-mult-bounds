"""Read-only exact certificate replay; --write explicitly creates artifacts.

Ryan Haines, with substantial OpenAI Codex assistance. Apache-2.0.
No pending-PR code is imported. See README.md for inherited source credit.
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
sys.path.insert(0, str(HERE))

from construct import (
    LIMIT,
    WORK,
    coefficient,
    eligible,
    exponent,
    lower_block,
    lower_macro,
    one_read_routes,
    plan,
    preparation_cost,
    register,
    require,
)

PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/"
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"
BASE = "66849e1475c930fd7732b1a0067ffee7e1e95f60"


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def load_inputs():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    require(pins["base_commit"] == BASE, "base pin mismatch")
    data = {}
    for path, expected in pins["payload_sha256"].items():
        payload = (ROOT / path).read_bytes()
        if path.endswith(".gz"):
            payload = gzip.decompress(payload)
        require(hashlib.sha256(payload).hexdigest() == expected,
                "source payload changed: " + path)
        if path.endswith((".json", ".json.gz")):
            data[path] = json.loads(payload)
    spec = data[SPEC]["providers"]["jp8"]
    for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
        require(digest(data[PROVIDER + name]) == spec["artifact_semantic_sha256"][name],
                "selected SPEC artifact binding failed")
    programs = data[PROVIDER + "LOCAL-PROGRAMS.json.gz"]
    require(set(programs) == {"forward", "backward"}, "orientation coverage")
    for name, events in programs.items():
        require(digest(events) == spec["program_hashes"][name], "program binding failed")
    native = data[PROVIDER + "CANONICAL-WORD.json.gz"]
    require((native["v"], native["R"], native["h"]) == (112, 492, 9),
            "supplier dimensions changed")
    return programs, native, spec


class Machine:
    """Sparse exact linear forms on arbitrary inputs and positive L1 envelope."""

    def __init__(self, registers=range(725)):
        self.rows = {r: {r: Q(1)} for r in registers}
        self.norms = {r: Q(1) for r in registers}
        self.prefix = Q(1)

    def execute(self, op):
        tag, target = op[:2]
        require(target in self.rows, "unknown primitive target")
        if tag == "clear":
            self.rows[target], self.norms[target] = {}, Q(0)
        elif tag == "copy":
            self.rows[target] = dict(self.rows[op[2]])
            self.norms[target] = self.norms[op[2]]
        elif tag in ("add", "sub"):
            source = op[2]
            require(target != source, "primitive source alias")
            sign = 1 if tag == "add" else -1
            row = self.rows[target]
            for col, value in self.rows[source].items():
                new = row.get(col, Q(0)) + sign * value
                if new:
                    row[col] = new
                else:
                    row.pop(col, None)
            self.norms[target] += self.norms[source]
        else:
            require(tag in ("double", "halve", "neg"), "unknown primitive")
            factor = {"double": Q(2), "halve": Q(1, 2), "neg": Q(-1)}[tag]
            self.rows[target] = {c: factor * x for c, x in self.rows[target].items()}
            self.norms[target] *= abs(factor)
        self.prefix = max(self.prefix, self.norms[target])


def macro_count(op):
    if op[0] in ("clear", "copy"):
        return 1
    if op[0] == "add":
        return preparation_cost(coefficient(op)) + 2
    require(op[0] == "scale", "unknown macro count")
    q = Q(op[2], op[3])
    k = exponent(abs(q))
    require(k is not None, "invalid scale count")
    return abs(k) + int(q < 0)


def recount(events, blocks):
    original = sum(macro_count(e[1]) for e in events if e[0] == "scalar")
    replacement = original
    for block in blocks:
        old = sum(macro_count(e[1]) for e in events[block["start"]:block["stop"]])
        new = len(lower_block(events, block))
        require(new < old, "nonprofitable selected block")
        replacement += new - old
    return 2 * original, 2 * replacement


def replay(events, native, blocks, orientation):
    machine, index, primitives = Machine(), 0, 0
    selected = {b["start"]: b for b in blocks}
    require(len(selected) == len(blocks), "duplicate blocks")
    previous_stop = 0
    for block in blocks:
        require(block["start"] >= previous_stop, "overlapping/unsorted blocks")
        previous_stop = block["stop"]
    paid, non_scalar = Counter(), []
    while index < len(events):
        event = events[index]
        if index in selected:
            block = selected[index]
            require(not machine.rows[WORK], "coefficient work dirty on block entry")
            for e in events[index:block["stop"]]:
                require(all(native["final"][register(r)] == 1 for r in e[1][1:3]),
                        "block touches a non-full terminal frame")
            ops = lower_block(events, block)
            index = block["stop"]
        else:
            ops = lower_macro(event[1]) if event[0] == "scalar" else []
            if event[0] == "scalar":
                require(len(ops) == macro_count(event[1]), "macro count mismatch")
            else:
                non_scalar.append(event)
                if event[0] == "climb":
                    paid[event[5]] += 1
                elif event[0] == "center":
                    paid[event[4]] += 1
                if event[0] in ("climb", "center", "adapter", "residual_adapter"):
                    require(not machine.rows[WORK], "work crossed an interface")
            index += 1
        for op in ops:
            machine.execute(op)
        primitives += len(ops)
    for r in range(716):
        expected = {r: Q(1)}
        if orientation == "forward" and 112 <= r < 224:
            expected[r - 112] = Q(1)
        elif orientation == "backward" and r < 112:
            expected[r + 112] = Q(-1)
        require(machine.rows[r] == expected, f"full endpoint mismatch: {orientation}/{r}")
    require(all(not machine.rows[r] for r in range(716, 725)), "private inputs survived")
    require(dict(paid) == {int(k): v for k, v in native["local_profile"].items()},
            "paid recursive children changed")
    require(machine.prefix < 2**192, "inherited prefix allowance exceeded")
    return {"columns": 725, "live_columns": 716, "arbitrary_private_columns": 9,
            "real_primitives": 2 * primitives, "prefix_l1": str(machine.prefix),
            "paid_profile": {str(k): v for k, v in sorted(paid.items())},
            "non_scalar_events_sha256": digest(non_scalar)}


def census(events):
    phase, previous = None, None
    counts, pairs = Counter(), Counter()
    for event in events:
        if event[0] == "phase":
            phase = event[1]
        current = eligible(event, phase)
        if previous and current and current[0] == previous[0]:
            a, b = previous[1], current[1]
            pairs[(a, b)] += 1
            counts["adjacent_pairs"] += 1
            if exponent(b / a) is None:
                counts["different_odd_numerator_pairs"] += 1
        previous = current
    result = []
    for (a, b), occurrences in sorted(pairs.items()):
        result.append({"from": str(a), "to": str(b), "occurrences": occurrences,
                       "one_read_routes": [list(r) for r in one_read_routes(a, b)]})
    return dict(counts), result


def rejects(call, name):
    try:
        call()
    except (ValueError, KeyError):
        return name
    raise ValueError("negative control accepted: " + name)


def negative_controls():
    events = [["phase", "full_frame_cleanup"],
              ["scalar", ["add", ["L", 1], ["L", 0], 1, 2], 1],
              ["scalar", ["add", ["L", 2], ["L", 0], -3, 2], 1]]
    block = plan(events, True)[0]
    good = lower_block(events, block)
    registers = [0, 1, 2, WORK]
    reference = Machine(registers)
    for event in events[1:]:
        for op in lower_macro(event[1]):
            reference.execute(op)

    def check(ops):
        actual = Machine(registers)
        for op in ops:
            actual.execute(op)
        require(actual.rows == reference.rows, "control endpoint/clearing failure")
        require(actual.prefix <= reference.prefix, "control prefix failure")

    check(good)
    controls = [rejects(lambda: check(good[1:]), "missing_initial_clear"),
                rejects(lambda: check(good[:-1]), "missing_final_clear")]
    wrong_sign = copy.deepcopy(good)
    wrong_sign[-2][0] = "add"
    controls.append(rejects(lambda: check(wrong_sign), "wrong_target_sign"))
    wrong_read = copy.deepcopy(good)
    j = next(j for j, op in enumerate(wrong_read) if j > 2 and op == ["add", WORK, 0])
    wrong_read[j][2] = 1
    controls.append(rejects(lambda: check(wrong_read), "wrong_transition_source"))
    excursion = good[:-1] + [["double", WORK]] * 8 + [["halve", WORK]] * 8 + good[-1:]
    controls.append(rejects(lambda: check(excursion), "endpoint_neutral_prefix_excursion"))
    for name, mutate in (
        ("source_alias", lambda e: e[2][1].__setitem__(1, ["L", 0])),
        ("changed_source", lambda e: e[2][1].__setitem__(2, ["L", 1])),
        ("frame_crossing", lambda e: e[2].__setitem__(2, 0)),
        ("phase_crossing", lambda e: e.__setitem__(2, ["phase", "done"])),
    ):
        bad = copy.deepcopy(events)
        mutate(bad)
        controls.append(rejects(lambda e=bad: lower_block(e, block), name))
    bad_route = copy.deepcopy(block)
    bad_route["routes"] = [["read", 1, 0]]
    controls.append(rejects(lambda: lower_block(events, bad_route), "wrong_shift_equation"))
    # Correct endpoint, but this route's middle coefficient exceeds numerator 1.
    require(not one_read_routes(Q(1, 2), Q(1, 8)), "unsafe fixture unexpectedly legal")
    controls.append("prefix_route_exclusion")
    boundary = events[:2] + [["phase", "done"]] + events[2:]
    require(plan(boundary, True) == [], "planner crossed phase boundary")
    controls.append("planner_phase_boundary")
    return controls


def build():
    programs, native, spec = load_inputs()
    certificate = {"schema": "jp8-positive-one-read/1", "assignment_seed": 31,
                   "base_commit": BASE, "exponent_limit": LIMIT, "orientations": {}}
    receipt = {"schema": "jp8-positive-one-read-replay/1", "base_commit": BASE,
               "negative_controls": negative_controls(), "orientations": {}}
    for orientation in ("forward", "backward"):
        events = programs[orientation]
        blocks = plan(events, True)
        pure = plan(events, False)
        original, candidate_count = recount(events, blocks)
        _, pure_count = recount(events, pure)
        counts, pairs = census(events)
        cert_blocks = []
        for block in blocks:
            item = dict(block)
            item["primitive_sha256"] = digest(lower_block(events, block))
            cert_blocks.append(item)
        certificate["orientations"][orientation] = {
            "census": counts, "distinct_pairs": pairs, "blocks": cert_blocks}
        actual = replay(events, native, blocks, orientation)
        contract = spec["complete_contract"]["local"][orientation]
        require(original == contract["real_component_primitives"], "original count binding")
        require(actual["real_primitives"] == candidate_count, "literal primitive count mismatch")
        require(actual["prefix_l1"] == contract["prefix_l1"], "global prefix changed")
        actual.update({"original_real_primitives": original,
                       "power_only_real_primitives": pure_count,
                       "additional_real_saved": pure_count - candidate_count,
                       "one_read_transitions": sum(r[0] == "read" for b in blocks
                                                   for r in b["routes"]),
                       "blocks": len(blocks)})
        receipt["orientations"][orientation] = actual
        print(f"PASS_LITERAL_{orientation.upper()} columns=725 primitives={candidate_count}",
              flush=True)
    receipt["certificate_sha256"] = digest(certificate)
    contract = spec["complete_contract"]
    proposed_max = max(r["real_primitives"] for r in receipt["orientations"].values())
    optimistic_bound = proposed_max + contract["local_adapters"] * contract["compiler"]
    require(optimistic_bound == contract["local_primitive_bound"],
            "unexpected local-invoice change")
    receipt["unintegrated_budget"] = {
        "unchanged_local_adapters": contract["local_adapters"],
        "unchanged_compiler_charge": contract["compiler"],
        "max_orientation_primitives": proposed_max,
        "binding_orientation": "backward",
        "original_local_primitive_bound": contract["local_primitive_bound"],
        "optimistic_local_primitive_bound": optimistic_bound,
        "new_kappa_claimed": False,
    }
    return certificate, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="explicit output directory for new artifacts")
    args = parser.parse_args()
    certificate, receipt = build()
    for filename, obj in (("CERTIFICATE.json", certificate), ("EXPECTED.json", receipt)):
        if args.write:
            args.write.mkdir(parents=True, exist_ok=True)
            path = args.write / filename
            require(not path.exists(), "refusing to replace existing artifact: " + str(path))
            path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
        else:
            require(obj == json.loads((HERE / filename).read_text()), filename + " mismatch")
    f = receipt["orientations"]["forward"]
    print(f"PASS_JP8_ADDITIVE_ROUTES extra_saved={f['additional_real_saved']} "
          f"total_saved={f['original_real_primitives'] - f['real_primitives']} "
          f"columns=725 orientations=2 controls={len(receipt['negative_controls'])}")


if __name__ == "__main__":
    main()
