"""Replay the directed price and both exact retimed-ascent occupancy walks."""

from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha1, sha256
from json import loads
from pathlib import Path, PurePosixPath
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"


def unique(pairs):
    result = dict(pairs)
    if len(pairs) != len(result):
        raise ValueError("duplicate JSON key")
    return result


def decode(data):
    return loads(data, object_pairs_hook=unique)


def digest(data):
    return sha256(data).hexdigest()


def relative(name):
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or ".." in path.parts:
        raise ValueError(f"invalid replay path: {name}")
    return path


def authenticate():
    pins = decode((ROOT / "LOCAL-PINS.json").read_bytes())
    for name, expected in pins.items():
        if digest((ROOT / relative(name)).read_bytes()) != expected:
            raise ValueError(f"changed package dependency: {name}")
    provenance = decode((ROOT / "PROVENANCE.json").read_bytes())
    for name, record in provenance["files"].items():
        raw = (ROOT / relative(name)).read_bytes()
        assert digest(raw) == record["sha256"] == pins[name]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == record["git_blob"]
    predecessor = decode((ROOT / "inputs/PR7362-SHA256.json").read_bytes())
    inputs = {}
    for key in ("R92-PRICE.json", "R92-GEOMETRY.json"):
        content = decompress((ROOT / f"inputs/{key}.gz").read_bytes())
        assert digest(content) == predecessor[key]
        inputs[key] = content
    return inputs


def command(script, *args, check=True):
    result = run([sys.executable, "-I", "-B", str(script), *map(str, args)],
                 capture_output=True, timeout=25)
    if check and result.returncode:
        sys.stderr.write(result.stderr.decode(errors="replace"))
        result.check_returncode()
    return result


def replay(scratch, out):
    inputs = authenticate()
    expected = decode((ROOT / "receipts/SHA256.json").read_bytes())
    for path in ("inputs", "lead", "independent/inputs"):
        (scratch / path).mkdir(parents=True)
    for path in ("lead/quote.py", "lead/geometry.py", "independent/reverse_windows.py", "independent/compare.py",
                 "inputs/7334-WORD.json.gz", "inputs/BENCHMARK.json"):
        copyfile(ROOT / path, scratch / path)
    for name, raw in inputs.items():
        (scratch / "inputs" / name).write_bytes(raw)
    for source, dest in (("R92-PRICE.json", "R92-PRICE.json"), ("R92-GEOMETRY.json", "GEOMETRY.json"),
                         ("7334-WORD.json.gz", "7334-WORD.json.gz")):
        copyfile(scratch / "inputs" / source, scratch / "independent/inputs" / dest)

    receipts = {}

    def record(name, path, result):
        raw = result.stdout
        assert digest(raw) == expected[name], ("changed receipt", name)
        path.write_bytes(raw)
        receipts[name] = raw
        return decode(raw)

    price_path = scratch / "lead/PRICE.json"
    price = record("R98-PRICE.json", price_path, command(scratch / "lead/quote.py"))
    assert price["head"] == HEAD and price["distinct_optimistic_cap"] == 31
    assert price["all_anchor_moves"] == 95 and price["all_quotient_lines"] == 285
    assert Fraction(price["whole_net_upper"]) == 31 * Fraction(price["one_net_upper"])
    assert Fraction(price["whole_moonshot_margin_upper"]) < 0
    assert Fraction(price["extra_rank_one_upper"]) < 0
    assert all(Fraction(row["full_probe"][0]) > 0 for row in price["quotes"])

    forward_script = scratch / "lead/geometry.py"
    forward = record("R98-FORWARD.json", scratch / "lead/GEOMETRY.json", command(forward_script))
    assert forward["stage"] == "complete" and forward["first_unvisited_event"] is None and not forward["timeout"]
    assert forward["eligible_raw_cuts"] == 0 and not forward["representatives"]

    reverse_script = scratch / "independent/reverse_windows.py"
    price_args = ("--price", price_path, "--price-sha256", expected["R98-PRICE.json"])
    reverse = record("R98-REVERSE.json", scratch / "independent/RESULT.json", command(reverse_script, *price_args))
    assert reverse["complete"] and not reverse["raw_unvisited_intervals"] and not reverse["selected"]
    assert reverse["counts"] == {"missing_pivot": 62}
    assert reverse["raw_counts"] == {"missing_pivot": 29641}

    comparison = record("R98-AGREEMENT.json", scratch / "AGREEMENT.json",
                        command(scratch / "independent/compare.py", scratch))
    assert comparison["complete"] and comparison["agree"] == 31
    assert comparison["raw_empty_cuts"] == 29641 and comparison["remaining"] == comparison["eligible"] == 0
    assert receipts["R98-AGREEMENT.json"] == (ROOT / "receipts/R98-AGREEMENT.json").read_bytes()

    price_path.write_bytes(price_path.read_bytes() + b"\n")
    mutated_price = command(reverse_script, *price_args, check=False)
    assert mutated_price.returncode == 1 and not mutated_price.stdout
    assert b"changed dependency: PRICE.json" in mutated_price.stderr
    price_path.write_bytes(receipts["R98-PRICE.json"])

    word = scratch / "inputs/7334-WORD.json.gz"
    word.write_bytes(word.read_bytes() + b"\n")
    mutated_word = command(forward_script, check=False)
    assert mutated_word.returncode == 1 and not mutated_word.stdout
    assert b"changed dependency inputs/7334-WORD.json.gz" in mutated_word.stderr

    assert set(receipts) == set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name, raw in receipts.items():
            (out / relative(name)).write_bytes(raw)
    print("PASS_RETIMED_PAID_RANK_TWO_EMPTY_BANKS labels=31 cuts=29641 blocks=62 eligible=0 unresolved=0")


def main():
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="new directory for all four regenerated receipts")
    args = parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp), args.out)


if __name__ == "__main__":
    main()
