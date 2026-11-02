"""Exact conformance and full-CLI controls for the integer Taylor adapter."""

import ast
from fractions import Fraction
from hashlib import sha256
import json
from math import factorial
from pathlib import Path
import runpy
import statistics
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ADAPTER = runpy.run_path(str(HERE / "replay.py"))
integer_exp = ADAPTER["exp_interval"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def direct_interval(x: Fraction, degree: int) -> tuple[Fraction, Fraction]:
    lower = sum((x ** k / factorial(k) for k in range(degree + 1)), Fraction())
    next_term = x ** (degree + 1) / factorial(degree + 1)
    return lower, lower + next_term / (1 - x / (degree + 2))


def polynomial_cases() -> int:
    cases = 0
    for denominator in range(1, 42):
        for numerator in range(denominator // 4 + 1):
            x = Fraction(numerator, denominator)
            for degree in (1, 2, 3, 8, 24, 64):
                require(integer_exp(x, degree) == direct_interval(x, degree),
                        "direct finite-polynomial/tail oracle")
                cases += 1
    for bits in (53, 127, 521):
        x = Fraction((1 << (bits - 3)) + 1, (1 << bits) + 1)
        require(integer_exp(x) == direct_interval(x, 24), "large rational oracle")
        cases += 1
    return cases


def traced_run(arm: str) -> tuple[dict, list[Fraction]]:
    namespace, _ = ADAPTER["load_primary"]()
    original = namespace["exp_positive"]
    arguments = []

    def tracked(x):
        require(len(arguments) < 80, "bounded complete-call trace")
        require(type(x) is Fraction, "source rational argument boundary")
        arguments.append(x)
        return original(x) if arm == "original" else integer_exp(x)

    namespace["exp_positive"] = tracked
    return namespace["run"](), arguments


def complete_conformance() -> dict:
    original, old_arguments = traced_run("original")
    candidate, new_arguments = traced_run("integer")
    require(original == candidate, "complete primary result equality")
    require(old_arguments == new_arguments and len(old_arguments) == 72,
            "complete ordered exponential-call trace")
    raw = (json.dumps(candidate, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    require(raw == (HERE / "source/RELATIVE-RESULT.json").read_bytes(),
            "complete retained result byte equality")
    for x in old_arguments:
        require(integer_exp(x) == direct_interval(x, 24), "every reached source interval")
    for arm in ("original", "integer"):
        optimization = ["-O"] if sys.flags.optimize else []
        result = subprocess.run(
            [sys.executable, "-I", "-W", "error", *optimization, "-B", str(HERE / "replay.py"),
             "--arm", arm], capture_output=True, timeout=30, check=False)
        require(result.returncode == 0 and not result.stderr and result.stdout ==
                b"PASS exact relative tariff threshold and retained receipt\n",
                "unchanged complete primary CLI, including receipt checks")
    return {"complete_result_sha256": sha256(raw).hexdigest(),
            "source_exp_calls": len(old_arguments),
            "source_taylor_iterations": 24 * len(old_arguments),
            "max_argument_denominator_bits": max(x.denominator.bit_length() for x in old_arguments),
            "retained_source_controls": sorted(candidate["controls"])}


def rejects(action) -> None:
    try:
        action()
    except ValueError:
        return
    raise ValueError("negative control accepted")


def negative_controls() -> int:
    for x in (Fraction(-1, 8), Fraction(1, 3), 0.1, 0):
        rejects(lambda: integer_exp(x))
    for degree in (0, 65, True):
        rejects(lambda: integer_exp(Fraction(1, 8), degree))
    rejects(lambda: integer_exp(Fraction(1, (1 << 4096) + 1)))
    x = Fraction(1, 4)
    correct = direct_interval(x, 24)
    rejects(lambda: require((correct[0], correct[0]) == correct, "omitted tail"))
    rejects(lambda: require((correct[0] + Fraction(1, 10**40), correct[1]) == correct,
                            "premature outward rounding"))
    raw = (HERE / "ORIGINS.json").read_bytes()
    check = ADAPTER["check_payload"]
    rejects(lambda: check(raw + b" ", ADAPTER["ORIGINS_SHA256"], 32768, "manifest"))
    rejects(lambda: check(raw, ADAPTER["ORIGINS_SHA256"], len(raw) - 1, "limit"))
    source = (HERE / "source/verify_tariff.py").read_bytes()
    rejects(lambda: check(source + b"\n", ADAPTER["SOURCE_SHA256"], 4194304, "source"))
    rejects(lambda: ADAPTER["replay"]("unknown"))
    return 14


def benchmark_receipt() -> dict:
    raw = (HERE / "BENCHMARK.json").read_bytes()
    require(len(raw) < 65536, "bounded benchmark receipt")
    report = json.loads(raw)
    require(report["schema_version"] == 1 and 5 <= report["pairs"] <= 15,
            "benchmark schema and repetitions")
    origin = json.loads(ADAPTER["checked_bytes"](
        HERE / "ORIGINS.json", ADAPTER["ORIGINS_SHA256"], 32768))
    expected_names = {"benchmark.py", "exp_series.py", "replay.py", "ORIGINS.json"}
    expected_names.update("source/" + row["path"] for row in origin["files"])
    require(set(report["inputs"]) == expected_names, "complete benchmark input inventory")
    for name, digest in report["inputs"].items():
        require(sha256((HERE / name).read_bytes()).hexdigest() == digest,
                "benchmark source binding: " + name)
    expected = sha256(b"PASS exact relative tariff threshold and retained receipt\n").hexdigest()
    require(len(report["samples"]) == 2 * report["pairs"] and report["failures"] == 0,
            "all complete benchmark samples succeeded")
    for index, row in enumerate(report["samples"]):
        require(row["arm"] == ("original", "integer")[index % 2] and
                row["nanoseconds"] > 0 and row["exit_code"] == row["stderr_bytes"] == 0 and
                row["stdout_sha256"] == expected, "alternating valid sample")
    for arm in ("original", "integer"):
        times = [row["nanoseconds"] for row in report["samples"] if row["arm"] == arm]
        require(report["summary"][arm] == {"median_ns": statistics.median(times),
                "min_ns": min(times), "max_ns": max(times)}, "recomputed timing summary")
    saving = 1 - report["summary"]["integer"]["median_ns"] / report["summary"]["original"]["median_ns"]
    require(report["reduction_fraction"] == saving and saving > 0, "recorded measured improvement")
    return {"pairs": report["pairs"], "source_bound_inputs": len(report["inputs"])}


def main() -> None:
    for name in ("exp_series.py", "replay.py", "verify.py", "benchmark.py"):
        ast.parse((HERE / name).read_bytes(), filename=name)
    report = {"status": "PASS_RELATIVE_TARIFF_INTEGER_EXP",
              "polynomial_cases": polynomial_cases(), "complete": complete_conformance(),
              "negative_controls": negative_controls(), "benchmark": benchmark_receipt()}
    report["package_code_sha256"] = {
        name: sha256((HERE / name).read_bytes()).hexdigest()
        for name in ("exp_series.py", "replay.py", "verify.py", "benchmark.py")}
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
