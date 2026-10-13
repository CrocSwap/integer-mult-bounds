"""Offline full CK scalar replay; Python 3.10+, standard library only.

Joseph / AmazedBot with substantial OpenAI Codex assistance. Apache-2.0.
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
from circuit import (WORK, block_word, copy_reference, magnitude, partitions, reference,
                     require, route, route_word)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = ROOT / "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck"
N = 716


def payload(path):
    data = path.read_bytes()
    return gzip.decompress(data) if path.suffix == ".gz" else data


def read(path):
    return json.loads(payload(path))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def pinned_inputs():
    manifest = read(HERE / "SOURCES.json")
    for name, pin in manifest["files"].items():
        path = ROOT / name
        require(digest(payload(path)) == pin["payload_sha256"], "source pin: " + name)
    programs = read(PROVIDER / "LOCAL-PROGRAMS.json.gz")
    checks = read(PROVIDER / "LOCAL-CHECKS.json")
    spec = read(ROOT / "research/complex-k492-owner-repair/data/SPEC.json")["providers"]["ck"]
    require(digest(payload(PROVIDER / "LOCAL-PROGRAMS.json.gz")) ==
            spec["artifact_semantic_sha256"]["LOCAL-PROGRAMS.json.gz"], "SPEC program binding")
    require(set(programs) == {"forward", "backward"}, "orientation inventory")
    for name, events in programs.items():
        require(digest(encoded(events)) == checks[name]["sha256"], "semantic program pin")
        require(checks[name]["sha256"] == spec["program_hashes"][name], "SPEC orientation binding")
    return programs, checks, read(PROVIDER / "INDEPENDENT-LOCAL-REPLAY.json")


def initial():
    rows = {("L", r): {r: Q(1)} for r in range(N)}
    rows.update({("C", r): {N + r: Q(1)} for r in range(8)})
    rows[WORK] = {N + 8: Q(1)}
    return rows


def step(rows, op):
    """Sparse exact row interpretation of individual primitives."""
    tag, t = op[:2]
    if tag == "clear":
        rows[t] = {}
    elif tag == "copy":
        rows[t] = rows[op[2]].copy()
    elif tag in ("double", "halve", "negate"):
        q = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
        rows[t] = {j: q * x for j, x in rows[t].items()}
    elif tag in ("add", "subtract"):
        require(t != op[2], "primitive source alias")
        for j, value in rows[op[2]].items():
            v = rows[t].get(j, Q(0)) + (value if tag == "add" else -value)
            if v:
                rows[t][j] = v
            else:
                rows[t].pop(j, None)
    else:
        raise ValueError("unknown primitive")


def envelope_step(env, op):
    """Literal positive triangle envelope; subtraction is charged as addition."""
    tag, t = op[:2]
    if tag == "clear":
        env[t] = Q(0)
    elif tag == "copy":
        env[t] = env[op[2]]
    elif tag == "double":
        env[t] *= 2
    elif tag == "halve":
        env[t] /= 2
    elif tag == "negate":
        pass
    elif tag in ("add", "subtract"):
        env[t] += env[op[2]]
    else:
        raise ValueError("unknown envelope primitive")
    return env[t]


def macro_step(rows, op):
    """Direct scalar semantics, separate from the primitive expansion."""
    tag, t = op[0], tuple(op[1])
    if tag == "clear":
        rows[t] = {}
    elif tag == "copy":
        rows[t] = rows[tuple(op[2])].copy()
    elif tag == "scale":
        q = Q(op[2], op[3])
        rows[t] = {j: q * v for j, v in rows[t].items()}
    elif tag == "add":
        q, s = Q(op[3], op[4]), tuple(op[2])
        for j, v in rows[s].items():
            value = rows[t].get(j, Q(0)) + q * v
            if value:
                rows[t][j] = value
            else:
                rows[t].pop(j, None)
        rows[WORK] = {}
    else:
        raise ValueError("unknown direct macro")


def original_count(op):
    tag = op[0]
    if tag in ("clear", "copy"):
        return 1
    q = Q(*op[3:5]) if tag == "add" else Q(*op[2:4])
    a, b = abs(q.numerator), q.denominator
    if tag == "scale":
        return abs(a.bit_length() - b.bit_length()) + int(q < 0)
    return 3 + (a.bit_length() - 1) + a.bit_count() + (b.bit_length() - 1)


def check_endpoint(rows, orientation):
    for r in range(N):
        expected = {r: Q(1)}
        if orientation == "forward" and 112 <= r < 224:
            expected[r - 112] = Q(1)
        if orientation == "backward" and r < 112:
            expected[r + 112] = Q(-1)
        require(rows["L", r] == expected, f"wrong full endpoint at L{r}")
    require(all(not row for register, row in rows.items() if register[0] != "L"),
            "private work or center dirt survived")


def fraction_bits(row):
    """Largest power-of-two denominator exponent in one exact coefficient row."""
    return max((x.denominator.bit_length() - 1 for x in row.values()), default=0)


def replay(events, orientation, checks):
    rows, direct, base = initial(), initial(), initial()
    depth = {"signed": 0, "original": 0}
    work_bits = Counter()
    env = {r: Q(1) for r in rows}
    baseline_env = env.copy()
    peak = baseline_peak = Q(1)
    primitive_hash, blocks_hash = hashlib.sha256(), hashlib.sha256()
    costs = Counter()
    operations, phases, signed_wins = Counter(), Counter(), Counter()
    paid = Counter()
    non_scalar = []
    pairs = set()
    phase = None
    block_count = run_additions = macros = 0
    for i, j in partitions(events):
        e = events[i]
        if e[0] != "scalar":
            require(j == i + 1 and e[0] in
                    ("phase", "adapter", "residual_adapter", "climb", "center"),
                    "unexpected non-scalar event")
            require(not rows[WORK] or i == 0, "work crosses a non-scalar event")
            non_scalar.append(e)
            if e[0] == "phase":
                phase = e[1]
            elif e[0] == "climb":
                paid[e[5]] += 1
            elif e[0] == "center":
                paid[e[4]] += 1
            continue
        chunk = events[i:j]
        old = sum(original_count(event[1]) for event in chunk)
        costs["original"] += 2 * old
        costs["copy_baseline"] += 2 * sum(len(copy_reference(event[1])) for event in chunk)
        macros += len(chunk)
        if j - i >= 2:
            block_count += 1
            run_additions += len(chunk)
            phases[phase] += 1
            word = block_word(chunk)
            choices = {mode: block_word(chunk, mode) for mode in ("power", "positive")}
            for mode, comparator in choices.items():
                costs[mode] += 2 * len(comparator)
            record = [i, j, phase, chunk[0][2], chunk[0][1][2], []]
            qs = [magnitude(event[1]) for event in chunk]
            for a, b in zip(qs, qs[1:]):
                pairs.add((a, b))
                choice = route(a, b)
                record[-1].append([str(a), str(b), list(choice)])
                if choice[0] < route(a, b, "positive")[0]:
                    require(choice[-1] == -1, "signed win without subtraction")
                    signed_wins[phase] += 1
            blocks_hash.update(encoded(record) + b"\n")
        else:
            word = copy_reference(e[1])
            require(len(reference(e[1])) == old, "reference count differs from source formula")
            costs["power"] += 2 * len(word)
            costs["positive"] += 2 * len(word)
        costs["signed"] += 2 * len(word)
        for event in chunk:
            macro_step(direct, event[1])
            for primitive in reference(event[1]):
                baseline_peak = max(baseline_peak, envelope_step(baseline_env, primitive))
                step(base, primitive)
                depth["original"] = max(depth["original"], fraction_bits(base[primitive[1]]))
        for primitive in word:
            step(rows, primitive)
            bits_now = fraction_bits(rows[primitive[1]])
            if primitive[1] == WORK:
                work_bits[bits_now] += 1
            depth["signed"] = max(depth["signed"], bits_now)
            peak = max(peak, envelope_step(env, primitive))
            operations[primitive[0]] += 2
            primitive_hash.update(encoded([e[2], primitive]) + b"\n")
        touched = {tuple(event[1][1]) for event in chunk}
        if any(event[1][0] == "add" for event in chunk):
            touched.add(WORK)
        require(all(rows[r] == direct[r] for r in touched),
                f"primitive/direct boundary disagreement at event {i}")
    require(rows == direct, "complete primitive/direct disagreement")
    check_endpoint(rows, orientation)
    require(macros == checks["scalar_macros"] == 21936, "macro inventory")
    require(costs["original"] == checks["real_component_primitive_bound"],
            "original invoice mismatch")
    require(costs["copy_baseline"] == (169618 if orientation == "forward" else 169634),
            "PR696 baseline count")
    require(dict(paid) == {int(k): v for k, v in checks["paid_profile"].items()},
            "paid child histogram")
    require(peak < 2 ** 192, "literal positive prefix exceeds inherited allowance")
    bits = peak.numerator.bit_length() - peak.denominator.bit_length() + 1
    return {
        "events": len(events), "scalar_macros": macros,
        "all_input_columns": N + 9, "dirty_helpers_restored": 492,
        "blocks": block_count, "run_additions": run_additions,
        "blocks_by_phase": dict(sorted(phases.items())),
        "signed_wins_by_phase": dict(sorted(signed_wins.items())),
        "real_primitives": dict(costs), "primitive_counts": dict(sorted(operations.items())),
        "signed_saving_vs_positive": costs["positive"] - costs["signed"],
        "signed_saving_vs_power": costs["power"] - costs["signed"],
        "signed_saving_vs_original": costs["original"] - costs["signed"],
        "signed_saving_vs_copy_baseline": costs["copy_baseline"] - costs["signed"],
        "literal_positive_prefix": str(peak), "literal_positive_prefix_bits": bits,
        "original_positive_prefix": str(baseline_peak),
        "charged_payload_bits": 192,
        # Low-end precision: exact rows on unit inputs, not an envelope.
        "max_fraction_bits": depth["signed"],
        "original_max_fraction_bits": depth["original"],
        "work_steps_finer_than_original_max": sum(
            n for b, n in work_bits.items() if b > depth["original"]),
        "paid_profile": {str(k): v for k, v in sorted(paid.items())},
        "non_scalar_sha256": digest(encoded(non_scalar)),
        "primitive_word_sha256": primitive_hash.hexdigest(),
        "blocks_sha256": blocks_hash.hexdigest(),
    }, pairs


def route_certificate(pairs):
    return [{"a": str(a), "b": str(b),
             **{mode: list(route(a, b, mode)) for mode in ("power", "positive", "signed")}}
            for a, b in sorted(pairs)]


def local_check(events, word):
    regs = {tuple(e[1][1]) for e in events} | {tuple(e[1][2]) for e in events} | {WORK}
    rows = {r: {i: Q(1)} for i, r in enumerate(sorted(regs))}
    direct = {r: row.copy() for r, row in rows.items()}
    for e in events:
        macro_step(direct, e[1])
    for op in word:
        step(rows, op)
    require(rows == direct, "local arbitrary-input identity or final clear failed")


def controls(programs):
    rejected = []

    def reject(name, action, fragment=None):
        try:
            action()
        except (ValueError, KeyError, ZeroDivisionError) as error:
            require(fragment is not None, "control without expected reason: " + name)
            require(fragment in str(error), "control failed for wrong reason: " + name)
            rejected.append(name)
        else:
            raise ValueError("accepted control: " + name)

    sample = [["scalar", ["add", ["L", 1], ["L", 0], 3, 2], 0],
              ["scalar", ["add", ["L", 2], ["L", 0], 1, 2], 0]]
    word = block_word(sample)
    require(("subtract", WORK, ("L", 0)) in word, "subtraction control absent")
    reject("missing_final_clear", lambda: local_check(sample, word[:-1]), "local arbitrary-input identity")
    reject("missing_initial_copy", lambda: local_check(sample, word[1:]), "local arbitrary-input identity")
    bad = [("add", *op[1:]) if op[0] == "subtract" else op for op in word]
    reject("wrong_signed_read", lambda: local_check(sample, bad), "local arbitrary-input identity")
    bad = [op for op in word if not (op[0] == "add" and op[1] == ("L", 2))]
    reject("missing_target_accumulation", lambda: local_check(sample, bad), "local arbitrary-input identity")
    bad = [op for op in word if op[0] != "halve"]
    reject("omitted_halving", lambda: local_check(sample, bad), "local arbitrary-input identity")
    barrier = "run crosses a source, frame, unit or non-scalar barrier"
    for name, event, why in (
        ("source_change", ["scalar", ["add", ["L", 2], ["L", 3], 1, 2], 0], barrier),
        ("frame_change", ["scalar", sample[1][1], 1], barrier),
        ("source_write", ["scalar", ["add", ["L", 0], ["L", 0], 1, 2], 0],
         "source aliases target"),
        ("unit_barrier", ["scalar", ["add", ["L", 2], ["L", 0], 1, 1], 0], barrier),
        ("phase_barrier", ["phase", "other"], barrier),
    ):
        reject(name, lambda event=event: block_word([sample[0], event]), why)
    reject("non_dyadic", lambda: reference(["add", ["L", 1], ["L", 0], 1, 3]),
           "nonzero dyadic required")
    reject("zero_coefficient", lambda: reference(["add", ["L", 1], ["L", 0], 0, 1]),
           "nonzero dyadic required")
    reject("work_alias", lambda: reference(["add", ["L", 1], list(WORK), 1, 2]),
           "source aliases target or work")
    choice = route(Q(3, 2), Q(1, 2))
    reject("undercharged_read", lambda: route_word(("L", 0), Q(1, 2),
                                                   (choice[0] - 1, *choice[1:])),
           "undercharged")
    # Endpoint-neutral growth cannot be accepted merely from endpoint equality.
    growth = [("double", ("L", 0))] * 193 + [("halve", ("L", 0))] * 193 + word
    local_check(sample, growth)
    env = {("L", i): Q(1) for i in range(3)} | {WORK: Q(1)}
    peak = max(envelope_step(env, op) for op in growth)
    reject("endpoint_neutral_prefix_growth", lambda: require(peak < 2 ** 192, "prefix"), "prefix")
    # Every actual run must clear arbitrary entry dirt, not just the toy case.
    all_missing_clear = 0
    for events in programs.values():
        for i, j in partitions(events):
            if j - i >= 2:
                chunk = events[i:j]
                local_check(chunk, block_word(chunk))
                try:
                    local_check(chunk, block_word(chunk)[:-1])
                except ValueError:
                    all_missing_clear += 1
                else:
                    raise ValueError("actual run accepted missing clear")
    return {"rejected": rejected, "actual_run_missing_clear_rejections": all_missing_clear}


def verify():
    programs, checks, inherited = pinned_inputs()
    outputs, pairs = {}, set()
    for orientation in ("forward", "backward"):
        outputs[orientation], used = replay(programs[orientation], orientation, checks[orientation])
        require(outputs[orientation]["original_positive_prefix"] ==
                inherited["local"][orientation]["prefix_l1_upper"], "original prefix binding")
        outputs[orientation]["historical_prefix_bits"] = inherited["local"][orientation]["prefix_bits_upper"]
        pairs.update(used)
    routes = route_certificate(pairs)
    contract = read(ROOT / "research/complex-k492-owner-repair/data/SPEC.json")["providers"]["ck"]["complete_contract"]
    reserve = contract["local_adapters"] * contract["compiler"]
    original = max(p["real_primitives"]["original"] for p in outputs.values()) + reserve
    require(original == contract["local_primitive_bound"], "original complete local invoice")
    revised = max(p["real_primitives"]["signed"] for p in outputs.values()) + reserve
    result = {"status": "PASS_CK_SIGNED_ROUTES", "programs": outputs,
              "distinct_coefficient_pairs": len(pairs),
              "one_read_domain": {"u": [-16, 16], "v": [-16, 16], "signs": [-1, 1]},
              "routes_sha256": digest(encoded(routes)), "controls": controls(programs),
              "local_substitution_budget": {"unchanged_adapter_reserve": reserve,
                  "old_max_orientation_plus_reserve": original,
                  "new_max_orientation_plus_reserve": revised,
                  "saving": original - revised,
                  "status": "conditional arithmetic only; no global admission"},
              "kappa_claim": "none"}
    return result, routes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print checked receipt")
    args = parser.parse_args()
    result, routes = verify()
    require(routes == read(HERE / "ROUTES.json"), "route certificate mismatch")
    require(result == read(HERE / "EXPECTED.json"), "receipt mismatch")
    # Second implementation (same AI author): imports neither this verifier nor
    # the construction module, but re-verifies the constructor's route table.
    from independent_check import audit
    independent = audit()
    require(independent["pairs"] == len(routes), "independent coverage")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        gains = ",".join(str(p["signed_saving_vs_positive"]) for p in result["programs"].values())
        print(f"PASS_CK_SIGNED_ROUTES orientations=2 columns=725 extra_saved={gains} "
              f"pairs={len(routes)} cases={independent['one_read_cases']} "
              f"controls={len(result['controls']['rejected'])} kappa=unchanged")


if __name__ == "__main__":
    main()
