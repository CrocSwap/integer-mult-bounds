#!/usr/bin/env python3
"""Compose four reviewed R439 blocks and replay all 16 subsets. No new kappa.

Prepared for woklerx with substantial OpenAI Codex assistance. Apache-2.0.
Uses the pinned PR880 record interpreter and PR589 interface checker;
check_blocks.py independently verifies the local and combined block maps.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "407d52ff15b2217b6e22bce44728b4c3907b6515"
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
AUDITOR = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
HELPERS = "research/r439-block1-schedule/verify.py"
CANDIDATES = [
    "research/r439-block1-schedule/CANDIDATE.json",
    "research/r439-block508-schedule/CERTIFICATE.json",
    "research/r439-frame519-seed02/CANDIDATE.json",
    "research/r439-frame524-seed13/CANDIDATE.json"]
EXECUTION_INPUTS = [WORD, AUDITOR, EXPORTER, HELPERS, *CANDIDATES]
FRAMES = [507, 508, 519, 524]
SAVINGS = {507: 5, 508: 7, 519: 10, 524: 14}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def sources():
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    need(pins["base_commit"] == BASE, "wrong base commit")
    need(pins["execution_inputs"] == EXECUTION_INPUTS, "execution closure changed")
    for name in pins["execution_inputs"] + pins["native_inputs"]:
        need(sha((ROOT / name).read_bytes()) == pins["files"][name]["sha256"],
             "source hash mismatch: " + name)
    return pins


def build(base, blocks, mask):
    need(type(mask) is int and 0 <= mask < 16, "invalid subset mask")
    need(sorted(b["frame"] for b in blocks) == FRAMES, "wrong four-block inventory")
    active = [b for b in blocks if mask & (1 << FRAMES.index(b["frame"]))]
    by_position = sorted(active, key=lambda b: b["start"])
    need(all(a["stop"] <= b["start"] for a, b in zip(by_position, by_position[1:])),
         "overlapping source slices")
    out = copy.deepcopy(base)
    # Original indices remain valid when replaced from right to left.
    for b in reversed(by_position):
        old = base["B"][b["start"]:b["stop"]]
        need(old and all(g[0] == b["frame"] for g in old), "wrong splice location")
        out["B"][b["start"]:b["stop"]] = copy.deepcopy(b["gates"])
    out["C"] = [[1, d, list(ss)] for _, d, ss in reversed(out["A"] + out["B"])
                if not 111 <= d < 222]
    return out


def reject(label, fn, exceptions):
    try:
        fn()
    except exceptions:
        return label
    raise ValueError("negative control accepted: " + label)


def audit_subset(word, base, helper, auditor, geometry, selected):
    need(helper.paths(word) == helper.paths(base), "frame paths changed")
    need(word["C"] == helper.cleanup(word), "nonliteral cleanup")
    for key in base:
        if key not in ("B", "C"):
            need(word[key] == base[key], "unscoped word change: " + key)
    result = helper.audit(word, auditor, geometry)
    need(result["columns"] == 661, "incomplete dirty-column coverage")
    return result


def export(word, destination, helper):
    word_path = destination.with_suffix(".json")
    word_path.write_text(json.dumps(word, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    result = subprocess.run([sys.executable, "-I", "-B", str(ROOT / EXPORTER),
                             str(word_path), str(destination)],
                            capture_output=True, text=True, encoding="utf-8")
    need(result.returncode == 0, "export failed: " + result.stdout + result.stderr)
    return helper.records_check(destination, word)


def run(output, write_certificate):
    sources()
    independent = module(HERE / "check_blocks.py", "composition_blocks")
    helper = module(ROOT / HELPERS, "pinned_pr880_helpers")
    auditor = module(ROOT / AUDITOR, "pinned_pr589_auditor")
    base = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    blocks = independent.load_blocks(ROOT)
    combined = build(base, blocks, 15)
    block_report = independent.verify_blocks(base, blocks, candidate_b=combined["B"])
    geometry, labels, baseline, h, c, _ = auditor.check(base)
    need(all(h.values()) and all(c.values()), "baseline H1-H5/interface failure")
    receipts = []
    for mask in range(16):
        active = [f for i, f in enumerate(FRAMES) if mask & (1 << i)]
        word = build(base, blocks, mask)
        audited = audit_subset(word, base, helper, auditor, geometry, active)
        name = "original" if mask == 0 else "replacement" if mask == 15 else f"subset-{mask:02d}"
        invoice = export(word, output / name, helper)
        expected = 24305 - 2 * sum(SAVINGS[f] for f in active)
        need(invoice["adds"] == expected, "incorrect complete ADD count")
        if receipts:
            original = receipts[0]["native_records"]
            for key in ("moves", "copies", "erasures", "paid_histogram", "rank_mass"):
                need(invoice[key] == original[key], "paid charge changed: " + key)
            need(all(a <= b for a, b in zip(invoice["positive_prefix"], original["positive_prefix"])),
                 "complete positive prefix exceeds baseline")
        need(invoice["rank_mass"] == 5129 and invoice["copies"] == invoice["erasures"] == 9,
             "incorrect paid profile or copy lifecycle")
        receipts.append({"mask": mask, "frames": active, "columns": audited["columns"],
                         "native_records": invoice, "word_sha256": sha(canonical(word))})
        print(f"subset={mask:02d} frames={active} adds={invoice['adds']} prefix={invoice['positive_prefix']}",
              flush=True)

    # Every cover relation of the subset cube must retain the exact saving and
    # improve (or preserve) the measured complete positive bound.
    cover_edges = 0
    for mask in range(16):
        for i, frame in enumerate(FRAMES):
            if mask & (1 << i):
                continue
            before = receipts[mask]["native_records"]
            after = receipts[mask | (1 << i)]["native_records"]
            need(before["adds"] - after["adds"] == 2 * SAVINGS[frame], "nonadditive saving")
            need(all(a <= b for a, b in zip(after["positive_prefix"], before["positive_prefix"])),
                 "subset cover increases prefix")
            cover_edges += 1
    need(cover_edges == 32, "incomplete subset-cover coverage")

    exceptions = (ValueError, helper.Reject, auditor.Reject)
    controls = []
    wrong = copy.deepcopy(combined)
    wrong["C"] = copy.deepcopy(base["C"])
    # The old inverse still restores the Boolean endpoint; the interface
    # deliberately demands the newly charged literal inverse.
    controls.append(reject("stale baseline cleanup", lambda: audit_subset(
        wrong, base, helper, auditor, geometry, FRAMES), exceptions))
    for frame in FRAMES:
        wrong = copy.deepcopy(combined)
        index = next(i for i, g in enumerate(wrong["B"]) if g[0] == frame)
        wrong["B"].pop(index)
        wrong["C"] = helper.cleanup(wrong)
        controls.append(reject(f"drop frame {frame} gate and rebuild cleanup", lambda: helper.audit(
            wrong, auditor, geometry), exceptions))
    wrong = copy.deepcopy(blocks)
    wrong[0]["start"] += 1
    controls.append(reject("shifted splice source", lambda: independent.verify_blocks(base, wrong), exceptions))
    wrong = copy.deepcopy(combined)
    wrong["D"][0][2].pop()
    controls.append(reject("missing dirty compensation", lambda: helper.audit(
        wrong, auditor, geometry), exceptions))
    wrong = copy.deepcopy(combined)
    index = next(i for i, g in enumerate(wrong["B"]) if g[0] == 507)
    wrong["B"][index][0] = 0
    controls.append(reject("illegal frame after composition", lambda: helper.audit(
        wrong, auditor, geometry), exceptions))
    path = output / "replacement" / "249-records.bin"
    raw = path.read_bytes()
    entries = list(struct.iter_unpack("<6i", raw))
    i = next(i for i, r in enumerate(entries) if r[0] == 1 and r[5] == 4 and r[4] == 507)
    try:
        path.write_bytes(raw[:24*i] + raw[24*(i+1):])
        controls.append(reject("drop literal exported ADD", lambda: helper.records_check(
            path.parent, combined), exceptions))
    finally:
        path.write_bytes(raw)

    report = {"status": "PASS_R439_FOUR_BLOCK_COMPOSITION", "base_commit": BASE,
              "assignment_seed": 1, "frames": FRAMES, "subsets": receipts,
              "subset_cover_edges": cover_edges, "block_maps": block_report,
              "native_records": {"original": receipts[0]["native_records"],
                                 "replacement": receipts[15]["native_records"]},
              "controls_rejected": controls, "columns_per_word": 661,
              "reconstructed_word_sha256": receipts[15]["word_sha256"],
              "kappa_claim": "none; unchanged recursive profile; hosted adoption remains open"}
    target = HERE / "CERTIFICATE.json"
    if write_certificate:
        target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    else:
        need(canonical(report) == canonical(json.loads(target.read_text(encoding="utf-8"))),
             "certificate mismatch")
    print(f"PASS_R439_FOUR_BLOCK_COMPOSITION subsets=16 cover_edges=32 adds=24305->24233 columns=661 controls={len(controls)}")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="fresh output directory (existing destinations refused)")
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        run(args.output.resolve(), args.write_certificate)
    else:
        with tempfile.TemporaryDirectory(prefix="r439-composition-") as tmp:
            run(Path(tmp), args.write_certificate)


if __name__ == "__main__":
    main()
