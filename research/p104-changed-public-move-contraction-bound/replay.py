"""Regenerate the exact current-word public MOVE and donor-span receipts."""
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


def unique(pairs):
    data = dict(pairs)
    if len(data) != len(pairs):
        raise ValueError("duplicate JSON key")
    return data


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def safe(name):
    path = PurePosixPath(name)
    if not path.parts or path.is_absolute() or path.as_posix() != name or ".." in path.parts:
        raise ValueError("invalid local path " + name)
    return path


def verify_inputs():
    pins = decode((HERE / "LOCAL-PINS.json").read_bytes())
    for name, expected in pins.items():
        if digest((HERE / safe(name)).read_bytes()) != expected:
            raise ValueError("changed dependency " + name)
    provenance = decode((HERE / "PROVENANCE.json").read_bytes())
    for name, row in provenance["files"].items():
        raw = (HERE / safe(name)).read_bytes()
        assert digest(raw) == row["sha256"]
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest() == row["git_blob"]
    admission = decode((HERE / "inputs/ADMITTED.json").read_bytes())
    bench = decode((HERE / "inputs/BENCHMARK.json").read_bytes())
    assert digest((HERE / "inputs/ADMITTED.json").read_bytes()) == bench["admission_sha256"]
    assert admission["head"] == bench["head"] and admission["crossing"] == bench["crossing"]
    r92 = decode((HERE / "inputs/PR7362-SHA256.json").read_bytes())
    assert digest(decompress((HERE / "inputs/R92-PRICE.json.gz").read_bytes())) == r92["R92-PRICE.json"]


def install(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    copyfile(source, destination)


def command(script, *args, timeout=20, check=True):
    return run([sys.executable,"-I","-B",str(script),*map(str,args)],
               capture_output=True,check=check,timeout=timeout)


def replay(root, output):
    verify_inputs()
    wanted = decode((HERE / "receipts/SHA256.json").read_bytes())
    regenerated = set()

    def stage(label, script, *args, timeout=20):
        raw = command(script,*args,timeout=timeout).stdout
        if digest(raw) != wanted[label]:
            raise ValueError(f"changed receipt {label}: {digest(raw)}")
        assert label not in regenerated
        regenerated.add(label)
        result = root / safe(label)
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_bytes(raw)
        return decode(raw)

    old, new = root/"r100", root/"r101"
    for target, name, primary, reverse in (
        (old, "r100", "geometry.py", "reverse_contacts.py"),
        (new, "r101", "support.py", "reverse_donors.py"),
    ):
        for path in ("quote.py", primary):
            install(HERE/"engines"/name/path, target/"lead"/path)
        install(HERE/"engines"/name/reverse,target/"independent"/reverse)
        for destination in (target/"inputs", target/"independent/inputs"):
            install(HERE/"inputs/7334-WORD.json.gz",destination/"7334-WORD.json.gz")
    for name in ("BENCHMARK.json", "7334-CHANGED.json", "pricing.py"):
        install(HERE/"inputs"/name,old/"inputs"/name)
    install(HERE/"inputs/7334-CHANGED.json",old/"independent/inputs/7334-CHANGED.json")
    (old/"inputs/R92-PRICE.json").write_bytes(decompress((HERE/"inputs/R92-PRICE.json.gz").read_bytes()))
    price = stage("r100/lead/PRICE.json", old/"lead/quote.py")
    assert price["full_paid_before"] == 110519 and price["full_paid_after"] == 110502
    assert price["productive_positions"] == 22461 and price["rank_surplus"] == 1424
    assert len(price["roles"]) == 14 and price["distinct_compatible_cap"] == 56
    assert Fraction(price["whole_target_margin_upper"]) < Fraction("-116")
    geom = stage("r100/lead/GEOMETRY.json",old/"lead/geometry.py")
    assert geom["counts"] == {"binary barrier":37} and not geom["candidate_keys"]
    assert geom["first_unvisited_event"] is None and geom["timeout"] is None
    assert sum(geom["moves"].values()) == 51
    install(old/"lead/PRICE.json",old/"independent/inputs/PRICE.json")
    contacts = old/"independent/reverse_contacts.py"
    reverse = stage("r100/independent/RESULT.json",contacts)
    assert reverse["events_checked"] == 76466 and not reverse["unvisited_pair_keys"]
    agreement = stage("r100/independent/AGREEMENT.json",contacts,"--primary",old/"lead/GEOMETRY.json")
    assert agreement["agrees"] and agreement["exact_windows"] == 37 and agreement["exact_signed_contact_incidences"] == 67
    assert agreement["access_counts"] == {"ADD:destination":32,"ADD:source":33,"SCALE:unary":2}

    for name in ("PRICE", "GEOMETRY"):
        install(old/f"lead/{name}.json",new/f"inputs/R100-{name}.json")
    install(HERE/"inputs/donor_span.py",new/"inputs/donor_span.py")
    install(HERE/"engines/r101/reverse_span.py",new/"independent/reused/reverse_span.py")
    quote = stage("r101/lead/PRICE.json",new/"lead/quote.py")
    assert len(quote["candidates"]) == 6 and quote["distinct_roles"] == 4
    assert quote["one_new_paid"] == 110502 and quote["targets"] == 22461
    assert Fraction(quote["whole_target_margin_upper"]) < Fraction("-138")
    support = stage("r101/lead/SUPPORT.json",new/"lead/support.py")
    assert support["counts"] == {"outside donor span":12} and not support["unvisited"]
    install(new/"lead/PRICE.json",new/"independent/inputs/PRICE.json")
    donors = new/"independent/reverse_donors.py"
    reverse = stage("r101/independent/RESULT.json",donors)
    assert len(reverse["exact_integer_rows"]) == 261 and not reverse["unvisited"]
    agree = stage("r101/independent/AGREEMENT.json",donors,"--primary",new/"lead/SUPPORT.json")
    assert agree["bank_status_agreement"] == agree["rank_agreement"] == 12

    witness = decode((HERE/"receipts/SEPARATORS.json").read_bytes())
    rows = reverse["exact_integer_rows"]
    for summary, tested in zip(witness,reverse["results"],strict=True):
        for k in ("key","chart","source","owned_donors_excluded"):
            assert summary[k] == tested[k]
        assert summary["donors"] == tested["bank_roles"]
        coordinate = str(summary["coordinate"])
        numerator, denominator = rows[tested["target_row_id"]]
        assert Fraction(numerator[coordinate],denominator) == Fraction(summary["coefficient"]) != 0
        assert all(coordinate not in rows[i][0] for _,i in tested["donor_role_row_ids"])
        assert tested["proof"]["separating_covector"] == {coordinate:"1"}

    for source, directory, mutation in (
        (contacts,old/"independent","PRICE.json"),
        (donors,new/"independent","7334-WORD.json.gz"),
    ):
        target = directory/"inputs"/mutation
        original = target.read_bytes()
        target.write_bytes(original+b"\n")
        try:
            bad = command(source,check=False,timeout=10)
            assert bad.returncode == 1 and not bad.stdout and b"Changed input " in bad.stderr
        finally:
            target.write_bytes(original)
    assert regenerated == set(wanted)
    if output:
        for name in sorted(regenerated):
            install(root/safe(name),output/safe(name))
    print("PASS_P104_PUBLIC_MOVE_CONTRACTION windows=37 binary=37 donor_banks=12 separators=12 unresolved=0 receipts=8")


def main():
    assert __debug__ and sys.version_info[:2] == (3,12)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,help="Optional directory for regenerated evidence")
    args = parser.parse_args()
    with TemporaryDirectory(prefix="public-move-contact-") as temporary:
        replay(Path(temporary),args.output)


if __name__ == "__main__":
    main()
