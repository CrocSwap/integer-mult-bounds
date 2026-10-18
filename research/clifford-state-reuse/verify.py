"""Opt-in source-bound Clifford phase replay; retained sources stay unchanged."""
import argparse
import datetime
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time

PREFIX = "research/complex-k492-owner-repair/vendor/multicold"
COMPILER = PREFIX + "/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py"
DRIVER = PREFIX + "/vendor/pr558/code/phases_full.py"
PORTABLE = PREFIX + "/code/run_portable.py"
PINS = {
    COMPILER: "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
    DRIVER: "a273c325ffd6793d5b63b79a289a9d2bbc9292e6940fb5a926924f3708627af4",
    PORTABLE: "322d29d43dbee8130cde15d4bf05396698b5e3dfe3735813899db91cc0ba7955",
}
CANDIDATE_SHA = "6fac2848d3a0c0dfa92f83c8636beb903083cce1b01bda8ef582514071429221"
WORD_GZIP_SHA = "387a2266ffe006d20042221d967f67a4b18d9bb8de1cd1e01d4031b539fa74a5"
WORD_RAW_SHA = "24db880b7dab31e6af4eec8a1aba1bbbae29cd50d9a7b77cf0e9b571b3e5ae7c"
RECIPE_SHA = "4629507dcbdd516457c001ff8f9dbe750d1a0cbfa5cfa3c6be003d45804ba0c5"
SEMANTIC_SHA = "c7f1b612c720904448d2112721d56bd130ed393ae460a7b30a8a5852c76646e6"
OLD = b"assert out.zero_state()==op.zero_state()"
NEW = b"assert out.zero_state()==(vec,den)"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sources(root):
    result = {p: (root / p).read_bytes() for p in PINS}
    for p, data in result.items():
        require(digest(data) == PINS[p], "Source pin mismatch: " + p)
    return result


def transform(data):
    require(digest(data) == PINS[COMPILER], "Compiler source pin mismatch")
    require(data.count(OLD) == 1, "Expected exactly one assertion operand")
    candidate = data.replace(OLD, NEW, 1)
    require(digest(candidate) == CANDIDATE_SHA, "Generated compiler pin mismatch")
    return candidate


def word_bytes(path):
    data = path.read_bytes()
    require(digest(data) == WORD_GZIP_SHA, "Canonical gzip pin mismatch")
    raw = gzip.decompress(data)
    require(digest(raw) == WORD_RAW_SHA, "Canonical raw pin mismatch")
    return data, json.loads(raw)


def prepare(root, word, work):
    require(__debug__, "Assertions must remain enabled")
    require(not work.exists(), "Work directory must be fresh")
    require(not work.is_relative_to(root), "Work directory must be outside this checkout")
    src = sources(root)
    data, canonical = word_bytes(word)
    candidate = transform(src[COMPILER])
    work.mkdir(parents=True)
    for variant, code in [("baseline", src[COMPILER]), ("candidate", candidate)]:
        directory = work / "compilers" / variant
        directory.mkdir(parents=True)
        (directory / "clifford_exact.py").write_bytes(code)
    driver = work / "driver"
    driver.mkdir()
    (driver / "phases_full.py").write_bytes(src[DRIVER])
    (driver / "run_portable.py").write_bytes(src[PORTABLE])
    write_json(work / "SOURCE-BINDING.json", {
        "source_pins": PINS, "candidate_sha256": CANDIDATE_SHA,
        "input_gzip_sha256": digest(data), "input_raw_sha256": WORD_RAW_SHA,
        "source_base": "8bddbee377e2f3ce1f1247196c4b290d55767d20",
        "transformation": "One monomial final assertion right operand; all guards retained",
    })
    return data, canonical


def load_compiler(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check_generated(work):
    expected = {
        "compilers/baseline/clifford_exact.py": PINS[COMPILER],
        "compilers/candidate/clifford_exact.py": CANDIDATE_SHA,
        "driver/phases_full.py": PINS[DRIVER],
        "driver/run_portable.py": PINS[PORTABLE],
    }
    for path, sha in expected.items():
        require(digest((work / path).read_bytes()) == sha, "Generated source pin mismatch: " + path)


def semantic_preflight(work, start, hard_seconds):
    original = Path(__file__).resolve().with_name("semantic_controls.py")
    raw = original.read_bytes()
    require(digest(raw) == SEMANTIC_SHA, "Independent control source pin mismatch")
    script = work / "driver/semantic_controls.py"
    script.write_bytes(raw)
    receipt = work / "SEMANTIC-CONTROLS.json"
    argv = [sys.executable, "-I", "-B", str(script), "--baseline",
            str(work / "compilers/baseline/clifford_exact.py"), "--candidate",
            str(work / "compilers/candidate/clifford_exact.py"), "--out", str(receipt)]
    remaining = hard_seconds - (time.monotonic() - start)
    require(remaining > 0, "Budget exhausted before independent controls")
    entry = {"argv": argv, "script_sha256": SEMANTIC_SHA, "status": "INCOMPLETE"}
    tick = time.monotonic()
    try:
        command = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 timeout=min(120, remaining))
        (work / "semantic.log").write_bytes(command.stdout)
        entry.update(exit_code=command.returncode, log_sha256=digest(command.stdout))
        require(command.returncode == 0, "Independent semantic controls failed")
        checked = json.loads(receipt.read_bytes())
        require(checked["status"] == "PASS_INDEPENDENT_CLIFFORD_STATE_REUSE_CONTROLS",
                "Incomplete independent semantic receipt")
        require(checked["baseline_sha256"] == PINS[COMPILER]
                and checked["candidate_sha256"] == CANDIDATE_SHA
                and checked["script_sha256"] == SEMANTIC_SHA, "Independent control binding mismatch")
        require(checked["fixture_cases"] == 107 and checked["basis_columns_per_input"] == 552,
                "Independent fixture coverage incomplete")
        controls = checked["monomial_guard_controls"]
        require(len(controls) == 12 and sum(c["rejected"] for c in controls) == 6,
                "Independent mathematical controls incomplete")
        require(len(checked["separate_cli_guards"]) == 3
                and all(c["rejected"] for c in checked["separate_cli_guards"]),
                "Independent CLI controls incomplete")
        require(original.read_bytes() == raw and script.read_bytes() == raw,
                "Independent control source changed")
        check_generated(work)
        require(time.monotonic() - start < hard_seconds,
                "Budget exhausted during independent controls")
        entry.update(status="PASS", receipt_sha256=digest(receipt.read_bytes()))
    except subprocess.TimeoutExpired as error:
        log = error.stdout or b""
        (work / "semantic.log").write_bytes(log)
        entry.update(status="ALLOCATED_HARD_TIMEOUT", log_sha256=digest(log))
        raise ValueError("Independent semantic controls timed out") from error
    except Exception as error:
        entry.update(status="FAILED_OR_INCOMPLETE", error=str(error))
        raise
    finally:
        entry["elapsed_seconds"] = time.monotonic() - tick
        write_json(work / "SEMANTIC-RUN.json", entry)
    return entry


def replay(root, word, work, rounds, hard_seconds):
    start = time.monotonic()
    data, unused = prepare(root, word, work)
    records = []
    result = {"status": "INCOMPLETE", "scope": "Supplementary complete U8 local phase replay only",
              "python": sys.version, "executable": sys.executable, "rounds": rounds,
              "jobs": records, "source_pins": PINS, "candidate_sha256": CANDIDATE_SHA}
    try:
        require(time.monotonic() - start < hard_seconds, "Budget exhausted during preparation")
        result["independent_semantic_controls"] = semantic_preflight(work, start, hard_seconds)
        for round_id in range(rounds):
            order = ("baseline", "candidate") if round_id % 2 == 0 else ("candidate", "baseline")
            for variant in order:
                check_generated(work)
                directory = work / (str(round_id) + "-" + variant)
                directory.mkdir()
                (directory / "CANONICAL-WORD.json.gz").write_bytes(data)
                argv = [sys.executable, "-I", "-B", str(work / "driver/run_portable.py"),
                        str(work / "driver/phases_full.py"), str(directory),
                        str(work / "compilers" / variant)]
                remaining = hard_seconds - (time.monotonic() - start)
                require(remaining > 0, "Allocated hard time exhausted")
                entry = {"variant": variant, "round": round_id, "argv": argv,
                         "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
                records.append(entry)
                tick = time.monotonic()
                env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
                try:
                    command = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                             env=env, timeout=remaining)
                except subprocess.TimeoutExpired as error:
                    log = error.stdout or b""
                    (directory / "phase.log").write_bytes(log)
                    entry.update(exit_code=None, status="ALLOCATED_HARD_TIMEOUT", log_sha256=digest(log),
                                 elapsed_seconds=time.monotonic() - tick)
                    raise ValueError("Allocated phase replay timed out") from error
                (directory / "phase.log").write_bytes(command.stdout)
                entry.update(exit_code=command.returncode, elapsed_seconds=time.monotonic() - tick,
                             log_sha256=digest(command.stdout))
                require(command.returncode == 0, "Phase command failed: " + variant)
                raw = (directory / "CLIFFORD-RECIPES.json").read_bytes()
                review_bytes = (directory / "CLIFFORD-REVIEW.json").read_bytes()
                review = json.loads(review_bytes)
                require(digest(raw) == RECIPE_SHA, "Complete recipe bytes differ")
                require(review["status"] == "PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES", "Incomplete review")
                require(review["canonical_word_sha256"] == WORD_GZIP_SHA, "Review input mismatch")
                require(review["recipe_sha256"] == RECIPE_SHA, "Review recipe mismatch")
                require(review["directed_edges"] == 2949 and review["endpoint_adapters"] == 224,
                        "Incomplete edge/adapter coverage")
                require(review["all_child_equalities_include_global_phase"] is True, "Phase coverage missing")
                semantic = {k: v for k, v in review.items() if k != "seconds"}
                if records[0].get("semantic_review") is not None:
                    require(semantic == records[0]["semantic_review"], "Proof-relevant review fields differ")
                entry.update(recipe_sha256=digest(raw), review_sha256=digest(review_bytes),
                             semantic_review=semantic, phase_seconds=review["seconds"])
                check_generated(work)
                sources(root)
                require(word.read_bytes() == data, "Original input changed")
                print("PASS phase round", round_id, variant, review["seconds"], flush=True)
        baseline = [r["phase_seconds"] for r in records if r["variant"] == "baseline"]
        candidate = [r["phase_seconds"] for r in records if r["variant"] == "candidate"]
        require(time.monotonic() - start < hard_seconds, "Budget exhausted during final checks")
        result.update(status="PASS_EXACT_SOURCE_BOUND_PHASE_REUSE",
                      baseline_seconds=baseline, candidate_seconds=candidate,
                      measured_timing_ranges_disjoint=rounds >= 3 and max(candidate) < min(baseline),
                      median_speed_ratio=statistics.median(baseline) / statistics.median(candidate),
                      all_complete_recipe_bytes_equal=True, default_frontier_checker_changed=False,
                      kappa_changed=False)
    except Exception as error:
        result.update(status="FAILED_OR_INCOMPLETE", error=str(error))
        raise
    finally:
        result["elapsed_seconds"] = time.monotonic() - start
        write_json(work / "RESULT.json", result)
    print(result["status"], flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--word", type=Path, default=Path(__file__).resolve().parent / "data/CANONICAL-WORD.json.gz")
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--hard-seconds", type=int, default=3600)
    args = parser.parse_args()
    require(__debug__, "Assertions must remain enabled")
    require(1 <= args.rounds <= 3, "Rounds must be 1 through 3")
    require(0 < args.hard_seconds <= 3600, "Hard time must be 1 through 3600 seconds")
    replay(args.root.resolve(), args.word.resolve(), args.work.resolve(), args.rounds, args.hard_seconds)


if __name__ == "__main__":
    main()
