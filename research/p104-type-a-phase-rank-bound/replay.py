"""Replay the fixed-layout and rank-two Type A provider exclusions."""
import gzip
from fractions import Fraction
from hashlib import sha1, sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def authenticate(scratch):
    pins = read(HERE / "LOCAL-PINS.json")
    for key, digest in pins.items():
        rel = PurePosixPath(key)
        if rel.is_absolute() or ".." in rel.parts or rel.as_posix() != key:
            raise ValueError(f"invalid dependency path {key}")
        if sha256((HERE / key).read_bytes()).hexdigest() != digest:
            raise ValueError(f"changed dependency {key}")
    deps = scratch / "dependencies"
    shutil.copytree(HERE / "dependencies", deps)
    for key, pin in read(HERE / "PROVENANCE.json")["files"].items():
        assert key in pins
        raw = (HERE / key).read_bytes()
        if pin["uncompress"]:
            raw = gzip.decompress(raw)
            (scratch / key).with_suffix("").write_bytes(raw)
        assert sha256(raw).hexdigest() == pin["sha256"], key
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == pin["git_blob"], key
    return deps


def run(script, *args):
    subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, args)], check=True)


def match(actual, expected):
    assert actual.read_bytes() == expected.read_bytes(), expected


def det3(rows):
    (a,b,c), (d,e,f), (g,h,i) = rows
    return a*(e*i-f*h) - b*(d*i-f*g) + c*(d*h-e*g)


def crosscheck(caller, fixed, rational, modular):
    def key(row):
        return row["query_clock"], row["j_clock"]

    old = {key(row): row for row in fixed["rows"]}
    exact = {key(row): row for row in rational["records"]}
    residue = {(row["query"], row["host"]): row for row in modular["rows"]}
    assert len(old) == len(exact) == len(residue) == 68
    assert old.keys() == exact.keys() == residue.keys()
    assert fixed["status"] == "all_alternatives_excluded" and not fixed["unvisited"]
    assert rational["counts"] == {"3":68} and not rational["unvisited"]
    assert not rational["admissible_cases"] and modular["excluded"] == 68 and not modular["unresolved"]
    prime = modular["prime"]

    def mod(x):
        return x.numerator * pow(x.denominator, -1, prime) % prime

    alpha = Fraction(caller["types"]["A"]["alpha2"])
    for pair, row in exact.items():
        cert = residue[pair]["rank_three_witness"]
        host = caller["events"][pair[1]]
        assert host[0] == "J" and row["stage"] == residue[pair]["stage"] == host[1]
        u,v,x,y = host[2]
        initial = {(v,u): -2, (x,y): -2*alpha}
        left = {int(k): Fraction(z) for k,z in row["update_column"].items()}
        right = {int(k): Fraction(z) for k,z in row["update_row"].items()}

        def entry(i,j):
            return Fraction(initial.get((i,j),0))-2*left.get(i,0)*right.get(j,0)

        minor = [[entry(i,j) for j in cert["columns"]] for i in cert["rows"]]
        assert [[mod(z) for z in r] for r in minor] == cert["minor"]
        assert mod(det3(minor)) == cert["determinant_residue"] != 0
        exact_minor = [[entry(i,j) for j in row["pivot_columns"]] for i in row["pivot_rows"]]
        assert [[str(z) for z in r] for r in exact_minor] == row["minor_entries"]
        assert det3(exact_minor) == Fraction(row["exact_minor"]) != 0


def replay():
    with TemporaryDirectory(prefix="type-a-query-provider-") as temp:
        scratch = Path(temp)
        deps = authenticate(scratch)
        r30, r45 = deps / "round30", deps / "round45"
        caller = r30 / "complex/source/inputs/CALLER.json"
        lead = r45 / "lead"
        fixed, exact, modular = (scratch / d for d in ("fixed", "exact", "modular"))
        run(lead / "screen.py", r30, fixed, "--cap", 68, "--seconds", 45)
        for name in ("PRICE.json", "SUPPORT.json"):
            match(fixed / name, lead / "run" / name)
        run(HERE / "engines/exact_rank.py", r30, r45, exact, "--seconds", 30)
        match(exact / "RESULT.json", HERE / "receipts/exact/RESULT.json")
        shutil.copyfile(caller, r45 / "CALLER.json")
        shutil.copyfile(fixed / "PRICE.json", r45 / "PRICE.json")
        run(HERE / "engines/minor.py", deps, modular, "--seconds", 60)
        for name in ("PRICE.json", "SUPPORT.json"):
            match(modular / name, HERE / "receipts/modular" / name)
        assert read(modular / "PRICE.json")["optimistic_saving_upper_per_alternative"] == "96"
        crosscheck(read(caller), read(fixed / "SUPPORT.json"), read(exact / "RESULT.json"),
                   read(modular / "SUPPORT.json"))
        print("PASS_TYPE_A_QUERY_PROVIDER alternatives=68 fixed_layout_excluded=68 rank_three=68 unresolved=0 saving_upper=0 kappa_change=0")


if __name__ == "__main__":
    assert __debug__, "run with assertions enabled"
    assert sys.version_info[:2] == (3,12), "Python 3.12 required"
    replay()
