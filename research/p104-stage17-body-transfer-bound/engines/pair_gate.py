"""Certify the two-slot Type B stage-17 bound from two matched exact receipts."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

LEAD = "01bae12428d3eee29174f69d00abf6ef1df2ff26930f91e045eb9f50c8c94856"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
SLOTS, J = (4646, 4660), 4691
DONORS, RAILS = (0, 1, 16, 17), (32, 33, 34, 35)


def unique(items):
    result = dict(items)
    assert len(result) == len(items), "Duplicate JSON key"
    return result


def load(path, expected):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == expected, f"Changed bytes in {path.name}"
    return loads(raw, object_pairs_hook=unique)


def timeout(*_):
    raise TimeoutError("10-second receipt cap")


def entries(triples):
    m = {(r, s): Q(v) for r, s, v in triples}
    assert len(m) == len(triples) and all(m.values())
    assert all(r in DONORS and s in DONORS for r, s in m)
    return m


def main():
    assert __debug__
    p = ArgumentParser(description=__doc__)
    p.add_argument("lead", type=Path)
    p.add_argument("independent", type=Path)
    p.add_argument("independent_sha256")
    p.add_argument("caller", type=Path)
    args = p.parse_args()
    signal(SIGALRM, timeout)
    alarm(10)
    lead = load(args.lead, LEAD)
    independent = load(args.independent, args.independent_sha256)
    c = load(args.caller, CALLER)
    assert lead["pins"]["caller_payload"] == independent["pins"]["inputs/CALLER.json"] == CALLER
    assert independent["comparator"] == HEAD and independent["caller_head"] == CALLER_HEAD
    assert independent["host_clock"] == J
    assert independent["q"] == independent["all_body_values"] == 1
    assert independent["expected_derivative_entries"] == [[i,i,"1"] for i in DONORS]
    assert independent["survivors"] == lead["unresolved"] == []
    l = {r["slot"]: entries(r["old_derivative"]) for r in lead["cases"]}
    i = {r["clock"]: entries(r["old_entries"]) for r in independent["cases"]}
    assert list(l) == list(i) == list(SLOTS) and l == i

    b, events = c["types"]["B"], c["events"]
    assert (b["offset"], b["roles"], len(b["ports"]), len(events)) == (36, 36, 8, 4783)
    assert [i for i,row in enumerate(b["diagonal"]) if row[18]] == list(DONORS)
    assert all(b["diagonal"][i][0:2] == [-1, 0] and sum(b["diagonal"][i][2:]) == 1
               and b["diagonal"][i][18] == 0 for i in RAILS)
    assert [t for t,e in enumerate(events) if (e[0]=="B" and e[1] in ("IDLE_ONE", "IDLE_ODD") and 17 in e[3])
            or e[:2]==["J",17]] == [*SLOTS, J]
    assert all(events[t] == ["B","IDLE_ONE",36,[17]] for t in SLOTS)
    assert events[J] == ["J",17,[17,0,18,35],[36,37,"-1","1/2"]]

    def summed(r, s):
        return sum(p.get((r,s), 0) for p in l.values())

    square = [[summed(r,s) for s in (0,1)] for r in (0,1)]
    one_factor_minors = {}
    for donor in DONORS:
        a,b = square[0]
        c,d = square[1]
        a -= donor == 0
        d -= donor == 1
        core_det = a*d - b*c
        assert core_det != 0
        one_factor_minors[donor] = {"core_rows_columns":[0,1],
                                   "core_matrix":[[str(a),str(b)],[str(c),str(d)]],
                                   "core_and_full_three_minor":str(core_det)}
    assert [r["core_and_full_three_minor"] for r in one_factor_minors.values()] == ["1","-5","-1","-1"]
    offdiag = summed(0,1)
    assert offdiag == 1 and all(l[t].get((0,1), 0) != 0 for t in SLOTS)
    one_factor = list(product(DONORS, RAILS))
    two_factor = [(u,v) for u,v in product(combinations(DONORS,2), combinations(RAILS,2))]
    assert len(one_factor) == 16 and len(two_factor) == 36
    alarm(0)
    print(dumps({"pins":{"lead_support":LEAD,"independent_support":args.independent_sha256,"caller":CALLER},
                 "comparator":HEAD,"caller_head":CALLER_HEAD,"slots":list(SLOTS),"unchanged_j":J,
                 "budgets":{"frozen_words":1,"core_minors":4,"persistent_off_diagonal_checks":1,"seconds":10},
                 "source_receipts_agree_on_all_slot_entries":True,"donors":list(DONORS),"rails":list(RAILS),
                 "one_factor_endpoint_count":len(one_factor),"one_factor_keys":one_factor,
                 "one_factor_minor_by_donor":one_factor_minors,
                 "two_factor_persistent_core_entry":{"row":0,"column":1,"value":str(offdiag)},
                 "two_factor_distinct_endpoint_count":len(two_factor),"two_factor_endpoint_keys":two_factor,
                 "two_factor_labelled_bijection_count":2*len(two_factor),
                 "one_slot_both_off_diagonal_values":[str(l[t][0,1]) for t in SLOTS],
                 "unresolved":[],"max_realized_raw_saving":"0",
                 "scope":"Unit body, q=+1. One or both D17 singleton slots, constant invertible wrappers ending before fixed J17, no other changed stage-17 contributor."},
                indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
