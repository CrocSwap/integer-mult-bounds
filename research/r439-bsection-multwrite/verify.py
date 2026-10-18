#!/usr/bin/env python3
"""Independent exact finite verification of the ten multi-write R439 phase-B
block programs.

The verifier does not import search.py.  It pins every consumed source,
re-derives each block's integer transfer map and Boolean truth tables, splices
all ten candidates into one word, rebuilds the literal reverse cleanup, and
rechecks the complete word: frame paths, all 661 arbitrary dirty-input
endpoint columns, the inherited H1-H5 interface, the paid profile and rank
mass, and the exported record bills and positive/payload bounds, with eight
mutation controls.

Prepared with help from opencode; Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"

# frame, first B index, last B index (inclusive)
BLOCKS = [
    (506, 102, 127),
    (507, 128, 162),
    (519, 163, 204),
    (508, 205, 241),
    (520, 242, 282),
    (509, 283, 313),
    (521, 314, 360),
    (522, 361, 403),
    (523, 404, 448),
    (524, 449, 489),
]
EXPECTED_PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
EXPECTED_RANK_MASS = 5129
EXPECTED_ADDS_BEFORE = 24305
EXPECTED_ADDS_AFTER = 24053
EXPECTED_COLUMNS = 661


class Reject(Exception):
    pass


def need(ok, msg):
    if not ok:
        raise Reject(msg)


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":")).encode()


def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()


def matrix(ops, n):
    cols = []
    for c in range(n):
        x = [int(i == c) for i in range(n)]
        for a, b in ops:
            need(type(a) is int and type(b) is int and 0 <= a < n and 0 <= b < n and a != b,
                 "invalid operation")
            x[a] += x[b]
        cols.append(x)
    return [list(r) for r in zip(*cols)]


def pins():
    s = json.loads((HERE / "SOURCES.json").read_text())
    need(s["base_commit"] == "007664306fff84fbb1c9a1b4053b69f439764034", "base pin")
    for p, h in s["files"].items():
        need(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h, "source pin: " + p)


def bind_block(word, entry):
    frame, first, last = entry["_block"]
    need(entry["frame"] == frame and entry["slice"] == [first, last + 1], "block binding")
    old = word["B"][first:last + 1]
    need(all(f == frame and len(ss) == 1 for f, _, ss in old), "source block")
    regs = sorted({t for _, t, _ in old} | {s for _, _, ss in old for s in ss})
    need(entry["registers"] == regs, "register binding")
    need(entry["original_gates"] == len(old), "original gate count")
    index = {r: i for i, r in enumerate(regs)}
    n = len(regs)
    old_ops = [(index[t], index[ss[0]]) for _, t, ss in old]
    newg = entry["gates"]
    need(type(entry["new_gates"]) is int and len(newg) == entry["new_gates"] < len(old),
         "candidate gate count")
    need(all(f == frame and d in index and len(ss) == 1 and ss[0] in index and d != ss[0]
             for f, d, ss in newg), "candidate shape")
    new_ops = [(index[d], index[ss[0]]) for _, d, ss in newg]
    mo, mn = matrix(old_ops, n), matrix(new_ops, n)
    need(mo == mn, "integer map " + str(frame))
    for val in range(1 << n):
        a = [(val >> i) & 1 for i in range(n)]
        b = list(a)
        for ops, state in ((old_ops, a), (new_ops, b)):
            for d, s in ops:
                state[d] ^= state[s]
        need(a == b, "F2 table " + str(frame))
    ro, rn = matrix(old_ops[::-1], n), matrix(new_ops[::-1], n)
    touched = sorted({regs[t] for t, _ in new_ops} | {regs[s] for _, s in new_ops})
    need(touched == regs and entry["all_registers_touched"] is True,
         "all registers touched " + str(frame))
    return {
        "frame": frame,
        "slice": [first, last + 1],
        "registers": regs,
        "original_gates": len(old_ops),
        "new_gates": len(new_ops),
        "boolean_inputs_checked": 1 << n,
        "forward_integer_sha256": digest(mo),
        "reverse_old_total": sum(map(sum, ro)),
        "reverse_new_total": sum(map(sum, rn)),
        "reverse_entrywise_dominated": all(x <= y for p, q in zip(rn, ro) for x, y in zip(p, q)),
    }


def cleanup(w):
    full = next(i for i, f in enumerate(w["frames"]) if len(f) == w["v"])
    return [[full, d, list(ss)] for _, d, ss in reversed(w["A"] + w["B"]) if d < w["v"] or d >= 2 * w["v"]]


def candidate_word(word, cand):
    w = copy.deepcopy(word)
    for entry in sorted(cand["blocks"], key=lambda b: b["slice"][0], reverse=True):
        first, last = entry["slice"]
        w["B"][first:last] = copy.deepcopy(entry["gates"])
    w["C"] = cleanup(w)
    return w


def paths(w):
    fs = list(map(set, w["frames"]))
    ps = [[f] for f in w["start"]]

    def move(r, f):
        if ps[r][-1] != f:
            need(fs[ps[r][-1]] < fs[f], "illegal frame move")
            ps[r].append(f)

    for k in "DABC":
        for f, d, ss in w[k]:
            for r in [d, *ss]:
                move(r, f)
    for r, f in enumerate(w["final"]):
        move(r, f)
    return ps


def endpoint(w):
    n = 2 * w["v"] + w["R"]
    v = w["v"]
    state = [{i} for i in range(n)]

    def run(k):
        for _, d, ss in w[k]:
            for s in ss:
                state[d].symmetric_difference_update(state[s])

    run("D")
    run("A")
    snap = [state[r].copy() for r in w["ret"]]
    for t, reads in enumerate(w["scatter"]):
        for k in reads:
            state[v + t].symmetric_difference_update(snap[k])
    run("B")
    run("C")
    for r, x in enumerate(state):
        need(x == ({r, r - v} if v <= r < 2 * v else {r}), "endpoint register " + str(r))
    return n


def checker():
    s = importlib.util.spec_from_file_location("r439_owner_checker", ROOT / CHECKER)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def bill(w, out):
    out.mkdir(parents=True)
    wp = out / "word.json.gz"
    wp.write_bytes(gzip.compress(canonical(w), mtime=0))
    subprocess.run([sys.executable, "-I", "-B", str(ROOT / EXPORTER), str(wp), str(out / "records")],
                   check=True, capture_output=True, text=True)
    raw = (out / "records/249-records.bin").read_bytes()
    need(len(raw) % 24 == 0, "record alignment")
    rec = list(struct.iter_unpack("<6i", raw))
    n = 2 * w["v"] + w["R"]
    bounds = []
    for rev in (False, True):
        norms = [1] * (n + 1)
        maximum = 1
        opened = False
        for op, a, b, c, _, _ in (reversed(rec) if rev else rec):
            if op == 0:
                continue
            if rev and op in (2, 3):
                op = 5 - op
            if op == 1:
                norms[a] += abs(c) * norms[b]
                maximum = max(maximum, norms[a])
            elif op == 2:
                need(not opened, "nested copy")
                norms[b] = norms[a]
                opened = True
            elif op == 3:
                need(opened, "erase without copy")
                norms[b] = 0
                opened = False
            else:
                raise Reject("record opcode")
        need(not opened, "unclosed copy")
        bounds.append(maximum)
    payload = 64 * bounds[0] ** 3 * bounds[1] ** 2
    need(payload < 1 << 104, "payload cap")
    return {"records": len(rec),
            "adds": sum(x[0] == 1 for x in rec),
            "copies": sum(x[0] == 2 for x in rec),
            "erasures": sum(x[0] == 3 for x in rec),
            "forward_positive_bound": bounds[0],
            "reverse_positive_bound": bounds[1],
            "payload_bits": payload.bit_length(),
            "record_sha256": hashlib.sha256(raw).hexdigest()}, rec


def reject(name, fn):
    try:
        fn()
    except Reject:
        return name
    raise Reject("negative control accepted: " + name)


def verify(out):
    pins()
    cand = json.loads((HERE / "CANDIDATE.json").read_text())
    need(cand["base_commit"] == "007664306fff84fbb1c9a1b4053b69f439764034", "candidate base pin")
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    by_frame = {}
    for spec in BLOCKS:
        entry = dict(cand["blocks"][[b["frame"] for b in cand["blocks"]].index(spec[0])])
        entry["_block"] = spec
        by_frame[spec[0]] = entry
    need(set(by_frame) == {b[0] for b in BLOCKS} and len(cand["blocks"]) == len(BLOCKS),
         "block inventory")
    blocks = [bind_block(word, by_frame[frame]) for frame, _, _ in BLOCKS]
    w = candidate_word(word, cand)
    need(all(w[k] == word[k] for k in word if k not in ("B", "C")), "unrelated field")
    need(w["C"] == cleanup(w), "literal cleanup")
    p0, p1 = paths(word), paths(w)
    need(p0 == p1, "frame paths")
    endpoint(word)
    columns = endpoint(w)
    need(columns == EXPECTED_COLUMNS, "column count")
    dim, labels, flow, hyp, con, _ = checker().check(w)
    need(all(hyp.values()) and all(con.values()), "H1-H5 interface")
    profile = Counter(dim.fdim[b] - dim.fdim[a] for p in p1 for a, b in itertools.pairwise(p))
    profile.update(t["rank"] for t in flow["totals"])
    need(dict(sorted(profile.items())) == EXPECTED_PROFILE, "profile")
    need(sum(k * v for k, v in profile.items()) == EXPECTED_RANK_MASS, "rank mass")
    before, r0 = bill(word, out / "before")
    after, r1 = bill(w, out / "after")
    need((before["adds"], after["adds"]) == (EXPECTED_ADDS_BEFORE, EXPECTED_ADDS_AFTER), "ADD bill")
    need(before["copies"] == after["copies"] == 9 and before["erasures"] == after["erasures"] == 9,
         "copy bill")
    need(Counter(x for x in r0 if x[0] != 1) == Counter(x for x in r1 if x[0] != 1), "non-ADD events")
    need(after["forward_positive_bound"] <= before["forward_positive_bound"], "forward bound")
    need(after["payload_bits"] <= 104, "payload bits")
    controls = []
    bad = copy.deepcopy(cand)
    regs0 = bad["blocks"][0]["registers"]
    cur = bad["blocks"][0]["gates"][0][2][0]
    bad["blocks"][0]["gates"][0][2] = [next(r for r in regs0 if r not in (cur, bad["blocks"][0]["gates"][0][1]))]
    controls.append(reject("mutated_source", lambda: bind_block(word, self_bind(bad["blocks"][0], BLOCKS[0]))))
    bad = copy.deepcopy(cand)
    bad["blocks"][1]["gates"].pop()
    bad["blocks"][1]["new_gates"] -= 1
    controls.append(reject("dropped_gate", lambda: bind_block(word, self_bind(bad["blocks"][1], BLOCKS[1]))))
    bad = copy.deepcopy(cand)
    bad["blocks"][2]["gates"][0][0] = 0
    controls.append(reject("illegal_frame", lambda: bind_block(word, self_bind(bad["blocks"][2], BLOCKS[2]))))
    bad = copy.deepcopy(cand)
    bad["blocks"][3]["gates"], bad["blocks"][3]["new_gates"] = bad["blocks"][4]["gates"], bad["blocks"][4]["new_gates"]
    controls.append(reject("swapped_block", lambda: bind_block(word, self_bind(bad["blocks"][3], BLOCKS[3]))))
    bad = copy.deepcopy(w)
    bad["C"].pop()
    controls.append(reject("omitted_cleanup", lambda: endpoint(bad)))
    first, last = BLOCKS[0][1], BLOCKS[0][2]
    bad = copy.deepcopy(w)
    del bad["B"][first]
    bad["C"] = cleanup(bad)
    controls.append(reject("missing_gate_matching_cleanup", lambda: endpoint(bad)))
    bad = copy.deepcopy(w)
    bad["B"][first][0] = 0
    controls.append(reject("illegal_frame_word", lambda: paths(bad)))
    stale = copy.deepcopy(w)
    stale["C"] = word["C"]
    endpoint(stale)
    controls.append(reject("stale_cleanup", lambda: need(stale["C"] == cleanup(stale), "H4")))
    return {
        "status": "PASS_R439_BSECTION_MULTWRITE",
        "base_commit": cand["base_commit"],
        "assignment_seed": 16,
        "blocks": blocks,
        "columns": columns,
        "closed_frames": labels["frames"],
        "copy_ranks": [t["rank"] for t in flow["totals"]],
        "paid_profile": {str(k): v for k, v in sorted(profile.items())},
        "rank_mass": EXPECTED_RANK_MASS,
        "identical_register_frame_paths": len(p1),
        "hypotheses": hyp,
        "conclusion": con,
        "before": before,
        "after": after,
        "adds_saved": before["adds"] - after["adds"],
        "new_kappa_claim": False,
        "candidate_content_sha256": digest(w),
        "negative_controls": controls,
        "search": cand["search"],
    }


def self_bind(entry, spec):
    entry = dict(entry)
    entry["_block"] = spec
    return entry


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    ap.add_argument("--record-certificate", action="store_true")
    a = ap.parse_args()
    if a.out:
        need(not a.out.exists(), "output exists")
        out = a.out
    else:
        tmp = tempfile.TemporaryDirectory(prefix="r439-bsec-")
        out = Path(tmp.name)
    report = verify(out)
    cert = HERE / "CERTIFICATE.json"
    if a.record_certificate:
        need(not cert.exists(), "certificate exists")
        cert.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    else:
        need(report == json.loads(cert.read_text()), "certificate mismatch")
    print("PASS_R439_BSECTION_MULTWRITE",
          "gates=%d->%d ADDs=%d->%d columns=%d controls=%d rank_mass=%d kappa=unchanged" % (
              sum(b["original_gates"] for b in report["blocks"]),
              sum(b["new_gates"] for b in report["blocks"]),
              report["before"]["adds"], report["after"]["adds"],
              report["columns"], len(report["negative_controls"]), report["rank_mass"]))


if __name__ == "__main__":
    main()
