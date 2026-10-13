"""Exact finite X4 backward scalar circuit replay. Standard library, offline.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
Run normally to compare the complete deterministic receipt; --write creates it.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


J = module("joint_horner", HERE / "joint.py")
require, WORK = J.require, J.WORK


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def inputs():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    require(pins["base_commit"] == "91a2094f2e022930069e8cfdc810a3ea1b81cd09", "starting base metadata")
    selected = None
    for name, expected in pins["files"].items():
        locations = [name]
        if name == "certificates/selected-result.json":
            locations.append("certificates/checkpoints/frontier799.json")
        matches = [ROOT / path for path in locations
                   if (ROOT / path).is_file() and sha((ROOT / path).read_bytes()) == expected]
        require(matches, "source pin: " + name)
        if name == "certificates/selected-result.json":
            selected = json.loads(matches[0].read_text())
    members = {}
    with tarfile.open(ROOT / pins["archive"]) as archive:
        for name, expected in pins["members"].items():
            matches = [m for m in archive.getmembers() if m.name == name]
            require(len(matches) == 1 and matches[0].isfile(), "archive member identity")
            raw = archive.extractfile(matches[0]).read()
            if name.endswith(".gz"):
                raw = gzip.decompress(raw)
            require(sha(raw) == expected, "member payload pin: " + name)
            members[name] = json.loads(raw)
    events = members["native/local/LOCAL-PROGRAMS.json.gz"]
    checks = members["native/local/LOCAL-CHECKS.json"]
    for orientation in ("forward", "backward"):
        require(sha(canonical(events[orientation])) == checks[orientation]["sha256"], "source event binding")
    spec = json.loads((ROOT / "research/gauge44-frames-x/data/SPEC.json").read_text())["providers"]["gauge44"]
    require(spec["program_hashes"] == {o: checks[o]["sha256"] for o in checks}, "selected SPEC binding")
    require(spec["expected_profile"] == checks["backward"]["paid_profile"], "selected recursive profile")
    require(selected["kappa"] == "1661634653669567/1000000000000000000", "selected witness context")
    require(pins["source_heads"]["799"] == selected["audited_source_head"], "PR799 source head")
    require(pins["source_heads"]["741"] == selected["reviewed_dependency_heads"]["741"], "PR741 source head")
    baseline = module("retained_pr696_lowering", ROOT / "research/complex-dyadic-lowering/lower.py")
    return events, checks, baseline.lower


def step(rows, op):
    tag, dst = op[:2]
    if tag == "clear":
        rows[dst] = {}
    elif tag == "copy":
        rows[dst] = rows[op[2]].copy()
    elif tag in ("double", "halve", "negate"):
        q = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
        rows[dst] = {i: q * x for i, x in rows[dst].items()}
    elif tag in ("add", "subtract"):
        require(dst != op[2], "primitive self ADD")
        for i, x in rows[op[2]].items():
            value = rows[dst].get(i, Q(0)) + (x if tag == "add" else -x)
            if value:
                rows[dst][i] = value
            else:
                rows[dst].pop(i, None)
    else:
        raise ValueError("unknown primitive")


def direct(rows, op):
    tag, dst = op[0], tuple(op[1])
    if tag in ("clear", "copy"):
        step(rows, (tag, dst, tuple(op[2])) if tag == "copy" else (tag, dst))
    elif tag == "scale":
        q = Q(op[2], op[3])
        rows[dst] = {i: q*x for i, x in rows[dst].items()}
    elif tag == "add":
        q = J.coefficient(op)
        for i, x in rows[tuple(op[2])].items():
            value = rows[dst].get(i, Q(0)) + q*x
            if value:
                rows[dst][i] = value
            else:
                rows[dst].pop(i, None)
        rows[WORK] = {}
    else:
        raise ValueError("unknown macro")


def check_pair(a, b, word):
    regs = [tuple(a[1]), tuple(a[2]), tuple(b[2]), WORK]
    require(len(set(regs)) == 4, "local register aliases")
    actual = {r: {i: Q(1)} for i, r in enumerate(regs)}
    expected = {r: row.copy() for r, row in actual.items()}
    direct(expected, a)
    direct(expected, b)
    for op in word:
        step(actual, op)
    require(actual == expected, "four-column pair endpoint")


def check_pair_cost(a, b, word):
    # Recount from the coefficients, independently of lower_pair's loop.
    qa, qb = J.coefficient(a), J.coefficient(b)
    denominator = max(qa.denominator, qb.denominator)
    numerators = [abs(q.numerator) * (denominator // q.denominator) for q in (qa, qb)]
    cost = max(x.bit_length() for x in numerators) + sum(x.bit_count() for x in numerators) + denominator.bit_length()
    require(len(word) == cost, "joint primitive cost")


def retained_count(op):
    if op[0] in ("copy", "clear"):
        return 1
    q = Q(*op[3:]) if op[0] == "add" else Q(*op[2:])
    a, d = abs(q.numerator), q.denominator
    if op[0] == "scale":
        return abs(a.bit_length() - d.bit_length()) + int(q < 0)
    return a.bit_length() + a.bit_count() + d.bit_length() + 1


def replay(events, lower, chosen=()):
    chosen = set(chosen)
    # Arbitrary logical, center and coefficient-work columns, including dirt.
    regs = [("L", i) for i in range(728)] + [("C", i) for i in range(8)] + [WORK]
    rows = {r: {i: Q(1)} for i, r in enumerate(regs)}
    envelope = {r: Q(1) for r in regs}
    peak = envelope_peak = Q(1)
    depth = 0
    tags, paid = Counter(), Counter()
    operand_reads = source_reads = scalar_macros = original_count = 0
    stream = hashlib.sha256()
    i = 0
    while i < len(events):
        event = events[i]
        if event[0] != "scalar":
            require(event[0] in ("climb", "center", "phase", "adapter", "residual_adapter"), "unknown event")
            if event[0] == "climb":
                paid[event[5]] += 1
            if event[0] == "center":
                paid[event[4]] += 1
            stream.update(canonical(event) + b"\n")
            i += 1
            continue
        count = 2 if i in chosen else 1
        group = events[i:i + count]
        require(len(group) == count and all(e[0] == "scalar" and e[2] == event[2] for e in group), "pair frame boundary")
        if count == 2:
            require(J.compatible(*group), "ineligible selected pair")
            word = J.lower_pair(group[0][1], group[1][1])
        else:
            word = lower(event[1])
        touched = {WORK}
        for e in group:
            op = e[1]
            touched.add(tuple(op[1]))
            if op[0] in ("add", "copy"):
                touched.add(tuple(op[2]))
        before = {r: rows[r].copy() for r in touched}
        expected = {r: row.copy() for r, row in before.items()}
        for e in group:
            direct(expected, e[1])
            scalar_macros += 1
            original_count += retained_count(e[1])
        for op in word:
            tag, dst = op[:2]
            require(dst in touched and (len(op) < 3 or op[2] in touched), "undeclared register")
            step(rows, op)
            if tag == "clear":
                envelope[dst] = Q(0)
            elif tag == "copy":
                envelope[dst] = envelope[op[2]]
            elif tag in ("double", "halve", "negate"):
                envelope[dst] *= {"double": Q(2), "halve": Q(1, 2), "negate": Q(1)}[tag]
            else:
                envelope[dst] += envelope[op[2]]
            tags[tag] += 1
            operand_reads += 0 if tag == "clear" else 2 if tag in ("add", "subtract") else 1
            source_reads += int(len(op) == 3 and op[2] != WORK)
            peak = max(peak, sum(map(abs, rows[dst].values()), Q(0)))
            if rows[dst]:
                depth = max(depth, max(x.denominator.bit_length() - 1 for x in rows[dst].values()))
            envelope_peak = max(envelope_peak, envelope[dst])
            stream.update(canonical(["primitive", event[2], op]) + b"\n")
        require(all(rows[r] == expected[r] for r in touched), "group boundary exact map")
        i += count
    for r in range(728):
        expected = {r: Q(1)}
        if r < 112:
            expected[r + 112] = Q(-1)
        require(rows[("L", r)] == expected, "full backward scalar map")
    require(all(not rows[r] for r in regs if r[0] != "L"), "dirty private input not erased")
    require(envelope_peak < 2**192, "retained local magnitude allowance")
    return {"real_primitives": 2*sum(tags.values()), "real_primitive_tags": {k: 2*v for k,v in sorted(tags.items())},
            "real_operand_reads": 2*operand_reads, "real_nonwork_source_reads": 2*source_reads,
            "primitive_stream_sha256": stream.hexdigest(), "all_formal_columns": len(regs),
            "scalar_macros_charged": scalar_macros, "retained_horner_real_primitives": 2*original_count,
            "paid_profile": {str(k): v for k, v in sorted(paid.items())},
            "scalar_prefix_row_l1": str(peak), "scalar_fractional_depth": depth,
            "positive_envelope_peak": str(envelope_peak), "retained_payload_bits": 192}


def controls(events, selected):
    index = selected[29 % len(selected)]
    a, b = (e[1] for e in events[index:index + 2])
    word = J.lower_pair(a, b)
    rejected = []
    for k in range(len(word)):
        try:
            check_pair(a, b, word[:k] + word[k+1:])
        except ValueError:
            rejected.append("delete_primitive_" + str(k))
        else:
            raise ValueError("accepted missing primitive")
    sign_index = next(i for i, x in enumerate(word) if x[0] in ("add", "subtract"))
    bad = word.copy()
    old = bad[sign_index]
    bad[sign_index] = ("subtract" if old[0] == "add" else "add", *old[1:])
    try:
        check_pair(a, b, bad)
    except ValueError:
        rejected.append("wrong_source_sign")
    else:
        raise ValueError("accepted sign mutation")
    for label, edit in (("wrong_frame", lambda x: x.__setitem__(2, x[2]+1)),
                        ("cross_non_scalar", lambda x: x.__setitem__(0, "phase"))):
        ev = json.loads(json.dumps(events[index:index+2]))
        edit(ev[1])
        require(not J.compatible(*ev), "accepted frame/boundary mutation")
        rejected.append(label)
    for label, q in (("nondyadic", [1, 3]), ("zero", [0, 1])):
        invalid = list(a)
        invalid[3:] = q
        try:
            J.lower_pair(invalid, b)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("accepted invalid coefficient")
    bad = list(b)
    bad[2] = a[2]
    try:
        J.lower_pair(a, bad)
    except ValueError:
        rejected.append("aliased_sources")
    else:
        raise ValueError("accepted source alias")
    # An endpoint-equivalent overpriced word must be caught by the cost gate.
    inflated = word + [("clear", WORK)] * 10
    check_pair(a, b, inflated)
    try:
        check_pair_cost(a, b, inflated)
    except ValueError as error:
        require(str(error) == "joint primitive cost", "wrong cost rejection")
        rejected.append("endpoint_neutral_cost_inflation")
    else:
        raise ValueError("accepted cost inflation")
    return {"event": index, "rejected": rejected}


def verify():
    programs, checks, lower = inputs()
    events = programs["backward"]
    census, selected, scores = J.plan(events, lower)
    require(selected, "no useful candidate")
    for row in census:
        i = row["event"]
        a, b = events[i][1], events[i+1][1]
        word = J.lower_pair(a, b)
        check_pair(a, b, word)
        check_pair_cost(a, b, word)
    baseline = replay(events, lower)
    candidate = replay(events, lower, selected)
    require(baseline["retained_horner_real_primitives"] == checks["backward"]["real_component_primitive_bound"], "retained bill")
    for receipt in (baseline, candidate):
        require(receipt["scalar_macros_charged"] == checks["backward"]["scalar_macros"], "macro accounting")
        require(receipt["paid_profile"] == checks["backward"]["paid_profile"], "recursive profile")
    require(baseline["real_primitives"]-candidate["real_primitives"] == 2*scores[0], "complete primitive saving")
    require(candidate["scalar_prefix_row_l1"] == baseline["scalar_prefix_row_l1"], "scalar prefix maximum changed")
    require(candidate["scalar_fractional_depth"] == baseline["scalar_fractional_depth"], "scalar grid changed")
    require(candidate["positive_envelope_peak"] == baseline["positive_envelope_peak"], "positive envelope changed")
    require(candidate["real_nonwork_source_reads"] == baseline["real_nonwork_source_reads"], "source-read bill changed")
    fcount = 2*sum(len(lower(e[1])) for e in programs["forward"] if e[0] == "scalar")
    contract = json.loads((ROOT / "research/gauge44-frames-x/data/SPEC.json").read_text())["providers"]["gauge44"]["complete_contract"]
    children = sum(map(int, checks["backward"]["paid_profile"].values()))
    adapters = 16*(checks["backward"]["scalar_macros"]+children+728+8)+64*73
    compiler = 64*74**3
    require(adapters == contract["local_adapters"] and compiler == contract["compiler"], "inherited adapter formula")
    before = max(fcount,baseline["real_primitives"])
    after = max(fcount,candidate["real_primitives"])
    non_scalar = [e for e in events if e[0] != "scalar"]
    return {"status": "PASS_X4_JOINT_HORNER", "orientation": "backward", "candidates": len(census),
            "profitable_candidates": sum(x["saving"] > 1 for x in census),
            "census_sha256": sha(canonical(census)), "selected_events": selected,
            "selected_pairs": len(selected), "dp_sha256": sha(canonical(scores)),
            "saving_real_primitives": 2*scores[0], "baseline": baseline, "candidate": candidate,
            "unchanged_forward_pr696_primitives": fcount,
            "orientation_maximum_before": before, "orientation_maximum_after": after,
            "conservative_local_recount": {"adapters_retained": adapters,"compiler": compiler,
                "before":before+adapters*compiler,"after":after+adapters*compiler,
                "saving":before-after,"scope":"arithmetic recount only; no global invoice admission"},
            "unchanged_non_scalar_events":len(non_scalar),"non_scalar_events_sha256":sha(canonical(non_scalar)),
            "controls": controls(events, selected), "scope": "finite scalar construction; no new kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt exclusively")
    args = parser.parse_args()
    result = verify()
    if args.write:
        with args.write.open("x") as out:
            out.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((HERE / "EXPECTED.json").read_text())
        require(canonical(result) == canonical(expected), "frozen receipt mismatch")
    print(f"PASS_X4_JOINT_HORNER candidates={result['candidates']} pairs={result['selected_pairs']} "
          f"saved={result['saving_real_primitives']} columns=737 no_new_kappa")


if __name__ == "__main__":
    main()
