"""Reproduce the closed chart-3 entrance price and exact chronology bounds."""
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
WORD = "inputs/7334-WORD.json.gz"
SIZES = {1:321, 2:95, 3:25, 4:14, 5:11, 6:7, 7:3, 8:1}


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def source(name):
    path = PurePosixPath(name)
    if not path.parts or path.is_absolute() or ".." in path.parts or path.as_posix() != name:
        raise ValueError("invalid package path " + name)
    return (ROOT / path).read_bytes()


def materialize(directory):
    pins = decode(source("LOCAL-PINS.json"))
    for name, expected in pins.items():
        if digest(source(name)) != expected:
            raise ValueError("changed package dependency " + name)

    provenance = decode(source("PROVENANCE.json"))
    for name, entry in provenance["files"].items():
        raw = source(name)
        assert digest(raw) == entry["sha256"] == pins[name]
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        assert blob == entry["git_blob"]
    admitted = decode(source("inputs/7334-ADMITTED.json"))
    assert admitted["head"] == HEAD and admitted["kappa"] == "0.00364665195644"

    inputs = directory / "inputs"
    inputs.mkdir()
    word = source(WORD)
    assert digest(gzip.decompress(word)) == provenance["derived_inputs"][WORD]["decoded_sha256"]
    (directory / WORD).write_bytes(word)
    price_name = "inputs/R92-PRICE.json.gz"
    price_pin = provenance["derived_inputs"][price_name]
    price = gzip.decompress(source(price_name))
    manifest = decode(source(price_pin["manifest"]))
    assert digest(price) == price_pin["sha256"] == manifest[price_pin["key"]]
    (inputs / "R92-PRICE.json").write_bytes(price)
    (inputs / "pricing.py").write_bytes(source("inputs/pricing.py"))
    for engine in ("price", "forward", "reverse", "delay", "delay_reverse"):
        (directory / f"{engine}.py").write_bytes(source(f"engines/{engine}.py"))


def run(directory, engine, *args):
    return subprocess.run(
        [sys.executable, "-I", "-B", str(directory / f"{engine}.py"), *map(str, args)],
        capture_output=True,
        timeout=12,
        check=False,
    )


def compare(price, forward, reverse):
    assert price["head"] == forward["comparator_head"] == reverse["head"] == HEAD
    assert price["caller"] == forward["caller_head"] == reverse["caller"] == CALLER
    assert forward["scope_exhausted"] and reverse["exhausted"]
    assert forward["events"] == reverse["caps"]["events"] == 76466
    assert forward["time_cap_seconds"] == reverse["caps"]["seconds"] == 10
    assert forward["initial_chart"] == reverse["caps"]["start_chart"] == 3
    assert forward["productive_helpers"] == reverse["productive_helpers"] == 1101
    assert forward["public_main"] == 400
    assert forward["chart3_helpers"] == reverse["chart_3_helpers"] == 860
    assert forward["outcomes"] == {"other_initial_chart":241,"proper":768,"zero_residual_target":92}
    assert forward["outcomes"]["zero_residual_target"] == reverse["zero_residual"] == 92
    assert forward["first_proper_MOVEs"] == reverse["proper_nonempty"] == 768
    assert len(forward["components"]) == len(reverse["components"]) == 477
    assert not forward["support_unresolved"] and not reverse["survivors"]
    assert Counter(len(c["roles"]) for c in forward["components"]) == SIZES
    assert {int(k):v for k,v in reverse["sizes"].items()} == SIZES

    role_ids = set()
    for direct, other in zip(forward["components"], reverse["components"], strict=True):
        assert direct["roles"] == other["roles"] and direct["chart"] == other["upper"]
        assert not role_ids.intersection(direct["roles"])
        role_ids.update(direct["roles"])
        assert [m[0] for m in direct["first_moves"]] == direct["roles"]
        assert [m[1] for m in direct["first_moves"]] == other["first_move_clocks"]
        assert direct["blocker_count"] == other["boundary_contacts"] > 0
        witness = direct["first_blocker"]
        op, dst, src, *_ = witness["event"]
        assert op in ("ADD", "COPY")
        peer = src if dst == witness["role"] else dst
        assert [witness["clock"], witness["role"], peer, op] == other["earliest_blocker"]
    assert len(role_ids) == 768
    sole_boundary = [c for c in forward["components"] if c["blocker_count"] == 1]
    assert len(sole_boundary) == 1 and sole_boundary[0]["roles"] == [624]
    assert sole_boundary[0]["first_blocker"] == {
        "role":624, "clock":32943, "event":["ADD",130,624,"-1/2",3], "reason":"main_contact"
    }

    assert Fraction(price["one_edit_gross_upper"]) < Fraction("0.380712103178623")
    assert Fraction(price["gross_whole_stock_upper"]) < Fraction("419.164025599663")
    assert price["whole_stock_relaxation_roles"] == 1101
    keys = decode(source("receipts/COMPONENTS.json"))
    assert keys == forward["components"]


def compare_delay(price, lead, reverse):
    fields = ("head", "helper", "main", "old_add", "first_move", "first_blocker",
              "literal_paths", "reachable_cut", "word_sha256", "payload_sha256")
    assert all(lead[key] == reverse[key] for key in fields)
    assert reverse["head"] == HEAD and (reverse["helper"], reverse["main"]) == (624,130)
    assert reverse["event_count"] == lead["caps"]["events"] == 76466
    assert reverse["seconds_cap"] == lead["caps"]["seconds"] == 10
    assert reverse["tested_pre_event_cuts"] == list(range(32946,32953))
    assert reverse["live_main_charts"] == [3] * 7
    assert [clock for clock,_ in reverse["intervening_read_only"]] == [32946,32948,32950]
    assert reverse["first_blocker"] == [32952,["ADD",624,623,"1",117]]
    assert reverse["literal_paths"]["130"][0] == [32981,3,336]
    assert lead["stop_charts"] == {"130":3,"624":117}
    assert not reverse["reachable_cut"] and not reverse["main_path_aliases_to_upper_span"]
    quote = price["cases"]["9/5"]
    assert reverse["paid_delta"] == quote["paid_delta"] == {"5":-17}
    assert reverse["target_delta"] == quote["target_delta"] == {"4":17,"9":-17}
    assert Fraction(quote["gross"][1]) < Fraction("0.380712103178623")
    assert reverse["compatible_saving"] == 0
    assert reverse == decode(source("receipts/DELAY-CUT.json"))


def replay(directory):
    materialize(directory)
    word = directory / WORD
    command_args = {"price": (), "forward": ("--word", word), "reverse": (word,),
                    "delay": (word,), "delay_reverse": (word,)}
    expected = decode(source("receipts/SHA256.json"))
    receipts = {}
    for engine, args in command_args.items():
        receipt = engine.upper() + ".json"
        result = run(directory, engine, *args)
        if result.returncode:
            sys.stderr.buffer.write(result.stderr)
            result.check_returncode()
        assert digest(result.stdout) == expected[receipt], ("changed receipt", receipt)
        receipts[receipt] = result.stdout
        if engine == "price":
            (directory / "PRICE-BOUND.json").write_bytes(result.stdout)
    compare(*(decode(receipts[name]) for name in ("PRICE.json", "FORWARD.json", "REVERSE.json")))

    compare_delay(*(decode(receipts[name]) for name in ("PRICE.json", "DELAY.json", "DELAY_REVERSE.json")))

    altered = directory / "altered-word.json.gz"
    altered.write_bytes(word.read_bytes() + b"\0")
    forward_fault = run(directory, "forward", "--word", altered)
    reverse_fault = run(directory, "reverse", altered)
    assert forward_fault.returncode == 1 and b"changed gzip input" in forward_fault.stderr
    assert reverse_fault.returncode == 1 and b"AssertionError" in reverse_fault.stderr
    try:
        decode(b'{"inputs/7334-WORD.json.gz":1,"inputs/7334-WORD.json.gz":2}')
    except ValueError as error:
        assert str(error) == "duplicate JSON key"
    else:
        raise AssertionError("duplicate dependency key accepted")
    return receipts


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as temporary:
        receipts = replay(Path(temporary))
    if args.out is not None:
        args.out.mkdir(parents=True, exist_ok=True)
        for name, raw in receipts.items():
            (args.out / name).write_bytes(raw)
    print("PASS_P104_CLOSED_CHART3_ENTRANCE_BOUND helpers=1101 proper=768 components=477 survivors=0 fixed_chart_delay_cuts=0")


if __name__ == "__main__":
    main()
