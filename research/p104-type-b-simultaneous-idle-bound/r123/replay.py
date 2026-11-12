"""Git-free replay of the exact two-edit Type B signed idle exclusion."""
from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha1,sha256
from json import loads
from pathlib import Path,PurePosixPath
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parent


def unique(pairs):
    value=dict(pairs)
    if len(value)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return value


def decode(raw):
    return loads(raw,object_pairs_hook=unique)


def relative(name):
    path=PurePosixPath(name)
    if path.is_absolute() or path.as_posix()!=name or ".." in path.parts:
        raise ValueError("invalid relative path "+name)
    return path


def source(name):
    return (ROOT/relative(name)).read_bytes()


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate():
    pins=decode(source("LOCAL-PINS.json"))
    for name,expected in pins.items():
        if digest(source(name))!=expected:
            raise ValueError("changed package dependency "+name)
    prov=decode(source("PROVENANCE.json"))
    for name,record in prov["files"].items():
        raw=source(name)
        if record.get("uncompress"):
            raw=decompress(raw)
        assert digest(raw)==record["sha256"]
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()==record["git_blob"]
    manifest=decode(source(prov["derived_gzip_manifest"]))
    derived={}
    for name,key in prov["derived_gzip"].items():
        raw=decompress(source(name))
        assert digest(raw)==manifest[key]
        derived[name.removesuffix(".gz")]=raw
    return derived


def command(script,*args,check=True):
    p=run([sys.executable,"-I","-B",str(script),*map(str,args)],capture_output=True,timeout=25)
    if check and p.returncode:
        sys.stderr.write(p.stderr.decode(errors="replace"))
        p.check_returncode()
    return p


def replay(root,out):
    derived=authenticate()
    expected=decode(source("receipts/SHA256.json"))
    for d in ("plan","inputs","lead","independent","r85/price/inputs","r85/lead","r85/independent"):
        (root/d).mkdir(parents=True)
    for path,content in derived.items():
        (root/relative(path)).write_bytes(content)
    for name in ("r85/price/SHA256","r85/independent/SHA256","r85/price/inputs/7334-ADMITTED.json",
        "r85/price/inputs/7334-READBACK.json","r85/price/inputs/derivative_check.py",
        "r85/price/inputs/pricing.py","inputs/7113-CALLER.json.gz","inputs/direct_impulse.py"):
        copyfile(ROOT/name,root/name)
    for path in ("plan/quote.py","lead/pair_derivative.py","independent/tangent.py","independent/compare.py"):
        copyfile(ROOT/"engines"/Path(path).name,root/path)

    outputs={}
    def record(name,response,target=None):
        raw=response.stdout
        assert digest(raw)==expected[name],("changed receipt",name)
        outputs[name]=raw
        if target:
            (root/target).write_bytes(raw)
        return decode(raw)

    price=record("PRICE.json",command(root/"plan/quote.py","--r85",root/"r85"),"plan/PRICE.json")
    assert price["all_disjoint_pair_placements"]==11938 and price["unequal_mask_exclusions"]==11728
    assert len(price["equal_mask_keys"])==210 and price["productive_fields"]==22461
    assert price["new_paid_positions"]==110503 and price["rank_surplus"]==1424
    lead=record("LEAD.json",command(root/"lead/pair_derivative.py"),"lead/RESULT.json")
    independent=record("INDEPENDENT.json",command(root/"independent/tangent.py"),"independent/RESULT.json")
    agreement=record("AGREEMENT.json",command(root/"independent/compare.py"))
    assert lead["counts"]==independent["counts"]=={"exact derivative exclusion":210}
    assert independent["progress"]["old_endpoint_columns"]==36 and independent["progress"]["direct_tangent_keys"]==2
    assert agreement["exact_witness_agreement"]==agreement["exact_nonzero_count_agreement"]==210
    assert agreement["unequal_mask_excluded"]==11728 and agreement["unresolved"]==0
    assert all(x["witness"]==[36,36,"16"] for x in agreement["direct_endpoint_tangent_priority"])
    assert outputs["AGREEMENT.json"]==source("receipts/AGREEMENT.json")

    for name,script,args in (
        ("r85/independent/RESULT.json","plan/quote.py",("--r85",root/"r85")),
        ("plan/PRICE.json","independent/tangent.py",()),
        ("inputs/7113-CALLER.json.gz","lead/pair_derivative.py",()),
        ("inputs/7113-CALLER.json.gz","independent/tangent.py",()),
    ):
        path=root/name
        before=path.read_bytes()
        path.write_bytes(before+b"\n")
        wrong=command(root/script,*args,check=False)
        assert wrong.returncode==1 and not wrong.stdout
        assert b"changed dependency" in wrong.stderr and path.name.encode() in wrong.stderr
        path.write_bytes(before)

    assert set(outputs)==set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name,raw in outputs.items():
            (out/relative(name)).write_bytes(raw)
    print("PASS_P104_TYPE_B_DOUBLE_ODD_EVEN_IDLE_BOUND equal=210 unequal=11728 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
