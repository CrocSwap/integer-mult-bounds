"""Replay the scoped JP8 coefficient-rescaling witness, offline and read-only."""

import gzip
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from itertools import pairwise
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from lowering import (
    WORK,
    block_data,
    coefficient,
    lower_block,
    lower_macro,
    plans,
    power_exponent,
    prepare_cost,
    require,
)

PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/"
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_inputs():
    pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
    data = {}
    for path, expected in pins["files"].items():
        payload = (ROOT / path).read_bytes()
        if path.endswith(".gz"):
            payload = gzip.decompress(payload)
        require(hashlib.sha256(payload).hexdigest() == expected["payload_sha256"],
                "source payload changed: " + path)
        if path.endswith((".json", ".json.gz")):
            data[path] = json.loads(payload)
    native = data[PROVIDER + "CANONICAL-WORD.json.gz"]
    programs = data[PROVIDER + "LOCAL-PROGRAMS.json.gz"]
    spec = data[SPEC]["providers"]["jp8"]
    for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
        require(digest(data[PROVIDER + name]) == spec["artifact_semantic_sha256"][name],
                "selected SPEC artifact binding failed: " + name)
    for orientation, events in programs.items():
        require(digest(events) == spec["program_hashes"][orientation], "selected program binding failed")
    require(native["v"] == 112 and native["R"] == 492 and native["h"] == 9,
            "unexpected supplier dimensions")
    return native, programs, spec


class Machine:
    """Sparse exact linear forms and a separate positive prefix envelope."""

    def __init__(self, registers):
        self.rows = {r: {i: Q(1)} for i, r in enumerate(registers)}
        self.norms = {r: Q(1) for r in registers}
        self.prefix = Q(1)

    def update(self, target, source, scalar):
        require(target != source, "interpreter received aliased addition")
        row = self.rows.setdefault(target, {})
        for col, value in self.rows[source].items():
            new = row.get(col, Q(0)) + scalar * value
            if new:
                row[col] = new
            else:
                row.pop(col, None)
        self.norms[target] = self.norms.get(target, Q(0)) + abs(scalar) * self.norms[source]

    def primitive(self, op):
        tag, target = op[:2]
        if tag == "clear":
            self.rows[target], self.norms[target] = {}, Q(0)
        elif tag == "copy":
            self.rows[target], self.norms[target] = dict(self.rows[op[2]]), self.norms[op[2]]
        elif tag == "inc":
            require(op[3] in (-1, 1), "non-unit primitive addition")
            self.update(target, op[2], op[3])
        else:
            require(tag in ("double", "halve", "neg"), "unknown primitive")
            scalar = {"double": Q(2), "halve": Q(1, 2), "neg": Q(-1)}[tag]
            self.rows[target] = {j: scalar * x for j, x in self.rows[target].items()}
            self.norms[target] *= abs(scalar)
        self.prefix = max(self.prefix, self.norms[target])

    def macro(self, op):
        tag, target = op[0], tuple(op[1])
        if tag == "add":
            source, q = tuple(op[2]), coefficient(op)
            self.prefix = max(self.prefix, abs(q.numerator) * self.norms[source])
            self.update(target, source, q)
            self.rows[WORK], self.norms[WORK] = {}, Q(0)
        elif tag == "scale":
            q = Q(op[2], op[3])
            require(power_exponent(abs(q)) is not None, "invalid scale")
            self.rows[target] = {j: q * x for j, x in self.rows[target].items()}
            self.norms[target] *= abs(q)
        elif tag in ("clear", "copy"):
            self.primitive((tag, target, tuple(op[2])) if tag == "copy" else (tag, target))
        else:
            raise ValueError("unknown macro")
        self.prefix = max(self.prefix, self.norms[target])


def macro_cost(op):
    if op[0] in ("clear", "copy"):
        return 1
    if op[0] == "add":
        return prepare_cost(coefficient(op)) + 2
    q = Q(op[2], op[3])
    exponent = power_exponent(abs(q))
    require(exponent is not None, "invalid scale cost")
    return abs(exponent) + int(q < 0)


def check_macro_library(programs):
    """Certify every unchanged arithmetic macro type on independent local inputs."""
    cases = set()
    for events in programs.values():
        for event in events:
            if event[0] != "scalar":
                continue
            op = event[1]
            if op[0] == "add":
                cases.add(("add", coefficient(op)))
            elif op[0] == "scale":
                cases.add(("scale", Q(op[2], op[3])))
    target, source = ("L", 0), ("L", 1)
    for tag, q in sorted(cases):
        op = ([tag, list(target), list(source), q.numerator, q.denominator]
              if tag == "add" else [tag, list(target), q.numerator, q.denominator])
        actual, reference = Machine([target, source, WORK]), Machine([target, source, WORK])
        primitives = lower_macro(op)
        for primitive in primitives:
            actual.primitive(primitive)
        reference.macro(op)
        require(actual.rows == reference.rows, "macro library endpoint mismatch")
        require(actual.prefix == reference.prefix, "macro library prefix mismatch")
        require(len(primitives) == macro_cost(op), "macro library cost mismatch")
    return len(cases)


def replay(events, native, spans, orientation):
    require(orientation in ("forward", "backward"), "unknown orientation")
    n = 2 * native["v"] + native["R"]
    machine = Machine([("L", r) for r in range(n)] + [WORK])
    selected = dict(spans)
    require(len(selected) == len(spans), "duplicate block starts")
    paid, cost, index, phase = Counter(), 0, 0, None
    blocks = []
    while index < len(events):
        event = events[index]
        if event[0] == "phase":
            phase = event[1]
        if index in selected:
            stop = selected[index]
            block = events[index:stop]
            require(phase == "full_frame_cleanup", "block outside cleanup")
            source, magnitudes = block_data(block)
            registers = {source} | {tuple(e[1][1]) for e in block}
            require(all(native["final"][r[1]] == 1 for r in registers), "block touches early-ended register")
            require(not machine.rows[WORK], "work not clear on block entry")
            reference_rows = {r: dict(machine.rows[r]) for r in registers}
            reference = Machine([])
            reference.rows = reference_rows
            reference.norms = {r: machine.norms[r] for r in registers}
            reference.prefix = machine.prefix
            for old_event in block:
                reference.macro(old_event[1])
            primitives = lower_block(block)
            for primitive in primitives:
                machine.primitive(primitive)
            require(all(machine.rows[r] == reference.rows[r] for r in registers | {WORK}),
                    "block changed live-register boundary or left private work")
            require(all(machine.norms[r] == reference.norms[r] for r in registers),
                    "block changed live positive envelope")
            require(machine.prefix <= reference.prefix, "block exceeded original prefix envelope")
            old_cost = sum(macro_cost(e[1]) for e in block)
            require(len(primitives) < old_cost, "unprofitable block")
            distinct = sum(a != b for a, b in pairwise(magnitudes))
            blocks.append({"start": index, "stop": stop, "source": source[1],
                           "distinct_transitions": distinct,
                           "real_primitives_before": 2 * old_cost,
                           "real_primitives_after": 2 * len(primitives),
                           "primitive_sha256": digest(primitives)})
            cost += len(primitives)
            index = stop
            continue
        if event[0] == "scalar":
            machine.macro(event[1])
            cost += macro_cost(event[1])
        elif event[0] == "climb":
            paid[event[5]] += 1
        elif event[0] == "center":
            paid[event[4]] += 1
        index += 1
    v = native["v"]
    for r in range(n):
        expected = {r: Q(1)}
        if orientation == "forward" and v <= r < 2 * v:
            expected[r - v] = Q(1)
        if orientation == "backward" and r < v:
            expected[v + r] = Q(-1)
        require(machine.rows[("L", r)] == expected, "full scalar projection endpoint mismatch")
    require(all(not row for reg, row in machine.rows.items() if reg[0] != "L"),
            "private register not erased")
    require(machine.prefix < 2**192, "192-bit local prefix allowance exceeded")
    require(dict(paid) == {int(r): k for r, k in native["local_profile"].items()},
            "paid recursive profile changed")
    return {"orientation": orientation, "all_live_columns": n, "arbitrary_work_input": True,
            "real_component_primitives": 2 * cost, "prefix_l1_upper": str(machine.prefix),
            "paid_profile": {str(r): count for r, count in sorted(paid.items())}, "blocks": blocks}


def reject(call, name):
    try:
        call()
    except (ValueError, KeyError):
        return name
    raise ValueError("negative control accepted: " + name)


def negative_controls():
    def event(t, s, p, q=1, frame=1):
        return ["scalar", ["add", ["L", t], ["L", s], p, q], frame]

    block = [event(1, 0, 3, 2), event(2, 0, -3, 1)]
    good = lower_block(block)
    registers = [("L", i) for i in range(3)] + [WORK]
    baseline = Machine(registers)
    for e in block:
        baseline.macro(e[1])

    def endpoint(ops):
        machine = Machine(registers)
        for op in ops:
            machine.primitive(op)
        require(machine.rows == baseline.rows, "control endpoint")
        require(machine.prefix <= baseline.prefix, "control prefix")

    endpoint(good)
    controls = [reject(lambda: endpoint(good[1:]), "omitted_initial_clear"),
                reject(lambda: endpoint(good[:-1]), "omitted_final_clear")]
    bad = list(good)
    i = next(i for i, op in enumerate(bad) if op[0] == "inc" and op[1] == ("L", 2))
    bad[i] = ("inc", ("L", 2), WORK, 1)
    controls.append(reject(lambda: endpoint(bad), "wrong_accumulation_sign"))
    bad = list(good)
    i = len(bad) - 3
    require(bad[i] == ("double", WORK), "bad rescale-control fixture")
    bad[i] = ("halve", WORK)
    controls.append(reject(lambda: endpoint(bad), "inverted_rescale"))
    bad = list(good)
    bad[-1:-1] = [("double", WORK)] * 8 + [("halve", WORK)] * 8
    controls.append(reject(lambda: endpoint(bad), "endpoint_neutral_prefix_excursion"))
    for name, mutated in (
        ("source_alias", [event(0, 0, 3, 2), block[1]]),
        ("changed_source", [block[0], event(2, 1, -3)]),
        ("changed_odd_numerator", [block[0], event(2, 0, -5)]),
        ("wrong_frame", [block[0], event(2, 0, -3, frame=0)]),
    ):
        controls.append(reject(lambda m=mutated: lower_block(m), name))
    losing = [["phase", "full_frame_cleanup"], event(1, 0, 16), event(2, 0, 1, 2)]
    require(plans(losing, "rescale") == [], "unprofitable rescaling selected")
    controls.append("unprofitable_exact_rescaling_cut")
    boundary = [["phase", "full_frame_cleanup"], block[0], ["phase", "done"], block[1]]
    require(plans(boundary, "rescale") == [], "block crossed phase boundary")
    controls.append("phase_boundary_cut")
    return controls


def build_receipt():
    from crosscheck import crosscheck

    native, programs, spec = load_inputs()
    result = {"schema": "complex-coefficient-rescaling/1", "assignment_seed": 39,
              "base_commit": "66849e1475c930fd7732b1a0067ffee7e1e95f60",
              "macro_library_cases": check_macro_library(programs),
              "negative_controls": negative_controls(), "orientations": {}}
    for orientation in ("forward", "backward"):
        events = programs[orientation]
        spans, equal_spans = plans(events, "rescale"), plans(events, "equal")
        original = replay(events, native, [], orientation)
        equal = replay(events, native, equal_spans, orientation)
        rescaled = replay(events, native, spans, orientation)
        original_contract = spec["complete_contract"]["local"][orientation]
        require(original["orientation"] == orientation, "orientation mismatch")
        require(original["real_component_primitives"] == original_contract["real_component_primitives"],
                "original count differs from selected contract")
        require(original["prefix_l1_upper"] == original_contract["prefix_l1"],
                "original prefix differs from selected contract")
        independent = crosscheck(events, spans, lower_block)
        result["orientations"][orientation] = {
            "original_real_primitives": original["real_component_primitives"],
            "equal_magnitude_real_primitives": equal["real_component_primitives"],
            "rescaled_real_primitives": rescaled["real_component_primitives"],
            "incremental_real_saving": equal["real_component_primitives"] - rescaled["real_component_primitives"],
            "equal_magnitude_blocks": len(equal_spans), "rescaled_blocks": len(spans),
            "all_live_columns": rescaled["all_live_columns"], "arbitrary_work_input": True,
            "original_prefix_l1": original["prefix_l1_upper"],
            "equal_prefix_l1": equal["prefix_l1_upper"],
            "rescaled_prefix_l1": rescaled["prefix_l1_upper"],
            "paid_profile": rescaled["paid_profile"],
            "blocks": rescaled["blocks"], "independent": independent,
        }
    return result


def main():
    require(len(sys.argv) == 1, "usage: python3 -I -B research/complex-coefficient-rescaling/verify.py")
    result = build_receipt()
    require(result == json.loads((HERE / "EXPECTED.json").read_text()), "committed receipt mismatch")
    forward = result["orientations"]["forward"]
    print("PASS_JP8_COEFFICIENT_RESCALING"
          f" incremental_real_saved={forward['incremental_real_saving']}"
          f" blocks={forward['rescaled_blocks']} columns=716 orientations=2"
          f" controls={len(result['negative_controls'])}")


if __name__ == "__main__":
    main()
