"""Replay the fixed chart-922 separating input and directed MOVE quote."""
from fractions import Fraction as F
from hashlib import sha256
from json import loads
from pathlib import Path, PurePosixPath
from runpy import run_path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
BANK = [7, 587, 779, 949, 960]


def unique(pairs):
    values = dict(pairs)
    assert len(values) == len(pairs), "duplicate JSON key"
    return values


def read(name):
    return loads((ROOT / name).read_bytes(), object_pairs_hook=unique)


def dot(row, probe):
    return sum(F(value)*F(probe.get(key, 0)) for key, value in row.items())


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    manifest = read("PINS.json")
    files = {f.relative_to(ROOT).as_posix() for folder in ("engines", "inputs", "receipts")
             for f in (ROOT / folder).iterdir() if f.is_file()}
    assert set(manifest) == files | {"PROVENANCE.json"}
    for name, digest in manifest.items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and ".." not in path.parts
        assert sha256((ROOT / path).read_bytes()).hexdigest() == digest, name

    output = run([executable, "-I", "-B", str(ROOT / "engines/scalar.py"),
                  str(ROOT / "inputs/7334-WORD.json.gz"),
                  str(ROOT / "receipts/CERTIFICATE.json")], check=True,
                 capture_output=True, timeout=22).stdout
    actual = loads(output, object_pairs_hook=unique)
    assert actual == read("receipts/INDEPENDENT.json")
    lead = read("receipts/LEAD.json")
    certificate = read("receipts/CERTIFICATE.json")
    assert lead["clocks"] == actual["key"] == [41944, 41946, 43419]
    assert lead["cut"] == actual["cut"] == 43421
    assert lead["bank_roles"] == actual["chart_bank"] == BANK
    assert lead["ranks"] == [3, 2, 5] and lead["rank"] == 5
    probe = certificate["input"]
    assert lead["separator"]["input"] == probe == {"1": "1", "2": "1", "311": "1"}
    assert dot(lead["target"], probe) == F(actual["source_value"]) == 1
    assert all(dot(lead["bank"][str(i)], probe) == F(actual["donor_values"][str(i)]) == 0 for i in BANK)
    assert actual["mutant_drop_coordinate"] == 1
    mutant = {k:v for k,v in probe.items() if k != "1"}
    assert dot(lead["target"], mutant) == F(actual["mutant_source_value"]) == 0
    assert [dot(lead["bank"][str(i)], mutant) for i in BANK] == [F(actual["mutant_donor_values"][str(i)]) for i in BANK] == [0, 0, -2, 0, 0]

    h = run_path(str(ROOT / "engines/pricing.py"))["power_bounds"]
    lo, hi = map(F, ("0.00364665195644044790699554028334161", "0.00364665195644044790699554028334162"))
    lower = 17 * (h(3, hi)[0] + h(2, hi)[0] - h(5, lo)[1])
    upper = 17 * (h(3, lo)[1] + h(2, lo)[1] - h(5, hi)[0])
    assert [lower, upper] == list(map(F, lead["gross"]))
    assert F("0.20766650") < lower < upper < F("0.20766651") < 1
    print("PASS_CHART922_DELAYED_BANK: 5 donors zero, old source 1, one-component mutant rejected")


if __name__ == "__main__":
    main()
