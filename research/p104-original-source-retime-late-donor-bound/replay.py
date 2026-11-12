"""Replay original-source chronology and late public donor exclusions."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha1, sha256
from json import loads
from pathlib import Path, PurePosixPath
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
WORD = "7334-WORD.json.gz"


def unique(pairs):
    data = dict(pairs)
    if len(data) != len(pairs):
        raise ValueError("duplicate JSON key")
    return data


def decode(raw):
    return loads(raw,object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def safe(name):
    path = PurePosixPath(name)
    if not path.parts or path.is_absolute() or path.as_posix() != name or ".." in path.parts:
        raise ValueError("invalid local path " + name)
    return path


def install(source, destination):
    destination.parent.mkdir(parents=True,exist_ok=True)
    copyfile(source,destination)


def command(script,*args,check=True,timeout=20):
    return run([sys.executable,"-I","-B",str(script),*map(str,args)],
               capture_output=True,check=check,timeout=timeout)


def verify_inputs():
    pins = decode((HERE/"LOCAL-PINS.json").read_bytes())
    for name,expected in pins.items():
        if digest((HERE/safe(name)).read_bytes()) != expected:
            raise ValueError("changed dependency " + name)
    provenance = decode((HERE/"PROVENANCE.json").read_bytes())
    for name,row in provenance["files"].items():
        raw = (HERE/safe(name)).read_bytes()
        assert digest(raw) == row["sha256"]
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest() == row["git_blob"]
    for name,row in provenance["derived_inputs"].items():
        receipt = decode((HERE/safe(row["receipt"])).read_bytes())
        assert digest((HERE/safe(name)).read_bytes()) == receipt[row["key"]]
    admission = decode((HERE/"inputs/ADMITTED.json").read_bytes())
    parent = decode((HERE/"inputs/R101-PRICE.json").read_bytes())
    assert admission["exit"] == 0 and admission["head"] == parent["head"]
    assert admission["caller"] == parent["caller_head"]
    assert admission["inputs"]["WORD.json.gz"] == parent["word_sha256"]


def verify_separators(price, exact):
    rows = exact["exact_integer_rows"]
    summaries = decode((HERE/"receipts/SEPARATORS.json").read_bytes())
    adds = {tuple(r["key"]):Fraction(r["add"][1][3]) for r in price["candidates"]}
    sizes = []
    for summary,case in zip(summaries,exact["results"],strict=True):
        for field in ("key","cut","chart","source","owned_donors_excluded"):
            assert summary[field] == case[field]
        assert summary["donors"] == case["bank_roles"]
        probe = {axis:Fraction(weight) for axis,weight in summary["covector"].items()}
        assert summary["covector"] == case["proof"]["separating_covector"]

        def apply(index):
            numerator,denominator = rows[index]
            return sum((Fraction(numerator.get(axis,0),denominator)*v for axis,v in probe.items()),Fraction())

        target = apply(case["target_row_id"])
        assert target == Fraction(summary["source_value"]) != 0
        assert target*adds[tuple(case["key"][:3])] == Fraction(summary["signed_add_value"])
        assert all(apply(i)==0 for _,i in case["donor_role_row_ids"])
        sizes.append(len(probe))
        if len(probe) == 2:
            assert case["key"] == [40102,44609,205,"exit"] and case["chart"] == 207
            assert probe == {"58":Fraction(1),"1493":Fraction(-1,2)}
            assert target == 1 and Fraction(summary["signed_add_value"]) == Fraction(-1,2)
    assert sorted(sizes) == [1]*9+[2]


def replay(root,output):
    verify_inputs()
    wanted = decode((HERE/"receipts/SHA256.json").read_bytes())
    regenerated = set()

    def stage(label,script,*args):
        raw = command(script,*args).stdout
        if digest(raw) != wanted[label]:
            raise ValueError(f"changed receipt {label}: {digest(raw)}")
        assert label not in regenerated
        regenerated.add(label)
        dest = root/safe(label)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(raw)
        return decode(raw)

    prior,late = root/"r103",root/"r104"
    for folder,name,leading,independent in (
        (prior,"r103",("quote.py","retime.py"),"reverse_retime.py"),
        (late,"r104",("support.py",),"reverse_late.py"),
    ):
        for name_py in leading:
            install(HERE/"engines"/name/name_py,folder/"lead"/name_py)
        install(HERE/"engines"/name/independent,folder/"independent"/independent)
        for destination in (folder/"inputs",folder/"independent/inputs"):
            install(HERE/"inputs"/WORD,destination/WORD)

    install(HERE/"inputs/R101-PRICE.json",prior/"inputs/R101-PRICE.json")
    install(HERE/"inputs/R101-PRICE.json",prior/"independent/inputs/R101-PRICE.json")
    price = stage("r103/lead/PRICE.json",prior/"lead/quote.py")
    assert len(price["candidates"]) == 5 and price["limits"]["typed_cuts"] == 18864
    assert price["full_paid_after_one"] == 110502 and price["productive"] == 22461
    assert 0 < Fraction(price["one_net_upper"]) < Fraction(price["whole_net_upper"]) < 1
    retime = stage("r103/lead/RETIMING.json",prior/"lead/retime.py")
    assert retime["counts"] == {"different chart":18864} and not retime["timeout"]
    assert retime["first_unvisited_event"] is retime["first_unvisited_cut"] is None
    for label in ("PRICE","RETIMING"):
        install(prior/f"lead/{label}.json",prior/f"independent/inputs/{label}.json")
    reverse = prior/"independent/reverse_retime.py"
    chronology = stage("r103/independent/RESULT.json",reverse)
    assert chronology["complete"] and chronology["agreement"] and not chronology["timeout"]
    assert chronology["progress"]["events_replayed"] == 76466
    assert chronology["progress"]["typed_cuts_replayed"] == 18864

    install(prior/"lead/PRICE.json",late/"lead/PRICE.json")
    install(prior/"lead/RETIMING.json",late/"inputs/R103-RETIMING.json")
    install(HERE/"inputs/donor_span.py",late/"inputs/donor_span.py")
    support = stage("r104/lead/SUPPORT.json",late/"lead/support.py")
    assert support["counts"] == {"outside donor span":10} and not support["unvisited"]
    install(prior/"lead/PRICE.json",late/"independent/inputs/PRICE.json")
    install(HERE/"engines/r104/reverse_span.py",late/"independent/reused/reverse_span.py")
    donors = late/"independent/reverse_late.py"
    exact = stage("r104/independent/RESULT.json",donors)
    assert exact["counts"] == support["counts"] and not exact["unvisited"]
    assert len(exact["exact_integer_rows"]) == 132
    agreement = stage("r104/independent/AGREEMENT.json",donors,"--primary",late/"lead/SUPPORT.json")
    assert agreement["bank_status_agreement"] == agreement["rank_agreement"] == 10
    verify_separators(price,exact)

    for source,directory,name in ((reverse,prior/"independent","PRICE.json"),
                                  (donors,late/"independent",WORD)):
        target = directory/"inputs"/name
        original = target.read_bytes()
        target.write_bytes(original+b"\n")
        try:
            bad = command(source,check=False,timeout=10)
            assert bad.returncode == 1 and not bad.stdout and name.encode() in bad.stderr
        finally:
            target.write_bytes(original)

    assert regenerated == set(wanted)
    if output:
        for name in sorted(regenerated):
            install(root/safe(name),output/safe(name))
    print("PASS_P104_RETIME_LATE_DONORS typed_cuts=18864 wrong_chart=18864 late_banks=10 separators=10 unresolved=0 receipts=6")


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,help="Optional directory for regenerated receipts")
    args = parser.parse_args()
    with TemporaryDirectory(prefix="p104-retime-late-") as temporary:
        replay(Path(temporary),args.output)


if __name__ == "__main__":
    main()
