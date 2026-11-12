"""Replay the source-side retiming and fixed crossed-read exclusions."""
from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
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
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def decode(raw):
    return loads(raw,object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def safe(name):
    path = PurePosixPath(name)
    if not path.parts or path.is_absolute() or path.as_posix() != name or ".." in path.parts:
        raise ValueError("invalid local path " + name)
    return path


def install(source,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    copyfile(source,dest)


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
    unpacked = {}
    for name,row in provenance["derived_inputs"].items():
        assert row["compression"] == "gzip"
        receipt = decode((HERE/safe(row["receipt"])).read_bytes())
        raw = decompress((HERE/safe(name)).read_bytes())
        assert digest(raw) == receipt[row["key"]]
        unpacked[name] = raw
    return unpacked


def check_response(summary,price,exact):
    b = exact["bank"]
    assert summary["paid_key"] == price["key"] == [44611,46018,532]
    assert summary["old_read_cut"] == b["cut"] == 44613
    assert summary["old_read_chart"] == b["chart"] == 207
    assert summary["public_donors"] == b["public"] and len(b["public"]) == 9
    assert summary["owned_excluded"] == b["owned_excluded"] == [1567]
    assert 198 in b["public"] and 205 in b["public"] and 532 not in b["public"]
    proof = b["proof"]
    assert summary["donor_rank"] == proof["donor_rank"] == 9
    assert summary["augmented_rank"] == proof["augmented_rank"] == 10
    assert summary["separating_covector"] == proof["separating_covector"] == {"27":"1"}

    def axis(row):
        entries,denominator = row
        return Fraction(entries.get("27",0),denominator)

    assert axis(b["old_205_row"]) == Fraction(-1,2)
    assert all(axis(row) == 0 for row in b["adjusted_public_rows"].values())
    assert axis(b["original_source_row"]) == Fraction(summary["original_source_value"]) == 1
    assert axis(b["target_row"]) == Fraction(summary["missing_signed_response"]) == Fraction(1,4)
    assert Fraction(price["old_add"][1][3])*Fraction(price["crossed"][1][3]) == axis(b["target_row"])
    assert summary["late_range"] == price["cuts"] == [45976,46018]
    assert summary["late_count"] == len(exact["typed_late_cuts"]) == 43
    assert [r["cut"] for r in exact["typed_late_cuts"]] == list(range(45976,46019))
    assert all(r["reader_chart"] == summary["actual_late_chart"] == 207
               and r["required_chart"] == summary["required_late_chart"] == 127
               and r["first_crossed_read"] is None for r in exact["typed_late_cuts"])
    assert summary["first_late_scale"] == exact["reader_incidents"][0] == [44614,["SCALE",198,"-2",207]]


def replay(root,output):
    unpacked = verify_inputs()
    wanted = decode((HERE/"receipts/SHA256.json").read_bytes())
    summary = decode((HERE/"receipts/CROSSED-RESPONSE.json").read_bytes())
    older = decode(unpacked["inputs/PR7338-GEOMETRY-69.json.gz"])
    match = [r for r in older["visited"] if r["key"] == "532:44611:46018"]
    assert match == [summary["predecessor_geometry"]]
    assert match[0]["reason"] == "protected_or_owned_component"
    regenerated = set()

    def stage(label,script):
        raw = command(script).stdout
        if digest(raw) != wanted[label]:
            raise ValueError(f"changed receipt {label}: {digest(raw)}")
        assert label not in regenerated
        regenerated.add(label)
        dest = root/safe(label)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(raw)
        return decode(raw)

    prior,crossed = root/"r106",root/"r107"
    for folder,name,lead_script,independent in (
        (prior,"r106","retime_source.py","reverse_recipient.py"),
        (crossed,"r107","correct.py","compensate.py"),
    ):
        for script in ("quote.py",lead_script):
            install(HERE/"engines"/name/script,folder/"lead"/script)
        for script in ("compare.py",independent):
            install(HERE/"engines"/name/script,folder/"independent"/script)
        for destination in (folder/"inputs",folder/"independent/inputs"):
            install(HERE/"inputs"/WORD,destination/WORD)

    for name in ("PRICE","GEOMETRY"):
        (prior/f"inputs/{name}.json").write_bytes(unpacked[f"inputs/R100-{name}.json.gz"])
    price = stage("r106/lead/PRICE.json",prior/"lead/quote.py")
    admitted = decode((HERE/"inputs/ADMITTED.json").read_bytes())
    assert admitted["exit"] == 0 and admitted["head"] == price["head"] == older["comparator_head"]
    assert admitted["caller"] == price["caller"] and admitted["inputs"]["WORD.json.gz"] == price["word_sha256"]
    assert price["old_paid"] == 110519 and price["new_paid"] == 110502 and price["productive"] == 22461
    assert len(price["candidate_rows"]) == 8 and len({r["key"][2] for r in price["candidate_rows"]}) == 7
    assert Fraction(price["one_upper"]) < 1 and Fraction(price["whole_target_complete_upper"]) < 0
    retime = stage("r106/lead/RETIMING.json",prior/"lead/retime_source.py")
    assert retime["counts"] == {"wrong chart":33517,"recipient contact barrier":43}
    assert not retime["candidates"] and retime["unvisited_cut"] is retime["unvisited_event"] is None
    for label in ("PRICE","RETIMING"):
        install(prior/f"lead/{label}.json",prior/f"independent/inputs/{label}.json")
        install(prior/f"lead/{label}.json",crossed/f"inputs/R106-{label}.json")
    reverse = prior/"independent/reverse_recipient.py"
    chrono = stage("r106/independent/RESULT.json",reverse)
    assert chrono["progress"]["events_checked"] == 76466
    assert chrono["progress"]["typed_cuts_checked"] == 33560 and not chrono["survivors"]
    agree = stage("r106/independent/AGREEMENT.json",prior/"independent/compare.py")
    assert agree["agreement"] and agree["typed_cut_count"] == 33560
    assert len(agree["chart_match_barriers"]) == 43

    install(HERE/"inputs/donor_span.py",crossed/"inputs/donor_span.py")
    install(HERE/"engines/r107/reverse_span.py",crossed/"independent/reused/reverse_span.py")
    quote = stage("r107/lead/PRICE.json",crossed/"lead/quote.py")
    assert quote["distinct_paid_edits"] == 1 and quote["old_paid"] == price["old_paid"]
    assert quote["new_paid"] == price["new_paid"] and quote["productive"] == price["productive"]
    assert quote["price"]["paid_delta"] == {"1":-17,"2":-17,"3":17}
    assert 0 < Fraction(quote["whole_upper"]) < 1
    correction = stage("r107/lead/CORRECTION.json",crossed/"lead/correct.py")
    assert correction["exact_crossed_response"] == "1/4" and not correction["late_eligible"]
    for label in ("PRICE","CORRECTION"):
        install(crossed/f"lead/{label}.json",crossed/f"independent/inputs/{label}.json")
    donors = crossed/"independent/compensate.py"
    exact = stage("r107/independent/RESULT.json",donors)
    assert exact["progress"]["bank_checked"] and exact["progress"]["late_checked"] == 43
    assert exact["late_counts"] == {"different chart":43} and exact["timeout"] is None
    checked = stage("r107/independent/AGREEMENT.json",crossed/"independent/compare.py")
    assert checked["agreement"] and checked["exact_bank_exclusions"] == 1 and checked["typed_late_exclusions"] == 43
    check_response(summary,quote,exact)

    for source,directory,name in ((reverse,prior/"independent","PRICE.json"),
                                  (donors,crossed/"independent",WORD)):
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
    print("PASS_P104_SOURCE_SIDE_CROSSED_READ typed_cuts=33560 wrong_chart=33517 read_barriers=43 correction_banks=1 late_cuts=43 unresolved=0 receipts=8")


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    p = ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,help="Optional directory for regenerated receipts")
    args = p.parse_args()
    with TemporaryDirectory(prefix="p104-source-side-") as temporary:
        replay(Path(temporary),args.output)


if __name__ == "__main__":
    main()
