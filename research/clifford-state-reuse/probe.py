"""Bounded same-input probe; complete phase replay is a separate command."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

spec = importlib.util.spec_from_file_location("phase_reuse_harness", Path(__file__).with_name("verify.py"))
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


def cases(module, word):
    n = word["h"]
    frames = word["frames"]
    edges = sorted(set(map(tuple, word["edges"])) |
                   {(a, b) for center in word["center_frames"] for a, b in ((center, 0), (0, center))})
    selected = []
    for rank in (1, 2, 3, 4, 5, 8):
        matches = [(a, b) for a, b in edges if abs(len(frames[a]) - len(frames[b])) == rank]
        h.require(len(matches) >= 2, "Probe rank domain changed")
        selected.extend(("edge", rank, a, b) for a, b in (matches[0], matches[-1]))
    needed = {x for _, _, a, b in selected for x in (a, b)}
    for port in (0, len(word["ports"]) - 1):
        needed.update((word["start"][port], word["final"][word["v"] + port]))
    ops = {f: module.canonical_frame(n, frames[f]) for f in sorted(needed)}
    result = [(key, ops[key[2]].adjoint().then(ops[key[3]])) for key in selected]
    for port in (0, len(word["ports"]) - 1):
        q = word["ports"][port]
        for role, old, frame in [
            ("source", module.cgate(n, q), word["start"][port]),
            ("target", module.cgate(n, q).adjoint().then(module.fourier(n)), word["final"][word["v"] + port]),
        ]:
            result.append(((role, 0, port, frame), old.adjoint().then(ops[frame])))
    h.require(len(result) == 16, "Incomplete 16-case probe")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument("--word", type=Path, default=Path(__file__).resolve().parent / "data/CANONICAL-WORD.json.gz")
    p.add_argument("--work", type=Path, required=True)
    p.add_argument("--seconds", type=int, default=120)
    args = p.parse_args()
    h.require(__debug__, "Assertions must remain enabled")
    h.require(0 < args.seconds <= 120, "Probe budget must be 1 through 120 seconds")
    start = time.monotonic()
    root, work, word_path = args.root.resolve(), args.work.resolve(), args.word.resolve()
    data, word = h.prepare(root, word_path, work)
    h.check_generated(work)
    modules = {v: h.load_compiler(work / "compilers" / v / "clifford_exact.py", "probe_" + v)
               for v in ("baseline", "candidate")}
    objects = {v: cases(m, word) for v, m in modules.items()}
    records = []
    try:
        for round_id in range(3):
            outputs = {}
            counts = {}
            for variant in (("baseline", "candidate") if round_id % 2 == 0 else ("candidate", "baseline")):
                module = modules[variant]
                original = module.Op.zero_state
                counter = [0]
                def counted(op, basis=0, original=original, counter=counter):
                    counter[0] += 1
                    return original(op, basis)
                module.Op.zero_state = counted
                tick = time.monotonic()
                output = []
                try:
                    for key, op in objects[variant]:
                        h.require(time.monotonic() - start < args.seconds, "Probe budget exhausted")
                        before = copy.deepcopy((op.tab, op.circuit))
                        recipe, compiled = module.lower_child(op)
                        h.require(recipe["rank"] == key[1], "Probe rank mismatch")
                        h.require((op.tab, op.circuit) == before, "Input Op mutated")
                        output.append((key, recipe, compiled.tab, compiled.circuit))
                finally:
                    module.Op.zero_state = original
                outputs[variant] = output
                counts[variant] = counter[0]
                records.append({"round": round_id, "variant": variant,
                                "seconds": time.monotonic() - tick, "zero_state_calls": counter[0]})
            h.require(outputs["baseline"] == outputs["candidate"], "Probe recipes/tableaus/circuits differ")
            h.require(counts["baseline"] - counts["candidate"] == 40, "Unexpected evaluation reduction")
        h.sources(root)
        h.check_generated(work)
        h.require(word_path.read_bytes() == data, "Original input changed")
        h.require(time.monotonic() - start < args.seconds, "Probe budget exhausted during final checks")
        result = {"status": "PASS_EXACT_16_CASE_PHASE_REUSE_PROBE", "seed": 88,
                  "cases": [list(k) for k, op in objects["baseline"]], "timings": records,
                  "source_pins": h.PINS, "candidate_sha256": h.CANDIDATE_SHA,
                  "redundant_evaluations_removed_per_round": 40,
                  "scope": "16 operators only, no complete-phase or default-chain claim"}
        h.write_json(work / "PROBE.json", result)
        print(json.dumps(result, sort_keys=True), flush=True)
    except Exception as error:
        h.write_json(work / "PROBE.json", {"status": "FAILED_OR_INCOMPLETE", "error": str(error), "timings": records})
        raise


if __name__ == "__main__":
    main()
