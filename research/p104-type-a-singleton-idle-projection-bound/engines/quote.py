"""Price one Type A singleton idle square and the whole repeated-mask stock."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def checked(path):
    data = (ROOT / path).read_bytes()
    if sha256(data).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return data


def main():
    assert __debug__
    base, caller = (loads(checked(path)) for path in ("inputs/R92-PRICE.json", "inputs/CALLER.json"))
    checked("inputs/pricing.py")
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    ports = len(caller["types"]["A"]["ports"])
    assert ports == 96
    jobs = defaultdict(list)
    for t, event in enumerate(caller["events"]):
        if event[:2] == ["A", "IDLE_ONE"] and len(event[3]) == 1:
            jobs[event[3][0]].append([t, event[2]])
    assert dict(jobs) == {8: [[1466, 7], [1487, 25]], 9: [[1742, 10], [1766, 28]]}
    paid, targets = (Counter({int(r): n for r, n in base[k].items()}) for k in ("old_paid", "old_targets"))
    margin = targets.copy()
    margin.subtract(paid)
    assert (sum(paid.values()), sum(targets.values()), sum(r*n for r,n in margin.items())) == (110519, 22461, 1424)
    cases = {}
    for rank, change in ((8, {8: ports}), (16, {8: 2*ports, 16: -ports})):
        for count in (1, 2):
            delta = {r: count*n for r,n in change.items()}
            new = margin.copy()
            new.update(delta)
            cases[f"{rank}/{count}"] = dict(new_paid=sum(paid.values())-ports*count,
                    new_rank_surplus=sum(r*n for r,n in new.items()), paid_delta={r:-n for r,n in delta.items()},
                    estimates={label:dict(gross=list(map(str,cost(delta,Q(base[label])))),
                                         complete=list(map(str,cost(new,Q(base[label])))))
                               for label in ("old_crossing_upper", "probe", "moonshot")})
    assert Q(cases["16/1"]["estimates"]["probe"]["complete"][0]) > 0
    assert Q(cases["16/2"]["estimates"]["old_crossing_upper"]["gross"][1]) < 96
    print(dumps(dict(pins=PINS, head=base["head"], caller=base["caller_head"], ports=ports, cases=cases,
                     pair=[1466,1487], whole_singleton_stock=jobs, targets=sum(targets.values()),
                     ordinary_unit_reservation=32*ports*340+2*ports*(1000+64)), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
