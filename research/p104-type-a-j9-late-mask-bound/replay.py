"""Replay exact fixed J9 Type A late-mask support and price for all roles."""
import ast
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
N, CUT, HOST = 36, 1741, 3058
ROLES = [9,0,18,27]


def unique(items):
    data = dict(items)
    if len(data) != len(items):
        raise ValueError("duplicate dependency or receipt key")
    return data


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def source(name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != name:
        raise ValueError("invalid package-relative path " + name)
    return (ROOT / path).read_bytes()


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate():
    pins = decode(source("LOCAL-PINS.json"))
    for name, expected in pins.items():
        raw = source(name)
        if digest(raw) != expected:
            raise ValueError("changed package input " + name)
        if name.endswith(".json"):
            decode(raw)
    prov = decode(source("PROVENANCE.json"))
    for name, entry in prov["files"].items():
        raw = source(name)
        assert digest(raw) == entry["sha256"] == pins[name]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == entry["git_blob"]
    assert decode(source("inputs/PR7362-SHA256.json"))["R92-PRICE.json"] == pins["inputs/R92-PRICE.json"]
    caller_pins = decode(source("inputs/7113-SHA256.json"))
    for name, entry in prov["files"].items():
        if entry["commit"] == CALLER and name != "inputs/7113-SHA256.json":
            key = entry["path"].removeprefix("research/signed-caller-8x9/")
            assert pins[name] == caller_pins[key]
    return pins


def physical_signs():
    child = ast.parse(source("inputs/7113-signed-child.py"))
    gate, = [ast.literal_eval(node.value) for node in child.body
             if isinstance(node,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id=="C" for t in node.targets)]
    for vector, expected in (((1,1),(2,0)),((1,-1),(0,2))):
        for row, sign in zip(gate,vector,strict=True):
            image = tuple(sum(a[i]*v for a,v in zip(row,vector,strict=True)) for i in range(2))
            assert image == tuple(sign*x for x in expected)
    app = source("inputs/7113-application.py").decode()
    assert "need(transform(q) == q" in app
    assert "fresh = [1 << (9+8*(stage-1)+j) for j in range(8)]" in app
    binding = decode(source("inputs/PHYSICAL-BINDING.json"))
    assert binding["caller_sha256"] == digest(source("inputs/CALLER.json"))
    assert binding["source_reviewer_sha256"] == digest(source("inputs/7113-application.py"))
    assert binding["occurrence_and_geometry"]["ambient"] == 145
    assert (1*1,1j*1j) == (1,-1)


def expand(data):
    matrix = [[Fraction(0) for _ in range(N)] for _ in range(N)]
    for i,j,value in data:
        assert not matrix[i][j] and Fraction(value)
        matrix[i][j] = Fraction(value)
    return matrix


def verify_equal_mask_control(phases):
    perm = list(range(N))
    perm[9],perm[27] = 27,9
    for phase in phases:
        n, inv = [expand(phase[k]) for k in ("n","n_inverse")]
        for i in range(N):
            for j in range(N):
                if i not in ROLES or j not in ROLES:
                    actual = sum(n[i][perm[k]]*inv[k][j] for k in range(N))
                    assert actual == (i==j)


def replay(stage, output):
    pins = authenticate()
    physical_signs()
    results = {}

    def copy(name, data):
        path = stage / name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)

    def launch(name):
        return run(
            [sys.executable,"-I","-B","-X",f"pycache_prefix={stage/'pycache'}",str(stage/name)],
            check=True,capture_output=True,timeout=32,
        ).stdout

    def record(name, script):
        raw = launch(script)
        assert digest(raw) == pins["receipts/"+name], name
        results[name] = raw
        return decode(raw)

    for name in pins:
        if name.startswith("inputs/"):
            copy(name,source(name))
        elif name.startswith("engines/"):
            copy(Path(name).name,source(name))
    copy("inputs/r178.py",source("engines/r178_reverse.py"))
    copy("inputs/r179.py",source("engines/r179_reverse.py"))
    price = record("R178-PRICE.json","r178_price.py")
    seam = record("R178-REVERSE.json","r178_reverse.py")
    assert price["head"] == seam["benchmark"] == HEAD and price["caller"] == seam["caller"] == CALLER
    assert 23 < Fraction(price["gross"][0]) <= Fraction(price["gross"][1]) < 24
    for name in ("R178-PRICE.json","R178-REVERSE.json"):
        copy("inputs/"+name,results[name])

    a = record("R189-FORWARD.json","r189_forward.py")
    b = record("R189-REVERSE.json","r189_reverse.py")
    assert (a["cut"],a["host_clock"],a["host_roles"]) == (CUT,HOST,ROLES)
    assert (b["cut"],b["host"],b["host_roles"]) == (CUT,HOST,ROLES)
    assert a["excluded"] and b["status"] == "excluded by exact support"
    assert [s["outside_nonzeros"] for s in a["signs"]] == [s["outside_nonzeros"] for s in b["cases"]] == [16,8]
    assert [s["first_outside"][0] for s in a["signs"]] == [s["first_outside"] for s in b["cases"]] == [[10,0,"4"],[0,10,"-2"]]
    for lhs,rhs in zip(a["signs"],b["cases"],strict=True):
        assert lhs["first_outside"] == rhs["outside"][:12]
    assert a["unit_middle_masks"] == [r[2] for r in b["middle_idles"]]
    copy("inputs/R189.json",results["R189-REVERSE.json"])

    f = record("R190-FORWARD.json","r190_forward.py")
    r = record("R190-REVERSE.json","r190_reverse.py")
    assert all((x["head"],x["caller"])==(HEAD,CALLER) for x in (a,b,f,r))
    assert f["classes"] == [g["roles"] for g in r["classes"]]
    assert f["class_counts"] == [g["early_late"] for g in r["classes"]]
    assert len(f["classes"]) == 35 and [g for g in f["classes"] if len(g)>1] == [[9,27]]
    assert sorted(i for g in f["classes"] for i in g) == list(range(N))
    assert f["assignment_examined"] == r["optimum"]
    assert f["productive_delta"] == r["delta"] == {}
    assert f["gross_upper"] == r["signed_gain_interval"] == ["0","0"]
    assert f["tested_permutations"] == r["enumerated_permutations"] == 0
    assert r["old_histogram"] == r["maximum_histogram"] and f["unresolved_within_scope"] == 0
    diagonal = decode(source("inputs/CALLER.json"))["types"]["A"]["diagonal"]
    assert diagonal[9] == diagonal[27] and diagonal[9][:2] == [-1,0]
    assert [stage for stage,flag in enumerate(diagonal[9][2:],1) if flag] == [9]
    verify_equal_mask_control(r["phases"])

    copy("inputs/R178-REVERSE.json",results["R178-REVERSE.json"]+b" ")
    try:
        launch("r189_reverse.py")
    except CalledProcessError as exc:
        assert exc.returncode==1 and b"inputs/R178-REVERSE.json" in exc.stderr
    else:
        raise AssertionError("corrupted predecessor accepted")
    if output is not None:
        output.mkdir(parents=True)
        for name,raw in results.items():
            (output/name).write_bytes(raw)
    print("PASS_P104_J9_LATE_MASK_BOUND roles=36 classes=35 nontrivial_equal_masks=1 gross=0 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("--out",type=Path)
    args = cli.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
