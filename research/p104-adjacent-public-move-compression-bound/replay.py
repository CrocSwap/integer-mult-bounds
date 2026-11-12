"""Price and independently verify all adjacent public same-chart MOVE pairs."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha1, sha256
from json import loads
from pathlib import Path
from subprocess import CalledProcessError, run
from tempfile import TemporaryDirectory
import sys

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError("duplicate dependency or receipt key")
    return out


def decode(data):
    return loads(data, object_pairs_hook=unique)


def source(name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != name:
        raise ValueError("invalid relative path " + name)
    return (ROOT / path).read_bytes()


def digest(raw):
    return sha256(raw).hexdigest()


def verify_minor(rows, coordinates, matrix, claimed):
    block = [[Fraction(row.get(str(i), 0)) for i in coordinates] for row in rows]
    assert block == [[Fraction(x) for x in row] for row in matrix]
    actual = block[0][0]*block[1][1]-block[0][1]*block[1][0]
    assert actual == Fraction(claimed) and actual


def replay(stage, out_dir):
    pins = decode(source("LOCAL-PINS.json"))
    for path, expected in pins.items():
        if digest(source(path)) != expected:
            raise ValueError("changed package input " + path)
    provenance = decode(source("PROVENANCE.json"))
    for path, entry in provenance["files"].items():
        raw = source(path)
        assert digest(raw) == entry["sha256"] == pins[path]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == entry["git_blob"]
    assert decode(source("inputs/PR7362-SHA256.json"))["R92-PRICE.json"] == pins["inputs/R92-PRICE.json"]
    results = {}

    def copy(path, data):
        dst = stage / path
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)

    def launch(path):
        return run(
            [sys.executable, "-I", "-B", "-X", f"pycache_prefix={stage / 'pycache'}", str(stage / path)],
            check=True, capture_output=True, timeout=35,
        ).stdout

    def record(name, data):
        assert digest(data) == pins["receipts/" + name], name
        results[name] = data
        return decode(data)

    for sub in ("pricing", "forward", "reverse"):
        for path in pins:
            if path.startswith("inputs/"):
                copy(f"{sub}/{path}", source(path))
    engines = {
        "pricing/price.py": "engines/price.py",
        "forward/r185.py": "engines/r185_forward.py",
        "forward/r186.py": "engines/r186_forward.py",
        "reverse/r185.py": "engines/r185_reverse.py",
        "reverse/r186.py": "engines/r186_reverse.py",
        "reverse/inputs/r185.py": "engines/r185_reverse.py",
    }
    for path, name in engines.items():
        copy(path, source(name))
    price = record("PRICE.json", launch("pricing/price.py"))
    assert (price["head"], price["caller"]) == (HEAD, CALLER)
    assert price["literal_pair_count"] == 29 and price["candidate"] == [32944,625,624,3,117,5]
    assert price["distinct_pair_ranks"] == {"1":7,"3":4,"4":1,"5":17}
    assert Fraction(price["relaxed_whole_gross_upper_interval"][1]) < 1827
    assert Fraction(price["complete_margin_at_probe"][0]) > 0
    for sub in ("forward","reverse"):
        copy(sub + "/inputs/PRICE.json", results["PRICE.json"])

    a = record("R185-FORWARD.json", launch("forward/r185.py"))
    b = record("R185-REVERSE.json", launch("reverse/r185.py"))
    assert [a["first_row"],a["second_row"]] == b["rows"]
    assert a["minor"]["determinant"] == b["decision"]["determinant"] == "-1"
    copy("forward/inputs/R185.json", results["R185-FORWARD.json"])
    copy("reverse/inputs/R185.json", results["R185-REVERSE.json"])
    f = record("R186-FORWARD.json", launch("forward/r186.py"))
    r = record("R186-REVERSE.json", launch("reverse/r186.py"))
    assert all((x["head"],x["caller"]) == (HEAD,CALLER) for x in (a,b,f,r))
    assert not (f["capped"] or r["capped"] or f["unresolved"] or r["unresolved"] or f["unvisited"])
    assert len(f["records"]) == len(r["resolved"]) == 29
    assert r["statistics"] == {"excluded nonzero minor":29}
    for key, x, y in zip(price["pairs"],f["records"],r["resolved"],strict=True):
        assert x["key"] == y["key"] == key and not y["orientation_swapped"]
        rows = [x["left_row"],x["right_row"]]
        assert rows == [y["donor_row"],y["target_row"]]
        p, q = x["minor"],y["decision"]
        verify_minor(rows,p["source_coordinates"],p["matrix"],p["determinant"])
        verify_minor(rows,q["coordinates"],q["submatrix"],q["determinant"])
        values = [sum(Fraction(v)*Fraction(row.get(j,0)) for j,v in q["probe"].items()) for row in rows]
        assert values == [0,Fraction(q["target_value"])] and values[1]

    copy("reverse/inputs/R185.json", results["R185-REVERSE.json"] + b" ")
    try:
        launch("reverse/r186.py")
    except CalledProcessError as exc:
        assert exc.returncode == 1 and b"inputs/R185.json" in exc.stderr
    else:
        raise AssertionError("altered predecessor receipt accepted")
    if out_dir is not None:
        out_dir.mkdir(parents=True)
        for name,data in results.items():
            (out_dir / name).write_bytes(data)
    print("PASS_P104_ADJACENT_PUBLIC_MOVE_COMPRESSION pairs=29 exact_rows=58 nonzero_minors=29 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__ == "__main__":
    main()
