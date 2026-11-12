"""Authenticate frozen separators and replay the coupled price exclusion."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
COMMON = ("7334-WORD.json.gz", "R92-PRICE.json", "pricing.py")


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def source(name):
    path = (ROOT / name).resolve()
    assert path.is_relative_to(ROOT) and path.relative_to(ROOT).as_posix() == name
    return path.read_bytes()


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate():
    pins = decode(source("LOCAL-PINS.json"))
    for name, expected in pins.items():
        raw = source(name)
        assert digest(raw) == expected, name
        if name.endswith(".json"):
            decode(raw)
    prov = decode(source("PROVENANCE.json"))
    for name, entry in prov["files"].items():
        raw = source(name)
        assert digest(raw) == entry["sha256"]
        assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == entry["git_blob"]
    assert digest(decompress(source("inputs/7334-WORD.json.gz"))) == prov["source_payload_sha256"]
    raw = decompress(source("inputs/PRIOR-RECEIPTS.json.gz"))
    assert digest(raw) == prov["derived_inputs"]["inputs/PRIOR-RECEIPTS.json.gz"]["decompressed_sha256"]
    assert decode(source("inputs/PR7362-SHA256.json"))["R92-PRICE.json"] == pins["inputs/R92-PRICE.json"]
    fixture = decode(raw)
    assert set(fixture) == {"lead", "independent"}
    return fixture


def stage(tmp, method, fixture):
    work = tmp / method
    (work / "inputs").mkdir(parents=True)
    manifest = source("engines/" + method.upper() + "-PINS")
    expected = {}
    for line in manifest.decode().splitlines():
        h, name = line.split()
        path = Path(name)
        assert len(path.parts) == 2 and path.parts[0] == "inputs" and name not in expected
        expected[name] = h
    raw = {"inputs/" + n: source("inputs/" + n) for n in COMMON}
    assert not set(raw).intersection(fixture)
    raw.update({name: text.encode() for name, text in fixture.items()})
    assert {name: digest(data) for name, data in raw.items()} == expected
    for name, data in raw.items():
        (work / name).write_bytes(data)
    (work / "PINS").write_bytes(manifest)
    (work / "replay.py").write_bytes(source("engines/" + method + ".py"))
    return work, raw


def execute(work, method=None):
    p = run([sys.executable, "-I", "-B", str(work / "replay.py")], capture_output=True, timeout=22)
    if method is None:
        assert p.returncode == 1 and not p.stdout and b"AssertionError" in p.stderr
        return None
    if p.returncode:
        sys.stderr.write(p.stderr.decode(errors="replace"))
    p.check_returncode()
    assert digest(p.stdout) == decode(source("receipts/EXPECTED.json"))[method]["sha256"]
    return decode(p.stdout)


def lead_duals(raw):
    get = lambda name: decode(raw["inputs/" + name + ".json"])
    old = get("R200")["separator"]
    out = {(48765,48766,48767): (old["input"], old["source_value"])}
    for record in get("R201")["checked"]:
        d = record["decision"]
        out[tuple(record["clocks"])] = d["separating_covector"], d["separated_target"]
    for name in ("R203", "R204"):
        for record in get(name)["records"]:
            d = record["separator"]
            out[tuple(record["clocks"])] = d["input"], d["source_value"]
    assert len(out) == 119
    return out


def validate(lead, independent):
    assert lead["head"] == independent["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert lead["caller"] == independent["caller"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert lead["cases"] == independent["case_count"] == 119
    assert lead["counts"]["witness_coordinates"] == 1970
    assert independent["checks"]["dual_nonzero_coordinates"] == 1979
    assert not lead["positive"] and independent["first_positive_for_one_exact_span"] is None
    lead_case, = lead["priced"]
    case, = [c for c in independent["reports"] if c["promotion_options"]]
    other, = case["promotion_options"]
    assert case["clocks"] == lead_case["clocks"] == [48765,48766,48767]
    assert lead_case["role"] == other["donor"] == 831
    assert lead_case["last_role_contact"] == other["last_contact"] == 36896
    assert lead_case["charts"] == other["initial_final_promoted"] == [3,306,127]
    assert other["fusion_ranks"] == [3,5,8] and other["promotion_ranks"] == [4,5,9]
    assert other["signed_histogram"] == {"3":17,"4":-17,"8":-17,"9":17}
    assert other["uniform_deficit_dominated"] and other["status"] == "nonpositive"
    assert other["gross_interval"] == lead_case["gross"]
    lo, hi = map(Q, other["gross_interval"])
    assert Q("-0.055") < lo <= hi < Q("-0.054")
    return other["gross_interval"]


def main():
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 12) or not __debug__:
        raise SystemExit("CPython 3.12 with assertions is required")
    fixture = authenticate()
    with TemporaryDirectory(prefix="p104-finished-helper-promotion-") as name:
        tmp = Path(name)
        lead_work, lead_raw = stage(tmp, "lead", fixture["lead"])
        other_work, other_raw = stage(tmp, "independent", fixture["independent"])
        interval = validate(execute(lead_work, "lead"), execute(other_work, "independent"))
        old = run_path(str(ROOT / "engines/independent.py"))["exact_cases"](other_raw)
        word = decode(decompress(source("inputs/7334-WORD.json.gz")))
        checks = run_path(str(ROOT / "engines/verify_duals.py"))["readback"](word, old, lead_duals(lead_raw))
        assert checks == 238
        path = other_work / "inputs/7334-WORD.json.gz"
        raw = path.read_bytes()
        path.write_bytes(bytes([raw[0] ^ 1]) + raw[1:])
        execute(other_work)
    print(dumps({"cases":119,"exact_dual_checks":238,"sole_donor":831,"positive":0,
                 "net_interval":interval,"wrong_dual_and_corrupt_word_rejected":True,"kappa_delta":"0"},sort_keys=True))
    print("PASS_P104_FINISHED_HELPER_PROMOTION_PRICE_BOUND")


if __name__ == "__main__":
    main()
