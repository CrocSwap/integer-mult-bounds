#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact lender-cut and fixed-block commutation audit of PR2530.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
No predecessor code is imported or executed. See README.md for the model.
"""

import argparse
import copy
import gzip
import hashlib
import json
from collections import defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
LENDERS = (49, 83, 98, 101, 68, 80, 88, 31)
# These identify the claimed objects, not expected output rows.
BLOCKS = (
    ("49", (1035,)), ("83", (1039,)), ("98", (1041,)),
    ("101", (1037,)), ("68", (971, 972)),
    ("80-88", (687, 688)), ("31", (973,)),
)


class AuditError(RuntimeError):
    pass


def need(condition, message):
    if not condition:
        raise AuditError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def row_json(row):
    return [[source, list(word), str(value)]
            for (source, word), value in sorted(row.items()) if value]


def add_term(row, key, value):
    value += row.get(key, Q(0))
    if value:
        row[key] = value
    else:
        row.pop(key, None)


def incident(gate):
    return gate[1:3] if gate[0] == "add" else gate[1:2]


def apply(rows, gate):
    """Forward row substitution over Q[free invertible operator symbols]."""
    kind, target = gate[:2]
    need(target in rows, "write to absent input role")
    if kind == "add":
        source, numerator, denominator = gate[2:5]
        need(source in rows and source != target, "invalid ADD source")
        coefficient = Q(numerator, denominator)
        for key, value in tuple(rows[source].items()):
            add_term(rows[target], key, coefficient * value)
    elif kind == "scale":
        coefficient = Q(gate[2], gate[3])
        need(coefficient != 0, "noninvertible scale")
        rows[target] = {key: coefficient * value
                        for key, value in rows[target].items()}
    elif kind == "warp":
        operator = gate[2]
        need(operator != 0, "zero warp symbol")
        result = {}
        for (source, word), value in rows[target].items():
            new_word = (word[1:] if word and word[0] == -operator
                        else (operator,) + word)
            add_term(result, (source, new_word), value)
        rows[target] = result
    else:
        raise AuditError("unknown gate " + str(kind))


def backward_row(program, output):
    """Reverse expression substitution, separate from the forward interpreter.

    A word acts to the left of a register. Back substitution APPENDS a warp;
    forward execution prepends one. This checks the noncommutative convention.
    """
    expression = {(output, ()): Q(1)}
    for gate in reversed(program):
        kind, target = gate[:2]
        affected = [(key, value) for key, value in expression.items()
                    if key[0] == target]
        if kind == "add":
            factor = Q(gate[3], gate[4])
            for (_, word), value in affected:
                key = gate[2], word
                result = expression.get(key, Q(0)) + factor * value
                if result:
                    expression[key] = result
                else:
                    expression.pop(key, None)
        elif kind == "scale":
            factor = Q(gate[2], gate[3])
            for key, value in affected:
                expression[key] = factor * value
        elif kind == "warp":
            operator = gate[2]
            # Remove the whole old slice first: a new word can equal another
            # old key, although right multiplication is itself bijective.
            for key, _ in affected:
                del expression[key]
            for key, value in affected:
                word = key[1]
                word = (word[:-1] if word and word[-1] == -operator
                        else word + (operator,))
                new_key = target, word
                expression[new_key] = expression.get(new_key, Q(0)) + value
        else:
            raise AuditError("unknown reverse gate")
        expression = {key: value for key, value in expression.items() if value}
    return expression


@lru_cache(maxsize=None)
def span(vectors):
    values = {0}
    for vector in vectors:
        need(isinstance(vector, int) and 0 <= vector < 512,
             "frame coordinate outside nine bits")
        values |= {value ^ vector for value in tuple(values)}
    return frozenset(values)


def frame(vectors):
    return span(tuple(vectors))


def mapped(columns, value):
    answer = 0
    for bit in range(9):
        if value & (1 << bit):
            answer ^= columns[bit]
    return answer


def advance_frame(current, gate, word):
    if gate[0] == "warp":
        _, register, operator, old, new = gate
        columns = word["warps"][abs(operator) - 1][2]
        need(len(columns) == 9 and len({mapped(columns, x)
                                     for x in range(512)}) == 512,
             "singular warp map")
        old, new = frame(old), frame(new)
        need(current[register] == old, "warp input frame mismatch")
        left, right = (old, new) if operator > 0 else (new, old)
        need(frozenset(mapped(columns, x) for x in left) == right,
             "warp frame image mismatch")
        current[register] = new
    else:
        destination = frame(gate[-1])
        for register in incident(gate):
            need(current[register] <= destination, "nonmonotone frame")
            current[register] = destination


def timeline(word):
    scheduled = defaultdict(list)
    for operator, record in enumerate(word["warps"], 1):
        cut, lender, _, old, new = record
        need(0 <= cut <= len(word["B"]), "warp outside B")
        scheduled[cut].append((operator, lender, old, new))
    result = []
    for cut in range(len(word["B"]) + 1):
        for operator, lender, old, new in scheduled[cut]:
            result.append((f"B:{cut}:warp:{operator}",
                           ["warp", lender, operator, old, new]))
        if cut < len(word["B"]):
            result.append((f"B:{cut}:gate", word["B"][cut]))
    return result


def prefix(word):
    need(word["initial_corrections"] == [], "scope requires no initial corrections")
    need(word["report"]["v"] == 112 and word["report"]["R"] == 480
         and word["report"]["h"] == 9, "unexpected source geometry")
    return sum((word[section] for section in
                ("precondition", "compensation", "A", "cut")), [])


def check_cuts(word, reverse=True):
    live = set(range(704)) - set(word["removed"])
    need(len(live) == 646 and set(LENDERS) <= live, "live input domain")
    rows = {register: {(register, ()): Q(1)} for register in live}
    program = prefix(word)
    for gate in program:
        apply(rows, gate)
    events = timeline(word)
    last_eight = word["warps"][-8:]
    need(tuple(record[1] for record in last_eight) == LENDERS,
         "changed eight-alias/lender binding")
    recovery_indices = {i for _, indices in BLOCKS for i in indices}
    recoveries, handoffs, context_handoffs = [], [], []
    for label, gate in events:
        if gate[0] == "warp" and gate[1] in (4, 12, 33, 55, 74, 85):
            context_handoffs.append({"event": label, "lender": gate[1],
                                     "row": row_json(rows[gate[1]])})
        if gate[0] == "warp" and gate[2] > len(word["warps"]) - 8:
            lender = gate[1]
            expected = {(lender, ()): Q(1)}
            actual = rows[lender]
            need(actual == expected,
                 f"lender {lender} at {label}: {row_json(actual)}")
            if reverse:
                pulled = backward_row(program, lender)
                need(pulled == actual, "reverse/forward cut discrepancy")
            handoffs.append({"event": label, "lender": lender,
                             "row": row_json(actual),
                             "prefix_events": len(program)})
        if gate[0] != "warp" and int(label.split(":")[1]) in recovery_indices:
            entry = {"event": label, "gate": gate,
                     "inputs": {str(r): row_json(rows[r])
                                for r in incident(gate)}}
            apply(rows, gate)
            entry["output"] = row_json(rows[gate[1]])
            recoveries.append(entry)
        else:
            apply(rows, gate)
        program.append(gate)
    need(len(handoffs) == 8 and len(recoveries) == 9 and len(context_handoffs) == 6,
         "incomplete cut/recovery coverage")
    return {"independent_inputs": len(live), "handoffs": handoffs,
            "recovery_gates": recoveries, "older_partner_handoffs": context_handoffs}


def commutator(block, gate):
    registers = set(incident(gate))
    for item in block:
        registers.update(incident(item))
    first = {r: {(r, ()): Q(1)} for r in registers}
    second = copy.deepcopy(first)
    for item in block + [gate]:
        apply(first, item)
    for item in [gate] + block:
        apply(second, item)
    for register in sorted(registers):
        if first[register] != second[register]:
            return {"output": register, "block_then_event": row_json(first[register]),
                    "event_then_block": row_json(second[register])}
    return None


def cut_label(events, position):
    return {"after": events[position - 1][0] if position else "B-start",
            "before": events[position][0] if position < len(events) else "B-end"}


def movement_windows(word):
    """Maximal component reached by legal adjacent swaps of one fixed block.

    No simultaneous block movement, global retiming or native optimality claim.
    """
    live = set(range(704)) - set(word["removed"])
    current = {r: frame([word["ports"][r]]) if r < 112 else frame([])
               for r in live}
    for register, values in word["start_extra"].items():
        current[int(register)] = frame(values)
    for gate in word["A"]:
        advance_frame(current, gate, word)
    events = timeline(word)
    states = [current.copy()]
    for _, gate in events:
        advance_frame(current, gate, word)
        states.append(current.copy())
    windows = []
    for name, indices in BLOCKS:
        start = next(i for i, item in enumerate(events)
                     if item[0] == f"B:{indices[0]}:gate")
        block_events = events[start:start + len(indices)]
        need([x[0] for x in block_events] == [f"B:{i}:gate" for i in indices],
             "recovery block is not contiguous")
        block = [item[1] for item in block_events]
        required = {}
        for offset, gate in enumerate(block):
            for register in incident(gate):
                value = frame(gate[-1])
                need(register not in required or required[register] == value,
                     "multi-frame recovery block outside scope")
                required[register] = value
            need(states[start + offset] == states[start + offset + 1],
                 "recovery changes a frame; zero-climb model inapplicable")
        skeleton = events[:start] + events[start + len(block):]

        def frame_failures(position):
            old_position = position if position <= start else position + len(block)
            return [{"register": r, "available_span": sorted(states[old_position][r]),
                     "required_span": sorted(value)}
                    for r, value in sorted(required.items())
                    if states[old_position][r] != value]

        def allowed(position):
            return not frame_failures(position)

        need(allowed(start), "original recovery cut lacks its frame")
        left = right = start
        blockers = {}
        for direction in (-1, 1):
            cursor = start
            while 0 <= cursor + direction <= len(skeleton):
                crossed = cursor - 1 if direction < 0 else cursor
                label, gate = skeleton[crossed]
                defect = commutator(block, gate)
                frame_ok = allowed(cursor + direction)
                if defect is not None or not frame_ok:
                    if frame_ok:
                        need(defect is not None and
                             all(not term[1] for side in
                                 ("block_then_event", "event_then_block")
                                 for term in defect[side]),
                             "boundary needs a concrete scalar obstruction")
                    blockers["left" if direction < 0 else "right"] = {
                        "event": label, "gate": gate,
                        "frame_available_beyond": frame_ok,
                        "frame_failures": frame_failures(cursor + direction),
                        "commutator": defect}
                    break
                cursor += direction
            if direction < 0:
                left = cursor
            else:
                right = cursor
        windows.append({"block": name, "original_B_indices": list(indices),
                        "skeleton_cuts_inclusive": [left, right],
                        "placements": right - left + 1,
                        "earliest": cut_label(skeleton, left),
                        "latest": cut_label(skeleton, right),
                        "blockers": blockers})
    return windows


def controls(word):
    rejected = []

    def reject(name, altered):
        try:
            check_cuts(altered, reverse=False)
        except AuditError as error:
            rejected.append({"name": name, "reason": str(error)})
        else:
            raise AuditError("accepted semantic control " + name)

    for _, indices in BLOCKS:
        for index in indices:
            altered = copy.deepcopy(word)
            gate = altered["B"][index]
            # Keep event numbering and frame annotations fixed: turn this
            # operation into an identity, rather than deleting a numbered cut.
            if gate[0] == "add":
                gate[3] = 0
            else:
                gate[2] = gate[3]
            reject(f"identity-recovery-B{index}", altered)
    altered = copy.deepcopy(word)
    altered["B"][687], altered["B"][688] = altered["B"][688], altered["B"][687]
    reject("reversed-80-88-restoration", altered)
    altered = copy.deepcopy(word)
    altered["B"][973][3] *= -1
    reject("wrong-sign-31-restoration", altered)
    altered = copy.deepcopy(word)
    # Borrow 80 immediately before its restoration, without changing its map.
    altered["warps"][-3][0] = 687
    reject("80-handoff-before-recovery", altered)
    need(len(rejected) == 12, "control coverage")

    # Deliberate scope control: target-only prelude corruption is NOT covered
    # by source handoff identities. It must not be advertised as a word audit.
    altered = copy.deepcopy(word)
    target_gate = next(g for g in altered["A"][:altered["prelude_events"]]
                       if g[0] == "add")
    target_gate[3] *= 2
    check_cuts(altered, reverse=False)
    return {"rejected": rejected,
            "accepted_scope_control": "doubled target-prelude ADD is outside lender-cut coverage"}


def algebra_controls():
    # Noncommuting symbols and inverse cancellation; no operator phase premise.
    program = [["warp", 0, 1], ["add", 1, 0, 3, 2, []],
               ["warp", 1, 2], ["warp", 0, -1]]
    rows = {r: {(r, ()): Q(1)} for r in (0, 1)}
    for gate in program:
        apply(rows, gate)
    need(rows[0] == {(0, ()): Q(1)} and
         rows[1] == {(1, (2,)): Q(1), (0, (2, 1)): Q(3, 2)},
         "free-word positive fixture")
    need(backward_row(program, 1) == rows[1], "reverse fixture")
    collision = [["add", 1, 0, 1, 1, []], ["warp", 0, 1],
                 ["add", 1, 0, 1, 1, []], ["warp", 0, 1]]
    rows = {r: {(r, ()): Q(1)} for r in (0, 1)}
    for gate in collision:
        apply(rows, gate)
    need(backward_row(collision, 1) == rows[1], "reverse old/new-key collision fixture")
    need(commutator([["add", 0, 1, 1, 1, []]],
                    ["add", 1, 0, 1, 1, []]) is not None,
         "noncommuting ADD control")
    need(commutator([["add", 0, 1, 1, 1, []]],
                    ["add", 2, 1, 1, 1, []]) is None,
         "shared-read positive control")


def compute():
    algebra_controls()
    inputs = json.loads((HERE / "INPUTS.json").read_text())
    names = [Path(record["path"]).name for record in inputs["sources"]]
    need(len(names) == 2 and set(names) ==
         {"eight-alias-base.json.gz", "eight-alias-extra.json.gz"},
         "exactly two distinct pinned providers required")
    output = {"status": "PASS_T74_SOURCE_PARTNER_CUT_AUDIT", "providers": {}}
    for record in inputs["sources"]:
        path = HERE / "inputs" / Path(record["path"]).name
        data = path.read_bytes()
        need(sha(data) == record["sha256"], "source SHA-256 mismatch")
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        need(blob == record["git_blob"], "source Git blob mismatch")
        word = json.loads(gzip.decompress(data))
        tag = "extra" if "extra" in path.name else "base"
        output["providers"][tag] = {
            "source_sha256": record["sha256"], "cuts": check_cuts(word),
            "movement_windows": movement_windows(word), "controls": controls(word)}
    need(set(output["providers"]) == {"base", "extra"}, "both providers required")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", type=Path,
                        help="write new evidence exclusively; normal replay is read-only")
    args = parser.parse_args()
    output = compute()
    if args.write_certificate:
        with args.write_certificate.open("x") as handle:
            json.dump(output, handle, sort_keys=True, indent=2)
            handle.write("\n")
    else:
        expected = json.loads((HERE / "CERTIFICATE.json").read_text())
        need(output == expected, "certificate differs from reconstructed evidence")
    print(output["status"], "providers=2 handoffs=16 recovery_gates=18 "
          "reverse_cuts=16 movement_windows=14 semantic_rejections=24 no_new_kappa")


if __name__ == "__main__":
    main()
