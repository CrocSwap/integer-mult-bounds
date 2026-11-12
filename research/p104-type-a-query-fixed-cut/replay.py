"""Replay the exact signed QUERY pair prices and formal fixed-cut result."""
from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha1, sha256
from json import loads
from pathlib import Path
from shutil import copyfile, copytree
from subprocess import run
from sys import executable
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
CALLER_BLOB = "9451ceaf6e8e037894680b549f3ef41c21b260d7"
SELECTED, UNRESOLVED = [1580, 1659], [1516, 1721]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "Duplicate JSON key or input path")
    return result


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def replay(output):
    require(__debug__, "CPython assertions must be enabled")
    pins = read((HERE / "LOCAL-PINS.json").read_bytes())
    for name, expected in pins.items():
        path = HERE / name
        require(path.resolve().is_relative_to(HERE) and digest(path.read_bytes()) == expected,
                f"Changed pinned file {name}")
    expected = read((HERE / "receipts/SHA256.json").read_bytes())
    raw = decompress((HERE / "inputs/7113-CALLER.json.gz").read_bytes())
    header = f"blob {len(raw)}".encode() + bytes(1)
    require(digest(raw) == CALLER and sha1(header + raw).hexdigest() == CALLER_BLOB,
            "Changed exact #7113 caller")
    output.mkdir(parents=True, exist_ok=False)
    with TemporaryDirectory(prefix="p104-query-pair-") as tmp:
        work = Path(tmp)
        copytree(HERE / "engines", work, dirs_exist_ok=True)
        price_root, lead, independent = (work / name for name in ("price", "lead", "independent"))
        inputs = price_root / "inputs"
        inputs.mkdir()
        for name in ("QUERY-CENSUS.json", "7334-READBACK.json", "7334-ADMITTED.json", "pricing.py"):
            copyfile(HERE / "inputs" / name, inputs / name)
        caller = inputs / "7113-CALLER.json"
        caller.write_bytes(raw)

        def stage(name, script, *args, timeout=20):
            result = run([executable, "-I", "-B", str(script), *map(str, args)], cwd=work,
                         capture_output=True, check=True, timeout=timeout)
            require(digest(result.stdout) == expected[name], f"Changed receipt {name}")
            (output / name).write_bytes(result.stdout)
            return read(result.stdout)

        price = stage("PRICE.json", price_root / "quote.py")
        price_path = price_root / "PRICE.json"
        copyfile(output / "PRICE.json", price_path)
        stage("DERIVATIVE.json", price_root / "derivative_check.py")
        direct = stage("DIRECT.json", lead / "fixed_cut.py", work)
        unit = stage("UNIT.json", independent / "transported_product.py", "--price", price_path, "--price-sha",
                     expected["PRICE.json"], "--caller", caller)
        args = ("--price", price_path, "--caller", caller, "--unit-receipt", output / "UNIT.json")
        finite = stage("FORMAL-PROBES.json", independent / "formal_necessity.py", *args)
        gaussian = stage("GAUSSIAN.json", independent / "gaussian_necessity.py", *args)
        symbolic = stage("SYMBOLIC.json", independent / "symbolic_transport.py", "--price", price_path,
                         "--caller", caller, "--gaussian", output / "GAUSSIAN.json", timeout=25)
        body = stage("FULL-BODY.json", lead / "full_body.py", work, timeout=25)

        require(not direct["unvisited"] and not unit["unvisited"] and len(direct["decisions"]) == 6,
                "Incomplete unit-body gate")
        for a, b, key in zip(direct["decisions"], unit["outcomes"], price["eligible_pairs_before_support"], strict=True):
            require(a["key"] == b["pair"] == key and b["q_plus"]["rank"] == 0 and
                    a["rank"] == b["q_minus"]["rank"] == 2 and
                    (a["square_witness"] is None) == (b["q_minus"]["square_rank"] == 0),
                    "Independent signed shape decisions differ")
        require([x["key"] for x in direct["decisions"] if x["decision"] == "provisional"] ==
                unit["rank_at_most_two_square_zero_keys"] == [UNRESOLVED, SELECTED],
                "Wrong provisional pairs")
        require(len(finite["probes"]) == 17 and len(gaussian["probes"]) == 18,
                "Incomplete exact body-specialization controls")
        require(symbolic["status"] == "EXACT_SYMBOLIC_AXES" and symbolic["pair"] == SELECTED and
                symbolic["unvisited_pair"] == UNRESOLVED and not any(symbolic["cross_actions"].values()) and
                not symbolic["outer_body_dependency"] and not symbolic["outer_q_odd_entries"],
                "Wrong formal scope or correction")
        require([body["fixed_cut"], body["later"]] == SELECTED and
                body["independent_basis_columns"] == 144 and body["arbitrary_body_variables"] == 17 and
                body["unchanged_recovered_action"] and body["sign_control"] == "passed",
                "Independent all-character body replay incomplete")

        caller.write_bytes(raw + b" ")
        negative = run([executable, "-I", "-B", str(independent / "transported_product.py"), "--price",
                        str(price_path), "--price-sha", expected["PRICE.json"], "--caller", str(caller)],
                       cwd=work, capture_output=True, timeout=20)
        require(negative.returncode and b"changed input 7113-CALLER.json" in negative.stderr and
                not negative.stdout, "Changed caller was accepted")

    require({p.name for p in output.iterdir()} == set(expected), "Wrong replay receipt set")
    print("PASS_TYPE_A_QUERY_PAIR_FIXED_CUT pairs=6 excluded=4 symbolic=1 unresolved=1 kappa_change=0")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.out:
        replay(args.out.resolve())
    else:
        with TemporaryDirectory(prefix="p104-query-pair-receipts-") as temp:
            replay(Path(temp) / "out")


if __name__ == "__main__":
    main()
