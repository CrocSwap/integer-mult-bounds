"""Replay the final two delayed chart-127 exclusions and directed prices."""
from fractions import Fraction as F
from hashlib import sha256
from json import loads
from pathlib import Path, PurePosixPath
from runpy import run_path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
CASES = {
    220: ([40430,40432,46222], 46224, 298, [4,2,6], 8, 90),
    221: ([43091,43093,46566], 46568, 417, [1,1,2], 157, 65),
}


def unique(pairs):
    values = dict(pairs)
    assert len(values) == len(pairs), "duplicate JSON key"
    return values


def read(name):
    return loads((ROOT / name).read_bytes(), object_pairs_hook=unique)


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

    h = run_path(str(ROOT / "engines/pricing.py"))["power_bounds"]
    lo, hi = map(F, ("0.00364665195644044790699554028334161", "0.00364665195644044790699554028334162"))
    total_upper = F(0)
    for n, (key, cut, donor_count, ranks, support, bad_count) in CASES.items():
        certificate_path = f"receipts/R{n}-CERTIFICATE.json"
        certificate = read(certificate_path)
        lead = read(f"receipts/R{n}-LEAD-COMPARISON.json")
        output = run([executable, "-I", "-B", str(ROOT / "engines/scalar.py"),
                      str(ROOT / "inputs/7334-WORD.json.gz"), str(ROOT / certificate_path)],
                     check=True, capture_output=True, timeout=22).stdout
        actual = loads(output, object_pairs_hook=unique)
        assert actual == read(f"receipts/R{n}-INDEPENDENT.json")
        assert lead["key"] == certificate["key"] == actual["key"] == key
        assert lead["cut"] == certificate["cut"] == actual["cut"] == cut
        assert lead["roles"] == len(actual["chart_bank"]) == donor_count
        assert len(certificate["input"]) == support
        assert [actual["source_value"], actual["mutant_source_value"]] == lead["source_values"] == ["1","1"]
        assert set(actual["donor_values"].values()) == {"0"}
        assert sum(v != "0" for v in actual["mutant_donor_values"].values()) == lead["violating_mutant_donors"] == bad_count
        assert lead["rank_split"] == ranks
        a, b, ab = ranks
        lower = 17 * (h(a, hi)[0] + h(b, hi)[0] - h(ab, lo)[1])
        upper = 17 * (h(a, lo)[1] + h(b, lo)[1] - h(ab, hi)[0])
        assert [lower, upper] == list(map(F, lead["gross"]))
        assert 0 < lower < upper < 1
        total_upper += upper
    assert total_upper < F("0.3214")
    print("PASS_CHART127_DELAYED_BANKS: 2 cuts, all 715 donor values zero, both mutants rejected")


if __name__ == "__main__":
    main()
