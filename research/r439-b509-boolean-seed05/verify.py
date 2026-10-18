#!/usr/bin/env python3
"""Finite frame-509 Boolean splice; no supplier adoption or kappa claim.

Hanson Sun (@bbMisk), substantial OpenAI Codex assistance. Apache-2.0.
Scalar receipt conventions follow Cinna Davis PR973 / Jerry Chen PR906 and
Gareth Davidson's six-wire Boolean package. Their implementations are not
imported. The original E8 checker and exporter are run unchanged and pinned.
"""
import argparse
import ast
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "1b59b624d21924f8e3537cdc1ac52d3be6eda2fe"
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
PRIOR = "research/r439-frame509-seed08/CANDIDATE.json"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
BIT = "research/e8-bit-carrier-skeleton/code/bit"
EXPORTER = BIT + "/export_records.py"
START, STOP, FRAME = 283, 314, 509
WIRES = [17, 22, 33, 38, 50, 60, 67, 77, 87, 92, 468]
SOURCE_PATHS = {
    WORD, PRIOR, CHECKER, EXPORTER, BIT + "/regression/stage_cohort.py",
    "research/e8-bit-carrier-skeleton/portable-include/bits/stdc++.h",
    *(BIT + "/checkers/" + name for name in
      ("legality_h.cpp", "columns_h.cpp", "columns_k.cpp", "json.hpp")),
    "research/r439-frame509-seed08/NOTICE.md",
    "research/e8-bit-p111-tuned/NOTICE.md",
    "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/"
    "e8-r715-eleven-stage-whole/code/global_k.py",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def strict_pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def load(path):
    raw = Path(path).read_bytes()
    if str(path).endswith(".gz"):
        raw = gzip.decompress(raw)
    return json.loads(raw, object_pairs_hook=strict_pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")


def pins(root):
    manifest = load(HERE / "SOURCES.json")
    need(manifest["base_commit"] == BASE, "base pin")
    need(set(manifest["files"]) == SOURCE_PATHS, "source inventory")
    for name, item in manifest["files"].items():
        raw = (root / name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source SHA256: " + name)
        header = ("blob " + str(len(raw)) + "\0").encode()
        need(hashlib.sha1(header + raw).hexdigest() == item["git_blob"], "source Git blob: " + name)
    return manifest


def operations(gates):
    out = []
    for gate in gates:
        need(type(gate) is list and len(gate) == 3, "gate shape")
        frame, dst, srcs = gate
        need(type(frame) is int and frame == FRAME, "block frame")
        need(type(dst) is int and dst in WIRES, "block destination")
        need(type(srcs) is list and len(srcs) == 1 and type(srcs[0]) is int
             and srcs[0] in WIRES and dst != srcs[0], "block source")
        out.append((dst, srcs[0]))
    return out


def column_map(gates, modulus=None):
    # Scalar unit inputs, independent of the discovery's packed-row matrices.
    ops = operations(gates)
    columns = []
    for initial in WIRES:
        values = {w: int(w == initial) for w in WIRES}
        for dst, src in ops:
            values[dst] += values[src]
            if modulus:
                values[dst] %= modulus
        columns.append([values[w] for w in WIRES])
    return columns


def cleanup(word):
    v = word["v"]
    return [[1, d, list(ss)] for _, d, ss in reversed(word["A"] + word["B"])
            if not v <= d < 2 * v]


def replace(base, gates):
    word = copy.deepcopy(base)
    word["B"][START:STOP] = copy.deepcopy(gates)
    word["C"] = cleanup(word)
    return word


def paths(word):
    result = [[f] for f in word["start"]]
    for phase in "DABC":
        for f, d, ss in word[phase]:
            for r in [d, *ss]:
                if result[r][-1] != f:
                    result[r].append(f)
    for r, f in enumerate(word["final"]):
        if result[r][-1] != f:
            result[r].append(f)
    return result


def splice_check(base, prior_gates, candidate_gates, candidate):
    need(len(prior_gates) == 21 and len(candidate_gates) == 20, "gate invoice")
    original = base["B"][START:STOP]
    need(column_map(original, 2) == column_map(candidate_gates, 2), "Boolean block map")
    need(column_map(original) == column_map(prior_gates), "predecessor integer map")
    delta = [[x - y for x, y in zip(a, b)] for a, b in
             zip(column_map(prior_gates), column_map(candidate_gates))]
    expected = [[2 * int(source == 33 and dst == 468) for dst in WIRES] for source in WIRES]
    need(delta == expected, "integer-map difference")
    need(candidate["C"] == cleanup(candidate), "literal cleanup")
    need(paths(candidate) == paths(base), "ordered frame paths")
    for key in base:
        if key not in ("B", "C"):
            need(candidate[key] == base[key], "unrelated word field: " + key)
    need(candidate["B"][:START] == base["B"][:START]
         and candidate["B"][START + 20:] == base["B"][STOP:], "unrelated B gates")
    return delta


def scalar_stream(word):
    n, v = 2 * word["v"] + word["R"], word["v"]
    out = []
    for phase in ("D", "A", "scatter", "B", "C"):
        if phase == "scatter":
            for j, center in enumerate(word["ret"]):
                out.append(("copy", n, center))
                out.extend(("add", v + i, n) for i, ss in enumerate(word["scatter"]) if j in ss)
                out.append(("erase", n, center))
        else:
            out.extend(("add", d, s) for _, d, ss in word[phase] for s in ss)
    return out


def scalar_audit(word):
    n, v = 2 * word["v"] + word["R"], word["v"]
    program = scalar_stream(word)
    peaks = []
    for reverse in (False, True):
        stream = [("erase" if op == "copy" else "copy" if op == "erase" else op, d, s)
                  for op, d, s in reversed(program)] if reverse else program
        values = [{i} for i in range(n)] + [set()]
        positive = [1] * n + [0]
        peak = 1
        for op, d, s in stream:
            if op == "add":
                values[d].symmetric_difference_update(values[s])
                positive[d] += positive[s]
            elif op == "copy":
                need(not values[d], "COPY temporary live")
                values[d] = set(values[s])
                positive[d] = positive[s]
            else:
                need(values[d] == values[s], "ERASE copy changed")
                values[d] = set()
                positive[d] = 0
            peak = max(peak, positive[d])
        expected = [{i, i - v} if v <= i < 2 * v else {i} for i in range(n)] + [set()]
        need(values == expected, "dirty endpoint")
        peaks.append(peak)
    f, b = peaks
    local, nine = 64 * f**3 * b**2, (1 << 18) * f**5 * b**4
    need(local < 1 << 104 and nine < 1 << 192, "precision ceilings")
    return {"additions": sum(op == "add" for op, _, _ in program), "columns": n,
            "forward_positive_bound": f, "reverse_positive_bound": b,
            "payload_upper": str(local), "payload_bits": local.bit_length(),
            "nine_stage_upper": str(nine), "nine_stage_bits": nine.bit_length()}


def prefix_binding(root):
    # Bind the inherited scalar envelope to its pinned source expression.
    source = next(path for path in SOURCE_PATHS if path.endswith("/global_k.py"))
    tree = ast.parse((root / source).read_text())
    expression = ast.dump(ast.parse("(1 << nb) * cf**(K+1) * cb**K", mode="eval").body)
    need(any(isinstance(node, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "prefix" for t in node.targets)
             and ast.dump(node.value) == expression for node in ast.walk(tree)), "prefix source expression")
    bridge = ast.dump(ast.parse("nb == 6*(K-1)", mode="eval").body)
    need(any(ast.dump(term) == bridge for node in ast.walk(tree) if isinstance(node, ast.Assert)
             for term in ast.walk(node.test)), "prefix bridge source")
    return {"source": source, "stages": 9, "K": 4, "bridges": 18,
            "envelope": "2^18 * F^5 * B^4", "charged_bits": 192}


def run(command, path):
    result = subprocess.run([str(x) for x in command], capture_output=True, text=True)
    path.write_text(result.stdout + result.stderr)
    need(result.returncode == 0, "command failed: " + str(path))
    return result.stdout


def exported_audit(records, word):
    n, v = 661, 111
    values = [1 << i for i in range(n)] + [0]
    profile = Counter()
    moved = [[f] for f in word["start"]]
    opened = None
    counts = Counter()
    literal = []
    for op, a, b, c, f, rank in records:
        need(type(op) is int and 0 <= op <= 3, "export opcode")
        counts[op] += 1
        if op == 0:
            need(0 <= a < n and 0 <= f <= 8, "MOVE range")
            if f:
                profile[f] += 1
            # exporter a,b,c encode register/from/to; f is rank difference
            need(moved[a][-1] == b, "MOVE origin")
            moved[a].append(c)
        elif op == 1:
            need(0 <= a < n and 0 <= b <= n and a != b and c == 1, "ADD operands")
            need(a != opened and (b < n or opened is not None), "COPY source/temporary use")
            values[a] ^= values[b]
            literal.append(("add", a, b))
        elif op == 2:
            need(opened is None and 0 <= a < n and b == n and rank == 7, "COPY lifecycle/rank")
            opened = a
            values[n] = values[a]
            profile[rank] += 1
            literal.append(("copy", n, a))
        else:
            need(opened == a and b == n and values[n] == values[a], "ERASE lifecycle")
            opened = None
            values[n] = 0
            literal.append(("erase", n, a))
    need(opened is None and counts[2] == counts[3] == 9, "COPY count/closure")
    need(literal == scalar_stream(word), "literal exported stream")
    need(values == [(1 << i) ^ ((1 << (i-v)) if v <= i < 2*v else 0)
                    for i in range(n)] + [0], "exported endpoint")
    need(moved == paths(word), "exported MOVE paths")
    return {"records": len(records), "moves": counts[0], "copies": counts[2],
            "erases": counts[3], "paid_profile": {str(k): v for k, v in sorted(profile.items())},
            "rank_mass": sum(k * v for k, v in profile.items())}


def negative_controls(base, prior, gates, candidate, records):
    rejected = []

    def reject(name, action, reason):
        try:
            action()
        except ValueError as exc:
            need(reason in str(exc), "wrong rejection for " + name + ": " + str(exc))
            rejected.append(name)
        else:
            raise ValueError("control accepted: " + name)

    target = column_map(base["B"][START:STOP], 2)
    for i in range(20):
        bad = gates[:i] + gates[i+1:]
        reject("omit_block_ADD_%02d" % i,
               lambda bad=bad: need(column_map(bad, 2) == target, "Boolean block map"), "Boolean block map")
    bad = copy.deepcopy(gates)
    bad[7], bad[8] = bad[8], bad[7]
    reject("restore_old_order_after_deletion",
           lambda: need(column_map(bad, 2) == target, "Boolean block map"), "Boolean block map")
    bad_word = copy.deepcopy(candidate)
    bad_word["C"] = base["C"]
    reject("stale_cleanup", lambda: splice_check(base, prior, gates, bad_word), "literal cleanup")
    bad_word2 = copy.deepcopy(candidate)
    bad_word2["B"][START][0] = 0
    reject("unpaid_frame_descent", lambda: splice_check(base, prior, gates, bad_word2), "ordered frame paths")
    bad_word3 = copy.deepcopy(candidate)
    helper_gate = next(i for i, (_, d, _) in enumerate(bad_word3["C"]) if d == 468)
    del bad_word3["C"][helper_gate]
    reject("missing_helper_restoration", lambda: scalar_audit(bad_word3), "dirty endpoint")
    bad_records = [r for r in records if r[0] != 3]
    reject("omitted_ERASE", lambda: exported_audit(bad_records, candidate), "COPY lifecycle")
    copy_at = next(i for i, r in enumerate(records) if r[0] == 2)
    center = records[copy_at][1]
    bad_records2 = records[:copy_at+1] + [(1, center, 661, 1, 0, 0)] + records[copy_at+1:]
    reject("mutate_copied_source", lambda: exported_audit(bad_records2, candidate), "COPY source")
    # An even number of ADDs is F2-invisible but must still be billed and priced.
    padded = copy.deepcopy(candidate)
    huge = [[509, 33, [38]], [509, 38, [33]]] * 180
    padded["B"][START:START] = huge + list(reversed(huge))
    padded["C"] = cleanup(padded)
    reject("F2_identity_precision_overflow", lambda: scalar_audit(padded), "precision ceilings")
    return rejected


def verify(root, output):
    pins(root)
    prefix = prefix_binding(root)
    base = load(root / WORD)
    prior_gates = load(root / PRIOR)["gates"]
    # The four-gate identity includes the commuting update of source 77.
    need(prior_gates[7:11] == [[509, 38, [33]], [509, 468, [33]],
                              [509, 77, [33]], [509, 468, [38]]], "predecessor window")
    derived = prior_gates[:7] + [prior_gates[10], prior_gates[7], prior_gates[9]] + prior_gates[11:]
    recipe = load(HERE / "CANDIDATE.json")
    need(recipe == {"format": "r439-b509-boolean/1", "base_commit": BASE,
                    "assignment_seed": 5, "slice": [START, STOP], "frame": FRAME,
                    "registers": WIRES, "gates": derived}, "candidate recipe")
    candidate = replace(base, recipe["gates"])
    prior_word = replace(base, prior_gates)
    delta = splice_check(base, prior_gates, derived, candidate)
    need(load(HERE / "candidate.json.gz") == candidate, "candidate decoded word")
    # Full Boolean truth tables with arbitrary helper 468, no clean input.
    old_ops, new_ops = operations(base["B"][START:STOP]), operations(derived)
    for assignment in range(1 << len(WIRES)):
        results = []
        for ops in (old_ops, new_ops):
            state = {w: (assignment >> i) & 1 for i, w in enumerate(WIRES)}
            for d, s in ops:
                state[d] ^= state[s]
            results.append(state)
        need(results[0] == results[1], "Boolean truth table")
    # Complete four-variable identity (a,b,h,c), including dirty h.
    for bits in range(16):
        a, b, h, c = [(bits >> i) & 1 for i in range(4)]
        old = [a, b ^ a, h ^ a ^ (b ^ a), c ^ a]
        new = [a, b ^ a, h ^ b, c ^ a]
        need(old == new, "four-wire identity")
    output.mkdir(parents=True, exist_ok=False)
    reports, record_sets = {}, {}
    for name, word in (("baseline", base), ("prior973", prior_word), ("candidate", candidate)):
        path = output / (name + ".json.gz")
        path.write_bytes(gzip.compress(canonical(word), mtime=0))
        report = scalar_audit(word)
        interface_path = output / (name + "-interface.json")
        run([sys.executable, "-I", "-B", root / CHECKER, path, "--json", interface_path],
            output / (name + "-interface.log"))
        interface = load(interface_path)
        need(all(interface["hypotheses"].values()) and all(interface["conclusion"].values()), "H1-H5 interface")
        need(interface["columns"] == 661 and interface["copy_ranks"] == [7] * 9,
             "interface columns/copies")
        record_dir = output / (name + "-records")
        run([sys.executable, "-I", "-B", root / EXPORTER, path, record_dir], output / (name + "-export.log"))
        raw = (record_dir / "249-records.bin").read_bytes()
        need(len(raw) % 24 == 0, "record alignment")
        records = list(struct.iter_unpack("<6i", raw))
        report.update(exported_audit(records, word))
        report.update({"hypotheses": interface["hypotheses"], "conclusions": interface["conclusion"],
                       "canonical_word_sha256": hashlib.sha256(canonical(word)).hexdigest()})
        reports[name], record_sets[name] = report, records
    for name in ("prior973", "candidate"):
        for key in ("moves", "copies", "erases", "paid_profile", "rank_mass", "columns"):
            need(reports[name][key] == reports["baseline"][key], "changed paid field: " + key)
        # Order within a frame may move identical charged events past ADDs.
        need(Counter(r for r in record_sets[name] if r[0] != 1) ==
             Counter(r for r in record_sets["baseline"] if r[0] != 1), "non-ADD invoice")
    need([reports[n]["additions"] for n in reports] == [24305, 24285, 24283], "complete ADD invoice")
    need(reports["candidate"]["rank_mass"] == 5129, "paid rank mass")
    controls = negative_controls(base, prior_gates, derived, candidate, record_sets["candidate"])
    result = {"status": "PASS_R439_B509_BOOLEAN", "base_commit": BASE,
              "block_additions": {"selected": 31, "prior973": 21, "candidate": 20},
              "integer_difference_columns": delta, "boolean_inputs": 2048,
              "four_wire_identity_inputs": 16, "frame_paths_checked": 661,
              "words": reports, "prefix_binding": prefix,
              "controls_rejected": controls, "new_kappa_claimed": False}
    write(output / "RESULT.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--source-root", type=Path, default=ROOT)
    parser.add_argument("--write-expected", action="store_true")
    args = parser.parse_args()
    if args.output:
        need(not args.output.exists(), "output already exists")
    with tempfile.TemporaryDirectory(prefix="r439-b509-") as temp:
        result = verify(args.source_root.resolve(), args.output or Path(temp) / "run")
    if args.write_expected:
        write(HERE / "EXPECTED.json", result)
    else:
        need(result == load(HERE / "EXPECTED.json"), "receipt mismatch")
    print("PASS_R439_B509_BOOLEAN gates=31/21->20 ADDs=24305/24285->24283 "
          "columns=661 truth_table=2048 H1-H5 controls=%d no_new_kappa" % len(result["controls_rejected"]))


if __name__ == "__main__":
    main()
