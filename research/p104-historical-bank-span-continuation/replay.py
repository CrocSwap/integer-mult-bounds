"""Replay the checked small and large historical-bank exclusions and freeze the rest."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha1,sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from subprocess import CalledProcessError,run
from tempfile import TemporaryDirectory
import sys

ROOT=Path(__file__).resolve().parent
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"


def unique(items):
    data=dict(items)
    if len(data)!=len(items):
        raise ValueError("duplicate dependency or receipt key")
    return data


def decode(raw):
    return loads(raw,object_pairs_hook=unique)


def source(name):
    p=Path(name)
    if p.is_absolute() or ".." in p.parts or p.as_posix()!=name:
        raise ValueError("invalid package-relative path "+name)
    return (ROOT/p).read_bytes()


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate():
    pins=decode(source("LOCAL-PINS.json"))
    for name,expected in pins.items():
        if digest(source(name))!=expected:
            raise ValueError("changed package input "+name)
    provenance=decode(source("PROVENANCE.json"))
    for name,entry in provenance["files"].items():
        raw=source(name)
        assert digest(raw)==entry["sha256"]==pins[name]
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()==entry["git_blob"]
    assert decode(source("inputs/PR7362-SHA256.json"))["R92-PRICE.json"]==pins["inputs/R92-PRICE.json"]
    return pins


def clockmap(rows):
    out={tuple(row["clocks"]):row for row in rows}
    assert len(out)==len(rows)
    return out


def price_all(cases):
    base=decode(source("inputs/R92-PRICE.json"))
    assert (base["head"],base["caller_head"])==(HEAD,CALLER)
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    k=Q(base["old_crossing_upper"])
    for row in cases:
        a,b,r=row["ranks"]
        assert r==a+b
        delta=Counter((a,b))
        delta[r]-=1
        quote=list(map(str,cost({j:17*v for j,v in delta.items() if v},k)))
        assert quote==row["gross"] and Q(quote[1])<1


def unresolved_bytes(cases,first_small,large):
    all_keys=clockmap(cases)
    small_keys=clockmap(first_small)
    large_keys=clockmap(large)
    assert not (small_keys.keys()&large_keys.keys())
    assert small_keys.keys()|large_keys.keys() <= all_keys.keys()
    unresolved=[{k:c[k] for k in ("clocks","role","peer","chart","bank_count","gross")}
                for c in cases if tuple(c["clocks"]) not in (small_keys.keys()|large_keys.keys())]
    assert len(unresolved)==125 and all(r["bank_count"]>19 for r in unresolved)
    upper=sum(Q(r["gross"][1]) for r in unresolved)
    assert upper<Q("14.380")
    doc={"head":HEAD,"caller":CALLER,"count":125,"keys":unresolved,
         "relaxed_gross_upper":str(upper)}
    return (dumps(doc,sort_keys=True,indent=2)+"\n").encode()


def replay(stage,out_dir):
    pins=authenticate()
    stage1_raw=decompress(source("inputs/STAGE1.json.gz"))
    stage2_raw=source("inputs/STAGE2.json")
    prior=decode(source("inputs/PR7434-EXPECTED.json"))
    assert digest(stage1_raw)==prior["STAGE1"]["sha256"]
    assert digest(stage2_raw)==prior["STAGE2"]["sha256"]
    stage1,stage2=map(decode,(stage1_raw,stage2_raw))
    assert (stage1["head"],stage1["caller"])==(stage2["head"],stage2["caller"])==(HEAD,CALLER)
    assert stage1["excluded_count"]==724 and len(stage2["checked"])==6
    first_six=clockmap(stage2["checked"])
    unresolved=[c for c in stage1["screen_survivors"] if tuple(c["clocks"]) not in first_six]
    assert len(unresolved)==237
    assert sum(Q(c["gross"][1]) for c in unresolved if c["bank_count"]>19)<Q("20.678")
    price_all(unresolved)
    results={}

    def copy(name,raw):
        path=stage/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(raw)

    def launch(script,*args):
        return run([sys.executable,"-I","-B","-X",f"pycache_prefix={stage/'pycache'}",str(stage/script),*args],
                   check=True,capture_output=True,timeout=40).stdout

    def record(name,script,*args):
        raw=launch(script,*args)
        assert digest(raw)==pins["receipts/"+name],name
        results[name]=raw
        return decode(raw)

    for name in pins:
        if name.startswith("inputs/"):
            copy(name,source(name))
        elif name.startswith("engines/"):
            copy(Path(name).name,source(name))
    copy("inputs/STAGE1.json",stage1_raw)
    copy("PINS",source("engines/R203-PINS"))
    f=record("R203-FORWARD.json","r203_forward.py")
    r=record("R203-REVERSE.json","r203_reverse.py")
    assert r["head"]==HEAD and r["caller"]==CALLER and not (r["capped"] or r["winner"] or r["unvisited"])
    assert r["statistics"]=={"exact_rank_exclusion":62} and not f["survivors"]
    assert r["reconstructed_rows"]==399
    fkeys,rkeys=map(clockmap,(f["records"],r["checked"]))
    expected=clockmap([c for c in unresolved if c["bank_count"]<=19])
    assert fkeys.keys()==rkeys.keys()==expected.keys() and len(expected)==62
    for key,x in expected.items():
        lead,rev=fkeys[key],rkeys[key]
        assert lead["bank"]==rev["bank_roles"] and len(lead["bank"])==x["bank_count"]
        assert (lead["role"],lead["peer"],lead["gross"])==(rev["role"],rev["peer"],rev["gross"])
        assert lead["target"]==x["target_row"]
        assert lead["rank"]==rev["decision"]["donor_rank"]
        assert lead["separator"] and rev["decision"]["separating_covector"]
    assert Q(r["relaxed_gross_upper"])<Q("7.364")
    copy("inputs/R203.json",results["R203-REVERSE.json"])
    lead_large=source("receipts/R204-LEAD.json")
    copy("inputs/R204-LEAD.json",lead_large)
    sha=digest(lead_large)
    old_large=decode(lead_large)
    assert old_large["capped"] and old_large["unvisited"]==125 and not old_large["survivors"]
    small=record("R204-FIRST12.json","r204_verify.py","--lead-sha",sha)
    rest=record("R204-REMAINING38.json","r204_verify.py","--lead-sha",sha,"--remaining")
    checked=small["checked"]+rest["checked"]
    assert len(small["checked"])==12 and len(rest["checked"])==38
    assert len(checked)==len(old_large["records"])==50
    assert small["historical_bank_rows_verified"]+rest["historical_bank_rows_verified"]==15172
    for actual,old in zip(checked,old_large["records"],strict=True):
        assert (actual["clocks"],actual["bank_count"])==(old["clocks"],old["bank_count"])
        assert actual["input"]==old["separator"]["input"] and actual["source_value"]==old["separator"]["source_value"]
    raw=unresolved_bytes(unresolved,r["checked"],checked)
    assert digest(raw)==pins["receipts/UNRESOLVED.json"]
    results["UNRESOLVED.json"]=raw

    copy("inputs/R203.json",results["R203-REVERSE.json"]+b" ")
    try:
        launch("r204_verify.py","--lead-sha",sha)
    except CalledProcessError as exc:
        assert exc.returncode==1 and b"inputs/R203.json" in exc.stderr
    else:
        raise AssertionError("corrupted predecessor accepted")
    if out_dir is not None:
        out_dir.mkdir(parents=True)
        for name,raw in results.items():
            (out_dir/name).write_bytes(raw)
    print("PASS_P104_HISTORICAL_BANK_CONTINUATION small=62 large=50 verified_new=112 unresolved=125")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    cli=ArgumentParser(description=__doc__)
    cli.add_argument("--out",type=Path)
    args=cli.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
