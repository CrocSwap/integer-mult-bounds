"""Replay both owned MOVE chronology screens and their exact reconciliations."""

from argparse import ArgumentParser
from hashlib import sha1, sha256
from json import loads
from pathlib import Path
from shutil import copyfile
from subprocess import run
from sys import executable
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent


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
    for relative, pin in read((HERE / "LOCAL-PINS.json").read_bytes()).items():
        local = (HERE / relative).resolve()
        require(local.is_relative_to(HERE) and sha256(local.read_bytes()).hexdigest() == pin,
                f"changed local input {relative}")
    provenance = read((HERE / "PROVENANCE.json").read_bytes())["files"]
    for relative, proof in provenance.items():
        raw = (HERE / relative).read_bytes()
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(sha256(raw).hexdigest() == proof["sha256"] and blob == proof["git_blob"],
                f"changed public source {relative}")


def replay(output):
    require(__debug__, "assertions must be enabled")
    verify_sources()
    output.mkdir(parents=True, exist_ok=False)
    with TemporaryDirectory(prefix="owned-move-chronology-") as directory:
        workspace = Path(directory)
        word = HERE / "inputs/7334-WORD.json.gz"

        def run_case(round_number, inherited):
            root = workspace / str(round_number)
            for relative in ("inputs", "price/inputs", "lead", "independent"):
                (root / relative).mkdir(parents=True, exist_ok=False)
            copyfile(word, root / "inputs" / word.name)
            shared = ("ADMITTED.json", "READBACK.json", "pricing.py")
            if round_number == 80:
                shared += ("7277-OWNED.json", "7277-CONTACTS.json")
            for name in shared:
                copyfile(HERE / "inputs" / name, root / "price/inputs" / name)
            for name, raw in inherited.items():
                (root / "price/inputs" / f"R80-{name}.json").write_bytes(raw)

            def stage(name, engine, args=(), destination=None):
                result = run([executable, "-I", "-B", str(engine), *map(str, args)], cwd=root,
                             check=True, capture_output=True, timeout=22)
                receipt = f"R{round_number}-{name}.json"
                require(result.stdout == (HERE / "receipts" / receipt).read_bytes(),
                        f"changed receipt {receipt}")
                (output / receipt).write_bytes(result.stdout)
                if destination:
                    destination.write_bytes(result.stdout)
                return result.stdout

            quote_engine = root / "price/quote.py"
            copyfile(HERE / "engines" / f"quote_r{round_number}.py", quote_engine)
            quote = stage("PRICE", quote_engine, destination=root / "price/PRICE.json")
            forward_args = [root, sha256(quote).hexdigest()] if round_number == 80 else [root]
            if round_number == 82:
                (root / "inputs/PRICE.json").write_bytes(quote)
            forward = stage("FORWARD", HERE / "engines" / f"forward_r{round_number}.py", forward_args,
                            root / "lead/RESULT.json")
            reverse = stage("REVERSE", HERE / "engines" / f"reverse_r{round_number}.py", [root],
                            root / "independent/RESULT.json")
            compared = stage("COMPARE", HERE / "engines" / f"compare_r{round_number}.py", [root])
            return root, {"FORWARD": forward, "REVERSE": reverse, "COMPARE": compared}

        _, r80 = run_case(80, {})
        last_root, r82 = run_case(82, r80)
        r80_result, r82_result = read(r80["REVERSE"]), read(r82["REVERSE"])
        require(r80_result["complete"] and r80_result["owned_paid"] == 47
                and r80_result["lifetimes"] == 73 and r80_result["neighbor_pairs"] == 9
                and r80_result["strict_opposite"] == 0 and not r80_result["unvisited_geometry"],
                "incomplete R80 exclusion")
        require(r82_result["complete"] and len(r82_result["placements"]) == 10
                and r82_result["visited_cuts"] == 51 and not r82_result["survivors"]
                and not r82_result["unvisited"], "incomplete R82 exclusion")
        source = last_root / "inputs" / word.name
        source.write_bytes(source.read_bytes() + b"\n")
        negative = run([executable, "-I", "-B", str(HERE / "engines/reverse_r82.py"), str(last_root)],
                       cwd=last_root, capture_output=True, timeout=22)
        require(negative.returncode == 1 and not negative.stdout
                and b"changed dependency inputs/7334-WORD.json.gz" in negative.stderr,
                "changed word was accepted")
    print("PASS_OWNED_MOVE_CHRONOLOGY turns=0 neighbor_pairs=9 cuts=51 excluded=51 unresolved=0 kappa_change=0")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.out:
        replay(args.out.resolve())
    else:
        with TemporaryDirectory(prefix="owned-move-chronology-receipts-") as directory:
            replay(Path(directory) / "out")


if __name__ == "__main__":
    main()
