"""Independently recover the two exact input rows at the old #7334 MOVE pair."""
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/PRICE.json": "5bac77abf307955e7eabcd7121e9657820e3d44d05a783193179055939137daa",
    "inputs/reverse_span.py": "f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
CLOCK, DONOR, TARGET, A, B, RANK = 32944, 625, 624, 3, 117, 5
COLUMNS, SECONDS = 1501, 20


def unique(items):
    out = dict(items)
    assert len(out) == len(items), "duplicate key"
    return out


def read(path):
    raw = (ROOT / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    return raw


def stop(*_):
    raise TimeoutError("20-second cap")


def dot(row, x):
    return sum(v*row.get(j,0) for j,v in x.items())


def decide(donor, target):
    if not donor:
        if not target:
            return {"status": "proportional", "lambda": Q(0)}
        j = min(target)
        return {"status": "excluded zero donor", "probe": {j: 1}, "target_value": target[j]}
    a = min(donor)
    scale = Q(target.get(a,0), donor[a])
    for b in sorted(donor.keys() | target.keys()):
        if target.get(b,0) == scale*donor.get(b,0):
            continue
        d1,d2 = donor[a],donor.get(b,0)
        t1,t2 = target.get(a,0),target.get(b,0)
        minor = d1*t2-d2*t1
        x = {a: -d2, b: d1}
        assert minor and dot(donor,x) == 0 and dot(target,x) == minor
        return {"status": "excluded nonzero minor", "coordinates": [a,b],
                "submatrix": [[d1,d2],[t1,t2]], "determinant": minor,
                "probe": {j:v for j,v in x.items() if v}, "target_value": minor}
    return {"status": "proportional", "lambda": scale}


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(SECONDS)
    deadline = monotonic() + SECONDS-1
    q = loads(read("inputs/PRICE.json"), object_pairs_hook=unique)
    assert (q["head"],q["caller"]) == (HEAD,CALLER)
    assert q["candidate"] == [CLOCK,DONOR,TARGET,A,B,RANK]
    assert q["signed_histogram_delta"] == {str(RANK):17} and q["new_paid_children"] == 0
    raw = decompress(read("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest() == PAYLOAD
    word = loads(raw, object_pairs_hook=unique)
    assert word["public"] == COLUMNS and len(word["program"]) == 76466
    assert word["program"][CLOCK:CLOCK+2] == [
        ["MOVE",DONOR,A,B,False],["MOVE",TARGET,A,B,False]]
    assert len(word["frames"][B])-len(word["frames"][A]) == RANK
    read("inputs/reverse_span.py")
    engine = run_path(str(ROOT/"inputs/reverse_span.py"))
    req = defaultdict(list, {CLOCK:[(DONOR,0),(TARGET,1)]})
    pairs = engine["transpose_prefix"](word, req, 2, deadline)
    rows = [{j:Q(value,denom) for j,value in integers.items()} for integers,denom in pairs]
    assert all(0 <= j < COLUMNS for row in rows for j in row)
    result = decide(*rows)
    positive = decide({4:Q(1),7:Q(-2)},{4:Q(-1,2),7:Q(1)})
    negative = decide({4:Q(1),7:Q(-2)},{4:Q(-1,2),7:Q(2)})
    assert positive == {"status":"proportional", "lambda":Q(-1,2)}
    assert negative["determinant"] == 1
    if result["status"] == "proportional":
        lam = result["lambda"]
        result["coefficient_grid_preflight"] = (abs(lam) <= 65534 and
            lam.numerator.bit_length() <= 24 and 37748736000%lam.denominator == 0)
    alarm(0)
    print(dumps({"head":HEAD,"caller":CALLER,"pins":PINS,"cut":CLOCK,"roles":[DONOR,TARGET],
                 "from_chart":A,"to_chart":B,"paid_rank":RANK,"case_cap":1,"source_coordinates":COLUMNS,
                 "runner_seconds_cap":SECONDS,"method":"exact reverse covector propagation",
                 "rows":rows,"support_sizes":[len(row) for row in rows],"decision":result,
                 "controls":["known rational proportional pair retained","one changed coefficient rejected"]},
                sort_keys=True,indent=2,default=str))


if __name__ == "__main__":
    main()
