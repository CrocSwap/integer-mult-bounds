#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the retained resource engines on the exact lowered #7636 pair."""

import argparse
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import runpy
import signal
import sys
import time


HEAD = "7e68d8dd62d9a38c0f3c942262a7a85ca7125b75"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
PARENTS = {
    "source": ("98b8c12ece2f323a6ff5cac8c7ed2f78ba3835438ea56b16bd7d4698ec5ad5b2",
               "1b4e33c3e3b69d1f1b42d019a2e372ac612fa28494bd8da18a734618f9bda659", 150836, 202668),
    "candidate": ("375f924e1588893680d39a194d29e5400bec4ab7e0b5db24b05f4cfe6fd05e15",
                  "3fb11603e14fc9d67aff97e1b0e737f98c1395180ff71119fa64b4d8acaa8626", 150834, 202666),
}
PREFLIGHT = "532be27b5689df79b9b843a639137bd6da353974d526a460cbabd44cbf3ce5f7"
MANIFEST = "8851d08cacad58e70ee4c63eecd922673e0ff6baa7a85338e4489c4e69591708"
OLD_ADD = ["ADD", 841, 284, "23184221/921600", 127]
LOWERED_ADDS = [["ADD", 841, 284, "25", 127], ["ADD", 841, 284, "144221/921600", 127]]


def require(test, message):
    if not test:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read(path, pin):
    raw = path.read_bytes()
    require(digest(raw) == pin, f"SHA-256 mismatch: {path.name}")
    return raw


def write(path, data):
    with path.open("x") as out:
        json.dump(data, out, sort_keys=True, indent=2)
        out.write("\n")


def stamp():
    return datetime.now(timezone.utc).isoformat()


def word_pin(spec, root, case):
    old_raw, old_gzip, clock, count = PARENTS[case]
    raw = gzip.decompress(read(root / spec["parent"], old_gzip))
    require(digest(raw) == old_raw, "exact unlowered input")
    word = spec["word"]
    path = (root / word["path"]).resolve()
    repaired_raw = gzip.decompress(read(path, word["gzip_sha256"]))
    require(digest(repaired_raw) == word["raw_sha256"], "exact lowered word bytes")
    original, repaired = map(json.loads, (raw, repaired_raw))
    program = original["program"]
    require(digest(canonical(repaired)) == word["canonical_sha256"], "canonical lowered bytes")
    require(len(program) == count and program[clock] == OLD_ADD, "exact original lowering clock")
    require(repaired == {**original, "program": program[:clock] + LOWERED_ADDS + program[clock + 1:]},
            "complete authorized scalar lowering")
    require((repaired["public"], repaired["owned_fields"], len(repaired["live"])) == (1501, 68, 104)
            and [repaired["initial"][r] for r in (457, 461)] == [281, 285], "the 180-CLEAR interface")
    return {**word, "head": HEAD, "path": path, "lifetimes": 180}


def prepare(evidence, out):
    manifest = json.loads(read(evidence / "SOURCE-INPUTS.json", MANIFEST))
    for name, pin in manifest["resource_engine_files"].items():
        read(evidence / name, pin["sha256"])
    resource_replay = evidence / "resource-replay"
    source = resource_replay / "preflight.py"
    read(source, PREFLIGHT)
    runner = runpy.run_path(str(source))
    runner["grid"].__globals__.update(RESOURCES=resource_replay / "engines",
                                      VENDOR=resource_replay / "engines" / "vendor", ACTIVE_OUT=out)
    return runner


def run(spec, root, case, evidence, out, cpu_seconds, wall):
    pin = word_pin(spec, root, case)
    runner = prepare(evidence, out)
    literal = runner["literal_inventory"](runner["identity"](pin))
    require(not literal["failures_by_guard"], "retained literal guards on the lowered word")
    runner["grid"](pin, cpu_seconds, wall)
    grid = json.loads((out / "GRID.json").read_bytes())
    fields = {"compressed_word_sha256": "gzip_sha256", "decompressed_sha256": "raw_sha256",
              "canonical_word_sha256": "canonical_sha256"}
    require(grid["status"] == "FINITE_GRID_AND_ENVELOPE_ONLY" and grid["caller_sha256"] == CALLER
            and all(grid[key] == pin[value] for key, value in fields.items()), "bound grid receipt")
    census = grid["native_envelope"]["census"]
    require((census["lifetimes"], census["peak_owned"], census["owned_labels"]) == (180, 50, 68),
            "grid bound to the 180-lifetime model")
    require(grid["context_c"] <= 4096 and grid["context_le_4096"]
            and grid["integer_grid"]["numerator_bits"] <= 24, "retained context and width guards")
    scale = grid["integer_grid"]["odd_scale_lcm"]
    runner["quick"](pin, scale)
    tariff = json.loads((out / "TARIFF.json").read_bytes())
    require(tariff["strict_ceiling_met"] and tariff["native_conversion_sites"] == 51034
            and tariff["canonical_sha256"] == pin["canonical_sha256"], "complete ordinary ceiling")
    read(pin["path"], pin["gzip_sha256"])
    captured = ["GRID.json", "LITERALS.json", "ORDINARY.json", "TAPE-SCALAR.json", "TARIFF.json"]
    return {"status": "PASS_LOWERED_7636_RESOURCE", "case": case, "caller_sha256": CALLER, "source_head": HEAD,
            "canonical_sha256": pin["canonical_sha256"], "odd_scale": scale, "context": grid["context_c"],
            "ordinary_upper": tariff["conservative_total"],
            "receipts": {name: digest((out / name).read_bytes()) for name in captured}}


def main():
    require(sys.version_info[:2] == (3, 12) and sys.flags.isolated and sys.dont_write_bytecode and __debug__,
            "use Linux Python 3.12 -I -B with assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True, help="retained #7660 application-evidence tree")
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--go", type=Path, required=True)
    parser.add_argument("--case", choices=PARENTS, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    config = args.spec.resolve()
    spec_bytes = config.read_bytes()
    spec = json.loads(spec_bytes)
    require(spec["source_head"] == HEAD and spec["scope"] == "7636-lowered-paired-resource", "exact resource scope")
    out = args.out.resolve()
    out.mkdir(exist_ok=False)
    write(out / "START-GUARD.json", {"started": stamp(), "case": args.case, "scope": spec["scope"],
                                     "spec_sha256": digest(spec_bytes), "adapter_sha256": digest(Path(__file__).read_bytes())})

    def interrupted(signum, _frame):
        raise InterruptedError(f"resource signal {signum}")

    for signum in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT, signal.SIGXCPU):
        signal.signal(signum, interrupted)
    signal.alarm(120)
    try:
        while not args.go.exists():
            time.sleep(0.2)
        go = json.loads(args.go.read_bytes())
        require(go["status"] == "GO" and go["scope"] == spec["scope"] and go["spec_sha256"] == digest(spec_bytes)
                and go["event_id"] and go["receipt_id"] and go["public_claim"], "recorded exact resource authorization")
        cap = go["bounds"][args.case]
        cpu, wall, cpu_seconds = cap["cpu"], cap["wall_seconds"], cap["cpu_seconds"]
        require(cpu in os.sched_getaffinity(0) and 0 < cpu_seconds <= 420 and 0 < wall <= 420,
                "one available CPU and bounded resource gate")
        os.sched_setaffinity(0, {cpu})
        resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
        write(out / "START.json", {"started": stamp(), "case": args.case, "authorization": go})
        signal.alarm(wall)
        result = run(spec[args.case], config.parent, args.case, args.evidence.resolve(), out, cpu_seconds, wall)
        signal.alarm(0)
        write(out / "RESULT.json", result)
    except BaseException as error:
        signal.alarm(0)
        write(out / "EXIT.json", {"ended": stamp(), "status": "INCOMPLETE", "failure": repr(error)})
        raise
    write(out / "EXIT.json", {"ended": stamp(), "status": "COMPLETE",
                               "result_sha256": digest((out / "RESULT.json").read_bytes())})
    print(result["status"], args.case, result["canonical_sha256"], flush=True)


if __name__ == "__main__":
    main()
