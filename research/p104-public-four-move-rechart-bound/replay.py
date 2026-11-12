"""Replay the signed predecessor matching and exact public chart intervals."""

from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha1, sha256
from json import loads
from pathlib import Path
from shutil import copyfile
from subprocess import run
from sys import executable
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    value = dict(pairs)
    require(len(value) == len(pairs), "duplicate JSON key")
    return value


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def authenticate():
    pins = read((HERE / "LOCAL-PINS.json").read_bytes())
    for relative, pin in pins.items():
        path = (HERE / relative).resolve()
        require(path.is_relative_to(HERE) and sha256(path.read_bytes()).hexdigest() == pin,
                f"changed local dependency {relative}")
    provenance = read((HERE / "PROVENANCE.json").read_bytes())
    for relative, entry in provenance["files"].items():
        require(relative in pins, f"unpinned public source {relative}")
        raw = (HERE / relative).read_bytes()
        if entry["uncompress"]:
            raw = decompress(raw)
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(sha256(raw).hexdigest() == entry["sha256"] and blob == entry["git_blob"],
                f"changed public source {relative}")
    for relative, entry in provenance["generated"].items():
        require(relative in pins, f"unpinned generated source {relative}")
        raw = decompress((HERE / relative).read_bytes())
        require(sha256(raw).hexdigest() == entry["receipt_sha256"],
                f"changed predecessor receipt {relative}")


def replay(output):
    require(__debug__, "assertions must be enabled")
    authenticate()
    output.mkdir(parents=True, exist_ok=False)
    with TemporaryDirectory(prefix="public-four-move-rechart-") as directory:
        root = Path(directory)
        price_root = root / "preflight"
        inputs = price_root / "inputs"
        ancestor_root = root / "lead/inputs"
        inputs.mkdir(parents=True)
        ancestor_root.mkdir(parents=True)
        for name in ("ADMITTED.json","READBACK.json","pricing.py","7334-CHANGED.json",
                     "7277-SUPPORT.json.gz","7334-WORD.json.gz"):
            copyfile(HERE / "inputs" / name, inputs / name)
        old_word = ancestor_root / "7277-WORD.json.gz"
        copyfile(HERE / "inputs/7277-WORD.json.gz", old_word)
        cohort = decompress((HERE / "inputs/7314-HELPERS.json.gz").read_bytes())
        (inputs / "7314-HELPERS.json").write_bytes(cohort)
        quote = price_root / "quote.py"
        copyfile(HERE / "engines/quote.py", quote)

        def stage(name, script, *args):
            result = run([executable, "-I", "-B", str(script), *map(str, args)], cwd=root,
                         check=True, capture_output=True, timeout=22)
            require(result.stdout == (HERE / "receipts" / name).read_bytes(), f"changed receipt {name}")
            (output / name).write_bytes(result.stdout)
            return result.stdout

        raw_price = stage("PRICE.json", quote)
        price_path = price_root / "PRICE.json"
        price_path.write_bytes(raw_price)
        forward_script = HERE / "engines/rechart_gate.py"
        raw_forward = stage("FORWARD.json", forward_script, root)
        reverse_script = HERE / "engines/reverse_geometry.py"
        raw_reverse = stage("REVERSE.json", reverse_script, "--price", price_path,
                            "--word", inputs / "7334-WORD.json.gz", "--legacy", old_word)
        raw_compare = stage("COMPARE.json", HERE / "engines/compare.py",
                             output / "FORWARD.json", output / "REVERSE.json")
        price, forward, reverse, compare = map(read, (raw_price, raw_forward, raw_reverse, raw_compare))
        require(price["head"] == forward["head"] == reverse["head"] == compare["head"] == HEAD
                and price["legacy_two_public_move_neighbors"] == 184 and price["allowed_helper_pairs"] == 48
                and len(price["alternatives"]) == 9, "changed source stock")
        require(forward["status"] == "EXHAUSTED" and reverse["timeout"] is None and not reverse["unvisited"]
                and compare["exact_key_agreements"] == compare["exact_rank_intervals_collapsed_to_old_span"] == 9
                and compare["geometry_survivors"] == compare["unresolved"] == 0, "incomplete exact geometry")
        for mutated in (price_path, old_word, inputs / "7334-WORD.json.gz"):
            original = mutated.read_bytes()
            mutated.write_bytes(original + b"\n")
            reject = run([executable, "-I", "-B", str(forward_script), str(root)], cwd=root,
                         capture_output=True, timeout=8)
            require(reject.returncode == 1 and not reject.stdout
                    and f"changed dependency {mutated.relative_to(root)}".encode() in reject.stderr,
                    f"changed dependency passed {mutated.relative_to(root)}")
            mutated.write_bytes(original)
    print("PASS_PUBLIC_FOUR_MOVE_RECHART keys=9 old_rank=4 required_rank=5 excluded=9 unresolved=0 kappa_change=0")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.out:
        replay(args.out.resolve())
    else:
        with TemporaryDirectory(prefix="public-four-move-receipts-") as directory:
            replay(Path(directory) / "out")


if __name__ == "__main__":
    main()
