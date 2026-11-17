#!/usr/bin/env python3
"""Check the new four-cycle endpoint; write only to temporary storage."""

import argparse
from collections import deque
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/restored-cycle-gap/"
MAX_BALL_BYTES = 9 * sum(66**depth for depth in range(5))
WORD = (
    (0, 1, 1), (1, 0, -1), (0, 1, 1), (1, 1, -1),
    (3, 2, -1), (1, 3, -1), (2, 3, 1),
    (3, 1, 1), (1, 3, -1), (1, 2, 1),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    require(path.is_file() and not path.is_symlink(), "regular file required")
    require(path.stat().st_size <= 1024 * 1024, "source exceeds 1 MiB")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate_sources():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    expected = {
        SOURCE + "README.md", SOURCE + "ternary.cpp", SOURCE + "packed.cpp",
        "research/complex-restored-borrowed-boundaries/PROOF.md",
    }
    rows = [row for row in sources["files"] if row["usage"] == "input"]
    require(len(rows) == len(expected), "unexpected source inventory")
    require({row["path"] for row in rows} == expected, "source paths differ")
    hashes = {}
    for row in rows:
        digest = sha256(ROOT / row["path"])
        require(digest == row["sha256"], "source hash mismatch: " + row["path"])
        hashes[row["path"]] = digest
    return hashes


def dense_change(matrix, n, target, source, sign):
    result = list(matrix)
    for column in range(n):
        offset = target * n + column
        value = matrix[offset]
        result[offset] = ((-value) if target == source else
                          value + sign * matrix[source * n + column]) % 3
    return tuple(result)


def dense_control_ball():
    n = 2
    identity = (1, 0, 0, 1)
    distance = {identity: 0}
    queue = deque([identity])
    # At most 3^4 matrices, with six generators and radius four.
    for _ in range(3**4):
        if not queue:
            break
        matrix = queue.popleft()
        if distance[matrix] == 4:
            continue
        for target in range(n):
            for source in range(n):
                for sign in (-1, 1):
                    if target == source and sign == 1:
                        continue
                    next_matrix = dense_change(matrix, n, target, source, sign)
                    if next_matrix not in distance:
                        distance[next_matrix] = distance[matrix] + 1
                        queue.append(next_matrix)
    require(not queue, "control worklist exhausted")
    encoded = {}
    for matrix, depth in distance.items():
        key = sum(value * 3**index for index, value in enumerate(matrix))
        encoded[key] = depth
    return encoded


def rational_map(word):
    rows = [[Fraction(int(i == j)) for j in range(6)] for i in range(6)]
    for target, source, sign in word:
        if target == source:
            rows[target] = [-entry for entry in rows[target]]
        else:
            rows[target] = [left + sign * right
                            for left, right in zip(rows[target], rows[source])]
    return rows


def check_upper_word():
    permutation = (1, 2, 3, 0, 4, 5)
    target = [[Fraction(int(j == permutation[i])) for j in range(6)]
              for i in range(6)]
    require(rational_map(WORD) == target, "ten-step rational endpoint failed")
    for omitted in range(len(WORD)):
        shorter = WORD[:omitted] + WORD[omitted + 1:]
        require(rational_map(shorter) != target, "omission was not detected")
    inverse = tuple((t, s, sign if t == s else -sign)
                    for t, s, sign in reversed(WORD))
    require(rational_map(WORD + inverse) == rational_map(()), "inverse failed")
    return {"length": len(WORD), "independent_input_columns": 6,
            "omissions_rejected": len(WORD), "inverse_checked": True}


def compile_engine(name, directory, compiler):
    executable = directory / name
    command = [compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-Werror",
               str(ROOT / (SOURCE + name + ".cpp")), "-o", str(executable)]
    subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
    return executable


def run_engine(executable, n, permutation, directory, label):
    ball = directory / (label + ".bin")
    report = directory / (label + ".json")
    completed = subprocess.run(
        [str(executable), str(n), permutation, str(ball), str(report)],
        check=True, capture_output=True, text=True, timeout=180,
    )
    require(completed.stdout.startswith("PASS_"), "missing native completion")
    require(report.stat().st_size <= 4096, "oversize native report")
    require(ball.stat().st_size <= MAX_BALL_BYTES, "oversize metric ball")
    return json.loads(report.read_text()), ball


def compare_balls(left, right):
    require(left.stat().st_size == right.stat().st_size, "ball lengths differ")
    digest = hashlib.sha256()
    with left.open("rb") as a, right.open("rb") as b:
        for _ in range(MAX_BALL_BYTES // 65536 + 2):
            first, second = a.read(65536), b.read(65536)
            require(first == second, "native metric balls differ")
            if not first:
                return digest.hexdigest()
            digest.update(first)
    raise ValueError("ball comparison exceeded bound")


def control_runs(executable, directory, oracle):
    for number, (permutation, minimum) in enumerate((('01', 0), ('a1', 1), ('ab', 2))):
        report, ball = run_engine(executable, 2, permutation, directory, "small" + str(number))
        require(report["minimum_through_nine"] == minimum, "control distance differs")
        payload = ball.read_bytes()
        require(len(payload) == 9 * len(oracle), "control cardinality differs")
        entries = list(struct.iter_unpack("<QB", payload))
        require(entries == sorted(oracle.items()), "dense/native balls differ")
    for number, (n, permutation) in enumerate(((1, "0"), (2, "00"))):
        completed = subprocess.run(
            [str(executable), str(n), permutation,
             str(directory / ("invalid" + str(number) + ".bin")),
             str(directory / ("invalid" + str(number) + ".json"))],
            capture_output=True, text=True, timeout=10,
        )
        reason = "dimension 2..6 required" if n == 1 else "permutation"
        require(completed.returncode == 1 and reason in completed.stderr,
                "invalid native domain did not reject for its declared reason")


def validate_report(report):
    require(type(report) is dict, "report must be an object")
    expected = {
        "n": 6, "permutation": "123045", "layers": [1, 66, 2655, 83270, 2213925],
        "states": 2299917, "generators": 66, "transitions": 151794522,
        "direct_hits": 0, "middle_hits": 0, "minimum_through_nine": None,
    }
    require(json.dumps(report, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "new four-cycle certificate differs")
    require(report["transitions"] == report["states"] * report["generators"],
            "middle scan is incomplete")
    return report


def reject_report_mutations(report):
    changes = (("transitions", 0), ("middle_hits", 1), ("direct_hits", 1),
               ("minimum_through_nine", 9), ("n", True), ("permutation", "123405"))
    for key, value in changes:
        damaged = dict(report)
        damaged[key] = value
        try:
            validate_report(damaged)
        except ValueError:
            continue
        raise ValueError("report mutation was accepted")
    return len(changes)


def verify():
    source_hashes = authenticate_sources()
    upper = check_upper_word()
    compiler = shutil.which("c++")
    require(compiler is not None, "C++17 compiler with __int128 is required")
    oracle = dense_control_ball()
    reports, balls = [], []
    with tempfile.TemporaryDirectory(prefix="four-cycle-") as temporary:
        directory = Path(temporary)
        for name in ("ternary", "packed"):
            executable = compile_engine(name, directory, compiler)
            control_runs(executable, directory, oracle)
            report, ball = run_engine(executable, 6, "123045", directory, name + "-target")
            reports.append(validate_report(report))
            balls.append(ball)
        require(reports[0] == reports[1], "native endpoint reports differ")
        ball_hash = compare_balls(balls[0], balls[1])
        require(balls[0].stat().st_size == 9 * reports[0]["states"], "ball size differs")
    files = sorted(PACKAGE.iterdir())
    require(len(files) <= 8 and all(p.is_file() for p in files), "package inventory differs")
    return {
        "status": "PASS_RESTORED_UNSIGNED_FOUR_CYCLE", "scalar_minimum": 10,
        "claim_type": "scoped proof with an exact finite exclusion certificate",
        "finite_exclusion": reports[0], "canonical_ball_sha256": ball_hash,
        "upper_word": upper, "report_mutations_rejected": reject_report_mutations(reports[0]),
        "dense_control_states": len(oracle), "control_endpoints_per_engine": 3,
        "invalid_native_domains_per_engine": 2, "source_sha256": source_hashes,
        "package_sha256": {path.name: sha256(path) for path in files},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="write a new receipt outside the repository")
    args = parser.parse_args()
    if args.emit:
        destination = args.emit.resolve()
        require(not destination.is_relative_to(ROOT), "receipt must be outside repository")
        require(not destination.exists(), "receipt destination already exists")
    result = verify()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.emit:
        with destination.open("x") as stream:
            stream.write(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
