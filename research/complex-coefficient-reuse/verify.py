"""Exact finite checker for the pinned JP8 coefficient-reuse circuit.

The rational interpreter, macro interpreter and positive prefix recounter
are separate from lower.py. No upstream verifier is imported or executed.
Apache-2.0; substantial OpenAI Codex assistance, prepared for @taizaki69.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

from lower import WORK, chunks, lower_run, lower_scalar, require

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/"


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def pinned_inputs():
    pins = read(HERE / "SOURCES.json")
    for name, expected in pins["payload_sha256"].items():
        path = ROOT / name
        raw = path.read_bytes()
        payload = gzip.decompress(raw) if path.suffix == ".gz" else raw
        require(hashlib.sha256(payload).hexdigest() == expected, "source pin mismatch: " + name)
    selected = read(ROOT / "certificates/selected-result.json")
    require(selected["audited_source_head"] == pins["selected_source_head"], "selected head changed")
    spec = read(ROOT / "research/complex-k492-owner-repair/data/SPEC.json")
    for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
        require(spec["providers"]["jp8"]["artifact_semantic_sha256"][name]
                == pins["payload_sha256"][PROVIDER + name], "provider binding mismatch")
    return (read(ROOT / (PROVIDER + "LOCAL-PROGRAMS.json.gz")),
            read(ROOT / (PROVIDER + "CANONICAL-WORD.json.gz")),
            read(ROOT / (PROVIDER + "LOCAL-CHECKS.json")),
            read(ROOT / (PROVIDER + "INDEPENDENT-LOCAL-REPLAY.json")))


def add_row(target, source, coefficient):
    out = target.copy()
    for column, value in source.items():
        total = out.get(column, Q(0)) + coefficient * value
        if total:
            out[column] = total
        else:
            out.pop(column, None)
    return out


def primitive(state, op):
    tag, target = op[:2]
    if tag == "clear":
        state[target] = {}
    elif tag == "copy":
        state[target] = state[op[2]].copy()
    elif tag in ("double", "half", "negate"):
        q = {"double": Q(2), "half": Q(1, 2), "negate": Q(-1)}[tag]
        state[target] = {k: q * v for k, v in state[target].items()}
    elif tag in ("add", "sub"):
        state[target] = add_row(state[target], state[op[2]], Q(1 if tag == "add" else -1))
    else:
        raise ValueError("unknown primitive: " + tag)


def macro(state, op):
    """Reference rational scalar semantics, without the lowering code."""
    tag, target = op[0], tuple(op[1])
    if tag == "clear":
        state[target] = {}
    elif tag == "copy":
        state[target] = state[tuple(op[2])].copy()
    elif tag == "scale":
        q = Q(op[2], op[3])
        state[target] = {k: q * v for k, v in state[target].items()}
    elif tag == "add":
        state[target] = add_row(state[target], state[tuple(op[2])], Q(op[3], op[4]))
        state[WORK] = {}
    else:
        raise ValueError("unknown macro")


def prefix_primitive(env, op):
    """Nonnegative l1 envelope, with subtraction charged as addition."""
    tag, target = op[:2]
    if tag == "clear":
        env[target] = Q(0)
    elif tag == "copy":
        env[target] = env[op[2]]
    elif tag in ("double", "half", "negate"):
        env[target] *= {"double": Q(2), "half": Q(1, 2), "negate": Q(1)}[tag]
    elif tag in ("add", "sub"):
        env[target] += env[op[2]]
    else:
        raise ValueError("unknown prefix primitive")
    return env[target]


def reference_cost_prefix(env, op):
    """Recount the ORIGINAL cleared-work Horner invoice without lower.py."""
    tag, target = op[0], tuple(op[1])
    peak = env[target]
    if tag == "clear":
        env[target], count = Q(0), 1
    elif tag == "copy":
        env[target], count = env[tuple(op[2])], 1
    elif tag == "scale":
        q = Q(op[2], op[3])
        count = abs(abs(q.numerator).bit_length() - q.denominator.bit_length()) + int(q < 0)
        env[target] *= abs(q)
    else:
        require(tag == "add", "unsupported reference macro")
        q, source = Q(op[3], op[4]), tuple(op[2])
        a, b = abs(q.numerator), q.denominator
        require(a > 0 and b & (b - 1) == 0 and source != target, "invalid reference add")
        # All Horner partial integers are between 0 and a. Halving only
        # decreases their magnitude, so a*env[source] is the exact maximum
        # coefficient-work envelope of this original macro.
        peak = max(peak, a * env[source])
        count = 3 + (a.bit_length() - 1) + a.bit_count() + (b.bit_length() - 1)
        env[target] += abs(q) * env[source]
        env[WORK] = Q(0)
    return count, max(peak, env[target])


def check_chunk(events, ops, state, reference, env, reference_env):
    """Execute every primitive and compare every touched row to scalar semantics."""
    expected_touched = {WORK}
    original_count = 0
    original_peak = max(reference_env.values(), default=Q(0))
    for event in events:
        require(event[0] == "scalar", "non-scalar event inside fused chunk")
        macro(reference, event[1])
        count, peak = reference_cost_prefix(reference_env, event[1])
        original_count += count
        original_peak = max(original_peak, peak)
        expected_touched.add(tuple(event[1][1]))
    touched = expected_touched | {op[1] for op in ops}
    candidate_peak = max(env.values(), default=Q(0))
    for op in ops:
        primitive(state, op)
        candidate_peak = max(candidate_peak, prefix_primitive(env, op))
    for register in touched:
        require(state.get(register, {}) == reference.get(register, {}),
                "scalar endpoint or private restoration mismatch: " + str(register))
        require(env.get(register, Q(0)) == reference_env.get(register, Q(0)),
                "boundary envelope mismatch: " + str(register))
    require(candidate_peak <= original_peak, "prefix envelope increased")
    return original_count, original_peak, candidate_peak


def replay(events, word, orientation, old_checks, inherited):
    n = 2 * word["v"] + word["R"]
    registers = [("L", r) for r in range(n)] + [("C", r) for r in range(len(word["centers"]))] + [WORK]
    state = {r: {i: Q(1)} for i, r in enumerate(registers)}
    reference = {r: row.copy() for r, row in state.items()}
    # Existing invoice treats private centres as cleared before use; starting
    # them with unit envelope adds only a peak of 1 and is checked against it.
    env = {r: Q(1) for r in registers}
    reference_env = env.copy()
    original = independent = reused = covered = 0
    peak_old = peak_new = Q(1)
    groups = []
    paid = Counter()
    non_scalar = []
    stream_hash = hashlib.sha256()
    last = 0
    for start, stop, ops in chunks(events):
        require(start == last and start < stop <= len(events), "partition gap or overlap")
        last = stop
        event = events[start]
        if ops is None:
            require(stop == start + 1 and event[0] != "scalar", "non-scalar partition changed")
            non_scalar.append(event)
            if event[0] == "climb":
                paid[event[5]] += 1
            elif event[0] == "center":
                paid[event[4]] += 1
            record = ["event", event]
        else:
            run = events[start:stop]
            if event[1][0] == "add" and abs(Q(event[1][3], event[1][4])) != 1 and stop < len(events):
                following = events[stop]
                same_next = (following[0] == "scalar" and following[1][0] == "add"
                             and following[1][2] == event[1][2] and following[2] == event[2]
                             and abs(Q(following[1][3], following[1][4]))
                             == abs(Q(event[1][3], event[1][4])))
                require(not same_next, "eligible run was not maximal")
            # Independently check fusion's immutable-source/frame obligation.
            if len(run) > 1:
                op = run[0][1]
                source, magnitude, frame = op[2], abs(Q(op[3], op[4])), run[0][2]
                require(magnitude != 1, "unit coefficient outside claimed scope")
                for e in run:
                    require(e[0] == "scalar" and e[1][0] == "add" and e[1][2] == source
                            and e[1][1] != source and abs(Q(e[1][3], e[1][4])) == magnitude
                            and e[2] == frame, "invalid fused run")
                groups.append([start, stop, source, str(magnitude), frame])
                covered += len(run)
            count, pold, pnew = check_chunk(run, ops, state, reference, env, reference_env)
            original += count
            independent += sum(len(lower_scalar(e[1])) for e in run)
            reused += len(ops)
            peak_old, peak_new = max(peak_old, pold), max(peak_new, pnew)
            record = ["scalar_chunk", start, stop, event[2], ops]
        stream_hash.update(json.dumps(record, separators=(",", ":")).encode() + b"\n")
    require(last == len(events), "incomplete event coverage")
    require(non_scalar == [e for e in events if e[0] != "scalar"], "non-scalar events changed")
    for r in range(n):
        want = {r: Q(1)}
        if orientation == "forward" and word["v"] <= r < 2 * word["v"]:
            want[r - word["v"]] = Q(1)
        elif orientation == "backward" and r < word["v"]:
            want[r + word["v"]] = Q(-1)
        require(state[("L", r)] == want, "full arbitrary-input boundary failed")
    require(all(not state[r] for r in registers if r[0] != "L"), "private dirt not erased")
    require(2 * original == old_checks[orientation]["real_component_primitive_bound"], "original invoice mismatch")
    require(sum(e[0] == "scalar" for e in events) == old_checks[orientation]["scalar_macros"], "macro census mismatch")
    require(dict(paid) == {int(k): v for k, v in old_checks[orientation]["paid_profile"].items()}, "paid profile mismatch")
    require(peak_old == Q(inherited["local"][orientation]["prefix_l1_upper"]), "inherited prefix mismatch")
    require(peak_new < 2 ** inherited["local"][orientation]["charged_payload_bits"], "payload budget exceeded")
    require(reused < independent < original, "claimed savings not obtained")
    sample = groups[39 % len(groups)]
    sample_events = events[sample[0]:sample[1]]
    return {
        "events": len(events), "scalar_macros": sum(e[0] == "scalar" for e in events),
        "all_logical_input_columns": n, "arbitrary_private_input_columns": len(registers) - n,
        "nonunit_reuse_runs": len(groups), "events_in_reuse_runs": covered,
        "maximum_run_length": max(g[1] - g[0] for g in groups),
        "original_real_primitives": 2 * original,
        "per_macro_copy_horner_real_primitives": 2 * independent,
        "shared_real_primitives": 2 * reused,
        "new_savings_over_per_macro": 2 * (independent - reused),
        "total_savings_over_original": 2 * (original - reused),
        "original_prefix_l1_upper": str(peak_old), "shared_prefix_l1_upper": str(peak_new),
        "charged_payload_bits": inherited["local"][orientation]["charged_payload_bits"],
        "paid_profile": {str(k): v for k, v in sorted(paid.items())},
        "runs_sha256": digest(groups), "primitive_stream_sha256": stream_hash.hexdigest(),
        "non_scalar_events_sha256": digest(non_scalar),
        "seed_selected_example": {"run": sample, "events": sample_events, "primitives": lower_run(sample_events)},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a newly computed certificate instead of comparing EXPECTED.json")
    args = parser.parse_args()
    programs, word, checks, inherited = pinned_inputs()
    require(set(programs) == {"forward", "backward"}, "unexpected orientation set")
    result = {"schema": "complex-coefficient-reuse-v1", "provider": "jp8", "assignment_seed": 39,
              "scope": "Finite local scalar lowering; no new recursive profile or kappa", "programs": {}}
    for orientation in ("forward", "backward"):
        result["programs"][orientation] = replay(programs[orientation], word, orientation, checks, inherited)
        print("PASS", orientation, "replay", flush=True)
    # Retain every original macro's adapter allowance, despite fusing its
    # private coefficient preparation. Recursive children are unchanged.
    children = sum(result["programs"]["forward"]["paid_profile"].values())
    macros = max(r["scalar_macros"] for r in result["programs"].values())
    n, centres, m = 2 * word["v"] + word["R"], len(word["centers"]), 73
    adapters = 16 * (macros + children + n + centres) + 64 * m
    compiler = 64 * (m + 1) ** 3
    spec = read(ROOT / "research/complex-k492-owner-repair/data/SPEC.json")
    contract = spec["providers"]["jp8"]["complete_contract"]
    original_local = max(r["original_real_primitives"] for r in result["programs"].values()) + adapters * compiler
    require((children, adapters, compiler, original_local) == (
        contract["children"], contract["local_adapters"], contract["compiler"], contract["local_primitive_bound"]),
        "retained local invoice reconstruction mismatch")
    result["conservative_local_invoice"] = {
        "helpers": word["R"], "private_centres": centres, "coefficient_work_real_streams": 2,
        "recursive_children": children, "retained_adapter_allowance": adapters,
        "retained_compiler_factor": compiler, "original_bound": original_local,
        "shared_bound": max(r["shared_real_primitives"] for r in result["programs"].values()) + adapters * compiler,
        "scope": "Local finite invoice arithmetic; no new global admission or selected receipt",
    }
    from controls import run_controls
    result["controls"] = run_controls()
    # Primitive tuples are serialized as JSON arrays; compare that exact
    # representation, including every proof-relevant certificate field.
    result = json.loads(json.dumps(result))
    if args.write:
        args.write.write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(result == read(HERE / "EXPECTED.json"), "certificate mismatch")
    savings = [result["programs"][o]["new_savings_over_per_macro"] for o in ("forward", "backward")]
    print("PASS_JP8_COEFFICIENT_REUSE columns=716+9 savings=" + ",".join(map(str, savings))
          + " controls=" + str(len(result["controls"])))


if __name__ == "__main__":
    main()
