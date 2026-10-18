"""Compare the original and replacement words with the pinned cohort checkers.

Adapted from Ali Romman PR688 and Ross Richardson PR925 by Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
import os
import shlex
import subprocess
import sys


def run(root, out):
    package = root / "research/e8-bit-carrier-skeleton"
    bit = package / "code/bit"
    checkers = bit / "checkers"
    python = [sys.executable, "-I", "-B"]
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    include = os.environ.get("BOOST_INCLUDE", "/usr/include")
    flags = ["-O2", "-std=c++17", "-DHDIM=8", "-DNCOPY=9", "-DVPORTS=120", "-DRHELP=480",
             "-I" + str(package / "portable-include"), "-I" + str(checkers), "-I" + include]
    bindir = out / "bin"
    bindir.mkdir()

    def call(name, command):
        with (out / (name + ".log")).open("w") as log:
            subprocess.run(list(map(str, command)), check=True, stdout=log, stderr=subprocess.STDOUT)

    call("compile-legality", compiler + flags + ["-o", bindir / "legality", checkers / "legality_h.cpp"])
    for pairs in (2, 4, 5):
        call("compile-columns" + str(pairs), compiler + flags + ["-DKPAIRS=" + str(pairs), "-o",
             bindir / ("columns" + str(pairs)), checkers / "columns_k.cpp"])
    call("relax", python + [bit / "independent/relax.py", out / "relaxed"])
    results = {}
    python_receipt = json.loads((out / "RESULT.json").read_text())["words"]
    for name in ("original", "candidate"):
        call(name + "-independent", [sys.executable, "-I", "-B", out / "relaxed/checkword_mut.py",
             out / (name + ".json.gz"), package / "code/pricing"])
        base = out / name
        records, cin, cout = (base / item for item in ("records", "cin", "cout"))
        call(name + "-cohort", python + [bit / "regression/stage_cohort.py", records, records, cin, cout])
        call(name + "-legality", [bindir / "legality", cin, cout, cout / "legality.json"])
        legality = json.loads((cout / "legality.json").read_text())
        if legality["status"] != "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE":
            raise ValueError("Legality did not pass")
        results[name] = {"legality": legality, "stages": {}}
        for pairs in (2, 4, 5):
            receipt = cout / ("columns.json" if pairs == 2 else "columns" + str(pairs) + ".json")
            call(name + "-columns" + str(pairs), [bindir / ("columns" + str(pairs)),
                 cout / "COHORT249-RECORDS.bin", receipt])
            data = json.loads(receipt.read_text())
            expected_status = ("PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL" if pairs == 2
                               else "PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL")
            if data["status"] != expected_status:
                raise ValueError("Formal columns did not pass")
            expected = 6 * (pairs - 1)
            if (len(data["negative_controls"]) != expected
                    or not all(c["rejected"] for c in data["negative_controls"])):
                raise ValueError("A bridge control failed")
            if data["formal_columns_checked"] != 240 * pairs + 480:
                raise ValueError("Wrong formal column count")
            reference = python_receipt[name]
            prefixes = [int(p["cancellation_free_signed_row_l1_upper"]) for p in data["signed_lift_prefix"]]
            expected_profile = [[int(k), v] for k, v in reference["paid_histogram"].items()]
            if (prefixes != [reference["F"], reference["B"]]
                    or data["payload_prefix_upper"] != reference["payload_upper"]
                    or data["local_scalar_additions"] != reference["ADDs"]
                    or data["local_raw_H"] != expected_profile):
                raise ValueError("Native and independent Python accounting disagree")
            data.pop("seconds", None)
            data.pop("local_scalar_stream", None)
            results[name]["stages"][str(2 * pairs + 1)] = data
    for stages in ("5", "9", "11"):
        old, new = (results[name]["stages"][stages] for name in ("original", "candidate"))
        if old["local_raw_H"] != new["local_raw_H"] or old["local_scalar_additions"] - new["local_scalar_additions"] != 24:
            raise ValueError("Paid profile or XOR saving differs")
        if int(new["payload_prefix_upper"]) > int(old["payload_prefix_upper"]):
            raise ValueError("Payload bound increased")
        for a, b in zip(old["signed_lift_prefix"], new["signed_lift_prefix"]):
            if a["reverse"] != b["reverse"] or int(b["cancellation_free_signed_row_l1_upper"]) > int(a["cancellation_free_signed_row_l1_upper"]):
                raise ValueError("Signed bound increased")
    return results


def main():
    import argparse
    import hashlib
    import platform
    import tempfile
    from pathlib import Path

    here = Path(__file__).resolve().parent
    root = here.parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', action='store_true')
    parser.add_argument('--output', type=Path, help='new output directory; preserve all native logs')
    args = parser.parse_args()
    pins = json.loads((here / 'SOURCES.json').read_text())
    for path, expected in pins['execution_inputs'].items():
        if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected['sha256']:
            raise ValueError('source hash mismatch: ' + path)
    if not (Path(os.environ.get('BOOST_INCLUDE', '/usr/include')) / 'boost/multiprecision/cpp_int.hpp').is_file():
        raise ValueError('Set BOOST_INCLUDE to the directory containing boost/multiprecision/cpp_int.hpp')
    with tempfile.TemporaryDirectory(prefix='r480-quad12-exact-native-') as temporary:
        work = args.output.resolve() if args.output else Path(temporary) / 'work'
        # The verifier refuses an existing path, and emits the two bound inputs.
        subprocess.run([sys.executable, '-I', '-B', str(here / 'verify.py'), '--output', str(work)], check=True)
        result = run(root, work)
        receipt = {'schema': 'r480-quad12-exact-native/1', 'words': result,
                   'normalization': 'Only seconds and local_scalar_stream removed; all other native fields retained.'}
        path = here / 'NATIVE-CERTIFICATE.json'
        if args.write_certificate:
            path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
        elif json.dumps(receipt, sort_keys=True) != json.dumps(json.loads(path.read_text()), sort_keys=True):
            raise ValueError('native certificate mismatch')
        (work / 'ENVIRONMENT.json').write_text(json.dumps({'python': sys.version, 'platform': platform.platform(),
            'compiler': subprocess.check_output(shlex.split(os.environ.get('CXX', 'c++')) + ['--version'], text=True),
            'boost_include': os.environ.get('BOOST_INCLUDE', '/usr/include'),
            'boost_version_header_sha256': hashlib.sha256((Path(os.environ.get('BOOST_INCLUDE', '/usr/include')) / 'boost/version.hpp').read_bytes()).hexdigest(),
            'boost_cpp_int_sha256': hashlib.sha256((Path(os.environ.get('BOOST_INCLUDE', '/usr/include')) / 'boost/multiprecision/cpp_int.hpp').read_bytes()).hexdigest()}, indent=2) + '\n')
        print('PASS_R480_QUAD12_NATIVE words=2 columns=960/1440/1680 bridge_controls=96 ADDs=33958->33934')


if __name__ == '__main__':
    main()
