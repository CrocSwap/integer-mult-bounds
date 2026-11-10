#!/usr/bin/env python3
"""Check the new guard implication, taking PR3235's ledger as a premise."""

from fractions import Fraction
from hashlib import sha1, sha256
from itertools import product
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
MAX_BYTES = 2_000_000
FACTOR = Fraction(17, 16)
INPUTS = (
    "research/qq16-producer-defect-transfer/README.md",
    "research/qq16-rounded-producer-envelope/README.md",
    "research/qq16-rounded-producer-envelope/RESULT.json",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_bytes(path: Path) -> bytes:
    require(path.is_file() and not path.is_symlink(), "expected regular file")
    require(path.stat().st_size <= MAX_BYTES, "input exceeds byte limit")
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, "input grew beyond byte limit")
    return data


def authenticate(data: bytes, row: dict) -> None:
    require(sha256(data).hexdigest() == row["sha256"], "source SHA256 mismatch")
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    require(sha1(header + data).hexdigest() == row["git_blob"], "source blob mismatch")


def source_inputs() -> tuple[dict, dict]:
    manifest = json.loads(read_bytes(PACKAGE / "SOURCES.json"))
    require(len(manifest["files"]) == 5, "unexpected source inventory")
    rows = {row["path"]: row for row in manifest["files"] if row["usage"] == "input"}
    require(set(rows) == set(INPUTS), "unexpected live inputs")
    hashes = {}
    ledger = None
    for name in INPUTS:
        data = read_bytes(ROOT / name)
        authenticate(data, rows[name])
        hashes[name] = sha256(data).hexdigest()
        if name.endswith("RESULT.json"):
            ledger = json.loads(data)
    require(ledger is not None, "missing derivative premise")
    return ledger, hashes


def feedback_bound(coefficients: tuple, sites: int, tolerance: Fraction) -> Fraction:
    require(type(sites) is int and 1 <= sites <= 8, "invalid fixture site count")
    require(1 <= len(coefficients) <= sites + 1, "degree exceeds site bound")
    require(all(type(c) is int and c >= 0 for c in coefficients), "negative coefficient")
    require(tolerance >= 0 and sites * tolerance < 1, "invalid feedback tolerance")
    derivative = sum(i * c for i, c in enumerate(coefficients))
    return tolerance * derivative / (1 - sites * tolerance)


def polynomial_controls() -> int:
    count = 0
    for coefficients in product(range(3), repeat=5):
        derivative = sum(i * c for i, c in enumerate(coefficients))
        for tolerance in (Fraction(0), Fraction(1, 68), Fraction(1, 136),
                          Fraction(1, 8), Fraction(1, 5)):
            difference = sum(c * ((1 + tolerance) ** i - 1)
                             for i, c in enumerate(coefficients))
            require(difference <= feedback_bound(coefficients, 4, tolerance),
                    "geometric feedback inequality failed")
            if 4 * tolerance <= Fraction(1, 17):
                require(difference <= FACTOR * tolerance * derivative,
                        "17/16 feedback inequality failed")
            count += 1
    tolerance = Fraction(1, 68)
    require((1 + tolerance) ** 2 - 1 > 2 * tolerance,
            "feedback-omission control did not distinguish the formulas")
    return count


def guard_certificate(ledger: dict, guard: int) -> dict:
    require(type(guard) is int and 1 <= guard <= 102, "invalid guard")
    cases = ledger["cases"]
    jf = Fraction(cases["F_0"]["all_cut"]["J"]["J"])
    jb = Fraction(cases["B_1_2"]["all_cut"]["J"]["J"])
    sites = max(cases[name]["defect_sites"] for name in ("F_0", "B_1_2"))
    require(jf > 0 and jb > 0 and 1 <= sites <= 30_000, "invalid ledger premise")
    require(17 * sites <= 2**guard, "feedback premise failed")
    f_ratio = FACTOR * jf * Fraction(2**8, 2**guard)
    b_ratio = FACTOR * jb * Fraction(2**19, 2**guard)
    require(f_ratio < 1 and b_ratio < 1, "completed-stage allowance exceeded")
    require(Fraction(49, 256) + Fraction(1923, 8192) + Fraction(1, 2)
            == Fraction(7587, 8192) < 1, "decoder transfer inequality failed")
    return {"guard": guard, "feedback_factor": str(FACTOR),
            "inherited_J_F": str(jf), "inherited_J_B": str(jb),
            "inherited_max_sites": sites, "F_allowance_ratio": str(f_ratio),
            "B_allowance_ratio": str(b_ratio), "B_strict_slack": str(1 - b_ratio)}


def parameter_controls(ledger: dict) -> int:
    cases = ledger["cases"]
    jf = Fraction(cases["F_0"]["all_cut"]["J"]["J"])
    jb = Fraction(cases["B_1_2"]["all_cut"]["J"]["J"])
    count = 0
    for beta, delta in product((0, 1, 2, 63, 64, 127), (0, 1, 5, 64)):
        tolerance = Fraction(1, 2 ** (beta + delta + 101))
        eta_f, eta_b = Fraction(1, 2 ** (beta + 8)), Fraction(1, 2 ** (beta + 13))
        require(FACTOR * 2**delta * tolerance * jf < eta_f, "F parameter case failed")
        data_bound, helper_bound = 58 + eta_f, 2**delta + eta_f
        require(max(data_bound, helper_bound) <= 2 ** (delta + 6), "noisy entry failed")
        require(FACTOR * 2 ** (delta + 6) * tolerance * jb < eta_b,
                "B parameter case failed")
        count += 1
    return count


def rejection_controls(ledger: dict) -> int:
    rejected = 0
    try:
        guard_certificate(ledger, 100)
    except ValueError as error:
        require(str(error) == "completed-stage allowance exceeded", "wrong guard rejection")
        rejected += 1
    else:
        raise ValueError("one-stronger fixed certificate unexpectedly passed")
    invalid = (((1, -1), 1, Fraction(0)), ((1, 1, 1), 1, Fraction(0)),
               ((1, 1), 0, Fraction(0)), ((1, 1), 1, Fraction(-1)),
               ((1, 1), 1, Fraction(1)), ((True, 1), 1, Fraction(0)))
    for coefficients, sites, tolerance in invalid:
        try:
            feedback_bound(coefficients, sites, tolerance)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid polynomial fixture accepted")
    manifest = json.loads(read_bytes(PACKAGE / "SOURCES.json"))
    for row in manifest["files"]:
        if row["usage"] == "input":
            try:
                authenticate(read_bytes(ROOT / row["path"]) + b" ", row)
            except ValueError as error:
                require(str(error) == "source SHA256 mismatch", "wrong source rejection")
                rejected += 1
            else:
                raise ValueError("source-byte mutation accepted")
    return rejected


def main() -> None:
    ledger, hashes = source_inputs()
    certificate = guard_certificate(ledger, 101)
    counts = {"polynomial_cases": polynomial_controls(),
              "parameter_cases": parameter_controls(ledger),
              "rejected_controls": rejection_controls(ledger)}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        hashes[f"research/{PACKAGE.name}/{name}"] = sha256(read_bytes(PACKAGE / name)).hexdigest()
    print(json.dumps({"status": "PASS_QQ16_PRODUCER_ONE_BIT_FEEDBACK",
                      "claim_type": "scoped proof conditional on the cited PR3235 ledger",
                      "certificate": certificate, "controls": counts,
                      "file_sha256": hashes}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
