"""Regenerate and match exact rank certificates for every endpoint-crossing four-set."""
from ast import Assign, Name, literal_eval, parse
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from math import comb
from pathlib import Path
from shutil import copyfile
from subprocess import PIPE, run
from sys import executable, implementation, version_info
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
STAGES = ("lead", "independent")


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def execute(path):
    return run([executable, "-I", "-B", str(path)], cwd=path.parent,
               stdout=PIPE, stderr=PIPE, timeout=50)


def physical_specialization():
    src = parse((ROOT / "inputs/7113-signed-child.py").read_bytes())
    C = next(literal_eval(n.value) for n in src.body if isinstance(n, Assign)
             and isinstance(n.targets[0], Name) and n.targets[0].id == "C")
    for sign,eigen in ((1,(2,0)),(-1,(0,2))):
        for i in range(2):
            actual = tuple(C[i][0][k]+sign*C[i][1][k] for k in range(2))
            assert actual == tuple(sign**i*v for v in eigen)


def corrupted_caller():
    with TemporaryDirectory(prefix="p104-four-factor-negative-") as folder:
        root = Path(folder)
        (root / "inputs").mkdir()
        (root / "engines").mkdir()
        for name in ("R193.json","R194.json","R195.json"):
            copyfile(ROOT / "inputs" / name, root / "inputs" / name)
        c = read((ROOT / "inputs/CALLER.json").read_bytes())
        assert c["events"][43] == ["J",1,[1,0,18,19],[36,37,"-1","1/2"]]
        c["events"][43][2][0] = 2
        (root / "inputs/CALLER.json").write_text(dumps(c))
        target = root / "engines/independent.py"
        copyfile(ROOT / "engines/independent.py", target)
        result = execute(target)
        assert result.returncode == 1 and not result.stdout
        assert b"AssertionError: inputs/CALLER.json" in result.stderr


def compare(lead,other):
    assert not lead["capped"] and not other["capped"]
    assert lead["unvisited"] == 0 and other["unvisited"] == []
    assert lead["survivors"] == other["survivors"] == []
    assert lead["factors"] == len(other["factor_labels"]) == 38
    scope = [list(ids) for ids in combinations(range(38),4) if ids[0]<2 and ids[-1]>=36]
    assert len(scope) == comb(38,4)-2*comb(36,4)+comb(34,4) == 2381
    assert len(scope) == lead["case_cap"] == other["case_cap"]
    assert lead["modulus"] == 65521 and other["counts"] == {"4":2381}
    for key,a,b in zip(scope,lead["records"],other["records"],strict=True):
        assert key == a["case"] == b["factors"]
        assert a["rank"] == b["rank"] == 4
        assert len(a["image_pivots"]) == len(a["covector_pivots"]) == 4
        assert len(b["U_pivots"]) == len(b["V_pivots"]) == 4
        assert b["U_minor"] and b["V_minor"]


def main():
    assert __debug__ and implementation.name=="cpython" and version_info[:2]==(3,12)
    pins=read((ROOT / "LOCAL-PINS.json").read_bytes())
    for name,digest in sorted(pins.items()):
        path = (ROOT / name).resolve()
        assert path.is_relative_to(ROOT) and sha256(path.read_bytes()).hexdigest() == digest, name
    manifest = read((ROOT / "inputs/7113-SHA256.json").read_bytes())
    assert manifest["expected/ODD-TYPE-AB-CALLER.json"] == pins["inputs/CALLER.json"]
    assert manifest["replay/supplier7112/short-caller/signed_child.py"] == pins["inputs/7113-signed-child.py"]
    physical_specialization()
    data = {}
    for stage in STAGES:
        result = execute(ROOT / "engines" / f"{stage}.py")
        assert result.returncode == 0, (stage,result.stderr.decode())
        assert result.stdout == (ROOT / "receipts" / f"{stage.upper()}.json").read_bytes(), stage
        data[stage] = read(result.stdout)
    compare(data["lead"],data["independent"])
    corrupted_caller()
    print('{"relative_factors":38,"endpoint_crossing_cases":2381,"rank_four":2381,'
          '"unresolved":0,"corrupted_caller_rejected":true,"kappa_delta":"0"}')
    print("PASS_P104_SIGNED_PHASE_LEG_FOUR_FACTOR_BOUND")


if __name__=="__main__":
    main()
