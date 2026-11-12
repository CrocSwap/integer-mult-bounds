"""Exact reverse covectors for the thirteen augmented destination banks."""
from collections import defaultdict
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic
import sys

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/GEOMETRY.json": "d1319c5df9f1f9227c8d364447834a8d54d60ff25bbb1890f9754672bbfb22c0",
    "inputs/reverse_span.py": "f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff",
    "PRICE.json": "81033768fdd58b304c388afa56208ac7d2864a6ff39ec883dd2fbc0c33872285",
}
ZIP = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def read(path):
    raw = (ROOT/path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    return raw


def stop(*_):
    raise TimeoutError("35-second exact augmented bank cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(35)
    cap = monotonic()+34
    geo = loads(read("inputs/GEOMETRY.json"))
    read("inputs/reverse_span.py")
    pricing = loads(read("PRICE.json"))
    raw = Path(sys.argv[1]).read_bytes()
    assert sha256(raw).hexdigest() == ZIP
    payload = decompress(raw)
    assert sha256(payload).hexdigest() == PAYLOAD
    w = loads(payload)
    engine = run_path(str(ROOT/"inputs/reverse_span.py"))
    controls = engine["controls"]()

    requests = defaultdict(list)
    ids = {}
    cases = []
    for x in geo["records"]:
        t, owner, B = x["clock"],x["owner"],x["to_chart"]
        for peer, next_clock, low, high, owned in x["candidates"]:
            assert high==B and w["program"][next_clock]==["MOVE",peer,low,B,owned]
            assert w["program"][t]==["MOVE",owner,x["from_chart"],B,True]
            bank = sorted([*x["unchanged_target_bank"],peer])
            assert len(bank)==len(set(bank))<=pricing["max_add_copy_per_native"] and owner not in bank
            cases.append(([t,owner,peer,next_clock],bank))
            for role in [owner,*bank]:
                if (t,role) not in ids:
                    ids[t,role] = len(ids)
                    requests[t].append((role,ids[t,role]))
    assert len(cases)==geo["donor_pairs"]==pricing["cases"]==13
    values = engine["transpose_prefix"](w,requests,len(ids),cap)
    result = []
    for (t,r,peer,k),bank in cases:
        target = values[ids[t,r]]
        proof = engine["exact_span"]([(j,values[ids[t,j]]) for j in bank],target)
        check = {"key":[t,r,peer,k],"bank":bank,"proof":proof}
        if proof["status"]=="exact_span":
            coefficients = list(map(Fraction,proof["coefficients"].values()))
            check["alphabet"] = all(abs(q)<=65534 and q.numerator.bit_length()<=24
                                    and 37748736000%q.denominator==0 for q in coefficients)
        result.append(check)
    alarm(0)
    print(dumps({"head":geo["head"],"caller":geo["caller"],"pins":PINS,"word_zip":ZIP,
        "distinct_rows":len(ids),"word_events":len(w["program"]),"cases":result,"controls":controls,
        "survivors":[r["key"] for r in result if r["proof"]["status"]=="exact_span"],"cap_seconds":35},
        sort_keys=True,indent=2))


if __name__=="__main__":
    main()
