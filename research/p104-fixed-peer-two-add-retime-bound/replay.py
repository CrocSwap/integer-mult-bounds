"""Replay the four exact fixed-peer two-ADD retiming windows."""
from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha1,sha256
from json import dumps,loads
from pathlib import Path,PurePosixPath
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


def replay(root,out):
    inputs=authenticate()
    expected=decode((ROOT/"receipts/SHA256.json").read_bytes())
    actual={}
    for folder in ("plan/inputs","inputs","lead","independent/inputs"):
        (root/folder).mkdir(parents=True)
    for name,target in (("quote","plan/quote.py"),("walk","lead/walk.py"),
                        ("reverse_intervals","independent/reverse_intervals.py"),
                        ("reverse_routes","independent/inputs/reverse_routes.py"),
                        ("compare","independent/compare.py")):
        copyfile(ROOT/"engines"/f"{name}.py",root/target)
    for name,raw in inputs.items():
        (root/"plan/inputs"/f"{name}.json").write_bytes(raw)
    copyfile(ROOT/"inputs/pricing.py",root/"plan/inputs/pricing.py")
    copyfile(ROOT/"inputs/7334-WORD.json.gz",root/"inputs/7334-WORD.json.gz")
    copyfile(root/"inputs/7334-WORD.json.gz",root/"independent/inputs/7334-WORD.json.gz")

    def record(name,result,target=None):
        raw=result.stdout
        assert digest(raw)==expected[name],("changed receipt",name)
        actual[name]=raw
        if target:
            target.write_bytes(raw)
        return decode(raw)

    price=record("PRICE.json",command(root/"plan/quote.py"),root/"plan/PRICE.json")
    assert price["head"]==HEAD and price["paid_delta"]=={"1":-34,"2":17}
    assert price["compatible_paid_delta"]=={"1":-136,"2":68}
    assert (price["old_paid"],price["one_new_paid"],price["optimistic_all_four_paid"])==(110519,110502,110451)
    assert price["productive"]==22461 and price["rank_surplus"]==1424
    assert Fraction(price["whole_upper"])==4*Fraction(price["one_upper"])<1
    assert Fraction(price["fixed_target_complete_upper"])<0
    copyfile(root/"plan/PRICE.json",root/"independent/inputs/PRICE.json")
    lead=record("FORWARD.json",command(root/"lead/walk.py"),root/"lead/RESULT.json")
    rev=record("REVERSE.json",command(root/"independent/reverse_intervals.py"),root/"independent/RESULT.json")
    agreement=record("AGREEMENT.json",command(root/"independent/compare.py",root))
    assert actual["AGREEMENT.json"]==(ROOT/"receipts/AGREEMENT.json").read_bytes()
    assert lead["completed_literal_events"]==rev["progress"]["events_replayed"]==76466
    assert agreement["total_excluded"]==8248 and agreement["survivors"]==agreement["unresolved"]==0
    assert agreement["late_counts"]=={"other blocked":1760,"other clean":2364}

    for file,script in (("independent/inputs/PRICE.json","independent/reverse_intervals.py"),
                        ("inputs/7334-WORD.json.gz","lead/walk.py")):
        victim=root/file
        victim.write_bytes(victim.read_bytes()+b"\n")
        changed=command(root/script,check=False)
        assert changed.returncode==1 and not changed.stdout
        assert b"changed dependency" in changed.stderr and victim.name.encode() in changed.stderr

    assert set(actual)==set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name,raw in actual.items():
            (out/relative(name)).write_bytes(raw)
    print("PASS_FIXED_PEER_TWO_ADD_RETIME windows=4 early_excluded=4124 late_excluded=4124 chart_C=0 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    p=ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,help="new directory for the four regenerated receipts")
    args=p.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
