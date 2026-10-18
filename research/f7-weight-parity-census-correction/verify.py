#!/usr/bin/env python3
"""Quick independent controls; --full additionally re-enumerates all six cases.

Nicholas Stone, with substantial OpenAI Codex assistance. Apache-2.0.
No stored receipt is treated as a freshly executed census.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "engine/corrected_census.c"
CASES = {(20, 10, 10), (20, 10, 9), (20, 10, 8), (20, 9, 9),
         (20, 10, 7), (18, 9, 9)}
FIELDS = ("nodes", "candidate_restored_leaves", "hits", "even_budget_prunes",
          "odd_budget_prunes", "aborted", "complete", "all_restored_leaves")


def require(condition, detail):
    if not condition:
        raise RuntimeError(detail)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_case(data, length, s, t):
    require(data["n"] == 7 and data["length"] == length and data["split"] == [s, t], data)
    require(data["groups"] == "hamming_weight_parity", data)
    require(data["even_budget_enabled"] and data["odd_budget_enabled"], data)
    require(data["even_budget"] == s*(s-1)//2+t*(t-1)//2-63, data)
    require(data["odd_budget"] == s*t-64, data)
    require(data["complete"] and not data["aborted"], data)
    require(data["requested_shards"] == data["completed_or_partial_shards"] == 1, data)
    require(len(data["shards"]) == 1 and data["shards"][0]["prefix"] == "", data)
    total = data["total"][0]
    require(total["complete"] and not total["aborted"] and total["hits"] == 0, data)
    require(total["all_restored_leaves"] is None, data)
    return total


def receipts():
    manifest = read(HERE / "engine/SUMMARIES.json")
    require(sha(SOURCE) == manifest["source_sha256"], "C source differs from recorded receipt")
    require(len(manifest["results"]) == len(CASES), "Missing or duplicate production case")
    expected = {}
    for record in manifest["results"]:
        name = record["case"].split("_")
        length, s, t = int(name[1][1:]), int(name[2]), int(name[3])
        key = length, s, t
        require(key in CASES and key not in expected, record)
        path = HERE / "engine" / record["result_file"]
        hits = HERE / "engine" / record["hits_file"]
        require(sha(path) == record["result_sha256"] and sha(hits) == record["hits_sha256"], record)
        require(record["process_exit_code"] == 0 and hits.read_bytes() == b"", record)
        total = check_case(read(path), length, s, t)
        require(all(total[field] == record[field] for field in FIELDS), record)
        expected[key] = total
    require(set(expected) == CASES, "Production cases do not cover stated domain")
    return expected


def upper_witness():
    record = read(HERE / "UPPER-WITNESS.json")
    word = tuple(map(int, record["word"]))
    require(len(word) == record["length"] == 24 and record["n"] == 7, record)
    require(all(word.count(j) > 0 and word.count(j) % 2 == 0 for j in range(7)), record)
    q, points = 0, set()
    for label in word:
        require(0 <= label < 7, word)
        points.add(q)
        q ^= 1 << label
    require(q == 0 and len({a ^ b for a in points for b in points}) == 128, record)


def python_script(path, *args):
    # -I keeps inherited PYTHONOPTIMIZE from disabling the mathematical checks.
    # Explicit path insertion permits the validator's local oracle import.
    loader = "import runpy,sys; from pathlib import Path; sys.path.insert(0,str(Path(sys.argv[1]).parent)); p=sys.argv.pop(1); runpy.run_path(p,run_name='__main__')"
    subprocess.run([sys.executable, "-I", "-B", "-c", loader, str(path), *map(str, args)],
                   check=True, timeout=180)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    expected = receipts()
    upper_witness()
    with tempfile.TemporaryDirectory(prefix="f7-parity-replay-") as temporary:
        out = Path(temporary)
        python_script(HERE / "math/check_math.py")
        python_script(HERE / "validation/check_corrected_c.py", "--output-dir", out / "small")
        python_script(HERE / "validation/crosscheck_n7.py", "--output-dir", out / "capped")
        if args.full:
            binaries = {}
            for length in (18, 20):
                binary = out / f"census-{length}"
                subprocess.run(["cc", "-O3", "-Wall", "-Wextra", "-Werror", "-std=c11",
                                "-DN=7", f"-DL={length}", str(SOURCE), "-o", str(binary)], check=True)
                binaries[length] = binary
            for (length, s, t), wanted in sorted(expected.items()):
                key = f"n7_l{length}_{s}_{t}"
                datafile, hitfile = out / (key+".json"), out / (key+".hits")
                subprocess.run([str(binaries[length]), f"{s},{t}", "--hits", str(hitfile),
                                "--json", str(datafile)], check=True, timeout=480)
                actual = check_case(read(datafile), length, s, t)
                require(all(actual[field] == wanted[field] for field in FIELDS), (key, actual, wanted))
                require(hitfile.read_bytes() == b"", (key, "unexpected universal word"))
    if args.full:
        print("PASS_F7_WEIGHT_PARITY_FULL fresh_six_case_census universal_words=0 f7_lower=22 f7_upper=24")
    else:
        print("PASS_F7_WEIGHT_PARITY_QUICK independent_controls_and_stored_receipts_only")


if __name__ == "__main__":
    main()
