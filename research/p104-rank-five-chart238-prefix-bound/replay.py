"""Replay the exact fixed-paid rank-five chart 3-to-238 prefix exclusions."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha1,sha256
from json import dumps,loads
from pathlib import Path,PurePosixPath
from runpy import run_path
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parent
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"


def unique(items):
    result=dict(items)
    if len(result)!=len(items):
        raise ValueError("duplicate JSON key")
    return result


def decode(raw):
    return loads(raw,object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def relative(name):
    path=PurePosixPath(name)
    if path.is_absolute() or path.as_posix()!=name or ".." in path.parts:
        raise ValueError(f"invalid relative path: {name}")
    return path


def authenticate():
    pins=decode((ROOT/"LOCAL-PINS.json").read_bytes())
    for name,expected in pins.items():
        if digest((ROOT/relative(name)).read_bytes())!=expected:
            raise ValueError(f"changed package dependency: {name}")
    provenance=decode((ROOT/"PROVENANCE.json").read_bytes())
    for name,record in provenance["files"].items():
        raw=(ROOT/relative(name)).read_bytes()
        assert digest(raw)==record["sha256"]==pins[name]
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()==record["git_blob"]
    inputs={}
    for name,record in provenance["derived_gzip"].items():
        raw=decompress((ROOT/"inputs"/f"{name}.json.gz").read_bytes())
        published=decode((ROOT/relative(record["receipt"])).read_bytes())
        assert digest(raw)==published[record["key"]]
        inputs[name]=raw
    return inputs


def command(script,*args,timeout=25,check=True):
    response=run([sys.executable,"-I","-B",str(script),*map(str,args)],capture_output=True,timeout=timeout)
    if check and response.returncode:
        sys.stderr.write(response.stderr.decode(errors="replace"))
        response.check_returncode()
    return response


def verify_price(selection,prior):
    readback=decode((ROOT/"inputs/READBACK.json").read_bytes())
    assert readback["head"]==prior["head"]==selection["head"]==HEAD
    assert readback["caller_head"]==prior["caller"]==selection["caller"]
    assert readback["copies"]==17 and not readback["empty_root_credits"]
    assert prior["pins"]["inputs/pricing.py"]==digest((ROOT/"inputs/pricing.py").read_bytes())
    assert prior["pins"]["inputs/READBACK.json"]==digest((ROOT/"inputs/READBACK.json").read_bytes())
    paid,target=(Counter({int(r):n for r,n in readback[k].items()}) for k in ("paid","targets"))
    assert (sum(paid.values()),sum(target.values()))==(110519,22461)
    old=target.copy()
    old.subtract(paid)
    delta={int(r):n for r,n in selection["productive_delta"].items()}
    assert not selection["paid_delta"] and delta=={2:17,3:17,5:-17}
    assert sum(r*v for r,v in old.items())==selection["surplus"]==1424
    assert sum(r*v for r,v in delta.items())==0
    assert selection["productive_one"]==sum(target.values())+sum(delta.values())==22478
    assert selection["unchanged_paid_positions"]==sum(paid.values())
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    at,probe,moon=map(Fraction,(prior["incumbent"],prior["probe"],selection["fixed_target"]))
    one=cost(delta,at)
    assert one==tuple(map(Fraction,selection["one_gross"])) and one[0]>0
    assert 2*one[1]==Fraction(selection["two_compatible_upper"])
    assert cost(old,at)[1]+2*one[1]<1
    after=old.copy()
    after.update(delta)
    assert cost(after,probe)[0]>0
    assert cost(old,moon)[1]+2*cost(delta,moon)[1]==Fraction(selection["fixed_target_complete_upper"])<0


def replay(root,out):
    inputs=authenticate()
    expected=decode((ROOT/"receipts/SHA256.json").read_bytes())
    outputs={}
    for folder in ("inputs","lead","independent/inputs"):
        (root/folder).mkdir(parents=True)
    for name,target in (("freeze","lead/freeze.py"),("modular","lead/modular.py"),
                        ("prefix","independent/prefix.py"),("verify_axes","independent/verify_axes.py")):
        copyfile(ROOT/"engines"/f"{name}.py",root/target)
    for name,raw in inputs.items():
        (root/"inputs"/f"{name}.json").write_bytes(raw)
    for name in ("7334-WORD.json.gz","exterior_rank23.py","reverse_engine.py"):
        copyfile(ROOT/"inputs"/name,root/"inputs"/name)
    for src,dst in (("R115-PRICE.json","PRICE.json"),("R115-GEOMETRY.json","GEOMETRY.json"),
                    ("7334-WORD.json.gz","7334-WORD.json.gz")):
        copyfile(root/"inputs"/src,root/"independent/inputs"/dst)
    copyfile(ROOT/"inputs/second_prime.py",root/"independent/inputs/second_prime.py")

    def record(name,result,target=None):
        raw=result.stdout
        assert digest(raw)==expected[name],("changed receipt",name)
        outputs[name]=raw
        if target is not None:
            target.write_bytes(raw)
        return decode(raw)

    selected=record("SELECTION.json",command(root/"lead/freeze.py"),root/"SELECTION.json")
    verify_price(selected,decode(inputs["R115-PRICE"]))
    assert selected["selected_group"]==[3,238] and selected["cohort"]==[325,1087]
    assert len(selected["selected"])==18 and len(selected["unselected"])==31
    assert all(not r["owned"] for r in selected["selected"])
    assert {r["key"][1] for r in selected["selected"]}=={370,375}

    p=root/"lead/RESULT.json"
    i=root/"independent/RESULT.json"
    first=record("PRIMARY.json",command(root/"lead/modular.py"),p)
    other=record("SECOND.json",command(root/"independent/prefix.py"),i)
    agree=record("AGREEMENT.json",command(root/"independent/verify_axes.py","--primary",p,
        "--primary-sha256",expected["PRIMARY.json"],"--independent",i,
        "--independent-sha256",expected["SECOND.json"]))
    assert outputs["AGREEMENT.json"]==(ROOT/"receipts/AGREEMENT.json").read_bytes()
    assert first["prime"]==65521 and other["prime"]==65537
    assert first["counts"]==other["counts"]=={"prefix exclusion":18}
    assert first["prefix_events"]==other["progress"]["events"]==76466
    assert len(other["denominator_units"])==98 and not other["unresolved"]
    assert agree["banks"]==agree["same_full_rank_disposition"]==agree["primary_nonzero_axes_at_second_prime"]==18
    assert first["unselected"]==selected["unselected"]
    assert all(row["suffix"] is None for row in first["results"])

    for path,script in (("SELECTION.json","lead/modular.py"),("independent/inputs/GEOMETRY.json","independent/prefix.py")):
        victim=root/path
        raw=victim.read_bytes()
        victim.write_bytes(raw+b"\n")
        changed=command(root/script,check=False)
        assert changed.returncode==1 and not changed.stdout
        assert b"changed dependency" in changed.stderr and victim.name.encode() in changed.stderr
        victim.write_bytes(raw)

    assert set(outputs)==set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name,raw in outputs.items():
            (out/relative(name)).write_bytes(raw)
    print("PASS_RANK_FIVE_CHART238_PREFIX_BOUND banks=18 primary=18 second=18 unresolved=0 other_cohorts=31")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    p=ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,help="new directory for the four regenerated receipts")
    args=p.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
