"""Regenerate the two bounded rank-eight cochart screens and verify every receipt."""
from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha1, sha256
from json import loads
from pathlib import Path, PurePosixPath
from shutil import copyfile, copytree
from subprocess import run
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD = "7334-WORD.json.gz"


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def relpath(name):
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or ".." in path.parts:
        raise ValueError("invalid package path: " + name)
    return path


def authenticate():
    pins = decode((HERE / "LOCAL-PINS.json").read_bytes())
    for name, expected in pins.items():
        if digest((HERE / relpath(name)).read_bytes()) != expected:
            raise ValueError("changed dependency: " + name)
    provenance = decode((HERE / "PROVENANCE.json").read_bytes())
    for name, source in provenance["files"].items():
        raw = (HERE / relpath(name)).read_bytes()
        assert pins[name] == source["sha256"] == digest(raw)
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == source["git_blob"]
    for name, source in provenance["derived_inputs"].items():
        receipt = decode((HERE / relpath(source["receipt"])).read_bytes())
        for key in source["keys"]:
            receipt = receipt[key]
        if source.get("compression") == "gzip":
            raw = decompress((HERE / relpath(name)).read_bytes())
            assert digest(raw) == receipt
        else:
            assert pins[name] == receipt


def command(script, *args, timeout=35, cwd=None, check=True):
    return run([sys.executable, "-I", "-B", str(script), *map(str, args)],
               capture_output=True, check=check, timeout=timeout, cwd=cwd)


def install(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    copyfile(source, destination)


def rational_engine(destination, version):
    suite = HERE / "engines/rational"
    install(suite / f"{version}_independent.py", destination)
    for name in ("exact_six.py", "rolling_exterior.py"):
        install(suite / name, destination.parent / "reused" / name)


def rational_agreement(primary, independent, expected_counts):
    rows = [row for result in independent for row in result["results"]]
    assert len(rows) == len(primary["results"]) == 4 and not primary["selected_unresolved"]
    assert all(not receipt["timeout"] and not receipt["selected_unvisited"] for receipt in independent)
    assert primary["counts"] == expected_counts
    for p, q in zip(primary["results"], rows, strict=True):
        assert all(p[k] == q[k] for k in ("key", "public", "owned", "pivots"))
        assert p["pure_prefix_dimension"] == q["prefix_nullity"] == 1
        assert p["nonzero_prefix_images"] == q["nonzero_prefix_basis_images"]
        if p["status"] == "no unit pairing":
            assert q["status"] == "no_exact_unit_pair"
            assert p["pure_suffix_dimension"] == q["suffix_nullity"] == 1
            assert p["nonzero_suffix_images"] == q["nonzero_suffix_basis_images"] == 1
            assert q["cut_pairing_matrix"] == q["endpoint_pairing_matrix"] == [["0"]]
        else:
            assert p["status"] == "no nonzero pure prefix"
            assert q["key"] == [45675, 1091] and q["owned"] == [1564, 1565]
            assert q["status"] == "no_nonzero_pure_prefix"
            assert q["nonzero_prefix_basis_images"] == 0
            assert q["prefix_pure_basis"][0]["a"] and not q["prefix_pure_basis"][0]["c"]
    return [row["key"] for row in rows]


def replay(scratch, output):
    authenticate()
    expected = decode((HERE / "receipts/SHA256.json").read_bytes())
    generated = set()

    def record(name, raw):
        if digest(raw) != expected[name]:
            raise ValueError(f"changed receipt: {name}: {digest(raw)}")
        assert name not in generated
        generated.add(name)
        destination = scratch / relpath(name)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        return decode(raw)

    def stage(name, script, *args, timeout=35):
        return record(name, command(script, *args, timeout=timeout).stdout)

    old = scratch / "input"
    copytree(HERE / "inputs", old / "inputs")
    old_engines = HERE / "engines/r96"
    new_engines = HERE / "engines/r97"
    rational = HERE / "engines/rational"
    copytree(HERE / "price", old / "price")
    compressed_census = old / "price/inputs/7314-HELPERS.json.gz"
    compressed_census.with_suffix("").write_bytes(decompress(compressed_census.read_bytes()))
    price = stage("input/price/PRICE.json", old / "price/quote.py", timeout=10)
    assert price["head"] == HEAD and len(price["cohort"]) == 15
    assert price["productive_delta"] == {"4": 34, "8": -17} and not price["paid_delta"]
    assert 0 < Fraction(price["at_incumbent"]["gross_one"][0]) < Fraction(price["at_incumbent"]["gross_one"][1]) < 1
    assert Fraction(price["at_target"]["complete_15_upper"]) < Fraction("-134.1394")

    geometry = stage("input/lead/GEOMETRY.json", old_engines / "geometry.py", old, timeout=20)
    assert geometry["status"] == "EXHAUSTED" and geometry["visited_events"] == 76466
    assert geometry["eligible_bank_count"] == 326 and geometry["eligible_chart_count"] == 3
    assert {key[1] for key in geometry["all_representative_keys"]} == {242, 772, 1091}
    prefix = stage("input/lead/RESULT.json", old_engines / "prefix.py", old, timeout=25)
    assert prefix["counts"] == {"excluded": 9, "rank drop": 7} and not prefix["unvisited"]
    suffix = stage("input/lead/SUFFIX.json", old_engines / "suffix.py", old, timeout=20)
    assert suffix["counts"] == {"excluded": 1, "rank drop": 6} and not suffix["unvisited"]
    stage("input/lead/SELECTION.json", old_engines / "select.py", old, timeout=10)
    initial_exact = stage("input/lead/EXACT.json", old_engines / "exact_four.py", old)
    assert initial_exact["counts"] == {"no unit pairing": 4} and not initial_exact["selected_unresolved"]
    remaining = stage("input/lead/REMAINING.json", old_engines / "freeze_remaining.py", old, timeout=10)
    assert remaining["unresolved"] == 312 and remaining["excluded"] == 14

    first_rational = old / "independent"
    first_sources = {"PRICE.json": old / "price/PRICE.json", WORD: old / "inputs" / WORD}
    for name, label in (("GEOMETRY", "GEOMETRY"), ("SELECTION", "SELECTION"),
                        ("SUFFIX", "SUFFIX"), ("PRIMARY", "EXACT")):
        first_sources[f"{name}.json"] = old / "lead" / f"{label}.json"
    for name, path in first_sources.items():
        install(path, first_rational / "inputs" / name)
    rational_engine(first_rational / "exact_four.py", "r96")
    stage("input/independent/RESULT.json", first_rational / "exact_four.py")
    agreed = stage("input/independent/AGREEMENT.json", rational / "r96_compare.py",
                   "--primary", first_rational / "inputs/PRIMARY.json",
                   "--independent", first_rational / "RESULT.json", timeout=10)
    assert agreed["agree"]
    obstruction = first_rational / "pairing_obstruction.py"
    install(rational / "r96_pairing_obstruction.py", obstruction)
    initial_forms = stage("input/independent/PAIRINGS.json", obstruction)
    assert len(initial_forms["results"]) == 4
    assert all(row["cut_pairing"] == row["endpoint_pairing"] == "0" for row in initial_forms["results"])

    continued = stage("lead/CONTINUATION.json", old_engines / "continue_modular.py", old, timeout=25)
    assert continued["counts"] == {"prefix_exclusion": 279, "dual_drop": 31}
    second_prime = new_engines / "second_prime.py"
    modular = scratch / "modular"
    for name in ("PRICE.json", WORD, "GEOMETRY.json", "REMAINING.json"):
        source = first_sources[name] if name in first_sources else old / "lead" / name
        install(source, modular / "inputs" / name)
    other = stage("modular/RESULT.json", second_prime, "--root", modular, timeout=25)
    assert other["complete"] and other["counts"] == continued["counts"]
    modular_agreement = stage("modular/AGREEMENT.json", new_engines / "modular_compare.py", scratch, timeout=10)
    assert modular_agreement["matched"] == 310 and modular_agreement["moduli"] == [65521, 65537]

    install(old_engines / "exact_four.py", old / "lead/exact_four.py")
    frozen = command(new_engines / "freeze.py", timeout=10, cwd=scratch)
    assert frozen.stdout.decode().strip() == expected["lead/SELECTION.json"]
    selection_file = scratch / "lead/SELECTION.json"
    selection = record("lead/SELECTION.json", selection_file.read_bytes())
    primary = stage("lead/EXACT.json", scratch / "lead/exact_four.py", old)

    second_rational = scratch / "independent"
    rational_engine(second_rational / "exact_pairing.py", "r97")
    for name, source in (("PRICE.json", first_sources["PRICE.json"]), (WORD, first_sources[WORD]),
                         ("REMAINING.json", old / "lead/REMAINING.json"),
                         ("PREFIX.json", old / "lead/RESULT.json"), ("SUFFIX.json", old / "lead/SUFFIX.json")):
        install(source, second_rational / "inputs" / name)
    independent_source = second_rational / "exact_pairing.py"
    inherited = stage("independent/RESULT.json", independent_source)
    follow_args = ("--only-followup", "--followup", selection_file,
                   "--followup-sha", expected["lead/SELECTION.json"])
    followup = stage("independent/FOLLOWUP.json", independent_source, *follow_args, timeout=34)
    exact_keys = rational_agreement(primary, (inherited, followup),
                                    {"no unit pairing": 3, "no nonzero pure prefix": 1})
    assert exact_keys == [row["key"] for row in selection["selected"]]
    unresolved = decode((HERE / "receipts/UNRESOLVED.json").read_bytes())
    assert unresolved == selection["unselected"] == primary["unselected"]
    assert len(unresolved) == len(set(map(tuple, unresolved))) == 29

    def keys(rows, status, field="disposition"):
        return {tuple(row["key"]) for row in rows if row[field] == status}

    excluded_sets = (
        keys(prefix["rows"], "excluded"),
        keys(suffix["rows"], "excluded"),
        keys(initial_exact["results"], "no unit pairing", "status"),
        keys(continued["rows"], "prefix_exclusion", "status"),
        set(map(tuple, exact_keys)),
    )
    exclusions = set.union(*excluded_sets)
    assert len(exclusions) == sum(map(len, excluded_sets)) == 297
    assert not exclusions.intersection(map(tuple, unresolved))
    assert exclusions | set(map(tuple, unresolved)) == set(map(tuple, geometry["all_representative_keys"]))

    damaged_selection = scratch / "bad-selection.json"
    damaged_selection.write_bytes(selection_file.read_bytes() + b"\n")
    negative = command(independent_source, "--only-followup", "--followup", damaged_selection,
                       "--followup-sha", expected["lead/SELECTION.json"], timeout=10, check=False)
    assert negative.returncode == 1 and b"Changed input bad-selection.json" in negative.stderr and not negative.stdout
    for name in ("REMAINING.json", WORD):
        target = modular / "inputs" / name
        original = target.read_bytes()
        target.write_bytes(original + b"\n")
        try:
            bad = command(second_prime, "--root", modular, timeout=10, check=False)
            assert bad.returncode == 1 and b"changed dependency:" in bad.stderr and not bad.stdout
        finally:
            target.write_bytes(original)

    assert generated == set(expected)
    if output:
        for name in sorted(generated):
            install(scratch / relpath(name), output / relpath(name))
    print("PASS_P104_RANK_EIGHT_FIXED_PAID banks=326 excluded=297 unresolved=29 receipts=17")


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional root for regenerated JSON receipts")
    args = parser.parse_args()
    with TemporaryDirectory(prefix="rank-eight-replay-") as temporary:
        replay(Path(temporary), args.output)


if __name__ == "__main__":
    main()
