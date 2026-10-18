#!/usr/bin/env python3
"""Optional inherited local replay: Python standard library, C++17, Boost headers.

Usage: BOOST_INCLUDE=/path/to/boost python native_replay.py --work /new/output
CXX defaults to c++; BOOST_INCLUDE defaults to /usr/include. This does not run
global template emission, hosting, assembly, or the repository-wide suite.

Prepared for Hao Yan (@FanPUYen) with substantial OpenAI Codex assistance.
Apache-2.0. The replayed checkers are attributed to Dylan Crow and eumemic,
with their original Anthropic Claude assistance notices retained unchanged.
"""
import argparse
import gzip
import hashlib
import json
import os
import platform
import re
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PARENT = ROOT / "research/e8-bit-carrier-skeleton"
PARENT_MANIFEST_SHA256 = "7f25c41d0400ef5adf763eae6e166003a9b59e5a655b860c04b052f6731c7297"
SOURCE = ROOT / "research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz"
SOURCE_SHA256 = "92e399e9a486b55229b5624632ac54f800dd9e022f2aee97f1e5f264bbc0ef5c"


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_sha(path):
    w = json.loads(gzip.decompress(path.read_bytes()))
    return hashlib.sha256(json.dumps(w, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def pinned_parent():
    """Pin the full inherited package, including all imported checker helpers."""
    manifest = PARENT / "MANIFEST.sha256"
    require(sha(manifest) == PARENT_MANIFEST_SHA256, "inherited manifest changed")
    seen = set()
    for row in manifest.read_text().splitlines():
        wanted, name = row.split("  ", 1)
        path = (PARENT / name).resolve()
        require(PARENT in path.parents and name not in seen, "invalid manifest path")
        require(sha(path) == wanted, "inherited source changed: " + name)
        seen.add(name)
    require(len(seen) == 93, "inherited manifest file count")
    # Refuse an unlisted Python/header sibling that could shadow a pinned import.
    code = {str(p.relative_to(PARENT)) for p in PARENT.rglob("*")
            if p.is_file() and p.suffix in (".py", ".h", ".hpp", ".cpp")}
    require(code <= seen, "unlisted inherited code files")
    require(sha(SOURCE) == SOURCE_SHA256, "R480 source word changed")


class Replay:
    def __init__(self, work):
        self.work = work
        self.python = sys.executable
        self.cxx = shlex.split(os.environ.get("CXX", "c++"))
        require(bool(self.cxx), "empty CXX")
        self.boost = Path(os.environ.get("BOOST_INCLUDE", "/usr/include")).resolve()
        self.env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONINTMAXSTRDIGITS="0",
                        TMPDIR=str(work / "tmp"))
        (work / "tmp").mkdir()
        (work / "logs").mkdir()
        (work / "bin").mkdir()
        self.commands = []

    def normalized(self, value):
        for old, new in ((self.python, "{python}"), (str(self.work), "{work}"),
                         (str(self.boost), "{boost_include}"), (str(ROOT), "{repo}")):
            value = value.replace(old, new)
        return value

    def run(self, name, command, expected_failure=None):
        command = list(map(str, command))
        result = subprocess.run(command, env=self.env, capture_output=True, text=True)
        (self.work / "logs" / (name + ".log")).write_text(result.stdout + result.stderr)
        self.commands.append({"name": name, "command": self.normalized(shlex.join(command)),
                              "exit_code": result.returncode})
        (self.work / "commands.json").write_text(json.dumps(self.commands, indent=2) + "\n")
        if expected_failure is None:
            require(result.returncode == 0, name + " failed; see " + str(self.work / "logs" / (name + ".log")))
        else:
            require(result.returncode != 0 and expected_failure in result.stderr,
                    name + " did not reject the expected control")
        print("PASS " + name, flush=True)
        return result.stdout

    def py(self, name, script, *args, expected_failure=None):
        return self.run(name, [self.python, "-I", "-B", script, *args], expected_failure)

    def compile(self):
        checkers = PARENT / "code/bit/checkers"
        inc = ["-I" + str(PARENT / "portable-include"), "-I" + str(checkers), "-I" + str(self.boost)]
        common = self.cxx + ["-O2", "-std=c++17", "-DHDIM=8"]
        specs = [("legality", "legality_h.cpp", ["-DNCOPY=9"]),
                 ("legality_ncopy_h", "legality_h.cpp", [])]
        for name, source, extra in (("columns_h", "columns_h.cpp", []),
                                    ("columns_k2", "columns_k.cpp", ["-DKPAIRS=2"]),
                                    ("columns_k4", "columns_k.cpp", ["-DKPAIRS=4"]),
                                    ("columns_k5", "columns_k.cpp", ["-DKPAIRS=5"])):
            specs.append((name, source, ["-DNCOPY=9", "-DVPORTS=120", "-DRHELP=480"] + extra))
        for name, source, extra in specs:
            self.run("compile-" + name, common + extra + inc +
                     ["-o", self.work / "bin" / name, checkers / source])

    def case(self, name, word):
        d = self.work / name
        d.mkdir()
        bit = PARENT / "code/bit"
        pricing = PARENT / "code/pricing"
        binary = self.work / "bin"
        py = lambda step, script, *args, **kwargs: self.py(name + "-" + step, script, *args, **kwargs)
        py("relax", bit / "independent/relax.py", d / "rchk")
        py("stock-refusal", bit / "independent/checkword.py", word, pricing,
           expected_failure="x register written")
        text = py("all720", d / "rchk/checkword_mut.py", word, pricing)
        require("legality + exact F2 on all 720 columns: PASS" in text, "all-column receipt")
        py("interface", bit / "independent/interface.py", word, "--json", d / "interface.json")
        text = py("word-controls", bit / "independent/mutate_mut.py", word,
                  d / "rchk/checkword_mut.py", pricing, bit / "independent/interface.py")
        require("6 word-level mutants and 5 mutable-source mutants rejected" in text and
                "PASS interface.py: 2 hypothesis controls rejected" in text, "word controls receipt")
        py("export", bit / "export_records.py", word, d / "records")
        py("cohort", bit / "regression/stage_cohort.py", d / "records", d / "records", d / "cin", d / "cout")
        co = d / "cout"
        self.run(name + "-legality", [binary / "legality", d / "cin", co, co / "legality.json"])
        for checker in ("columns_h", "columns_k2", "columns_k4", "columns_k5"):
            self.run(name + "-" + checker,
                     [binary / checker, co / "COHORT249-RECORDS.bin", co / (checker + ".json")])
        text = py("record-controls", bit / "mutate_records.py", d / "records", d / "cin", co,
                  binary / "legality", binary / "columns_k5", binary / "legality_ncopy_h")
        require("PASS all 6 record-level negative controls rejected" in text, "record controls receipt")
        text = py("source-record-controls", bit / "mutate_records_mut.py", word, d / "records", d / "cin", co,
                  binary / "legality", binary / "columns_h", binary / "columns_k5")
        require("PASS all 3 record-level mutable-source mutants rejected" in text, "source record controls receipt")
        text = py("gram", bit / "checkers/gram_frames.py", d / "records", "--gram", "e8ham", "--h", "8", "--positive")
        require("672 frames checked, all nondegenerate and positive definite" in text and
                "primes [2]" in text, "Gram receipt")
        return semantic_case(word, d)


def semantic_case(word, directory):
    """Only deterministic, independently computed receipt fields are frozen."""
    co = directory / "cout"
    read = lambda name: json.loads((co / (name + ".json")).read_text())
    legality = read("legality")
    require(legality["status"] == "PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE",
            "legality status")
    five, k2 = read("columns_h"), read("columns_k2")
    require({k: v for k, v in five.items() if k != "seconds"} ==
            {k: v for k, v in k2.items() if k != "seconds"}, "KPAIRS=2 must reproduce five-stage receipt")
    stages = {}
    for label, source, count in (("five", "columns_h", 5), ("nine", "columns_k4", 9),
                                 ("eleven", "columns_k5", 11)):
        receipt = read(source)
        wanted = "PASS_NEW_COHORT249_ALL_" + ("FIVE_STAGE" if count == 5 else "BRIDGED_STAGE") + "_FORMAL_COLUMNS_AND_PREFIX_BILL"
        require(receipt["status"] == wanted and len(receipt["stages"]) == count, "formal column status")
        require(all(x["rejected"] for x in receipt["negative_controls"]), "omitted bridge control")
        require(int(receipt["payload_prefix_upper"]) < (1 << 104), "payload prefix bound")
        for key in ("local_scalar_additions", "local_raw_H", "signed_lift_prefix", "payload_prefix_bits", "payload_prefix_upper"):
            require(receipt[key] == five[key], "stage-independent local invoice: " + key)
        stages[label] = {key: receipt[key] for key in ("formal_columns_checked", "bridge_additions")}
        stages[label]["omitted_bridge_controls_rejected"] = len(receipt["negative_controls"])
    return {
        "word_content_sha256": content_sha(word),
        "local_columns": 720,
        "interface": json.loads((directory / "interface.json").read_text()),
        "legality": {key: legality[key] for key in
                     ("records", "common_frame_ADDs", "nested_MOVEs", "copies", "erasures", "rank_mass", "paid_histogram")},
        "local_invoice": {key: five[key] for key in
                          ("local_scalar_additions", "local_raw_H", "signed_lift_prefix", "payload_prefix_bits", "payload_prefix_upper")},
        "stages": stages,
        "negative_controls": {"word_generic": 6, "word_mutable_source": 5, "interface": 2,
                              "record_generic": 6, "record_mutable_source": 3},
        "gram_frames": 672,
        "gram_prime_witnesses": [2],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True, type=Path, help="new output directory outside this package")
    args = parser.parse_args()
    require(not sys.flags.optimize, "run without Python -O; inherited checks use assertions")
    work = args.work.resolve()
    require(work != HERE and HERE not in work.parents and work != PARENT and PARENT not in work.parents,
            "work directory must be outside this package and inherited sources")
    require(not work.exists() or not any(work.iterdir()), "work directory must be absent or empty")
    pinned_parent()
    work.mkdir(parents=True, exist_ok=True)
    replay = Replay(work)
    replay.py("primary-verifier", HERE / "verify.py", "--out", work / "constructed")
    replay.compile()
    observed = {"status": "PASS_R480_QUAD_SEED1_NATIVE_LOCAL_REPLAY",
                "inherited_manifest_sha256": PARENT_MANIFEST_SHA256,
                "baseline": replay.case("baseline", SOURCE),
                "candidate": replay.case("candidate", work / "constructed/word.json.gz")}
    (work / "NATIVE-RESULT.json").write_text(json.dumps(observed, indent=2, sort_keys=True) + "\n")
    expected = json.loads((HERE / "NATIVE-EXPECTED.json").read_text())
    require(observed == expected, "semantic native receipt differs from NATIVE-EXPECTED.json")
    version = replay.run("compiler-version", replay.cxx + ["--version"])
    boost_header = replay.boost / "boost/version.hpp"
    boost_version = re.search(r'^#define BOOST_LIB_VERSION "([^"]+)"', boost_header.read_text(), re.M)
    validation = {"status": observed["status"], "python": platform.python_version(),
                  "compiler": version.strip(), "boost_version": boost_version.group(1) if boost_version else None,
                  "boost_version_header_sha256": sha(boost_header),
                  "native_expected_sha256": sha(HERE / "NATIVE-EXPECTED.json"),
                  "inherited_manifest_sha256": PARENT_MANIFEST_SHA256,
                  "commands": replay.commands,
                  "scope": "Local finite/native replay only; no global hosting replay or exponent improvement."}
    (work / "VALIDATION.json").write_text(json.dumps(validation, indent=2) + "\n")
    print(observed["status"] + " ADDs=33958->33946 prefix_bits=102 unchanged_paid_profile")


if __name__ == "__main__":
    main()
