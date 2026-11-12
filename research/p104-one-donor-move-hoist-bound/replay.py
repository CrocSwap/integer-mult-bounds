"""Replay the priced geometry and exact normalized next-contact donor exclusions."""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path
from subprocess import CalledProcessError, run
from tempfile import TemporaryDirectory
import sys

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
WORD = "7334-WORD.json.gz"


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def path_bytes(path):
    p = Path(path)
    if p.is_absolute() or ".." in p.parts or p.as_posix() != path:
        raise ValueError("invalid package-relative path " + path)
    return (ROOT / p).read_bytes()


def authenticate():
    pins = decode(path_bytes("LOCAL-PINS.json"))
    for path, expected in pins.items():
        if digest(path_bytes(path)) != expected:
            raise ValueError("changed package dependency " + path)
    provenance = decode(path_bytes("PROVENANCE.json"))
    assert provenance["caller"]["commit"] == CALLER
    for path, entry in provenance["files"].items():
        raw = path_bytes(path)
        assert digest(raw) == entry["sha256"] == pins[path]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == entry["git_blob"]
    for path, entry in provenance["derived_inputs"].items():
        assert entry["receipt_key"] == Path(path).name and entry["sha256"] == pins[path]
    return pins


def keys(rows):
    result = set()
    for row in rows:
        clock = row["next_donor_move"] if "next_donor_move" in row else row["donor_move_clock"]
        result.add((row["clock"], row["owner"], row["donor"], clock))
    assert len(result) == len(rows)
    return result


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def replay(stage, output):
    pins = authenticate()
    results = {}

    def copy(dst, src):
        write(stage / dst, path_bytes(src))

    def record(name, raw):
        assert digest(raw) == pins["receipts/" + name], ("changed receipt", name)
        results[name] = raw
        return decode(raw)

    def launch(script, *args):
        return run(
            [sys.executable, "-I", "-B", "-X", f"pycache_prefix={stage / 'pycache'}", str(stage / script),
             *map(str, args)], check=True, capture_output=True, timeout=40,
        ).stdout

    def execute(name, script, *args):
        return record(name, launch(script, *args))

    for path in sorted(p for p in pins if p.startswith(("engines/", "inputs/"))):
        copy(Path(path).name if path.startswith("engines/") else path, path)

    p176 = execute("R176-PRICE.json", "ascent_price.py")
    geo = execute("R176-GEOMETRY.json", "geometry.py")
    assert p176["head"] == geo["head"] == HEAD and p176["caller"] == geo["caller"] == CALLER
    assert geo["owned_rises"] == 23 and geo["old_bank_keys"] == 47 and geo["events"] == 76466
    assert geo["sites_with_donors"] == 8 and geo["donor_pairs"] == 13
    covered = Counter(r["owner_rank"] for r in geo["records"] if r["candidates"])
    assert covered == {1: 4, 2: 3, 4: 1}
    assert 17 * sum(rank * count for rank, count in covered.items()) == 238
    assert p176["added_paid_children"] == 0 and p176["ordinary_source_units_upper"] == 782817804
    geometry = results["R176-GEOMETRY.json"]
    write(stage / "GEOMETRY.json", geometry)
    write(stage / "inputs" / "GEOMETRY.json", geometry)

    mod = execute("R176-MODULAR.json", "screen.py", stage / "inputs" / WORD)
    signed = execute("R176-SIGNED.json", "values.py")
    assert not mod["survivors"] and not signed["unresolved_pairs"] and not signed["capped"]
    assert len(mod["cases"]) == signed["tested_pairs"] == signed["excluded_pairs"] == 13
    for row in mod["cases"]:
        a, b = row["owner"], row["donor"]
        assert (a[0] * b[1] - a[1] * b[0]) % mod["modulus"], row["key"]

    max_copies = max(len(r["unchanged_target_bank"]) + 1 for r in geo["records"] if r["candidates"])
    assert max_copies == 28
    assert p176["extra_lifetimes_per_native"] == 1
    p177 = {
        "ascent_price_sha256": digest(results["R176-PRICE.json"]),
        "caller": CALLER,
        "cases": geo["donor_pairs"],
        "extra_lifetimes": p176["extra_lifetimes_per_native"],
        "geometry_sha256": digest(geometry),
        "hard_cap_seconds": 35,
        "max_add_copy_per_native": max_copies,
        "max_coeff_bits": 24,
        "max_coeff_denominator_divides": 37748736000,
        "max_coeff_magnitude": 65534,
        "max_ordinary_source_units": 782715464 + 17 * (6 * 1000 + 4 + max_copies * 340),
        "native": HEAD,
        "no_new_paid": not p176["added_paid_children"],
        "retained_paid_delta": {r: detail["delta_paid"] for r, detail in p176["cases"].items()},
        "whole_stock_upper": p176["total_relaxed_gross"],
    }
    raw_price = (dumps(p177, sort_keys=True, indent=2) + "\n").encode()
    record("R177-PRICE.json", raw_price)
    write(stage / "PRICE.json", raw_price)
    reverse = execute("R177-REVERSE.json", "lead_span.py", stage / "inputs" / WORD)
    forward = execute("R177-FORWARD.json", "independent_span.py")
    assert reverse["head"] == forward["head"] == HEAD and reverse["caller"] == forward["caller"] == CALLER
    assert not reverse["survivors"] and not forward["unresolved_pairs"] and not forward["capped"]
    assert len(reverse["cases"]) == forward["tested_pairs"] == forward["excluded_pairs"] == 13
    assert {tuple(row["key"]) for row in reverse["cases"]} == keys(forward["results"])
    assert {tuple(row["key"]) for row in mod["cases"]} == keys(signed["checks"]) == keys(forward["results"])
    assert all(r["proof"]["status"] in ("exact_rank_exclusion", "absent_exterior_coordinate")
               for r in reverse["cases"])

    changed = stage / "inputs" / "R137-LEAD.json"
    write(changed, changed.read_bytes() + b" ")
    try:
        launch("independent_span.py")
    except CalledProcessError as exc:
        assert exc.returncode == 1 and b"inputs/R137-LEAD.json" in exc.stderr
    else:
        raise AssertionError("corrupted source receipt was accepted")
    if output is not None:
        output.mkdir(parents=True)
        for name, raw in results.items():
            write(output / name, raw)
    print("PASS_P104_ONE_DONOR_MOVE_HOIST ascents=23 eligible=13 signed_excluded=13 augmented_excluded=13 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    with TemporaryDirectory() as stage:
        replay(Path(stage), args.out)


if __name__ == "__main__":
    main()
