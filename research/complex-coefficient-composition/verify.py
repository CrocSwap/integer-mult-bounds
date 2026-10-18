"""Source-bound exact primitive replay; Python 3.11+, standard library only.

Prepared for Gareth Davidson (@bitplane) with substantial OpenAI Codex
assistance. Apache-2.0. No production verifier or selected artifact is changed.
"""

import argparse
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDERS = "research/community-k492-audit/pr626/replay/mixed-global/base/providers"
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"
WORK = ("W", 0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def payload(path):
    raw = path.read_bytes()
    return gzip.decompress(raw) if path.suffix == ".gz" else raw


def read(path):
    return json.loads(payload(path))


def source_check(root=ROOT):
    pins = read(HERE / "SOURCE-PINS.json")
    for item in pins["files"]:
        path = root / item["path"]
        data = payload(path) if item["encoding"] == "gzip-payload" else path.read_bytes()
        need(hashlib.sha256(data).hexdigest() == item["sha256"], "source hash: " + item["path"])
    prior = (HERE / "vendor" / "pr696_lower.py").read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(prior)).encode() + b"\0" + prior).hexdigest()
    need(git_blob == pins["pr696_lower_git_blob"], "PR696 reference bytes changed")
    selected = read(root / "certificates/selected-result.json")
    need(selected["audited_source_head"] == pins["selected_pr626_head"], "selected source head mismatch")
    manifest = read(root / selected["source_manifest"])
    need(manifest["files"][SPEC] == hashlib.sha256((root / SPEC).read_bytes()).hexdigest(),
         "selected source manifest does not bind SPEC")
    return pins


def load_lower():
    spec = importlib.util.spec_from_file_location("signed_horner_lower", HERE / "lower.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def plus(left, right, q):
    result = dict(left)
    for k, value in right.items():
        value = result.get(k, Q(0)) + q * value
        if value:
            result[k] = value
        else:
            result.pop(k, None)
    return result


def primitive(step, rows, norms):
    """Interpret a primitive, propagating a cancellation-free triangle bound."""
    tag, target = step[:2]
    if tag == "clear":
        rows[target], norms[target] = {}, Q(0)
    elif tag == "copy":
        source = step[2]
        rows[target], norms[target] = dict(rows[source]), norms[source]
    elif tag in ("double", "halve", "negate"):
        factor = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
        rows[target] = {k: factor * value for k, value in rows[target].items()}
        norms[target] *= abs(factor)
    elif tag in ("add", "subtract"):
        source = step[2]
        rows[target] = plus(rows[target], rows[source], Q(1 if tag == "add" else -1))
        norms[target] += norms[source]
    else:
        raise ValueError("unknown primitive: " + tag)
    return norms[target]


def macro_row(op, rows):
    tag, target = op[0], tuple(op[1])
    if tag == "clear":
        return {}
    if tag == "copy":
        return dict(rows[tuple(op[2])])
    if tag == "scale":
        return {k: Q(op[2], op[3]) * v for k, v in rows[target].items()}
    need(tag == "add", "unknown scalar macro")
    return plus(rows[target], rows[tuple(op[2])], Q(op[3], op[4]))


def selected_cost(op):
    """Independent recount of the selected emitter's real-component bill."""
    tag = op[0]
    if tag in ("clear", "copy"):
        return 1
    q = Q(op[3], op[4]) if tag == "add" else Q(op[2], op[3])
    a, b = abs(q.numerator), q.denominator
    if tag == "scale":
        return abs(a.bit_length() - b.bit_length()) + int(q < 0)
    return 3 + (a.bit_length() - 1) + a.bit_count() + (b.bit_length() - 1)


def coefficient_check(q, chain, budget):
    """Three independent input columns: target, source, arbitrary old work."""
    target, source = ("T", 0), ("S", 0)
    rows = {target: {0: Q(1)}, source: {1: Q(1)}, WORK: {2: Q(1)}}
    norms = dict.fromkeys(rows, Q(1))
    peak = Q(1)
    need(len(chain) <= budget, "coefficient cost increased")
    for step in chain:
        need(step[1] in (target, WORK), "coefficient circuit writes source/foreign register")
        need(len(step) == 2 or step[2] in rows, "foreign primitive source")
        peak = max(peak, primitive(step, rows, norms))
    need(rows[target] == {0: Q(1), 1: q}, "wrong coefficient endpoint")
    need(rows[source] == {1: Q(1)}, "source changed")
    need(rows[WORK] == {}, "coefficient work not cleared")
    # Deliberately conservative, and checked from actual primitive prefixes.
    need(peak <= 2 * abs(q.numerator) + 1, "coefficient prefix allowance exceeded")
    return {"coefficient": str(q), "binary": budget, "signed": len(chain),
            "positive_prefix": str(peak), "word_sha256": digest(chain)}


def block_check(events, chain, budget):
    """Exact block map including one independent variable per touched register."""
    registers = sorted({tuple(e[1][i]) for e in events for i in (1, 2)} | {WORK})
    rows = {r: {i: Q(1)} for i, r in enumerate(registers)}
    expected = dict(rows)
    norms = dict.fromkeys(rows, Q(1))
    targets = {tuple(e[1][1]) for e in events}
    for _, op, _ in events:
        expected[tuple(op[1])] = macro_row(op, expected)
    expected[WORK] = {}
    need(len(chain) <= budget, "block cost increased")
    for step in chain:
        need(step[1] in targets | {WORK}, "foreign block write")
        primitive(step, rows, norms)
    need(rows == expected, "block endpoint or scratch clear mismatch")


def negative_controls(lowering):
    op = ["add", ["T", 0], ["S", 0], 31, 8]
    word = lowering.lower(op)
    budget = len(lowering.reference.lower(op))
    controls = []

    def rejects(name, action):
        try:
            action()
        except (ValueError, ZeroDivisionError):
            controls.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    sub = next(i for i, e in enumerate(word) if e[0] == "subtract")
    half = next(i for i, e in enumerate(word) if e[0] == "halve")
    mutations = {
        "wrong_signed_digit": word[:sub] + [("add",) + word[sub][1:]] + word[sub+1:],
        "missing_double": word[:1] + word[2:],
        "missing_halving": word[:half] + word[half+1:],
        "wrong_accumulation_sign": word[:-2] + [("subtract",) + word[-2][1:]] + word[-1:],
        "dirty_work_leak": word[1:],
        "missing_work_clear": word[:-1],
        # 31 has two spare operations versus binary; the neutral excursion
        # preserves the endpoint and meets the budget but violates the peak.
        "endpoint_neutral_prefix_growth": word[:sub] + [("double", WORK), ("halve", WORK)] + word[sub:],
        "cost_inflation": word + [("clear", WORK)] * (budget + 1),
    }
    for name, candidate in mutations.items():
        rejects(name, lambda c=candidate: coefficient_check(Q(31, 8), c, budget))
    for name, bad in [
        ("aliased_data", ["add", ["T", 0], ["T", 0], 31, 8]),
        ("work_as_source", ["add", ["T", 0], list(WORK), 31, 8]),
        ("work_as_target", ["add", list(WORK), ["S", 0], 31, 8]),
        ("odd_denominator", ["add", ["T", 0], ["S", 0], 31, 3]),
        ("zero_coefficient", ["add", ["T", 0], ["S", 0], 0, 1]),
    ]:
        rejects(name, lambda o=bad: lowering.lower(o))
    a = ["scalar", ["add", ["T", 0], ["S", 0], 31, 8], 1]
    b = ["scalar", ["add", ["T", 1], ["S", 0], -31, 8], 1]
    shared = lowering.lower_block([a, b])
    budget = sum(len(lowering.lower(e[1])) for e in (a, b))
    block_check([a, b], shared, budget)
    for name, bad in [
        ("shared_missing_target_read", shared[:-3] + shared[-2:]),
        ("shared_missing_final_clear", shared[:-1]),
        ("shared_wrong_second_sign", shared[:-2] + [("add",) + shared[-2][1:]] + shared[-1:]),
    ]:
        rejects(name, lambda c=bad: block_check([a, b], c, budget))
    for name, bad in [
        ("sharing_across_frame_change", [a, ["scalar", b[1], 0]]),
        ("sharing_across_child", [a, ["climb", "full_frame_cleanup", 0, 0, 1, 9], b]),
        ("sharing_changed_source", [a, ["scalar", ["add", ["T", 1], ["S", 1], 31, 8], 1]]),
        ("sharing_changed_magnitude", [a, ["scalar", ["add", ["T", 1], ["S", 0], 15, 8], 1]]),
        ("sharing_source_write", [a, ["scalar", ["add", ["S", 0], ["S", 0], 31, 8], 1]]),
    ]:
        rejects(name, lambda es=bad: lowering.lower_block(es))
    return controls


def replay(events, canonical, provider_spec, orientation, lowering):
    n = 2 * canonical["v"] + canonical["R"]
    rows = {("L", i): {i: Q(1)} for i in range(n)}
    for i in range(len(canonical["centers"])):
        rows["C", i] = {n + i: Q(1)}
    rows[WORK] = {n + len(canonical["centers"]): Q(1)}
    norms = dict.fromkeys(rows, Q(1))
    old_norms = dict(norms)
    peak = old_peak = Q(1)
    paid, kinds = Counter(), Counter()
    costs = Counter()
    changed = macros = 0
    stream = hashlib.sha256()
    coefficients = set()
    groups = []
    for index, block in lowering.blocks(events):
        event = block[0]
        if event[0] in ("climb", "center"):
            paid[event[5] if event[0] == "climb" else event[4]] += 1
        if event[0] != "scalar":
            continue
        ops = [e[1] for e in block]
        frame = event[2]
        expected = dict(rows)
        targets = {tuple(op[1]) for op in ops}
        for op in ops:
            target = tuple(op[1])
            expected[target] = macro_row(op, expected)
            binary = lowering.reference.lower(op)
            signed = lowering.lower(op)
            need(len(signed) <= len(binary), "primitive cost regressed")
            changed += signed != binary
            macros += 1
            costs["selected"] += 2 * selected_cost(op)
            costs["pr696"] += 2 * len(binary)
            costs["signed"] += 2 * len(signed)
            if op[0] == "add":
                source, q = tuple(op[2]), Q(op[3], op[4])
                coefficients.add(q)
                old_peak = max(old_peak, abs(q.numerator) * old_norms[source])
                old_norms[target] += abs(q) * old_norms[source]
            elif op[0] == "scale":
                old_norms[target] *= abs(Q(op[2], op[3]))
            elif op[0] == "clear":
                old_norms[target] = Q(0)
            elif op[0] == "copy":
                old_norms[target] = old_norms[tuple(op[2])]
            old_peak = max(old_peak, old_norms[target])
        chain = lowering.lower_block(block)
        shared_binary = lowering.lower_block(block, signed=False)
        costs["pr696_shared"] += 2 * len(shared_binary)
        costs["composed"] += 2 * len(chain)
        # Original cleared-work preparation, shared according to PR722.
        costs["selected_shared"] += 2 * (selected_cost(ops[0]) + len(ops) - 1)
        if len(block) > 1:
            block_check(block, chain, sum(len(lowering.lower(op)) for op in ops))
            need(frame == 1 and all(canonical["final"][r[1]] == 1
                 for op in ops for r in (op[1], op[2])), "sharing touches a non-full register")
            groups.append([index, len(block), ops[0][2], str(abs(Q(*ops[0][-2:]))),
                           2*sum(selected_cost(op) for op in ops), 2*len(shared_binary), 2*len(chain)])
        stream.update(json.dumps([frame, chain], separators=(",", ":")).encode() + b"\n")
        for step in chain:
            need(step[1] in targets | {WORK}, "foreign write in lowered block")
            kinds[step[0]] += 1
            peak = max(peak, primitive(step, rows, norms))
        need(all(rows[target] == expected[target] for target in targets), "scalar block endpoint mismatch")
        if ops[0][0] == "add":
            need(not rows[WORK], "work survives block boundary")
    for i in range(n):
        expected = {i: Q(1)}
        if orientation == "forward" and canonical["v"] <= i < 2 * canonical["v"]:
            expected[i - canonical["v"]] = Q(1)
        elif orientation == "backward" and i < canonical["v"]:
            expected[i + canonical["v"]] = Q(-1)
        need(rows["L", i] == expected, "full dirty-input endpoint mismatch")
    need(all(not row for reg, row in rows.items() if reg[0] != "L"), "private work survives program")
    need(dict(paid) == {int(k): v for k, v in provider_spec["expected_profile"].items()}, "paid profile mismatch")
    prior = provider_spec["expected_local." + orientation]
    need(costs["selected"] == prior["real_component_primitives"], "selected invoice mismatch")
    need(macros == prior["macros"] and len(events) == prior["events"], "macro/event inventory mismatch")
    need(old_peak == Q(prior["prefix_l1"]), "selected prefix recount mismatch")
    need(peak < 2**192, "192-bit local prefix allowance exceeded")
    return {
        "events": len(events), "macros": macros, "changed_macros": changed,
        "all_exact_input_columns": len(rows), "logical_input_columns": n,
        "dirty_helper_columns": canonical["R"], "private_input_columns": len(rows) - n,
        "real_component_primitives": dict(costs),
        "saved_beyond_pr696": costs["pr696"] - costs["signed"],
        "saved_by_sharing_after_signed": costs["signed"] - costs["composed"],
        "saved_total": costs["selected"] - costs["composed"],
        "naive_additive_overstatement": costs["selected"] - costs["selected_shared"] -
                                       (costs["signed"] - costs["composed"]),
        "sharing_groups": groups,
        "sharing_group_fields": ["event_index", "length", "source", "absolute_coefficient",
                                 "selected_real_cost", "copy_binary_shared_real_cost", "composed_real_cost"],
        "primitive_kinds_per_real_component": dict(sorted(kinds.items())),
        "selected_positive_prefix": str(old_peak), "composed_positive_prefix": str(peak),
        "composed_prefix_bits": peak.numerator.bit_length() - peak.denominator.bit_length() + 1,
        "charged_payload_bits": 192, "paid_profile": {str(k): v for k, v in sorted(paid.items())},
        "lowered_stream_sha256": stream.hexdigest(),
        "all_dirty_helpers_restored": True, "private_work_cleared": True,
    }, coefficients


def verify(root=ROOT):
    pins = source_check(root)
    lowering = load_lower()
    spec = read(root / SPEC)
    programs, coefficients = {}, set()
    for provider in ("ck", "jp8"):
        directory = root / PROVIDERS / provider
        for name in ("LOCAL-PROGRAMS.json.gz", "CANONICAL-WORD.json.gz"):
            need(hashlib.sha256(payload(directory / name)).hexdigest() ==
                 spec["providers"][provider]["artifact_semantic_sha256"][name], "selected SPEC binding: " + name)
        canonical = read(directory / "CANONICAL-WORD.json.gz")
        for orientation, events in sorted(read(directory / "LOCAL-PROGRAMS.json.gz").items()):
            need(digest(events) == spec["providers"][provider]["program_hashes"][orientation], "selected event digest")
            result, qs = replay(events, canonical, spec["providers"][provider], orientation, lowering)
            programs[provider + "/" + orientation] = result
            coefficients.update(qs)
    certificates = []
    for q in sorted(coefficients):
        op = ["add", ["T", 0], ["S", 0], q.numerator, q.denominator]
        certificates.append(coefficient_check(q, lowering.lower(op), len(lowering.reference.lower(op))))
    return {"status": "finite scalar circuit improvement; no new kappa",
            "base_commit": pins["base_commit"], "programs": programs,
            "coefficient_certificates": certificates,
            "negative_controls": negative_controls(lowering)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new certificate; destination must not exist")
    args = parser.parse_args()
    if args.write:
        need(not args.write.exists(), "output already exists")
    result = verify()
    if args.write:
        with args.write.open("x") as out:
            json.dump(result, out, indent=2, sort_keys=True)
            out.write("\n")
    else:
        need(result == read(HERE / "EXPECTED.json"), "certificate mismatch")
    savings = [result["programs"][p]["saved_total"] for p in
               ("ck/forward", "ck/backward", "jp8/forward", "jp8/backward")]
    print("PASS_COMPLEX_COEFFICIENT_COMPOSITION programs=4 logical_columns=716 coefficients=" +
          str(len(result["coefficient_certificates"])) + " savings=" +
          ",".join(map(str, savings)) + " controls=" + str(len(result["negative_controls"])))


if __name__ == "__main__":
    main()
