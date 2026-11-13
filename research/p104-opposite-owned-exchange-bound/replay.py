"""Replay both fixed-direction exclusions for the opposite owned transfers."""
from hashlib import sha256
from json import loads
from pathlib import Path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "inputs"
LEAD = "receipts/REVERSE.json"
FORWARD = "receipts/FORWARD.jsonl"
PINNED = {
    "PROVENANCE.json", "check_exchange.py", "check_opposite_owned_forward.py", LEAD, FORWARD,
    "inputs/7481-WORD.json.gz", "inputs/7481-APPLICATION.json", "inputs/7113-CALLER.json",
    "inputs/gate.py",
}


def unique(items):
    result = dict(items)
    assert len(result) == len(items), "duplicate JSON key"
    return result


def parse(data):
    return loads(data, object_pairs_hook=unique)


def check_hash(data, digest):
    assert sha256(data).hexdigest() == digest, "changed pinned bytes"


def reproduce(script, *arguments):
    result = run([executable, "-I", "-B", str(ROOT / script), *map(str, arguments)],
                 capture_output=True, timeout=32, check=True)
    assert not result.stderr
    return result.stdout


def forward_records(data):
    records = [parse(line) for line in data.splitlines()]
    records[-1].pop("seconds")
    return records


def cross_check(lead, forward):
    assert lead["status"] == "EXACT_ONE_DIRECTION_EXCLUSION"
    assert lead["window"] == [40536, 40558] and lead["unresolved"] == []
    assert lead["gross_raw"] == 17 and lead["productive_delta"] == {}
    left, right, final = forward
    assert final["status"] == "PASS_INDEPENDENT_OPPOSITE_OWNED_FIXED_DIRECTIONS"
    assert final["case_count"] == len(lead["directions"]) == 2
    assert final["runner_cap_seconds"] == lead["runner_cap_seconds"] == 30
    assert final["completed"] == ["L_TO_R", "R_TO_L"] and final["unresolved"] == []
    assert [row["offered_rank"] for row in lead["directions"]] == [9, 3]
    assert sorted(map(int, left["left"])) == lead["source_left_roles"]
    assert sorted(map(int, right["ingresses"])) == [40536, 40546, 40548]
    assert not any(left["left"].values())
    assert not any(right["right"].values()) and not any(right["ingresses"].values())
    assert [row["omitted_ADD"] for row in (left, right)] == [40557, 40539]
    for primary, independent in zip(lead["directions"], (left, right), strict=True):
        assert independent["status"] == "EXACT_FIXED_DIRECTION_SEPARATOR"
        for key in ("retained_direction", "target_cut", "target_role", "probe", "target_response"):
            assert primary[key] == independent[key], key
        assert independent["target_response"] == "1/2" and independent["control_target_response"] == 0
        assert independent["init_guards_each"] == 67 and independent["copy_guards_each"] == 1


def rejects(check):
    try:
        check()
    except AssertionError:
        return
    raise AssertionError("rejection control unexpectedly passed")


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    pins = parse((ROOT / "PINS.json").read_bytes())
    assert set(pins) == PINNED
    for name, digest in pins.items():
        check_hash((ROOT / name).read_bytes(), digest)
    primary = reproduce("check_exchange.py", INPUTS)
    assert primary == (ROOT / LEAD).read_bytes()
    independent = reproduce("check_opposite_owned_forward.py", INPUTS, ROOT / LEAD, pins[LEAD])
    forward = forward_records(independent)
    assert forward == forward_records((ROOT / FORWARD).read_bytes())
    lead = parse(primary)
    cross_check(lead, forward)
    rejects(lambda: parse('{"clock":0,"clock":1}'))
    rejects(lambda: check_hash(b"changed native word", pins["inputs/7481-WORD.json.gz"]))
    mutated = [dict(forward[0], control_target_response="1/2"), *forward[1:]]
    rejects(lambda: cross_check(lead, mutated))
    print("PASS_OPPOSITE_OWNED_EXCHANGE: two exact fixed-direction exclusions")


if __name__ == "__main__":
    main()
