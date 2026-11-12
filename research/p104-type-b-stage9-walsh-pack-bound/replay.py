"""Regenerate both stage-9 Walsh receipts from pinned offline inputs."""
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from shutil import copyfile
from subprocess import PIPE, run
from sys import executable, implementation, version_info
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
STAGES = ("lead", "independent")
MARKER = b"PASS_R180_WIDTH_ONE_WALSH_PRICE_AND_ACTION\n"


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def execute(root, stage):
    return run([executable, "-I", "-B", str(root / "engines" / f"{stage}.py")],
               stdout=PIPE, stderr=PIPE, cwd=root, timeout=35)


def corrupted_caller_control():
    with TemporaryDirectory(prefix="p104-stage9-negative-") as path:
        root = Path(path)
        (root / "inputs").mkdir()
        (root / "engines").mkdir()
        copyfile(ROOT / "engines/independent.py", root / "engines/independent.py")
        for name in ("7113-signed-child.py", "7334-RESULT.json"):
            copyfile(ROOT / "inputs" / name, root / "inputs" / name)
        caller = read((ROOT / "inputs/CALLER.json").read_bytes())
        assert caller["events"][2866] == ["B", "IDLE_ONE", 36, [9]]
        caller["events"][2866][3][0] = 10
        (root / "inputs/CALLER.json").write_text(dumps(caller))
        result = execute(root, "independent")
        assert result.returncode == 1 and not result.stdout
        assert b"AssertionError: inputs/CALLER.json" in result.stderr


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    pins = read((ROOT / "LOCAL-PINS.json").read_bytes())
    for name, pin in sorted(pins.items()):
        file = (ROOT / name).resolve()
        assert file.is_relative_to(ROOT) and sha256(file.read_bytes()).hexdigest() == pin, name
    signed = read((ROOT / "inputs/7113-SHA256.json").read_bytes())
    assert signed["expected/ODD-TYPE-AB-CALLER.json"] == pins["inputs/CALLER.json"]
    assert signed["replay/supplier7112/short-caller/signed_child.py"] == pins["inputs/7113-signed-child.py"]
    stock = read((ROOT / "inputs/PR7362-SHA256.json").read_bytes())
    assert stock["R92-PRICE.json"] == pins["inputs/R92-PRICE.json"]
    receipts = {}
    for stage in STAGES:
        result = execute(ROOT, stage)
        assert result.returncode == 0, (stage, result.stderr.decode())
        actual = result.stdout
        if stage == "independent":
            assert actual.endswith(MARKER)
            actual = actual[:-len(MARKER)]
        expected = (ROOT / "receipts" / f"{stage.upper()}.json").read_bytes()
        assert actual == expected, stage
        receipts[stage] = read(actual)
    lead, independent = (receipts[stage] for stage in STAGES)
    assert lead["clock"] == independent["checked_clock"] == 2866
    assert lead["ports"] == independent["exact_ports"]
    assert lead["counts_f1"] == independent["phases_forward_and_adjoint"]
    assert lead["active_f1"] == independent["displacement_rank"] == 184 > lead["capacity_f1_rank7"]
    assert not lead["build_admitted"] and independent["unresolved_within_width_one"] == 0
    corrupted_caller_control()
    print('{"clock":2866,"ports":8,"basis_columns":256,"displacement_rank":184,"rank7_capacity":128,'
          '"corrupted_caller_rejected":true,"kappa_delta":"0"}')
    print("PASS_P104_TYPE_B_STAGE9_WALSH_PACK_BOUND")


if __name__ == "__main__":
    main()
