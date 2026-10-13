"""Exact six-program replay for bidirectional dyadic Horner circuits.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance, Apache-2.0.
Sparse rational replay adapts our PR787 (93ceb65c); no production imports.
"""

import argparse
import gzip
import hashlib
import importlib.util
import json
import tarfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ("W", 0)
OLD_SPEC = "research/complex-k492-owner-repair/data/SPEC.json"
NEW_SPEC = "research/complex-sw4-frame8/data/SPEC.json"
PROVIDERS = "research/community-k492-audit/pr626/replay/mixed-global/base/providers"
ARCHIVE = "research/community-frontier741-audit/composed-replay-evidence.tar.gz"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def payload(path):
    raw = path.read_bytes()
    return gzip.decompress(raw) if path.suffix == ".gz" else raw


def read(path):
    return json.loads(payload(path))


def load_lower():
    spec = importlib.util.spec_from_file_location("direction_lower", HERE / "lower.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_check(root=ROOT):
    pins = read(HERE / "SOURCES.json")
    resolved = {}
    for item in pins["files"]:
        for name in [item["path"]] + item.get("archived_paths", []):
            path = root / name
            if not path.is_file():
                continue
            data = payload(path) if item["encoding"] == "gzip-payload" else path.read_bytes()
            if hashlib.sha256(data).hexdigest() == item["sha256"]:
                resolved[item["path"]] = path
                break
        need(item["path"] in resolved, "source hash: " + item["path"])
    for record, head, spec in [
        ("certificates/checkpoints/k492626.json", pins["pr626_head"], OLD_SPEC),
        ("certificates/selected-result.json", pins["pr741_head"], NEW_SPEC),
    ]:
        selected = read(resolved[record])
        need(selected["audited_source_head"] == head, "record head mismatch")
        manifest = read(root / selected["source_manifest"])
        need(manifest["files"][spec] == hashlib.sha256((root / spec).read_bytes()).hexdigest(),
             "record manifest does not bind SPEC")
    return pins


def inputs(root=ROOT):
    spec = read(root / OLD_SPEC)
    for provider in ("ck", "jp8"):
        directory = root / PROVIDERS / provider
        parts = {n: payload(directory / n) for n in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz")}
        yield provider, spec["providers"][provider], parts
    # No extraction or execution of archive contents. Container metadata is
    # irrelevant; every consumed, decompressed member is bound by the SPEC.
    with tarfile.open(root / ARCHIVE) as archive:
        parts = {}
        for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
            matches = [m for m in archive.getmembers() if m.name == "complex/local/" + name]
            need(len(matches) == 1 and matches[0].isfile(), "ambiguous archive member")
            parts[name] = gzip.decompress(archive.extractfile(matches[0]).read())
    yield "sw4", read(root / NEW_SPEC)["providers"]["gauge44"], parts


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
    """Sparse exact rows plus cancellation-free positive prefix bounds."""
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


def original_cost(op):
    """Independent recount of the inherited clear/add binary invoice."""
    if op[0] in ("clear", "copy"):
        return 1
    q = Q(op[3], op[4]) if op[0] == "add" else Q(op[2], op[3])
    a, b = abs(q.numerator), q.denominator
    if op[0] == "scale":
        return abs(a.bit_length() - b.bit_length()) + int(q < 0)
    return 3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1


def coefficient_check(q, chain, budget, prefix_limit=None):
    """Check three arbitrary inputs, source immutability, work erasure and cost."""
    target, source = ("T", 0), ("S", 0)
    rows = {target: {0: Q(1)}, source: {1: Q(1)}, WORK: {2: Q(1)}}
    norms = dict.fromkeys(rows, Q(1))
    peak = Q(1)
    need(len(chain) <= budget, "coefficient cost increased")
    for step in chain:
        need(step[1] in (target, WORK), "source/foreign register write")
        need(len(step) == 2 or step[2] in rows, "foreign primitive source")
        peak = max(peak, primitive(step, rows, norms))
    need(rows[target] == {0: Q(1), 1: q}, "wrong coefficient endpoint")
    need(rows[source] == {1: Q(1)}, "source changed")
    need(rows[WORK] == {}, "coefficient work not cleared")
    if prefix_limit is not None:
        need(peak <= prefix_limit, "coefficient prefix exceeded")
    return str(peak)


def replay(events, word, spec, orientation, lowering):
    n = 2 * word["v"] + word["R"]
    rows = {("L", i): {i: Q(1)} for i in range(n)}
    for i in range(len(word["centers"])):
        rows["C", i] = {n + i: Q(1)}
    rows[WORK] = {n + len(word["centers"]): Q(1)}
    norms = dict.fromkeys(rows, Q(1))
    old_norms = dict(norms)
    peak = old_peak = Q(1)
    paid, kinds, costs, chosen = Counter(), Counter(), Counter(), Counter()
    changed = macros = 0
    stream = hashlib.sha256()
    coefficients = Counter()
    for event in events:
        if event[0] in ("climb", "center"):
            paid[event[5] if event[0] == "climb" else event[4]] += 1
        if event[0] != "scalar":
            continue
        _, op, frame = event
        target = tuple(op[1])
        expected = macro_row(op, rows)
        binary = lowering.reference.lower(op)
        forward = lowering.choose(op, reverse=False)[1]
        name, chain = lowering.choose(op)
        need(len(chain) <= len(forward) <= len(binary), "cost regression")
        changed += len(chain) < len(forward)
        chosen[name] += 1
        macros += 1
        costs["original"] += 2 * original_cost(op)
        costs["copy_binary"] += 2 * len(binary)
        costs["forward_best"] += 2 * len(forward)
        costs["bidirectional"] += 2 * len(chain)
        if op[0] == "add":
            source, q = tuple(op[2]), Q(op[3], op[4])
            coefficients[q] += 1
            old_peak = max(old_peak, abs(q.numerator) * old_norms[source])
            old_norms[target] += abs(q) * old_norms[source]
        elif op[0] == "scale":
            old_norms[target] *= abs(Q(op[2], op[3]))
        elif op[0] == "clear":
            old_norms[target] = Q(0)
        elif op[0] == "copy":
            old_norms[target] = old_norms[tuple(op[2])]
        old_peak = max(old_peak, old_norms[target])
        stream.update(canonical([frame, chain]).encode() + b"\n")
        for step in chain:
            need(step[1] in (target, WORK), "foreign write")
            kinds[step[0]] += 1
            peak = max(peak, primitive(step, rows, norms))
        need(rows[target] == expected, "scalar macro endpoint mismatch")
        if op[0] == "add":
            need(not rows[WORK], "work survives macro boundary")
    for i in range(n):
        expected = {i: Q(1)}
        if orientation == "forward" and word["v"] <= i < 2 * word["v"]:
            expected[i - word["v"]] = Q(1)
        elif orientation == "backward" and i < word["v"]:
            expected[i + word["v"]] = Q(-1)
        need(rows["L", i] == expected, "full arbitrary-input endpoint mismatch")
    need(all(not row for reg, row in rows.items() if reg[0] != "L"), "private stream survives")
    need(dict(paid) == {int(k): v for k, v in spec["expected_profile"].items()}, "paid profile mismatch")
    prior = spec["expected_local"][orientation] if "expected_local" in spec else spec["expected_local." + orientation]
    need(costs["original"] == prior["real_component_primitives"], "original invoice mismatch")
    need(macros == prior["macros"] and len(events) == prior["events"], "event/macro count mismatch")
    need(old_peak == Q(prior["prefix_l1"]), "original prefix mismatch")
    need(peak < 2**192, "192-bit local prefix allowance exceeded")
    return {
        "events": len(events), "macros": macros, "improved_by_reverse": changed,
        "logical_columns": n, "private_columns": len(rows) - n,
        "dirty_helpers_restored": word["R"], "private_streams_cleared": True,
        "real_primitives": dict(costs), "saved_beyond_forward": costs["forward_best"] - costs["bidirectional"],
        "chosen_methods": dict(chosen), "primitive_kinds_per_real_component": dict(kinds),
        "original_positive_prefix": str(old_peak), "new_positive_prefix": str(peak),
        "new_prefix_bits": peak.numerator.bit_length() - peak.denominator.bit_length() + 1,
        "charged_payload_bits": 192, "paid_profile": {str(k): v for k, v in sorted(paid.items())},
        "lowered_stream_sha256": stream.hexdigest(),
        "coefficient_occurrences": {str(q): count for q, count in sorted(coefficients.items())},
    }, set(coefficients)


def negative_controls(lowering):
    controls = []

    def rejects(name, action):
        try:
            action()
        except (ValueError, ZeroDivisionError):
            controls.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    op = ["add", ["T", 0], ["S", 0], 3, 4]
    word = lowering.lower(op)
    budget = len(lowering.choose(op, reverse=False)[1])
    peak = Q(coefficient_check(Q(3, 4), word, budget))
    for name, mutant in {
        "missing_initial_copy": word[1:],
        "missing_first_half": word[:1] + word[2:],
        "wrong_reverse_digit": word[:2] + [("subtract", WORK, ("S", 0))] + word[3:],
        "wrong_target_sign": word[:-2] + [("subtract", ("T", 0), WORK)] + word[-1:],
        "missing_final_clear": word[:-1],
        "source_write": word + [("clear", ("S", 0))],
        "cost_understatement": word,
        "endpoint_neutral_prefix_growth": word[:1] + [("double", WORK), ("halve", WORK)] + word[1:],
    }.items():
        # The excursion gets enough cost budget, isolating the prefix check.
        cap = len(mutant) if name == "endpoint_neutral_prefix_growth" else budget
        if name == "cost_understatement":
            cap = len(word) - 1
        rejects(name, lambda w=mutant, b=cap: coefficient_check(Q(3, 4), w, b, peak))
    # For 11/8 the reverse NAF starts with -1. Omitting its sign correction
    # gives -11/8 even though the positive binary example above still passes.
    signed_op = ["add", ["T", 0], ["S", 0], 11, 8]
    signed = lowering.candidates(signed_op)["naf-reverse"]
    coefficient_check(Q(11, 8), signed, len(signed))
    mutant = signed[:-2] + [("add", ("T", 0), WORK)] + signed[-1:]
    rejects("reverse_naf_initial_sign", lambda: coefficient_check(Q(11, 8), mutant, len(mutant)))
    for name, bad in [
        ("aliased_data", ["add", ["T", 0], ["T", 0], 3, 4]),
        ("work_as_source", ["add", ["T", 0], list(WORK), 3, 4]),
        ("work_as_target", ["add", list(WORK), ["S", 0], 3, 4]),
        ("non_dyadic", ["add", ["T", 0], ["S", 0], 3, 5]),
        ("zero_coefficient", ["add", ["T", 0], ["S", 0], 0, 1]),
    ]:
        rejects(name, lambda o=bad: lowering.lower(o))
    return controls


def verify(root=ROOT):
    pins = source_check(root)
    lowering = load_lower()
    programs, coefficients = {}, set()
    for provider, spec, parts in inputs(root):
        for name, raw in parts.items():
            need(hashlib.sha256(raw).hexdigest() == spec["artifact_semantic_sha256"][name],
                 "SPEC payload binding: " + provider + "/" + name)
        word = json.loads(parts["CANONICAL-WORD.json.gz"])
        for orientation, events in sorted(json.loads(parts["LOCAL-PROGRAMS.json.gz"]).items()):
            need(digest(events) == spec["program_hashes"][orientation], "event hash mismatch")
            result, qs = replay(events, word, spec, orientation, lowering)
            programs[provider + "/" + orientation] = result
            coefficients.update(qs)
    certificates = []
    for q in sorted(coefficients):
        op = ["add", ["T", 0], ["S", 0], q.numerator, q.denominator]
        words = lowering.candidates(op)
        peaks = {k: coefficient_check(q, v, len(v)) for k, v in words.items()}
        name, chosen = lowering.choose(op)
        certificates.append({"coefficient": str(q), "chosen": name,
                             "costs": {k: len(v) for k, v in words.items()}, "positive_prefixes": peaks,
                             "word_sha256": digest(chosen)})
    return {"status": "finite coefficient circuit construction; no new kappa",
            "base_commit": pins["base_commit"], "programs": programs,
            "coefficient_certificates": certificates, "negative_controls": negative_controls(lowering)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write verified receipt; destination must not exist")
    args = parser.parse_args()
    if args.write:
        need(not args.write.exists(), "output already exists")
    result = verify()
    if args.write:
        with args.write.open("x") as out:
            json.dump(result, out, indent=2, sort_keys=True)
            out.write("\n")
    else:
        need(canonical(result) == canonical(read(HERE / "EXPECTED.json")), "certificate mismatch")
    savings = [result["programs"][p + "/forward"]["saved_beyond_forward"] for p in ("ck", "jp8", "sw4")]
    print("PASS_DYADIC_HORNER_DIRECTION programs=6 coefficients=" + str(len(result["coefficient_certificates"])) +
          " extra_saved_per_orientation=" + ",".join(map(str, savings)) +
          " controls=" + str(len(result["negative_controls"])) + " kappa=unchanged")


if __name__ == "__main__":
    main()
