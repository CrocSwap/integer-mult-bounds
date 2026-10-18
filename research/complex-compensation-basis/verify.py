#!/usr/bin/env python3
"""Exact, offline verification of a restored JP8 compensation basis.

The search implementation is never imported. All checks remain active with -O.
Sricharan Vagvala (@theon199), with substantial OpenAI Codex assistance.
Apache-2.0. See README.md for predecessor credit and scope.
"""
import argparse
import copy
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = "research/community-k492-audit/pr622/replay/jp8-local/"
CODE = "research/complex-k492-owner-repair/code/"
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def payload(path):
    data = path.read_bytes()
    return gzip.decompress(data) if path.suffix == ".gz" else data


def read(path):
    return json.loads(payload(path))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sources():
    pins = read(HERE / "SOURCES.json")
    for path, expected in pins["files"].items():
        need(hashlib.sha256(payload(ROOT / path)).hexdigest() == expected, "source pin: " + path)
    selected = read(ROOT / "certificates/selected-result.json")
    need(selected["audited_source_head"] == pins["pr626_head"], "selected source head")
    need(selected["reviewed_dependency_heads"]["622"] == pins["pr622_head"], "construction head")
    spec = read(ROOT / SPEC)["providers"]["jp8"]
    for filename in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
        need(pins["files"][NATIVE + filename] == spec["artifact_semantic_sha256"][filename],
             "word/program binding to selected SPEC")
    return spec


def add(t, s, q):
    return ["add", t, s, q.numerator, q.denominator, 0]


def coefficient_cost(q):
    """Count a literal Horner primitive trace, independently of search.price."""
    need(q != 0 and q.denominator & (q.denominator - 1) == 0, "nonzero dyadic add")
    bits = bin(abs(q.numerator))[2:]
    operations = ["clear"]
    for index, bit in enumerate(bits):
        if index:
            operations.append("double")
        if bit == "1":
            operations.append("add_source")
    denominator = q.denominator
    while denominator > 1:
        operations.append("halve")
        denominator //= 2
    operations.extend(("signed_accumulate", "clear"))
    return 2 * len(operations)


def circuit_cost(ops):
    return sum(coefficient_cost(Q(e[3], e[4])) for e in ops)


def compensation_rows(word):
    v, n = word["v"], 2 * word["v"] + word["R"]
    rows = {t: {} for t in range(v, 2 * v)}
    for e in word["compensation"]:
        need(len(e) == 6 and e[0] == "add" and e[-1] == 0, "compensation instruction")
        _, t, s, a, b, _ = e
        need(t in rows and 2 * v <= s < n and s not in rows[t], "compensation incidence")
        need(word["start"][s] == 0 and word["final"][s] == 1, "unwrapped cold source")
        rows[t][s] = Q(a, b)
    return rows


def construct(word, recipe):
    need((word["v"], word["R"], word["h"]) == (112, 492, 9), "selected geometry")
    need(recipe["provider"] == "jp8" and recipe["seed"] == 24, "assignment")
    rows = compensation_rows(word)
    original = copy.deepcopy(rows)
    prep, restore, used = [], [], set()
    domain = {Q(s) * Q(2) ** k for s in (-1, 1) for k in range(-2, 3)}
    for pair in recipe["pairs"]:
        t, d, q = pair["target"], pair["donor"], Q(pair["coefficient"])
        need(t in rows and d in rows and t != d, "target pair")
        need(not ({t, d} & used), "disjoint target pairs")
        need(q in domain, "coefficient domain")
        used.update((t, d))
        prep.append(add(t, d, -q))
        restore.append(add(t, d, q))
        # Read the frozen original donor, rather than a successively changed row.
        rows[t] = {s: original[t].get(s, Q(0)) - q * original[d].get(s, Q(0))
                   for s in original[t].keys() | original[d].keys()}
        rows[t] = {s: x for s, x in rows[t].items() if x}
        old_ops = [add(t, s, x) for s, x in original[t].items()]
        new_ops = [prep[-1]] + [add(t, s, x) for s, x in rows[t].items()] + [restore[-1]]
        need(circuit_cost(old_ops) - circuit_cost(new_ops) == pair["saved_real_primitives"] > 0,
             "pair's fully paid primitive saving")
        need(len(old_ops) - len(new_ops) == pair["saved_macros"], "pair's macro saving")
    replacement = prep + [add(t, s, q) for t, row in sorted(rows.items())
                          for s, q in sorted(row.items())] + restore
    candidate = copy.deepcopy(word)
    candidate["compensation"] = replacement
    need({k: v for k, v in candidate.items() if k != "compensation"} ==
         {k: v for k, v in word.items() if k != "compensation"}, "only compensation changed")
    return candidate


def dual(e):
    _, t, s, a, b, frame = e
    return ["add", s, t, -a, b, frame]


def boundary_matrix(ops, word, backward=False):
    """Sparse row replay on the COMPLETE input basis, including target dirt."""
    n, v = 2 * word["v"] + word["R"], word["v"]
    state = [{r: Q(1)} for r in range(n)]
    for gate in ops:
        need(len(gate) == 6 and gate[0] == "add", "boundary add grammar")
        _, t, s, a, b, frame = gate
        need(type(t) is int and type(s) is int and 0 <= t < n and 0 <= s < n and t != s,
             "boundary register incidence")
        need(v <= t < 2 * v and s >= v, "forward boundary writes targets and does not read data")
        need(frame == 0 and word["start"][t] == word["start"][s] == 0, "zero common frame")
        need(s < 2 * v or word["final"][s] == 1, "cold wrapper boundary")
        q = Q(a, b)
        coefficient_cost(q)
        if backward:
            t, s, q = s, t, -q
        for j, x in list(state[s].items()):
            new = state[t].get(j, Q(0)) + q * x
            if new:
                state[t][j] = new
            else:
                state[t].pop(j, None)
    return state


def check_boundary(word, replacement):
    for backward in (False, True):
        need(boundary_matrix(word["compensation"], word, backward) ==
             boundary_matrix(replacement, word, backward), "complete boundary operator")


def scalar_event(gate, backward):
    if backward:
        gate = dual(gate)
    _, t, s, a, b, f = gate
    return ["scalar", ["add", ["L", t], ["L", s], a, b], f]


def replace_programs(word, candidate, programs):
    """Retain every event outside the identified compensation slice verbatim."""
    out = {}
    first = 1 + len(word["precondition"])
    last = first + len(word["compensation"])
    for name, events in programs.items():
        backward = name == "backward"
        need(events[0] == ["phase", "zero_frame_precondition"] and
             events[last] == ["phase", "entry_adapters"], "exact replacement boundaries")
        need(events[first:last] == [scalar_event(e, backward) for e in word["compensation"]],
             "source compensation/program correspondence")
        out[name] = events[:first] + [scalar_event(e, backward) for e in candidate["compensation"]] + events[last:]
        need([e for e in events if e[0] != "scalar"] ==
             [e for e in out[name] if e[0] != "scalar"], "unchanged non-scalar event stream")
    return out


def replay_integer_matrix(events, n, v, backward):
    """Exact integer-matrix scalar replay covering every input column.

    The inherited native checker uses Fraction-valued sparse rows. This separate
    implementation uses integer vectors with a shared power-of-two denominator
    per register. Rescaling and normalization are exact, without rounding.
    """
    scalar_ops = [event[1] for event in events if event[0] == "scalar"]
    # Each live register's nonzero input coefficients have a denominator
    # exponent shared across the entire vector.
    state = {("L", r): ({r: 1}, 0) for r in range(n)}
    for op in scalar_ops:
        tag, target = op[0], tuple(op[1])
        if tag == "clear":
            state[target] = ({}, 0)
            continue
        if tag == "copy":
            nums, power = state[tuple(op[2])]
            state[target] = (nums.copy(), power)
            continue
        a, b = (op[2], op[3]) if tag == "scale" else (op[3], op[4])
        q = Q(a, b)
        need(q.denominator & (q.denominator - 1) == 0, "dyadic replay")
        if tag == "scale":
            nums, power = state[target]
            state[target] = ({j: q.numerator * value for j, value in nums.items()},
                             power + q.denominator.bit_length() - 1)
        else:
            need(tag == "add", "scalar grammar")
            source = tuple(op[2])
            left, lp = state.get(target, ({}, 0))
            right, rp = state[source]
            rp += q.denominator.bit_length() - 1
            power = max(lp, rp)
            result = {j: value << (power - lp) for j, value in left.items()}
            for j, value in right.items():
                value = result.get(j, 0) + q.numerator * (value << (power - rp))
                if value:
                    result[j] = value
                else:
                    result.pop(j, None)
            state[target] = (result, power)
        # Remove common powers of two to keep integers small. Zero rows have
        # no precision debt. No rounding or modular arithmetic is used.
        nums, power = state[target]
        if not nums:
            state[target] = ({}, 0)
        elif power:
            shift = min(power, min((abs(x) & -abs(x)).bit_length() - 1 for x in nums.values()))
            if shift:
                state[target] = ({j: value >> shift for j, value in nums.items()}, power - shift)
    for r in range(n):
        nums, power = state[("L", r)]
        expected = {r: 1 << power}
        if backward and r < v:
            expected[r + v] = -(1 << power)
        if not backward and v <= r < 2 * v:
            expected[r - v] = 1 << power
        need(nums == expected, "full scalar operator at register " + str(r))
    need(all(not nums for reg, (nums, _) in state.items() if reg[0] == "C"), "private centers cleared")


def rejected(name, operation):
    try:
        operation()
    except (ValueError, KeyError, ZeroDivisionError):
        return name
    raise ValueError("negative control accepted: " + name)


def controls(word, candidate, recipe):
    ops = candidate["compensation"]
    count = len(recipe["pairs"])
    mutations = []
    mutations.append(("missing_preparation_on_dirty_targets", ops[1:]))
    mutations.append(("missing_restoration", ops[:-1]))
    changed = copy.deepcopy(ops)
    changed[0][3] *= -1
    mutations.append(("wrong_preparation_sign", changed))
    changed = copy.deepcopy(ops)
    del changed[count]
    mutations.append(("missing_helper_read", changed))
    changed = copy.deepcopy(ops)
    changed[0][-1] = 1
    mutations.append(("nonzero_frame", changed))
    changed = copy.deepcopy(ops)
    changed[count][2] = next(r for r in range(224, 716) if word["start"][r] == 0 and word["final"][r] != 1)
    mutations.append(("cold_ended_helper_before_wrapper", changed))
    changed = copy.deepcopy(ops)
    changed[0][2] = changed[0][1]
    mutations.append(("aliased_shear", changed))
    changed = copy.deepcopy(ops)
    changed[0][4] = 3
    mutations.append(("non_dyadic_coefficient", changed))
    names = [rejected(name, lambda es=es: check_boundary(word, es)) for name, es in mutations]
    bad_recipe = copy.deepcopy(recipe)
    bad_recipe["pairs"].append(bad_recipe["pairs"][0])
    names.append(rejected("overlapping_pairs", lambda: construct(word, bad_recipe)))
    bad_recipe = copy.deepcopy(recipe)
    bad_recipe["pairs"][0]["saved_real_primitives"] += 1
    names.append(rejected("undercharged_basis_changes", lambda: construct(word, bad_recipe)))
    # Explain why zero-target-only testing is inadequate: omitted preparation
    # preserves every helper-input column but changes a target-input column.
    good = boundary_matrix(ops, word)
    bad = boundary_matrix(ops[1:], word)
    need(all({j: x for j, x in a.items() if j >= 224} ==
             {j: x for j, x in b.items() if j >= 224} for a, b in zip(good, bad)),
         "missing-preparation control must pass the helper-only check")
    need(good != bad, "dirty target control is distinguishing")
    # A cancelling pair has identity endpoint but still costs 16 real primitives.
    t, s = recipe["pairs"][0]["target"], recipe["pairs"][0]["donor"]
    neutral = [add(t, s, Q(1)), add(t, s, Q(-1))]
    check_boundary(word, ops + neutral)
    need(circuit_cost(ops + neutral) == circuit_cost(ops) + 16, "charge neutral work")
    return names


def native_replay(candidate, expected_programs):
    """Unmodified pinned emitter and independent frame/wrapper auditor."""
    with tempfile.TemporaryDirectory(prefix="complex-compensation-seed24-") as directory:
        out = Path(directory)
        canonical = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()
        (out / "CANONICAL-WORD.json.gz").write_bytes(gzip.compress(canonical, mtime=0))
        for script in ("hpe_emit_local.py", "hpe_audit_local.py"):
            # -I ignores PYTHONOPTIMIZE; inherited assertion checks run enabled,
            # including when this parent verifier itself is invoked with -O.
            result = subprocess.run([sys.executable, "-I", "-B", str(ROOT / CODE / script), str(out)],
                                    text=True, capture_output=True, check=False)
            need(result.returncode == 0, "native replay failed: " + script + "\n" + result.stdout + result.stderr)
        need(read(out / "LOCAL-PROGRAMS.json.gz") == expected_programs, "fresh native emitter agreement")
        checks = read(out / "LOCAL-CHECKS.json")
        audit = read(out / "INDEPENDENT-LOCAL-REPLAY.json")
        # Container hashes vary with zlib; only semantic, proof-relevant output
        # fields enter EXPECTED.json. Immutable source pins use payload hashes.
        return checks, {k: audit[k] for k in ("status", "v", "helpers", "local", "paid_profiles",
                                            "entering_helpers", "cold_hyperplane_ended_helpers",
                                            "negative_controls_rejected")}


def verify():
    spec = sources()
    word = read(ROOT / NATIVE / "CANONICAL-WORD.json.gz")
    recipe = read(HERE / "RECIPE.json")
    candidate = construct(word, recipe)
    check_boundary(word, candidate["compensation"])
    names = controls(word, candidate, recipe)
    original_programs = read(ROOT / NATIVE / "LOCAL-PROGRAMS.json.gz")
    programs = replace_programs(word, candidate, original_programs)
    for label, batch in (("original", original_programs), ("candidate", programs)):
        for name, events in batch.items():
            replay_integer_matrix(events, 716, 112, name == "backward")
    checks, audit = native_replay(candidate, programs)
    for name in ("forward", "backward"):
        need(checks[name]["paid_profile"] == spec["expected_profile"], "unchanged paid profile")
        need(checks[name]["all_columns"] == 716, "full native basis")
        need(Q(audit["local"][name]["prefix_l1_upper"]) < 2 ** 192, "retained local payload allowance")
    baseline = read(ROOT / NATIVE / "LOCAL-CHECKS.json")
    prior_audit = read(ROOT / NATIVE / "INDEPENDENT-LOCAL-REPLAY.json")
    saved = circuit_cost(word["compensation"]) - circuit_cost(candidate["compensation"])
    need(saved == sum(p["saved_real_primitives"] for p in recipe["pairs"]), "complete compensation cost")
    for name in ("forward", "backward"):
        need(baseline[name]["real_component_primitive_bound"] - checks[name]["real_component_primitive_bound"] == saved,
             "full native primitive saving")
    return dict(status="PASS_COMPLEX_COMPENSATION_BASIS", seed=24, provider="jp8",
                recipe_sha256=digest(recipe), canonical_sha256=digest(candidate),
                pairs=len(recipe["pairs"]), columns=716, compensation_before=len(word["compensation"]),
                compensation_after=len(candidate["compensation"]),
                compensation_real_primitives_before=circuit_cost(word["compensation"]),
                compensation_real_primitives_after=circuit_cost(candidate["compensation"]),
                saved_real_primitives_each_orientation=saved,
                scalar_replays=4, dirty_target_control_passes_helper_only_check=True,
                negative_controls=names, native=checks, native_audit=audit,
                original_local=baseline, original_prefix=prior_audit["local"],
                kappa="unchanged; no global invoice or assembly claim")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a fresh certificate instead of comparing EXPECTED.json")
    args = parser.parse_args()
    result = verify()
    if args.output:
        with args.output.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(result == read(HERE / "EXPECTED.json"), "certificate mismatch")
    print(f"PASS_COMPLEX_COMPENSATION_BASIS pairs={result['pairs']} "
          f"compensation={result['compensation_before']}->{result['compensation_after']} "
          f"saved_real_primitives={result['saved_real_primitives_each_orientation']} "
          f"columns=716 controls={len(result['negative_controls'])}+25 kappa=unchanged")


if __name__ == "__main__":
    main()
