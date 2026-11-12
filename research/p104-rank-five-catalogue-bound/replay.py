"""Replay exact rank-five catalogue and selected-cohort exclusions."""
from argparse import ArgumentParser
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


def replay(scratch,out):
    authenticate()
    expected=decode((ROOT/"receipts/SHA256.json").read_bytes())
    outputs={}

    def record(name,response,target=None):
        raw=response.stdout
        assert digest(raw)==expected[name],("changed receipt",name)
        outputs[name]=raw
        if target is not None:
            target.write_bytes(raw)
        return decode(raw)

    r114,r115=(scratch/name for name in ("r114","r115"))
    for root in (r114,r115):
        for folder in ("inputs","lead","independent/inputs"):
            (root/folder).mkdir(parents=True)
        for name in ("7334-WORD.json.gz","7334-CHANGED.json","ADMITTED.json","READBACK.json","pricing.py"):
            copyfile(ROOT/"inputs"/name,root/"inputs"/name)
        (root/"inputs/7314-HELPERS.json").write_bytes(decompress((ROOT/"inputs/7314-HELPERS.json.gz").read_bytes()))
    for root,names in ((r114,("quote","geometry")),(r115,("quote","geometry"))):
        for name in names:
            copyfile(ROOT/"engines"/root.name/f"{name}.py",root/"lead"/f"{name}.py")
    copyfile(ROOT/"engines/r114/gf2_catalogue.py",r114/"independent/gf2_catalogue.py")
    price114=record("R114-PRICE.json",command(r114/"lead/quote.py"),r114/"lead/PRICE.json")
    geom114=record("R114-GEOMETRY.json",command(r114/"lead/geometry.py",r114),r114/"lead/GEOMETRY.json")
    for name in ("PRICE.json","GEOMETRY.json"):
        copyfile(r114/"lead"/name,r114/"independent/inputs"/name)
    copyfile(r114/"inputs/7334-WORD.json.gz",r114/"independent/inputs/7334-WORD.json.gz")
    ind114=record("R114-INDEPENDENT.json",command(r114/"independent/gf2_catalogue.py"))
    assert price114["head"]==geom114["head"]==ind114["head"]==HEAD
    assert ind114["endpoints"]==[1090,127] and ind114["endpoint_ranks"]==[4,9]
    assert len(ind114["catalogue"])==336 and ind114["primary_agreement"]
    assert not geom114["intermediate_charts"] and not ind114["nested_charts"]
    assert geom114["visited_events"]==76466 and len(ind114["cohort_paid_moves"])==9

    for name in ("exterior_rank23.py","reverse_engine.py"):
        copyfile(ROOT/"inputs"/name,r115/"inputs"/name)
    copyfile(ROOT/"inputs/SELECTION.json",r115/"SELECTION.json")
    for name in ("alias","modular_support"):
        copyfile(ROOT/"engines/r115"/f"{name}.py",r115/f"{name}.py")
    for name in ("second_prefix","alias_check","second_prime","sweep"):
        sub="inputs/" if name in ("second_prime","sweep") else ""
        copyfile(ROOT/"engines/r115"/f"{name}.py",r115/"independent"/f"{sub}{name}.py")
    price115=record("R115-PRICE.json",command(r115/"lead/quote.py"),r115/"lead/PRICE.json")
    geom115=record("R115-GEOMETRY.json",command(r115/"lead/geometry.py"),r115/"lead/GEOMETRY.json")
    selection=decode((r115/"SELECTION.json").read_bytes())
    assert price115["head"]==geom115["head"]==selection["head"]==HEAD
    assert sum(len(g["roles"]) for g in price115["groups"])==80 and len(geom115["groups"])==28
    assert geom115["status"]=="EXHAUSTED" and geom115["visited_events"]==76466
    assert geom115["selected_group"]==selection["selected_group"]==[3,241]
    assert len(geom115["candidate_rows"])==68 and len(selection["selected"])==11
    keys={tuple(row["key"]) for row in geom115["candidate_rows"]}
    selected={tuple(r["key"])+tuple(selection["selected_group"]) for r in selection["selected"]}
    assert selected=={tuple(r["key"]) for r in geom115["selected"]}
    assert keys-selected==set(map(tuple,selection["unselected"]))
    assert sum(key[2:]==(3,241) for key in keys)==19

    primary=record("R115-MODULAR.json",command(r115/"modular_support.py"),r115/"lead/MODULAR.json")
    aliases=record("R115-ALIASES.json",command(r115/"alias.py",r115),r115/"lead/ALIASES.json")
    for name in ("ALIASES.json","GEOMETRY.json","MODULAR.json","PRICE.json"):
        copyfile(r115/"lead"/name,r115/"independent/inputs"/name)
    for name,source in (("SELECTION.json",r115/"SELECTION.json"),("7334-WORD.json.gz",r115/"inputs/7334-WORD.json.gz")):
        copyfile(source,r115/"independent/inputs"/name)
    second=record("R115-SECOND.json",command(r115/"independent/second_prefix.py"),r115/"independent/RESULT.json")
    comparison=record("R115-AGREEMENT.json",command(r115/"independent/alias_check.py"))
    assert outputs["R115-AGREEMENT.json"]==(ROOT/"receipts/R115-AGREEMENT.json").read_bytes()
    assert primary["counts"]=={"prefix exclusion":11} and second["agreement"]
    assert second["original_minor_axes_nonzero"]==11 and not second["unresolved_selected"]
    assert not aliases["unvisited"] and comparison["whole_group_excluded"]
    assert comparison["checked_aliases"]==8 and comparison["raw_banks"]==19
    assert len(keys)-comparison["raw_banks"]==49

    for name,script in (("SELECTION.json","second_prefix.py"),("ALIASES.json","alias_check.py")):
        path=r115/"independent/inputs"/name
        before=path.read_bytes()
        path.write_bytes(before+b"\n")
        changed=command(r115/"independent"/script,check=False)
        assert changed.returncode==1 and not changed.stdout and name.encode() in changed.stderr
        path.write_bytes(before)
    assert set(outputs)==set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name,raw in outputs.items():
            (out/relative(name)).write_bytes(raw)
    print("PASS_RANK_FIVE_CATALOGUE_BOUND roles=80 cohorts=28 raw=68 selected_closed=19 direct=11 aliases=8 outside=49")


def main():
    assert __debug__ and sys.version_info[:2]==(3,12)
    p=ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,help="new directory for the nine regenerated receipts")
    args=p.parse_args()
    with TemporaryDirectory() as directory:
        replay(Path(directory),args.out)


if __name__=="__main__":
    main()
