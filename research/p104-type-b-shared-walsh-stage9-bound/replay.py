"""Regenerate and compare the two stage-9 Walsh cut and flow certificates."""
import ast
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
        if "git_blob" in entry:
            assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == entry["git_blob"]
        else:
            assert decode(source(entry["receipt_path"]))[entry["receipt_key"]] == digest(raw)
    signed = decode(source("inputs/7113-SHA256.json"))
    assert signed["expected/ODD-TYPE-AB-CALLER.json"] == pins["inputs/CALLER.json"]
    assert signed["replay/supplier7112/short-caller/signed_child.py"] == pins["inputs/7113-signed-child.py"]
    old = decode(source("inputs/R92-PRICE.json"))
    comparator = decode(source("inputs/7334-RESULT.json"))
    predecessor = decode(source("inputs/R180-LEAD.json"))
    assert predecessor["head"] == old["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert comparator["caller_sha256"] == pins["inputs/CALLER.json"]
    assert comparator["status"] == "PASS_HELPER_319_FUSED_CALLER"
    assert Fraction(comparator["claim"]) == Fraction(old["kappa"])
    assert old["old_paid"]["8"] == 741 and old["full_paid_positions_before"] == 110519
    assert old["productive_positions_before"] == 22461
    child = ast.parse(source("inputs/7113-signed-child.py"))
    gate, = [ast.literal_eval(node.value) for node in child.body
             if isinstance(node, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "C" for t in node.targets)]
    assert gate == (((1, 1), (1, -1)), ((1, -1), (1, 1)))
    # Gaussian numerators over 2. Diagonal factors (1,i) on both sides
    # turn C into (1+i)/2 times the unnormalised two-point Walsh matrix.
    for row, entries in enumerate(gate):
        for col, (a, b) in enumerate(entries):
            for _ in range(row + col):
                a, b = -b, a
            assert (a, b) == ((-1, -1) if row == col == 1 else (1, 1))


def execute(tmp, script, receipt, *args):
    result = run([sys.executable, "-I", "-B", str(tmp / script), *map(str, args)],
                 capture_output=True, timeout=62)
    if receipt is None:
        assert result.returncode == 1 and not result.stdout and b"AssertionError" in result.stderr
        return None
    if result.returncode:
        sys.stderr.write(result.stderr.decode(errors="replace"))
    result.check_returncode()
    assert result.stdout == source("receipts/" + receipt), receipt
    return result.stdout


def compare(lead, explicit, lead_unforced, explicit_unforced):
    assert (lead["native_head"], lead["signed_head"], lead["predecessor"]) == (
        explicit["benchmark"], explicit["caller"], explicit["pr7411"])
    assert lead["forced"] == explicit["forced_clock"] == 2866
    assert lead["stage"] == explicit["stage"] == 9
    assert lead["ports"] == explicit["ports"]
    assert lead["tape_events"] == explicit["event_cap"] == 4783
    g, unit = explicit["graph"], explicit["unit"]
    assert lead["typed_events"] == g["counts"]
    assert len(g["gaps"]) == lead["edge_count"] + 2*lead["typed_events"]["SWAP"] == 7450
    assert len(g["nodes"]) == 7488 and len(g["equalities"]) == 3492 and len(g["fixed"]) == 74
    assert lead["anchors"] == sorted({g["nodes"][i][0] for i in g["fixed"] if 0 <= g["nodes"][i][0] < 4783}) == [3058]
    assert lead["rewards"] == {str(clock): rank for _, clock, _, rank in g["rewards"]}
    assert lead["credited_clocks"] == [clock for clock, _, _ in unit["collected_idle_calls"]] == [2866]
    assert lead["transitions"] == [[a[0], b[0]] for _, a, b in unit["conversions"]] == [[2865,2866], [2866,2867]]
    assert lead["cut"] == unit["flow_value"] == 17
    assert lead["upper_h8_units_per_port"] == Fraction(unit["upper_per_port"]) == -1
    assert explicit["weighted_if_needed"] is None
    assert Fraction(explicit["raw_upper_at_crossing"]) < Fraction("-63.232")
    assert lead_unforced["feasible_unforced_flow"] == explicit_unforced["flow_value"] == 16
    assert lead_unforced["all_original_cut"] == explicit_unforced["all_original_cut"] == 16
    assert lead_unforced["unforced_upper_h8_units_per_port"] == explicit_unforced["global_upper_units_per_port"] == 0
    assert lead_unforced["additional_solves"] == 0 and explicit_unforced["no_second_solve"]
    assert not explicit["build_admitted_by_price"]


def replay(tmp):
    (tmp / "inputs").mkdir()
    for name in ("CALLER.json", "R180-LEAD.json", "R92-PRICE.json", "pricing.py"):
        (tmp / "inputs" / name).write_bytes(source("inputs/" + name))
    for target, engine in (("replay.py", "lead.py"), ("lead_unforced.py", "lead_unforced.py"),
                           ("explicit.py", "explicit.py"), ("explicit_unforced.py", "explicit_unforced.py")):
        (tmp / target).write_bytes(source("engines/" + engine))
    lead = execute(tmp, "replay.py", "LEAD-FORCED.json")
    explicit = execute(tmp, "explicit.py", "EXPLICIT-FORCED.json")
    (tmp / "FORCED-RESULT.json").write_bytes(lead)
    explicit_path = tmp / "EXPLICIT.json"
    explicit_path.write_bytes(explicit)
    lu = execute(tmp, "lead_unforced.py", "LEAD-UNFORCED.json")
    eu = execute(tmp, "explicit_unforced.py", "EXPLICIT-UNFORCED.json", explicit_path)
    compare(*(decode(raw) for raw in (lead, explicit, lu, eu)))
    # Remove one unit from a nonforcing path of the certificate.
    damaged = decode(explicit)
    damaged["unit"]["positive_flow_arcs"].pop(0)
    explicit_path.write_text(dumps(damaged), encoding="utf-8")
    execute(tmp, "explicit_unforced.py", None, explicit_path)
    caller_path = tmp / "inputs/CALLER.json"
    caller = decode(caller_path.read_bytes())
    caller["events"][2866][3] = [10]
    caller_path.write_text(dumps(caller), encoding="utf-8")
    execute(tmp, "replay.py", None)
    execute(tmp, "explicit.py", None)


def main():
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 12) or not __debug__:
        raise SystemExit("CPython 3.12 with assertions is required")
    authenticate()
    with TemporaryDirectory(prefix="p104-shared-walsh-") as path:
        replay(Path(path))
    print(dumps({"events": 4783, "roles": 36, "eligible_calls": 16, "forced_cut": 17,
                 "forced_upper_h8_units_per_port": -1, "unforced_flow": 16, "unforced_upper": 0,
                 "corrupt_caller_and_flow_rejected": True, "kappa_delta": "0"}, sort_keys=True))
    print("PASS_P104_TYPE_B_SHARED_WALSH_STAGE9_BOUND")


if __name__ == "__main__":
    main()
