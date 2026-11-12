"""Reproduce the guarded chart-242 closure at every public cut and role."""
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
        raise ValueError(f"invalid relative path {name}")
    return path


def authenticate():
    pins = decode((ROOT / "LOCAL-PINS.json").read_bytes())
    for name, expected in pins.items():
        if digest((ROOT / relative(name)).read_bytes()) != expected:
            raise ValueError(f"changed package dependency {name}")
    source = decode((ROOT / "PROVENANCE.json").read_bytes())
    for name, record in source["files"].items():
        raw = (ROOT / relative(name)).read_bytes()
        assert digest(raw) == record["sha256"] == pins[name]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == record["git_blob"]
    predecessor = decode((ROOT / "inputs/PR7363-SHA256.json").read_bytes())
    inputs = {}
    for name, key in source["derived_payloads"].items():
        raw = decompress((ROOT / "inputs" / (name + ".gz")).read_bytes())
        assert digest(raw) == predecessor[key]
        inputs[name] = raw
    funded = source["funded_cohort_payload"]
    cohort_source = decode((ROOT / relative(funded["manifest"])).read_bytes())
    cohort = decompress((ROOT / relative(funded["file"])).read_bytes())
    assert digest(cohort) == cohort_source[funded["key"]]
    inputs[funded["key"]] = cohort
    return inputs


def command(root, script, *args, check=True):
    result = run([sys.executable, "-I", "-B", str(root / script), *args],
                 capture_output=True, timeout=37)
    if check and result.returncode:
        sys.stderr.write(result.stderr.decode(errors="replace"))
        result.check_returncode()
    return result


def setup(root, stage, scripts, inputs, *, native=True):
    (root / "inputs").mkdir(parents=True)
    if native:
        copyfile(ROOT / "inputs/7334-WORD.json.gz", root / "inputs/7334-WORD.json.gz")
    for name, raw in inputs.items():
        path = root / relative(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    for name in scripts:
        path = root / relative(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        copyfile(ROOT / "engines" / stage / path.name, path)


def reject(root, name, script, *args):
    path = root / relative(name)
    raw = path.read_bytes()
    path.write_bytes(raw + b"\n")
    result = command(root, script, *args, check=False)
    assert result.returncode == 1 and not result.stdout
    assert b"changed dependency" in result.stderr and path.name.encode() in result.stderr
    path.write_bytes(raw)


def replay(root, out):
    prior_inputs = authenticate()
    expected = decode((ROOT / "receipts/SHA256.json").read_bytes())
    outputs = {}

    def record(stage, name, work, script, *args, target=None):
        key = f"{stage}/{name}.json"
        data = command(work, script, *args).stdout
        assert digest(data) == expected[key], ("changed receipt", key)
        outputs[key] = data
        if target is not None:
            (work / target).write_bytes(data)
        return decode(data)

    initial = root / "r125"
    source = {f"price/inputs/{k}": v for k, v in prior_inputs.items() if k != "R92-PRICE.json"}
    for key in ("READBACK.json", "pricing.py"):
        source[f"price/inputs/{key}"] = (ROOT / "inputs" / key).read_bytes()
    source["inputs/donor_span.py"] = (ROOT / "inputs/donor_span.py").read_bytes()
    setup(initial, "r125", ("price/freeze.py", "lead/history.py", "independent/maximal.py"), source)
    price = record("r125", "PRICE", initial, "price/freeze.py", target="price/PRICE-STOCK.json")
    lead = record("r125", "LEAD", initial, "lead/history.py")
    maximal = record("r125", "MAXIMAL", initial, "independent/maximal.py")
    assert price["head"] == lead["head"] == maximal["head"] == HEAD
    assert price["caller"] == lead["caller"] == maximal["caller"] == CALLER
    assert price["paid_delta"] == {} and price["productive_delta"] == {"4": 34, "8": -17}
    assert price["paid"] == 110519 and price["productive_new"] == 22478
    assert Fraction(price["complete_probe"][0]) > 0 > Fraction(price["extra_rank_one_complete_upper"])
    assert Fraction(price["fixed_target_complete_upper"]) < 0
    assert lead["status"] == "no guarded temporal span" and not lead["unresolved_frozen_form"]
    assert lead["prefix"] == {"1123": "1"} and lead["full_projection"]["residual"] == {"1123": "1"}
    assert lead["full_projection"]["rank"] == maximal["support_rank"] == 19
    assert lead["injection_keys"] == maximal["excluded_injection_keys"] == 354
    reject(initial, "price/inputs/R97-EXACT.json", "price/freeze.py")

    extended = root / "r126"
    inputs = {f"inputs/R125-{name}.json": outputs[f"r125/{name}.json"] for name in ("PRICE", "LEAD")}
    inputs["inputs/R125-INDEPENDENT.json"] = outputs["r125/MAXIMAL.json"]
    setup(extended, "r126", ("plan/freeze.py", "lead/contacts.py", "independent/topology.py",
                            "independent/agreement.py"), inputs)
    record("r126", "PRICE", extended, "plan/freeze.py", target="plan/PRICE.json")
    args = ("--price-sha256", expected["r126/PRICE.json"])
    record("r126", "FORWARD", extended, "lead/contacts.py", target="lead/RESULT.json")
    reverse = record("r126", "REVERSE", extended, "independent/topology.py", *args,
                     target="independent/RESULT.json")
    agreement = record("r126", "AGREEMENT", extended, "independent/agreement.py")
    assert outputs["r126/AGREEMENT.json"] == (ROOT / "receipts/AGREEMENT.json").read_bytes()
    assert reverse["status"] == "full suffix contained" and not agreement["unresolved"]
    assert agreement["interval_inclusive"] == [41740, 76466]
    assert agreement["before_maximal_cut_pairs"] == 60355
    assert agreement["at_and_after_maximal_cut_pairs"] == 267978
    assert agreement["all_public_cut_role_pairs"] == 328333
    (extended / "inputs/7334-WORD.json.gz").unlink()
    reject(extended, "plan/PRICE.json", "independent/topology.py", *args)

    funded = root / "r127"
    inputs = {
        "inputs/R125-INDEPENDENT.json": outputs["r125/MAXIMAL.json"],
        "inputs/R126-PRICE.json": outputs["r126/PRICE.json"],
        "inputs/R126-LEAD.json": outputs["r126/FORWARD.json"],
        "inputs/R126-AGREEMENT.json": outputs["r126/AGREEMENT.json"],
        "inputs/R97-EXACT.json": prior_inputs["R97-EXACT.json"],
        "inputs/R92-PRICE.json": prior_inputs["R92-PRICE.json"],
        "inputs/pricing.py": (ROOT / "inputs/pricing.py").read_bytes(),
    }
    setup(funded, "r127", ("plan/freeze.py", "lead/dual_transfer.py"), inputs, native=False)
    funded_price = record("r127", "PRICE", funded, "plan/freeze.py", target="plan/PRICE.json")
    transfer = record("r127", "TRANSFER", funded, "lead/dual_transfer.py")
    assert outputs["r127/TRANSFER.json"] == (ROOT / "receipts/FUNDED-TRANSFER.json").read_bytes()
    assert funded_price["paid_delta"] == {"1": 17}
    assert funded_price["target_delta"] == {"4": 17, "5": 17, "8": -17}
    assert len(funded_price["new_cohort"]) == 616 and funded_price["rank_surplus"] == 1424
    assert funded_price["paid"] == 110536 and funded_price["productive"] == 22478
    assert Fraction(funded_price["probe_complete_margin"][0]) > 0
    assert Fraction(funded_price["extra_rank_one_upper"]) < 0
    assert Fraction(funded_price["fixed_target_complete_upper"]) < 0
    assert transfer["funded_exit"] == [1123, 245, 127, 1]
    assert transfer["status"] == "funded exit still separated"
    assert transfer["funded_cohort_intersection"] == [1123] and transfer["dual_on_pivot"] == "1"
    assert transfer["dual_on_maximal_columns"] == ["0"] * 20
    reject(funded, "inputs/R92-PRICE.json", "plan/freeze.py")
    reject(funded, "inputs/R126-AGREEMENT.json", "lead/dual_transfer.py")

    assert set(outputs) == set(expected)
    if out is not None:
        out.mkdir(parents=True)
        for name, raw in outputs.items():
            path = out / relative(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
    print("PASS_STATIONARY_CHART242_HISTORY_BOUND pairs=328333 rank=19 tail_egress=12 funded_cohort=616 unresolved=0")


def main():
    assert __debug__ and sys.version_info[:2] == (3, 12)
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="new directory for nine regenerated receipts")
    args = parser.parse_args()
    with TemporaryDirectory() as tmp:
        replay(Path(tmp), args.out)


if __name__ == "__main__":
    main()
