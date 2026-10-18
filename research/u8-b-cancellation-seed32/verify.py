#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reproduce the finite PR1115 shear rewrite from committed, immutable inputs.

Prepared for Martin Rv with OpenAI Codex assistance. Scalar lowering and the
binary-Horner invoice follow the attributed complex-sw4-frame8 local emitter;
the sparse rational checker below imports no construction code.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REWRITE_INDICES = (176, 194, 204, 278)
WORD_MEMBER = "native/local/CANONICAL-WORD.json.gz"
CHECKS_MEMBER = "native/local/LOCAL-CHECKS.json"
PROGRAMS_MEMBER = "native/local/LOCAL-PROGRAMS.json.gz"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_inputs():
    pins = json.loads((HERE / "SOURCES.json").read_bytes())
    require(pins.get("schema") == "u8-b-shear-immutable-inputs-v1", "unsupported source schema")
    require(set(pins["members"]) == {WORD_MEMBER, CHECKS_MEMBER, PROGRAMS_MEMBER},
            "immutable input inventory differs")
    archive_path = (ROOT / pins["archive"]["path"]).resolve()
    require(archive_path.is_relative_to(ROOT.resolve()), "archive path escapes repository")
    require(sha256(archive_path.read_bytes()).hexdigest() == pins["archive"]["sha256"],
            "archive pin differs")
    payloads = {}
    # Read only the three pinned regular members; never extract or execute members.
    with tarfile.open(archive_path, "r:gz") as archive:
        for name, expected in pins["members"].items():
            matches = [member for member in archive.getmembers() if member.name == name]
            require(len(matches) == 1, "missing or duplicate input member: " + name)
            member = matches[0]
            require(member.isfile() and 0 <= member.size <= 16 * 1024 * 1024,
                    "invalid input member: " + name)
            stream = archive.extractfile(member)
            require(stream is not None, "unreadable input member: " + name)
            payloads[name] = stream.read()
            require(sha256(payloads[name]).hexdigest() == expected, "member pin differs: " + name)
    word = json.loads(gzip.decompress(payloads[WORD_MEMBER]))
    checks = json.loads(payloads[CHECKS_MEMBER])
    programs = json.loads(gzip.decompress(payloads[PROGRAMS_MEMBER]))
    return pins, word, checks, programs


def shear_replacement(triple):
    require(len(triple) == 3 and all(event[0] == "add" for event in triple),
            "rewrite requires three adjacent additions")
    first, middle, last = triple
    x, source, target = first[1], first[2], middle[1]
    require(len({x, source, target}) == 3 and middle[2] == x,
            "rewrite register dependency differs")
    require(last[1:3] == first[1:3] and first[-1] == middle[-1] == last[-1],
            "rewrite register or common frame differs")
    a, q = Fraction(first[3], first[4]), Fraction(middle[3], middle[4])
    require(a != 0 and q != 0 and Fraction(last[3], last[4]) == -a,
            "rewrite inverse coefficient differs")
    cross = a * q
    return [list(middle), ["add", target, source, cross.numerator, cross.denominator, first[-1]]]


def rewritten_word(word):
    candidate = copy.deepcopy(word)
    for index in reversed(REWRITE_INDICES):
        candidate["B"][index:index + 3] = shear_replacement(word["B"][index:index + 3])
    return candidate


def apply_scalar(rows, operation):
    tag, target = operation[:2]
    if tag == "clear":
        rows[target] = {}
    elif tag == "copy":
        rows[target] = dict(rows[operation[2]])
    elif tag == "scale":
        q = Fraction(operation[2], operation[3])
        rows[target] = {column: q * value for column, value in rows[target].items() if q * value}
    else:
        require(tag == "add", "unknown scalar operation: " + tag)
        source, numerator, denominator = operation[2:5]
        require(source != target, "self addition is outside the scalar interface")
        q = Fraction(numerator, denominator)
        row = rows.setdefault(target, {})
        for column, value in list(rows[source].items()):
            updated = row.get(column, Fraction(0)) + q * value
            if updated:
                row[column] = updated
            else:
                row.pop(column, None)


def stage_matrix(events, columns, backward=False):
    rows = {register: {register: Fraction(1)} for register in range(columns)}
    for event in events:
        event = list(event)
        if backward:
            if event[0] == "add":
                event[1], event[2], event[3] = event[2], event[1], -event[3]
            else:
                event[2], event[3] = event[3], event[2]
        apply_scalar(rows, event[:-1])
    return rows


def contains(smaller, larger):
    for vector in smaller:
        for pivot in larger:
            if vector >> (pivot.bit_length() - 1) & 1:
                vector ^= pivot
        if vector:
            return False
    return True


def lowered(event, backward):
    event = list(event)
    if event[0] == "add":
        target, source, numerator, denominator = event[1:5]
        if backward:
            target, source, numerator = source, target, -numerator
        return ["add", ["L", target], ["L", source], numerator, denominator]
    require(event[0] == "scale", "unsupported word operation")
    numerator, denominator = event[2:4]
    if backward:
        numerator, denominator = denominator, numerator
    return ["scale", ["L", event[1]], numerator, denominator]


def emit_program(word, backward):
    """Lower the frozen scalar word using the retained frame/center convention."""
    frames, current = word["frames"], list(word["start"])
    v, columns = word["v"], 2 * word["v"] + word["R"]
    entering = {r for r in range(2 * v, columns) if word["start"][r] != 0}
    ended = {r for r in range(2 * v, columns) if word["final"][r] != 1}
    wrapped = entering | ended
    events = [["phase", "zero_frame_precondition"]]

    def scalar(operation, frame):
        events.append(["scalar", operation, frame])

    def climb(register, frame, phase):
        old = current[register]
        if old == frame:
            return
        require(contains(frames[old], frames[frame]), "non-nested frame climb")
        rank = len(frames[frame]) - len(frames[old])
        require(rank > 0, "non-positive frame climb")
        events.append(["climb", phase, register, old, frame, rank])
        current[register] = frame

    for event in word["precondition"] + word["compensation"]:
        registers = event[1:3] if event[0] == "add" else event[1:2]
        require(all(word["start"][r] == 0 for r in registers), "nonzero precondition frame")
        scalar(lowered(event, backward), 0)
    events.append(["phase", "entry_adapters"])
    for register, frame in enumerate(word["start"]):
        if register in wrapped:
            events.append(["residual_adapter", "pre", register, frame] +
                          ([word["final"][register]] if register in ended else []))
        else:
            events.append(["adapter", "old_to_new", register, frame])
    phases = ["A", "centers", "B"] + (["cleanup_tail"] if word.get("tail") else []) + ["final"]
    for phase in phases:
        events.append(["phase", phase])
        if phase in ("A", "B", "cleanup_tail"):
            for event in word["tail"] if phase == "cleanup_tail" else word[phase]:
                registers = event[1:3] if event[0] == "add" else event[1:2]
                for register in registers:
                    climb(register, event[-1], phase)
                scalar(lowered(event, backward), event[-1])
        elif phase == "centers":
            def level(register):
                return word.get("target_levels", {}).get(str(register - v), 0)
            require(all(current[r] == level(r) for r in range(v, 2 * v)), "center target frame differs")
            for k, register in enumerate(word["centers"]):
                frame = word["center_frames"][k]
                require(current[register] == frame, "center source frame differs")
                terms = [event for event in word["cut"] if event[2] == register]
                path = [frame] + sorted({level(event[1]) for event in terms} - {frame},
                                        key=lambda item: -len(frames[item]))
                private = ["C", k]
                if not backward:
                    scalar(["clear", private], frame)
                    scalar(["copy", private, ["L", register]], frame)
                    for step in range(len(path)):
                        if step:
                            events.append(["center", k, path[step - 1], path[step],
                                           len(frames[path[step - 1]]) - len(frames[path[step]])])
                        for event in terms:
                            if level(event[1]) == path[step]:
                                scalar(["add", ["L", event[1]], private, event[3], event[4]], path[step])
                    scalar(["clear", private], path[-1])
                else:
                    scalar(["clear", private], path[-1])
                    for step in reversed(range(len(path))):
                        for event in terms:
                            if level(event[1]) == path[step]:
                                scalar(["add", private, ["L", event[1]], event[3], event[4]], path[step])
                        if step:
                            events.append(["center", k, path[step], path[step - 1],
                                           len(frames[path[step - 1]]) - len(frames[path[step]])])
                    scalar(["add", ["L", register], private, -1, 1], frame)
                    scalar(["clear", private], frame)
        else:
            for register, frame in enumerate(word["final"]):
                climb(register, frame, phase)
    events.append(["phase", "exit_adapters"])
    for register, frame in enumerate(word["final"]):
        if register not in ended:
            events.append(["adapter", "new_to_old", register, frame])
    events.append(["phase", "full_frame_cleanup"])
    for event in word["cleanup"]:
        registers = event[1:3] if event[0] == "add" else event[1:2]
        require(all(word["final"][r] == 1 for r in registers), "cleanup frame differs")
        scalar(lowered(event, backward), 1)
    for register in sorted(wrapped):
        events.append(["residual_adapter", "post", register, word["start"][register]] +
                      ([word["final"][register]] if register in ended else []))
    events.append(["phase", "done"])
    return events


def primitive_bound(operation):
    if operation[0] in ("clear", "copy"):
        return 1
    q = Fraction(*operation[3:5]) if operation[0] == "add" else Fraction(*operation[2:4])
    numerator, denominator = abs(q.numerator), q.denominator
    require(numerator > 0 and denominator & (denominator - 1) == 0, "non-dyadic scalar")
    if operation[0] == "scale":
        require(numerator & (numerator - 1) == 0, "non-binary scale")
        return abs(numerator.bit_length() - denominator.bit_length()) + int(q < 0)
    return 3 + numerator.bit_length() - 1 + numerator.bit_count() + denominator.bit_length() - 1


def replay_program(events, word, backward):
    columns, v = 2 * word["v"] + word["R"], word["v"]
    rows = {("L", r): {r: Fraction(1)} for r in range(columns)}
    paid, macros, primitives = Counter(), 0, 0
    for event in events:
        if event[0] == "climb":
            paid[event[5]] += 1
        elif event[0] == "center":
            paid[event[4]] += 1
        elif event[0] == "scalar":
            operation = copy.deepcopy(event[1])
            macros += 1
            primitives += 2 * primitive_bound(operation)
            operation[1] = tuple(operation[1])
            if operation[0] in ("add", "copy"):
                operation[2] = tuple(operation[2])
            apply_scalar(rows, operation)
    require(all(not row for register, row in rows.items() if register[0] == "C"), "private centers not cleared")
    for register in range(columns):
        expected = {register: Fraction(1)}
        if backward and register < v:
            expected[v + register] = Fraction(-1)
        elif not backward and v <= register < 2 * v:
            expected[register - v] = Fraction(1)
        require(rows["L", register] == expected, "complete local map differs at register " + str(register))
    profile = {str(rank): count for rank, count in sorted(paid.items())}
    require(profile == word["local_profile"], "paid rank profile differs")
    return {"sha256": sha256(canonical(events)).hexdigest(), "events": len(events),
            "scalar_macros": macros, "real_component_primitive_bound": primitives,
            "paid_profile": profile, "all_columns": columns, "private_centers_cleared": True,
            "private_coefficient_stream_cleared_after_each_macro": True}


def verify():
    pins, word, baseline_checks, baseline_programs = load_inputs()
    columns = 2 * word["v"] + word["R"]
    candidate = rewritten_word(word)
    baseline_matrix = stage_matrix(word["B"], columns)
    require(stage_matrix(candidate["B"], columns) == baseline_matrix, "complete B-stage map differs")
    require(stage_matrix(candidate["B"], columns, True) == stage_matrix(word["B"], columns, True),
            "inverse-transpose B-stage map differs")
    for index in REWRITE_INDICES:
        triple = word["B"][index:index + 3]
        require(stage_matrix(triple, columns) == stage_matrix(shear_replacement(triple), columns),
                "local three-register identity differs")
    controls = []
    for k, index in enumerate(REWRITE_INDICES):
        dropped = copy.deepcopy(word["B"])
        dropped.pop(index)
        require(stage_matrix(dropped, columns) != baseline_matrix, "single-deletion control accepted")
        controls.append("drop_first_" + str(k))
    for k, index in enumerate(REWRITE_INDICES):
        wrong = copy.deepcopy(candidate["B"])
        cross = wrong[index - k + 1]
        cross[3] = -cross[3]
        require(stage_matrix(wrong, columns) != baseline_matrix, "wrong-cross-term control accepted")
        controls.append("wrong_cross_term_" + str(k))
    triple = word["B"][REWRITE_INDICES[0]:REWRITE_INDICES[0] + 3]
    touch = ["scale", triple[0][1], 2, 1, triple[0][-1]]
    require(stage_matrix([triple[0], touch, triple[1], triple[2]], columns) !=
            stage_matrix([touch] + shear_replacement(triple), columns), "dependency-touch control accepted")
    controls.append("intervening_target_write")
    original, changed = {}, {}
    for name, backward in (("forward", False), ("backward", True)):
        events = emit_program(word, backward)
        require(events == baseline_programs[name], "baseline emitted program differs: " + name)
        original[name] = replay_program(events, word, backward)
        require(original[name] == baseline_checks[name], "baseline receipt differs: " + name)
        changed[name] = replay_program(emit_program(candidate, backward), candidate, backward)
        require(original[name]["scalar_macros"] - changed[name]["scalar_macros"] == len(REWRITE_INDICES),
                "scalar macro saving differs")
    savings = [original[name]["real_component_primitive_bound"] - changed[name]["real_component_primitive_bound"]
               for name in ("forward", "backward")]
    require(savings[0] == savings[1] and savings[0] > 0, "orientation primitive savings differ")
    result = {
        "all_exact_columns": columns, "archive_sha256": pins["archive"]["sha256"], "assignment_seed": 32,
        "b_events": [len(word["B"]), len(candidate["B"])],
        "backward_real_component_primitives": [original["backward"]["real_component_primitive_bound"],
                                                changed["backward"]["real_component_primitive_bound"]],
        "base_commit": pins["base_commit"], "canonical_word_sha256": pins["members"][WORD_MEMBER],
        "controls_rejected": controls,
        "forward_real_component_primitives": [original["forward"]["real_component_primitive_bound"],
                                               changed["forward"]["real_component_primitive_bound"]],
        "new_kappa": False, "paid_profile_unchanged": changed["forward"]["paid_profile"],
        "real_component_primitives_saved_each_orientation": savings[0], "rewrite_count": len(REWRITE_INDICES),
        "scalar_macros_saved_each_orientation": len(word["B"]) - len(candidate["B"]),
        "scope": "Exact finite B-stage identity and unchanged-emitter local admission; global hosting, outer pricing, all-size/compiler, precision/tape and analytic transfer are not rebuilt.",
        "status": "PASS_U8_B_SHEAR_REWRITE_SEED32", "track": "complex supplier"
    }
    return result, candidate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    parser.add_argument("--write-candidate", type=Path, help="write the verified candidate canonical word for local validation")
    args = parser.parse_args()
    result, candidate = verify()
    receipt = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    require(receipt == (HERE / "RESULT.json").read_bytes(), "committed deterministic result differs")
    if args.write_result:
        args.write_result.write_bytes(receipt)
    if args.write_candidate:
        args.write_candidate.write_bytes(gzip.compress(canonical(candidate), mtime=0))
    forward, backward = result["forward_real_component_primitives"], result["backward_real_component_primitives"]
    print(f'{result["status"]} rewrites={result["rewrite_count"]} B={result["b_events"][0]}->{result["b_events"][1]} '
          f'primitives={forward[0]}->{forward[1]}/{backward[0]}->{backward[1]} '
          f'columns={result["all_exact_columns"]} controls={len(result["controls_rejected"])} no_new_kappa')


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, tarfile.TarError) as error:
        raise SystemExit("FAIL_U8_B_SHEAR_REWRITE_SEED32: " + str(error)) from error
