"""Reproduce all distinct-mask odd-idle union prices and exclusions."""
from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
import sys

ROOT = Path(__file__).resolve().parent


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError("duplicate JSON key")
    return out


def decoded(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def source(name):
    p = Path(name)
    if p.is_absolute() or ".." in p.parts or p.as_posix() != name:
        raise ValueError(f"invalid relative dependency {name}")
    return (ROOT/p).read_bytes()


def checked_inputs():
    pins = decoded(source("LOCAL-PINS.json"))
    for name, expected in pins.items():
        if digest(source(name)) != expected:
            raise ValueError(f"changed package dependency {name}")
    provenance = decoded(source("PROVENANCE.json"))
    for name, row in provenance["public_inputs"].items():
        raw = source(name)
        if row.get("payload") == "gzip":
            raw = decompress(raw)
        assert digest(raw) == row["sha256"]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == row["git_blob"]
    admission = decoded(source("inputs/ADMITTED.json"))
    assert admission["head"] == provenance["comparator"]["head"]
    assert admission["caller"] == provenance["caller"]["head"]
    assert admission["kappa"] == "0.00364665195644" and admission["exit"] == 0
    predecessor = decoded(source("inputs/7357-SHA256.json"))
    assert predecessor["PRICE.json"] == digest(source("inputs/R85-PRICE.json"))


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def invoke(script, *args, checked=True):
    p = run([sys.executable,"-I","-B",str(script),*args],capture_output=True,timeout=28)
    if checked and p.returncode:
        sys.stderr.write(p.stderr.decode(errors="replace"))
        p.check_returncode()
    return p


def normalized(report):
    rows = {}
    for row in report["schedules"]:
        key = tuple(map(tuple,row["pairs"])), tuple(row["kept"])
        assert key not in rows
        rows[key] = row["decision"], row["witnesses"]
    return rows


def replay(root):
    checked_inputs()
    hashes = decoded(source("receipts/SHA256.json"))
    outputs = {}

    def save(name, script, *args):
        raw = invoke(script,*args).stdout
        assert digest(raw) == hashes[name], f"changed deterministic receipt {name}"
        outputs[name] = raw
        return decoded(raw)

    quote_root = root/"quote"
    quote = quote_root/"quote.py"
    write(quote, source("engines/quote.py"))
    for name in ("R85-PRICE.json","pricing.py"):
        write(quote_root/"inputs"/name,source("inputs/"+name))
    price = save("PRICE.json",quote)
    stage = root/"stage"
    write(stage/"inputs/PRICE.json",outputs["PRICE.json"])
    for name in ("7113-CALLER.json.gz","direct_impulse.py","7295-CERTIFICATE.json",
                 "7295-PROVENANCE.json","7295-trace_and_price.py"):
        write(stage/"inputs"/name,source("inputs/"+name))
    lead = stage/"lead/projectors.py"
    audit = stage/"independent/contact_sets.py"
    write(lead,source("engines/projectors.py"))
    write(audit,source("engines/contact_sets.py"))
    primary = save("PRIMARY.json",lead)
    independent = save("CONTACT-SETS.json",audit,"--root",str(stage))
    for name in ("PRIMARY.json","CONTACT-SETS.json"):
        assert outputs[name] == source("receipts/"+name)
    assert primary["head"] == independent["head"] == price["head"]
    assert primary["caller"] == independent["caller"] == price["caller"]
    assert primary["events"] == independent["events"] == 4783
    assert primary["caps"] == independent["caps"] == [4,16,20]
    assert primary["projectors"] == independent["projectors"]
    assert primary["unresolved"] == independent["unresolved"] == 0
    schedules = normalized(primary)
    assert schedules == normalized(independent) and len(schedules) == 16
    assert sum(len(key[0]) == 1 for key in schedules) == 8
    assert all(v[0] == "derivative excluded" and v[1] for v in schedules.values())

    def reject(path, script, *args, message=b"changed dependency"):
        original = path.read_bytes()
        try:
            path.write_bytes(original+b" ")
            result = invoke(script,*args,checked=False)
            assert result.returncode == 1 and message in result.stderr
        finally:
            path.write_bytes(original)

    reject(quote_root/"inputs/R85-PRICE.json",quote,message=b"changed inputs/R85-PRICE.json")
    reject(stage/"inputs/PRICE.json",lead)
    reject(stage/"inputs/7113-CALLER.json.gz",lead)
    reject(stage/"inputs/7295-CERTIFICATE.json",audit,"--root",str(stage))
    return outputs


def main():
    assert __debug__
    if sys.version_info[:2] != (3,12):
        raise RuntimeError("CPython 3.12 is required")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="odd-idle-") as scratch:
        outputs = replay(Path(scratch))
    if args.out:
        args.out.mkdir(parents=True,exist_ok=False)
        for name,raw in outputs.items():
            write(args.out/name,raw)
    print("PASS_ODD_IDLE_UNIONS 16 exact schedules excluded; 0 unresolved; 4 mutation controls")


if __name__ == "__main__":
    main()
