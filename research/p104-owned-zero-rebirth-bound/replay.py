"""Replay the exact single-site and paired P104 owned zero-rebirth exclusions."""
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
    old=decompress(source('inputs/R92-PRICE.json.gz'))
    assert digest(old)==decode(source('inputs/PR7362-SHA256.json'))['R92-PRICE.json']
    a=decode(source('inputs/ADMITTED.json'))
    assert a['head']=='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
    assert a['kappa']=='0.00364665195644'
    return old


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
    old_price = load_inputs()
    expected = decode(source("receipts/SHA256.json"))
    outputs = {}

    def engine(directory, program, script=None):
        target = directory / (script or program)
        write(target,source("engines/"+program))
        return target

    def record(name,script,*args):
        proc = call(script,*args)
        raw = proc.stdout
        assert digest(raw) == expected[name], ("changed deterministic receipt",name)
        outputs[name] = raw
        return decode(raw)

    prefix, lead, independent, pairs, pair_check = (
        root/key for key in ("prefix","lead","independent","pairs","pair-check"))
    for d in (prefix,lead,independent):
        write(d/"inputs/7334-WORD.json.gz",source("inputs/7334-WORD.json.gz"))
    for name in ("R80-OWNED.json","aggregate.py","donor_span.py","pricing.py"):
        write(prefix/"inputs"/name,source("inputs/"+name))
    write(prefix/"inputs/R92-PRICE.json",old_price)
    prefix_engine = engine(prefix,"first_use.py","lead/first_use.py")
    record("R137-PRICE.json",prefix_engine,"--price-only")
    p = record("R137-LEAD.json",prefix_engine)
    assert p["counts"] == {"outside donor span":47} and not p["unvisited"]
    assert all(r["row"] for r in p["records"])

    for d, names in ((lead,("PRICE.json","RESULT.json")),
                     (independent,("R137-PRICE.json","R137-RESULT.json")),
                     (pairs,("R137-PRICE.json","R137-RESULT.json"))):
        for name, label in zip(names,("R137-PRICE.json","R137-LEAD.json"),strict=True):
            write(d/"inputs"/name,outputs[label])
    lead_engine = engine(lead,"lead_suffix.py","lead/guarded_suffix.py")
    record("R139-PRICE.json",lead_engine,"--price-only")
    single = record("R139-LEAD.json",lead_engine)
    assert not single["survivors"] and not single["unresolved"]
    write(independent/"inputs/R139-PRICE.json",outputs["R139-PRICE.json"])
    write(independent/"inputs/R139-LEAD-RESULT.json",outputs["R139-LEAD.json"])
    independent_engine = engine(independent,"guarded_suffix.py")
    independent_args = ("--price-sha",expected["R139-PRICE.json"])
    record("R139-INDEPENDENT.json",independent_engine,*independent_args)
    write(independent/"RESULT.json",outputs["R139-INDEPENDENT.json"])
    agreement = record("R139-AGREEMENT.json",engine(independent,"compare_suffix.py","compare.py"))
    assert agreement["copy_guard_checks"] == 11 and agreement["copy_guard_nonzero"] == 0
    assert outputs["R139-AGREEMENT.json"] == source("receipts/SUFFIX-AGREEMENT.json")

    write(pairs/"inputs/R139-RESULT.json",outputs["R139-LEAD.json"])
    write(pairs/"inputs/R92-PRICE.json",old_price)
    write(pairs/"inputs/pricing.py",source("inputs/pricing.py"))
    pair_engine = engine(pairs,"pair_screen.py","lead/pair_screen.py")
    record("R140-PRICE.json",pair_engine,"--price-only")
    paired = record("R140-LEAD.json",pair_engine)
    assert not paired["unresolved"]
    for name,label in (
        ("R137-RESULT.json","R137-LEAD.json"),
        ("R139-INDEPENDENT-RESULT.json","R139-INDEPENDENT.json"),
        ("R140-PRICE.json","R140-PRICE.json"),
        ("R140-LEAD-RESULT.json","R140-LEAD.json")):
        write(pair_check/"inputs"/name,outputs[label])
    audit_engine = engine(pair_check,"pair_audit.py")
    audit = record("R140-INDEPENDENT.json",audit_engine)
    assert outputs["R140-INDEPENDENT.json"] == source("receipts/PAIR-WITNESSES.json")
    assert audit["counts"] == paired["counts"] == {
        "different guarded suffix support":8, "independent prefix rows":1073}
    assert len(audit["exact_suffix_witnesses"]) == 8 and not audit["unresolved"]
    assert set(outputs) == set(expected)

    (independent/"inputs/7334-WORD.json.gz").unlink()
    for path,script,args in (
        (independent/"inputs/R139-PRICE.json",independent_engine,independent_args),
        (pair_check/"inputs/R139-INDEPENDENT-RESULT.json",audit_engine,())):
        path.write_bytes(path.read_bytes()+b" ")
        proc = call(script,*args,expect_success=False)
        assert proc.returncode == 1 and b"changed dependency" in proc.stderr

    if out is not None:
        out.mkdir(parents=True)
        for name,raw in outputs.items():
            write(out/name,raw)
    print("PASS_P104_OWNED_ZERO_REBIRTH_BOUND single=47 paired=1081 guards=11 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("--out",type=Path)
    args = cli.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__ == "__main__":
    main()
