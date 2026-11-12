"""Rebuild the exact three-J quote and both 153-window sign-rank censuses."""
from ast import Assign, Name, literal_eval, parse
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from shutil import copyfile
from subprocess import PIPE, run
from sys import executable, implementation, version_info
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
STAGES = {
    "lead192": "R192-LEAD", "independent192": "R192-INDEPENDENT",
    "lead193": "R193-LEAD", "independent193": "R193-INDEPENDENT",
}
PRICE_SOURCES = ("7334-WORD.json.gz", "7334-RESULT.json", "CALLER.json", "R92-PRICE.json", "pricing.py")


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def execute(path, timeout):
    return run([executable, "-I", "-B", str(path)], cwd=path.parent,
               stdout=PIPE, stderr=PIPE, timeout=timeout)


def prep_and_negative_control():
    with TemporaryDirectory(prefix="p104-window-controls-") as folder:
        root = Path(folder)
        (root / "inputs").mkdir()
        (root / "engines").mkdir()
        for name in PRICE_SOURCES:
            copyfile(ROOT / "inputs" / name, root / "inputs" / name)
        copyfile(ROOT / "prepare.py", root / "prepare.py")
        result = execute(root / "prepare.py", 20)
        assert result.returncode == 0 and not result.stdout, result.stderr.decode()
        for name in ("GRAPH.json", "PRICE.json"):
            assert (root / name).read_bytes() == (ROOT / "inputs" / name).read_bytes()
            copyfile(root / name, root / "inputs" / name)

        caller = read((root / "inputs/CALLER.json").read_bytes())
        assert caller["events"][43] == ["J",1,[1,0,18,19],[36,37,"-1","1/2"]]
        caller["events"][43][2][0] = 2
        (root / "inputs/CALLER.json").write_text(dumps(caller))
        copyfile(ROOT / "engines/independent192.py", root / "engines/independent192.py")
        negative = execute(root / "engines/independent192.py", 25)
        assert negative.returncode == 1 and not negative.stdout
        assert b"AssertionError: inputs/CALLER.json" in negative.stderr


def compare(results):
    lead, other = results["lead192"], results["independent192"]
    assert lead["rank"] == other["rank"] == 6
    assert lead["basis_columns"] == other["columns_per_sign"] == 36
    assert lead["clock_window_inclusive"] == other["window"] == [43,268]
    entries = {(i,j): Fraction(v) for i,j,v in lead["delta_entries"]}
    minor = [[entries.get((i,j), 0) for j in other["pivot_columns"]] for i in other["pivot_rows"]]
    assert minor == [[Fraction(v) for v in row] for row in other["minor"]]
    assert Fraction(other["nonzero_minor_determinant"]) == -64
    assert not other["four_query_gate_survives"]

    lead, other = results["lead193"], results["independent193"]
    assert not lead["capped"] and not other["capped"]
    assert lead["unvisited"] == other["unresolved_keys"] == []
    assert not lead["positive_price_upper"] and not lead["uniform_upper_positive"]
    assert len(lead["records"]) == len(other["cases"]) == 153
    for a,b in zip(lead["records"], other["cases"], strict=True):
        assert a["hosts"] == b["first_last"]
        assert a["clock_interval"] == [b["clocks"][0], b["clocks"][1]+1]
        assert a["rank"] == b["required_phase_rank"]
        assert a["retained_QUERY"] == b["retained_queries_per_port"]
        assert a["new_type_A_channels_lower"] == b["new_queries_lower_per_port"]
        assert a["optimistic_gross"] == b["incumbent_gross_interval"]
        assert a["uniform_price_upper"] == b["uniform_gross_upper"]
    upper = max(Fraction(r["uniform_gross_upper"]) for r in other["cases"])
    assert upper < Fraction("-43.31626802209")


def main():
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3,12)
    pins = read((ROOT / "LOCAL-PINS.json").read_bytes())
    for name, digest in sorted(pins.items()):
        path = (ROOT / name).resolve()
        assert path.is_relative_to(ROOT) and sha256(path.read_bytes()).hexdigest() == digest, name
    signed = read((ROOT / "inputs/7113-SHA256.json").read_bytes())
    assert signed["expected/ODD-TYPE-AB-CALLER.json"] == pins["inputs/CALLER.json"]
    assert signed["replay/supplier7112/short-caller/signed_child.py"] == pins["inputs/7113-signed-child.py"]
    stock = read((ROOT / "inputs/PR7362-SHA256.json").read_bytes())
    assert stock["R92-PRICE.json"] == pins["inputs/R92-PRICE.json"]
    source = parse((ROOT / "inputs/7113-signed-child.py").read_bytes())
    C = next(literal_eval(n.value) for n in source.body if isinstance(n,Assign)
             and isinstance(n.targets[0],Name) and n.targets[0].id == "C")
    for direction, eigen in ((1,(2,0)),(-1,(0,2))):
        for i in range(2):
            actual = tuple(C[i][0][k] + direction*C[i][1][k] for k in range(2))
            assert actual == tuple(direction**i * v for v in eigen)

    prep_and_negative_control()
    results = {}
    for stage,receipt in STAGES.items():
        result = execute(ROOT / "engines" / f"{stage}.py",65)
        assert result.returncode == 0, (stage,result.stderr.decode())
        assert result.stdout == (ROOT / "receipts" / f"{receipt}.json").read_bytes(), stage
        results[stage] = read(result.stdout)
    compare(results)
    print('{"first_three_rank":6,"windows":153,"positive_windows":0,'
          '"unresolved_windows":0,"corrupted_caller_rejected":true,"kappa_delta":"0"}')
    print("PASS_P104_CONTIGUOUS_DIRECT_J_REPLACEMENT_BOUND")


if __name__ == "__main__":
    main()
