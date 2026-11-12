"""Replay the exact public-donor exclusion on one P104 role-532 contraction."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha1, sha256
from json import loads
from pathlib import Path, PurePosixPath
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def relative(name):
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or ".." in path.parts:
        raise ValueError(f"invalid relative path {name}")
    return path


def authenticate():
    pins = decode((ROOT / "LOCAL-PINS.json").read_bytes())
    for name, expected in pins.items():
        if digest((ROOT / relative(name)).read_bytes()) != expected:
            raise ValueError(f"changed package dependency {name}")
    source = decode((ROOT / "PROVENANCE.json").read_bytes())
    for name, record in source["files"].items():
        raw = (ROOT / relative(name)).read_bytes()
        assert digest(raw) == record["sha256"] == pins[name]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == record["git_blob"]
    predecessor = decode((ROOT / "inputs/PR7383-SHA256.json").read_bytes())
    assert predecessor["PRICE.json"] == pins["inputs/R130-PRICE.json"]


def command(root, script, *args, check=True):
    result = run([sys.executable, "-I", "-B", str(root / script), *args],
                 capture_output=True, timeout=22)
    if check and result.returncode:
        sys.stderr.write(result.stderr.decode(errors="replace"))
        result.check_returncode()
    return result


def reject(root, name, script, *args):
    path = root / relative(name)
    raw = path.read_bytes()
    path.write_bytes(raw + b"\n")
    result = command(root, script, *args, check=False)
    assert result.returncode == 1 and not result.stdout
    assert b"changed dependency" in result.stderr and path.name.encode() in result.stderr
    path.write_bytes(raw)


def replay(root, out):
    authenticate()
    expected = decode((ROOT / "receipts/SHA256.json").read_bytes())
    outputs = {}
    for folder in ("lead", "inputs", "independent/inputs"):
        (root / folder).mkdir(parents=True)
    for name in ("7334-WORD.json.gz", "R130-PRICE.json", "donor_span.py"):
        copyfile(ROOT / "inputs" / name, root / "inputs" / name)
    copyfile(ROOT / "engines/aggregate.py", root / "lead/aggregate.py")
    independent = root / "independent"
    for name in ("reverse_aggregate.py", "compare.py"):
        copyfile(ROOT / "engines" / name, independent / name)
    for name in ("7334-WORD.json.gz", "PLAN.md"):
        copyfile(ROOT / "inputs" / name, independent / "inputs" / name)
    copyfile(ROOT / "inputs/R130-PRICE.json", independent / "inputs/PRICE.json")

    def record(name, work, script, *args, target=None):
        raw = command(work, script, *args).stdout
        assert digest(raw) == expected[name], ("changed receipt", name)
        outputs[name] = raw
        if target is not None:
            (work / target).write_bytes(raw)
        return decode(raw)

    price = record("PRICE.json", root, "lead/aggregate.py", "--price-only")
    lead = record("LEAD.json", root, "lead/aggregate.py")
    (independent / "inputs/R131-PRICE.json").write_bytes(outputs["PRICE.json"])
    (independent / "inputs/R131-LEAD.json").write_bytes(outputs["LEAD.json"])
    backward = record("INDEPENDENT.json", independent, "reverse_aggregate.py", target="RESULT.json")
    agree = record("AGREEMENT.json", independent, "compare.py")
    assert outputs["AGREEMENT.json"] == (ROOT / "receipts/AGREEMENT.json").read_bytes()
    assert price["head"] == lead["head"] == backward["head"] == HEAD
    assert price["caller"] == lead["caller"] == backward["caller"] == CALLER
    assert price["candidate"]["old_ranks"] == [3,3,2] and price["candidate"]["new_rank"] == 8
    assert price["candidate"]["paid_delta"] == {"2":-17,"3":-34,"8":17}
    assert (price["paid"], price["productive"], price["surplus"]) == (110485,22461,1424)
    assert Fraction(price["candidate"]["probe_lower"]) > 0
    assert Fraction(price["candidate"]["raw_upper"]) <= Fraction("0.53373482346222227") < 1
    assert agree["aggregate_coordinates"] == 26 and agree["unresolved_in_scope"] == 0
    assert [len(r["public"]) for r in agree["banks"]] == [8,9]
    assert [r["owned_excluded"] for r in agree["banks"]] == [[],[1567]]
    assert all(r["common_separator"] == {"27":"1"} and r["value"] == "1" for r in agree["banks"])
    reject(root, "inputs/R130-PRICE.json", "lead/aggregate.py", "--price-only")
    (independent / "inputs/7334-WORD.json.gz").unlink()
    reject(independent, "inputs/PLAN.md", "reverse_aggregate.py")

    assert set(outputs) == set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name, raw in outputs.items():
            (out / relative(name)).write_bytes(raw)
    print("PASS_P104_PUBLIC_AGGREGATE_BOUND role=532 banks=2 coordinates=26 separator=27 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="new directory for four regenerated receipts")
    args = parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp), args.out)


if __name__ == "__main__":
    main()
