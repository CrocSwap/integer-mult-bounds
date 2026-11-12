"""Replay both exact entry-shadow support gates and the signed price."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha1,sha256
from json import loads
from pathlib import Path
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
        raw=source(name)
        if digest(raw)!=expected:
            raise ValueError("changed package input "+name)
    prov=decode(source("PROVENANCE.json"))
    for name,entry in prov["files"].items():
        raw=source(name)
        assert digest(raw)==entry["sha256"]==pins[name]
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()==entry["git_blob"]
    assert decode(source("inputs/PR7362-SHA256.json"))["R92-PRICE.json"]==pins["inputs/R92-PRICE.json"]
    return pins


def groups(row,initial):
    result={}
    for i in sorted(map(int,row)):
        result.setdefault(str(initial[i]),[]).append([i,row[str(i)]])
    return result


def replay(stage,output):
    pins=authenticate()
    initial=decode(decompress(source("inputs/7334-WORD.json.gz")))["initial"]
    assert len(initial)==1501 and initial.count(3)==1060
    results={}

    def copy(name,raw):
        path=stage/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(raw)

    def launch(script):
        return run([sys.executable,"-I","-B","-X",f"pycache_prefix={stage/'pycache'}",str(stage/script)],
                   check=True,capture_output=True,timeout=32).stdout

    def record(name,script):
        raw=launch(script)
        assert digest(raw)==pins["receipts/"+name],name
        results[name]=raw
        return decode(raw)

    for name in pins:
        if name.startswith("inputs/"):
            copy(name,source(name))
        elif name.startswith("engines/"):
            copy(Path(name).name,source(name))

    price=record("R197-PRICE.json","r197_price.py")
    census=record("R198-CENSUS.json","r198_census.py")
    assert (price["head"],price["caller"])==(census["head"],census["caller"])==(HEAD,CALLER)
    assert price["signed_delta"]=={"1":-17,"5":17} and Fraction(price["gross"][0])>67
    assert len(census["census"])==8 and Fraction(census["gross"][1])<289
    copy("PRICE.json",results["R197-PRICE.json"])
    copy("inputs/PRICE.json",results["R197-PRICE.json"])
    copy("CENSUS.json",results["R198-CENSUS.json"])

    a=record("R197-FORWARD.json","r197_forward.py")
    b=record("R197-REVERSE.json","r197_reverse.py")
    assert (a["head"],a["cut"])==(b["head"],b["clock"])==(HEAD,39811)
    assert a["row"]==b["row"] and len(b["row"])==236
    assert a["entry_chart_support"]==groups(b["row"],initial)
    assert not a["entry_chart3_only"] and b["first_outside"]==[0,"1/4",0]
    assert len(b["outside_entry_chart"])==52
    assert a["shadow_first_init"]==b["shadow_first_old_contact"]==39828
    assert b["ancestor"]["ratio_at_first_pivot"]=="-1/2"
    difference=b["ancestor"]["disagreement"]
    assert a["ancestor_difference"]==[[i,difference[str(i)]] for i in sorted(map(int,difference))]
    copy("inputs/R197.json",results["R197-REVERSE.json"])

    f=record("R198-FORWARD.json","r198_forward.py")
    r=record("R198-REVERSE.json","r198_reverse.py")
    assert f["head"]==r["head"]==HEAD and r["caller"]==CALLER
    assert not (f["survivors"] or r["survivors"] or r["unvisited"])
    assert f["case_cap"]==r["case_cap"]==8 and r["new_case_cap"]==7
    assert r["whole_optimistic_gross"]==census["gross"]
    assert [x["entry_destination_count"] for x in r["results"]]==[0,1,0,0,2,0,1,0]
    for key,x,y in zip(census["census"],f["records"],r["results"],strict=True):
        assert key==x["key"]==y["key"] and x["row"]==y["row"]
        row=y["row"]
        dest=key[3]
        assert x["entry_chart_support"]==groups(row,initial)
        counts=Counter(str(initial[int(i)]) for i in row)
        assert counts==y["support_groups"]
        outside={int(i):v for i,v in row.items() if initial[int(i)] not in (3,dest)}
        assert x["outside_count"]==y["outside_count"]==len(outside)==52
        j,v,chart=y["witness"]
        assert chart==initial[j] and j==min(outside) and Fraction(v)==Fraction(outside[j])!=0
        chart,j,v=x["first_outside"]
        assert chart==initial[j] and Fraction(v)==Fraction(outside[j])!=0

    copy("inputs/R197.json",results["R197-REVERSE.json"]+b" ")
    try:
        launch("r198_reverse.py")
    except CalledProcessError as exc:
        assert exc.returncode==1 and b"inputs/R197.json" in exc.stderr
    else:
        raise AssertionError("changed predecessor accepted")
    if output is not None:
        output.mkdir(parents=True)
        for name,raw in results.items():
            (output/name).write_bytes(raw)
    print("PASS_P104_ENTRY_SHADOW_OWNED_DESCENT_BOUND cases=8 new=7 exterior_per_row=52 survivors=0 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    cli=ArgumentParser(description=__doc__)
    cli.add_argument("--out",type=Path)
    args=cli.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
