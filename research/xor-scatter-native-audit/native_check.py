"""Fresh Boost-native checks of a fixed XOR-normalised scatter boundary.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
The retained C++ checkers and staging script are invoked without source edits.
Their lineage and the earlier native control design are credited in README.md.
"""

from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import signal
import struct
import subprocess
import sys

CHECKERS = Path("research/e8-bit-carrier-skeleton/code/bit/checkers")
STAGER = Path("research/e8-bit-carrier-skeleton/code/bit/regression/stage_cohort.py")
RECORD = struct.Struct("<6i")
LEGAL_PASS = "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE"
COLUMN_PASS = "PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL"
ENDPOINT_FAILURE = "local defining-decoder full formal column"
FIXTURES = ("baseline", "paired_absent", "odd_existing", "retained_alias")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def child_limits():
    """The historical legality executable aborts on rejected inputs."""
    import resource
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def command(arguments, timeout=120):
    environment = os.environ.copy()
    for name in ("CPATH", "CPLUS_INCLUDE_PATH", "C_INCLUDE_PATH", "PYTHONOPTIMIZE"):
        environment.pop(name, None)
    options = {"start_new_session": True, "preexec_fn": child_limits} if os.name == "posix" else {}
    process = subprocess.Popen(
        [str(argument) for argument in arguments], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, env=environment, **options,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        return subprocess.CompletedProcess(arguments, process.returncode, stdout, stderr)
    finally:
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        elif process.poll() is None:
            process.kill()
        process.wait()


def read_records(raw):
    require(0 < len(raw) <= 100000 * RECORD.size and len(raw) % RECORD.size == 0,
            "bounded aligned native stream")
    records = list(RECORD.iter_unpack(raw))
    require(all(row[0] in range(4) for row in records), "native stream opcode")
    return records


def invoice(records):
    operations = Counter(row[0] for row in records)
    ranks = Counter()
    for op, _a, _b, _c, frame, charge in records:
        if op == 0 and frame:
            ranks[frame] += 1
        elif op == 2:
            ranks[charge] += 1
    return {
        "records": len(records), "moves": operations[0], "adds": operations[1],
        "copies": operations[2], "erasures": operations[3],
        "scatter_adds": sum(row[0] == 1 and row[5] == 3 for row in records),
        "rank_mass": sum(rank * count for rank, count in ranks.items()),
        "paid_histogram": [[rank, ranks[rank]] for rank in sorted(ranks)],
    }


def prefix_invoice(records):
    """Unbounded Python integers independently check the native signed bill."""
    events = [row for row in records if row[0] != 0]
    maxima = []
    for reverse in (False, True):
        norms, peak = [1] * 662, 1
        for op, a, b, coefficient, _f, _z in (reversed(events) if reverse else events):
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                norms[a] += abs(coefficient) * norms[b]
                peak = max(peak, norms[a])
            elif op == 2:
                norms[661] = norms[a]
            else:
                norms[661] = 0
        require(norms[661] == 0, "prefix temporary restored")
        maxima.append(peak)
    forward, backward = maxima
    payload = 64 * forward ** 3 * backward ** 2
    return {"forward": str(forward), "reverse": str(backward),
            "payload": str(payload), "bits": payload.bit_length()}


def boost_dependencies(dependency_path, boost_include, require_version=False):
    """Bind the compiler's actual Boost header dependencies, not a guessed inventory."""
    text = dependency_path.read_text(encoding="utf-8").replace("\\\n", " ")
    require(text.startswith("native-object:"), "compiler dependency target")
    paths = [Path(token.replace("$$", "$")) for token in shlex.split(text.split(":", 1)[1])]
    expected_root = boost_include.resolve()
    boost = {}
    for path in paths:
        parts = path.parts
        if "boost" not in parts:
            continue
        resolved = path.resolve()
        require(resolved.is_relative_to(expected_root / "boost"), "foreign Boost header: " + str(path))
        relative = resolved.relative_to(expected_root).as_posix()
        boost[relative] = hashlib.sha256(resolved.read_bytes()).hexdigest()
    require("boost/multiprecision/cpp_int.hpp" in boost, "compiler did not resolve cpp_int header")
    require(not require_version or "boost/version.hpp" in boost, "compiler did not resolve Boost version")
    return boost


def probe_boost(flags, workdir, boost_include, compiler):
    source, binary = workdir / "boost_probe.cpp", workdir / "boost_probe"
    source.write_text(
        '#include <boost/version.hpp>\n#include <boost/multiprecision/cpp_int.hpp>\n'
        '#include <iostream>\n#include <limits>\n'
        '#ifdef INTEGER_MULT_CHECKED_CPP_INT_STANDIN\n#error stand-in forbidden\n#endif\n'
        'int main() { using boost::multiprecision::cpp_int;\n'
        'static_assert(!std::numeric_limits<cpp_int>::is_bounded, "unbounded cpp_int required");\n'
        'cpp_int a = (cpp_int(1) << 521) - 1, b = (cpp_int(1) << 257) + 1;\n'
        'cpp_int c = a * b; if (c / b != a || c % b != 0) return 2;\n'
        'std::cout << BOOST_VERSION << "\\n" << BOOST_LIB_VERSION << "\\n"\n'
        '<< c << "\\n" << boost::multiprecision::msb(c) + 1 << "\\n"; }\n',
        encoding="utf-8",
    )
    dependency = workdir / "boost_probe.d"
    built = command([*flags, "-MD", "-MF", dependency, "-MT", "native-object", source, "-o", binary])
    require(built.returncode == 0 and binary.is_file(), "Boost probe build: " + built.stderr)
    result = command([binary], timeout=15)
    expected = ((1 << 521) - 1) * ((1 << 257) + 1)
    rows = result.stdout.splitlines()
    require(result.returncode == 0 and len(rows) == 4, "Boost probe execution")
    require(rows[2:] == [str(expected), str(expected.bit_length())], "unbounded Boost probe value")
    version = command([compiler, "--version"], timeout=15)
    require(version.returncode == 0 and version.stdout, "compiler version")
    headers = {}
    for name in ("boost/version.hpp", "boost/multiprecision/cpp_int.hpp"):
        headers[name] = hashlib.sha256((boost_include / name).read_bytes()).hexdigest()
    return {"backend": "boost::multiprecision::cpp_int", "boost_version": int(rows[0]),
            "boost_lib_version": rows[1], "unbounded_probe_bits": expected.bit_length(),
            "unbounded_probe_decimal": str(expected), "header_sha256": headers,
            "compiler_version": version.stdout.splitlines()[0],
            "probe_dependencies": boost_dependencies(dependency, boost_include, require_version=True)}


def compile_native(snapshot_root, workdir, boost_include, compiler):
    require((boost_include / "boost/multiprecision/cpp_int.hpp").is_file(),
            "provide genuine Boost headers with --boost-include")
    flags = [compiler, "-O2", "-std=c++17", "-DHDIM=8", "-DVPORTS=111", "-DRHELP=439"]
    flags += ["-I" + str(path) for path in (boost_include, snapshot_root / CHECKERS)]
    backend = probe_boost(flags, workdir, boost_include, compiler)
    binaries, dependencies = {}, {}
    for copies in (9, 10):
        binaries[copies] = {}
        for checker in ("legality_h", "columns_h"):
            target = workdir / f"{checker}_{copies}"
            dependency = workdir / f"{checker}_{copies}.d"
            result = command([*flags, f"-DNCOPY={copies}", "-MD", "-MF", dependency, "-MT", "native-object",
                              snapshot_root / CHECKERS / (checker + ".cpp"), "-o", target])
            require(result.returncode == 0 and target.is_file(), "native compile: " + result.stderr)
            binaries[copies][checker] = target
            dependencies[f"{checker}_{copies}"] = boost_dependencies(dependency, boost_include)
    backend["native_dependencies"] = dependencies
    return binaries, backend


def checked_native(binary, arguments, receipt, expected_status, rejection=None):
    require(not receipt.exists() and not receipt.is_symlink(), "native receipt already exists")
    result = command([binary, *arguments, receipt], timeout=60)
    if rejection is not None:
        require(result.returncode != 0 and not receipt.exists() and not result.stdout,
                "native rejection published a receipt or reported success")
        require(rejection in result.stderr, "native rejection site: " + result.stderr)
        return {"accepted": False, "rejection": rejection}
    require(result.returncode == 0 and receipt.is_file(), "native failure: " + result.stderr)
    value = json.loads(receipt.read_bytes())
    require(value.get("status") == expected_status, "native status for invoked checker")
    if value["status"] == COLUMN_PASS:
        require(json.loads(result.stdout) == value, "native stdout/receipt equality")
        require(value["local_scalar_stream"] == str(arguments[0]), "native stream binding")
        value["local_scalar_stream"] = "COHORT249-RECORDS.bin"
        seconds = value.pop("seconds")
        require(type(seconds) in (int, float) and math.isfinite(seconds) and seconds >= 0,
                "native elapsed-time field")
        lines = result.stderr.splitlines()
        require(len(lines) == 5, "native five-stage diagnostics")
        for stage, line in enumerate(lines):
            match = re.fullmatch(r"stage (\d) PASS elapsed ([\d.eE+-]+)s", line)
            require(match is not None and int(match[1]) == stage, "native stage order")
            elapsed = float(match[2])
            require(math.isfinite(elapsed) and elapsed >= 0, "native stage elapsed time")
    return {"accepted": True, "receipt": value}


def stage(snapshot_root, output, directory):
    directory.mkdir()
    cin, cout = directory / "cin", directory / "cout"
    result = command([sys.executable, "-I", "-B", snapshot_root / STAGER, output, output, cin, cout], 30)
    require(result.returncode == 0, "native staging: " + result.stderr)
    require((cout / "COHORT249-RECORDS.bin").read_bytes() ==
            (output / "249-records.bin").read_bytes(), "native staging stream changed")
    require(json.loads((cout / "COHORT249-SELECTION.json").read_bytes()) == [], "empty selection")
    require(json.loads((cin / "249-DONOR-OWNERSHIP.json").read_bytes()) == {"donor_keys": []},
            "staging donor scope")
    return cin, cout


def reconcile(result, expected_invoice, expected_prefix, copies):
    legal = result["legality"]["receipt"]
    require(legal["status"] == LEGAL_PASS, "expected legality receipt")
    fields = (("records", "records"), ("nested_MOVEs", "moves"), ("common_frame_ADDs", "adds"),
              ("copies", "copies"), ("erasures", "erasures"), ("rank_mass", "rank_mass"),
              ("paid_histogram", "paid_histogram"))
    for native, literal in fields:
        require(legal[native] == expected_invoice[literal], "native event invoice: " + native)
    require(legal["selected_pairs"] == legal["selected_helpers"] == 0, "empty selection scope")
    require(legal["source_owner_intersections"] == legal["donor_intersections"] == 0,
            "native ownership scope")
    require(legal["all_final_frames_pass"] is True, "native final frames")
    columns = result["columns"]["receipt"]
    require(columns["status"] == COLUMN_PASS and columns["formal_columns_checked"] == 883,
            "native formal columns")
    require(columns["local_registers"] == 661 and columns["independent_dirty_registers"] == 439,
            "native arbitrary dirty-register domain")
    require(columns["local_raw_H"] == expected_invoice["paid_histogram"], "native column invoice")
    require(columns["local_scalar_additions"] == expected_invoice["adds"] and
            columns["five_stage_additions"] == 5 * expected_invoice["adds"], "five-stage ADD bill")
    require(columns["fresh_center_copies"] == 5 * copies and
            columns["reverse_fresh_center_copies"] == 2 * copies, "five-stage COPY bill")
    require([row["cancellation_free_signed_row_l1_upper"] for row in columns["signed_lift_prefix"]]
            == [expected_prefix["forward"], expected_prefix["reverse"]], "native exact prefix recurrence")
    require(columns["payload_prefix_upper"] == expected_prefix["payload"] and
            columns["payload_prefix_bits"] == expected_prefix["bits"], "native payload prefix")
    require(columns["copied_center_original_source_immutable"] is True, "native source immutability")
    require(columns["negative_controls"] == [{"omit_bridge": i, "rejected": True} for i in range(6)],
            "native bridge controls")


def fixture_checks(binaries, snapshot_root, name, output, workdir):
    records = read_records((output / "249-records.bin").read_bytes())
    literal, prefix = invoice(records), prefix_invoice(records)
    copies = 10 if name == "retained_alias" else 9
    require(literal["copies"] == literal["erasures"] == copies, "fixture copy count")
    require(literal["scatter_adds"] == 527 and literal["adds"] == 24305, "normalised ADD invoice")
    require(literal["records"] == (27236 if copies == 10 else 27234), "fixture record count")
    require(literal["rank_mass"] == (5136 if copies == 10 else 5129), "fixture paid rank mass")
    directory = workdir / name
    cin, cout = stage(snapshot_root, output, directory)
    stream = cout / "COHORT249-RECORDS.bin"
    outcomes = {}
    for contract in (9, 10):
        correct = copies == contract
        result = {
            "legality": checked_native(binaries[contract]["legality_h"], [cin, cout],
                                       directory / f"legality{contract}.json",
                                       LEGAL_PASS,
                                       None if correct else "unclosed COPY"),
            "columns": checked_native(binaries[contract]["columns_h"], [stream],
                                      directory / f"columns{contract}.json",
                                      COLUMN_PASS,
                                      None if correct else "center boundaries"),
        }
        if correct:
            reconcile(result, literal, prefix, copies)
        outcomes[str(contract)] = result
    return {"invoice": literal, "prefix": prefix, "contracts": outcomes}, records


def mutation_records(records, kind):
    mutated = [list(row) for row in records]
    copy_index = max(i for i, row in enumerate(records) if row[0] == 2)
    erase_index = next(i for i in range(copy_index + 1, len(records)) if records[i][0] == 3)
    require(erase_index == copy_index + 1, "normalised alias has empty COPY window")
    if kind == "underpriced_copy":
        mutated[copy_index][5] -= 1
        return mutated, copy_index, "COPY rank", None
    if kind == "wrong_erase_source":
        mutated[erase_index][1] = (mutated[erase_index][1] + 1) % 661
        return mutated, erase_index, "invalid ERASE lifecycle", "discard original-source binding"
    require(kind == "omitted_scatter_add", "unknown native mutation")
    index = next(i for i, row in enumerate(records) if row[0] == 1 and row[5] == 3)
    del mutated[index]
    return mutated, index, None, ENDPOINT_FAILURE


def scalar_differences(records):
    """Independent F2 endpoint projection only, with no claim about native geometry."""
    values = [1 << index for index in range(661)] + [0]
    for op, a, b, coefficient, _frame, _phase in records:
        if op == 1 and coefficient % 2:
            values[a] ^= values[b]
        elif op == 2:
            values[661] = values[a]
        elif op == 3:
            values[661] = 0
    differences = []
    for output in range(661):
        expected = (1 << output) ^ ((1 << (output - 111)) if 111 <= output < 222 else 0)
        delta = expected ^ values[output]
        if delta:
            differences.append({"output": output, "input_columns": [
                column for column in range(661) if delta >> column & 1]})
    require(values[661] == 0, "scalar control temporary restored")
    return differences


def reconcile_control(name, result, changed, baseline_invoice):
    literal = invoice(changed)
    if name == "underpriced_copy":
        columns = result["columns"]["receipt"]
        require(columns["local_raw_H"] == literal["paid_histogram"], "underpriced column invoice")
        require(columns["formal_columns_checked"] == 883 and columns["fresh_center_copies"] == 50,
                "underpriced unchanged column domain and copy count")
        require(literal["rank_mass"] == baseline_invoice["rank_mass"] - 1,
                "one-rank underpricing control")
    elif name == "omitted_scatter_add":
        legal = result["legality"]["receipt"]
        require(legal["records"] == baseline_invoice["records"] - 1 and
                legal["common_frame_ADDs"] == baseline_invoice["adds"] - 1,
                "single omitted ADD invoice")
        require(legal["rank_mass"] == baseline_invoice["rank_mass"] and
                legal["copies"] == legal["erasures"] == 10, "omission leaves COPY bill unchanged")
    differences = scalar_differences(changed)
    require(bool(differences) == (name == "omitted_scatter_add"), "independent control endpoint witness")
    return differences


def native_controls(binaries, records, workdir):
    directory = workdir / "retained_alias"
    cin, cout = directory / "cin", directory / "cout"
    stream = cout / "COHORT249-RECORDS.bin"
    original = stream.read_bytes()
    baseline_invoice = invoice(records)
    require(not scalar_differences(records), "independent positive alias endpoint")
    results = {}
    try:
        for name in ("underpriced_copy", "wrong_erase_source", "omitted_scatter_add"):
            changed, index, legal_error, column_error = mutation_records(records, name)
            changed_bytes = b"".join(RECORD.pack(*row) for row in changed)
            stream.write_bytes(changed_bytes)
            results[name] = {
                "legality": checked_native(binaries["legality_h"], [cin, cout],
                                           directory / (name + "_legal.json"), LEGAL_PASS, legal_error),
                "columns": checked_native(binaries["columns_h"], [stream],
                                          directory / (name + "_columns.json"), COLUMN_PASS, column_error),
            }
            results[name]["scalar_differences"] = reconcile_control(
                name, results[name], changed, baseline_invoice)
            results[name]["mutation"] = {
                "zero_based_record_index": index, "before": list(records[index]),
                "after": None if name == "omitted_scatter_add" else changed[index],
                "original_stream_sha256": hashlib.sha256(original).hexdigest(),
                "mutated_stream_sha256": hashlib.sha256(changed_bytes).hexdigest(),
            }
    finally:
        stream.write_bytes(original)
    require(stream.read_bytes() == original, "native control stream restored")
    return results


def run_native(snapshot_root, outputs_by_fixture, workdir, boost_include, compiler="c++"):
    snapshot_root, workdir, boost_include = map(Path, (snapshot_root, workdir, boost_include))
    require(set(outputs_by_fixture) == set(FIXTURES), "fixed native fixture inventory")
    workdir.mkdir(parents=True, exist_ok=False)
    binaries, backend = compile_native(snapshot_root, workdir, boost_include, compiler)
    results, streams = {}, {}
    for name in FIXTURES:
        results[name], streams[name] = fixture_checks(
            binaries, snapshot_root, name, Path(outputs_by_fixture[name]), workdir)
    for name in ("paired_absent", "odd_existing"):
        require(results[name] == results["baseline"], "same-byte normal forms have equal native receipts")
    require(results["retained_alias"]["prefix"] == results["baseline"]["prefix"],
            "empty alias copy preserves signed prefix")
    return {
        "status": "PASS_XOR_SCATTER_NATIVE_AUDIT", "backend": backend,
        "compile_contract": {"HDIM": 8, "VPORTS": 111, "RHELP": 439, "NCOPY": [9, 10]},
        "fixtures": results,
        "controls": native_controls(binaries[10], streams["retained_alias"], workdir),
        "scope": "Fixed complete boundary exports; empty kernel selection, no donors or owners; no supplier admission.",
        "no_new_kappa": True,
    }
