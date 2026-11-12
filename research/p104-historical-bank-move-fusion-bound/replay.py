"""Authenticate and reproduce the exact historical-bank MOVE fusion screen."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from gzip import compress, decompress
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent


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
    refs = prov["derived_inputs"]
    assert digest(decompress(source("inputs/COFRAME.json.gz"))) == refs["inputs/COFRAME.json.gz"]["decompressed_sha256"]
    assert digest(source("inputs/BANK.json")) == refs["inputs/BANK.json"]["sha256"]
    price = refs["inputs/R92-PRICE.json"]
    assert decode(source("inputs/PR7362-SHA256.json"))[price["receipt_key"]] == pins["inputs/R92-PRICE.json"]


def execute(tmp, script, receipt, cap, output=None):
    result = run([sys.executable, "-I", "-B", str(tmp / script)], capture_output=True, timeout=cap)
    if receipt is None:
        assert result.returncode == 1 and not result.stdout and b"AssertionError" in result.stderr
        return None
    if result.returncode:
        sys.stderr.write(result.stderr.decode(errors="replace"))
    result.check_returncode()
    expected = decode(source("receipts/EXPECTED.json"))[receipt]["sha256"]
    assert digest(result.stdout) == expected, receipt
    if output:
        (output / (receipt + ".json")).write_bytes(result.stdout)
    return result.stdout


def validate(r200, first, second, readback):
    assert r200["key"] == [48765,48766,48767,1034,1561]
    assert r200["bank_cap"] == 760 and r200["source_coordinates"] == 1501
    assert r200["target_row"] == [{"831":-1,"1497":1},1]
    assert r200["decision"] == {"coordinate":831,"status":"absent_exterior_coordinate","target_coefficient":"-1"}
    assert not first["capped"] and not first["unvisited"]
    assert len(first["records"]) == readback["checked"] == 967
    assert first["excluded_count"] == readback["coordinate_excluded"] == 724
    assert len(first["screen_survivors"]) == 243
    control, = [c for c in first["records"] if c["clocks"] == r200["key"][:3]]
    assert control["missing_witness"] == [831,"-1"] and control["bank_count"] == 760
    assert not second["capped"] and not second["unresolved_within_top_six"] and second["winner"] is None
    assert len(second["checked"]) == readback["dual_checks"] == 6
    assert all(c["decision"]["status"] == "exact_rank_exclusion" for c in second["checked"])
    assert second["reconstructed_rows"] == 31
    checked = {tuple(c["clocks"]) for c in second["checked"]}
    assert checked == {tuple(c["clocks"]) for c in first["screen_survivors"][:6]}
    remaining = [c for c in first["screen_survivors"] if tuple(c["clocks"]) not in checked]
    assert len(remaining) == second["outside_top_six_unresolved_count"] == 237
    upper = sum(Q(c["gross"][1]) for c in remaining)
    assert Q("28.040") < upper < Q("28.041")
    best = second["checked"][0]
    assert best["clocks"] == [40102,40103,44609]
    assert best["decision"]["separating_covector"] == {"58":"1","1493":"-1/2"}
    # Omitting the second coefficient destroys the separating property.
    assert any(row.get("58", 0) for _, (row, _) in best["bank_rows"])
    return upper


def replay(tmp, output):
    inputs = tmp / "inputs"
    inputs.mkdir()
    for path in (ROOT / "inputs").iterdir():
        if path.name != "COFRAME.json.gz":
            (inputs / path.name).write_bytes(source("inputs/" + path.name))
    (inputs / "COFRAME.json").write_bytes(decompress(source("inputs/COFRAME.json.gz")))
    for script in ("r200.py", "stage1.py", "stage2.py", "readback.py", "bank_gate.py"):
        (tmp / script).write_bytes(source("engines/" + script))
    (tmp / "PINS").write_bytes(source("engines/READBACK-PINS"))
    r200 = execute(tmp, "r200.py", "R200", 22, output)
    (inputs / "R200-RESULT.json").write_bytes(r200)
    first = execute(tmp, "stage1.py", "STAGE1", 27, output)
    (tmp / "STAGE1.json").write_bytes(first)
    second = execute(tmp, "stage2.py", "STAGE2", 47, output)
    (inputs / "STAGE1.json").write_bytes(first)
    (inputs / "STAGE2.json").write_bytes(second)
    readback = execute(tmp, "readback.py", "READBACK", 27, output)
    upper = validate(*(decode(x) for x in (r200, first, second, readback)))
    target = inputs / "7334-WORD.json.gz"
    word = decode(decompress(target.read_bytes()))
    word["program"][48766][3] = "-1"
    target.write_bytes(compress(dumps(word).encode(), mtime=0))
    execute(tmp, "r200.py", None, 22)
    execute(tmp, "stage1.py", None, 27)
    return upper


def main():
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 12) or not __debug__:
        raise SystemExit("CPython 3.12 with assertions is required")
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="directory for regenerated JSON receipts")
    args = parser.parse_args()
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
    authenticate()
    with TemporaryDirectory(prefix="p104-historical-bank-move-") as name:
        upper = replay(Path(name), args.out)
    print(dumps({"cases":967,"coordinate_excluded":724,"exact_dual_excluded":6,"unresolved":237,
                 "unresolved_gross_upper":str(upper),"r200_missing_coordinate":831,
                 "corrupt_word_and_dual_controls":True,"kappa_delta":"0"},sort_keys=True))
    print("PASS_P104_HISTORICAL_BANK_MOVE_FUSION_BOUND")


if __name__ == "__main__":
    main()
