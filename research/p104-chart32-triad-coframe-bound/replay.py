"""Git-free replay of the two frozen chart-32 coframe exclusions."""
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
    for folder in ("inputs","plan/inputs","lead","independent"):
        (root/folder).mkdir(parents=True)
    for name,content in raw_inputs.items():
        (root/"plan/inputs"/name).write_bytes(content)
    copyfile(ROOT/"inputs/pricing.py",root/"plan/inputs/pricing.py")
    copyfile(ROOT/"inputs/7334-WORD.json.gz",root/"inputs/7334-WORD.json.gz")
    for path in ("plan/quote.py","lead/splice.py","independent/reverse_route.py","independent/compare.py"):
        copyfile(ROOT/"engines"/Path(path).name,root/path)

    outputs={}
    def record(name,script,target=None):
        raw=command(root/script).stdout
        assert digest(raw)==expected[name],("changed receipt",name)
        outputs[name]=raw
        if target:
            (root/target).write_bytes(raw)
        return decode(raw)

    price=record("PRICE.json","plan/quote.py","plan/PRICE.json")
    assert price["rank_surplus"]==1424 and price["productive_count"]==22461
    assert len(price["stock"])==2 and len(price["profiles"])==90
    lead=record("LEAD.json","lead/splice.py","lead/RESULT.json")
    independent=record("INDEPENDENT.json","independent/reverse_route.py","independent/RESULT.json")
    agreement=record("AGREEMENT.json","independent/compare.py")
    assert lead["counts"]==independent["counts"]=={"nesting exclusion":4}
    assert agreement["unique_span_basis"]==[50] and agreement["preserved_ranks"]==[1,1,0,1]
    assert agreement["unresolved"]==0
    assert outputs["AGREEMENT.json"]==source("receipts/AGREEMENT.json")

    for name,script in (("plan/inputs/R100-GEOMETRY.json","plan/quote.py"),
            ("plan/PRICE.json","lead/splice.py"),("plan/PRICE.json","independent/reverse_route.py"),
            ("inputs/7334-WORD.json.gz","independent/reverse_route.py")):
        file=root/name
        original=file.read_bytes()
        file.write_bytes(original+b"\n")
        rejected=command(root/script,check=False)
        assert rejected.returncode==1 and not rejected.stdout
        assert b"changed dependency" in rejected.stderr and file.name.encode() in rejected.stderr
        file.write_bytes(original)

    assert set(outputs)==set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name,raw in outputs.items():
            (out/relative(name)).write_bytes(raw)
    print("PASS_P104_CHART32_TRIAD_COFRAME_BOUND windows=2 endpoint_cases=4 common_span_rank=1 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
