"""Rebuild directed prices and reconcile both exact Type B endpoint exclusions."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path
from shutil import copyfile
from subprocess import run
from sys import executable
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CAP = 25350


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    value = dict(pairs)
    require(len(value) == len(pairs), "duplicate JSON key")
    return value


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def verify_sources():
    local_pins = read((HERE / "LOCAL-PINS.json").read_bytes())
    for relative, pin in local_pins.items():
        path = (HERE / relative).resolve()
        require(path.is_relative_to(HERE) and sha256(path.read_bytes()).hexdigest() == pin,
                f"changed local dependency {relative}")
    public = read((HERE / "PROVENANCE.json").read_bytes())["files"]
    for relative, source in public.items():
        require(relative in local_pins, f"untracked provenance path {relative}")
        raw = (HERE / relative).read_bytes()
        if source["uncompress"]:
            raw = decompress(raw)
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(sha256(raw).hexdigest() == source["sha256"] and blob == source["git_blob"],
                f"changed public source {relative}")


def reconcile(price, keys, modular, exact, pins):
    require(price["head"] == modular["head"] == exact["head"] == HEAD,
            "changed comparator")
    require(price["keys_sha256"] == modular["keys_sha256"] == exact["input_sha256"]["keys"] == pins["KEYS.json"]
            and modular["price_sha256"] == exact["input_sha256"]["price"] == pins["PRICE.json"], "changed price or keys")
    require(modular["status"] == exact["status"] == "EXHAUSTED"
            and modular["unvisited_index_interval"] == [CAP, CAP] and not exact["unvisited"]
            and not modular["provisional"] and not exact["survivors"], "incomplete replay")
    require(modular["case_cap"] == exact["case_cap"] == exact["tested"] == len(keys) == CAP
            and exact["old_endpoint_columns"] == 36, "incomplete arbitrary-input gate")
    require(modular["q"] == -1 and modular["body"] == "all one" and modular["prime"] == 65521
            and exact["common_denominator"] > 0, "changed specialization")
    require(sum(price["complete_paid"].values()) == 110519
            and sum(price["complete_targets"].values()) == 22461
            and price["signed_surplus"] == 1424 and price["empty_root_credit"] == 0, "changed complete price")
    counts = Counter()
    for index, (key, residue, rational) in enumerate(zip(keys, modular["records"], exact["outcomes"], strict=True)):
        clocks = sorted(key["odd"] + key["even"])
        m = len(key["odd"])
        require(len(clocks) == 2*m == len(set(clocks)) and m in (3,4), "duplicate or wrong clocks")
        require(clocks == rational["key"] and rational["price"] == key["price"]
                and rational["status"] == "excluded", f"changed rational key {index}")
        i, probe, row, value = residue
        require(i == index and probe == "dense" and 0 <= row < 36 and 0 < value < 65521,
                f"invalid modular witness {index}")
        row, value = rational["dense_witness"]
        require(36 <= row < 72 and Fraction(value), f"invalid rational witness {index}")
        counts[m] += 1
    require(dict(counts) == {3: 10400, 4: 14950}
            and modular["tested_by_transfer_count"] == {"3":10400, "4":14950}
            and exact["counts"] == {"excluded":CAP}, "wrong exhausted coverage")
    return (dumps({
        "head": HEAD, "tested": CAP, "exactly_three": counts[3], "exactly_four": counts[4],
        "specialization": {"q": -1, "body": "all one"},
        "dense_witnesses_each": CAP, "survivors": 0, "unvisited": 0,
        "input_sha256": {k:pins[k] for k in ("PRICE.json","KEYS.json","MODULAR.json","EXACT.json")},
        "compatible_gross_upper": "0",
    }, sort_keys=True, indent=2) + "\n").encode()


def replay(output):
    require(__debug__, "assertions must be enabled")
    verify_sources()
    pins = read((HERE / "receipts/SHA256.json").read_bytes())
    output.mkdir(parents=True, exist_ok=False)

    def accept(name, raw):
        require(sha256(raw).hexdigest() == pins[name], f"changed generated receipt {name}")
        (output / name).write_bytes(raw)
        return raw

    with TemporaryDirectory(prefix="three-four-type-b-phases-") as directory:
        root = Path(directory)
        literal = root / "inputs"
        price_root = root / "price"
        price_inputs = price_root / "inputs"
        literal.mkdir()
        price_inputs.mkdir(parents=True)
        caller = decompress((HERE / "inputs/7113-CALLER.json.gz").read_bytes())
        (literal / "CALLER.json").write_bytes(caller)
        (price_inputs / "7113-CALLER.json").write_bytes(caller)
        for name in ("7334-ADMITTED.json","7334-READBACK.json","R59-PRICE.json","pricing.py","derivative_check.py"):
            copyfile(HERE / "inputs" / name, price_inputs / name)
        for name in ("screen.py", "two_phase.py"):
            copyfile(HERE / "inputs" / name, literal / name)
        quote_engine = price_root / "quote.py"
        copyfile(HERE / "engines/quote.py", quote_engine)

        def stage(script, *args, timeout):
            return run([executable, "-I", "-B", str(script), *map(str, args)], cwd=root,
                       check=True, capture_output=True, timeout=timeout).stdout

        price_path, keys_path = price_root / "PRICE.json", price_root / "KEYS.json"
        price_raw = accept("PRICE.json", stage(quote_engine, "--keys-out", keys_path, timeout=25))
        price_path.write_bytes(price_raw)
        keys_raw = accept("KEYS.json", keys_path.read_bytes())
        modular_raw = accept("MODULAR.json", stage(HERE / "engines/reflection_gate.py", root, timeout=35))
        exact_script = HERE / "engines/multiple_edits.py"
        exact_args = ["--price", price_path, "--keys", keys_path, "--admission",
                      price_inputs / "7334-ADMITTED.json", "--caller", price_inputs / "7113-CALLER.json"]
        exact_raw = accept("EXACT.json", stage(exact_script, *exact_args, timeout=35))
        accept("COMPARE.json", reconcile(*map(read, (price_raw,keys_raw,modular_raw,exact_raw)), pins))
        (price_inputs / "7113-CALLER.json").write_bytes(caller + b"\n")
        rejected = run([executable, "-I", "-B", str(exact_script), *map(str, exact_args)],
                       cwd=root, capture_output=True, timeout=10)
        require(rejected.returncode == 1 and not rejected.stdout and b"changed input caller" in rejected.stderr,
                "changed caller was accepted")
    print("PASS_TYPE_B_PHASE_TRANSFERS triples=10400 quadruples=14950 excluded=25350 unresolved=0 kappa_change=0")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.out:
        replay(args.out.resolve())
    else:
        with TemporaryDirectory(prefix="three-four-type-b-receipts-") as directory:
            replay(Path(directory) / "out")


if __name__ == "__main__":
    main()
