"""Replay the fixed-paid rank-seven bank and prefix exclusion receipts."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path, PurePosixPath
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def decode(data):
    return loads(data, object_pairs_hook=unique)


def digest(data):
    return sha256(data).hexdigest()


def relative(name):
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or ".." in path.parts:
        raise ValueError(f"invalid relative path: {name}")
    return path


def authenticate():
    pins = decode((ROOT / "LOCAL-PINS.json").read_bytes())
    for path, expected in pins.items():
        if digest((ROOT / relative(path)).read_bytes()) != expected:
            raise ValueError(f"changed package dependency: {path}")
    provenance = decode((ROOT / "PROVENANCE.json").read_bytes())
    for path, record in provenance["files"].items():
        raw = (ROOT / relative(path)).read_bytes()
        assert digest(raw) == record["sha256"] == pins[path]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == record["git_blob"]
    for path, record in provenance["derived_inputs"].items():
        raw = (ROOT / relative(path)).read_bytes()
        if record.get("compression") == "gzip":
            raw = decompress(raw)
        expected = decode((ROOT / relative(record["receipt"])).read_bytes())
        for key in record["keys"]:
            expected = expected[key]
        assert digest(raw) == expected


def command(script, *args, timeout=25, check=True):
    result = run([sys.executable, "-I", "-B", str(script), *map(str,args)], capture_output=True, timeout=timeout)
    if check and result.returncode:
        sys.stderr.write(result.stderr.decode(errors="replace"))
        result.check_returncode()
    return result


def materialize(scratch):
    r102 = scratch / "round102-input"
    ind = scratch / "independent"
    for d in (r102/"inputs",r102/"lead",ind/"inputs"):
        d.mkdir(parents=True)
    for name in ("7334-CHANGED.json", "7334-WORD.json.gz", "ADMITTED.json", "READBACK.json",
                 "exterior_rank56.py", "pricing.py", "reverse_engine.py"):
        copyfile(ROOT/"inputs"/name,r102/"inputs"/name)
    (r102/"inputs/7314-HELPERS.json").write_bytes(decompress((ROOT/"inputs/7314-HELPERS.json.gz").read_bytes()))
    for name in ("quote.py","geometry.py","prefix.py"):
        copyfile(ROOT/"engines/r102"/name,r102/"lead"/name)
    for name in ("alias_rank_seven.py","freeze_support.py","modular_support.py"):
        copyfile(ROOT/"engines/r105"/name,scratch/name)
    for name in ("verify.py","r102_prefix.py"):
        copyfile(ROOT/"engines/independent"/name,ind/name)
    for name in ("r102_prefix.py","second_prime.py"):
        copyfile(ROOT/"engines/independent"/name,ind/"inputs"/name)
    copyfile(ROOT/"inputs/7334-WORD.json.gz",ind/"inputs/7334-WORD.json.gz")
    return r102,ind


def reconcile(geometry,old,old_second,alias,reverse,selection,modular,second):
    all_keys = {tuple(k) for k in geometry["all_representative_keys"]}
    assert len(all_keys) == geometry["eligible_bank_count"] == 65
    assert geometry["eligible_chart_count"] == 5 and geometry["status"] == "EXHAUSTED"
    old_keys = {tuple(r["key"]) for r in old["rows"] if r["determinant"]}
    assert old_keys == {tuple(r["key"]) for r in old_second["rows"] if r["independent_minor"]["determinant"]}
    assert len(old_keys) == 16 and old["counts"] == old_second["counts"] == {"excluded":16}
    assert all(r["chart_rank"] == 6 for r in old_second["rows"] + second["rows"])
    assert alias["classes"] == reverse["strict_classes"] == reverse["fixed_public_only_classes"]
    assert not reverse["diagnostic_additional_links"] and len(alias["classes"]) == 45
    assert len(alias["links"]) == 60 and sum(r["alias"] for r in alias["links"]) == 20
    chosen = {tuple(r["key"]):r for r in selection["selected"]}
    left = {tuple(r["key"]) for r in selection["unselected"]}
    assert chosen.keys() == {tuple(r["key"]) for r in modular["results"] if r["status"] == "prefix exclusion"}
    assert chosen.keys() == {tuple(r["key"]) for r in second["rows"] if r["independent_minor"]["determinant"]}
    assert len(chosen) == second["certified_primary_axes"] == 16
    assert modular["counts"] == second["counts"] == {"prefix exclusion":16}
    assert not old_keys & chosen.keys()
    disposition = {}
    for component in alias["classes"]:
        keys = list(map(tuple,component["keys"]))
        original = list(map(tuple,component["reuses"]))
        new = [k for k in keys if k in chosen]
        assert not (original and new) and len(original) <= 1 and len(new) <= 1
        if original:
            witness = original[0]
            for key in keys:
                disposition[key] = ("original direct minor" if key == witness else "original minor via alias",witness)
        elif new:
            witness = new[0]
            assert chosen[witness]["aliases"] == [list(k) for k in keys if k != witness]
            for key in keys:
                disposition[key] = ("continuation direct minor" if key == witness else "continuation minor via alias",witness)
        else:
            assert len(keys) == 1 and keys[0] in left
            disposition[keys[0]] = ("unresolved after cap",None)
    assert disposition.keys() == all_keys
    assert left == {k for k,(status,_) in disposition.items() if status == "unresolved after cap"}
    counts = Counter(s for s,_ in disposition.values())
    assert counts == {"original direct minor":16,"original minor via alias":9,"continuation direct minor":16,
                      "continuation minor via alias":11,"unresolved after cap":13}
    rows = [dict(key=k,disposition=disposition[k][0],witness=disposition[k][1]) for k in sorted(disposition)]
    return dict(head=HEAD,counts=counts,original=65,excluded=52,unresolved=13,rows=rows)


def replay(scratch,out):
    authenticate()
    expected = decode((ROOT / "receipts/SHA256.json").read_bytes())
    r102,ind = materialize(scratch)
    produced = {}

    def record(name, target, response):
        raw = response.stdout
        assert digest(raw) == expected[name], ("changed receipt",name)
        target.write_bytes(raw)
        produced[name] = raw
        return decode(raw)

    price = record("R102-PRICE.json",r102/"lead/PRICE.json",command(r102/"lead/quote.py"))
    assert price["head"] == HEAD and price["paid_delta"] == {} and price["productive_delta"] == {"3":17,"4":17,"7":-17}
    one = list(map(Fraction,price["at_incumbent"]["gross_one"]))
    margin = list(map(Fraction,price["at_incumbent"]["old_margin"]))
    assert 0 < one[0] <= one[1] < 1 and one[1]+margin[1] < 1
    assert Fraction(price["at_incumbent"]["whole_5_upper"]) == 5*one[1]
    assert Fraction(price["at_target"]["complete_5_upper"]) < 0
    geometry = record("R102-GEOMETRY.json",r102/"lead/GEOMETRY.json",
                      command(r102/"lead/geometry.py",r102,timeout=20))
    old = record("R102-PREFIX.json",r102/"lead/PREFIX.json",command(r102/"lead/prefix.py",r102))
    for name in ("PRICE.json","GEOMETRY.json","PREFIX.json"):
        copyfile(r102/"lead"/name,ind/"inputs"/name)
    old_second = record("R102-SECOND.json",ind/"inputs/PREFIX-SECOND-PRIME.json",command(ind/"r102_prefix.py"))
    alias = record("R105-ALIASES.json",scratch/"ALIASES.json",command(scratch/"alias_rank_seven.py",r102,timeout=20))
    copyfile(scratch/"ALIASES.json",ind/"inputs/ALIASES.json")
    reverse = record("R105-REVERSE.json",scratch/"REVERSE.json",command(ind/"verify.py","alias",timeout=20))
    selection = record("R105-SELECTION.json",scratch/"SELECTION.json",command(scratch/"freeze_support.py"))
    modular = record("R105-MODULAR.json",scratch/"MODULAR.json",command(scratch/"modular_support.py"))
    for name in ("SELECTION.json","MODULAR.json"):
        copyfile(scratch/name,ind/"inputs"/name)
    second = record("R105-SECOND.json",scratch/"SECOND.json",command(ind/"verify.py","modular"))
    summary = reconcile(geometry,old,old_second,alias,reverse,selection,modular,second)
    raw = (dumps(summary,indent=2,sort_keys=True)+"\n").encode()
    assert raw == (ROOT/"receipts/RECONCILED.json").read_bytes()
    assert set(produced) == set(expected)
    produced["RECONCILED.json"] = raw

    for victim,script,args in (
        (ind/"inputs/PRICE.json",ind/"verify.py",("alias",)),
        (r102/"inputs/7334-WORD.json.gz",r102/"lead/geometry.py",(r102,)),
    ):
        before = victim.read_bytes()
        victim.write_bytes(before+b"\n")
        failure = command(script,*args,check=False)
        assert failure.returncode == 1 and not failure.stdout
        assert b"changed dependency" in failure.stderr and victim.name.encode() in failure.stderr
        victim.write_bytes(before)

    if out is not None:
        out.mkdir(parents=True)
        for name,content in produced.items():
            (out / relative(name)).write_bytes(content)
    print("PASS_RANK_SEVEN_PREFIX_BANK_BOUND original=65 direct=32 transfers=20 excluded=52 unresolved=13")


def main():
    assert sys.version_info[:2] == (3,12) and __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,help="new directory for the ten regenerated receipts")
    args = parser.parse_args()
    with TemporaryDirectory() as directory:
        replay(Path(directory),args.out)


if __name__ == "__main__":
    main()
