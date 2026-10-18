#!/usr/bin/env python3
"""Source-pinned finite JP8 circuit replay; standard library, no writes by default.

Michał Ciemięga (@zewelor), with substantial OpenAI Codex assistance.
Apache-2.0. The sparse dyadic-row representation follows the independent
integer replay in Philipp's PR882; code here is newly written. PR696 supplies
the unchanged reference lowering. This does not execute physical frame events.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from lower import lower

BASE = "007664306fff84fbb1c9a1b4053b69f439764034"
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/"
REFERENCE = "research/complex-dyadic-lowering/lower.py"
SPEC = "research/complex-k492-owner-repair/data/SPEC.json"
CHECKPOINT = "certificates/checkpoints/k492626.json"
FILES = {REFERENCE, SPEC, CHECKPOINT,
         PROVIDER + "LOCAL-PROGRAMS.json.gz", PROVIDER + "LOCAL-CHECKS.json",
         PROVIDER + "INDEPENDENT-LOCAL-REPLAY.json"}
WORK = ("W", 0)
PRIVATE = (WORK,) + tuple(("C", i) for i in range(8))
REGISTERS = tuple(("L", i) for i in range(716)) + PRIVATE


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def source_check(root=ROOT):
    pins = read(HERE / "SOURCES.json")
    need(pins["base_commit"] == BASE, "wrong source base")
    need(set(pins["files"]) == FILES, "source inventory mismatch")
    for name, pin in pins["files"].items():
        data = (root / name).read_bytes()
        expected_kind = "decompressed-payload" if name.endswith(".gz") else "exact-bytes"
        need(pin["representation"] == expected_kind, "source representation mismatch")
        if name.endswith(".gz"):
            data = gzip.decompress(data)
        need(hashlib.sha256(data).hexdigest() == pin["sha256"], "source pin mismatch: " + name)
    checkpoint, spec = read(root / CHECKPOINT), read(root / SPEC)
    need(checkpoint["audited_source_head"] == "660de893d27bb7abd1d5b01b1640207528a5c851",
         "historical source head mismatch")
    need(Q(checkpoint["kappa"]) == Q(spec["expected"]["kappa"]), "checkpoint/SPEC mismatch")
    return spec["providers"]["jp8"]


def load_reference():
    spec = importlib.util.spec_from_file_location("pr696_direct_reference", ROOT / REFERENCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.lower


def row(numerators, depth=0):
    """Canonical sparse integer row divided by 2**depth."""
    numerators = {k: v for k, v in numerators.items() if v}
    if not numerators:
        return (0, {})
    common = min([depth] + [(abs(v) & -abs(v)).bit_length() - 1 for v in numerators.values()])
    return depth - common, {k: v >> common for k, v in numerators.items()}


def scale(value, q):
    need(q.denominator & (q.denominator - 1) == 0, "nondyadic row scale")
    return row({k: v * q.numerator for k, v in value[1].items()},
               value[0] + q.denominator.bit_length() - 1)


def add(left, right, sign=1):
    depth = max(left[0], right[0])
    result = {k: v << (depth - left[0]) for k, v in left[1].items()}
    for k, v in right[1].items():
        result[k] = result.get(k, 0) + sign * (v << (depth - right[0]))
    return row(result, depth)


def initial():
    return {register: (0, {i: 1}) for i, register in enumerate(REGISTERS)}


def macro(rows, op):
    """Direct mathematical oracle, independent of primitive lowering."""
    tag, target = op[0], tuple(op[1])
    if tag == "clear":
        rows[target] = (0, {})
    elif tag == "copy":
        rows[target] = rows[tuple(op[2])]
    elif tag == "scale":
        rows[target] = scale(rows[target], Q(op[2], op[3]))
    elif tag == "add":
        rows[target] = add(rows[target], scale(rows[tuple(op[2])], Q(op[3], op[4])))
        rows[WORK] = (0, {})
    else:
        raise ValueError("unknown macro")


class Replay:
    def __init__(self):
        self.rows = initial()
        self.counts = Counter()
        self.source_reads = self.operand_reads = self.depth = 0
        self.peak = Q(1)
        self.stream = hashlib.sha256()

    def step(self, instruction, event_index, frame, macro_source):
        tag, target = instruction[:2]
        need(target in self.rows, "unknown primitive target")
        source = instruction[2] if len(instruction) == 3 else None
        need(len(instruction) == (3 if tag in ("copy", "add", "subtract") else 2),
             "primitive arity")
        if source is not None:
            need(source in self.rows and source != target, "unknown or aliased source")
        reads = ([] if tag == "clear" else [source] if tag == "copy"
                 else [target, source] if source is not None else [target])
        self.operand_reads += len(reads)
        self.source_reads += reads.count(macro_source) if macro_source else 0
        if tag == "clear":
            self.rows[target] = (0, {})
        elif tag == "copy":
            self.rows[target] = self.rows[source]
        elif tag in ("add", "subtract"):
            self.rows[target] = add(self.rows[target], self.rows[source], 1 if tag == "add" else -1)
        elif tag in ("double", "halve", "negate"):
            self.rows[target] = scale(self.rows[target], {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag])
        else:
            raise ValueError("unknown primitive")
        d, values = self.rows[target]
        self.depth = max(self.depth, d)
        self.peak = max(self.peak, Q(sum(abs(v) for v in values.values()), 1 << d))
        self.counts[tag] += 2
        self.stream.update((canonical([event_index, frame, instruction]) + "\n").encode())

    def receipt(self):
        return {"real_primitives": sum(self.counts.values()), "primitive_counts": dict(sorted(self.counts.items())),
                "real_macro_source_reads": 2*self.source_reads, "real_operand_reads": 2*self.operand_reads,
                "maximum_denominator_depth": self.depth, "maximum_row_l1": str(self.peak),
                "stream_sha256": self.stream.hexdigest()}


def replay(direction, events, checks, inherited, baseline):
    old, new, oracle = Replay(), Replay(), initial()
    changed, census, phases, frames, paid = [], Counter(), Counter(), Counter(), Counter()
    nonscalar = hashlib.sha256()
    phase = None
    macros = 0
    for index, event in enumerate(events):
        if event[0] != "scalar":
            need(event[0] in ("phase", "center", "climb", "adapter", "residual_adapter"), "unknown event")
            if event[0] == "phase":
                phase = event[1]
            elif event[0] in ("center", "climb"):
                paid[str(event[4 if event[0] == "center" else 5])] += 1
            nonscalar.update((canonical([index, event]) + "\n").encode())
            continue
        need(len(event) == 3, "scalar event arity")
        op, frame = event[1:]
        target = tuple(op[1])
        source = tuple(op[2]) if op[0] in ("add", "copy") else None
        original, replacement = baseline(op), lower(op, baseline)
        if replacement != original:
            q = Q(op[3], op[4])
            need(op[0] == "add" and abs(q) in (2, 3), "changed outside claimed domain")
            need(len(original) - len(replacement) == 1, "unexpected local cost")
            changed.append(index)
            census[str(q)] += 1
            phases[str(phase)] += 1
            frames[str(frame)] += 1
        for machine, word in ((old, original), (new, replacement)):
            for instruction in word:
                need(instruction[1] in ({target, WORK} if op[0] == "add" else {target}), "extra primitive write")
                if len(instruction) == 3:
                    need(instruction[2] in {target, source, WORK}, "extra primitive read")
                machine.step(instruction, index, frame, source)
        macro(oracle, op)
        for machine in (old, new):
            need(machine.rows[target] == oracle[target], f"{direction} event {index}: target boundary")
            need(machine.rows[WORK] == oracle[WORK], f"{direction} event {index}: work boundary")
        macros += 1
    for i in range(716):
        expected = {i: 1}
        if direction == "forward" and 112 <= i < 224:
            expected[i-112] = 1
        elif direction == "backward" and i < 112:
            expected[i+112] = -1
        for machine in (old, new):
            need(machine.rows[("L", i)] == (0, expected), "full endpoint mismatch")
    for machine in (old, new):
        need(all(machine.rows[r] == (0, {}) for r in PRIVATE), "private dirt survived")
        need(machine.rows == oracle, "full oracle mismatch")
    need(macros == checks["scalar_macros"] and len(events) == checks["events"], "event census mismatch")
    need(dict(paid) == checks["paid_profile"] == inherited["paid_profiles"][direction], "paid profile mismatch")
    a, b = old.receipt(), new.receipt()
    need(a["real_primitives"] - b["real_primitives"] == 2*len(changed), "complete cost mismatch")
    need(b["real_macro_source_reads"] - a["real_macro_source_reads"] == 2*len(changed), "source access mismatch")
    need(a["real_operand_reads"] == b["real_operand_reads"], "operand access mismatch")
    need(new.depth <= old.depth and new.peak <= old.peak, "prefix budget increased")
    need(new.peak <= Q(inherited["local"][direction]["prefix_l1_upper"]), "inherited envelope exceeded")
    return {"events": len(events), "macros": macros, "exact_input_columns": 725,
            "dirty_helpers_restored": 492, "private_registers_cleared": 9,
            "changed_macros": len(changed), "changed_event_indices": changed,
            "coefficient_census": dict(sorted(census.items())), "phase_census": dict(sorted(phases.items())),
            "frame_census": dict(sorted(frames.items())), "paid_profile": dict(sorted(paid.items())),
            "retained_nonscalar_sha256": nonscalar.hexdigest(), "baseline": a, "candidate": b,
            "saved_real_primitives": a["real_primitives"] - b["real_primitives"]}


def collect():
    provider = source_check()
    baseline = load_reference()
    import controls
    programs = read(ROOT / (PROVIDER + "LOCAL-PROGRAMS.json.gz"))
    checks = read(ROOT / (PROVIDER + "LOCAL-CHECKS.json"))
    inherited = read(ROOT / (PROVIDER + "INDEPENDENT-LOCAL-REPLAY.json"))
    need(set(programs) == {"forward", "backward"}, "orientation coverage")
    need(digest(programs) == provider["artifact_semantic_sha256"]["LOCAL-PROGRAMS.json.gz"], "SPEC payload mismatch")
    result = {}
    for direction in ("forward", "backward"):
        need(digest(programs[direction]) == checks[direction]["sha256"] == provider["program_hashes"][direction], "program source binding")
        result[direction] = replay(direction, programs[direction], checks[direction], inherited, baseline)
    return {"schema": "jp8-direct-small-integers/1", "status": "finite scalar construction; no new kappa",
            "base_commit": BASE, "assignment_seed": 29,
            "programs": result, "local_controls": controls.run(baseline)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt; refuse an existing path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.write and args.write.exists():
        parser.error("output already exists")
    receipt = collect()
    if args.write:
        with args.write.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(receipt, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    else:
        need(canonical(receipt) == canonical(read(HERE / "EXPECTED.json")), "expected receipt mismatch")
    if args.json:
        print(json.dumps(receipt, indent=2))
    print("PASS_JP8_DIRECT_SMALL_INTEGERS macros=1424+1424 saved=2848/2848 columns=725 no_new_kappa")


if __name__ == "__main__":
    main()
