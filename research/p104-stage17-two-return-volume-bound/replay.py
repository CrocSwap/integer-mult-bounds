"""Verify the exact rank-two window and its one-field physical volume floor."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
ENGINES = {
    "count_modes.py": "R173-LEAD.json",
    "tensor_columns.py": "R173-INDEPENDENT.json",
}


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def source(name):
    p = Path(name)
    if p.is_absolute() or ".." in p.parts or p.as_posix() != name:
        raise ValueError(f"invalid source path {name}")
    return (ROOT/p).read_bytes()


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def read_json(name):
    return decode(source(name))


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate():
    pins = read_json("LOCAL-PINS.json")
    for name, expected in pins.items():
        raw = source(name)
        if digest(raw) != expected:
            raise ValueError(f"changed package dependency {name}")
        if name.endswith(".json"):
            decode(raw)
    prov = read_json("PROVENANCE.json")
    for name, entry in prov["files"].items():
        raw = source(name)
        assert digest(raw) == entry["sha256"]
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest() == entry["git_blob"]
    price = prov["derived_inputs"]["inputs/R92-PRICE.json"]
    assert digest(source("inputs/R92-PRICE.json")) == read_json(price["receipt"])[price["key"]]
    caller = read_json("inputs/7113-SHA256.json")
    assert digest(source("inputs/PHYSICAL-BINDING.json")) == caller["expected/ODD-PHYSICAL-BINDING.json"]


def save(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def execute(script, succeeds=True):
    result = run([sys.executable, "-I", "-B", str(script)], capture_output=True, timeout=46)
    if succeeds:
        if result.returncode:
            sys.stderr.write(result.stderr.decode(errors="replace"))
        result.check_returncode()
    else:
        assert result.returncode != 0 and b"changed source inputs/CALLER.json" in result.stderr
        assert not result.stdout
    return result.stdout


def replay(tmp, out):
    authenticate()
    for path in (ROOT/"inputs").iterdir():
        save(tmp/"inputs"/path.name, source("inputs/"+path.name))
    save(tmp/"inputs/signed_child.py", source("inputs/7113-signed-child.py"))
    results = []
    for engine, receipt in ENGINES.items():
        save(tmp/engine, source("engines/"+engine))
        raw = execute(tmp/engine)
        assert raw == source("receipts/"+receipt), f"changed receipt {receipt}"
        results.append(decode(raw))
        if out:
            save(out/receipt, raw)
    lead, independent = results
    assert lead["head"] == independent["benchmark"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert lead["caller"] == independent["caller"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert lead["clocks"] == independent["clocks"] == [4646, 4660]
    assert lead["width1_walsh_multiplicities_one_spectator"] == independent["eigenphase_counts_per_lane"]
    assert lead["width1_rank_both_lanes"] == independent["combined_displacement_rank"] == 736
    assert lead["uniform_volume_lower"] == independent["volume_lower_all_widths"] == "23/16"
    assert Q(lead["affordable_rank16_volume"][1]) == Q(independent["rank16_affordability_upper"])
    upper = Q(independent["eight_port_raw_delta_upper"])
    assert Q(lead["raw_gain_interval_upper_model"][1]) == upper < Q("-55.11596368443582")
    bit = Q(read_json("inputs/R92-PRICE.json")["retained_bit_premise"])
    assert bit == Q("0.00376669") < Q(1, 2) and Q(23, 16)**2 > 2

    caller = tmp/"inputs/CALLER.json"
    caller.write_bytes(caller.read_bytes()+b" ")
    execute(tmp/"tensor_columns.py", succeeds=False)
    print(dumps({"authenticated_receipts":2, "mutated_caller_rejected":True,
                 "physical_rank":736, "per_lane_columns":512, "kappa_delta":"0"}, sort_keys=True))
    print("PASS_P104_STAGE17_TWO_RETURN_VOLUME_BOUND")


def main():
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 12) or not __debug__:
        raise SystemExit("CPython 3.12 with assertions is required")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="p104-stage17-volume-") as d:
        replay(Path(d), args.out)


if __name__ == "__main__":
    main()
