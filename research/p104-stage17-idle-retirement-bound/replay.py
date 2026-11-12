"""Replay the exact stage-17 idle retirement and forced-host gates."""
from fractions import Fraction as Q
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
    path = (ROOT / name).resolve()
    assert path.is_relative_to(ROOT) and path.relative_to(ROOT).as_posix() == name
    return path.read_bytes()


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate():
    pins = decode(source("LOCAL-PINS.json"))
    for name, expected in pins.items():
        raw = source(name)
        assert digest(raw) == expected, name
        if name.endswith(".json"):
            decode(raw)
    prov = decode(source("PROVENANCE.json"))
    for name, entry in prov["files"].items():
        raw = source(name)
        assert digest(raw) == entry["sha256"]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == entry["git_blob"]
    price = prov["derived_inputs"]["inputs/R92-PRICE.json"]
    assert decode(source(price["receipt"]))[price["key"]] == pins["inputs/R92-PRICE.json"]
    signed = decode(source("inputs/7113-SHA256.json"))
    for name, key in (("CALLER.json", "expected/ODD-TYPE-AB-CALLER.json"),
                      ("PHYSICAL-BINDING.json", "expected/ODD-PHYSICAL-BINDING.json"),
                      ("7113-signed-grid.py", "replay/supplier7112/short-caller/check_odd_caller_exact_grid.py"),
                      ("7113-signed-child.py", "replay/supplier7112/short-caller/signed_child.py")):
        assert signed[key] == pins["inputs/" + name]
    binding = decode(source("inputs/PHYSICAL-BINDING.json"))
    assert binding["caller_sha256"] == pins["inputs/CALLER.json"]
    assert binding["occurrence_and_geometry"]["ambient"] == 145
    lead_inputs = {}
    for line in source("engines/LEAD-PINS").decode().splitlines():
        expected, name = line.split()
        assert name not in lead_inputs and pins[name] == expected
        lead_inputs[name] = expected
    assert len(lead_inputs) == 4


def execute(tmp, script, receipt=None):
    result = run([sys.executable, "-I", "-B", str(tmp / script)], capture_output=True, timeout=22)
    if receipt is None:
        assert result.returncode == 1 and not result.stdout and b"AssertionError" in result.stderr
        return None
    if result.returncode:
        sys.stderr.write(result.stderr.decode(errors="replace"))
    result.check_returncode()
    assert result.stdout == source("receipts/" + receipt), receipt
    return decode(result.stdout)


def compare(lead, independent):
    assert lead["native"] == independent["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert lead["caller"] == independent["caller"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert lead["basis_columns_per_body"] == independent["basis_rows_per_body"] == 36
    assert lead["target_difference_rank"] == independent["old_endpoint_displacement_rank"] == 4
    assert lead["ports"] == independent["ports"] == [15, 17, 27, 34, 35, 42, 47, 55]
    assert lead["body_signs"] == independent["physical_sectors"]["stage17_signs"] == [1, -1]
    assert independent["physical_sectors"]["central"] == independent["physical_sectors"]["other_bodies"] == 1
    assert [i for i, x in lead["diagonal"] if x == "2"] == independent["old_displacement_roles_local"] == [0, 1, 16, 17]
    assert independent["clocks"] == [4646, 4660] and independent["host_clock"] == 4691
    assert independent["host_roles_global"] == [36, 37]
    assert independent["body_dependent_occurrences"] == [[4646,"idle",1],[4660,"idle",1],[4691,"host",2]]
    by_case = {tuple(c["deleted_clocks"]): c for c in lead["cases"]}
    witnesses = {(4646,): [[16,17,"-6"],[17,17,"-2"]],
                 (4660,): [[16,16,"-2"],[16,17,"6"]],
                 (4646,4660): [[16,16,"-2"],[17,17,"-2"]]}
    assert len(by_case) == len(independent["retirement_cases"]) == len(witnesses) == 3
    for c in independent["retirement_cases"]:
        deleted = tuple(c["deleted"])
        other = by_case[deleted]
        assert c["max_complete_endpoint_displacement_rank"] == other["rank_upper"] == 4-len(deleted)
        assert c["optimistic_paid_gain_interval"] == other["optimistic_raw"]
        lower, upper = map(Q, other["optimistic_raw"])
        assert Q("63.51")*len(deleted) < lower <= upper < Q("63.52")*len(deleted)
        assert other["result"] == "EXCLUDED" and c["outside_host_nonzeros"] == 2
        assert c["first_outside_host_entries"] == witnesses[deleted]
        assert c["forced_host_block"] == [["-1","1"],["-1/2","-1/2"]]
        assert {i for a,b,_ in witnesses[deleted] for i in (a,b)} == {16,17}
    assert not independent["unresolved"]


def main():
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 12) or not __debug__:
        raise SystemExit("CPython 3.12 with assertions is required")
    authenticate()
    with TemporaryDirectory(prefix="p104-stage17-idle-retirement-") as name:
        tmp = Path(name)
        (tmp / "inputs").mkdir()
        for path in (ROOT / "inputs").iterdir():
            (tmp / "inputs" / path.name).write_bytes(source("inputs/" + path.name))
        (tmp / "PINS").write_bytes(source("engines/LEAD-PINS"))
        for engine in ("lead.py", "independent.py"):
            (tmp / engine).write_bytes(source("engines/" + engine))
        lead = execute(tmp, "lead.py", "LEAD.json")
        independent = execute(tmp, "independent.py", "INDEPENDENT.json")
        compare(lead, independent)
        caller_path = tmp / "inputs/CALLER.json"
        caller = decode(caller_path.read_bytes())
        caller["events"][4660][3] = [16]
        caller_path.write_text(dumps(caller), encoding="utf-8")
        execute(tmp, "lead.py")
        execute(tmp, "independent.py")
    print(dumps({"checked_cases": 3, "body_signs": [1,-1], "basis_per_sign": 36,
                 "endpoint_difference_rank": 4, "single_retirement_capacity": 3,
                 "double_retirement_capacity": 2, "forced_support_roles": [36,37,52,53],
                 "corrupt_caller_rejected": True, "unresolved": 0, "kappa_delta": "0"}, sort_keys=True))
    print("PASS_P104_STAGE17_IDLE_RETIREMENT_BOUND")


if __name__ == "__main__":
    main()
