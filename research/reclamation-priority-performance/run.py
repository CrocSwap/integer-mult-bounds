"""Compile one complete pinned axis, then compare and independently replay it."""

import argparse
import gzip
from hashlib import sha256
import importlib
import json
from pathlib import Path
import platform
import sys
import time

from adapter import ROOT, load, require


def run(mode, h, output):
    require(not output.exists(), "Output must be a fresh directory")
    compiler = load(mode)
    output.mkdir(parents=True)
    wall = time.perf_counter()
    cpu = time.process_time()
    result, word = compiler.compile_axis(h)
    seconds = time.perf_counter() - wall
    cpu_seconds = time.process_time() - cpu
    stored = json.loads((ROOT / "certificates/joint-dual-compiler.json").read_text())
    expected = stored["axes"][str(h)]
    require(json.loads(json.dumps(result)) == expected["compiled"],
            "Complete compiler receipt differs")
    raw = (json.dumps(word, separators=(",", ":")) + "\n").encode()
    frozen = gzip.decompress((ROOT / f"certificates/joint-dual-word-{h}.json.gz").read_bytes())
    require(raw == frozen, "Complete generated physical word differs")
    path = output / "word.json"
    path.write_bytes(raw)
    replay = importlib.import_module("binary_frame_replay").replay(path)
    require(json.loads(json.dumps(replay)) == expected["replay"],
            "Independent all-column/frame replay receipt differs")
    transitions = importlib.import_module("binary_frame_profile_prepare").prepare(
        path, output / "transitions.bin")
    expected_transitions = json.loads((ROOT / f"certificates/joint-dual-transitions-{h}.json").read_text())
    require(json.loads(json.dumps(transitions)) == expected_transitions,
            "Independent transition reconstruction differs")
    record = dict(
        status="PASS", engine=mode, h=h, compile_wall_seconds=seconds,
        compile_cpu_seconds=cpu_seconds, python=sys.version, platform=platform.platform(),
        word_sha256=sha256(raw).hexdigest(), word_bytes=len(raw),
        compiler_receipt=result, independent_replay=replay, transitions=transitions,
        scope="Complete axis compilation, exact decompressed word equality, independent dirty-basis/frame replay and transition reconstruction; no new bound",
    )
    (output / "RESULT.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(f"PASS_RECLAMATION_AXIS engine={mode} h={h} compile_seconds={seconds:.6f}", flush=True)
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("reference", "buckets", "indexed"), required=True)
    parser.add_argument("--h", type=int, choices=(23, 25), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args.mode, args.h, args.out)
