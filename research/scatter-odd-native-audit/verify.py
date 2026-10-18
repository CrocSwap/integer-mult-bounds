#!/usr/bin/env python3
"""Four source-bound scatter fixtures; optional actual native replay.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
Original scripts/checkers are audit subjects. No predecessor audit is imported.
"""

import argparse
import copy
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BIT = "research/e8-bit-carrier-skeleton/code/bit/"
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = BIT + "export_records.py"
BOUNDARY = "research/simple-scatter-boundary/boundary.py"
SELECTED = "research/community-frontier1094-audit/SELECTED-SOURCE.json"
STANDIN = "research/bit589-checked-cpp-int-seed92/include"
PORTABLE = "research/e8-bit-carrier-skeleton/portable-include"
ARTIFACTS = ("249-records.bin", "249-states.json", "frames.json")
FIXTURES = {
    "baseline": [],
    "even_absent": [0, 0],
    "odd_present": [4, 4],
    "odd_absent": [0, 0, 0],
}
LEGALITY_PASS = "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE"
COLUMNS_PASS = "PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL"
COLUMN_REJECTION = "local defining-decoder full formal column"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"


def digest(body):
    return hashlib.sha256(body).hexdigest()


def sources(root=ROOT):
    pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    data = {}
    for pin in pins["files"]:
        if pin["usage"] != "input":
            continue
        name = pin["path"]
        require(not Path(name).is_absolute() and ".." not in Path(name).parts,
                "contained source path")
        body = (root / name).read_bytes()
        require(len(body) < 5 * 1024 * 1024, "bounded source file")
        require(digest(body) == pin["sha256"], "source pin mismatch: " + name)
        require(name not in data, "duplicate source pin")
        data[name] = body
    selected = json.loads(data[SELECTED])["files"]
    for name in (WORD, CHECKER, EXPORTER):
        require(digest(data[name]) == selected[name], "selected source link: " + name)
    return data


def snapshot(data, directory):
    for name, body in data.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)


def command(args, timeout=60):
    return subprocess.run([str(arg) for arg in args], capture_output=True,
                          text=True, check=False, timeout=timeout)


def python(script, *args):
    # -I ignores inherited PYTHONOPTIMIZE; -B leaves the source inventory alone.
    return command([sys.executable, "-I", "-B", script, *args])


def fixture_word(original, name):
    require(original["scatter"][0] == [4, 5, 6, 7, 8], "fixed mutation row")
    require(len(set(original["ret"])) == len(original["ret"]) == 9,
            "injective retained slots")
    require(original["ret"][0] == 472, "fixed absent-slot dirty witness")
    result = copy.deepcopy(original)
    result["scatter"][0].extend(FIXTURES[name])
    return result


def word_operator(word):
    """Independent JSON evaluation, including actual occurrence semantics."""
    v, n = word["v"], 2 * word["v"] + word["R"]
    state = [1 << i for i in range(n)]
    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            copied = tuple(state[q] for q in word["ret"])
            for target, row in enumerate(word[section], start=v):
                for slot in row:
                    state[target] ^= copied[slot]
        else:
            for _frame, target, operands in word[section]:
                require(target not in operands, "JSON gate self operand")
                for source in operands:
                    state[target] ^= state[source]
    return state


def record_operator(body, n=661):
    """All arbitrary dirty F2 columns, with fresh immutable COPY/ERASE.

    MOVE is the identity only in this scalar projection. Native legality is a
    separate check. No zero-helper assumption is made.
    """
    require(0 < len(body) <= 30000 * 24 and len(body) % 24 == 0,
            "record alignment or bound")
    state = [1 << i for i in range(n)] + [0]
    owner = None
    for op, a, b, c, _frame, _phase in struct.iter_unpack("<6i", body):
        if op == 0:
            require(0 <= a < n, "MOVE register")
        elif op == 1:
            require(0 <= a < n and 0 <= b <= n and a != b, "ADD operands")
            require(b != n or owner is not None, "read unopened temporary")
            require(a != owner, "modified COPY source")
            if c % 2:
                state[a] ^= state[b]
        elif op == 2:
            require(owner is None and 0 <= a < n and b == n, "COPY lifecycle")
            owner, state[n] = a, state[a]
        elif op == 3:
            require(owner is not None and a == owner and b == n, "ERASE lifecycle")
            require(state[a] == state[n], "COPY source value changed")
            owner, state[n] = None, 0
        else:
            raise ValueError("unknown record opcode")
    require(owner is None and state[n] == 0, "unclosed temporary")
    return state[:n]


def expected_operator(v=111, n=661):
    return [(1 << i) ^ ((1 << (i - v)) if v <= i < 2 * v else 0)
            for i in range(n)]


def differences(actual, expected):
    require(len(actual) == len(expected) == 661, "column inventory")
    return [{"register": i, "input_columns": [j for j in range(661)
                                             if (a ^ e) >> j & 1]}
            for i, (a, e) in enumerate(zip(actual, expected)) if a != e]


def symbolic_cli(root, argument, receipt, accepted):
    result = python(root / CHECKER, argument, "--json", receipt)
    if not accepted:
        require(result.returncode == 1 and result.stdout.strip() == "REJECT targets not y + x: [0]"
                and not receipt.exists(), "symbolic endpoint rejection")
        return {"exit_code": 1, "rejection": result.stdout.strip()}
    require(result.returncode == 0 and receipt.is_file(), "symbolic checker: " + result.stderr)
    value = json.loads(receipt.read_bytes())
    require(value["status"] == "PASS_EXACT_REPLAY_AND_INTERLEAVED_INTERFACE"
            and value["columns"] == 661, "symbolic status and columns")
    require(all(value["hypotheses"].values()) and all(value["conclusion"].values()),
            "symbolic complete interface")
    require(value["copy_ranks"] == [7] * 9, "unchanged COPY rank bill")
    return {"exit_code": 0, "receipt": value}


def guard_cli(root, argument, directory, accepted, original_artifacts):
    results = {}
    for mode in ("check", "export"):
        output = directory / "guarded-export"
        args = [mode, argument] + ([output] if mode == "export" else [])
        result = python(root / BOUNDARY, *args)
        if accepted:
            require(result.returncode == 0, "guard positive: " + result.stderr)
            if mode == "export":
                require({name: (output / name).read_bytes() for name in ARTIFACTS}
                        == original_artifacts, "guard export changed bytes")
        else:
            require(result.returncode == 2 and "duplicate index" in result.stderr
                    and not result.stdout, "guard did not reject before delegation")
            require(not output.exists(), "guard created rejected export")
        results[mode] = {"exit_code": result.returncode}
    return results


def scalar_fixture(root, original, name, directory):
    directory.mkdir()
    word = fixture_word(original, name)
    argument = directory / "word.json.gz"
    argument.write_bytes(gzip.compress(canonical(word).encode(), mtime=0))
    symbolic = symbolic_cli(root, argument, directory / "symbolic.json",
                            name != "odd_absent")
    output = directory / "export"
    result = python(root / EXPORTER, argument, output)
    require(result.returncode == 0, "real exporter failed: " + result.stderr)
    artifacts = {item: (output / item).read_bytes() for item in ARTIFACTS}
    raw = artifacts["249-records.bin"]
    symbolic_action, export_action = word_operator(word), record_operator(raw)
    expected = expected_operator()
    require((symbolic_action == expected) == (name != "odd_absent"),
            "independent symbolic endpoint")
    require((export_action == expected) == (name in ("baseline", "odd_present")),
            "independent exported endpoint")
    require((export_action == symbolic_action) == (name != "even_absent"),
            "symbolic/export agreement")
    scatter_adds = sum(op == 1 and phase == 3
                       for op, _a, _b, _c, _f, phase in struct.iter_unpack("<6i", raw))
    summary = {
        "appended": FIXTURES[name], "row": word["scatter"][0],
        "occurrence_count": sum(map(len, word["scatter"])),
        "emitted_scatter_ADDs": scatter_adds, "records": len(raw) // 24,
        "artifacts_sha256": {item: digest(body) for item, body in artifacts.items()},
        "symbolic": symbolic,
        "guard": guard_cli(root, argument, directory, name == "baseline", artifacts),
        "symbolic_vs_expected": differences(symbolic_action, expected),
        "export_vs_expected": differences(export_action, expected),
        "export_vs_symbolic": differences(export_action, symbolic_action),
    }
    return artifacts, summary


def compile_native(root):
    compiler = os.environ.get("CXX", "c++")
    flags = [compiler, "-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9",
             "-DVPORTS=111", "-DRHELP=439"]
    flags += ["-I" + str(root / name) for name in (STANDIN, PORTABLE, BIT + "checkers")]
    probe = root / "backend.cpp"
    probe.write_text('#include <boost/multiprecision/cpp_int.hpp>\n'
                     '#ifndef INTEGER_MULT_CHECKED_CPP_INT_STANDIN\n'
                     '#error expected checked stand-in\n#endif\n')
    result = command(flags + ["-fsyntax-only", probe], timeout=120)
    require(result.returncode == 0, "native arithmetic backend: " + result.stderr)
    binaries = {}
    for name in ("legality_h", "columns_h"):
        target = root / name
        result = command(flags + [root / (BIT + "checkers/" + name + ".cpp"),
                                  "-o", target], timeout=120)
        require(result.returncode == 0 and target.is_file(), "native build: " + result.stderr)
        binaries[name] = target
    return binaries


def native_columns(binary, stream, output, accepted, rejection=COLUMN_REJECTION):
    result = command([binary, stream, output])
    if not accepted:
        require(result.returncode == 2 and result.stderr.strip() == rejection,
                "native rejection reason: " + result.stderr)
        require(not result.stdout and not output.exists(), "native false success receipt")
        return {"exit_code": 2, "rejection": rejection}
    require(result.returncode == 0 and output.is_file(), "native columns: " + result.stderr)
    value = json.loads(output.read_bytes())
    require(value["status"] == COLUMNS_PASS and value["formal_columns_checked"] == 883,
            "native status and complete physical columns")
    require(value["local_scalar_stream"] == str(stream), "native stream binding")
    value["local_scalar_stream"] = "COHORT249-RECORDS.bin"
    seconds = value.pop("seconds")
    require(type(seconds) in (int, float) and math.isfinite(seconds) and seconds >= 0,
            "native timing field")
    diagnostics = result.stderr.splitlines()
    require(len(diagnostics) == 5, "five native stage diagnostics")
    for stage, line in enumerate(diagnostics):
        match = re.fullmatch(r"stage (\d) PASS elapsed ([\d.eE+-]+)s", line)
        require(match is not None and int(match[1]) == stage, "stage sequence")
        require(math.isfinite(float(match[2])) and float(match[2]) >= 0, "stage timing")
    return {"exit_code": 0, "receipt": value}


def native_fixture(root, directory, binaries, accepted, summary):
    output = directory / "export"
    incoming, outgoing = directory / "cin", directory / "cout"
    result = python(root / (BIT + "regression/stage_cohort.py"),
                    output, output, incoming, outgoing)
    require(result.returncode == 0, "cohort staging: " + result.stderr)
    stream = outgoing / "COHORT249-RECORDS.bin"
    require(stream.read_bytes() == (output / "249-records.bin").read_bytes(),
            "staging stream identity")
    receipt = directory / "legality.json"
    result = command([binaries["legality_h"], incoming, outgoing, receipt])
    require(result.returncode == 0 and receipt.exists(), "native legality: " + result.stderr)
    legal = json.loads(receipt.read_bytes())
    require(legal["status"] == LEGALITY_PASS and legal["records"] == summary["records"],
            "native legality status and records")
    require(legal["rank_mass"] == 5129 and legal["copies"] == legal["erasures"] == 9,
            "native COPY/restoration bill")
    require(legal["common_frame_ADDs"] == summary["records"] - 2929, "native ADD bill")
    columns = native_columns(binaries["columns_h"], stream, directory / "columns.json", accepted)
    return {"legality": legal, "columns": columns}


def native_control(root, binaries, raw):
    records = list(struct.iter_unpack("<6i", raw))
    index = next(i for i, row in enumerate(records) if row[0] == 1 and row[5] == 3)
    omitted = raw[:24 * index] + raw[24 * (index + 1):]
    require(record_operator(omitted) != expected_operator(), "nonvacuous omitted scatter ADD")
    path = root / "omitted-scatter.bin"
    path.write_bytes(omitted)
    omission = native_columns(binaries["columns_h"], path, root / "omission.json", False)
    truncated = root / "truncated.bin"
    truncated.write_bytes(raw[:-1])
    alignment = native_columns(binaries["columns_h"], truncated, root / "alignment.json",
                               False, "stream alignment")
    return {"omitted_scatter_ADD": omission, "truncated_stream": alignment}


def audit(data, directory, native=False):
    snapshot(data, directory)
    original = json.loads(gzip.decompress(data[WORD]))
    require(original["v"] == 111 and original["R"] == 439, "fixed selected dimensions")
    binaries = compile_native(directory) if native else None
    artifacts, fixtures, native_results = {}, {}, {}
    for name in FIXTURES:
        path = directory / name
        artifacts[name], fixtures[name] = scalar_fixture(directory, original, name, path)
        if native:
            native_results[name] = native_fixture(directory, path, binaries,
                                                  name in ("baseline", "odd_present"), fixtures[name])
    require(artifacts["baseline"] == artifacts["odd_present"], "existing triple artifact identity")
    require(artifacts["even_absent"] == artifacts["odd_absent"], "absent fixtures artifact identity")
    scalar = {"status": "PASS_SCATTER_ODD_BOUNDARY", "columns": 661, "fixtures": fixtures,
              "baseline_equals_odd_present_all_artifacts": True,
              "even_absent_equals_odd_absent_all_artifacts": True}
    if not native:
        return scalar, None
    require(native_results["baseline"] == native_results["odd_present"],
            "existing triple native receipt identity")
    require(native_results["even_absent"] == native_results["odd_absent"],
            "absent fixtures native receipt identity")
    native_receipt = {"status": "PASS_SCATTER_ODD_NATIVE", "backend": "checked_cpp_int_128_standin",
                      "fixtures": native_results,
                      "controls": native_control(directory, binaries, artifacts["baseline"]["249-records.bin"])}
    return scalar, native_receipt


def check_receipt(result, filename):
    expected = json.loads((PACKAGE / filename).read_bytes())
    require(canonical(result) == canonical(expected), "typed receipt mismatch: " + filename)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", action="store_true", help="compile and run two C++17 checkers serially")
    parser.add_argument("--write-receipts", type=Path, help="write to a NEW directory; never replace evidence")
    args = parser.parse_args()
    data = sources()
    if args.write_receipts is not None:
        require(not args.write_receipts.exists(), "receipt directory already exists")
    with tempfile.TemporaryDirectory(prefix="scatter-odd-") as temporary:
        scalar, native = audit(data, Path(temporary), args.native)
    if args.write_receipts is not None:
        args.write_receipts.mkdir()
        (args.write_receipts / "RESULT.json").write_text(canonical(scalar))
        if native is not None:
            (args.write_receipts / "NATIVE.json").write_text(canonical(native))
    else:
        check_receipt(scalar, "RESULT.json")
        if native is not None:
            check_receipt(native, "NATIVE.json")
    print(scalar["status"], "fixtures=4 columns=661 guarded_duplicates_rejected=3")
    if native is not None:
        print(native["status"], "legality_accepts=4 columns_accept=2 columns_reject=2 controls=2")


if __name__ == "__main__":
    main()
