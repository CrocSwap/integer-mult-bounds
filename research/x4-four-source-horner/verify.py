#!/usr/bin/env python3
"""Exact four-source X4 Horner construction; finite scalar evidence, no kappa."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import circuits as C

INPUT = "research/complex-x4-compensation-pairs/inputs/"
BASE = "007664306fff84fbb1c9a1b4053b69f439764034"
REQUIRED = {
    INPUT + "CANONICAL-WORD.json.gz", INPUT + "LOCAL-PROGRAMS.json.gz", INPUT + "LOCAL-CHECKS.json",
    "research/complex-x4-compensation-pairs/SOURCES.json", "research/complex-dyadic-lowering/lower.py",
    "research/gauge44-frames-x/PROOF-NOTE-FRAMES-X4.md",
    "research/gauge44-frames-x/construction/jx/LOCAL-PINS-jx-X4.json",
    "certificates/checkpoints/frontier799.json", "docs/research/community-frontier799-review.md",
}
need = C.need


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()


def read(p):
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == ".gz" else b)


def inputs(root=ROOT):
    pins = read(HERE / "SOURCES.json")
    need(pins["base_commit"] == BASE, "source base")
    need(REQUIRED == set(pins["files"]), "missing or unexpected source pin")
    for name, record in pins["files"].items():
        b = (root / name).read_bytes()
        need(hashlib.sha256(b).hexdigest() == record["sha256"], "source digest: " + name)
        need(hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest() == record["git_blob"], "source blob: " + name)
    word = read(root / INPUT / "CANONICAL-WORD.json.gz")
    programs = read(root / INPUT / "LOCAL-PROGRAMS.json.gz")
    checks = read(root / INPUT / "LOCAL-CHECKS.json")
    need((word["v"], word["R"]) == (112, 504), "X4 dimensions")
    for orientation in ("forward", "backward"):
        need(digest(programs[orientation]) == checks[orientation]["sha256"], "source program binding")
    return word, programs, checks


class Replay:
    def __init__(self, n=728):
        regs = [("L", i) for i in range(n)] + [("C", i) for i in range(8)] + [C.WORK]
        self.rows = {r: {i: Q(1)} for i, r in enumerate(regs)}
        self.envelope = {r: Q(1) for r in regs}; self.positive_peak = Q(1)
        self.count = 0; self.opcodes = Counter(); self.peak = Q(1); self.grid = 0
        self.operand_reads = 0; self.nonwork_source_reads = 0; self.work_source_reads = 0

    def apply(self, op):
        tag, target = op[0], tuple(op[1])
        need(target in self.rows, "unknown target")
        if tag == "clear":
            row = {}; bound = Q(0)
        elif tag == "copy":
            source = tuple(op[2]); row = dict(self.rows[source]); self.operand_reads += 1
            self.nonwork_source_reads += source != C.WORK
            bound = self.envelope[source]
        elif tag in ("double", "halve", "negate"):
            factor = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
            row = {j: x * factor for j, x in self.rows[target].items()}; self.operand_reads += 1
            bound = self.envelope[target] * abs(factor)
        elif tag in ("add", "subtract"):
            source = tuple(op[2]); need(source != target, "primitive alias")
            sign = 1 if tag == "add" else -1
            row = dict(self.rows[target]); self.operand_reads += 2
            self.nonwork_source_reads += source != C.WORK
            bound = self.envelope[target] + self.envelope[source]
            for j, x in self.rows[source].items():
                value = row.get(j, Q(0)) + sign*x
                if value: row[j] = value
                else: row.pop(j, None)
        else:
            raise ValueError("unknown primitive")
        self.rows[target] = row; self.count += 1; self.opcodes[tag] += 1
        self.envelope[target] = bound; self.positive_peak = max(self.positive_peak, bound)
        if tag in ("copy", "add", "subtract") and target == C.WORK and tuple(op[2]) != C.WORK:
            self.work_source_reads += 1
        self.peak = max(self.peak, sum(map(abs, row.values()), Q(0)))
        for value in row.values():
            need(value.denominator & (value.denominator-1) == 0, "nondyadic prefix")
            self.grid = max(self.grid, value.denominator.bit_length()-1)

    def endpoint(self, backward=True):
        for r in range(728):
            expected = {r: Q(1)}
            if backward and r < 112: expected[r+112] = Q(-1)
            if not backward and 112 <= r < 224: expected[r-112] = Q(1)
            need(self.rows[("L", r)] == expected, "scalar endpoint row " + str(r))
        need(all(not row for r, row in self.rows.items() if r[0] != "L"), "dirty private endpoint")

    def receipt(self):
        return dict(per_component_primitives=self.count, real_component_primitives=2*self.count,
                    exact_prefix_row_l1=str(self.peak), exact_prefix_fraction_bits=self.grid,
                    positive_prefix_row_l1=str(self.positive_peak), work_source_reads=self.work_source_reads,
                    per_component_opcodes=dict(sorted(self.opcodes.items())),
                    operand_reads=self.operand_reads, nonwork_source_reads=self.nonwork_source_reads)


def local_check(window, primitive_word=None):
    target = tuple(window[0][1][1]); regs = [target] + [tuple(e[1][2]) for e in window] + [C.WORK]
    replay = Replay(); replay.rows = {r: {i: Q(1)} for i, r in enumerate(regs)}
    replay.envelope = {r: Q(1) for r in regs}
    for op in primitive_word if primitive_word is not None else C.joint(window): replay.apply(op)
    expected = {0: Q(1)}
    expected.update({i+1: C.coefficient(e[1]) for i,e in enumerate(window)})
    need(replay.rows[target] == expected, "joint local target")
    need(not replay.rows[C.WORK], "joint dirty work not cleared")
    for i, r in enumerate(regs[1:-1], 1): need(replay.rows[r] == {i: Q(1)}, "source changed")


def replay_full(events, recipe):
    before, after = Replay(), Replay()
    choices = dict(recipe); i = 0; boundaries = 0
    while i < len(events):
        event = events[i]
        if i in choices:
            length = choices[i]; window = events[i:i+length]
            for e in window:
                for op in C.lower(e[1]): before.apply(op)
            for op in C.joint(window): after.apply(op)
            target = tuple(event[1][1])
            need(before.rows[target] == after.rows[target] and not before.rows[C.WORK] and not after.rows[C.WORK], "window boundary")
            boundaries += 1; i += length
        else:
            if event[0] == "scalar":
                for op in C.lower(event[1]): before.apply(op); after.apply(op)
            i += 1
    before.endpoint(); after.endpoint()
    need(before.rows == after.rows, "full endpoint differs")
    return before.receipt(), after.receipt(), boundaries


def verify(root=ROOT):
    word, programs, checks = inputs(root)
    events = programs["backward"]; rows = C.census(events)
    recipe, saving = C.choose(events, rows)
    pairs, pair_saving = C.choose(events, rows, 2)
    for row in rows: local_check(events[row["start"]:row["start"]+row["length"]])
    before, after, boundaries = replay_full(events, recipe)
    need(before["real_component_primitives"] == 143674, "PR696 baseline count")
    need(pair_saving*2 == 13072 and len(pairs) == 1586, "PR945 pair comparator")
    need(before["per_component_primitives"] - after["per_component_primitives"] == saving, "complete saving")
    need(after["exact_prefix_fraction_bits"] <= before["exact_prefix_fraction_bits"], "full scalar grid increased")
    need(Q(after["exact_prefix_row_l1"]) <= Q(before["exact_prefix_row_l1"]), "full scalar prefix increased")
    need(Q(after["positive_prefix_row_l1"]) <= Q(before["positive_prefix_row_l1"]), "full positive envelope increased")
    emitted = list(C.emitted(events, recipe)); baseline = list(C.emitted(events, []))
    need([e for e in emitted if e[0] != "primitive"] == [e for e in events if e[0] != "scalar"], "non-scalar stream")
    forward_count = sum(len(C.lower(e[1])) for e in programs["forward"] if e[0] == "scalar")*2
    import independent as I
    independent = I.run(recipe=recipe)
    alternate_rows = [[r["start"],r["length"],r["before"],r["after"],r["saving"]] for r in rows]
    need(alternate_rows == I.census(events,4), "independent complete census differs")
    for label, actual, stream in (("backward_baseline", before, baseline), ("backward_candidate", after, emitted)):
        other = independent[label]
        need(other["real_component_primitives"] == actual["real_component_primitives"], "independent price")
        need(other["primitive_histogram"] == actual["per_component_opcodes"], "independent opcodes")
        need(other["stream_sha256"] == digest(stream), "independent emitted stream")
        need(Q(*other["exact_prefix_l1"]) == Q(actual["exact_prefix_row_l1"]), "independent exact prefix")
        need(Q(*other["positive_prefix_l1"]) == Q(actual["positive_prefix_row_l1"]), "independent positive prefix")
        need(other["max_grid_exponent"] == actual["exact_prefix_fraction_bits"], "independent grid")
        need(other["operand_reads"] == actual["operand_reads"] and other["source_reads_into_work"] == actual["work_source_reads"]
             and other["nonwork_source_reads"] == actual["nonwork_source_reads"], "independent reads")
    need(independent["forward_retained"]["real_component_primitives"] == forward_count, "forward retained invoice")
    result = dict(status="PASS_X4_FOUR_SOURCE_HORNER", base_commit=BASE, assignment_seed=22,
                  candidate_counts=dict(sorted(Counter(r["length"] for r in rows).items())),
                  candidates_sha256=digest(rows), recipe=recipe, recipe_sha256=digest(recipe),
                  selected_lengths=dict(sorted(Counter(n for _,n in recipe).items())),
                  before=before, after=after, boundaries=boundaries, formal_columns=737,
                  pair_only_saved_real=2*pair_saving, pair_only_windows=len(pairs),
                  saved_real=2*saving, extra_beyond_pairs_real=2*(saving-pair_saving),
                  forward_retained_real=forward_count, orientation_max_before=max(forward_count,before["real_component_primitives"]),
                  orientation_max_after=max(forward_count,after["real_component_primitives"]),
                  baseline_stream_sha256=digest(baseline), candidate_stream_sha256=digest(emitted),
                  non_scalar_sha256=digest([e for e in events if e[0] != "scalar"]),
                  local_candidate_identities=len(rows), no_new_kappa=True)
    result["independent"] = independent
    result["eligible_beyond_clear_only"] = sum(r["saving"] > r["length"]-1 for r in rows)
    return result


def main():
    p=argparse.ArgumentParser(); p.add_argument("--write", type=Path); p.add_argument("--json", action="store_true")
    p.add_argument("--emit", type=Path, help="save the checked complete backward primitive event stream to a new JSON file")
    args=p.parse_args()
    for destination in (args.write, args.emit):
        if destination is not None: need(not destination.exists(), "output already exists")
    result=verify()
    if args.write:
        with args.write.open("x") as f: f.write(json.dumps(result,indent=2,sort_keys=True)+"\n")
    else:
        need(canonical(result) == canonical(read(HERE / "EXPECTED.json")), "result receipt mismatch")
    if args.emit:
        _, programs, _ = inputs()
        stream = list(C.emitted(programs["backward"], result["recipe"]))
        need(digest(stream) == result["candidate_stream_sha256"], "emitted output hash")
        with args.emit.open("x") as f: f.write(canonical(stream)+"\n")
    if args.json: print(json.dumps(result, sort_keys=True))
    print("PASS_X4_FOUR_SOURCE_HORNER candidates=%d windows=%d saved=%d extra_vs_pairs=%d columns=737 no_new_kappa" %
          (result["local_candidate_identities"], result["boundaries"], result["saved_real"], result["extra_beyond_pairs_real"]))


if __name__ == "__main__": main()
