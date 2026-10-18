#!/usr/bin/env python3
"""Pending allocations and actual quotas in frozen PR2697 caller fixtures.

Ross Richardson with substantial OpenAI Codex assistance; Apache-2.0.
The source fixture/harness is explicitly reused from PR2825, not independent.
"""
import argparse
from contextlib import contextmanager, ExitStack
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
SNAPSHOT = "d5010fc3914128612ea92ca2698e56d4a90fd8f73b549c80fb6ba0e499579d33"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            need(k not in result, "duplicate JSON key")
            result[k] = v
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique,
                      parse_constant=lambda _: need(False, "nonfinite JSON"))


def authenticate():
    raw = (ROOT / "SNAPSHOTS.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SNAPSHOT, "snapshot manifest pin")
    records = read_json(ROOT / "SNAPSHOTS.json")["files"]
    names = [r["path"] for r in records]
    need(len(set(names)) == len(names), "unique source paths")
    actual = {p.relative_to(ROOT).as_posix() for directory in ("predecessor", "evidence")
              for p in (ROOT / directory).rglob("*")
              if p.is_file() and p.suffix != ".pyc"}
    need(actual == set(names), "closed frozen input inventory")
    for r in records:
        p = ROOT / r["path"]
        need(p.resolve().is_relative_to(ROOT.resolve()) and not p.is_symlink(), "contained source")
        data = p.read_bytes()
        need(hashlib.sha256(data).hexdigest() == r["sha256"], "frozen source SHA256")
        need(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
             == r["git_blob"], "frozen source Git blob")


@contextmanager
def frozen_probe():
    authenticate()
    saved = sys.modules.get("runtime")
    oldpath = sys.path[:]
    try:
        runtime = ModuleType("runtime")
        runtime.__file__ = str(ROOT / "predecessor/runtime.py")
        sys.modules["runtime"] = runtime
        exec(compile(Path(runtime.__file__).read_bytes(), runtime.__file__, "exec"), runtime.__dict__)
        probe = ModuleType("credited_pr2825_probe")
        probe.__file__ = str(ROOT / "predecessor/verify.py")
        exec(compile(Path(probe.__file__).read_bytes(), probe.__file__, "exec"), probe.__dict__)
        runtime.authenticate_dependencies()
        yield probe, runtime
    finally:
        sys.path[:] = oldpath
        if saved is None:
            sys.modules.pop("runtime", None)
        else:
            sys.modules["runtime"] = saved


def instrument(probe, quotas, warm, guard=True):
    """Check BEFORE zero(), including the request that a capacity guard rejects."""
    base = probe.Census
    instances = []

    class Pending(base):
        def __init__(self, m, arenas, bounds):
            for arena, count in zip(arenas, warm):
                held = [arena.zero() for _ in range(count)]
                # Non-LIFO reuse order is deliberately allowed.
                for w in held[::2] + held[1::2]:
                    arena.free(w)
            super().__init__(m, arenas, bounds)
            self.pending = [0] * len(arenas)
            self.requests = self.rejections = 0
            self.backing = tuple(len(a.words) for a in arenas)
            for j, a in enumerate(arenas):
                a.capacity = max(self.backing[j], self.entry[j] + quotas[j])
            self.capacities = tuple(a.capacity for a in arenas)
            instances.append(self)

        def allocate(self, arena):
            if arena in self.arenas:
                j = self.arenas.index(arena)
                demand = len(arena.live) + 1 - self.entry[j]
                self.pending[j] = max(self.pending[j], demand)
                self.requests += 1
                if guard:
                    need(demand <= self.bounds[j], "pending allocation budget")
                try:
                    return super().allocate(arena)
                except ValueError as e:
                    if str(e) == "fixed register inventory":
                        self.rejections += 1
                    raise
            return super().allocate(arena)

        def receipt(self):
            return {"entry_live": list(self.entry), "entry_backing": list(self.backing),
                    "capacity": list(self.capacities), "pending_peaks": self.pending,
                    "successful_live_peaks": self.peaks, "requests": self.requests,
                    "actual_quota_rejections": self.rejections}

    return Pending, instances


def caller(probe, runtime, good, rank, width, depth, warm=(0, 0),
           quotas=(4096, 41), expect_failure=False):
    Census, instances = instrument(probe, quotas, warm)
    with runtime.runtime() as m, patch.object(probe, "Census", Census):
        try:
            result = probe.caller_case(m, good, rank, width, depth, borrowed=3,
                                       callee_indices=22)
        except ValueError as e:
            need(expect_failure and str(e) == "fixed register inventory", "actual caller quota failure")
            need(instances[0].rejections == 1, "observed source capacity rejection")
            return {"good": good, "width": width, "depth": depth,
                    "failure": str(e), "quota": list(quotas), **instances[0].receipt()}
    need(not expect_failure, "underquota caller unexpectedly passed")
    c = instances[0]
    need(c.pending == c.peaks, "successful requests match postallocation peaks")
    return {"good": good, "rank": rank, "width": width, "depth": depth,
            "warm": list(warm), "trace_events": result["trace_events"],
            "callback_samples": result["callback_samples"], **c.receipt()}


def primitive(probe, runtime, kind, q, exponent, quota=6, expect_failure=False):
    Census, instances = instrument(probe, (quota,), (0,))
    with runtime.runtime() as m, patch.object(probe, "Census", Census):
        try:
            result = probe.primitive_case(m, kind, q, exponent, 1, 1, 1)
        except ValueError as e:
            need(expect_failure and str(e) == "fixed register inventory", "actual primitive quota failure")
            need(instances[0].rejections == 1, "observed primitive capacity rejection")
            return {"kind": kind, "q": q, "exponent": exponent,
                    "failure": str(e), **instances[0].receipt()}
    need(not expect_failure, "underquota primitive unexpectedly passed")
    return {"kind": kind, "q": q, "exponent": exponent,
            "payload_bits": result["payload_bits"], **instances[0].receipt()}


def add(probe, runtime, modulus, coefficient, quota=6, expect_failure=False):
    Census, instances = instrument(probe, (quota,), (0,))
    with runtime.runtime() as m:
        arena = m.words.Arena(modulus.bit_length()+1, 32)
        ring = m.words.Ring(arena.literal(modulus))
        resident = arena.literal(coefficient)
        count = m.cardinal_counts.Count.literal(1)
        extent = count.marginal()
        count.close()
        values = [int(((j*37+11) ^ (j >> 2)) % 11 < 5) for j in range(modulus**2)]
        source = m.records.Tape()
        for bit in values:
            source.append(bit)
        source.rewind()
        census = Census(m, (arena,), (6,))
        try:
            with ExitStack() as stack:
                census.install(stack)
                output, _ = m.stream.add_pass(source, ring, extent, extent, extent,
                                              lambda: arena.copy(resident))
        except ValueError as e:
            need(expect_failure and str(e) == "fixed register inventory", "actual ADD quota failure")
            need(census.rejections == 1, "observed ADD capacity rejection")
            return {"modulus": modulus, "coefficient": coefficient,
                    "failure": str(e), **census.receipt()}
        need(not expect_failure, "underquota ADD unexpectedly passed")
        expected = [values[x*modulus+(y-coefficient*x) % modulus]
                    for x in range(modulus) for y in range(modulus)]
        need(probe.tape_values(output) == expected, "complete Boolean ADD shear")
        need(probe.tape_values(source) == values and source.head == 1, "borrowed ADD payload")
        census.restored()
        need(census.pending[0] <= 6, "ADD six includes returned coefficient")
        output.clear(); source.clear(); extent.close()
        return {"modulus": modulus, "coefficient": coefficient, "payload_bits": len(values),
                **census.receipt()}


def run():
    with frozen_probe() as (probe, runtime):
        callers = [caller(probe, runtime, *args) for args in (
            (True, 1, 64, 0), (True, 42, 127, 4),
            (False, 1, 127, 4, (4100, 44)))]
        primitives = [primitive(probe, runtime, kind, q, exponent)
                      for kind in ("swap", "sign") for q, exponent in ((3, 1), (3, 3), (5, 2))]
        adds = [add(probe, runtime, modulus, coefficient)
                for modulus, coefficient in ((3, 0), (3, 1), (9, 8), (25, 7))]
        need(max(row["pending_peaks"][0] for row in adds) == 6, "ADD bound attained in fixture set")
        rejected = [caller(probe, runtime, True, 1, 64, 0, quotas=(4095, 41), expect_failure=True),
                    caller(probe, runtime, False, 1, 64, 0, quotas=(4096, 40), expect_failure=True)]
        rejected += [primitive(probe, runtime, kind, 3, 1, quota=5, expect_failure=True)
                     for kind in ("swap", "sign")]
        rejected.append(add(probe, runtime, 9, 8, quota=5, expect_failure=True))
    return {"status": "PASS_CALLER_PENDING_CAPACITY", "callers": callers,
            "primitives": primitives, "complete_adds": adds, "actual_underquota_failures": rejected,
            "closed_coefficient_bodies": "abstracted; PR2835 prefix theorem is a separate premise",
            "synthetic_child_callback_scratch_indices": 22,
            "full_selected_catalogue_or_GL64_payload": False, "no_new_kappa": True}


def compare_receipt(actual, expected):
    need(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
         "typed receipt equality")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true")
    args = ap.parse_args()
    result = run()
    if not args.emit:
        compare_receipt(result, read_json(ROOT / "RESULT.json"))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
