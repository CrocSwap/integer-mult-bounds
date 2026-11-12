"""Replay fixed Type B two-return incidence and canonical capacity."""
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
    receipts={}
    def stage(directory,name,origin=None):
        write(directory/"inputs"/name,data[origin or name])
    def install(directory,name):
        path=directory/name
        write(path,source("engines/"+name))
        return path
    def record(name,script):
        raw=call(script).stdout
        assert digest(raw)==expected[name],("changed receipt",name)
        receipts[name]=raw
        return decode(raw)
    for name in ("7113-SHA256.json","7334-ADMITTED.json","PR7344-CONTRACT.json","pricing.py","WORD.json.gz"):
        data[name]=source("inputs/"+name)
    quote,lead,independent=(root/n for n in ("quote","lead","independent"))
    for name in ("R149-PRICE.json","R85-PRICE.json","pricing.py","PR7344-CONTRACT.json"):
        stage(quote,name)
    qscript=install(quote,"quote_volume.py")
    volume=record("QUOTE.json",qscript)
    data["QUOTE.json"]=receipts["QUOTE.json"]
    assert volume["phase"]==[72,64,56,64] and volume["need"]=="15/16"
    for a,b in (("APPLICATION.py","upstream_application.py"),("EMITTER.py","emit_odd_type_ab.py"),
        ("PHYSICAL-BINDING.py","check_odd_physical_binding.py"),("CALLER.json","CALLER.json"),
        ("DATA-PHASES.json","DATA-PHASES.json"),("PRICE.json","R149-PRICE.json"),
        ("VOLUME-QUOTE.json","QUOTE.json"),("WORD.json.gz","WORD.json.gz")):
        stage(lead,a,b)
    ls=install(lead,"signed_returns.py")
    literal=record("LITERAL.json",ls)
    for name in ("7113-SHA256.json","7334-ADMITTED.json","PLAN.md","QUOTE.json","CONTRACT-READBACK.json",
        "PR7344-CONTRACT.json","CALLER.json","check_odd_physical_binding.py","upstream_application.py",
        "emit_odd_type_b.py","emit_odd_type_ab.py","signed_model.py","independent.py","lower.py",
        "odd_unit_dyadic_tapes.py","ODD-LOCALIZED-GROUPING.json","mirrored.py"):
        stage(independent,name)
    rs=install(independent,"physical_trace.py")
    emitter=record("EMITTER.json",rs)
    assert (literal["head"],literal["caller"],literal["clocks"])==(
        emitter["head"],emitter["caller"],emitter["clocks"])
    assert (literal["events"],literal["recorded_source_width"],literal["volume_test_width"])==(4783,73,8)
    assert literal["hits"]=={"68":[[1339,"IDLE_ODD"]],"70":[[2970,"IDLE_ODD"]]}
    assert not literal["unresolved"] and not emitter["q_sensitive_retained_path_to_selected_returns"]
    phases=("1","i","-1","-i")
    coords=dict(zip(phases,([1,0],[0,1],[-1,0],[0,-1]),strict=True))
    by_phase={(r["port"],phases[r["phase"]]):r for r in literal["cases"]}
    assert len(by_phase)==len(emitter["comparisons"])==32
    for row in emitter["comparisons"]:
        other=by_phase.pop((row["port"],row["q"]))
        assert other["required_at_unit_bodies"]==[coords[row["signed_coefficient"]]]*2
        assert other["correction"]==coords[row["translation_coefficient"]]
        assert other["opposite_q_difference_rank"]==row["opposite_pair_required_rank"]==2
        assert other["retained_odd_rank"]==row["fixed_erased_normalized_rank"]==0
    assert not by_phase
    for d,name,script in ((quote,"R149-PRICE.json",qscript),(lead,"CALLER.json",ls),
                          (independent,"emit_odd_type_b.py",rs)):
        path=d/"inputs"/name
        raw=path.read_bytes()
        path.write_bytes(raw+b" ")
        check=call(script,expect_success=False)
        assert check.returncode==1 and b"changed dependency" in check.stderr
        path.write_bytes(raw)
    if out is not None:
        out.mkdir(parents=True)
        for name,raw in receipts.items():
            write(out/name,raw)
    print("PASS_P104_FIXED_TYPE_B_TWO_RETURN_BOUND clocks=2 ports=8 phases=32 ranks=16,18")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    cli=ArgumentParser(description=__doc__)
    cli.add_argument("--out",type=Path)
    args=cli.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
