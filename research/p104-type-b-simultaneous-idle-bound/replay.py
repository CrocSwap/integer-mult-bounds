"""Git-free replay of the fixed-clock Type B simultaneous union bounds."""
from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha256
from json import loads
from pathlib import Path,PurePosixPath
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parent


def unique(pairs):
    data=dict(pairs)
    if len(data)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return data


def json(raw):
    return loads(raw,object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def relative(name):
    path=PurePosixPath(name)
    if path.is_absolute() or path.as_posix()!=name or ".." in path.parts:
        raise ValueError("invalid relative path "+name)
    return path


def command(script,*args,check=True,timeout=25):
    p=run([sys.executable,"-I","-B",str(script),*map(str,args)],capture_output=True,timeout=timeout)
    if check and p.returncode:
        sys.stderr.write(p.stderr.decode(errors="replace"))
        p.check_returncode()
    return p


def replay(root,out):
    pins=json((ROOT/"LOCAL-PINS.json").read_bytes())
    for name,expected in pins.items():
        if digest((ROOT/relative(name)).read_bytes())!=expected:
            raise ValueError("changed package dependency "+name)
    nested=ROOT/"r123"
    pair_receipts=root/"pair-receipts"
    pair=command(nested/"replay.py","--out",pair_receipts,timeout=70)
    assert b"equal=210 unequal=11728 unresolved=0" in pair.stdout
    for d in ("plan","inputs","lead","independent","r85/price/inputs","r85/lead","r85/independent"):
        (root/d).mkdir(parents=True)
    prov=json((nested/"PROVENANCE.json").read_bytes())
    for name in prov["derived_gzip"]:
        raw=decompress((nested/relative(name)).read_bytes())
        (root/relative(name.removesuffix(".gz"))).write_bytes(raw)
    for name in ("r85/price/SHA256","r85/independent/SHA256","r85/price/inputs/7334-ADMITTED.json",
        "r85/price/inputs/7334-READBACK.json","r85/price/inputs/derivative_check.py",
        "r85/price/inputs/pricing.py","inputs/7113-CALLER.json.gz","inputs/direct_impulse.py"):
        copyfile(nested/relative(name),root/relative(name))
    for a,b in (("quote.py","inputs/r123_quote.py"),("pair_derivative.py","inputs/r123_pair_derivative.py"),
                ("tangent.py","independent/r123_tangent.py")):
        copyfile(nested/"engines"/a,root/relative(b))
    copyfile(ROOT/"engines/stage_quote.py",root/"plan/quote.py")
    copyfile(ROOT/"engines/stage_support.py",root/"lead/stage_support.py")

    prices=command(root/"plan/quote.py").stdout
    assert prices==(ROOT/"receipts/STAGE-PRICE.json").read_bytes()
    (root/"plan/PRICE.json").write_bytes(prices)
    lead=command(root/"lead/stage_support.py").stdout
    assert lead==(ROOT/"receipts/STAGE-LEAD.json").read_bytes()
    (root/"lead/RESULT.json").write_bytes(lead)
    p,d=json(prices),json(lead)
    assert p["paid_count_at_upper_witness"]==110487 and p["productive"]==22461 and p["rank_surplus"]==1424
    assert p["relaxed_comparisons"]==26075 and d["comparisons"]==18443
    assert len(d["stages"])==17 and d["exact_match_count"]==0 and not d["remaining_even_sites"]
    assert len(d["eliminations"])==1 and len(d["eliminations"][0])==60
    assert not d["unvisited_stages"] and d["timeout"] is None
    assert all(row["exact_sums"]==row["modular_collisions"]==0
        for stage in d["stages"] for row in stage["cardinalities"])
    outputs={"STAGE-PRICE.json":prices,"STAGE-LEAD.json":lead}
    verify_independent(root,p,d,outputs)

    for name,script in (("plan/PRICE.json","lead/stage_support.py"),
                       ("inputs/7113-CALLER.json.gz","lead/stage_support.py"),
                       ("plan/PRICE.json","independent/stage_tangent.py")):
        path=root/name
        before=path.read_bytes()
        path.write_bytes(before+b"\n")
        rejected=command(root/script,check=False)
        assert rejected.returncode==1 and not rejected.stdout
        assert b"changed dependency" in rejected.stderr and path.name.encode() in rejected.stderr
        path.write_bytes(before)
    if out is not None:
        out.mkdir(parents=True)
        for f in pair_receipts.iterdir():
            (out/("PAIR-"+f.name)).write_bytes(f.read_bytes())
        for name,raw in outputs.items():
            (out/relative(name)).write_bytes(raw)
    print("PASS_P104_TYPE_B_SIMULTANEOUS_IDLE_BOUND stages=17 comparisons=18443 even_eliminated=60 unresolved=0")


def verify_independent(root,price,lead,outputs):
    copyfile(ROOT/"engines/stage_tangent.py",root/"independent/stage_tangent.py")
    copyfile(ROOT/"engines/stage_compare.py",root/"independent/compare.py")
    raw=command(root/"independent/stage_tangent.py").stdout
    assert raw==(ROOT/"receipts/STAGE-INDEPENDENT.json").read_bytes()
    (root/"independent/RESULT.json").write_bytes(raw)
    agreement=command(root/"independent/compare.py").stdout
    assert agreement==(ROOT/"receipts/STAGE-AGREEMENT.json").read_bytes()
    check=json(agreement)
    assert check["stages"]==17 and check["comparisons"]==18443 and check["fully_mask_compatible"]==4527
    assert check["missing_stage_certificates"]==60 and check["exact_matches"]==0 and not check["unvisited_stages"]
    outputs["STAGE-INDEPENDENT.json"]=raw
    outputs["STAGE-AGREEMENT.json"]=agreement


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
