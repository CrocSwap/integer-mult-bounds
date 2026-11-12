"""Rebuild the exact existing-bank and singleton virtual-cut exclusions."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha1, sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"


def unique(pairs):
    result=dict(pairs)
    if len(result)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def decode(raw):
    return json.loads(raw,object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def relative(name):
    path=PurePosixPath(name)
    if path.is_absolute() or path.as_posix()!=name or ".." in path.parts:
        raise ValueError("invalid replay path: "+name)
    return path


def authenticate():
    pins=decode((HERE/"LOCAL-PINS.json").read_bytes())
    for name,expected in pins.items():
        if digest((HERE/relative(name)).read_bytes())!=expected:
            raise ValueError("changed dependency: "+name)
    provenance=decode((HERE/"PROVENANCE.json").read_bytes())
    for name,record in provenance["files"].items():
        raw=(HERE/relative(name)).read_bytes()
        assert not record["uncompress"] and digest(raw)==record["sha256"]==pins[name]
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()==record["git_blob"]
    stock=provenance["generated"]["r92/price/inputs/RANK-STOCK.json"]
    manifest=decode((HERE/relative(stock["manifest"])).read_bytes())
    assert manifest[stock["key"]]==pins["r92/price/inputs/RANK-STOCK.json"]


def command(script,*args,timeout=20,check=True):
    argv=[sys.executable,"-I","-B",str(HERE/script),*map(str,args)]
    run=subprocess.run(argv,capture_output=True,timeout=timeout)
    if check and run.returncode:
        sys.stderr.write(run.stderr.decode(errors="replace"))
        run.check_returncode()
    return run


def replay(scratch,output):
    authenticate()
    expected=decode((HERE/"receipts/SHA256.json").read_bytes())
    actual={}

    def record(name,raw):
        assert digest(raw)==expected[name],("changed receipt",name)
        actual[name]=raw
        path=scratch/relative(name)
        path.write_bytes(raw)
        return path,decode(raw)

    word=HERE/"inputs/7334-WORD.json.gz"
    price_path,price=record("R92-PRICE.json",command("r92/price/quote.py").stdout)
    assert price["head"]==HEAD and price["public_paid_stock"]["2"]==844
    assert price["rank_surplus"]==1424 and price["empty_root_credits"]==0
    assert (price["full_paid_positions_before"],price["full_paid_positions_after"])==(110519,110536)
    assert (price["productive_positions_before"],price["productive_positions_after"])==(22461,22478)
    forward_path,forward=record("R92-GEOMETRY.json",command("r92/lead/geometry.py","--price",price_path,
        "--word",word,timeout=25).stdout)
    assert forward["events_replayed"]==76466 and forward["first_unvisited_event"] is None
    assert forward["counts"]=={"cohort_rank_two_crossings":95,"no_existing_chart":254,
        "rank_two_public_moves":844,"unoccupied_or_guarded":31}
    assert not forward["eligible"] and not forward["selected"] and not forward["unvisited_support_keys"]
    guards_path,guards=record("R92-GUARDS.json",command("r92/lead/guard_audit.py","--price",price_path,
        "--geometry",forward_path,"--word",word,timeout=25).stdout)
    assert guards["counts"]=={"empty_chart":31} and not guards["unresolved_in_scoped_geometry"]

    reverse_root=scratch/"reverse"
    (reverse_root/"inputs").mkdir(parents=True)
    for path,name in ((word,"7334-WORD.json.gz"),(price_path,"PRICE.json"),(HERE/"inputs/R92-PLAN.md","PLAN.md")):
        shutil.copyfile(path,reverse_root/"inputs"/name)
    reverse_path,reverse=record("R92-REVERSE.json",command("r92/independent/reverse_geometry.py",reverse_root,timeout=25).stdout)
    assert reverse["status"]=="EXHAUSTED" and not reverse["eligible"] and not reverse["selected"] and not reverse["unselected"]
    _,geom_compare=record("R92-COMPARE.json",command("r92/independent/compare.py",forward_path,
        guards_path,reverse_path).stdout)
    assert geom_compare["matched_quotient_placements"]==285 and geom_compare["matched_existing_label_banks"]==31
    assert not geom_compare["eligible"] and not geom_compare["unresolved"]

    quote_root=scratch/"singleton-price"
    (quote_root/"inputs").mkdir(parents=True)
    shutil.copyfile(HERE/"r93/lead/quote.py",quote_root/"quote.py")
    for path,name in ((price_path,"R92-PRICE.json"),(forward_path,"GEOMETRY.json"),(guards_path,"GUARDS.json")):
        shutil.copyfile(path,quote_root/"inputs"/name)
    singleton_path,singleton_price=record("R93-PRICE.json",command(quote_root/"quote.py").stdout)
    assert len(singleton_price["keys"])==95 and singleton_price["midpoint_subspaces"]==285
    quote=singleton_price["one_edit"]
    assert quote["paid_delta"]=={"1":34,"2":-17} and quote["target_delta"]=={"4":17,"5":17,"9":-17}
    assert Fraction(quote["full_probe"][0])>0 and Fraction(singleton_price["whole_complete_margin_at_moonshot_upper"])<0
    modular_path,modular=record("R93-MODULAR.json",command("r93/lead/singleton.py","--price",singleton_path,
        "--word",word,timeout=25).stdout)
    assert modular["counts"]=={"exterior_on_both":95} and len(modular["denominator_units"])==98
    assert not modular["unresolved"] and not modular["unvisited"] and not modular["exact_selected"]

    rational_root=scratch/"rational"
    (rational_root/"inputs").mkdir(parents=True)
    shutil.copytree(HERE/"r93/independent/reused",rational_root/"reused")
    for path,name in ((word,"7334-WORD.json.gz"),(singleton_path,"PRICE.json"),
                      (reverse_path,"R92-REVERSE.json"),(HERE/"inputs/R93-PLAN.md","PLAN.md")):
        shutil.copyfile(path,rational_root/"inputs"/name)
    rational_path,rational=record("R93-RATIONAL.json",command("r93/independent/singleton.py",rational_root,timeout=25).stdout)
    assert rational["counts"]=={"no_nonzero_pure_prefix":95} and not rational["survivors"] and not rational["unvisited"]
    _,proof=record("R93-COMPARE.json",command("r93/independent/compare.py",modular_path,rational_path).stdout)
    assert proof["matched_nonzero_prefix_witnesses"]==proof["matched_nonzero_suffix_witnesses"]==95
    assert not proof["unresolved"] and not proof["paired_support_tests"]

    for root,relative_path,script in ((reverse_root,"inputs/7334-WORD.json.gz","r92/independent/reverse_geometry.py"),
                                     (rational_root,"inputs/PRICE.json","r93/independent/singleton.py")):
        changed=root/relative_path
        changed.write_bytes(changed.read_bytes()+b"\n")
        rejection=command(script,root,check=False)
        assert rejection.returncode==1 and not rejection.stdout
        assert f"changed dependency: {relative_path}".encode() in rejection.stderr

    assert set(actual)==set(expected)
    if output is not None:
        output.mkdir(parents=True)
        for name,raw in actual.items():
            (output/relative(name)).write_bytes(raw)
    print("PASS_RANK_TWO_VIRTUAL_CUT_BOUND placements=285 no_label=254 empty=31 singleton=95 unresolved=0")


def main():
    if sys.version_info[:2]!=(3,12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,help="new directory for all nine regenerated receipts")
    args=parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp),args.out)


if __name__=="__main__":
    main()
