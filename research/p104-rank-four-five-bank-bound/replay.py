"""Replay the fixed-paid rank-four/five public-bank support results."""
from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha1, sha256
from json import loads
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def checked_path(name):
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or ".." in path.parts:
        raise ValueError("invalid package path: " + name)
    return path


def authenticate():
    pins = decode((HERE / "LOCAL-PINS.json").read_bytes())
    for name, expected in pins.items():
        raw = (HERE / checked_path(name)).read_bytes()
        if digest(raw) != expected:
            raise ValueError("changed dependency: " + name)
    sources = decode((HERE / "PROVENANCE.json").read_bytes())["files"]
    for name, source in sources.items():
        raw = (HERE / checked_path(name)).read_bytes()
        assert not source["uncompress"] and pins[name] == source["sha256"] == digest(raw)
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == source["git_blob"]
    for name, source in decode((HERE / "PROVENANCE.json").read_bytes())["derived_inputs"].items():
        raw = (HERE / checked_path(name)).read_bytes()
        assert name in pins and source["published_receipt"] in sources
        if source.get("compression") == "gzip":
            raw = decompress(raw)
        published = decode((HERE / checked_path(source["published_receipt"])).read_bytes())
        assert digest(raw) == published[source["receipt_key"]]


def command(script, *args, timeout=35, check=True):
    argv = [sys.executable, "-I", "-B", str(HERE / script), *map(str, args)]
    return subprocess.run(argv, capture_output=True, check=check, timeout=timeout)


def replay_suffix(scratch, record, expected):
    """Continue on the exact R87 unresolved bank list without changing its receipts."""
    root = scratch / "r89"
    for name in ("price", "inputs", "lead", "independent/reused"):
        (root / name).mkdir(parents=True)
    for name in ("7334-WORD.json.gz", "PRICE.json", "paired_rank.py", "paired_support.py"):
        shutil.copyfile(scratch / "inputs" / name, root / "inputs" / name)
    shutil.copyfile(HERE / "engines/modular_primary.py", root / "inputs/exterior_minor.py")
    shutil.copyfile(HERE / "engines/r89/suffix_sweep.py", root / "lead/suffix_sweep.py")
    independent_exact = root / "independent/exact_selection.py"
    shutil.copyfile(HERE / "engines/r89/exact_independent.py", independent_exact)
    for local, source in (("exact_six.py", "exact_independent.py"),
                          ("rolling_exterior.py", "rolling_exterior.py")):
        shutil.copyfile(HERE / "engines" / source, root / "independent/reused" / local)

    def stage(name, script, *args, timeout=35):
        return record("r89/" + name, command(script, *args, timeout=timeout).stdout)

    frozen = stage("price/KEYS.json", "engines/r89/freeze.py", scratch, timeout=10)
    assert frozen["cases"] == 2128 and frozen["one_split_per_literal_pivot_cap"] == 129
    primary = stage("lead/RESULT.json", "engines/r89/suffix_sweep.py", root)
    assert primary["status"] == "EXHAUSTED" and not primary["unvisited"]
    assert primary["counts"] == {"excluded":663, "rank drop":1465}
    keys_path = root / "price/KEYS.json"
    price_path = root / "inputs/PRICE.json"
    word_path = root / "inputs/7334-WORD.json.gz"
    suffix_script = "engines/r89/reverse_suffix.py"
    modular_args = ("--keys", keys_path, "--price", price_path, "--word", word_path)
    other = stage("independent/RESULT.json", suffix_script, *modular_args)
    assert len(other["denominator_units"]) == 98 and not other["unvisited"]
    assert not other["control_discrepancies"] and not other["control_unvisited"]
    compare = stage("independent/COMPARE.json", "engines/r89/compare_modular.py", keys_path,
                    root / "lead/RESULT.json", root / "independent/RESULT.json", timeout=10)
    assert compare["agreed_keys"] == 2128 and compare["full_suffix_exclusions"] == 663
    assert compare["suffix_rank_drops"] == 1465 and len(compare["remaining_pivots"]) == 109
    assert Fraction(compare["moonshot_optimistic_complete_upper"]) < 0

    heuristic = stage("lead/PAIR.json", "engines/r89/rank_pairs.py", root)
    assert heuristic["cases"] == 1465 and heuristic["modular_pairs"] == 0 and not heuristic["unvisited"]
    selection = stage("lead/SELECTION.json", "engines/r89/select.py", root, timeout=10)
    assert len(selection["selected"]) == selection["case_cap"] == 6
    exact = stage("lead/EXACT.json", "engines/r89/exact_primary.py", root)
    assert exact["counts"] == {"no unit pairing":6} and not exact["selected_unresolved"]
    selection_path = root / "lead/SELECTION.json"
    selection_hash = expected["r89/lead/SELECTION.json"]
    exact_args = (*modular_args, "--suffix", root / "independent/RESULT.json",
                  "--selection", selection_path, "--selection-sha", selection_hash)
    independent = stage("independent/EXACT.json", independent_exact, *exact_args)
    assert independent["counts"] == {"no_exact_unit_pair":6} and not independent["unresolved"]
    checked = stage("independent/EXACT-COMPARE.json", "engines/r89/compare_exact.py",
                    selection_path, root / "lead/EXACT.json", root / "independent/EXACT.json",
                    root / "independent/RESULT.json", timeout=10)
    assert checked["exact_agreements"] == 6 and checked["exact_unit_pairs"] == 0
    assert checked["remaining_modular_drops"] == 1459 and len(checked["remaining_literal_pivots"]) == 109

    unresolved = decode((HERE / "receipts/UNRESOLVED.json").read_bytes())
    checked_keys = {tuple(row["key"]) for row in independent["results"]}
    independently_remaining = [row["key"] for row in other["tested"]
                               if row["status"] == "modular_suffix_rank_drop" and tuple(row["key"]) not in checked_keys]
    assert unresolved == exact["unselected"] == selection["unselected"] == independently_remaining
    assert len(unresolved) == len(set(map(tuple, unresolved))) == 1459
    assert 4207 - (24 + 2049 + 6 + 663 + 6) == len(unresolved)

    for target, message, args, index, script in (
        (keys_path, b"Changed input keys", modular_args, 1, suffix_script),
        (word_path, b"Changed input word", modular_args, 5, suffix_script),
        (selection_path, b"Changed input bad-SELECTION.json", exact_args, 9, independent_exact),
    ):
        bad = root / ("bad-" + target.name)
        bad.write_bytes(target.read_bytes() + b"\n")
        changed = [*args]
        changed[index] = bad
        negative = command(script, *changed, timeout=10, check=False)
        assert negative.returncode == 1 and message in negative.stderr and not negative.stdout


def replay(scratch, output):
    authenticate()
    expected = decode((HERE / "receipts/SHA256.json").read_bytes())
    generated = {}

    def record(name, raw):
        if digest(raw) != expected[name]:
            raise ValueError("changed receipt: " + name)
        generated[name] = raw
        (scratch / checked_path(name)).write_bytes(raw)
        return decode(raw)

    for name in ("lead", "independent"):
        (scratch / name).mkdir()
    for name in ("price", "inputs"):
        shutil.copytree(HERE / name, scratch / name)
    compressed = scratch / "price/inputs/R72-OCCUPANCY.json.gz"
    (compressed.parent / "R72-OCCUPANCY.json").write_bytes(decompress(compressed.read_bytes()))
    price_path = scratch / "price/PRICE.json"
    price = record("price/PRICE.json", command(scratch / "price/quote.py", timeout=15).stdout)
    assert price["head"] == HEAD and price["native_copies"] == 17
    split = price["one_split"]
    assert not split["paid_delta"] and split["target_delta"] == {"4":17, "5":17, "9":-17}
    assert sum(split["paid"].values()) == 110519
    assert (sum(price["old_targets"].values()), sum(split["targets"].values())) == (22461,22478)
    assert price["signed_rank_surplus"] == 1424 and price["empty_root_credits"] == 0
    assert 0 < Fraction(split["complete_margin"][0]) and Fraction(split["complete_margin_with_one_extra_paid_rank1_upper"]) < 0

    geometry_path = scratch / "lead/GEOMETRY.json"
    geom = record("lead/GEOMETRY.json", command("engines/geometry.py", scratch, timeout=20).stdout)
    assert geom["head"] == HEAD and geom["status"] == "EXHAUSTED"
    assert (geom["visited_events"],geom["eligible_bank_count"],geom["eligible_chart_count"]) == (76466,4207,90)
    assert len(geom["selected"]) == 24 and len(geom["unvisited_keys"]) == 4183
    assert len(price["endpoint_cohort"]) == 615
    old_rational = record("lead/R86-RATIONAL.json", command("engines/prior_rational.py", scratch,
                        expected["lead/GEOMETRY.json"],timeout=25).stdout)
    assert old_rational["counts"] == {"no nonzero pure prefix":24} and not old_rational["selected_unresolved"]
    word = scratch / "inputs/7334-WORD.json.gz"
    prior = record("inputs/R86-PRIOR.json", command("engines/prior_minors.py", "--price", price_path,
                   "--geometry", geometry_path, "--word", word,
                   "--primary", scratch / "lead/R86-RATIONAL.json",timeout=25).stdout)
    assert prior["head"] == HEAD
    shutil.copyfile(price_path, scratch / "inputs/PRICE.json")
    shutil.copyfile(geometry_path, scratch / "inputs/GEOMETRY.json")

    modular = record("lead/RESULT.json", command("engines/modular_primary.py", scratch).stdout)
    assert modular["status"] == "EXHAUSTED" and not modular["unvisited"]
    assert modular["counts"] == {"excluded":2049, "rank drop":2134}
    other = record("independent/RESULT.json", command("engines/rolling_exterior.py", "--price", price_path,
                   "--geometry", geometry_path, "--prior", scratch / "inputs/R86-PRIOR.json",
                   "--word", word).stdout)
    assert len(other["denominator_units"]) == 98 and not other["unvisited"]
    selection = record("lead/SELECTION.json", command("engines/select_six.py", scratch, timeout=10).stdout)
    assert len(selection["selected"]) == 6
    exact = record("lead/EXACT.json", command("engines/exact_primary.py", scratch).stdout)
    assert exact["counts"] == {"no nonzero pure suffix":4, "no unit pairing":2}
    assert not exact["selected_unresolved"]
    assert len(exact["unselected"]) == len(set(map(tuple, exact["unselected"]))) == 2128
    record("independent/EXACT.json", command("engines/exact_independent.py", "--price", price_path, "--word", word,
           "--selection", scratch / "lead/SELECTION.json", "--modular", scratch / "independent/RESULT.json").stdout)
    compare = record("independent/COMPARE.json", command("engines/compare.py", scratch / "lead/RESULT.json",
                     scratch / "independent/RESULT.json", scratch / "lead/EXACT.json",
                     scratch / "independent/EXACT.json", timeout=10).stdout)
    assert compare["modular_exact_bank_agreements"] == 4207
    assert compare["new_full_rank_exclusions"] == 2049 and compare["exact_scope_exclusions"] == 6
    assert compare["remaining_unresolved"] == 2128

    replay_suffix(scratch, record, expected)

    # Check that the actual scientific entry points reject changed receipts before replaying the word.
    for target, script, message in (("inputs/GEOMETRY.json", "engines/modular_primary.py", b"changed dependency"),
                                    ("lead/RESULT.json", "engines/select_six.py", b"changed modular support receipt")):
        changed = scratch / target
        changed.write_bytes(changed.read_bytes() + b"\n")
        negative = command(script, scratch, timeout=10, check=False)
        assert negative.returncode == 1 and message in negative.stderr and not negative.stdout

    assert generated.keys() == expected.keys()
    if output is not None:
        output.mkdir(parents=True)
        for name, raw in generated.items():
            target = output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    print("PASS_RANK_FOUR_FIVE_BANK_BOUND prior=24 new=2724 unresolved=1459 kappa_change=0")


def main():
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="new directory to retain regenerated receipts")
    args = parser.parse_args()
    with TemporaryDirectory() as temporary:
        replay(Path(temporary), args.out)


if __name__ == "__main__":
    main()
