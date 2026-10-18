#!/usr/bin/env python3
"""Check the complete high-scaling physical scratch interval."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime import PACKAGE, load, prepare, require, run


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def exhaustion(runtime, s, inverse):
    """Actual one-role-short rejection, without a failure-cleanup claim."""
    state = prepare(runtime, 3, 1, s, 6 + (s > 1), 0, False)
    arena, modulus, ring, before, suffix, pool, held, source = state
    try:
        with pool.install():
            runtime.kernels.doubled(source, ring, before, suffix, pool.acquire, inverse)
    except ValueError as error:
        require(
            str(error) == "fixed scratch role inventory exhausted", "inventory failure"
        )
    else:
        raise ValueError("one-role-short call accepted")
    stranded = len(pool.live)
    # The harness owns a failed fixture. This is not source exception safety.
    for lease in tuple(pool.live.values()):
        lease.clear()
    pool.empty()
    source.clear()
    before.close()
    suffix.close()
    ring.close()
    arena.free(modulus)
    return {"s": s, "inverse": inverse, "stranded": stranded, "held": len(held)}


def result():
    runtime = load()
    rows = []
    for q in (3, 5, 7, 9, 15, 17, 25, 31, 33, 63, 65, 127, 129):
        for b in (1, 2, 5):
            for s in (1, 2, 3, 5, 7):
                for inverse in (False, True):
                    rows.append(run(runtime, q, b, s, inverse))
    warm = [
        run(runtime, 9, 2, s, inverse, occupied=3, pooled_source=pooled)
        for s in (1, 3)
        for inverse in (False, True)
        for pooled in (False, True)
    ]
    short = [
        exhaustion(runtime, s, inverse) for s in (1, 3) for inverse in (False, True)
    ]
    for first, second in zip(rows[::2], rows[1::2], strict=True):
        require(first["traffic"] == second["traffic"], "equal directional traffic")
    return {
        "status": "PASS_HIGH_SCALING_SCRATCH_TRAFFIC",
        "cases": len(rows),
        "bits": sum(r["q"] * r["b"] * r["s"] for r in rows),
        "rows_sha256": digest(rows),
        "warm": warm,
        "exhaustion": short,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    actual = result()
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    expected = json.loads((PACKAGE / "RESULT.json").read_bytes())
    require(
        json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "complete typed receipt mismatch",
    )
    print(
        actual["status"], "cases=" + str(actual["cases"]), "bits=" + str(actual["bits"])
    )


if __name__ == "__main__":
    main()
