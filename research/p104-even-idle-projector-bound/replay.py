"""Replay both even-idle pair stocks and their exact rational controls."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
CALLER = "round30/complex/source/inputs/CALLER.json"
HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def read(path):
    return json.loads(path.read_bytes(),object_pairs_hook=unique)


def authenticate(scratch):
    pins = read(HERE / "LOCAL-PINS.json")
    for key, expected in pins.items():
        rel = PurePosixPath(key)
        if rel.is_absolute() or ".." in rel.parts or rel.as_posix() != key:
            raise ValueError(f"invalid dependency path {key}")
        if sha256((HERE / key).read_bytes()).hexdigest() != expected:
            raise ValueError(f"changed dependency {key}")
    deps = scratch / "dependencies"
    shutil.copytree(HERE / "dependencies",deps)
    provenance = read(HERE / "PROVENANCE.json")["files"]
    assert len(provenance) == 7 and sum(p["uncompress"] for p in provenance.values()) == 2
    for key,pin in provenance.items():
        assert key in pins
        raw = (HERE / key).read_bytes()
        if pin["uncompress"]:
            raw = gzip.decompress(raw)
            (scratch / key).with_suffix("").write_bytes(raw)
        assert sha256(raw).hexdigest() == pin["sha256"], key
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest() == pin["git_blob"], key
    return deps


def run(script,*args):
    done = subprocess.run([sys.executable,"-I","-B",str(script),*map(str,args)],
                          capture_output=True,check=True,timeout=25)
    return done.stdout


def check_receipts(files,pins):
    for key,path in files.items():
        if sha256(path.read_bytes()).hexdigest() != pins[key]:
            raise ValueError(f"replay receipt changed: {key}")


def crosscheck(files,pins):
    summary = read(HERE / "receipts/SUMMARY.json")
    assert summary["head"] == HEAD and summary["caller_head"] == CALLER_HEAD
    assert summary["copies"] == 17 and summary["type_b_ports"] == 8
    assert summary["unresolved"] == 0 and summary["compatible_saving_after_support"] == "0"
    assert summary["kappa_change"] == "0"
    results = {}
    for scope,count in (("singleton",544),("disjoint",1348)):
        p,b,i = (read(files[f"{scope}/{name}.json"]) for name in ("PRICE","BODY1","INDEPENDENT"))
        assert p["head"] == HEAD and p["caller_head"] == CALLER_HEAD
        assert p["native_copies"] == 17 and p["type_b_ports"] == 8
        assert b["price_sha256"] == pins[f"{scope}/PRICE.json"]
        assert b["scope"] == b["visited"] == b["exclusions"] == i["checked"] == count
        assert not b["unvisited"] and not b["survivors"] and i["both_survivors"] == 0
        assert i["caller_sha256"] == p["inputs"]["round30/complex/source/inputs/CALLER.json"]
        modular = {tuple(row["key"]):row["witness"] for row in b["records"]}
        exact = {tuple(row["clocks"]):row for row in i["rows"]}
        assert len(modular) == len(exact) == count and modular.keys() == exact.keys()
        jobs = {row[0]:(row[1],[row[2]] if scope == "singleton" else row[2])
                for row in p["jobs" if scope == "singleton" else "job_masks"]}
        price_keys = {tuple(row[:2]) for row in p["pair_keys"]}
        assert len(price_keys) == count and price_keys == exact.keys()
        for key,witness in modular.items():
            row = exact[key]
            assert not row["plus"] and not row["minus"]
            assert witness["q"] in (-1,1)
            assert not row["plus" if witness["q"] == 1 else "minus"]
            assert any(v and v[1] for v in (witness["outside_read"],witness["outside_write"]))
            roles,masks = zip(*(jobs[k] for k in key),strict=True)
            row_masks = [[x] for x in row["stages"]] if scope == "singleton" else row["masks"]
            assert row["roles"] == [r+36 for r in roles]
            assert [sorted(m) for m in row_masks] == list(masks)
            assert set(masks[0]).isdisjoint(masks[1])
        row = {"checked_pairs":count, "excluded_pairs":count, "unvisited":0,
               "exact_survivors":0, "pre_support_compatible_upper":p["whole_compatible_optimistic_upper"]}
        if scope == "singleton":
            assert len(jobs) == 34 and p["maximum_disjoint_pairs"] == 17
            assert 17*Q(p["one_pair_moment_credit"][1]) == Q(p["whole_compatible_optimistic_upper"])
            row.update(jobs=34,max_disjoint_pairs=17,pair_credit=p["one_pair_moment_credit"],
                       pair_complete_margin=p["one_pair_complete_margin"],
                       break_even_volume=p["break_even_volume_factor"])
        else:
            assert len(jobs) == 60 and len(p["price_by_rank_signature"]) == 35
            assert b["singleton_controls_matched"] == 544 and b["unresolved_optimistic_upper"] == "0"
            endpoint_upper = Counter()
            for a,t,k in p["pair_keys"]:
                r,s = sorted(8*len(jobs[c][1]) for c in (a,t))
                assert k == f"{r}+{s}"
                quote = p["price_by_rank_signature"][k]
                assert quote["old_ranks"] == [r,s] and quote["new_rank"] == r+s
                assert Q(quote["complete_margin"][0]) > 0
                credit = Q(quote["credit"][1])
                for c in (a,t):
                    endpoint_upper[c] = max(endpoint_upper[c],credit)
            assert sum(endpoint_upper.values(),Q(0))/2 == Q(p["whole_compatible_optimistic_upper"])
            row.update(jobs=60,rank_signatures=35,singleton_controls_matched=544)
        assert row == summary[scope]
        results[scope] = (p,jobs,modular)
    s,sjobs,sm = results["singleton"]
    d,djobs,dm = results["disjoint"]
    assert sm.keys() < dm.keys() and all(dm[k] == v for k,v in sm.items())
    assert sjobs == {k:v for k,v in djobs.items() if len(v[1]) == 1}
    for key in ("crossing_upper","old_complete_paid","old_complete_targets","old_complete_margin"):
        assert s[key] == d[key]


def replay(output):
    with TemporaryDirectory(prefix="p104-even-idle-") as temp:
        scratch = Path(temp)
        deps = authenticate(scratch)
        pins = read(HERE / "receipts/SHA256.json")
        files = {}
        earlier = scratch / "singleton"
        engines = HERE / "engines"
        options = ["--round30",deps/"round30","--predecessor",deps/"7298","--caller-root",deps/"7113"]
        for scope,extra in (
            ("singleton",[]),
            ("disjoint",["--r52",engines/"singleton.py","--r52-run",earlier]),
        ):
            result = scratch / scope
            run(engines / (scope+".py"),*options,"--out",result,"--stage","body1",*extra)
            (result/"INDEPENDENT.json").write_bytes(run(engines / f"independent_{scope}.py",deps/CALLER))
            current = {f"{scope}/{name}.json":result/f"{name}.json"
                       for name in ("PRICE","BODY1","INDEPENDENT")}
            check_receipts(current,pins)
            files.update(current)
        assert files.keys() == pins.keys()
        crosscheck(files,pins)
        if output is not None:
            output.mkdir(parents=True,exist_ok=False)
            for key,path in files.items():
                target = output/key
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(path,target)
        print("PASS_EVEN_IDLE_PROJECTOR_BOUND singleton=544 disjoint=1348 exact_survivors=0 unresolved=0 saving_upper=0 kappa_change=0")


if __name__ == "__main__":
    assert __debug__, "run with assertions enabled"
    assert sys.version_info[:2] == (3,12), "Python 3.12 required"
    p = ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,help="fresh directory for all six full receipts")
    replay(p.parse_args().out)
