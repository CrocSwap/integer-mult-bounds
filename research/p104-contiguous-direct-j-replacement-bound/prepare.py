"""Pin the three-J invoice and graph before any feasibility search."""
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/7334-RESULT.json": "7f2d587c59f063b01f1e8b320084a7f0943f2f05d65e3e0f5e80448c6c8e8194",
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
CLOCKS = (43, 137, 268)


def emit(name, data):
    (ROOT / name).write_text(dumps(data, sort_keys=True, indent=2, default=str) + "\n")


def main():
    assert __debug__
    for name, digest in PINS.items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    def read(name):
        return loads((ROOT / "inputs" / name).read_bytes())
    raw = decompress((ROOT / "inputs/7334-WORD.json.gz").read_bytes())
    assert sha256(raw).hexdigest() == "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    word = loads(raw)
    caller = read("CALLER.json")
    result = read("7334-RESULT.json")["price"]["after"]
    quote = read("R92-PRICE.json")
    assert len(caller["events"]) == 4783
    assert len(caller["types"]["A"]["ports"]) == 96 and len(caller["types"]["B"]["ports"]) == 8
    roles = [[1, 0, 18, 19], [2, 0, 18, 20], [3, 0, 18, 21]]
    events = caller["events"]
    assert [events[i] for i in CLOCKS] == [["J", j, role, [36,37,"-1","1/2"]] for j,role in enumerate(roles, 1)]
    main_roles = set(word["live"]) | {r+112 for r in word["live"]} | set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    helpers = sorted(set(range(word["public"])) - main_roles)
    assert (len(main_roles), len(helpers), len(word["program"])) == (400,1101,76466)
    def rank(chart):
        return len(word["frames"][chart])
    P = Counter(abs(rank(e[3])-rank(e[2])) for e in word["program"] if e[0]=="MOVE")
    T = Counter(rank(word["final"][r])-rank(word["initial"][r]) for r in helpers)
    assert sum(P.values()) == 6279 and min(T) > 0
    assert sum(r*n for r,n in P.items()) == 11004 and sum(r*n for r,n in T.items()) == 7692
    oldP,oldT = [Counter({int(r):n for r,n in result[h].items()}) for h in ("P","T")]
    assert (sum(oldP.values()),sum(oldT.values()),result["S"]) == (110519,22461,1424)
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    k = Fraction(quote["old_crossing_upper"])
    dT = {r:-3*n for r,n in T.items()}
    prices = {}
    for transitions in (0,4,5,6):
        dP = Counter({r:-3*n for r,n in P.items()})
        dP.update({8:1200,1:3*16+96*transitions})
        margin = Counter(dT)
        margin.subtract(dP)
        prices[str(transitions)] = {"delta_P":dP,"delta_T":dT,"raw_gross":cost(margin,k)}
    assert Fraction(prices["4"]["raw_gross"][0]) > 55
    assert Fraction(prices["5"]["raw_gross"][1]) < -40
    lo, hi = CLOCKS[0], CLOCKS[-1]
    typed_events = [[i,e] for i,e in enumerate(events[lo:hi+1],lo) if e[0] in ("A","J")]
    assert not any(e[:2] in (["A","QUERY"],["A","SWAP"]) for _,e in typed_events)
    constraints = []
    for i,e in typed_events:
        if e[0]=="J":
            constraints.extend([[i,e[2][0],e[2][1],1],[i,e[2][2],e[2][3],1]])
        elif e[1]=="ADD":
            constraints.append([i,e[2],e[3],0])
        else:
            assert e[1] in ("IDLE_ONE","LAMBDA","SCALE")
    emit("GRAPH.json", {"pins":PINS,"clocks":CLOCKS,"window_inclusive":[lo,hi],
                        "fixed_gauge_roots":[0,18],"type_a_roles":36,"typed_events":typed_events,
                        "constraints_clock_role_role_xor":constraints,"fixed_boundary_parity":0,
                        "max_charged_toggles_per_port":4,"runner_cap_seconds":20})
    emit("PRICE.json",{"pins":PINS,"head":quote["head"],"caller":quote["caller_head"],
                       "exact_crossing_upper":k,"clocks":CLOCKS,"per_J_old_P":P,"per_J_old_helper_T":T,
                       "old_full_P":oldP,"old_full_T":oldT,"retired_helper_ids_each_J":helpers,
                       "new_rank8_children":1200,"new_type_b_rank1_children":48,
                       "price_by_type_a_rank1_per_port":prices,"criterion_four_passes_five_fails":True})


if __name__ == "__main__":
    main()
