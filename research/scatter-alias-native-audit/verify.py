#!/usr/bin/env python3
"""PR3128 alias boundary audit, including optional actual native replay.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Apache-2.0. Predecessor programs execute as authenticated audit subjects.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECK = "research/e8-bit-p111-tuned/code/xcheck_p.py"
BIT = "research/e8-bit-carrier-skeleton/code/bit/"
EXPORT = BIT + "export_records.py"
STAGE = BIT + "regression/stage_cohort.py"
CHECKERS = BIT + "checkers/"
PORTABLE = "research/e8-bit-carrier-skeleton/portable-include/"
STANDIN = "research/bit589-checked-cpp-int-seed92/include/"
BOUNDARY = "research/simple-scatter-boundary/boundary.py"
PREVIOUS = "research/retained-alias-parity-audit/EXPECTED.json"
SELECTED = "research/community-frontier1094-audit/SELECTED-SOURCE.json"
ARTIFACTS = ("249-records.bin", "249-states.json", "frames.json")
RECORD = struct.Struct("<6i")
LEGAL_PASS = "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE"
COLUMN_PASS = "PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL"
ENDPOINT_FAILURE = "local defining-decoder full formal column"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def sources(root=ROOT):
    pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    data = {}
    for row in pins["files"]:
        if row["usage"] == "input":
            body = (root / row["path"]).read_bytes()
            need(digest(body) == row["sha256"], "source pin mismatch: " + row["path"])
            data[row["path"]] = body
    selected = json.loads(data[SELECTED])["files"]
    for path in (WORD, CHECK, EXPORT):
        need(digest(data[path]) == selected[path], "selected source binding: " + path)
    return data


def command(args, timeout=60):
    return subprocess.run([str(x) for x in args], capture_output=True,
                          text=True, check=False, timeout=timeout)


def python(script, *args):
    # No audit-subject repository imports; scripts run on private snapshots.
    return command([sys.executable, "-I", "-B", script, *args])


def snapshot(data, directory):
    for name, body in data.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)


def fixtures(word):
    need((word["v"], word["R"], len(word["ret"])) == (111, 439, 9), "fixed header")
    need(word["ret"][8] == 480 and word["scatter"][64] == [2, 4, 6], "PR3128 site")
    out = {"baseline": copy.deepcopy(word)}
    for name, tail, helper in (
        ("balanced_alias", [8, 8, 9, 9], 480),
        ("unpaired_even", [8, 8], 480),
        ("distinct_helpers", [8, 8, 9, 9], 479),
        ("unused_alias", [], 480),
    ):
        mutant = copy.deepcopy(word)
        mutant["ret"].append(helper)
        mutant["scatter"][64].extend(tail)
        out[name] = mutant
    return out


def read_records(raw):
    need(len(raw) % RECORD.size == 0, "record alignment")
    need(0 < len(raw) // RECORD.size < 30000, "bounded record count")
    return list(RECORD.iter_unpack(raw))


def scalar_and_invoice(records, n=661, v=111):
    """Independent scalar projection and literal paid-event recount.

    MOVE geometry is left to the actual native program. Each integer bit is
    one arbitrary dirty-input basis column. COPY/ERASE source binding is checked.
    """
    values = [1 << r for r in range(n)] + [0]
    opened = None
    counts, ranks = Counter(), Counter()
    scatter_adds = 0
    for op, a, b, c, f, z in records:
        need(op in range(4) and 0 <= a <= n, "opcode or destination")
        counts[op] += 1
        if op == 0:
            need(a != n or opened is not None, "MOVE inactive temporary")
            need(f >= 0, "negative MOVE charge")
            if f:
                ranks[f] += 1
        elif op == 1:
            need(0 <= b <= n and a != b, "ADD source")
            need(a != n and (b != n or opened is not None), "ADD temporary lifecycle")
            need(a != opened, "copied source mutated")
            if c % 2:
                values[a] ^= values[b]
            scatter_adds += (z == 3)
        elif op == 2:
            need(opened is None and a < n and b == n, "COPY lifecycle")
            need(z >= 0, "COPY charge")
            opened = a
            values[n] = values[a]
            ranks[z] += 1
        else:
            need(opened is not None and a == opened and b == n, "ERASE source binding")
            values[n] = 0
            opened = None
    need(opened is None and values[n] == 0, "temporary not closed")
    differences = []
    for r in range(n):
        expected = (1 << r) ^ ((1 << (r - v)) if v <= r < 2 * v else 0)
        delta = values[r] ^ expected
        if delta:
            differences.append({"output": r, "input_columns": [
                i for i in range(n) if delta >> i & 1]})
    return differences, {
        "records": len(records), "moves": counts[0], "adds": counts[1],
        "copies": counts[2], "erasures": counts[3], "scatter_adds": scatter_adds,
        "rank_mass": sum(k * count for k, count in ranks.items()),
        "paid_histogram": [[k, ranks[k]] for k in sorted(ranks)],
        "copy_rank_sum": sum(row[5] for row in records if row[0] == 2),
    }


def prefix_invoice(records, n=661):
    """Unbounded integer recurrence cross-checking the native checked128 bill."""
    events = [(op, a, b, c) for op, a, b, c, _, _ in records if op != 0]
    maxima = []
    for reverse in (False, True):
        norms = [1] * (n + 1)
        peak = 1
        for op, a, b, coefficient in (reversed(events) if reverse else events):
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                norms[a] += abs(coefficient) * norms[b]
                peak = max(peak, norms[a])
            elif op == 2:
                norms[n] = norms[a]
            else:
                norms[n] = 0
        need(norms[n] == 0, "prefix temporary closure")
        maxima.append(peak)
    forward, backward = maxima
    payload = 64 * forward ** 3 * backward ** 2
    return {"forward": str(forward), "reverse": str(backward),
            "payload": str(payload), "bits": payload.bit_length(),
            "below_2_104": payload < 2 ** 104}


def guard(snapshot_root, wordpath, directory, accepted, artifacts):
    checked = python(snapshot_root / BOUNDARY, "check", wordpath)
    need(checked.returncode == (0 if accepted else 2), "actual guard check outcome")
    if not accepted:
        need("duplicate index 8" in checked.stderr, "guard check rejection site")
    output = directory / "guard-export"
    result = python(snapshot_root / BOUNDARY, "export", wordpath, output)
    need(result.returncode == (0 if accepted else 2), "actual guard export outcome")
    if accepted:
        need(all((output / k).read_bytes() == artifacts[k] for k in ARTIFACTS),
             "guard changes valid export")
    else:
        need(not output.exists() and "duplicate index 8" in result.stderr,
             "guard must reject before output")
        output.mkdir()
        for name in ARTIFACTS:
            (output / name).write_bytes(b"preexisting output\n")
        result = python(snapshot_root / BOUNDARY, "export", wordpath, output)
        need(result.returncode == 2, "existing-output duplicate rejected")
        need(all((output / k).read_bytes() == b"preexisting output\n" for k in ARTIFACTS),
             "guard clobbered output")
    return {"accepted": accepted, "valid_bytes_preserved": True if accepted else None,
            "rejected_before_creation": None if accepted else True,
            "existing_outputs_preserved": None if accepted else True}


def run_fixture(name, word, snapshot_root, directory, predecessor):
    directory.mkdir()
    wordpath = directory / "word.json.gz"
    wordpath.write_bytes(gzip.compress(canonical(word).encode(), mtime=0))
    receipt = directory / "symbolic.json"
    checked = python(snapshot_root / CHECK, wordpath, "--json", receipt)
    need(checked.returncode == 0 and receipt.exists(),
         "full symbolic check: " + checked.stdout + checked.stderr)
    symbolic = json.loads(receipt.read_bytes())
    need(symbolic["status"] == "PASS_EXACT_REPLAY_AND_INTERLEAVED_INTERFACE", "symbolic status")
    need(symbolic["columns"] == 661 and all(symbolic["hypotheses"].values())
         and all(symbolic["conclusion"].values()), "full interface")
    output = directory / "records"
    exported = python(snapshot_root / EXPORT, wordpath, output)
    need(exported.returncode == 0, "actual exporter: " + exported.stderr)
    artifacts = {k: (output / k).read_bytes() for k in ARTIFACTS}
    raw = artifacts["249-records.bin"]
    records = read_records(raw)
    differences, invoice = scalar_and_invoice(records)
    if name in predecessor["fixtures"]:
        prior = predecessor["fixtures"][name]
        need(digest(raw) == prior["records_sha256"], "exact PR3128 record fixture identity")
        need(differences == prior["differences"], "independent full-column comparison to PR3128")
        need(invoice["copy_rank_sum"] == prior["copy_rank_sum"], "COPY rank cross-check")
    return {
        "artifacts_sha256": {k: digest(body) for k, body in artifacts.items()},
        "symbolic": symbolic, "scalar_differences": differences, "invoice": invoice,
        "prefix": prefix_invoice(records),
        "guard": guard(snapshot_root, wordpath, directory,
                       name in ("baseline", "unused_alias"), artifacts),
    }, records


def primary(data, directory):
    snapshot_root = directory / "sources"
    snapshot(data, snapshot_root)
    predecessor = json.loads(data[PREVIOUS])
    results, streams = {}, {}
    for name, word in fixtures(json.loads(gzip.decompress(data[WORD]))).items():
        results[name], streams[name] = run_fixture(
            name, word, snapshot_root, directory / name, predecessor)
    base, alias = results["baseline"], results["balanced_alias"]
    need(not base["scalar_differences"] and not alias["scalar_differences"], "positive endpoints")
    for name in ("unpaired_even", "distinct_helpers"):
        delta = results[name]["scalar_differences"]
        need(len(delta) == 1 and delta[0]["output"] == 175
             and 480 in delta[0]["input_columns"], "dirty-column control")
    need(base["artifacts_sha256"]["frames.json"] == alias["artifacts_sha256"]["frames.json"],
         "unchanged frame dictionary")
    delta = {k: alias["invoice"][k] - base["invoice"][k] for k in (
        "records", "moves", "adds", "copies", "erasures",
        "scatter_adds", "rank_mass", "copy_rank_sum")}
    need(delta == {"records": 4, "moves": 0, "adds": 2, "copies": 1, "erasures": 1,
                   "scatter_adds": 2, "rank_mass": 7, "copy_rank_sum": 7},
         "complete literal alias delta")
    unused = results["unused_alias"]
    need(not unused["scalar_differences"], "unused alias endpoint")
    unused_delta = {k: unused["invoice"][k] - base["invoice"][k] for k in delta}
    need(unused_delta == {"records": 2, "moves": 0, "adds": 0, "copies": 1,
                          "erasures": 1, "scatter_adds": 0, "rank_mass": 7,
                          "copy_rank_sum": 7}, "unused alias count-only control")
    return {"status": "PASS_SCATTER_ALIAS_BOUNDARY_AUDIT", "fixtures": results,
            "balanced_minus_selected": delta, "unused_minus_selected": unused_delta,
            "columns": 661,
            "no_new_kappa": True}, streams, snapshot_root


def compile_native(snapshot_root, directory, copies):
    flags = [os.environ.get("CXX", "c++"), "-O2", "-std=c++17", "-DHDIM=8",
             "-DVPORTS=111", "-DRHELP=439", f"-DNCOPY={copies}"]
    flags += ["-I" + str(snapshot_root / p) for p in (PORTABLE, CHECKERS, STANDIN)]
    out = {}
    for name in ("legality_h", "columns_h"):
        target = directory / (name + str(copies))
        result = command(flags + ["-o", target, snapshot_root / CHECKERS / (name + ".cpp")],
                         timeout=120)
        need(result.returncode == 0 and target.exists(), "native compile: " + result.stderr)
        out[name] = target
    return out


def native_check(binary, args, receipt, rejection=None):
    result = command([binary, *args, receipt])
    if rejection:
        need(result.returncode != 0 and not receipt.exists(),
             "native must reject without success receipt")
        need(rejection in result.stderr, "native rejection site: " + result.stderr)
        return {"accepted": False, "reason": rejection}
    need(result.returncode == 0 and receipt.exists(), "native failure: " + result.stderr)
    value = json.loads(receipt.read_bytes())
    need(value.get("status") in (LEGAL_PASS, COLUMN_PASS), "native success status")
    if "seconds" in value:
        seconds = value.pop("seconds")
        need(type(seconds) in (int, float) and math.isfinite(seconds) and seconds >= 0,
             "native elapsed time")
        need(value["local_scalar_stream"] == str(args[0]), "native stream receipt binding")
        value["local_scalar_stream"] = "COHORT249-RECORDS.bin"
        lines = result.stderr.splitlines()
        need(len(lines) == 5, "five native stages")
        for i, line in enumerate(lines):
            prefix = f"stage {i} PASS elapsed "
            need(line.startswith(prefix) and line.endswith("s"), "native stage progress")
            elapsed = float(line[len(prefix):-1])
            need(math.isfinite(elapsed) and elapsed >= 0, "stage elapsed time")
    return {"accepted": True, "receipt": value}


def stage(snapshot_root, directory):
    source = directory / "records"
    cin, cout = directory / "cin", directory / "cout"
    result = python(snapshot_root / STAGE, source, source, cin, cout)
    need(result.returncode == 0, "native staging: " + result.stderr)
    need((cout / "COHORT249-RECORDS.bin").read_bytes() ==
         (source / "249-records.bin").read_bytes(), "staging changed stream")
    return cin, cout


def reconcile_native(result, local, copies):
    legal, invoice = result["legality"]["receipt"], local["invoice"]
    need(legal["status"] == LEGAL_PASS, "legality receipt status")
    for native, own in (("records", "records"), ("nested_MOVEs", "moves"),
                        ("common_frame_ADDs", "adds"), ("copies", "copies"),
                        ("erasures", "erasures"), ("rank_mass", "rank_mass"),
                        ("paid_histogram", "paid_histogram")):
        need(legal[native] == invoice[own], "native invoice mismatch: " + native)
    if not result["columns"]["accepted"]:
        return
    columns = result["columns"]["receipt"]
    need(columns["status"] == COLUMN_PASS and columns["formal_columns_checked"] == 883,
         "native columns")
    need(columns["local_raw_H"] == invoice["paid_histogram"], "column paid histogram")
    need(columns["local_scalar_additions"] == invoice["adds"]
         and columns["five_stage_additions"] == 5 * invoice["adds"], "five-stage ADD bill")
    need(columns["fresh_center_copies"] == 5 * copies
         and columns["reverse_fresh_center_copies"] == 2 * copies, "five-stage COPY bill")
    prefix = local["prefix"]
    need([x["cancellation_free_signed_row_l1_upper"] for x in columns["signed_lift_prefix"]]
         == [prefix["forward"], prefix["reverse"]], "native prefix recurrence")
    need(columns["payload_prefix_upper"] == prefix["payload"]
         and columns["payload_prefix_bits"] == prefix["bits"], "native payload invoice")


def native_controls(binaries, records, directory):
    fixture_dir = directory / "balanced_alias"
    cin, cout = fixture_dir / "cin", fixture_dir / "cout"
    stream = cout / "COHORT249-RECORDS.bin"
    copy_index = max(i for i, row in enumerate(records) if row[0] == 2)
    erase_index = next(i for i in range(copy_index + 1, len(records)) if records[i][0] == 3)
    add_index = next(i for i in range(copy_index + 1, erase_index) if records[i][0] == 1)
    result = {}
    for kind in ("underprice_copy_rank", "wrong_erase_source", "omit_alias_add"):
        mutated = [list(r) for r in records]
        if kind == "underprice_copy_rank":
            mutated[copy_index][5] -= 1
            legal_failure, column_failure = "COPY rank", None
        elif kind == "wrong_erase_source":
            mutated[erase_index][1] = 479
            legal_failure, column_failure = "invalid ERASE lifecycle", "discard original-source binding"
        else:
            del mutated[add_index]
            legal_failure, column_failure = None, ENDPOINT_FAILURE
        stream.write_bytes(b"".join(RECORD.pack(*row) for row in mutated))
        result[kind] = {
            "legality": native_check(binaries["legality_h"], [cin, cout],
                                    fixture_dir / (kind + "-legal.json"), legal_failure),
            "columns": native_check(binaries["columns_h"], [stream],
                                   fixture_dir / (kind + "-columns.json"), column_failure),
        }
    stream.write_bytes(b"".join(RECORD.pack(*row) for row in records))
    return result


def native_audit(primary_result, streams, snapshot_root, directory):
    # The legacy legality checker aborts on failure; prevent core-file writes.
    if os.name == "posix":
        import resource
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    binaries = {count: compile_native(snapshot_root, directory, count) for count in (9, 10)}
    results = {}
    for name, local in primary_result["fixtures"].items():
        fixture_dir = directory / name
        cin, cout = stage(snapshot_root, fixture_dir)
        stream = cout / "COHORT249-RECORDS.bin"
        results[name] = {}
        for count in (9, 10):
            right_count = count == local["invoice"]["copies"]
            legal_failure = None if right_count else "unclosed COPY"
            column_failure = ("center boundaries" if not right_count else
                              (ENDPOINT_FAILURE if local["scalar_differences"] else None))
            result = {
                "legality": native_check(binaries[count]["legality_h"], [cin, cout],
                                        fixture_dir / f"legality{count}.json", legal_failure),
                "columns": native_check(binaries[count]["columns_h"], [stream],
                                       fixture_dir / f"columns{count}.json", column_failure),
            }
            if right_count:
                reconcile_native(result, local, count)
            results[name][str(count)] = result
    previous = json.loads((snapshot_root / "research/scatter-export-parity-audit/NATIVE.json").read_bytes())
    for kind in ("legality", "columns"):
        need(results["baseline"]["9"][kind]["receipt"] == previous["fixtures"]["baseline"][kind],
             "unchanged PR2977 native baseline receipt")
    return {"status": "PASS_SCATTER_ALIAS_NATIVE_AUDIT",
            "backend": "checked_cpp_int_128_standin", "fixtures": results,
            "controls": native_controls(binaries[10], streams["balanced_alias"], directory),
            "columns": 883, "no_new_kappa": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", action="store_true",
                        help="compile both actual checker contracts with C++17")
    parser.add_argument("--emit", action="store_true",
                        help="print reconstructed deterministic receipt")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="scatter-alias-") as temporary:
        directory = Path(temporary)
        result, streams, snapshot_root = primary(sources(), directory)
        if args.native:
            result["native"] = native_audit(result, streams, snapshot_root, directory)
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        receipt = PACKAGE / ("NATIVE.json" if args.native else "RESULT.json")
        need(canonical(result) == canonical(json.loads(receipt.read_bytes())),
             "deterministic typed receipt mismatch")
        if args.native:
            print("PASS_SCATTER_ALIAS_NATIVE_AUDIT fixtures=5 contracts=2 native_columns=883 controls=3 no_new_kappa")
        else:
            print("PASS_SCATTER_ALIAS_BOUNDARY_AUDIT fixtures=5 columns=661 guard_rejects=3 no_new_kappa")


if __name__ == "__main__":
    main()
