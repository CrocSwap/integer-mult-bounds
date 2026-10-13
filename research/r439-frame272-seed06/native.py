#!/usr/bin/env python3
"""Fresh native legality and 5/9/11-stage checks for the frame-272 replacement.

Current frame-272 adaptation: GitHub @woklerx, substantial OpenAI Codex assistance.
The Windows compiler adapter is adapted from PR989 at
101103e56e3effdb268ce90110c6caa4c6885671,
research/r439-four-block-composition/native.py. That predecessor is
adapted from Krishnendu Purohit (@Deftsalt-debug)'s r439-block1-schedule/native.py,
which credits Ali Romman / PR688's r420-two-block-composition/native.py.
Environment reporting follows Ross Richardson's r439-frame524-seed13/native.py.
These predecessors and this contribution include substantial OpenAI Codex
assistance. Apache-2.0; original checker/exporter source notices are retained.

Requires Python 3, a C++17 compiler and Boost headers; installs nothing. Linux:
  BOOST_INCLUDE=/usr/include CXX=c++ python3 native.py --output /tmp/r439-native
Windows: run from an x64 Visual Studio developer shell with CXX=cl and set
BOOST_INCLUDE to the directory containing boost/multiprecision/cpp_int.hpp.
GCC/Clang are also supported. A literal compiler path containing spaces is valid.
Use --write-receipt once to save NATIVE.json and NATIVE-ENVIRONMENT.json; a normal
run independently regenerates all records and compares the mathematical receipt.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PREDECESSOR = {"pr": 989, "head": "101103e56e3effdb268ce90110c6caa4c6885671",
               "path": "research/r439-four-block-composition/native.py",
               "git_source_sha256": "bc8d7d09c4e47e7bdd6b758bd0593614e78448b0a849cd83ef150baee44daf04",
               "observed_checkout_sha256": "387ac33c3b34f65604381ad21bda7780f1fbdf6154555cdfb0b6bd7b40ed18fa",
               "checkout_difference": "Output encoding/newline and source-pin JSON hash normalization only; pinned-source conventions retained here."}
spec = importlib.util.spec_from_file_location("frame272_verifier", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def run(out, write):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    package = verify.ROOT / "research/e8-bit-carrier-skeleton"
    bit = package / "code/bit"
    checkers = bit / "checkers"
    required = [p.relative_to(verify.ROOT).as_posix() for p in
                (bit / "regression/stage_cohort.py", checkers / "legality_h.cpp",
                 checkers / "columns_k.cpp", checkers / "json.hpp",
                 package / "portable-include/bits/stdc++.h")]
    verify.need(pins["native_inputs"] == required, "native input coverage mismatch")
    for path in required:
        verify.need(verify.sha((verify.ROOT / path).read_bytes()) == pins["files"][path]["sha256"],
                    "native source hash mismatch: " + path)
    raw_compiler = os.environ.get("CXX", "c++")
    compiler = ([raw_compiler] if Path(raw_compiler).is_file() else
                shlex.split(raw_compiler, posix=os.name != "nt"))
    if os.name == "nt":
        compiler = [part.strip('"') for part in compiler]
    verify.need(bool(compiler), "CXX must name a C++17 compiler")
    executable = shutil.which(compiler[0])
    verify.need(executable is not None, "CXX compiler not found: " + compiler[0])
    boost = Path(os.environ.get("BOOST_INCLUDE", "/usr/include")).resolve()
    boost_headers = [boost / "boost/version.hpp", boost / "boost/multiprecision/cpp_int.hpp"]
    verify.need(all(p.is_file() for p in boost_headers), "Set BOOST_INCLUDE to a Boost header root")
    local = out / "local"
    local.mkdir()
    verify.run(local, False)
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    bindir = out / "bin"
    bindir.mkdir()
    msvc = Path(compiler[0]).stem.lower() in ("cl", "clang-cl")
    includes = [package / "portable-include", checkers, boost]
    definitions = ["HDIM=8", "NCOPY=9", "VPORTS=111", "RHELP=439"]
    flags = (["/nologo", "/O2", "/std:c++17", "/EHsc"] if msvc else ["-O2", "-std=c++17"])
    flags += [("/D" if msvc else "-D") + x for x in definitions]
    flags += [("/I" if msvc else "-I") + str(x) for x in includes]
    commands = {}

    def call(name, command):
        commands[name] = list(map(str, command))
        with (out / (name + ".log")).open("w") as log:
            subprocess.run(commands[name], check=True, cwd=bindir, stdout=log, stderr=subprocess.STDOUT)

    def compile_checker(name, source, extra=()):
        binary = bindir / (name + (".exe" if os.name == "nt" else ""))
        output = ["/Fe:" + str(binary), "/Fo:" + str(bindir / (name + ".obj"))] if msvc else ["-o", binary]
        call("compile-" + name, compiler + flags + list(extra) + output + [checkers / source])
        return binary

    def receipt(path):
        data = json.loads(path.read_text())
        # Only execution time and the temporary absolute stream pathname vary.
        data.pop("seconds", None)
        data.pop("local_scalar_stream", None)
        return data

    legality_binary = compile_checker("legality", "legality_h.cpp")
    column_binaries = {pairs: compile_checker("columns" + str(pairs), "columns_k.cpp",
                       [("/D" if msvc else "-D") + "KPAIRS=" + str(pairs)]) for pairs in (2, 4, 5)}
    results = {}
    for name, additions in (("original", 24305), ("replacement", 24283)):
        records = local / name / "records"
        cin, cout = out / name / "cin", out / name / "cout"
        call(name + "-cohort", [sys.executable, "-I", "-B", bit / "regression/stage_cohort.py",
                                records, records, cin, cout])
        call(name + "-legality", [legality_binary, cin, cout, cout / "legality.json"])
        legality = receipt(cout / "legality.json")
        verify.need(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
                    "native legality did not pass")
        verify.need(legality["rank_mass"] == 5129 and legality["copies"] == legality["erasures"] == 9
                    and legality["common_frame_ADDs"] == additions, "native legality price mismatch")
        results[name] = {"legality": legality, "stages": {}}
        for pairs in (2, 4, 5):
            path = cout / ("columns" + str(pairs) + ".json")
            call(name + "-columns" + str(pairs), [column_binaries[pairs], cout / "COHORT249-RECORDS.bin", path])
            data = receipt(path)
            status = ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL" if pairs == 2 else
                      "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL")
            verify.need(data["status"] == status, "native columns did not pass")
            verify.need(data["formal_columns_checked"] == 222 * pairs + 439, "column coverage mismatch")
            controls = data["negative_controls"]
            verify.need(len(controls) == 6 * (pairs - 1) and all(c["rejected"] for c in controls),
                        "native bridge control failed")
            expected = certificate["native_records"][name]
            verify.need(data["local_scalar_additions"] == expected["adds"] == additions,
                        "native/Python count mismatch")
            results[name]["stages"][str(2 * pairs + 1)] = data
    for stages in ("5", "9", "11"):
        old, new = (results[name]["stages"][stages] for name in ("original", "replacement"))
        verify.need(old["local_raw_H"] == new["local_raw_H"] and
                    old["local_scalar_additions"] - new["local_scalar_additions"] == 22,
                    "native paid profile or saving mismatch")
        verify.need(int(new["payload_prefix_upper"]) <= int(old["payload_prefix_upper"]),
                    "native prefix increased")
        verify.need(int(new["payload_prefix_bits"]) <= int(old["payload_prefix_bits"]),
                    "native prefix bit count increased")
        verify.need(len(old["signed_lift_prefix"]) == len(new["signed_lift_prefix"]) == 2,
                    "native signed prefix coverage mismatch")
        for before, after in zip(old["signed_lift_prefix"], new["signed_lift_prefix"]):
            verify.need(before["reverse"] == after["reverse"] and
                        int(after["cancellation_free_signed_row_l1_upper"]) <=
                        int(before["cancellation_free_signed_row_l1_upper"]) and
                        int(after["bits"]) <= int(before["bits"]),
                        "native signed prefix bound increased")
        verify.need(new["copied_center_original_source_immutable"] is True,
                    "native copied center source changed")
    old_legality, new_legality = (results[name]["legality"] for name in ("original", "replacement"))
    for key in ("paid_histogram", "rank_mass", "copies", "erasures", "nested_MOVEs"):
        verify.need(old_legality[key] == new_legality[key], "native legality resource changed: " + key)
    verify.need(new_legality["max_inherited_integer_abs"] <= old_legality["max_inherited_integer_abs"],
                "native inherited integer bound increased")
    path = HERE / "NATIVE.json"
    if write:
        path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        version = subprocess.run(compiler + (["/Bv"] if msvc else ["--version"]),
                                 capture_output=True, text=True)
        environment = {"runner_predecessor": PREDECESSOR, "python": sys.version, "python_executable": sys.executable,
                       "platform": platform.platform(), "compiler_command": compiler,
                       "compiler_path": str(Path(executable).resolve()),
                       "compiler_sha256": verify.sha(Path(executable).read_bytes()),
                       "compiler_version_output": version.stdout + version.stderr,
                       "boost_include": str(boost),
                       "boost_header_sha256": {str(p): verify.sha(p.read_bytes()) for p in boost_headers},
                       "boost_version_header": boost_headers[0].read_text(),
                       "source_pins_canonical_sha256": verify.sha(verify.canonical(
                           json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8")))),
                       "commands": commands}
        (HERE / "NATIVE-ENVIRONMENT.json").write_text(json.dumps(environment, indent=2, sort_keys=True) + "\n",
                                                   encoding="utf-8", newline="\n")
    else:
        verify.need(results == json.loads(path.read_text()), "native receipt mismatch")
    print("PASS_R439_FRAME272_NATIVE words=2 saving=22 stages=5,9,11 columns=883,1327,1549 bridge_controls=96")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="fresh directory for logs and execution artifacts")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        run(args.output.resolve(), args.write_receipt)
    else:
        with tempfile.TemporaryDirectory(prefix="r439-frame272-native-") as temporary:
            run(Path(temporary), args.write_receipt)


if __name__ == "__main__":
    main()
