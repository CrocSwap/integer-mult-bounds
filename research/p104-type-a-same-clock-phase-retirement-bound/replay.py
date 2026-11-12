"""Replay the same-clock Type A phase retirement bounds with two exact engines."""
import argparse
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
ROWS = (0, 1, 18, 19)
COLUMNS = (2, 9, 20, 27)
ENGINES = {
    "PRICE.json": "quote.py",
    "FORWARD.json": "literal.py",
    "REVERSE.json": "replay_reverse.py",
    "EVEN-FORWARD.json": "coefficients.py",
    "EVEN-REVERSE.json": "replay_r164.py",
    "ANCHOR-FORWARD.json": "anchors.py",
    "ANCHOR-REVERSE.json": "diagonal_anchors.py",
    "NEXT-PRICE.json": "price.py",
}
MISSING_ANCHORS = [[18], [18], [18], [0], [], []]
EVEN_RANKS = [3, 3, 3, 3, 4, 4]
NEXT_RANKS = [4, 4, 4, 3, 4, 4]


def unique(pairs):
    out = dict(pairs)
    if len(out) != len(pairs):
        raise ValueError("duplicate JSON key")
    return out


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def source(name):
    path = PurePosixPath(name)
    if not path.parts or path.is_absolute() or ".." in path.parts or path.as_posix() != name:
        raise ValueError("invalid package-relative path " + name)
    return (ROOT / path).read_bytes()


def materialize(directory):
    pins = decode(source("LOCAL-PINS.json"))
    for name, expected in pins.items():
        if digest(source(name)) != expected:
            raise ValueError("changed package dependency " + name)
    provenance = decode(source("PROVENANCE.json"))
    for name, entry in provenance["files"].items():
        raw = source(name)
        assert digest(raw) == entry["sha256"] == pins[name]
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        assert blob == entry["git_blob"]

    admitted = decode(source("inputs/7334-ADMITTED.json"))
    assert admitted["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert admitted["kappa"] == "0.00364665195644"
    inputs = directory / "inputs"
    inputs.mkdir()
    for name, entry in provenance["derived_inputs"].items():
        raw = source(entry["file"])
        if entry.get("compression") == "gzip":
            raw = gzip.decompress(raw)
        assert digest(raw) == entry["sha256"]
        if "manifest" in entry:
            manifest = decode(source(entry["manifest"]))
            assert digest(raw) == manifest[entry["key"]]
        (inputs / name).write_bytes(raw)
    (inputs / "pricing.py").write_bytes(source("inputs/pricing.py"))
    for name in ENGINES.values():
        (directory / name).write_bytes(source("engines/" + name))


def invoke(script):
    return subprocess.run([sys.executable, "-I", "-B", str(script)], capture_output=True, timeout=25)


def verify_receipts(receipts):
    price, forward, reverse = (receipts[name] for name in ("PRICE.json", "FORWARD.json", "REVERSE.json"))
    assert price["head"] == forward["head"] == reverse["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert price["caller"] == forward["caller_head"] == reverse["caller_head"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert forward["caller_sha256"] == reverse["pins"]["inputs/CALLER.json"] == price["pins"]["inputs/CALLER.json"]
    assert forward["roles"] == reverse["roles"] == 36
    assert forward["events"] == reverse["events"] == 4783
    assert forward["fixed_j"] == reverse["fixed_J_stages"] == 17
    assert forward["hard_cap_seconds"] == reverse["hard_cap_seconds"] == 20
    assert forward["even_query_factor"] == reverse["even_query_factor"] == 1
    assert forward["target_phase_retirements"] == reverse["roots"] == price["roots"] == [0, 18]
    assert forward["query_indices_zero_based"] == reverse["zero_based_query_clocks"] == [1516, 1580, 1659, 1721]
    assert forward["candidate_rank"] == reverse["rank"] == 4
    assert price["paid_delta"] == {"1": -192} and price["productive_delta"] == {"136": 192, "137": -192}
    assert Fraction(price["quote"]["old_crossing_upper"]["gross"][1]) < Fraction("4.099242419852824")
    assert Fraction(price["quote"]["probe"]["complete"][0]) > Fraction("4.098855957122750")

    reverse_entries = {(i, j): Fraction(value) for i, j, value in reverse["nonzero_delta_entries"]}
    forward_entries = {(i, j): Fraction(value) for i, j, value in forward["nonzero_delta_entries"]}
    assert len(reverse_entries) == len(reverse["nonzero_delta_entries"])
    assert len(forward_entries) == len(forward["nonzero_delta_entries"])
    assert reverse_entries == forward_entries
    assert set(ROWS).isdisjoint(COLUMNS)
    minor = [[reverse_entries.get((i, j), 0) for j in COLUMNS] for i in ROWS]
    assert minor == [[-6, -2, 0, 0], [-4, 0, 0, 0], [0, 0, -6, -2], [0, 0, -4, 0]]
    determinant = (minor[0][0] * minor[1][1] - minor[0][1] * minor[1][0]) * (
        minor[2][2] * minor[3][3] - minor[2][3] * minor[3][2]
    )
    assert determinant == 64
    forward_minor = forward["off_diagonal_minor"]
    assert forward_minor["rows"] == list(ROWS) and forward_minor["columns"] == list(COLUMNS)
    assert [list(map(Fraction, row)) for row in forward_minor["entries"]] == minor
    assert Fraction(forward_minor["determinant"]) == determinant


def verify_coefficients(receipts):
    forward = receipts["EVEN-FORWARD.json"]
    reverse = receipts["EVEN-REVERSE.json"]
    assert forward["cases"] == reverse["evaluated_erased_words"] == 8
    assert forward["events"] == reverse["events"] == 4783
    assert forward["roles"] == reverse["roles"] == 36
    assert forward["hard_cap_seconds"] == reverse["hard_cap_seconds"] == 20
    assert forward["flipped_roots"] == reverse["roots"] == [0, 18]
    assert forward["plus_all_opposite_rank"] == 4
    plus = reverse["plus_full_rank_control"]
    entries = {(i, j): Fraction(value) for i, j, value in forward["plus_all_opposite_nonzero_entries"]}
    assert len(entries) == len(forward["plus_all_opposite_nonzero_entries"])
    assert [[-entries.get((i, j), 0) for j in plus["columns"]] for i in plus["rows"]] == plus["matrix"]
    assert plus["determinant"] == 16
    minus_forward = forward["minus_all_opposite_off_diagonal_minor"]
    minus_reverse = reverse["minus_offdiagonal_full_rank_control"]
    assert minus_forward["rows"] == minus_reverse["rows"] == list(ROWS)
    assert minus_forward["columns"] == minus_reverse["columns"] == list(COLUMNS)
    assert [[-Fraction(v) for v in row] for row in minus_forward["entries"]] == minus_reverse["matrix"]
    assert Fraction(minus_forward["determinant"]) == minus_reverse["determinant"] == 64
    assert not forward["survivors"] and not reverse["unresolved"]
    for rank, direct, other in zip(EVEN_RANKS, forward["tested_sign_patterns"], reverse["balanced_cases"], strict=True):
        assert direct["coefficients"] == other["constants"]
        assert direct["unchanged_plus_rank"] == direct["unchanged_minus_rank"] == 2
        assert direct["changed_minus_rank"] == rank and other["residual_ranks"] == [2, rank]
        assert other["minus_exclusion"]["determinant"]


def verify_anchors(receipts):
    forward = receipts["ANCHOR-FORWARD.json"]
    reverse = receipts["ANCHOR-REVERSE.json"]
    even = receipts["EVEN-FORWARD.json"]
    price = receipts["NEXT-PRICE.json"]
    assert forward["words"] == reverse["words"] == 6
    assert reverse["checks"] == 216 and reverse["missing"] == 4
    assert forward["number_of_anchors"] == reverse["anchors"] == 212
    assert forward["hard_cap_seconds"] == reverse["hard_cap_seconds"] == 20
    assert price["head"] == reverse["head"] == receipts["PRICE.json"]["head"]
    assert price["caller_head"] == reverse["caller_head"] == receipts["PRICE.json"]["caller"]
    assert price["roots"] == forward["candidate_pair"] == reverse["next_pair"]["roots"] == [0, 17]
    assert price["ranks"] == [137, 73]
    assert price["signed_histogram_delta"] == {"1": 192, "72": 96, "73": -96, "136": 96, "137": -96}
    assert Fraction(price["gross_at_crossing_upper"][1]) < Fraction("3.882211372694752")
    assert Fraction(price["complete_at_probe"][0]) > Fraction("3.881824851665655")
    assert reverse["next_pair"]["evaluated"] and reverse["next_pair"]["residual_ranks"] == NEXT_RANKS
    for missing, rank, direct, other, coefficients in zip(
        MISSING_ANCHORS, NEXT_RANKS, forward["patterns"], reverse["cases"],
        even["tested_sign_patterns"], strict=True,
    ):
        assert direct["coefficients"] == other["constants"] == coefficients["coefficients"]
        assert direct["missing_roles"] == other["missing"] == missing
        assert direct["changed_pair_rank"] == rank
        assert other["full_rank"] == other["off_diagonal_rank"] == 2
        direct_roles = {role for role, _, _, _ in direct["anchors"]}
        other_roles = {int(role) for role in other["anchors"]}
        assert len(direct_roles) == len(direct["anchors"])
        assert direct_roles == other_roles == set(range(36)) - set(missing)
        for role, rows, columns, determinant in direct["anchors"]:
            assert set(rows).isdisjoint(columns) and role not in rows and role not in columns
            assert Fraction(determinant)


def replay(directory):
    materialize(directory)
    expected = decode(source("receipts/SHA256.json"))
    raw_receipts = {}
    for receipt, name in ENGINES.items():
        result = invoke(directory / name)
        if result.returncode:
            sys.stderr.buffer.write(result.stderr)
            result.check_returncode()
        assert digest(result.stdout) == expected[receipt], ("changed receipt", receipt)
        raw_receipts[receipt] = result.stdout
    receipts = {name: decode(raw) for name, raw in raw_receipts.items()}
    verify_receipts(receipts)
    verify_coefficients(receipts)
    verify_anchors(receipts)
    for filename, scripts in (
        ("inputs/CALLER.json", (("literal.py", b"AssertionError"), ("replay_reverse.py", b"AssertionError"),
                                ("replay_r164.py", b"changed signed caller"))),
        ("inputs/R92-PRICE.json", (("quote.py", b"AssertionError"), ("price.py", b"AssertionError"))),
        ("replay_r164.py", (("diagonal_anchors.py", b"changed input replay_r164.py"),)),
    ):
        path = directory / filename
        raw = path.read_bytes()
        path.write_bytes(raw + b" ")
        for script, expected_error in scripts:
            check = invoke(directory / script)
            assert check.returncode == 1 and expected_error in check.stderr
        path.write_bytes(raw)
    try:
        decode(b'{"inputs/CALLER.json":1,"inputs/CALLER.json":2}')
    except ValueError as error:
        assert str(error) == "duplicate JSON key"
    else:
        raise AssertionError("duplicate dependency key accepted")
    return raw_receipts


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as temporary:
        raw_receipts = replay(Path(temporary))
    if args.out is not None:
        args.out.mkdir(parents=True)
        for name, raw in raw_receipts.items():
            (args.out / name).write_bytes(raw)
    print("PASS_P104_TYPE_A_SAME_CLOCK_PHASE_RETIREMENT_BOUND words=8 roles=36 anchors=212 pairs_excluded=630")


if __name__ == "__main__":
    main()
