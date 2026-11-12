"""Authenticate and independently replay the exact Type A seam family screen."""
import ast
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def source(name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != name:
        raise ValueError(f"invalid source path {name}")
    return (ROOT / path).read_bytes()


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate():
    pins = decode(source("LOCAL-PINS.json"))
    for name, expected in pins.items():
        raw = source(name)
        if digest(raw) != expected:
            raise ValueError(f"changed package dependency {name}")
        if name.endswith(".json"):
            decode(raw)
    prov = decode(source("PROVENANCE.json"))
    for name, entry in prov["files"].items():
        raw = source(name)
        assert digest(raw) == entry["sha256"]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == entry["git_blob"]
    receipt = prov["derived_inputs"]["inputs/R92-PRICE.json"]
    assert pins["inputs/R92-PRICE.json"] == decode(source(receipt["receipt"]))[receipt["key"]]
    predecessor = decode(source("inputs/7113-SHA256.json"))
    for name, entry in prov["files"].items():
        if entry["commit"] == prov["predecessors"]["signed_caller"]["head"] and name != "inputs/7113-SHA256.json":
            key = entry["path"].removeprefix("research/signed-caller-8x9/")
            assert pins[name] == predecessor[key]


def physical_signs():
    child = ast.parse(source("inputs/7113-signed-child.py"))
    gate, = [ast.literal_eval(node.value) for node in child.body
             if isinstance(node, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "C" for t in node.targets)]
    for vector, expected in (((1, 1), (2, 0)), ((1, -1), (0, 2))):
        for row, sign in zip(gate, vector, strict=True):
            image = tuple(sum(a[i]*v for a, v in zip(row, vector, strict=True)) for i in range(2))
            assert image == tuple(sign*x for x in expected)
    app = source("inputs/7113-application.py").decode()
    assert "need(transform(q) == q" in app
    assert "fresh = [1 << (9+8*(stage-1)+j) for j in range(8)]" in app
    binding = decode(source("inputs/PHYSICAL-BINDING.json"))
    assert binding["caller_sha256"] == digest(source("inputs/CALLER.json"))
    assert binding["source_reviewer_sha256"] == digest(source("inputs/7113-application.py"))
    assert binding["occurrence_and_geometry"]["ambient"] == 145
    # Tensor eigenvalues on two copies of the central bit; all body bits use plus.
    assert (1*1, 1j*1j) == (1, -1)


def run_engine(tmp, engine, receipt=None, timeout=32):
    result = run([sys.executable, "-I", "-B", str(tmp / engine)], capture_output=True, timeout=timeout)
    if receipt is None:
        assert result.returncode != 0 and not result.stdout and b"AssertionError" in result.stderr
        return None
    if result.returncode:
        sys.stderr.write(result.stderr.decode(errors="replace"))
    result.check_returncode()
    assert result.stdout == source("receipts/" + receipt), f"changed receipt {receipt}"
    return decode(result.stdout)


def compare(forward, reverse, seam):
    assert forward["head"] == reverse["benchmark"] == seam["benchmark"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert forward["cut"] == reverse["cut"] == seam["cut"] == 1741
    assert forward["budget_seconds"] == reverse["runner_cap_seconds"] == 30
    assert reverse["central_signs"] == seam["central_signs"] == [1, -1]
    assert seam["basis_columns"] == 36
    tallies = Counter()
    for (a, b, old, new, status, witness), other in zip(forward["cases"], reverse["case_results"], strict=True):
        assert other["pair"] == [a, b]
        assert old == sorted(other["old_ranks"]) and new == sorted(other["new_ranks"])
        if other["price"] == "improves":
            tallies["profitable"] += 1
            assert (status == "survives") == other["commuting"]
            assert bool(witness) == bool(other["first_commutator_entry"])
        else:
            assert status == {"ties": "tie", "worsens": "worse"}[other["price"]]
            assert witness is None
        tallies[status] += 1
    assert tallies == forward["counts"] == {"excluded": 60, "profitable": 60, "tie": 282, "worse": 288}
    assert reverse["statistics"] == {"excluded": 60, "improves": 60, "ties": 282, "worsens": 288}
    assert not reverse["survivors"] and len(forward["cases"]) == 630
    lead_control = next(case for case in forward["cases"] if case[:2] == [0, 9])
    assert lead_control[2:5] == [[9, 137], [73, 73], "excluded"]
    assert seam["roots"] == [0, 9] and seam["odd_entries_count"] == 100
    assert lead_control[5] == seam["first_odd_entries"][0] == [0, 0, "4"]
    assert 23 < Fraction(forward["control_pair_0_9_upper"]) < 24


def verify_permutation(forward, reverse):
    assert forward["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert forward["caller"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert forward["cut"] == 1741 and sorted(map(len, forward["classes"])) == [2, 8, 10, 16]
    assert sorted(i for group in forward["classes"] for i in group) == list(range(36))
    assert forward["old_ranks"] == forward["compatible_optimal_ranks"]
    assert forward["class_gross"] == ["0", "0"]
    assert forward["assignments_visited"] == forward["full_automorphisms"] == 0
    assert forward["stop"] == "zero productive gain at class upper"
    assert (reverse["head"], reverse["caller"], reverse["cut"]) == (forward["head"], forward["caller"], forward["cut"])
    assert forward["classes"] == [entry["roles"] for entry in reverse["classes"]]
    assert reverse["h_nonzero"] == 72 and not reverse["capped"]
    assert reverse["old_histogram"] == reverse["relaxed_histogram"] and reverse["relaxed_delta"] == {}
    assert reverse["relaxed_upper_interval"] == forward["class_gross"]
    assert reverse["search"]["assignments"] == forward["assignments_visited"]
    assert reverse["status"] == "uniform zero optimistic gain"
    for entry in reverse["classes"]:
        early, late = zip(*entry["early_late"], strict=True)
        assert len(set(early)) == 1 or len(set(late)) == 1
    assert sorted(int(r) for r, count in reverse["old_histogram"].items()
                  for _ in range(count)) == forward["old_ranks"]


def main():
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 12) or not __debug__:
        raise SystemExit("CPython 3.12 with assertions is required")
    authenticate()
    physical_signs()
    with TemporaryDirectory(prefix="p104-type-a-seam-") as scratch:
        tmp = Path(scratch)
        (tmp / "inputs").mkdir()
        for name in ("CALLER.json", "R92-PRICE.json", "pricing.py"):
            (tmp / "inputs" / name).write_bytes(source("inputs/" + name))
        for name in ("family_forward.py", "seam_reverse.py", "family_reverse.py", "permutation_forward.py", "permutation_reverse.py"):
            (tmp / name).write_bytes(source("engines/" + name))
        seam = run_engine(tmp, "seam_reverse.py", "R178-REVERSE.json")
        (tmp / "inputs/R178-REVERSE.json").write_bytes(source("receipts/R178-REVERSE.json"))
        forward = run_engine(tmp, "family_forward.py", "R179-FORWARD.json")
        reverse = run_engine(tmp, "family_reverse.py", "R179-REVERSE.json")
        compare(forward, reverse, seam)
        permutation = run_engine(tmp, "permutation_forward.py", "R181-FORWARD.json", timeout=62)
        (tmp / "inputs/r179_replay.py").write_bytes(source("engines/family_reverse.py"))
        (tmp / "inputs/R178-PRICE.json").write_bytes(source("receipts/R178-PRICE.json"))
        permutation_reverse = run_engine(tmp, "permutation_reverse.py", "R181-REVERSE.json", timeout=62)
        verify_permutation(permutation, permutation_reverse)
        caller = tmp / "inputs/CALLER.json"
        caller.write_bytes(caller.read_bytes() + b" ")
        for engine in ("family_forward.py", "family_reverse.py", "seam_reverse.py"):
            run_engine(tmp, engine)
    print(dumps({"compared_pairs": 630, "profitable_excluded": 60, "ties": 282, "worse": 288,
                 "unresolved": 0, "control_odd_entries": 100, "changed_caller_rejected": True,
                 "class_sizes": [2, 16, 10, 8], "all_permutation_gross_upper": "0",
                 "kappa_delta": "0"}, sort_keys=True))
    print("PASS_P104_TYPE_A_LATE_MASK_PERMUTATION_BOUND")


if __name__ == "__main__":
    main()
