"""Reprice and replay both charged rank-six support exclusions."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path, PurePosixPath
import runpy
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def authenticate(scratch):
    pins = read(HERE / "LOCAL-PINS.json")
    for key, expected in pins.items():
        rel = PurePosixPath(key)
        if rel.is_absolute() or ".." in rel.parts or rel.as_posix() != key:
            raise ValueError(f"invalid dependency path {key}")
        if sha256((HERE / key).read_bytes()).hexdigest() != expected:
            raise ValueError(f"changed dependency {key}")
    deps = scratch / "dependencies"
    shutil.copytree(HERE / "dependencies", deps)
    unpack = read(HERE / "UNPACK.json")
    assert len(unpack) == 3
    for key, entry in unpack.items():
        assert key in pins and key.endswith(".gz") and entry["destination"] == key.removesuffix(".gz")
        raw = gzip.decompress((HERE / key).read_bytes())
        assert sha256(raw).hexdigest() == entry["sha256"], key
        (scratch / entry["destination"]).write_bytes(raw)
    provenance = read(HERE / "PROVENANCE.json")["files"]
    assert len(provenance) == 5 and sum(p["uncompress"] for p in provenance.values()) == 2
    for key, pin in provenance.items():
        assert key in pins
        literal = unpack[key]["destination"] if pin["uncompress"] else key
        raw = (scratch / literal).read_bytes()
        assert sha256(raw).hexdigest() == pin["sha256"], key
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest() == pin["git_blob"], key
    return deps


def basis_control(deps):
    folder = deps / "round36/incremental"
    sys.path.insert(0, str(folder))
    try:
        mod = runpy.run_path(str(folder / "predecessor_split.py"))
    finally:
        sys.path.pop(0)
    a, b = {0: Q(1), 1: Q(1)}, {1: Q(1)}
    program = mod["basis"](a,b,0,0)
    def apply(events, values):
        state = list(values)
        for event in events:
            if event[0] == "ADD":
                _,d,s,q,_ = event
                state[d] += Q(q)*state[s]
            else:
                assert event[0] == "SCALE"
                _,d,q,_ = event
                state[d] *= Q(q)
        return state
    assert program and apply(program, [0,1]) == [1,0]
    for j in (0,1):
        v = [Q(j==0),Q(j==1)]
        transformed = apply(program, v)
        assert transformed[0] == a[j]
        assert apply(mod["inverse"](program), transformed) == v
    try:
        mod["basis"](a,{1:Q(-1)},0,0)
    except ValueError as exc:
        assert "Unit basis pairing" in str(exc)
    else:
        raise AssertionError("invalid paired basis accepted")


def run(script, *args, timeout):
    subprocess.run([sys.executable,"-I","-B",str(script),*map(str,args)], check=True, timeout=timeout)


def check_receipts(files, pins):
    for key, path in files.items():
        if sha256(path.read_bytes()).hexdigest() != pins[key]:
            raise ValueError(f"replay receipt changed: {key}")


def crosscheck(files):
    summary = read(HERE / "receipts/SUMMARY.json")
    assert summary["head"] == HEAD and summary["copies"] == 17
    assert summary["unresolved"] == 0 and summary["compatible_saving_after_support"] == "0"
    assert summary["kappa_change"] == "0"
    signatures = {}
    for label,parts,cut_count,suffix in (("3-plus-4",[3,4],714,24),("2-plus-5",[2,5],346,0)):
        p,n,s,c,i = (read(files[f"{label}/{name}.json"])
                     for name in ("PRICE","INVENTORY","SUPPORT","CUTS","RESULT"))
        assert {r["head"] for r in (p,n,s,c,i)} == {HEAD}
        assert p["copies"] == 17 and p["paid_rank_delta"] == {"1":17}
        assert p["productive_rank_delta"] == {"6":-17, **{str(x):17 for x in parts}}
        assert len(p["alternatives"]) == n["selected_signatures"] == i["typed_signatures"] == 83
        assert Counter(r["side"] for r in p["alternatives"]) == {"input":50,"output":33}
        assert len(n["counts"]) == n["union_groups"] == i["union_groups"] == 73
        assert n["cuts"] == c["cut_incidences"] == i["cut_incidences"] == cut_count
        assert s["counts"] == {"prefix_checked":cut_count}
        assert s["phase"] == "exhausted" and s["pending_cut_count"] == 0
        assert not s["unresolved"] and s["candidate"] is None
        assert i["positive_prefix_images"] == i["positive_pairings"] == 0
        assert i["suffix_nonzero_cuts"] == suffix and i["literal_paid_move_omission_rejected"]
        margin = p["complete_margin_interval_per_alternative"]
        assert Q(0) < Q(margin[0]) <= Q(margin[1])
        assert all(r["parts"] == parts and r["complete_margin_interval"] == margin for r in p["alternatives"])
        lo, hi = map(Q, i["whole_margins"]["+".join(map(str,parts))])
        assert 0 < lo <= hi and Q(margin[0]) <= hi and lo <= Q(margin[1])
        assert summary[label] == {
            "typed_signatures":83, "union_groups":73, "representative_cut_incidences":cut_count,
            "prefix_nonzero":0, "suffix_nonzero_independent":suffix, "price_only_complete_margin":margin,
            "unresolved":0, "candidate":None,
        }
        signatures[label] = {(r["side"],tuple(r["prior"]),tuple(r["new"]),tuple(r["parts"]))
                             for r in p["alternatives"]}
    assert all(len(x) == 83 for x in signatures.values())
    assert signatures["3-plus-4"].isdisjoint(signatures["2-plus-5"])


def replay(output):
    with TemporaryDirectory(prefix="p104-charged-rank-six-") as temp:
        scratch = Path(temp)
        deps = authenticate(scratch)
        basis_control(deps)
        pins = read(HERE / "receipts/SHA256.json")
        files = {}
        for label,primary,independent in (
            ("3-plus-4",deps / "round50/lead/screen.py",HERE / "engines/independent_3_4.py"),
            ("2-plus-5",HERE / "engines/primary_2_5.py",HERE / "engines/independent_2_5.py"),
        ):
            result = scratch / label
            audit = scratch / (label+"-independent")
            run(primary,deps,result,"--seconds",120,timeout=122)
            for name in ("PRICE","INVENTORY","SUPPORT"):
                files[f"{label}/{name}.json"] = result / f"{name}.json"
            check_receipts({k:v for k,v in files.items() if k.startswith(label)},pins)
            run(independent,*(deps / d for d in ("round30","round35","round36","round37")),
                result,audit,"--inventory-sha",pins[f"{label}/INVENTORY.json"],
                "--support-sha",pins[f"{label}/SUPPORT.json"],timeout=45)
            for name in ("CUTS","RESULT"):
                files[f"{label}/{name}.json"] = audit / f"{name}.json"
        assert files.keys() == pins.keys()
        check_receipts(files,pins)
        crosscheck(files)
        if output is not None:
            output.mkdir(parents=True,exist_ok=False)
            for key, path in files.items():
                dest = output / key
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(path,dest)
        print("PASS_CHARGED_RANK_SIX_SUPPORT signatures=166 cuts=1060 pure_prefix=0 suffix_3_4=24 suffix_2_5=0 unresolved=0 saving_upper=0 kappa_change=0")


if __name__ == "__main__":
    assert __debug__, "run with assertions enabled"
    assert sys.version_info[:2] == (3,12), "Python 3.12 required"
    p = ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,help="fresh destination for all ten full receipts")
    replay(p.parse_args().out)
