"""Regenerate both exact receipts for one Type B odd-rail rank allocation."""
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from shutil import copyfile
from subprocess import PIPE, run
from sys import executable, implementation, version_info
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
STAGES = ("lead", "independent")


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def execute(root, stage):
    return run([executable, "-I", "-B", str(root / "engines" / f"{stage}.py")],
               stdout=PIPE, stderr=PIPE, cwd=root, timeout=25)


def mutated_caller_rejected():
    with TemporaryDirectory(prefix="p104-odd-rail-negative-") as directory:
        root = Path(directory)
        (root / "inputs").mkdir()
        (root / "engines").mkdir()
        copyfile(ROOT / "engines/independent.py", root / "engines/independent.py")
        for name in ("7113-signed-child.py", "7334-RESULT.json"):
            copyfile(ROOT / "inputs" / name, root / "inputs" / name)
        caller = read((ROOT / "inputs/CALLER.json").read_bytes())
        assert caller["events"][1339] == ["B", "IDLE_ODD", 68, [8], -1]
        caller["events"][1339][3][0] = 9
        (root / "inputs/CALLER.json").write_text(dumps(caller))
        result = execute(root, "independent")
        assert result.returncode == 1 and not result.stdout
        assert b"AssertionError: inputs/CALLER.json" in result.stderr


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    pins = read((ROOT / "LOCAL-PINS.json").read_bytes())
    for name, digest in sorted(pins.items()):
        path = (ROOT / name).resolve()
        assert path.is_relative_to(ROOT) and sha256(path.read_bytes()).hexdigest() == digest, name
    signed = read((ROOT / "inputs/7113-SHA256.json").read_bytes())
    assert signed["expected/ODD-TYPE-AB-CALLER.json"] == pins["inputs/CALLER.json"]
    assert signed["replay/supplier7112/short-caller/signed_child.py"] == pins["inputs/7113-signed-child.py"]
    stock = read((ROOT / "inputs/PR7362-SHA256.json").read_bytes())
    assert stock["R92-PRICE.json"] == pins["inputs/R92-PRICE.json"]
    receipts = {}
    for stage in STAGES:
        result = execute(ROOT, stage)
        assert result.returncode == 0, (stage, result.stderr.decode())
        assert result.stdout == (ROOT / "receipts" / f"{stage.upper()}.json").read_bytes(), stage
        receipts[stage] = read(result.stdout)
    lead, independent = (receipts[stage] for stage in STAGES)
    assert lead["ports"] == independent["ports"]
    assert lead["columns"] == independent["columns_checked"] == 4
    assert lead["determinant"] == independent["determinant_required"] == 4
    assert lead["allowed_replacement_difference_rank_upper"] == independent["replacement_difference_rank_upper"] == 1
    assert {r: -v for r, v in lead["rank_histogram_delta"].items()} == independent["paid_delta"]
    assert {r: [j for j, _ in c] for r, c in lead["contacts"].items()} == independent["contacts"]
    lower, upper = map(Fraction, lead["price_at_old_crossing_upper"])
    assert 0 < lower <= upper < Fraction(independent["gross_strict_upper"])
    mutated_caller_rejected()
    print('{"clocks":[1339,2970],"ports":8,"columns":4,"required_rank":2,'
          '"replacement_rank_upper":1,"corrupted_caller_rejected":true,"kappa_delta":"0"}')
    print("PASS_P104_TYPE_B_ODD_RAIL_CONCENTRATION_BOUND")


if __name__ == "__main__":
    main()
