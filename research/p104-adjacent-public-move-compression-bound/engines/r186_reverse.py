"""One independent backwards pass for all adjacent equal-chart public MOVE pairs."""
from collections import Counter, defaultdict
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
    "inputs/r185.py": "8b72adacd30cf991c827225468415fb7f73345ae5891dcde27d4dd11e2ba4156",
    "inputs/R185.json": "275520b630339d2fca5934c0af8075147541a7acb5569b0f65c1135f174e89eb",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
CASES, COLUMNS, SECONDS = 29, 1501, 25


def unique(items):
    result = dict(items)
    assert len(items) == len(result), "duplicate key"
    return result


def read(path):
    raw = (ROOT / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    return raw


def stop(*_):
    raise TimeoutError("25-second reverse cap")


def load_engine(path):
    read(path)
    return run_path(str(ROOT / path))


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(SECONDS)
    until = monotonic() + SECONDS-1
    result = {"head": HEAD, "caller": CALLER, "pins": PINS, "case_cap": CASES,
              "source_coordinates": COLUMNS, "runner_seconds_cap": SECONDS,
              "resolved": [], "unresolved": [], "capped": False}
    try:
        quote = loads(read("inputs/PRICE.json"), object_pairs_hook=unique)
        old = loads(read("inputs/R185.json"), object_pairs_hook=unique)
        assert (old["head"],old["caller"]) == (quote["head"],quote["caller"]) == (HEAD,CALLER)
        keys = quote["pairs"]
        assert len(keys) == len({tuple(x) for x in keys}) == CASES
        result["unresolved"] = keys.copy()
        raw = decompress(read("inputs/7334-WORD.json.gz"))
        assert sha256(raw).hexdigest() == PAYLOAD
        word = loads(raw, object_pairs_hook=unique)
        assert (word["public"],len(word["program"])) == (COLUMNS,76466)
        requests = defaultdict(list)
        for j,(clock,d,t,a,b,rank) in enumerate(keys):
            assert word["program"][clock:clock+2] == [["MOVE",d,a,b,False],["MOVE",t,a,b,False]]
            assert len(word["frames"][b])-len(word["frames"][a]) == rank
            requests[clock].extend(((d,2*j),(t,2*j+1)))
        reducer = load_engine("inputs/reverse_span.py")["transpose_prefix"]
        decide = load_engine("inputs/r185.py")["decide"]
        cost = load_engine("inputs/pricing.py")["cost"]
        power_at = Q(quote["old_crossing_upper"])
        exact = reducer(word,requests,2*CASES,until)
        controls = []
        for j,key in enumerate(keys):
            left,right = [{i:Q(v,denom) for i,v in body.items()} for body,denom in exact[2*j:2*j+2]]
            assert all(0 <= i < COLUMNS for row in (left,right) for i in row)
            swapped = not left and bool(right)
            decision = decide(right,left) if swapped else decide(left,right)
            if key == quote["candidate"]:
                old_rows = [{int(i):Q(v) for i,v in row.items()} for row in old["rows"]]
                assert [left,right] == old_rows
                canon = loads(dumps(decision,default=str))
                assert canon == old["decision"]
                controls.append("exact R185 rows and determinant reproduce")
            rec = {"key":key,"support_sizes":[len(left),len(right)],"orientation_swapped":swapped,
                   "decision":decision,"donor_row":right if swapped else left,
                   "target_row":left if swapped else right}
            if decision["status"] == "proportional":
                rec["gross_interval_before_other_charges"] = cost({key[-1]:17},power_at)
            else:
                assert decision["status"] == "excluded nonzero minor"
            result["resolved"].append(rec)
            result["unresolved"].remove(key)
        assert decide({0:Q(1),2:Q(-2)},{0:Q(-1,2),2:Q(1)})["lambda"] == Q(-1,2)
        assert decide({0:Q(1),2:Q(-2)},{0:Q(-1,2),2:Q(2)})["determinant"] == 1
        result["controls"] = controls+["known proportional pair retained","altered coefficient rejected"]
    except TimeoutError as err:
        result.update(capped=True, cap_reason=str(err))
    finally:
        alarm(0)
    result["statistics"] = Counter(r["decision"]["status"] for r in result["resolved"])
    print(dumps(result,sort_keys=True,indent=2,default=str))
    if result["capped"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
