"""Replay the exact Type A singleton idle projection exclusion."""
from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha1,sha256
from json import dumps,loads
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
import sys

ROOT=Path(__file__).resolve().parent


def unique(items):
    out=dict(items)
    if len(out)!=len(items):
        raise ValueError('duplicate JSON key')
    return out


def decode(raw):
    return loads(raw,object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def source(name):
    path=Path(name)
    if path.is_absolute() or '..' in path.parts or path.as_posix()!=name:
        raise ValueError('invalid package-relative path '+name)
    return (ROOT/path).read_bytes()


def load_inputs():
    pins=decode(source('LOCAL-PINS.json'))
    for name,expected in pins.items():
        if digest(source(name))!=expected:
            raise ValueError('changed package dependency '+name)
    p=decode(source('PROVENANCE.json'))
    for name,entry in p['files'].items():
        raw=source(name)
        assert digest(raw)==entry['sha256']==pins[name]
        assert sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()==entry['git_blob']
    a=decode(source('inputs/7334-ADMITTED.json'))
    assert a['head']=='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
    assert a['kappa']=='0.00364665195644'
    materialized={}
    for name,entry in p["derived_inputs"].items():
        raw=source(entry["file"])
        if entry.get("compression")=="gzip":
            raw=decompress(raw)
        assert digest(raw)==entry["sha256"]
        if "manifest" in entry:
            manifest=decode(source(entry["manifest"]))
            if "manifest_section" in entry:
                manifest=manifest[entry["manifest_section"]]
            assert digest(raw)==manifest[entry["key"]]
        materialized[name]=raw
    return materialized



def call(script,*args,expect_success=True):
    p=run([sys.executable,'-I','-B',str(script),*args],capture_output=True,timeout=40)
    if expect_success and p.returncode:
        sys.stderr.write(p.stderr.decode(errors='replace'))
        p.check_returncode()
    return p


def write(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)


def replay(root,out):
    data=load_inputs()
    expected=decode(source("receipts/SHA256.json"))
    outputs={}

    def stage(d,name,raw):
        write(d/"inputs"/name,raw)

    def engine(d,name):
        path=d/name
        write(path,source("engines/"+name))
        return path

    def record(name,script):
        raw=call(script).stdout
        assert digest(raw)==expected[name],("changed receipt",name)
        outputs[name]=raw
        return decode(raw)

    qdir,lead,brackets=(root/n for n in ("quote","direct","brackets"))
    for d in (qdir,lead,brackets):
        stage(d,"CALLER.json",data["CALLER.json"])
    stage(qdir,"R92-PRICE.json",data["R92-PRICE.json"])
    stage(qdir,"pricing.py",source("inputs/pricing.py"))
    qscript=engine(qdir,"quote.py")
    quote=record("PRICE.json",qscript)
    assert quote["pair"]==[1466,1487] and quote["ports"]==96
    assert quote["whole_singleton_stock"]=={"8":[[1466,7],[1487,25]],"9":[[1742,10],[1766,28]]}
    write(lead/"PRICE.json",outputs["PRICE.json"])
    stage(brackets,"PRICE.json",outputs["PRICE.json"])
    dscript=engine(lead,"derivative.py")
    rscript=engine(brackets,"projector_brackets.py")
    direct=record("DERIVATIVE.json",dscript)
    transported=record("BRACKETS.json",rscript)
    assert (direct["head"],direct["caller"],direct["pair"])==(
        transported["head"],transported["caller"],transported["scope"]["clocks"])
    assert direct["events"]==len(transported["literal"])==22
    assert transported["scope"]["interior_events"]==20
    assert direct["exact_rank"]==transported["rank"]==2
    assert direct["minor_columns"]==[["1","0"],["0","1"]]
    assert direct["determinant"]==transported["minor"]["determinant"]=="1"
    assert transported["exact_specialization"]["minor_determinant"]=="4"
    assert not transported["unresolved"]
    (brackets/"inputs/CALLER.json").unlink()
    for path,script,message in (
        (lead/"inputs/CALLER.json",dscript,b"changed dependency inputs/CALLER.json"),
        (brackets/"inputs/PRICE.json",rscript,b"changed dependency inputs/PRICE.json"),
        (qdir/"inputs/R92-PRICE.json",qscript,b"changed dependency inputs/R92-PRICE.json")):
        raw=path.read_bytes()
        path.write_bytes(raw+b" ")
        check=call(script,expect_success=False)
        assert check.returncode==1 and message in check.stderr
        path.write_bytes(raw)

    if out is not None:
        out.mkdir(parents=True)
        for name,raw in outputs.items():
            write(out/name,raw)
    print("PASS_P104_TYPE_A_SINGLETON_IDLE_PROJECTION_BOUND pairs=1 interior=20 inclusive=22 rank=2")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    cli=ArgumentParser(description=__doc__)
    cli.add_argument("--out",type=Path)
    args=cli.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
