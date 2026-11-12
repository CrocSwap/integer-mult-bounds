"""Reproduce the 17 frozen same-span banks for two paid rank-two subdivisions."""
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

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
SHARED = ("7334-WORD.json.gz", "BENCHMARK.json", "pricing.py", "second_prime.py")


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def relative(name):
    path = PurePosixPath(name)
    if path.is_absolute() or path.as_posix() != name or ".." in path.parts:
        raise ValueError(f"invalid relative path: {name}")
    return path


def authenticate():
    pins = decode((ROOT / "LOCAL-PINS.json").read_bytes())
    for name, expected in pins.items():
        if digest((ROOT / relative(name)).read_bytes()) != expected:
            raise ValueError(f"changed package dependency: {name}")
    provenance = decode((ROOT / "PROVENANCE.json").read_bytes())
    for name, record in provenance["files"].items():
        raw = (ROOT / relative(name)).read_bytes()
        assert digest(raw) == record["sha256"] == pins[name]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == record["git_blob"]
    published = decode((ROOT / "inputs/PR7362-SHA256.json").read_bytes())
    inputs = {}
    for name in ("R92-GEOMETRY.json", "R92-PRICE.json"):
        raw = decompress((ROOT / "inputs" / (name + ".gz")).read_bytes())
        assert digest(raw) == published[name]
        inputs[name] = raw
    readback = decode((ROOT / "inputs/READBACK.json").read_bytes())
    price = decode(inputs["R92-PRICE.json"])
    bench = decode((ROOT / "inputs/BENCHMARK.json").read_bytes())
    assert readback["head"] == price["head"] == bench["head"] == HEAD
    assert readback["caller_head"] == price["caller_head"] == CALLER
    assert readback["copies"] == 17 and readback["empty_root_credits"] == 0
    assert (readback["paid_positions"], readback["productive_fields"], readback["rank_surplus"]) == (110519, 22461, 1424)
    assert readback["paid"] == price["old_paid"] and readback["targets"] == price["old_targets"]
    assert bench["receipt_sha256"]["peer-price/READBACK.json"] == pins["inputs/READBACK.json"]
    return inputs


def command(root, script, *, timeout=25, check=True):
    result = run([sys.executable, "-I", "-B", str(root / script)],
                 capture_output=True, timeout=timeout)
    if check and result.returncode:
        sys.stderr.write(result.stderr.decode(errors="replace"))
        result.check_returncode()
    return result


def seed(root, stage, scripts, shared, extra, inputs):
    for folder in ("inputs", *sorted({Path(name).parent.as_posix() for name in scripts})):
        (root / folder).mkdir(parents=True, exist_ok=True)
    for name in (*shared, *extra):
        copyfile(ROOT / "inputs" / name, root / "inputs" / name)
    for path in scripts:
        copyfile(ROOT / "engines" / stage / Path(path).name, root / path)
    for name, raw in inputs.items():
        (root / "inputs" / name).write_bytes(raw)


def reject(root, path, script):
    victim = root / path
    raw = victim.read_bytes()
    victim.write_bytes(raw + b"\n")
    result = command(root, script, check=False)
    assert result.returncode == 1 and not result.stdout
    assert b"changed dependency" in result.stderr and victim.name.encode() in result.stderr
    victim.write_bytes(raw)


def replay(root, out):
    prior_inputs = authenticate()
    expected = decode((ROOT / "receipts/SHA256.json").read_bytes())
    receipts = {}

    def record(stage, name, run_root, script, target=None):
        key = f"{stage}/{name}.json"
        raw = command(run_root, script).stdout
        assert digest(raw) == expected[key], ("changed receipt", key)
        receipts[key] = raw
        if target is not None:
            (run_root / target).write_bytes(raw)
        return decode(raw)

    first = root / "r99"
    seed(first, "r99", ("lead/quote.py", "lead/geometry.py", "lead/select.py", "lead/modular.py"),
         SHARED, (), prior_inputs)
    record("r99", "PRICE", first, "lead/quote.py", "lead/PRICE.json")
    geometry = record("r99", "GEOMETRY", first, "lead/geometry.py", "lead/GEOMETRY.json")
    selection = record("r99", "SELECTION", first, "lead/select.py", "lead/SELECTION.json")
    original = record("r99", "MODULAR", first, "lead/modular.py", "lead/MODULAR.json")
    assert geometry["stage"] == "complete" and geometry["timeout"] is None
    assert (geometry["visited_placements"], geometry["pair_comparisons"], geometry["visited_cuts"]) == (285, 108, 38967)
    assert len(geometry["representatives"]) == 102 and not geometry["owned_rejections"]
    assert len(selection["selected"]) == 16 and len(selection["unselected"]) == 1
    assert original["counts"] == {"prefix exclusion": 16} and original["prime"] == 65537
    assert all(row["prefix"]["rank"] == 2 and row["suffix"] is None for row in original["results"])
    assert original["unvisited"] == selection["unselected"]
    reject(first, "inputs/R92-PRICE.json", "lead/modular.py")

    second = root / "r120"
    inputs = {"R92-PRICE.json": prior_inputs["R92-PRICE.json"]}
    inputs.update({f"R99-{name}.json": receipts[f"r99/{name}.json"]
                   for name in ("PRICE", "GEOMETRY", "SELECTION", "MODULAR")})
    seed(second, "r120", ("plan/freeze.py", "lead/check.py", "independent/prefix.py", "independent/compare.py"),
         SHARED, ("donor_span.py", "paired_support.py"), inputs)
    price = record("r120", "PRICE", second, "plan/freeze.py", "plan/PRICE.json")
    exact = record("r120", "EXACT", second, "lead/check.py", "lead/RESULT.json")
    other = record("r120", "SECOND", second, "independent/prefix.py", "independent/RESULT.json")
    agreement = record("r120", "AGREEMENT", second, "independent/compare.py")
    assert receipts["r120/AGREEMENT.json"] == (ROOT / "receipts/AGREEMENT.json").read_bytes()
    assert price["head"] == exact["head"] == other["head"] == HEAD
    assert price["caller"] == exact["caller"] == other["caller"] == CALLER
    assert price["row"] == selection["unselected"][0]
    assert price["paid_delta"] == {"1": 68, "2": -34} and price["productive_delta"] == {"4": 17, "5": 17, "9": -17}
    assert (price["paid"], price["productive"], price["rank_surplus"]) == (110553, 22478, 1424)
    assert Fraction(price["probe_complete_margin"][0]) > 0 > Fraction(price["extra_rank_one_upper"])
    assert Fraction(price["fixed_target_complete_upper"]) < 0
    assert exact["status"] == "prefix exclusion" and exact["proof"]["axes"] == [0, 890]
    assert exact["proof"]["determinant"] == "-1/2"
    assert len(exact["raw_keys"]) == len(other["raw_excluded"]) == agreement["raw_keys_agreement"] == 9
    assert len(exact["representative_keys"]) == 6
    assert not exact["unresolved"] and not other["unresolved"] and agreement["unresolved"] == 0
    assert other["progress"] == {"events": 76466, "first_unvisited_cut": None}
    assert all(row["rank"] == 2 for row in other["rows"])
    assert agreement["primary_axes_det_mod_65537"] == 32768
    (second / "inputs/7334-WORD.json.gz").unlink()
    reject(second, "plan/PRICE.json", "independent/prefix.py")

    assert set(receipts) == set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name, raw in receipts.items():
            path = out / relative(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    print("PASS_TWO_PAID_SUBDIVISION_BANK_BOUND forms=17 previous=16 residual=1 raw_residual=9 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="new directory for all eight regenerated receipts")
    args = parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp), args.out)


if __name__ == "__main__":
    main()
