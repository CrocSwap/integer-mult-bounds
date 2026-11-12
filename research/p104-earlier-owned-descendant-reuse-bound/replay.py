"""Regenerate the descendant prices, span certificates and full-rank minor."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from shutil import copyfile
from subprocess import PIPE, run
from sys import executable, implementation, version_info
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
STAGES = ("price", "lead", "independent")


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def execute(path):
    return run([executable, "-I", "-B", str(path)], cwd=path.parent,
               stdout=PIPE, stderr=PIPE, timeout=35)


def determinant(matrix):
    if len(matrix) == 1:
        return matrix[0][0]
    return sum((-1)**j * value * determinant([row[:j] + row[j+1:] for row in matrix[1:]])
               for j,value in enumerate(matrix[0]) if value)


def verify_full_rank(pivots):
    raw = decompress((ROOT / "inputs/7334-WORD.json.gz").read_bytes())
    assert sha256(raw).hexdigest() == "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    initial = read(raw)["initial"]
    rows = read((ROOT / "inputs/R198.json").read_bytes())["records"]
    assert len(rows) == len(pivots) == 8
    assert len(set(pivots)) == 8 and all(initial[j] != 3 for j in pivots)
    minor = [[4*Fraction(row["row"].get(str(j), "0")) for j in pivots] for row in rows]
    assert all(value.denominator == 1 for row in minor for value in row)
    assert determinant([[int(value) for value in row] for row in minor]) == 2


def corrupt_source_control():
    with TemporaryDirectory(prefix="p104-descendant-negative-") as folder:
        root = Path(folder)
        (root / "engines").mkdir()
        (root / "inputs").mkdir()
        for source in (ROOT / "inputs").iterdir():
            copyfile(source, root / "inputs" / source.name)
        changed = root / "inputs/R198.json"
        source = read(changed.read_bytes())
        row = source["records"][0]["row"]
        assert row["4"] == "1/4"
        row["4"] = "0"
        changed.write_text(dumps(source))
        engine = root / "engines/independent.py"
        copyfile(ROOT / "engines/independent.py", engine)
        negative = execute(engine)
        assert negative.returncode == 1 and not negative.stdout
        assert b"AssertionError: inputs/R198.json" in negative.stderr


def compare(results):
    price,lead,other = (results[stage] for stage in STAGES)
    assert not other["capped"] and other["unvisited"] == []
    assert len(price["cases"]) == other["examined"] == lead["all_subsets"] == 247
    assert price["positive_count"] == lead["tested_price_positive"] == other["price_admitted"] == 64
    assert lead["whole_exterior_rank"] == 8 and lead["survivors"] == other["survivors"] == []
    for a,b in zip(price["cases"],other["cases"],strict=True):
        assert price["keys"][a["target"]] == b["target"]
        assert [price["keys"][i][0] for i in a["donors"]] == b["donors"]
        assert a["new_rank1"] == b["paid_rank_one_per_copy"]
        assert a["gross"] == b["directed_gross"]
        assert a["price_positive"] == (b["certificate"] is not None)
    for a,b in zip(lead["records"],[row for row in other["cases"] if row["certificate"]],strict=True):
        assert price["keys"][a["target"]] == b["target"]
        assert [price["keys"][i][0] for i in a["donors"]] == b["donors"]
        assert not a["survives"] and b["certificate"]["status"] == "outside span"
        assert a["donor_rank"] == b["certificate"]["rank"]
        assert Fraction(a["first_residual"][1]) == Fraction(b["certificate"]["target_value"])
    verify_full_rank(lead["pivots"])


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3,12)
    pins = read((ROOT / "LOCAL-PINS.json").read_bytes())
    for name, digest in sorted(pins.items()):
        path = (ROOT / name).resolve()
        assert path.is_relative_to(ROOT) and sha256(path.read_bytes()).hexdigest() == digest, name
    stock = read((ROOT / "inputs/PR7362-SHA256.json").read_bytes())
    assert stock["R92-PRICE.json"] == pins["inputs/R92-PRICE.json"]
    results = {}
    for stage in STAGES:
        result = execute(ROOT / "engines" / f"{stage}.py")
        assert result.returncode == 0, (stage, result.stderr.decode())
        assert result.stdout == (ROOT / "receipts" / f"{stage.upper()}.json").read_bytes(), stage
        results[stage] = read(result.stdout)
    compare(results)
    corrupt_source_control()
    print('{"subsets":247,"price_admitted":64,"certified_exclusions":64,"exterior_rank":8,'
          '"minor_determinant":"1/32768","unresolved":0,"corrupted_row_rejected":true,"kappa_delta":"0"}')
    print("PASS_P104_EARLIER_OWNED_DESCENDANT_REUSE_BOUND")


if __name__ == "__main__":
    main()
