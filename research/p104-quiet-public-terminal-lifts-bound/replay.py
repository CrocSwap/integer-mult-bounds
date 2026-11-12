"""Replay the exact source-metadata proof for quiet public terminal lifts."""
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
    a=decode(source('inputs/ADMITTED.json'))
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
    materialized=load_inputs()
    materialized["7334-construct.py"]=source("inputs/7334-construct.py")
    expected=decode(source("receipts/SHA256.json"))
    for name,raw in materialized.items():
        write(root/"inputs"/name,raw)
    h9,stock=root/"check.py",root/"stock.py"
    write(h9,source("engines/check.py"))
    write(stock,source("engines/stock.py"))
    outputs={}
    for name,script in (("H9.json",h9),("ALL.json",stock)):
        raw=call(script).stdout
        assert digest(raw)==expected[name],("changed receipt",name)
        outputs[name]=raw
        if name=="H9.json":
            write(root/"inputs/R144-H9.json",raw)
    result=decode(outputs["ALL.json"])
    assert result["all_productive_helpers"]==1101 and result["non_H9_helpers"]==485
    assert result["H9_checked"]==615 and result["protected_H9"][:2]==[319,61388]
    assert not result["eligible"] and not result["unresolved"] and result["ideal_compatible_upper"]=="0"

    for script,name in ((h9,"R136-REVERSE.json"),(stock,"R62-REVERSE.json"),(stock,"7334-construct.py")):
        path=root/"inputs"/name
        old=path.read_bytes()
        path.write_bytes(old+b" ")
        rejected=call(script,expect_success=False)
        error=("changed " if script==h9 else "changed dependency ")+("inputs/"+name)
        assert rejected.returncode==1 and error.encode() in rejected.stderr
        path.write_bytes(old)

    if out is not None:
        out.mkdir(parents=True)
        for name,raw in outputs.items():
            write(out/name,raw)
    print("PASS_P104_QUIET_PUBLIC_TERMINAL_BOUND helpers=1101 h9=616 non_h9=485 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    cli=ArgumentParser(description=__doc__)
    cli.add_argument("--out",type=Path)
    args=cli.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
