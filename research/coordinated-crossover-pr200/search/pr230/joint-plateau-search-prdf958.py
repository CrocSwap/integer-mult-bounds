#!/usr/bin/env python3
"""Reproduce the equal-frame plateau descent on the joint physical word.

The d*log(d) score proposes moves only. The repository's actual joint
Candidate checks exact operation-frame spans, nondegeneracy, and chain nesting.
The paid moment and exponent are certified separately by the finite verifier.
No random numbers are used. This incremental search was prepared by sennemmi
with substantial OpenAI Codex assistance. It builds on PR210 by eumemic and
PR216 by Dugongue; all inherited contributors retain their original credit.
Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import shutil
import sys
import tempfile
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
SOURCE_P = Path(__file__).resolve().parents[1]
PARENT = "df95878d11190518e45ef9717c9ee05011f88ace"
BASE_SHA256 = "687496f3c15818e7cad1beb5fdf3812b8e38825ea302bfd60aea7ac23f3516b4"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def source_package(tmp: Path) -> Path:
    manifest = json.loads((SOURCE_P / "BASELINE.json").read_text())
    parts = []
    skip = set()
    for entry in manifest["parts"]:
        part = SOURCE_P / entry["file"]
        data = part.read_bytes()
        assert len(data) == entry["bytes"] and sha256(data) == entry["sha256"]
        parts.append(data)
        skip.add(entry["file"])
    archive = b"".join(parts)
    assert sha256(archive) == manifest["archive_sha256"]
    root = tmp / "source"
    root.mkdir()
    with zipfile.ZipFile(__import__("io").BytesIO(archive)) as z:
        for entry in z.infolist():
            try:
                (root / entry.filename).resolve().relative_to(root.resolve())
            except ValueError as exc:
                raise AssertionError("unsafe pinned archive entry") from exc
        z.extractall(root)
    package = root / "research" / "coordinated-crossover-pr200"
    package.mkdir()
    for file in SOURCE_P.rglob("*"):
        if file.is_file() and file.name not in skip:
            target = package / file.relative_to(SOURCE_P)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)
    # The source tree contains the committed candidate frames. Reproduction must
    # begin from PR210's pinned parent input, not from that candidate output.
    parent_frames = package / "search" / "base-frames-prdf958.json"
    assert sha256(parent_frames.read_bytes()) == BASE_SHA256
    shutil.copyfile(parent_frames, package / "frames" / "opframe-bases.json")
    return package


def load_candidate(P: Path):
    sys.path.insert(0, str(P.parents[1] / "research" / "paired-cube-diagonal-bit-168" / "bit"))
    spec = importlib.util.spec_from_file_location("joint_word", P / "joint" / "joint_word.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.Candidate


def run_search(P: Path):
    started = time.monotonic()
    base_path = P / "search" / "base-frames-prdf958.json"
    base_bytes = base_path.read_bytes()
    assert sha256(base_bytes) == BASE_SHA256, "parent PR210 frame input changed"
    assert sha256((P / "frames" / "opframe-bases.json").read_bytes()) == BASE_SHA256

    W = load_candidate(P)()
    C = W.C
    W.changed_frames = [i for i, (a, b) in enumerate(zip(W.original_opframe, W.opframe)) if a != b]
    W.endframe = {s: W.opframe[xs[-1]] for s, xs in W.role_ops.items()}
    W.exact_frames()
    baseline = W.row()
    base = W.opframe[:]

    zero = W.register([])
    full = W.w["full_frame"]
    before = [[] for _ in W.ops]
    after = [[] for _ in W.ops]
    starts = {b: W.w["source_frame"][x] for x, b in W.source.items()}
    starts.update({b: z["frame"] for b, z in W.gauge.items()})
    ends = {s: W.w["root_frame"][j] for j, s in enumerate(W.w["rootroles"])}
    ends.update({d: W.gauge[b]["frame"] for b, d in W.pairs})
    for s, xs in W.role_ops.items():
        chain = [-starts.get(s, zero) - 1] + xs + [-ends.get(s, full) - 1]
        for j, i in enumerate(xs, 1):
            before[i].append(chain[j - 1])
            after[i].append(chain[j + 1])
    assert all(len(x) == 2 for x in before + after)

    def frame(ref):
        return W.opframe[ref] if ref >= 0 else -ref - 1

    F = [0] + [r * math.log(r) for r in range(1, W.h + 1)]

    def merit(d, prev, nxt):
        return sum(F[d - C.dimf[p]] for p in prev) + sum(F[C.dimf[n] - d] for n in nxt)

    nondeg = {}
    intersections = {}

    def good(f):
        if f not in nondeg:
            nondeg[f] = C.nondeg(f)
        return nondeg[f]

    def intersection(a, b):
        if C.sub(a, b):
            return a
        if C.sub(b, a):
            return b
        key = tuple(sorted((a, b)))
        if key not in intersections:
            rows, _ = W.module.kernel(C.A[a] + C.A[b], W.h)
            intersections[key] = W.register(rows)
        return intersections[key]

    parent = list(range(len(W.ops)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        i, j = find(i), find(j)
        if i != j:
            parent[j] = i

    for i, successors in enumerate(after):
        for j in successors:
            if j >= 0 and C.dimf[W.opframe[i]] == C.dimf[W.opframe[j]] and C.sub(W.opframe[i], W.opframe[j]):
                union(i, j)
    groups = defaultdict(list)
    for i in range(len(W.ops)):
        groups[find(i)].append(i)

    stats = Counter()
    moves = []
    sweeps = []
    total_gain = 0.0
    for sweep in range(8):
        changed = 0
        sweep_gain = 0.0
        for xs in groups.values():
            members = set(xs)
            old = W.opframe[xs[0]]
            d = C.dimf[old]
            if any(not (C.dimf[W.opframe[i]] == d and C.sub(old, W.opframe[i])) for i in xs):
                continue
            prev = [frame(j) for i in xs for j in before[i] if j not in members]
            nxt = [frame(j) for i in xs for j in after[i] if j not in members]
            stats["groups"] += 1
            if min(C.dimf[f] for f in nxt) <= d:
                continue
            stats["dimension_room"] += 1
            f = nxt[0]
            for next_frame in nxt[1:]:
                f = intersection(f, next_frame)
                if C.dimf[f] <= d:
                    break
            new_dim = C.dimf[f]
            if new_dim <= d:
                continue
            stats["intersection_room"] += 1
            if not good(f):
                stats["degenerate"] += 1
                continue
            assert C.sub(old, f)
            gain = merit(new_dim, prev, nxt) - merit(d, prev, nxt)
            stats["positive" if gain > 1e-10 else "nonpositive"] += 1
            if gain <= 1e-10:
                continue
            for i in xs:
                W.opframe[i] = f
            changed += len(xs)
            sweep_gain += gain
            moves.append({"ops": xs, "old_dim": d, "new_dim": new_dim, "score_gain": round(gain, 15)})
        sweeps.append({"sweep": sweep, "changed_operations": changed, "score_gain": round(sweep_gain, 15)})
        total_gain += sweep_gain
        if changed == 0:
            break

    W.changed_frames = [i for i, (a, b) in enumerate(zip(W.original_opframe, W.opframe)) if a != b]
    W.endframe = {s: W.opframe[xs[-1]] for s, xs in W.role_ops.items()}
    W.exact_frames()
    profile = W.row()
    delta = Counter({int(k): n for k, n in profile["child_histogram"].items()})
    delta.subtract({int(k): n for k, n in baseline["child_histogram"].items()})
    all_frames = [[i, C.B[f]] for i, f in enumerate(W.opframe) if f != W.w["op_frame"][i]]
    frame_bytes = (json.dumps(all_frames, separators=(",", ":")) + "\n").encode()
    record = {
        "schema": "joint-equal-frame-plateau-v1",
        "parent_commit": PARENT,
        "starting_frames_sha256": BASE_SHA256,
        "candidate_frames_sha256": sha256(frame_bytes),
        "random_seed": None,
        "randomness": "none; deterministic group order and greedy sweeps",
        "objective": "float d*log(d) proposal; exact frame and nested-chain predicates admit moves",
        "status": "EXACT_FRAMES_AND_NESTED_CHAINS_PASS_NOT_FULL_WORD_REPLAY",
        "group_count": len(groups),
        "sweeps": sweeps,
        "accepted_moves": moves,
        "search_counters": dict(sorted(stats.items())),
        "proposal_score_gain": round(total_gain, 15),
        "baseline_profile": baseline,
        "candidate_profile": profile,
        "child_histogram_delta": {str(k): v for k, v in sorted(delta.items()) if v},
        "changed_operation_frames_from_parent": len([i for i, (a, b) in enumerate(zip(base, W.opframe)) if a != b]),
        "changed_operation_frames_from_word": len(W.changed_frames),
        "elapsed_seconds_excluded_from_record": True,
    }
    return frame_bytes, canonical(record), record, time.monotonic() - started


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verify-committed", action="store_true")
    ap.add_argument("--frames-out", type=Path)
    ap.add_argument("--record-out", type=Path)
    args = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="joint-plateau-") as tmp_name:
        P = source_package(Path(tmp_name))
        frames, record_bytes, record, elapsed = run_search(P)
    if args.verify_committed:
        assert frames == (SOURCE_P / "frames" / "opframe-bases.json").read_bytes(), "frame witness differs"
        assert record_bytes == (SOURCE_P / "search" / "joint-plateau-result-prdf958.json").read_bytes(), "search record differs"
        print(f"PASS deterministic plateau reproduction; {len(record['accepted_moves'])} moves, {record['changed_operation_frames_from_parent']} operation frames; {elapsed:.1f}s")
        return
    assert args.frames_out and args.record_out, "supply output paths or use --verify-committed"
    args.frames_out.parent.mkdir(parents=True, exist_ok=True)
    args.record_out.parent.mkdir(parents=True, exist_ok=True)
    args.frames_out.write_bytes(frames)
    args.record_out.write_bytes(record_bytes)
    print(f"Wrote candidate frames and record; {len(record['accepted_moves'])} moves in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
