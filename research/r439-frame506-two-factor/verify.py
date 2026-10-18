#!/usr/bin/env python3
"""Exact finite frame-506 experiment. Adapted for Eva Ayala with substantial Codex assistance from Ross Richardson PR914.

Apache-2.0. No search implementation is imported by this verifier.
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
from collections import Counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECK = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORT = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sources():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for name, expected in pins["sha256"].items():
        need(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected,
             "source mismatch: " + name)
    selected = json.loads((ROOT / "research/community-frontier942-audit/SELECTED-SOURCE.json").read_text())
    need(selected["files"][WORD] == pins["sha256"][WORD], "selected supplier binding mismatch")
    return pins


def candidate(word, recipe):
    out = copy.deepcopy(word)
    need(recipe["source_range"] == [102, 128], "wrong source range")
    need(all(g[0] == 506 for g in word["B"][102:128]), "wrong source block")
    gates = recipe["candidate_gates"]
    regs = sorted({r for f, d, ss in word["B"][102:128] for r in [d, *ss]})
    need(recipe["registers"] == regs, "wrong registers")
    need(all(f == 506 and len(ss) == 1 and d != ss[0] and d in regs and ss[0] in regs
             for f, d, ss in gates), "bad candidate gate")
    out["B"][102:128] = copy.deepcopy(gates)
    full = next(i for i, f in enumerate(out["frames"]) if len(f) == out["v"])
    z = [g for g in out["A"] + out["B"] if not out["v"] <= g[1] < 2 * out["v"]]
    out["C"] = [[full, d, list(ss)] for f, d, ss in reversed(z)]
    return out


def integer_map(gates, regs, reverse=False):
    positions = {r: i for i, r in enumerate(regs)}
    rows = [[int(i == j) for j in range(len(regs))] for i in range(len(regs))]
    for f, d, ss in reversed(gates) if reverse else gates:
        for s in ss:
            a, b = positions[d], positions[s]
            rows[a] = [x + y for x, y in zip(rows[a], rows[b])]
    return rows


def boolean_check(old, new, regs):
    # A truth-table interpreter, separate from the matrix calculation.
    pos = {r: i for i, r in enumerate(regs)}
    for bits in range(1 << len(regs)):
        outputs = []
        for gates in (old, new):
            values = [(bits >> i) & 1 for i in range(len(regs))]
            for f, d, ss in gates:
                for s in ss:
                    values[pos[d]] ^= values[pos[s]]
            outputs.append(values)
        need(outputs[0] == outputs[1], "truth-table disagreement")
    return 1 << len(regs)


def emit(word, dim):
    """Separately interpret the export contract, including actual COPY/ERASE."""
    v = word["v"]
    n = 2 * v + word["R"]
    zero = next(i for i, d in enumerate(dim) if d == 0)
    cur = list(word["start"])
    events = []
    def move(r, f):
        if cur[r] != f:
            events.append((0, r, cur[r], f, dim[f] - dim[cur[r]], 0))
            cur[r] = f
    def section(name, phase):
        for f, d, ss in word[name]:
            for r in [d, *ss]:
                move(r, f)
            for s in ss:
                events.append((1, d, s, 1, f, phase))
    section("D", 1)
    section("A", 2)
    for k, q in enumerate(word["ret"]):
        events.append((2, q, n, cur[q], zero, dim[cur[q]]))
        for t, row in enumerate(word["scatter"]):
            if k in row:
                events.append((1, v + t, n, 1, zero, 3))
        events.append((3, q, n, cur[q], zero, 0))
    section("B", 4)
    section("C", 5)
    for r, f in enumerate(word["final"]):
        move(r, f)
    return events


def invoice(events, n):
    counts = Counter(e[0] for e in events)
    paid = Counter()
    for op, a, b, c, f, z in events:
        if op == 0 and f:
            paid[f] += 1
        elif op == 2:
            paid[z] += 1
    maxima = []
    for reverse in (False, True):
        norms = [1] * (n + 1)
        maximum = 1
        opened = False
        for op, a, b, c, f, z in reversed(events) if reverse else events:
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                norms[a] += abs(c) * norms[b]
                maximum = max(maximum, norms[a])
            elif op == 2:
                need(not opened, "copy nested")
                norms[b] = norms[a]
                opened = True
            elif op == 3:
                need(opened, "erase without copy")
                norms[b] = 0
                opened = False
        need(not opened, "unclosed copy")
        maxima.append(maximum)
    payload = 64 * maxima[0] ** 3 * maxima[1] ** 2
    need(payload < 1 << 104, "payload cap exceeded")
    return {"records": len(events), "ADDs": counts[1], "MOVEs": counts[0],
            "COPYs": counts[2], "ERASEs": counts[3],
            "paid_profile": {str(k): v for k, v in sorted(paid.items())},
            "rank_mass": sum(k * v for k, v in paid.items()),
            "forward_positive_bound": maxima[0], "reverse_positive_bound": maxima[1],
            "payload_prefix_upper": str(payload), "payload_bits": payload.bit_length()}


def frame_paths(word, events):
    paths = [[f] for f in word["start"]]
    for op, a, b, c, f, z in events:
        if op == 0:
            need(paths[a][-1] == b, "MOVE source mismatch")
            paths[a].append(c)
    return paths


def export_check(word, expected, directory):
    path = directory / "word.json.gz"
    path.write_bytes(gzip.compress(canonical(word), mtime=0))
    out = directory / "records"
    subprocess.run([sys.executable, "-I", "-B", str(ROOT / EXPORT), str(path), str(out)],
                   check=True, capture_output=True, text=True)
    raw = (out / "249-records.bin").read_bytes()
    actual = list(struct.iter_unpack("<6i", raw))
    need(actual == expected, "independent/exported records disagree")
    return hashlib.sha256(raw).hexdigest()


def verify(write=False):
    pins = sources()
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    recipe = json.loads((HERE / "CANDIDATE.json").read_text())
    for key, expected in (("base_commit", pins["base_commit"]), ("assignment_seed", 18),
                          ("source_path", WORD), ("source_sha256", pins["sha256"][WORD]),
                          ("frame", 506), ("fixed_cuts", [102, 114, 128])):
        need(recipe.get(key) == expected, "candidate metadata mismatch: " + key)
    factor = module(HERE / "independent.py", "frame506_factor_check")
    factors = factor.run(recipe, word)
    factor_controls = factor.controls(recipe, word)
    need(recipe["candidate_gates"] == [[506,d,[s]] for f in recipe["factors"] for d,s in f["new_ops"]],
         "candidate gates differ from independently checked factors")
    proposed = candidate(word, recipe)
    regs = recipe["registers"]
    old = word["B"][102:128]
    new = proposed["B"][102:102 + len(recipe["candidate_gates"]) ]
    need(integer_map(old, regs) == integer_map(new, regs), "forward integer map changed")
    old_reverse, new_reverse = integer_map(old, regs, True), integer_map(new, regs, True)
    reverse_dominated = all(a <= b for nr, br in zip(new_reverse, old_reverse)
                            for a, b in zip(nr, br))
    need(reverse_dominated == recipe["positive_reverse_entrywise_dominated"],
         "reverse domination metadata mismatch")
    need(recipe["positive_reverse_identity"] == (old_reverse == new_reverse), "reverse identity claim")
    need(recipe["integer_forward_identity"] is True, "forward identity claim")
    need((recipe["original_additions"], recipe["candidate_additions"], recipe["saved_additions"])
         == (len(old), len(new), len(old) - len(new)), "candidate addition counts")
    def both_orders(gates):
        return integer_map(gates + list(reversed(gates)), regs)
    need(recipe["local_unit_norm_forward_then_reverse_max"] ==
         {"original": max(map(sum, both_orders(old))), "candidate": max(map(sum, both_orders(new)))},
         "local norm metadata mismatch")
    truth_inputs = boolean_check(old, new, regs)
    checker = module(ROOT / CHECK, "frame506_source_checker")
    receipts = []
    records = []
    for current in (word, proposed):
        W, lab, full, H, C, info = checker.check(current)
        need(all(H.values()) and all(C.values()), "H1-H5/interface failed")
        rec = emit(current, W.fdim)
        records.append(rec)
        receipts.append({"columns": full["columns"], "labels": lab,
                         "H": H, "conclusion": C, "invoice": invoice(rec, W.n)})
    base, result = receipts
    need(base["columns"] == result["columns"] == 661, "wrong column coverage")
    need(frame_paths(word, records[0]) == frame_paths(proposed, records[1]), "frame paths changed")
    for key in ("paid_profile", "rank_mass", "MOVEs", "COPYs", "ERASEs"):
        need(base["invoice"][key] == result["invoice"][key], "changed bill: " + key)
    saved = len(old) - len(new)
    need(saved > 0 and base["invoice"]["ADDs"] - result["invoice"]["ADDs"] == 2 * saved,
         "complete restoration saving mismatch")
    controls = []
    def reject(name, function):
        try:
            function()
        except (ValueError, checker.Reject):
            controls.append(name)
            return
        raise ValueError("control accepted: " + name)
    wrong = copy.deepcopy(proposed)
    del wrong["B"][102]
    reject("omitted forward gate", lambda: checker.check(wrong))
    wrong_cleanup = copy.deepcopy(proposed)
    wrong_cleanup["C"] = copy.deepcopy(word["C"])
    def interface_control():
        H, C, info = checker.Word(wrong_cleanup).interface()
        need(all(H.values()) and all(C.values()), "literal restoration missing")
    reject("unmodified cleanup", interface_control)
    wrong_frame = copy.deepcopy(proposed)
    wrong_frame["B"][102][0] = 0
    reject("frame descent", lambda: checker.check(wrong_frame))
    wrong_dirty = copy.deepcopy(proposed)
    wrong_dirty["B"][102][2] = [222]
    reject("substituted dirty helper", lambda: checker.check(wrong_dirty))
    wrong_scatter = copy.deepcopy(proposed)
    wrong_scatter["scatter"][0] = wrong_scatter["scatter"][0][1:]
    reject("omitted copied-total contribution", lambda: checker.check(wrong_scatter))
    wrong_erase = list(records[1])
    wrong_erase.pop(next(i for i, e in enumerate(wrong_erase) if e[0] == 3))
    reject("omitted erase", lambda: invoice(wrong_erase, 661))
    with tempfile.TemporaryDirectory(prefix="frame506-check-") as tmp:
        hashes = []
        for i, (current, rec) in enumerate(zip((word, proposed), records)):
            out = Path(tmp) / str(i)
            out.mkdir()
            hashes.append(export_check(current, rec, out))
    receipt = {"status": "PASS_R439_FRAME506", "base_commit": pins["base_commit"],
               "candidate_recipe_sha256": digest(recipe),
               "source_word_canonical_sha256": digest(word),
               "candidate_word_canonical_sha256": digest(proposed),
               "source_block_ADDs": len(old), "candidate_block_ADDs": len(new),
               "complete_saved_ADDs": 2 * saved, "truth_table_inputs": truth_inputs,
               "unchanged_register_frame_paths": 661, "reverse_positive_entrywise_dominated": reverse_dominated,
               "factors": factors, "baseline": base, "candidate": result,
               "independent_factor_controls_rejected": factor_controls,
               "exported_record_sha256": hashes, "negative_controls_rejected": controls,
               "selected_kappa": "1661960547713947/1000000000000000000", "new_kappa_claim": False}
    path = HERE / "CERTIFICATE.json"
    if write:
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        need(receipt == json.loads(path.read_text()), "certificate differs from fresh replay")
    print("PASS_R439_FRAME506", "block=%d->%d" % (len(old), len(new)),
          "ADDs=%d->%d" % (base["invoice"]["ADDs"], result["invoice"]["ADDs"]),
          "columns=661", "inputs=" + str(truth_inputs), "controls=" + str(len(controls)), "no_new_kappa")
    return proposed, receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true")
    parser.add_argument("--word", type=Path)
    args = parser.parse_args()
    w, receipt = verify(args.write_certificate)
    if args.word:
        need(not args.word.exists(), "output already exists")
        args.word.write_bytes(gzip.compress(canonical(w), mtime=0))
