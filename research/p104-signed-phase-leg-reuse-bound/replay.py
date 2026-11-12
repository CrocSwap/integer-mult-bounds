"""Replay the exact fixed-factor Type A signed reuse exclusion."""
import ast
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from itertools import combinations
from json import loads
from pathlib import Path
from runpy import run_path
from subprocess import CalledProcessError, run
from tempfile import TemporaryDirectory
import sys

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
N = 36


def unique(items):
    data = dict(items)
    if len(data) != len(items):
        raise ValueError("duplicate dependency or receipt key")
    return data


def decode(raw):
    return loads(raw,object_pairs_hook=unique)


def source(name):
    p = Path(name)
    if p.is_absolute() or ".." in p.parts or p.as_posix() != name:
        raise ValueError("invalid relative path " + name)
    return (ROOT/p).read_bytes()


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate():
    pins = decode(source("LOCAL-PINS.json"))
    for name,expected in pins.items():
        if digest(source(name)) != expected:
            raise ValueError("changed package input " + name)
    prov = decode(source("PROVENANCE.json"))
    for name,entry in prov["files"].items():
        raw = source(name)
        assert digest(raw) == entry["sha256"] == pins[name]
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest() == entry["git_blob"]
    assert decode(source("inputs/PR7362-SHA256.json"))["R92-PRICE.json"] == pins["inputs/R92-PRICE.json"]
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


def price(preflight):
    native = decode(source("inputs/NATIVE-RESULT.json"))["native"]
    base = decode(source("inputs/R92-PRICE.json"))
    assert (base["head"],base["caller_head"]) == (HEAD,CALLER)
    assert native["paid"] == preflight["per_J_old_P"]
    assert native["helpers"] == preflight["per_J_old_helper_T"]
    paid = Counter({int(r):n for r,n in native["paid"].items()})
    targets = {int(r):n for r,n in native["helpers"].items()}
    assert sum(paid.values()) == 6279 and sum(targets.values()) == 1101
    delta = paid.copy()
    delta.subtract(targets)
    delta.subtract({8:400,1:112})
    cost = run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    quote = cost(delta,Fraction(base["old_crossing_upper"]))
    assert 50 < quote[0] <= quote[1] < 51
    return list(map(str,quote))


def check_windows(a,b,labels):
    assert (a["head"],a["caller"]) == (HEAD,CALLER)
    assert not (a["capped"] or b["capped"] or a["unvisited"] or b["unresolved_keys"])
    assert len(a["records"]) == len(b["cases"]) == 153
    rank_windows = []
    for f,r in zip(a["records"],b["cases"],strict=True):
        lo,hi = f["clock_interval"]
        i,j = f["hosts"]
        assert (r["clocks"],r["first_last"]) == ([lo,hi-1],[i,j])
        assert f["rank"] == r["required_phase_rank"]
        count = sum(lo<=key[0]<hi for key in labels)
        assert count == 2*(j-i+1)+f["retained_QUERY"] == 2*(j-i+1)+r["retained_queries_per_port"]
        if (i,j) != (1,17):
            assert count == f["rank"]
            rank_windows.append((lo,hi))
        else:
            assert count == 38 and f["rank"] == 36
    assert len(rank_windows) == 152
    all_pairs = set(combinations(range(38),2))
    proper = {(a,b) for a,b in all_pairs if any(lo<=labels[a][0]<=labels[b][0]<hi for lo,hi in rank_windows)}
    assert len(proper) == 699 and all_pairs-proper == {(0,36),(0,37),(1,36),(1,37)}
    all_triples = set(combinations(range(38),3))
    exterior = {t for t in all_triples if not any(
        lo <= labels[t[0]][0] <= labels[t[-1]][0] < hi for lo,hi in rank_windows)}
    assert len(all_triples) == 8436 and len(exterior) == 140
    return exterior


def replay(stage):
    pins = authenticate()
    physical_signs()

    def copy(name,raw):
        path = stage/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(raw)

    def launch(script):
        return run([sys.executable,"-I","-B","-X",f"pycache_prefix={stage/'pycache'}",str(stage/script)],
                   check=True,capture_output=True,timeout=45).stdout

    def receipt(name,script=None):
        raw = source("receipts/"+name) if script is None else launch(script)
        assert digest(raw) == pins["receipts/"+name], name
        return decode(raw)

    for name in pins:
        if name.startswith("inputs/"):
            copy(name,source(name))
        elif name.startswith("engines/"):
            copy(Path(name).name,source(name))
    copy("PINS",source("engines/LEAD-PINS"))
    for name in ("forward.py","reverse.py"):
        copy("inputs/"+name,source("engines/"+name))
    copy("inputs/R193.json",source("receipts/R193-LEAD.json"))
    preflight = source("receipts/R193-PRICE.json")
    copy("inputs/PRICE.json",preflight)
    copy("inputs/R193-PRICE.json",preflight)
    quote = price(decode(preflight))
    old = receipt("R193-LEAD.json")
    old_independent = receipt("R193-REVERSE.json","r193_reverse.py")
    f = receipt("R194-LEAD.json","lead.py")
    r = receipt("R194-REVERSE.json","independent.py")
    assert (r["head"],r["caller"]) == (HEAD,CALLER)
    assert f["factors"] == r["factor_count"] == 38 and f["old_endpoint"] == r["old_relative_endpoint"] == "-I"
    assert f["upper_gross_with_one_saved_leg"] == r["price"] == quote
    assert not (f["survivors"] or r["survivors"]) and len(f["records"]) == len(r["pairs"]) == 4
    exterior = check_windows(old,old_independent,r["factor_labels"])
    assert [m["rank_two_minor"]["determinant"] for m in r["pairs"]] == ["4","-4","12","4"]
    for a,b in zip(f["records"],r["pairs"],strict=True):
        assert a["legs"] == [[row[0],row[3],row[4]] for row in (b["early"],b["late"])]
        assert a["rank"] == 2
        u,x = [list(map(Fraction,row)) for row in b["column_factors"]]
        v,y = [list(map(Fraction,row)) for row in b["row_factors"]]
        matrix = [[u[i]*v[j]+x[i]*y[j] for j in range(N)] for i in range(N)]
        sparse = [[i,j,str(matrix[i][j])] for j in range(N) for i in range(N) if matrix[i][j]]
        assert a["delta"] == sparse
        p = b["rank_two_minor"]
        sub = [[matrix[i][j] for j in p["columns"]] for i in p["rows"]]
        assert sub == [[Fraction(x) for x in row] for row in p["matrix"]]
        assert sub[0][0]*sub[1][1]-sub[0][1]*sub[1][0] == Fraction(p["determinant"])

    copy("inputs/R193-RESULT.json",source("receipts/R193-LEAD.json"))
    copy("inputs/R194-RESULT.json",source("receipts/R194-REVERSE.json"))
    triple_lead = receipt("R195-LEAD.json","triple_lead.py")
    copy("PINS",source("engines/TRIPLE-PINS"))
    triple_reverse = receipt("R195-REVERSE.json","triple_reverse.py")
    assert not triple_lead["survivors"] and not triple_reverse["survivors"]
    assert triple_lead["factors"] == triple_reverse["factor_count"] == 38
    assert triple_reverse["factor_labels"] == r["factor_labels"]
    assert triple_reverse["counts"] == {"3":140}
    assert {tuple(z["case"]) for z in triple_lead["records"]} == exterior
    assert len(triple_lead["records"]) == len(triple_reverse["cases"]) == 140
    for lead, independent in zip(triple_lead["records"],triple_reverse["cases"],strict=True):
        assert lead["case"] == independent["triple"]
        assert lead["keys"] == [[row[0],row[3],row[4]] for row in independent["labels"]]
        assert lead["rank"] == independent["rank"] == 3
        proof = independent["minor"]
        a,b,c = [[Fraction(x) for x in row] for row in proof["matrix"]]
        det = a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
        assert det and det == Fraction(proof["determinant"])

    copy("inputs/CALLER.json",source("inputs/CALLER.json")+b" ")
    try:
        launch("independent.py")
    except CalledProcessError as exc:
        assert exc.returncode == 1 and b"inputs/CALLER.json" in exc.stderr
    else:
        raise AssertionError("changed caller accepted")
    print("PASS_P104_SIGNED_PHASE_LEG_REUSE factors=38 pairs=703 triples=8436 endpoint_pairs=4 endpoint_triples=140 survivors=0")


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    with TemporaryDirectory() as tmp:
        replay(Path(tmp))


if __name__=="__main__":
    main()
