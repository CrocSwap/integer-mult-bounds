"""Replay the exact temporal outer-bank exclusion for owned role 1531."""
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
    manifest=decode(source("inputs/PR7378-SHA256.json"))
    for name,entry in p["derived_inputs"].items():
        assert digest(source(name))==entry["sha256"]
        if "key" in entry:
            assert digest(source(name))==manifest[entry["key"]]
    return p


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
    load_inputs()
    expected=decode(source("receipts/SHA256.json"))
    outputs={}

    def record(name,script,*args):
        raw=call(script,*args).stdout
        assert digest(raw)==expected[name],("changed deterministic receipt",name)
        outputs[name]=raw
        return decode(raw)

    lead=root/"lead"
    for name in ("PLAN.md","R122-PRICE.json","R122-RESULT.json","7334-WORD.json.gz"):
        write(lead/"inputs"/name,source("inputs/"+name))
    engine=lead/"temporal_outer.py"
    write(engine,source("engines/temporal_outer.py"))
    quote=record("PRICE.json",engine,"--price-only")
    write(lead/"PRICE.json",outputs["PRICE.json"])
    result=record("LEAD.json",engine)
    assert outputs["LEAD.json"]==source("receipts/ALIASES.json")
    assert quote["switches"]=={"early":41996,"late":44242}
    assert result["status"]=="both schedules excluded" and not result["unresolved"]
    assert (result["events"],result["bank_cuts"],result["donor_incidences"])==(76466,4494,7163)
    assert {c:len(rows) for c,rows in result["aliases"].items()}=={"534":4,"594":5}
    assert all(not row["nonzero"] for rows in result["aliases"].values() for row in rows)
    assert result["owner_diagonal"]==[41996,"0"] and result["aggregate_response"]=="-1/2"

    reverse=root/"independent"
    for name,raw in (
        ("PRICE.json",outputs["PRICE.json"]),
        ("FORWARD.json",outputs["LEAD.json"]),
        ("7334-WORD.json.gz",source("inputs/7334-WORD.json.gz"))):
        write(reverse/"inputs"/name,raw)
    reverse_engine=reverse/"reverse.py"
    write(reverse_engine,source("engines/reverse.py"))
    independent=record("INDEPENDENT.json",reverse_engine,"--root",str(reverse))
    assert not independent["unresolved"]
    assert independent["copy_prewrite"]==[[33805,1525,"0"]]
    for field in ("head","caller","events","bank_cuts","donor_incidences","owner_diagonal",
                  "old_source_responses","aggregate_response"):
        assert independent[field]==result[field]
    observed={(r["chart"],r["first"],r["last"]):r for r in independent["aliases"]}
    assert len(observed)==9
    for chart,rows in result["aliases"].items():
        for row in rows:
            alias=observed.pop((int(chart),row["first"],row["last"]))
            assert alias["roles"]==row["roles"] and alias["owned_births"]==row["owned_births"]
            assert alias["coordinate_244"]==[[role,"0"] for role in row["roles"]]
    assert not observed

    (reverse/"inputs/7334-WORD.json.gz").unlink()
    forward=reverse/"inputs/FORWARD.json"
    forward.write_bytes(forward.read_bytes()+b" ")
    rejection=call(reverse_engine,"--root",str(reverse),expect_success=False)
    assert rejection.returncode==1 and b"changed dependency inputs/FORWARD.json" in rejection.stderr
    (lead/"inputs/7334-WORD.json.gz").unlink()
    for name in ("R122-PRICE.json","R122-RESULT.json"):
        path=lead/"inputs"/name
        saved=path.read_bytes()
        path.write_bytes(saved+b" ")
        rejection=call(engine,expect_success=False)
        assert rejection.returncode==1 and b"changed dependency" in rejection.stderr
        path.write_bytes(saved)

    assert set(outputs)==set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name,raw in outputs.items():
            write(out/name,raw)
    print("PASS_P104_OWNED_OUTER_TEMPORAL_BOUND switches=2 bank_cuts=4494 aliases=9 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    cli=ArgumentParser(description=__doc__)
    cli.add_argument("--out",type=Path)
    args=cli.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
