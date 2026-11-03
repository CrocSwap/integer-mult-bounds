"""Execute the changed lane in the credited caller. Produced by Nick Petalas."""
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from packing import child_bits, residue_lane


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def authenticated_caller():
    repository = ROOT.parent.parent
    sources = json.loads((ROOT / "SOURCES.json").read_text())
    check(len(sources["files"]) <= 32, "source inventory capacity")
    check(sum(row["usage"] == "input" for row in sources["files"]) == 8, "input count")
    for row in sources["files"]:
        if row["usage"] == "input":
            path = repository / row["path"]
            with path.open("rb") as stream:
                raw = stream.read(1024 * 1024 + 1)
            check(len(raw) <= 1024 * 1024, "source capacity")
            check(sha256(raw).hexdigest() == row["sha256"], "source hash " + row["path"])
    path = repository / "research/modular-gaussian-recovery/hybrid.py"
    spec = importlib.util.spec_from_file_location("centered_residue_source_caller", path)
    check(spec is not None and spec.loader is not None, "source loader")
    caller = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(caller)
    return caller


def schoolbook(left, right):
    result = [0] * (len(left) + len(right) - 1)
    for j, x in enumerate(left):
        for i, y in enumerate(right):
            result[i + j] += x * y
    return result


def run_case(caller, lines, n):
    length = (n + 63) // 64
    top = n - 64 * (length - 1)
    # Leading coefficient attains the new sharp magnitude-bit bound.
    left = 1 << (64 * (length - 1) + min(top, 28) - 1)
    # Populate all lower signed slots, including negative representatives.
    right = (1 << n) - 1
    answer, trace = caller.multiply(left, right, lines, 64, 28, input_bits=n)
    check(answer == left * right, "changed complete Gaussian product")
    radix = 1 << 64
    a = [(left >> (j * 64)) % radix for j in range(length)]
    b = [(right >> (j * 64)) % radix for j in range(length)]
    expected = schoolbook(a, b)
    check(trace["coefficients"] == expected + [0] * (455 - len(expected)), "recovered coefficients")
    lane = trace["exact_lane"]
    check(lane["left_child_bits"] == child_bits(n, 64, 28), "new attained child bound")
    check(lane["slot_bits"] == 55 + (length - 1).bit_length(), "new source adapter reached")
    check(lane["exact_child_calls"] == 1 and lane["strictly_smaller_child_bound"], "paid strict child")
    check(Fraction(*trace["uniform_radius"]) < 1 << 27, "inherited modular precision")
    check(trace["precision"] == 180, "new uniform-tail precision")
    return {"parent_bits": n, "sharp_child_bits": child_bits(n, 64, 28),
            "actual_child_bits": [lane["left_child_bits"], lane["right_child_bits"]],
            "slot_bits": lane["slot_bits"], "recovered_coefficients": len(trace["coefficients"]),
            "gaussian_line_executions": trace["gaussian_line_executions"],
            "precision": trace["precision"], "uniform_radius": trace["uniform_radius"]}


def main():
    caller = authenticated_caller()
    seeds = caller.seed_lines()
    lines = caller.precision_view(seeds, 180)
    original_lane = caller.residue_lane
    # The source module is private to this process. Its caller, certificates,
    # transforms, CRT order and carry scan are unchanged. Restore the sole
    # substituted dependency even if an endpoint check raises.
    caller.residue_lane = residue_lane
    try:
        cases = [run_case(caller, lines, n) for n in (8193, 14592)]
    finally:
        caller.residue_lane = original_lane
    check(caller.residue_lane is original_lane, "restored source dependency")
    result = {"status": "PASS_CENTERED_GAUSSIAN_BOUNDARY", "cases": cases}
    files = sorted(p for p in ROOT.iterdir() if p.is_file())
    check(len(files) == 8, "package file count")
    result["sha256"] = {}
    for path in files:
        with path.open("rb") as stream:
            raw = stream.read(1024 * 1024 + 1)
        check(len(raw) <= 1024 * 1024, "receipt file capacity")
        result["sha256"][path.name] = sha256(raw).hexdigest()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
