"""Exact finite scalar checks, costs and positive prefix envelopes. No writes.

Sagar Thakrar with substantial OpenAI Codex assistance. Apache-2.0.
Selected scalar semantics and invoice: retained PR531/558/622/626 lineage.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lowering import WORK, groups, lower, original_cost, require

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/"
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read_sources():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    result = {}
    for name, expected in pins["files"].items():
        raw = (ROOT / name).read_bytes()
        payload = gzip.decompress(raw) if name.endswith(".gz") else raw
        require(digest(payload) == expected["payload_sha256"], "changed source: " + name)
        if name.endswith((".json", ".json.gz")):
            result[name] = json.loads(payload)
    spec = result[SPEC]["providers"]["jp8"]
    word = result[PROVIDER + "CANONICAL-WORD.json.gz"]
    programs = result[PROVIDER + "LOCAL-PROGRAMS.json.gz"]
    for name, value in (("CANONICAL-WORD.json.gz", word),
                        ("LOCAL-PROGRAMS.json.gz", programs)):
        require(digest(canonical(value)) == spec["artifact_semantic_sha256"][name],
                "selected SPEC semantic identity: " + name)
    require(set(programs) == {"forward", "backward"}, "orientation inventory")
    require((word["v"], word["R"], word["h"]) == (112, 492, 9), "native geometry")
    require(len(word["frames"][1]) == word["h"], "cleanup frame must be full")
    for events in programs.values():
        for start, end in groups(events):
            require(all(word["final"][event[1][side][1]] == 1
                        for event in events[start:end] for side in (1, 2)),
                    "batch reads an early-ended register")
    return word, programs, result[PROVIDER + "LOCAL-CHECKS.json"], result[PROVIDER + "INDEPENDENT-LOCAL-REPLAY.json"]


def add_row(target, source, coefficient):
    result = dict(target)
    for column, value in source.items():
        total = result.get(column, Q(0)) + coefficient * value
        if total:
            result[column] = total
        else:
            result.pop(column, None)
    return result


def execute(program, state, envelope):
    """Interpret literal unit primitives independently of the binary recipe."""
    peak = Q(0)
    for op in program:
        tag, target = op[:2]
        if tag == "clear":
            state[target], envelope[target] = {}, Q(0)
        elif tag == "add":
            source, sign = op[2:]
            require(sign in (-1, 1) and source != target, "primitive signed-add contract")
            state[target] = add_row(state[target], state[source], Q(sign))
            envelope[target] += envelope[source]
        elif tag in ("double", "half"):
            factor = Q(2) if tag == "double" else Q(1, 2)
            state[target] = {j: value * factor for j, value in state[target].items()}
            envelope[target] *= factor
        else:
            raise ValueError("unknown primitive")
        peak = max(peak, envelope[target])
    return peak


def macro(op, state, envelope):
    tag, target = op[0], tuple(op[1])
    peak = Q(0)
    if tag == "clear":
        state[target], envelope[target] = {}, Q(0)
    elif tag == "copy":
        source = tuple(op[2])
        state[target], envelope[target] = dict(state[source]), envelope[source]
    elif tag == "scale":
        q = Q(op[2], op[3])
        state[target] = {j: q * value for j, value in state[target].items()}
        envelope[target] *= abs(q)
    elif tag == "add":
        source, q = tuple(op[2]), Q(op[3], op[4])
        require(source != target, "macro alias")
        state[target] = add_row(state[target], state[source], q)
        envelope[target] += abs(q) * envelope[source]
        # Original Horner grows monotonically to |numerator| before halving.
        peak = abs(q.numerator) * envelope[source]
        state[WORK], envelope[WORK] = {}, Q(0)
    else:
        raise ValueError("unknown macro")
    return max(peak, envelope[target])


def block_check(block, program=None):
    """Check all local inputs, including arbitrary incoming private work."""
    registers = sorted({tuple(e[1][1]) for e in block} | {tuple(e[1][2]) for e in block} | {WORK})
    state = {r: {i: Q(1)} for i, r in enumerate(registers)}
    expected = {r: dict(row) for r, row in state.items()}
    env = {r: Q(1) for r in registers}
    old_env = dict(env)
    for event in block:
        macro(event[1], expected, old_env)
    recipe = lower(block) if program is None else program
    peak = execute(recipe, state, env)
    require(state == expected, "wrong block boundary map or private clearing")
    require(env == old_env, "wrong block endpoint envelope")
    require(2 * len(recipe) < sum(original_cost(e[1]) for e in block), "no strict saving")
    return peak


def replay(events, orientation, changed, n):
    # Rows carry every arbitrary live/helper input and incoming centre/work dirt.
    state = {("L", r): {r: Q(1)} for r in range(n)}
    state.update({("C", r): {n + r: Q(1)} for r in range(8)})
    state[WORK] = {n + 8: Q(1)}
    env = {r: Q(1) for r in state}
    peak, scratch_peak, cost, index = Q(1), Q(0), 0, 0
    selected = dict(groups(events)) if changed else {}
    profile = Counter()
    records = []
    while index < len(events):
        if index in selected:
            end = selected[index]
            block = events[index:end]
            recipe = lower(block)
            block_check(block, recipe)
            sources = [tuple(e[1][2]) for e in block]
            q = abs(Q(block[0][1][3], block[0][1][4]))
            total = sum((env[r] for r in sources), Q(0))
            work_bound = total * max(Q(1), Q(2 ** (q.numerator.bit_length() - 1), q.denominator))
            scratch_peak = max(scratch_peak, work_bound)
            peak = max(peak, execute(recipe, state, env))
            baseline = sum(original_cost(e[1]) for e in block)
            cost += 2 * len(recipe)
            records.append([index, end, list(block[0][1][1]), str(q), baseline, 2 * len(recipe)])
            index = end
            continue
        event = events[index]
        if event[0] == "scalar":
            cost += original_cost(event[1])
            peak = max(peak, macro(event[1], state, env))
        elif event[0] == "climb":
            profile[event[5]] += 1
        elif event[0] == "center":
            profile[event[4]] += 1
        else:
            require(event[0] in ("phase", "adapter", "residual_adapter"), "event tag")
        index += 1
    for r in range(n):
        expected = {r: Q(1)}
        if orientation == "backward" and r < 112:
            expected[112 + r] = Q(-1)
        elif orientation == "forward" and 112 <= r < 224:
            expected[r - 112] = Q(1)
        require(state["L", r] == expected, "all-column scalar endpoint")
    require(all(not row for r, row in state.items() if r[0] != "L"), "private work or centre dirt")
    return dict(real_primitives=cost, prefix_l1=str(peak),
                prefix_bits=peak.numerator.bit_length() - peak.denominator.bit_length() + 1,
                scratch_prefix_l1=str(scratch_peak), paid_profile=dict(sorted(profile.items())),
                batches=len(records), additions=sum(b - a for a, b, *_ in records),
                batch_sha256=digest(canonical(records)),
                length_histogram=dict(sorted(Counter(b - a for a, b, *_ in records).items())))


def controls():
    sample = [["scalar", ["add", ["L", 0], ["L", i], sign * 13, 4], 1]
              for i, sign in ((1, 1), (2, -1), (3, 1))]
    recipe = lower(sample)
    block_check(sample)
    cases = {"missing_entry_clear": recipe[1:], "missing_exit_clear": recipe[:-1],
             "missing_source_read": recipe[:2] + recipe[3:]}
    half = next(i for i, op in enumerate(recipe) if op[0] == "half")
    double = next(i for i, op in enumerate(recipe) if op[0] == "double")
    cases["missing_halving"] = recipe[:half] + recipe[half + 1:]
    cases["missing_doubling"] = recipe[:double] + recipe[double + 1:]
    wrong = list(recipe)
    wrong[2] = ("add", WORK, ("L", 2), 1)
    cases["wrong_source_sign"] = wrong
    last_add = max(i for i, op in enumerate(recipe) if op[0] == "add")
    cases["missing_target_accumulation"] = recipe[:last_add] + recipe[last_add + 1:]
    cases["cost_inflation"] = recipe[:-1] + [("double", WORK), ("half", WORK)] * 100 + recipe[-1:]
    rejected = []
    for name, program in cases.items():
        try:
            block_check(sample, program)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("control accepted: " + name)
    for name, pos, value in (("target_alias", (0, 1, 2), ["L", 0]),
                             ("frame_boundary", (1, 2), 0),
                             ("non_dyadic", (0, 1, 4), 3)):
        mutated = json.loads(json.dumps(sample))
        obj = mutated
        for part in pos[:-1]:
            obj = obj[part]
        obj[pos[-1]] = value
        try:
            lower(mutated)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("invalid input accepted: " + name)
    # An endpoint-neutral excursion must still increase the measured envelope.
    registers = [("L", i) for i in range(4)] + [WORK]
    state = {r: {i: Q(1)} for i, r in enumerate(registers)}
    env = {r: Q(1) for r in registers}
    excursion = recipe[:-1] + [("double", WORK)] * 10 + [("half", WORK)] * 10 + recipe[-1:]
    require(execute(excursion, state, env) > block_check(sample), "prefix excursion undetected")
    rejected.append("endpoint_neutral_prefix_excursion")
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", action="store_true", help="print computed evidence instead of checking EXPECTED.json")
    args = parser.parse_args()
    word, programs, checks, prior = read_sources()
    rows = {}
    for orientation, events in programs.items():
        before = replay(events, orientation, False, 716)
        after = replay(events, orientation, True, 716)
        require(before["real_primitives"] == checks[orientation]["real_component_primitive_bound"], "original invoice")
        require(before["prefix_l1"] == prior["local"][orientation]["prefix_l1_upper"], "original prefix")
        require(after["paid_profile"] == before["paid_profile"] == {int(k): v for k, v in word["local_profile"].items()}, "paid profile")
        require(Q(after["prefix_l1"]) < 2 ** prior["local"][orientation]["charged_payload_bits"], "payload allowance exceeded")
        rows[orientation] = dict(before=before, after=after,
                                 real_saved=before["real_primitives"] - after["real_primitives"])
    result = dict(status="PASS_JP8_REVERSE_HORNER_FANIN", live_columns=716,
                  arbitrary_private_inputs=9, orientations=rows, controls=controls())
    if args.receipt:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(json.loads((HERE / "EXPECTED.json").read_text()) == json.loads(json.dumps(result)), "receipt mismatch")
        backward = rows["backward"]
        print("PASS_JP8_REVERSE_HORNER_FANIN"
              f" batches={backward['after']['batches']} additions={backward['after']['additions']}"
              f" real_saved={backward['real_saved']} columns=716 controls={len(result['controls'])}")


if __name__ == "__main__":
    main()
