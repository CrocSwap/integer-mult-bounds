#!/usr/bin/env python3
"""Check the warm-entry boundary without changing the frozen composition proof."""
from contextlib import ExitStack, contextmanager
from fractions import Fraction as F
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import argparse
import json

import check

HERE = Path(__file__).resolve().parent
PROOF_PIN = "f40697245c65ade66b84d49f7ed64c5c13a598d962a71bb3e2881bd64f65f9fd"


def need(ok, why):
    if not ok:
        raise AssertionError(why)


def source_pipe(size):
    cleared = []

    class Tape(BytesIO):
        def close(self):
            need(not any(self.getvalue()), "source left dirty bytes after return")
            cleared.append(len(self.getvalue()))
            super().close()

    env = {"ExitStack": ExitStack, "contextmanager": contextmanager,
           "TemporaryFile": Tape, "CHUNK": 65536, "ZEROS": bytes(65536)}
    check.extract("streaming_routes.py", ["read_exact", "write_zeros", "copy_bytes", "erase"], env)
    check.extract("stack_tapes.py", ["FileHead", "Page", "PacketStack", "Arena"], env)
    check.extract("growing_binary.py", ["pipe"], env)
    arena = env["Arena"]()
    data = bytes((i*13+1)%256 for i in range(size))
    out = BytesIO()

    def identity(source, target):
        env["copy_bytes"](source, target, size)

    env["pipe"](arena, "weighted", BytesIO(data), out, size, [identity, identity])
    need(out.getvalue() == data, "complete source pipe return")
    need(all(not head.frames for head in arena.heads.values()), "source retained page markers")
    peaks = {f"{key[0]}:{key[1]}": head.peak for key, head in arena.heads.items()}
    need(peaks["weighted:0"] == peaks["weighted:1"] == size, "two per-call historical peaks")
    arena.close()
    need(len(cleared) == len(peaks), "not every source role closed")
    return peaks


def combine(entry, new):
    return {r: max(entry.get(r, 0), new.get(r, 0)) for r in entry.keys() | new.keys()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE/"evidence/ENTRY-HISTORY.json")
    args = parser.parse_args()
    check.source_pins()
    need(sha256((HERE/"PROOF.md").read_bytes()).hexdigest() == PROOF_PIN, "frozen proof changed")
    large, small = source_pipe(128), source_pipe(8)
    retained = combine(large, small)
    need(sum(large.values()) == 256 and sum(small.values()) == 16,
         "shrinking-control geometry")
    need(sum(retained.values()) == 256, "historical capacity was discarded after erasure")
    g = 6+F(123,8*(17-1))
    need(sum(retained.values()) > g*8, "current-small-call bound control is vacuous")
    need(sum(retained.values()) <= g*128, "reservation-wide maximum does not cover the history")
    entry = {"weighted:0": 512, "weighted:1": 3, "public-cold-only:0": 1024}
    warm = combine(entry, small)
    need(warm["weighted:0"] == 512 and warm["weighted:1"] == 8
         and warm["public-cold-only:0"] == 1024, "blank or untouched entry capacity lost")
    need(sum(warm.values()) <= sum(entry.values())+sum(small.values()), "additive warm grant")
    histories = ((128,8), (8,128,4), (64,32,16,8,4,2,1), (1,1,1))
    for sizes in histories:
        state = {}
        for size in sizes:
            state = combine(state, source_pipe(size))
        need(sum(state.values()) == 2*max(sizes), "coordinatewise history induction")
    report = {
        "status": "PASS_NATIVE_ENTRY_HISTORY_BOUNDARY",
        "frozen_proof_sha256": PROOF_PIN,
        "applicability_note_sha256": sha256((HERE/"ENTRY-HISTORY.md").read_bytes()).hexdigest(),
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "large_call_peak_sum": sum(large.values()),
        "smaller_call_peak_sum": sum(small.values()),
        "reused_reserve_after_smaller_call": sum(retained.values()),
        "current_call_only_bound": str(g*8),
        "current_call_only_bound_rejected": True,
        "asymmetric_warm_entry": entry,
        "asymmetric_warm_exit": warm,
        "history_cases": len(histories),
        "scope": "Actual source pipe/allocator returns plus separate coordinatewise historical ledger; native-entry theorem only",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
