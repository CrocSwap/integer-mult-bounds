"""Git-free replay of the five fixed-partner three-MOVE exclusions."""
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


def unique(items):
    doc=dict(items)
    if len(doc)!=len(items):
        raise ValueError("duplicate JSON key")
    return doc


def decode(raw):
    return loads(raw,object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def relative(name):
    path=PurePosixPath(name)
    if path.is_absolute() or path.as_posix()!=name or ".." in path.parts:
        raise ValueError("invalid relative path "+name)
    return path


def source(name):
    return (ROOT/relative(name)).read_bytes()


def inputs():
    pins=decode(source("LOCAL-PINS.json"))
    for name,expected in pins.items():
        if digest(source(name))!=expected:
            raise ValueError("changed package dependency "+name)
    provenance=decode(source("PROVENANCE.json"))
    for name,record in provenance["files"].items():
        raw=source(name)
        assert digest(raw)==record["sha256"]==pins[name]
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()==record["git_blob"]
    raw={}
    for name,record in provenance["derived_inputs"].items():
        predecessor=decode(source(record["receipt"]))
        if name.endswith(".gz"):
            content=decompress(source(name))
            assert digest(content)==predecessor[record["key"]]
            raw[PurePosixPath(name).name.removesuffix(".gz")]=content
        else:
            content=source(name)
            bench=decode(content)
            assert bench["admission_sha256"]==digest(source(record["receipt"]))
            assert all(bench[k]==predecessor[k] for k in ("head","crossing","kappa","assumptions"))
            raw[PurePosixPath(name).name]=content
    return raw


def command(script,check=True):
    call=run([sys.executable,"-I","-B",str(script)],capture_output=True,timeout=25)
    if check and call.returncode:
        sys.stderr.write(call.stderr.decode(errors="replace"))
        call.check_returncode()
    return call


def replay(root,out):
    raw_inputs=inputs()
    expected=decode(source("receipts/SHA256.json"))
    for folder in ("inputs","lead","independent"):
        (root/folder).mkdir(parents=True)
    for name,content in raw_inputs.items():
        (root/"inputs"/name).write_bytes(content)
    copyfile(ROOT/"inputs/pricing.py",root/"inputs/pricing.py")
    copyfile(ROOT/"inputs/7334-WORD.json.gz",root/"inputs/7334-WORD.json.gz")
    for path in ("lead/quote.py","lead/retime.py","independent/barriers.py"):
        copyfile(ROOT/"engines"/Path(path).name,root/path)

    outputs={}
    def record(name,script,target=None):
        raw=command(root/script).stdout
        assert digest(raw)==expected[name],("changed receipt",name)
        outputs[name]=raw
        if target:
            (root/target).write_bytes(raw)
        return decode(raw)

    price=record("PRICE.json","lead/quote.py","lead/PRICE.json")
    assert price["before_paid"]==110519 and price["after_paid_one"]==110485
    assert price["surplus"]==1424 and price["productive"]==22461
    assert len(price["candidates"])==5 and price["compatible_cap"]==3
    assert Fraction(price["fixed_target_complete_upper"])<0
    lead=record("LEAD.json","lead/retime.py","lead/RESULT.json")
    independent=record("INDEPENDENT.json","independent/barriers.py")
    assert lead["typed_cut_checks"]==47490 and not lead["unvisited"]
    assert independent["events"]==76466 and independent["excluded"]==5 and independent["unresolved"]==0
    assert independent["direct_move_clock_granted_arbitrary_inside_original_window"]
    agreement=[]
    for case,a,b in zip(price["candidates"],lead["rows"],independent["results"],strict=True):
        assert case["role"]==a["role"]==b["role"] and case["clocks"]==a["clocks"]==b["clocks"]
        assert [case["charts"][0],case["charts"][-1]]==b["endpoints"]
        assert [x["peer"] for x in b["tests"]]==a["partners"]
        assert [x["bounds"] for x in b["tests"]]==a["commuting_intervals"]
        assert [p["retained_clock"] for p in a["placements"]]==case["clocks"]
        assert all(p["slot_counts"]==[0,0] and p["witness"] is None for p in a["placements"])
        assert len(b["tests"])==2 and all(not x["endpoint_hits"] for x in b["tests"])
        assert b["excluded"]
        agreement.append(dict(role=case["role"],clocks=case["clocks"],endpoints=b["endpoints"],
            partner_clocks=[x["clock"] for x in b["tests"]],partner_bounds=a["commuting_intervals"]))
    summary=dict(head=price["head"],caller=price["caller"],typed_cut_checks=47490,
        agreement=agreement,excluded_windows=5,unresolved=0)
    raw=(dumps(summary,indent=2,sort_keys=True)+"\n").encode()
    outputs["AGREEMENT.json"]=raw
    assert raw==source("receipts/AGREEMENT.json")

    assert set(outputs)-{"AGREEMENT.json"}==set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name,raw in outputs.items():
            (out/relative(name)).write_bytes(raw)
    print("PASS_P104_THREE_MOVE_TWO_ADD_RETIME_BOUND windows=5 typed_cuts=47490 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
