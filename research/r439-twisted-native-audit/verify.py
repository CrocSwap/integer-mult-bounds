#!/usr/bin/env python3
"""Fresh native replay of PR1868 using unchanged inherited C++ checkers.

Hanson Sun, substantial OpenAI Codex assistance. Apache-2.0.
Native command conventions follow Gareth Davidson's PR1122/1188 harness.
Candidate reconstruction, Python record/boundary checks and controls are new.
"""
import argparse
import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HUB = ROOT / "research/e8-bit-carrier-skeleton"
PARENTS = {"pr1062": "research/r439-bsection-stars-seed01/candidate.json.gz",
           "pr1188": "research/r439-gl5-shortest/candidate.json.gz"}
# centre, leaf, absorbing A index, frame, replacement source
EDITS = ((506, 374, 288, 71, 69), (507, 355, 290, 74, 72), (514, 367, 304, 65, 360))
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def equal(actual, expected, message):
    need(canonical(actual) == canonical(expected), message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pairs(items):
    out = {}
    for key, value in items:
        need(key not in out, "duplicate JSON key: " + key)
        out[key] = value
    return out


def invalid(value):
    raise ValueError("nonfinite JSON: " + value)


def load(path):
    path = Path(path)
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def check_blob(data, row):
    need(sha(data) == row["sha256"], "source SHA256: " + row["path"])
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    need(blob == row["git_blob"], "source Git blob: " + row["path"])


def sources():
    manifest = load(HERE / "SOURCES.json")
    checked = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
        else:
            data = subprocess.check_output(["git", "show", manifest["base_commit"] + ":" + row["path"]], cwd=ROOT)
        check_blob(data, row)
        checked[row["path"]] = row["sha256"]
    predecessor = load(HERE / "PREDECESSOR.json")
    need(predecessor["head"] == "6b222d01fee072bcd3a680e6a96ae7d22e13bcac", "unexpected predecessor")
    for row in predecessor["files"]:
        check_blob((HERE / row["path"]).read_bytes(), row)
        checked[row["path"]] = row["sha256"]
    return checked


def prefix_formula():
    path = ROOT / ("research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/"
                   "vendor/e8-r715-eleven-stage-whole/code/global_k.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    matches = [node.value for node in ast.walk(tree) if isinstance(node, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "prefix" for t in node.targets)]
    expected = ast.parse("(1 << nb) * cf ** (K + 1) * cb ** K", mode="eval").body
    need(len(matches) == 1 and ast.dump(matches[0]) == ast.dump(expected), "inherited prefix formula")
    # In the retained nine-stage schedule K=4 and six bridges per extra pair.
    return {"K": 4, "bridge_exponent": 6 * (4 - 1), "local_bits_cap": 104, "nine_bits_cap": 192}


def rebuild(parent):
    out, drop = deepcopy(parent), []
    for centre, leaf, index, frame, replacement in EDITS:
        matches = [i for i, gate in enumerate(parent["D"]) if gate == [0, centre, [leaf]]]
        need(len(matches) == 2, "preparation/restoration pair")
        drop.append(matches[-1])
        equal(parent["A"][index], [frame, centre, [leaf]], "absorbing A gate")
        out["A"][index] = [frame, centre, [replacement]]
    out["D"] = [gate for i, gate in enumerate(parent["D"]) if i not in drop]
    return out


def rank(rows):
    basis = {}
    for original in rows:
        row = list(map(Fraction, original))
        for pivot, vector in sorted(basis.items()):
            scale = row[pivot]
            row = [a - scale * b for a, b in zip(row, vector)]
        if any(row):
            pivot = next(i for i, value in enumerate(row) if value)
            scale = row[pivot]
            basis[pivot] = [x / scale for x in row]
    return len(basis)


def records_from_word(word):
    """Separately derive the exact event bytes, including frame ranks and copies."""
    n = 2 * word["v"] + word["R"]
    dimensions = [rank([word["lines"][i] for i in frame]) for frame in word["frames"]]
    need(dimensions.count(0) == 1, "unique zero frame")
    zero, frames, records = dimensions.index(0), list(word["start"]), []

    def phase(gates, tag):
        for frame, dest, operands in gates:
            for role in [dest, *operands]:
                if frames[role] != frame:
                    old = frames[role]
                    records.append((0, role, old, frame, dimensions[frame] - dimensions[old], 0))
                    frames[role] = frame
            records.extend((1, dest, source, 1, frame, tag) for source in operands)

    phase(word["D"], 1)
    phase(word["A"], 2)
    for slot, centre in enumerate(word["ret"]):
        frame = frames[centre]
        records.append((2, centre, n, frame, zero, dimensions[frame]))
        for target, slots in enumerate(word["scatter"]):
            if slot in slots:
                records.append((1, word["v"] + target, n, 1, zero, 3))
        records.append((3, centre, n, frame, zero, 0))
    phase(word["B"], 4)
    phase(word["C"], 5)
    for role, frame in enumerate(word["final"]):
        old = frames[role]
        if old != frame:
            records.append((0, role, old, frame, dimensions[frame] - dimensions[old], 0))
    return records


def binary_records(records):
    return b"".join(struct.pack("<6i", *event) for event in records)


def local_check(records, reverse=False, clean_helpers=False):
    state = [1 << i if not clean_helpers or i < 222 else 0 for i in range(661)] + [0]
    expected, opened = state[:], None
    for i in range(111):
        expected[111 + i] ^= expected[i]
    for op, a, b, c, frame, extra in (reversed(records) if reverse else records):
        if reverse and op in (2, 3):
            op = 5 - op
        if op == 1:
            need(a != b and a != 661 and (b != 661 or opened is not None), "illegal scalar ADD")
            if c % 2:
                state[a] ^= state[b]
        elif op == 2:
            need(opened is None and b == 661, "copy shape")
            opened, state[661] = a, state[a]
        elif op == 3:
            need(opened == a and b == 661 and state[661] == state[a], "copy source/closure")
            state[661], opened = 0, None
        else:
            need(op == 0, "unknown opcode")
    need(opened is None, "unclosed copy")
    return {"columns": 661, "bad_registers": [i for i in range(662) if state[i] != expected[i]],
            "endpoint_sha256": sha(canonical([str(x) for x in state]))}


def price(records):
    peaks = []
    for reverse in (False, True):
        bounds, peak, opened = [1] * 661 + [0], 1, None
        for op, a, b, c, frame, extra in (reversed(records) if reverse else records):
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                bounds[a] += abs(c) * bounds[b]
                peak = max(peak, bounds[a])
            elif op == 2:
                need(opened is None and b == 661, "bound copy shape")
                opened, bounds[b] = a, bounds[a]
            elif op == 3:
                need(opened == a and b == 661, "bound copy closure")
                bounds[b], opened = 0, None
        need(opened is None, "bound final copy")
        peaks.append(peak)
    forward, backward = peaks
    local, nine = 64 * forward**3 * backward**2, 2**18 * forward**5 * backward**4
    need(local < 2**104 and nine < 2**192, "strict precision guard")
    hist = Counter()
    for op, a, b, c, frame, extra in records:
        if op == 0 and frame:
            hist[frame] += 1
        elif op == 2:
            hist[extra] += 1
    need(dict(hist) == PROFILE, "paid profile")
    counts = Counter(r[0] for r in records)
    need(counts[2] == counts[3] == 9, "copy count")
    return {"ADDs": counts[1], "MOVEs": counts[0], "COPYs": counts[2], "ERASEs": counts[3],
            "F": forward, "B": backward, "local_upper": str(local), "nine_upper": str(nine),
            "local_bits": local.bit_length(), "nine_bits": nine.bit_length(),
            "paid_histogram": sorted(map(list, hist.items())), "rank_mass": sum(r * c for r, c in hist.items())}


def check_columns(receipt, k, prices):
    stages = 2 * k + 1
    status = ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL" if k == 2
              else "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL")
    need(receipt["status"] == status, "native status")
    need(receipt["formal_columns_checked"] == receipt["global_live_registers"] == 222 * k + 439,
         "native column coverage")
    need(receipt["local_registers"] == 661 and receipt["independent_dirty_registers"] == 439, "native dirty domain")
    need(receipt["local_scalar_additions"] == prices["ADDs"], "native local ADDs")
    key = "five_stage_additions" if k == 2 else "stage_additions"
    need(receipt[key] == stages * prices["ADDs"], "native complete ADD bill")
    need(receipt["fresh_center_copies"] == 9 * stages and receipt["reverse_fresh_center_copies"] == 9 * k,
         "native fresh copies")
    need(receipt["bridge_additions"] == 666 * (k - 1), "native bridge bill")
    equal(receipt["local_raw_H"], prices["paid_histogram"], "native rank profile")
    equal(receipt["stages"], [{"stage": i, "signed_inverse": bool(i % 2), "fresh_copies": 9,
                               "scalar_additions": prices["ADDs"]} for i in range(stages)], "native stage coverage")
    equal([int(x["cancellation_free_signed_row_l1_upper"]) for x in receipt["signed_lift_prefix"]],
          [prices["F"], prices["B"]], "native signed lift")
    equal([x["reverse"] for x in receipt["signed_lift_prefix"]], [False, True], "native orientations")
    need(receipt["payload_prefix_upper"] == prices["local_upper"] and
         receipt["payload_prefix_bits"] == prices["local_bits"], "native local precision")
    equal(receipt["negative_controls"], [{"omit_bridge": i, "rejected": True} for i in range(6 * (k - 1))],
          "native bridge controls")
    need(receipt["copied_center_original_source_immutable"] is True, "native copy immutability")


class Runner:
    def __init__(self, output):
        self.output, self.commands = output, []
        self.env = dict(os.environ)
        self.env.pop("PYTHONOPTIMIZE", None)

    def run(self, argv, log, failure=None, timeout=90):
        argv = list(map(str, argv))
        result = subprocess.run(argv, cwd=ROOT, env=self.env, capture_output=True, text=True, timeout=timeout)
        log.write_text(result.stdout + result.stderr, encoding="utf-8")
        self.commands.append({"argv": argv, "returncode": result.returncode,
                              "log": str(log.relative_to(self.output))})
        if failure is None:
            if result.returncode != 0:
                print((result.stdout + result.stderr)[-4000:], file=sys.stderr)
            need(result.returncode == 0, "command failed; inspect " + str(log))
        else:
            need(result.returncode != 0 and failure in result.stdout + result.stderr,
                 "control did not fail as expected: " + str(log))

    def export(self, word_path, directory):
        directory.mkdir()
        records, cin, cout = [directory / name for name in ("records", "cin", "cout")]
        python = [sys.executable, "-I", "-B"]
        self.run(python + [HUB / "code/bit/export_records.py", word_path, records], directory / "export.log")
        self.run(python + [HUB / "code/bit/regression/stage_cohort.py", records, records, cin, cout], directory / "stage.log")
        return records, cin, cout


def controls(parent, candidate, tag, output, runner, report):
    rejected = []
    mutated = deepcopy(candidate)
    mutated["A"] = deepcopy(parent["A"])
    events = records_from_word(mutated)
    dirty, clean = local_check(events), local_check(events, clean_helpers=True)
    need(len(dirty["bad_registers"]) == 102 and not clean["bad_registers"], "dirty-only omission control")
    folder = output / (tag + "-controls")
    folder.mkdir()
    raw_path = folder / "uncompensated.bin"
    raw_path.write_bytes(binary_records(events))
    for k in (2, 4, 5):
        runner.run([output / f"columns-{k}", raw_path, folder / f"uncompensated-{k}.json"],
                   folder / f"uncompensated-{k}.log", failure="local defining-decoder full formal column")
        rejected.append(f"uncompensated dirty helpers, {2*k+1} stages")
    for _, _, index, _, _ in EDITS:
        bad = deepcopy(candidate)
        bad["A"][index] = deepcopy(parent["A"][index])
        broken = records_from_word(bad)
        need(bool(local_check(broken)["bad_registers"]), "single absorption mutation survived")
        path = folder / f"missing-{index}.bin"
        path.write_bytes(binary_records(broken))
        runner.run([output / "columns-2", path, folder / f"missing-{index}.json"], folder / f"missing-{index}.log",
                   failure="local defining-decoder full formal column")
        rejected.append(f"missing compensation at A[{index}]")
    original = records_from_word(candidate)
    directory = output / (tag + "-absorbed")
    cin, cout = directory / "cin", directory / "cout"
    record_path = cout / "COHORT249-RECORDS.bin"
    original_bytes = record_path.read_bytes()
    try:
        bad = list(original)
        index = next(i for i, e in enumerate(bad) if e[0] == 1 and e[1] == 506 and e[5] == 2)
        item = list(bad[index]); item[4] = 0; bad[index] = tuple(item)
        need(not local_check(bad)["bad_registers"], "frame control must retain scalar endpoint")
        record_path.write_bytes(binary_records(bad))
        runner.run([output / "legality", cin, cout, folder / "wrong-frame.json"], folder / "wrong-frame.log",
                   failure="ADD not in common frame")
        rejected.append("scalar-valid wrong common frame")
        bad = list(original)
        index = next(i for i, e in enumerate(bad) if e[0] == 2)
        item = list(bad[index]); item[5] -= 1; bad[index] = tuple(item)
        record_path.write_bytes(binary_records(bad))
        runner.run([output / "legality", cin, cout, folder / "wrong-copy-rank.json"], folder / "wrong-copy-rank.log",
                   failure="COPY rank")
        rejected.append("undercharged COPY rank")
    finally:
        record_path.write_bytes(original_bytes)
    need(record_path.read_bytes() == original_bytes, "control restoration")
    receipt = deepcopy(report["words"][tag + "-absorbed"]["native"]["9"])
    receipt["formal_columns_checked"] -= 1
    try:
        check_columns(receipt, 4, report["words"][tag + "-absorbed"]["prices"])
    except ValueError as exc:
        need(str(exc) == "native column coverage", "wrong coverage rejection")
    else:
        raise ValueError("shortened native coverage accepted")
    rejected.append("passing receipt with shortened column coverage")
    return {"rejected": rejected, "uncompensated_dirty_bad_registers": dirty["bad_registers"],
            "uncompensated_clean_helpers_pass": not clean["bad_registers"]}


def run(output):
    checked, runner = sources(), Runner(output)
    formula = prefix_formula()
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    need(bool(compiler), "empty CXX")
    checker = HUB / "code/bit/checkers"
    flags = compiler + ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9",
                        "-I" + str(HUB / "portable-include"), "-I" + str(checker)]
    if os.environ.get("BOOST_INCLUDE"):
        flags.append("-I" + os.environ["BOOST_INCLUDE"])
    print("Compiling pinned native checkers", flush=True)
    runner.run(flags + ["-o", output / "legality", checker / "legality_h.cpp"], output / "compile-legality.log")
    for k in (2, 4, 5):
        runner.run(flags + ["-DVPORTS=111", "-DRHELP=439", "-DKPAIRS=" + str(k),
                            "-o", output / f"columns-{k}", checker / "columns_k.cpp"], output / f"compile-columns-{k}.log")
    report = {"format": "r439-twisted-native-audit/1", "sources": checked, "prefix_formula": formula,
              "words": {}, "controls": {}}
    for tag, parent_path in PARENTS.items():
        parent = load(ROOT / parent_path)
        path = HERE / "vendor/pr1868" / ("absorbed-" + tag + ".json.gz")
        candidate = load(path)
        equal(rebuild(parent), candidate, "independent candidate reconstruction")
        movements = []
        for label, word_path, word in (("parent", ROOT / parent_path, parent), ("absorbed", path, candidate)):
            name = tag + "-" + label
            print("Replaying", name, flush=True)
            directory = output / name
            record_dir, cin, cout = runner.export(word_path, directory)
            events = records_from_word(word)
            raw = binary_records(events)
            need(raw == (record_dir / "249-records.bin").read_bytes(), "export record mismatch")
            need(raw == (cout / "COHORT249-RECORDS.bin").read_bytes(), "staged record mismatch")
            prices = price(events)
            for reverse in (False, True):
                need(not local_check(events, reverse)["bad_registers"], "Python arbitrary-dirty boundary")
            move = {}
            for event in events:
                if event[0] == 0:
                    move.setdefault(event[1], []).append(event)
            movements.append({"per_register": move, "copy_erase": [r for r in events if r[0] in (2, 3)]})
            runner.run([output / "legality", cin, cout, cout / "legality.json"], directory / "legality.log")
            legal = load(cout / "legality.json")
            need(legal["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE", "native legality status")
            for field, expected in (("records", len(events)), ("common_frame_ADDs", prices["ADDs"]),
                                    ("nested_MOVEs", prices["MOVEs"]), ("copies", 9), ("erasures", 9),
                                    ("rank_mass", 5129), ("all_final_frames_pass", True),
                                    ("selected_pairs", 0), ("selected_helpers", 0),
                                    ("source_owner_intersections", 0), ("donor_intersections", 0),
                                    ("new_frame_ids_collision", False)):
                equal(legal[field], expected, "native legality field " + field)
            equal(legal["paid_histogram"], prices["paid_histogram"], "native legality profile")
            native = {}
            for k in (2, 4, 5):
                receipt_path = cout / f"columns-{k}.json"
                runner.run([output / f"columns-{k}", cout / "COHORT249-RECORDS.bin", receipt_path], directory / f"columns-{k}.log")
                receipt = load(receipt_path)
                check_columns(receipt, k, prices)
                # Retain every proof-relevant field; omit only path and elapsed time.
                native[str(2 * k + 1)] = {key: value for key, value in receipt.items()
                                        if key not in ("seconds", "local_scalar_stream")}
            report["words"][name] = {"decoded_sha256": sha(canonical(word)), "record_sha256": sha(raw),
                "prices": prices, "local_forward": local_check(events), "local_reverse": local_check(events, True),
                "legality": legal, "native": native}
        equal(movements[0], movements[1], "changed frame paths or copy windows")
        need(report["words"][tag + "-parent"]["prices"]["ADDs"] -
             report["words"][tag + "-absorbed"]["prices"]["ADDs"] == 3, "complete three-ADD saving")
        report["controls"][tag] = controls(parent, candidate, tag, output, runner, report)
    boost_probe = subprocess.run(compiler + ["-std=c++17", "-x", "c++", "-E", "-dM", "-"] +
                                 (["-I" + os.environ["BOOST_INCLUDE"]] if os.environ.get("BOOST_INCLUDE") else []),
                                 input="#include <boost/version.hpp>\n", capture_output=True, text=True,
                                 timeout=30, check=True)
    boost_version = next(line for line in boost_probe.stdout.splitlines() if line.startswith("#define BOOST_VERSION "))
    write(output / "ENVIRONMENT.json", {"python": sys.version, "platform": platform.platform(),
          "compiler": subprocess.check_output(compiler + ["--version"], text=True),
          "boost_version": boost_version, "boost_include": os.environ.get("BOOST_INCLUDE"),
          "commands": runner.commands})
    write(output / "RESULT.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new directory retaining raw logs, binaries and receipts")
    parser.add_argument("--write", action="store_true", help="regenerate the deterministic result explicitly")
    args = parser.parse_args()
    if args.output:
        output = args.output.resolve()
        output.mkdir(parents=True, exist_ok=False)
        result = run(output)
    else:
        with tempfile.TemporaryDirectory(prefix="twisted-native-") as tmp:
            result = run(Path(tmp))
    if args.write:
        write(HERE / "RESULT.json", result)
    else:
        equal(result, load(HERE / "RESULT.json"), "committed result differs from fresh replay")
    print("PASS_R439_TWISTED_NATIVE_AUDIT words=4 absorbed=2 stages=5/9/11 "
          "columns=883/1327/1549 bridge_controls=192 added_controls=18 no_new_kappa")


if __name__ == "__main__":
    main()
