"""Replay two exact stage-17 parity-shell affine chart obstructions."""
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
                      ("7113-signed-child.py", "replay/supplier7112/short-caller/signed_child.py")):
        assert signed[key] == pins["inputs/" + name]
    binding = decode(source("inputs/PHYSICAL-BINDING.json"))
    assert binding["caller_sha256"] == pins["inputs/CALLER.json"]
    assert binding["occurrence_and_geometry"]["ambient"] == 145


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
    assert lead["head"] == independent["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert lead["caller"] == independent["caller"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert independent["pr7406"] == "a5fa7b464a773afb47eb8b9725b94f660c407528"
    assert lead["clocks"] == independent["clocks"] == [4646, 4660]
    assert lead["width_one_addresses"] == independent["case_count"] == 512
    assert lead["active_width_one"] == independent["residual_modes_total"] == 240
    assert lead["affine_hull_dimension"] == independent["affine_rank"] == 9
    assert independent["discard_one_lane_control_rank"] == 8
    assert independent["selected_axes"] == list(range(137, 145))
    assert lead["affine_minimum_volume_fraction"] == Q(independent["affine_chart_old_lane_volume"]) == 2
    phases = lead["phase_counts"]
    assert independent["forward_residual_multiplicities_by_lane"] == [
        {"(0, 0)": phases["0"] + phases["1"], "(-2, 0)": phases["2"], "(0, -2)": phases["3"]}] * 2
    assert Q(independent["residual_volume_old_lane"]) == Q(15, 16)
    lo, hi = map(Q, lead["rank16_affordability"])
    assert hi == Q(independent["affordability_upper"])
    assert 1 < lo <= hi < Q("1.003")
    low, high = map(Q, lead["ideal_one_lane_raw_gain"])
    assert Q("0.320") < low <= high < Q("0.321")
    low, high = map(Q, lead["affine_chart_raw_gain"])
    assert low <= high < Q("-126.39")
    assert not independent["build_admitted"]


def main():
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 12) or not __debug__:
        raise SystemExit("CPython 3.12 with assertions is required")
    authenticate()
    with TemporaryDirectory(prefix="p104-stage17-parity-shell-") as name:
        tmp = Path(name)
        (tmp / "inputs").mkdir()
        for path in (ROOT / "inputs").iterdir():
            (tmp / "inputs" / path.name).write_bytes(source("inputs/" + path.name))
        for engine in ("lead.py", "independent.py"):
            (tmp / engine).write_bytes(source("engines/" + engine))
        lead = execute(tmp, "lead.py", "LEAD.json")
        independent = execute(tmp, "independent.py", "INDEPENDENT.json")
        compare(lead, independent)
        caller_path = tmp / "inputs/CALLER.json"
        caller = decode(caller_path.read_bytes())
        caller["events"][4646][3] = [16]
        caller_path.write_text(dumps(caller), encoding="utf-8")
        execute(tmp, "lead.py")
        execute(tmp, "independent.py")
    print(dumps({"checked_addresses": 512, "residual_addresses": 240, "affine_rank": 9,
                 "old_lane_volume_required": "2", "affordability_below": "1.003",
                 "eight_port_gross_upper_below": "-126.39", "corrupt_caller_rejected": True,
                 "kappa_delta": "0"}, sort_keys=True))
    print("PASS_P104_STAGE17_PARITY_SHELL_AFFINE_BOUND")


if __name__ == "__main__":
    main()
