"""Rebuild both exact public MOVE fusion scopes and their independent receipts."""
from argparse import ArgumentParser
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
WORD = "round30/complex/source/inputs/WORD.json.gz"
HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def decode(data):
    return json.loads(data, object_pairs_hook=unique)


def read(path):
    return decode(path.read_bytes())


def authenticate(scratch):
    pins = read(HERE / "LOCAL-PINS.json")
    for key, expected in pins.items():
        rel = PurePosixPath(key)
        if rel.is_absolute() or ".." in rel.parts or rel.as_posix() != key:
            raise ValueError(f"invalid dependency path {key}")
        if sha256((HERE / key).read_bytes()).hexdigest() != expected:
            raise ValueError(f"changed dependency {key}")
    deps = scratch / "dependencies"
    shutil.copytree(HERE / "dependencies", deps)
    provenance = read(HERE / "PROVENANCE.json")["files"]
    assert len(provenance) == 8 and sum(p["uncompress"] for p in provenance.values()) == 2
    for key, pin in provenance.items():
        assert key in pins
        raw = (HERE / key).read_bytes()
        if pin["uncompress"]:
            raw = gzip.decompress(raw)
            (scratch / key).with_suffix("").write_bytes(raw)
        assert sha256(raw).hexdigest() == pin["sha256"], key
        assert sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest() == pin["git_blob"], key
    return deps


def run(script, *args, timeout):
    result = subprocess.run([sys.executable, "-I", "-B", str(script), *map(str,args)],
                            capture_output=True, check=True, timeout=timeout)
    return result.stdout


def check_receipts(artifacts):
    pins = read(HERE / "receipts/SHA256.json")
    assert pins.keys() == artifacts.keys()
    for key, path in artifacts.items():
        if sha256(path.read_bytes()).hexdigest() != pins[key]:
            raise ValueError(f"replay receipt changed: {key}")


def crosscheck(artifacts):
    price, support, independent = (read(artifacts[f"scalar-silence/{name}.json"])
                                    for name in ("PRICE","SUPPORT","INDEPENDENT"))
    lift_price, lift, reverse = (read(artifacts[f"common-lift/{name}.json"])
                                 for name in ("PRICE","SUPPORT","INDEPENDENT"))
    assert {r["head"] for r in (price,support,independent,lift_price,lift,reverse)} == {HEAD}
    assert price["old_full_paid"] == lift_price["original_paid"]
    assert price["old_full_targets"] == lift_price["original_productive"]
    assert price["copies"] == lift_price["copies"] == 17
    assert price["crossing_upper"] == lift_price["crossing_upper"]
    assert price["old_margin"] == lift_price["baseline_interval"]
    assert len(price["records"]) == len(support["records"]) == independent["public_pairs"] == 4732
    assert not price["unresolved_price"] and not support["unresolved"] and not support["survivors"]
    assert not independent["unresolved_pairs"] and independent["first_unvisited_literal_index"] is None
    assert independent["whole_compatible_upper_from_pinned_weights"] == price["whole_compatible_upper"]
    assert independent["unique_contacts"] == independent["nonzero_contact_count"] == 7721
    rows = {tuple(r["moves"]):r for r in support["records"]}
    proofs = {(l,r):proof for l,r,proof in independent["pair_proofs"]}
    assert len(rows) == len(proofs) == 4732 and rows.keys() == proofs.keys()
    for key, proof in proofs.items():
        row = rows[key]
        kind = {"add_source": "nonzero_add_source", "scale_row": "nonzero_scale_row"}[proof[1]]
        assert row["status"] == "scalar_exclusion" and row["scalar_evidence"][0] == [proof[0],kind]
        assert proof[-1] != 0
    assert len(lift_price["records"]) == len(lift["records"]) == reverse["exact_one_add"] == 1922
    assert reverse["total_windows"] == 4732 and reverse["all_cases_match_lead"]
    assert not lift["survivors"] and not lift["remaining"] and reverse["unresolved"] == 0
    assert lift["post_support_compatible_upper"] == "0"
    expected = read(HERE / "receipts/SUMMARY.json")
    assert expected["scalar-silence"] == {
        "checked": len(rows), "primary_status_counts": support["counts"],
        "pre_support_compatible_upper": price["whole_compatible_upper"],
        "unique_contacts": independent["unique_contacts"], "certified_nonzero": independent["nonzero_contact_count"],
        "first_witness_counts": independent["proved_pair_witness_kinds"], "prime": independent["prime"],
    }
    assert expected["common-lift"] == {
        "checked": len(lift["records"]), "primary_status_counts": lift["counts"],
        "pre_support_compatible_upper": lift_price["whole_compatible_upper"],
        "first_blockers": reverse["first_blockers"],
    }
    assert expected["head"] == HEAD and expected["copies"] == price["copies"]
    assert expected["unresolved"] == 0 and expected["compatible_saving_after_support"] == "0"
    assert expected["kappa_change"] == "0"


def replay(output):
    with TemporaryDirectory(prefix="p104-move-fusion-") as temp:
        scratch = Path(temp)
        deps = authenticate(scratch)
        engines = HERE / "engines"
        lead = scratch / "lead"
        lead.mkdir()
        shutil.copyfile(engines / "silence.py", lead / "screen.py")
        silence, lift = scratch / "run", scratch / "common-lift"
        word = deps / WORD
        run(lead / "screen.py", "--r47", deps / "r47/lead/screen.py",
            "--round30", deps / "round30", "--predecessor", deps / "7298",
            "--core", deps / "round41/independent/replay_core.py", "--out", silence, timeout=45)
        (silence / "INDEPENDENT.json").write_bytes(run(engines / "silence_audit.py",
            "--word", word, "--price", silence / "PRICE.json", timeout=45))
        run(engines / "common_lift.py", scratch, lift, "--cap", 1922, "--seconds", 25, timeout=25)
        (lift / "INDEPENDENT.json").write_bytes(run(engines / "common_lift_audit.py",
            word, lift, timeout=25))
        artifacts = {f"{scope}/{name}.json": folder / f"{name}.json"
                     for scope,folder in (("scalar-silence",silence),("common-lift",lift))
                     for name in ("PRICE","SUPPORT","INDEPENDENT")}
        check_receipts(artifacts)
        crosscheck(artifacts)
        if output is not None:
            output.mkdir(parents=True, exist_ok=False)
            for key, path in artifacts.items():
                target = output / key
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
        print("PASS_PUBLIC_MOVE_CONTACT_BOUND silence=4732 nonzero_contacts=7721 common_lift=1922 unresolved=0 saving_upper=0 kappa_change=0")


if __name__ == "__main__":
    assert __debug__, "run with assertions enabled"
    assert sys.version_info[:2] == (3,12), "Python 3.12 required"
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="fresh destination for the full deterministic receipts")
    args = parser.parse_args()
    replay(args.out)
