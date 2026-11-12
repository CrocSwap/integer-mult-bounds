"""Replay the exact fixed-clock two-bank source synthesis exclusions."""
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
    receipts={}
    for folder in ("plan/inputs","inputs","lead","independent/reused"):
        (root/folder).mkdir(parents=True)
    for name,target in (("quote","plan/quote.py"),("donors","lead/donors.py"),
                        ("bank_covectors","independent/bank_covectors.py"),("compare","independent/compare.py")):
        copyfile(ROOT/"engines"/f"{name}.py",root/target)
    for name,raw in inputs.items():
        (root/"plan/inputs"/f"{name}.json").write_bytes(raw)
    for source,target in (("7334-WORD.json.gz","inputs/7334-WORD.json.gz"),
                          ("7334-RESULT.json","plan/inputs/7334-RESULT.json"),
                          ("donor_span.py","inputs/donor_span.py"),
                          ("reverse_span.py","independent/reused/reverse_span.py")):
        copyfile(ROOT/"inputs"/source,root/target)
    copyfile(root/"plan/inputs/R116-PRICE.json",root/"inputs/R116-PRICE.json")

    def record(name,result,target=None):
        raw=result.stdout
        assert digest(raw)==expected[name],("changed receipt",name)
        receipts[name]=raw
        if target is not None:
            target.write_bytes(raw)
        return decode(raw)

    price=record("PRICE.json",command(root/"plan/quote.py"),root/"plan/PRICE.json")
    assert price["head"]==HEAD and price["limits"]=={"windows":4,"banks":8,"events":76466,"seconds":20}
    assert price["paid_delta"]=={"1":-34,"2":17} and price["all_four_relaxed_paid_delta"]=={"1":-136,"2":68}
    assert (price["old_paid"],price["one_paid"],price["four_relaxed_paid"])==(110519,110502,110451)
    assert price["productive"]==22461 and price["rank_surplus"]==1424
    assert Fraction(price["four_relaxed_upper"])==4*Fraction(price["one_upper"])<1
    assert Fraction(price["fixed_target_complete_upper"])<0
    assert price["conditional_ordinary"]["four_relaxed_upper"]==782903240
    assert price["conditional_tape"]["one_scalar_services_upper"]-price["conditional_tape"]["old_scalar_services"]==2176
    lead=record("FORWARD.json",command(root/"lead/donors.py"),root/"lead/RESULT.json")
    reverse=record("REVERSE.json",command(root/"independent/bank_covectors.py"),root/"independent/RESULT.json")
    compare=record("AGREEMENT.json",command(root/"independent/compare.py"))
    assert receipts["AGREEMENT.json"]==(ROOT/"receipts/AGREEMENT.json").read_bytes()
    assert lead["counts"]=={"coordinate exclusion":7,"rational exclusion":1}
    assert len(lead["excluded_windows"])==4 and not lead["viable_windows"] and not lead["unvisited_banks"]
    assert reverse["progress"]["events_checked"]==76466 and not reverse["unvisited"]
    assert compare["bank_and_disposition_agreement"]==8 and compare["signed_coordinate_agreement"]==7
    assert compare["exact_residual_agreement"]==1 and compare["unresolved"]==0
    proof=reverse["results"][0]["proof"]
    assert reverse["results"][0]["key"]==[41321,44605,1305,41322]
    assert proof["separating_covector"]=={"1488":"1","1493":"-2"} and proof["separated_target"]=="2"

    for file,script in (("plan/PRICE.json","independent/bank_covectors.py"),
                        ("inputs/7334-WORD.json.gz","lead/donors.py")):
        victim=root/file
        before=victim.read_bytes()
        victim.write_bytes(before+b"\n")
        changed=command(root/script,check=False)
        assert changed.returncode==1 and not changed.stdout
        assert victim.name.encode() in changed.stderr
        victim.write_bytes(before)

    assert set(receipts)==set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name,raw in receipts.items():
            (out/relative(name)).write_bytes(raw)
    print("PASS_FIXED_CLOCK_TWO_BANK_BOUND windows=4 banks=8 coordinate=7 rational=1 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    p=ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,help="new directory for the four regenerated receipts")
    args=p.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
