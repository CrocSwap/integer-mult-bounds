"""Replay the coordinate and even-basis rank-137 root exclusions."""
from argparse import ArgumentParser
from collections import Counter
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ENGINE = HERE / "engines"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def load(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def authenticate(scratch):
    pins = load(HERE / "LOCAL-PINS.json")
    for name, digest in pins.items():
        rel = PurePosixPath(name)
        if rel.is_absolute() or ".." in rel.parts or rel.as_posix() != name:
            raise ValueError(f"invalid dependency path {name}")
        if sha256((HERE / rel).read_bytes()).hexdigest() != digest:
            raise ValueError(f"changed dependency {name}")
    shutil.copytree(HERE / "dependencies", scratch / "dependencies")
    provenance = load(HERE / "PROVENANCE.json")["files"]
    assert len(provenance) == 9
    for name, pin in provenance.items():
        assert name in pins
        raw = (HERE / name).read_bytes()
        if pin["uncompress"]:
            raw = gzip.decompress(raw)
            (scratch / name).with_suffix("").write_bytes(raw)
        assert sha256(raw).hexdigest() == pin["sha256"], name
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest() == pin["git_blob"], name


def invoke(name, *args, check=True):
    argv = [sys.executable, "-I", "-B", str(ENGINE / name), *map(str,args)]
    return subprocess.run(argv, check=check, capture_output=True)


def coordinate_compare(forward, reverse):
    def key(r):
        return r["root"], r["boundary"], r["slot"]

    by_key = {key(r):r for r in forward["rows"]}
    assert len(by_key) == len(forward["rows"]) == len(reverse["records"]) == 241
    assert by_key.keys() == {key(r) for r in reverse["records"]}
    for row in reverse["records"]:
        other = by_key[key(row)]
        if row["decision"] == "not_monomial":
            assert other["status"] == "isolated_not_monomial" and row["terms"] == other["isolated_terms"] == 2
        else:
            assert row["decision"] == other["status"] == "zero_rank_side"
            assert row["phase"] == other["phase"]
            assert sum(z << (8*j) for j,z in enumerate(row["body"])) == other["degree"]
    return dict(exact_dispositions_match=True, cases=len(by_key),
                status=dict(Counter(r["status"] for r in by_key.values())))


def replay(scratch, emit):
    authenticate(scratch)
    expected = load(HERE / "receipts/SHA256.json")
    generated = {}

    def record(label, source):
        raw = source.read_bytes() if isinstance(source,Path) else source
        assert sha256(raw).hexdigest() == expected[label], label
        generated[label] = raw
        return json.loads(raw, object_pairs_hook=unique)

    deps = scratch / "dependencies"
    caller = deps / "round30/complex/source/inputs/CALLER.json"
    base = scratch / "r54"
    coordinate = base / "lead/run"
    coordinate.parent.mkdir(parents=True)
    invoke("coordinate.py", deps, coordinate, "--seconds", 30)
    price54 = record("r54-price.json", coordinate / "PRICE.json")
    body = record("r54-body-one.json", coordinate / "BODY1.json")
    assert price54["ordered_factorizations_per_root"] == 262142
    assert not price54["paid_delta"] and len(price54["stage_partition_classes"]) == 34
    assert body["root_cases_visited"] == 9568 and body["unresolved_boundary_interval"] is None
    assert body["counts"]["interior_support_only"] == 241

    (deps / "r54").mkdir()
    for name in ("PRICE.json","BODY1.json"):
        shutil.copyfile(coordinate / name, deps / "r54" / name)
    shutil.copyfile(caller, deps / "7113/CALLER.json")
    laurent = scratch / "laurent"
    invoke("laurent.py", deps, laurent, "--seconds", 90)
    forward54 = record("r54-laurent.json", laurent / "RESULT.json")
    assert forward54["full_old_endpoint_checked"] and forward54["exhausted"]
    assert not forward54["unresolved"] and not forward54["witnessed"]

    independently = base / "independent"
    independently.mkdir()
    shutil.copyfile(ENGINE / "reverse.py", independently / "reverse.py")
    reverse_raw = invoke("reverse.py", caller, coordinate / "BODY1.json",
                         "--body-one-sha", expected["r54-body-one.json"]).stdout
    reverse54 = record("r54-reverse.json", reverse_raw)
    (independently / "RESULT.json").write_bytes(reverse_raw)
    assert reverse54["endpoints_recovered"] == 2 and not reverse54["positive_column_only"]
    match54 = coordinate_compare(forward54,reverse54)
    record("r54-compare.json", (json.dumps(match54,sort_keys=True)+"\n").encode())
    assert match54["status"] == {"isolated_not_monomial":22,"zero_rank_side":219}

    lead55 = scratch / "r55-reverse"
    invoke("column_reverse.py", "--caller", caller, "--r54", base, "--out", lead55, "--seconds", 42)
    record("r55-price.json", lead55 / "PRICE.json")
    reverse55 = record("r55-reverse.json", lead55 / "SUPPORT.json")
    assert reverse55["initial_endpoints_recovered"] == [0,18]
    assert reverse55["cases_visited"] == 9568 and not reverse55["unvisited"] and not reverse55["survivors"]

    fdeps = scratch / "forward-inputs"
    fdeps.mkdir()
    shutil.copyfile(caller, fdeps / "CALLER.json")
    shutil.copyfile(deps / "7113/check_odd_caller_exact_grid.py", fdeps / "check_odd_caller_exact_grid.py")
    shutil.copyfile(ENGINE / "laurent.py", fdeps / "forward_engine.py")
    forward55 = scratch / "r55-forward.json"
    invoke("column_forward.py", fdeps, forward55, "--seconds", 45)
    observed = record("r55-forward.json", forward55)
    assert observed["roots_final_endpoints_checked"] == [0,18]
    match55 = record("r55-compare.json",
                     invoke("compare_columns.py", forward55, lead55 / "SUPPORT.json").stdout)
    assert match55["matched_case_keys"] == 9568 and match55["counts"] == {
        "mixed_body_exponents":8383,"mixed_central_parity":913,"zero_rank_side":272}

    # Input mutations are confined to the disposable scratch closure.
    altered = deps / "r54/BODY1.json"
    altered.write_bytes(altered.read_bytes()+b"\n")
    bad = scratch / "bad-coordinate"
    failed = invoke("laurent.py", deps, bad, "--seconds", 10, check=False)
    assert failed.returncode == 1 and b"changed dependency" in failed.stderr
    assert not (bad / "RESULT.json").exists()
    altered = fdeps / "CALLER.json"
    altered.write_bytes(altered.read_bytes()+b"\n")
    bad = scratch / "bad-column.json"
    failed = invoke("column_forward.py", fdeps, bad, "--seconds", 10, check=False)
    assert failed.returncode == 1 and b"changed input" in failed.stderr and not bad.exists()

    assert generated.keys() == expected.keys()
    if emit is not None:
        emit.mkdir()
        for label, raw in generated.items():
            (emit / label).write_bytes(raw)
    print("PASS_TYPE_A_RANK137_ROOT_BOUND coordinate_cases=9568 exact_coordinate_cases=241 "
          "even_basis_cases=9568 matched=9568 unresolved=0 saving_upper=0 kappa_change=0")


if __name__ == "__main__":
    assert __debug__, "assertions are required"
    assert sys.version_info[:2] == (3,12), "Python 3.12 required"
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="p104-rank137-root-") as temp:
        replay(Path(temp),args.out)
