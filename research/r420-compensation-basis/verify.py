#!/usr/bin/env python3
"""R420 dirty-compensation basis factoring. Apache-2.0.

Prepared by Greer Guthrie with substantial OpenAI Codex assistance.
Finite circuit evidence, with an explicit semantic D-prefix contract; no new kappa.
"""

import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
BASE = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
WORD = "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
XCHECK = "research/e8-bit-r420/code/xcheck.py"
BIT = "research/e8-bit-carrier-skeleton/code/bit"
SEED = 12
STATUS = "PASS_R420_COMPENSATION_BASIS"


class Reject(Exception):
    pass


def need(ok, why):
    if not ok:
        raise Reject(why)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def source_check(root):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    need(pins["base_commit"] == BASE, "source base changed")
    for name, pin in pins["files"].items():
        data = (root / name).read_bytes()
        if pin["representation"] == "gzip-payload":
            data = gzip.decompress(data)
        else:
            need(pin["representation"] == "file-bytes", "unknown pin representation")
        need(hashlib.sha256(data).hexdigest() == pin["sha256"], "source pin mismatch: " + name)


def columns(word):
    v, count = word["v"], word["R"]
    out = [0] * count
    for frame, target, inputs in word["D"]:
        need(frame == 0 and v <= target < 2 * v, "noncanonical baseline D")
        for register in inputs:
            need(2 * v <= register < 2 * v + count, "baseline D reads a non-helper")
            out[register - 2 * v] ^= 1 << (target - v)
    return out


def nominate(word):
    """One exhaustive pair-score pass, then one seeded greedy disjoint matching."""
    col = columns(word)
    rng = random.Random(SEED)
    candidates = []
    for a in range(len(col)):
        for b in range(a + 1, len(col)):
            changed = (col[a] ^ col[b]).bit_count()
            ab = col[b].bit_count() - changed - 2
            ba = col[a].bit_count() - changed - 2
            gain = max(ab, ba)
            if gain > 0:
                dst, src = (a, b) if ab >= ba else (b, a)
                candidates.append((-gain, rng.getrandbits(64), dst, src))
    used = set()
    pairs = []
    for negative_gain, _, dst, src in sorted(candidates):
        if dst in used or src in used:
            continue
        used.update((dst, src))
        pairs.append({"dst": dst + 2 * word["v"], "src": src + 2 * word["v"],
                      "net_saved_additions": -negative_gain})
    return {"seed": SEED, "unordered_pairs_scored": len(col) * (len(col) - 1) // 2,
            "orientations_per_pair": 2, "positive_pair_candidates": len(candidates),
            "pairs": pairs, "stopping_rule": "one score enumeration and one greedy matching",
            "optimality_claim": False}


def build(word, recipe):
    v, count = word["v"], word["R"]
    encoded = columns(word)
    used = set()
    prefix = []
    for pair in recipe["pairs"]:
        a, b = pair["dst"], pair["src"]
        need(2 * v <= a < 2 * v + count and 2 * v <= b < 2 * v + count and a != b,
             "basis operation does not use distinct helpers")
        need(a not in used and b not in used, "basis pairs are not disjoint")
        used.update((a, b))
        prefix.append([0, a, [b]])
        encoded[b - 2 * v] ^= encoded[a - 2 * v]
    reads = [[0, v + t, [2 * v + h for h, mask in enumerate(encoded) if mask >> t & 1]]
             for t in range(v)]
    need(all(gate[2] for gate in reads), "empty target read")
    result = copy.deepcopy(word)
    result["D"] = prefix + reads + list(reversed(copy.deepcopy(prefix)))
    return result


def gate_count(word, section):
    return sum(len(inputs) for _, _, inputs in word[section])


def d_endpoint_set(word):
    """Set-based all-column replay, separate from the pinned bit-mask checker."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    rows = [{r} for r in range(n)]
    for frame, dst, inputs in word["D"]:
        need(frame == 0 and word["frames"][frame] == [], "D is not at the zero frame")
        need(v <= dst < n and inputs and len({dst, *inputs}) == len(inputs) + 1,
             "invalid D operands")
        need(all(2 * v <= src < n for src in inputs), "D reads a source or target")
        need(all(word["start"][r] == 0 for r in [dst] + inputs), "D has a nonzero start")
        for src in inputs:
            rows[dst].symmetric_difference_update(rows[src])
    return rows


def prefix_contract(before, after):
    need(set(before) == set(after), "word schema changed")
    need(all(before[k] == after[k] for k in before if k != "D"), "change outside D")
    expected = d_endpoint_set(before)
    actual = d_endpoint_set(after)
    need(actual == expected, "D endpoint differs on an independent input column")
    v, n = before["v"], 2 * before["v"] + before["R"]
    need(all(actual[r] == {r} for r in range(n) if not v <= r < 2 * v),
         "D did not restore every source/helper")
    return {"all_columns": n, "dirty_helper_columns": before["R"],
            "all_helpers_restored_before_A": True,
            "target_response_sha256": digest([sorted(row) for row in actual[v:2 * v]])}


def scalar_events(word):
    """Literal scalar ADD/COPY/ERASE stream, independent of the file exporter."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    events = []
    for section in ("D", "A"):
        for _, dst, inputs in word[section]:
            events.extend(("add", dst, src) for src in inputs)
    for k, register in enumerate(word["ret"]):
        events.append(("copy", n, register))
        events.extend(("add", v + target, n) for target, row in enumerate(word["scatter"]) if k in row)
        events.append(("erase", n, register))
    for section in ("B", "C"):
        for _, dst, inputs in word[section]:
            events.extend(("add", dst, src) for src in inputs)
    return events


def interpret(events, v, helpers, reverse=False, positive=False):
    n = 2 * v + helpers
    rows = [1] * (n + 1) if positive else [1 << r for r in range(n)] + [0]
    peak, opened, center, copies = 1, False, None, 0
    stream = reversed(events) if reverse else events
    for kind, dst, src in stream:
        if reverse and kind != "add":
            kind = "erase" if kind == "copy" else "copy"
        if kind == "add":
            need(0 <= dst < n and 0 <= src <= n and dst != src, "bad scalar roles")
            need(src != n or opened, "read unopened copy")
            need(not opened or dst != center, "mutate copied center")
            if positive:
                rows[dst] += rows[src]
                peak = max(peak, rows[dst])
            else:
                rows[dst] ^= rows[src]
        elif kind == "copy":
            need(not opened and dst == n and 0 <= src < n, "invalid COPY")
            rows[n] = rows[src]
            opened, center = True, src
            copies += 1
        elif kind == "erase":
            need(opened and dst == n and src == center, "invalid ERASE")
            rows[n] = 0
            opened, center = False, None
        else:
            raise Reject("unknown scalar event")
    need(not opened and rows[n] == 0, "unclosed temporary")
    if not positive:
        expected = [1 << r for r in range(n)] + [0]
        for t in range(v):
            expected[v + t] ^= 1 << t
        need(rows == expected, "full scalar word does not implement the defining shear")
    return {"copies": copies, "peak": peak} if positive else {"copies": copies, "columns": n}


def frame_paths(word, dimensions):
    """Chronological frame paths; exact containment is checked by pinned Word.full."""
    current = word["start"].copy()
    paths = [[frame] for frame in current]
    paid = Counter()
    for section in ("D", "A", "scatter", "B", "C", "final"):
        if section == "scatter":
            for register in word["ret"]:
                paid[dimensions[current[register]]] += 1
            continue
        gates = ([[frame, r, []] for r, frame in enumerate(word["final"])]
                 if section == "final" else word[section])
        for frame, dst, inputs in gates:
            for register in [dst] + inputs:
                old = current[register]
                if old != frame:
                    rank = dimensions[frame] - dimensions[old]
                    need(rank > 0, "nonincreasing frame path")
                    paid[rank] += 1
                    paths[register].append(frame)
                    current[register] = frame
    return paths, {str(r): count for r, count in sorted(paid.items())}


def word_receipt(word, frames):
    events = scalar_events(word)
    directions = [interpret(events, word["v"], word["R"], reverse=rev) for rev in (False, True)]
    bounds = [interpret(events, word["v"], word["R"], reverse=rev, positive=True)["peak"]
              for rev in (False, True)]
    payload = 64 * bounds[0] ** 3 * bounds[1] ** 2
    need(payload < 1 << 104, "complete signed-prefix budget exceeds 104-bit cap")
    paths, profile = frame_paths(word, frames)
    return {"semantic_word_sha256": digest(word), "scalar_stream_sha256": digest(events),
            "binary_additions": sum(event[0] == "add" for event in events),
            "D_binary_additions": gate_count(word, "D"), "D_grouped_gates": len(word["D"]),
            "forward_and_reverse": directions, "forward_prefix": bounds[0], "reverse_prefix": bounds[1],
            "payload_prefix_upper": str(payload), "payload_prefix_bits": payload.bit_length(),
            "paid_histogram": profile, "rank_mass": sum(int(r) * c for r, c in profile.items()),
            "frame_paths_sha256": digest(paths)}


def controls(before, after):
    results = []
    cases = []
    x = copy.deepcopy(after); x["D"].pop(0); cases.append(("missing compute", x))
    x = copy.deepcopy(after); x["D"].pop(); cases.append(("missing helper restoration", x))
    x = copy.deepcopy(after); x["D"][201][2].pop(); cases.append(("missing recoded target read", x))
    x = copy.deepcopy(after); x["D"].insert(0, copy.deepcopy(x["D"][0])); cases.append(("cancelled compute", x))
    x = copy.deepcopy(after); x["D"][0][0] = 1; cases.append(("nonzero prefix frame", x))
    x = copy.deepcopy(after); x["D"].insert(0, [0, 240, [120]]); x["D"].insert(0, [0, 240, [120]])
    cases.append(("F2-neutral target-fed helper outside the contract", x))
    x = copy.deepcopy(after); x["A"].pop(); cases.append(("unrelated A change", x))
    for name, word in cases:
        try:
            prefix_contract(before, word)
        except Reject as exc:
            results.append({"name": name, "rejected_by": str(exc)})
        else:
            raise Reject("invalid prefix accepted: " + name)
    # A neutral pair is a valid endpoint, but still costs two scalar additions.
    x = copy.deepcopy(after); x["D"].extend([[0, 240, [241]], [0, 240, [241]]])
    prefix_contract(before, x)
    need(gate_count(x, "D") == gate_count(after, "D") + 2, "neutral XOR work was not charged")
    results.append({"name": "neutral pair still charged", "accepted_endpoint": True, "extra_binary_additions": 2})
    return results


def run(command, cwd=None):
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    need(completed.returncode == 0,
         "command failed: " + " ".join(map(str, command)) + "\n" + completed.stdout + completed.stderr)
    return completed


def export_check(root, word, receipt, work):
    word_path = work / "word.json.gz"
    word_path.write_bytes(gzip.compress(canonical(word), mtime=0))
    records = work / "records"
    run([sys.executable, "-I", "-B", str(root / BIT / "export_records.py"), str(word_path), str(records)])
    data = (records / "249-records.bin").read_bytes()
    need(len(data) % 24 == 0, "record alignment")
    exported = []
    paid = Counter()
    for opcode, dst, src, coefficient, frame, phase in struct.iter_unpack("<6i", data):
        if opcode == 0:
            if frame:
                paid[frame] += 1
        elif opcode == 1:
            need(coefficient == 1, "unexpected ADD coefficient")
            exported.append(("add", dst, src))
        elif opcode == 2:
            paid[phase] += 1
            exported.append(("copy", src, dst))
        elif opcode == 3:
            exported.append(("erase", src, dst))
        else:
            raise Reject("unknown record opcode")
    need(exported == scalar_events(word), "exported scalar stream differs from literal word")
    need({str(r): n for r, n in sorted(paid.items())} == receipt["paid_histogram"], "exported paid profile differs")
    receipt["exported_records"] = len(data) // 24
    receipt["record_sha256"] = hashlib.sha256(data).hexdigest()
    return records


def native_checks(root, records, receipt, work, cxx, boost):
    """Compile and run the original C++ admission code without edits."""
    checkers = root / BIT / "checkers"
    include = ["-I" + str(checkers), "-I" + str(root / "research/e8-bit-carrier-skeleton/portable-include")]
    if boost:
        include.append("-I" + str(boost))
    cin, cout = work / "cin", work / "cout"
    run([sys.executable, "-I", "-B", str(root / BIT / "regression/stage_cohort.py"),
         str(records), str(records), str(cin), str(cout)])
    binary = work / "legality"
    run([cxx, "-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", *include,
         str(checkers / "legality_h.cpp"), "-o", str(binary)])
    output = work / "legality.json"
    run([str(binary), str(cin), str(cout), str(output)])
    legality = json.loads(output.read_text())
    need(legality["common_frame_ADDs"] == receipt["binary_additions"] and
         legality["rank_mass"] == receipt["rank_mass"] and legality["copies"] == legality["erasures"] == 9,
         "native legality invoice mismatch")
    result = {"legality": "PASS", "stages": []}
    for pairs in (2, 4, 5):
        binary = work / ("columns_" + str(pairs))
        run([cxx, "-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=120", "-DRHELP=420",
             "-DKPAIRS=" + str(pairs), *include, str(checkers / "columns_k.cpp"), "-o", str(binary)])
        output = work / ("columns_" + str(pairs) + ".json")
        run([str(binary), str(cout / "COHORT249-RECORDS.bin"), str(output)])
        check = json.loads(output.read_text())
        need(check["formal_columns_checked"] == 2 * pairs * 120 + 420, "native formal-column count")
        need(check["local_scalar_additions"] == receipt["binary_additions"] and
             check["payload_prefix_upper"] == receipt["payload_prefix_upper"] and
             check["payload_prefix_bits"] == receipt["payload_prefix_bits"], "native prefix invoice mismatch")
        need(dict(check["local_raw_H"]) == {int(r): c for r, c in receipt["paid_histogram"].items()},
             "native recursive profile mismatch")
        need(len(check["negative_controls"]) == 6 * (pairs - 1) and
             all(z["rejected"] for z in check["negative_controls"]), "native bridge controls failed")
        result["stages"].append({"stages": 2 * pairs + 1, "all_columns": check["formal_columns_checked"],
                                 "bridge_mutations_rejected": len(check["negative_controls"]),
                                 "payload_bits": check["payload_prefix_bits"]})
        # Missing helper restoration is still frame-legal; native columns must catch it.
        raw = (cout / "COHORT249-RECORDS.bin").read_bytes()
        rows = list(struct.iter_unpack("<6i", raw))
        index = max(i for i, e in enumerate(rows) if e[0] == 1 and e[5] == 1 and e[1] >= 240)
        mutant = work / "missing-restoration.bin"
        mutant.write_bytes(b"".join(struct.pack("<6i", *e) for i, e in enumerate(rows) if i != index))
        rejected = subprocess.run([str(binary), str(mutant), str(work / "invalid.json")], capture_output=True, text=True)
        need(rejected.returncode != 0 and "local defining-decoder full formal column" in rejected.stderr,
             "native missing-restoration control not rejected for its endpoint")
    result["missing_restoration_rejected_at_each_stage_count"] = True
    return result


def make_certificate(root, work):
    source_check(root)
    word = json.loads(gzip.decompress((root / WORD).read_bytes()))
    recipe = nominate(word)
    need(recipe == json.loads((HERE / "RECIPE.json").read_text()), "nomination differs from frozen recipe")
    changed = build(word, recipe)
    prefix = prefix_contract(word, changed)
    spec = importlib.util.spec_from_file_location("pinned_r420_xcheck", root / XCHECK)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    W, labels, full, H, C, _ = checker.check(word)
    need(all(H.values()) and all(C.values()), "baseline interleaved interface failed")
    _, labels_new, full_new, new_H, new_C, _ = checker.check(changed)
    need(labels_new == labels and full_new["columns"] == full["columns"] == 660, "native all-column replay failed")
    need([k for k, value in new_H.items() if not value] == ["H2_D_frame0_targets_from_helpers"],
         "unexpected legacy hypothesis failure")
    need([k for k, value in new_C.items() if not value] == ["K_equals_D"], "unexpected legacy conclusion failure")
    before = word_receipt(word, W.fdim)
    after = word_receipt(changed, W.fdim)
    need(before["frame_paths_sha256"] == after["frame_paths_sha256"] and
         before["paid_histogram"] == after["paid_histogram"], "frame/profile change")
    saved = before["D_binary_additions"] - after["D_binary_additions"]
    need(saved == sum(pair["net_saved_additions"] for pair in recipe["pairs"]) > 0,
         "net saving does not include complete compute/uncompute work")
    need(before["binary_additions"] - after["binary_additions"] == saved, "full-word saving mismatch")
    original_dir, changed_dir = work / "original", work / "changed"
    original_dir.mkdir(); changed_dir.mkdir()
    export_check(root, word, before, original_dir)
    records = export_check(root, changed, after, changed_dir)
    certificate = {"schema": "r420-compensation-basis/1", "status": STATUS, "base_commit": BASE,
                   "seed": SEED, "source_pr": 543, "source_pr_head": "2065fe4f72a914d907f1046603f5a36f17018535",
                   "matching_pairs": len(recipe["pairs"]), "touched_helpers": 2 * len(recipe["pairs"]),
                   "before": before, "after": after, "binary_additions_saved": saved,
                   "semantic_prefix_contract": prefix, "legacy_H2_accepts_changed_syntax": False,
                   "legacy_raw_D_column_extraction_accepts_changed_syntax": False,
                   "all_other_legacy_interface_checks_pass": True, "labels": labels,
                   "controls": controls(word, changed),
                   "scope": "Finite circuit improvement; semantic D-prefix substitution is proved separately. No new kappa or hosted-supplier invoice."}
    return certificate, changed, records, changed_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=HERE.parents[1])
    parser.add_argument("--native", action="store_true", help="also compile original C++ legality and 5/9/11-stage checks")
    parser.add_argument("--cxx", default="c++")
    parser.add_argument("--boost-include", type=Path)
    parser.add_argument("--output", type=Path, help="write a new directory containing the rebuilt word and verified receipts")
    args = parser.parse_args()
    need(args.output is None or not args.output.exists(), "output directory already exists")
    root = args.repo_root.resolve()
    with tempfile.TemporaryDirectory(prefix="r420-compensation-") as tmp:
        certificate, word, records, native_work = make_certificate(root, Path(tmp))
        need(certificate == json.loads((HERE / "CERTIFICATE.json").read_text()), "certificate differs from exact replay")
        native = native_checks(root, records, certificate["after"], native_work, args.cxx, args.boost_include) if args.native else None
        if args.output:
            args.output.mkdir(parents=True)
            (args.output / "word.json.gz").write_bytes(gzip.compress(canonical(word), mtime=0))
            (args.output / "certificate.json").write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
            if native:
                (args.output / "native.json").write_text(json.dumps(native, indent=2, sort_keys=True) + "\n")
        print(STATUS + " D=19922->12988 native_ADDs=26916->19982 saved=6934 rank_mass=5112 payload_bits=102<104")
        if native:
            print("PASS_NATIVE_LEGALITY_AND_5_9_11_STAGE_COLUMNS " + json.dumps(native, sort_keys=True))


if __name__ == "__main__":
    main()
