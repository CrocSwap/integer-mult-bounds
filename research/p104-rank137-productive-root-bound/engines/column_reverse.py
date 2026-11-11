"""All-cut non-coordinate rank-137 root column gate on the signed #7113 caller."""

import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import runpy
from time import monotonic

CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PINS = {
    "lead/run/PRICE.json": "8df5a1b86b5c2429f1581dcf4216d51e45f4297fa94fabc7f9847b128d7568e2",
    "independent/reverse.py": "d763b974585a439472bcaacf0913fc5c8469ea24212545287a3a359526ff51cd",
    "independent/RESULT.json": "fc1124d08396cbd205424106e3053529a46648b036d3076bdd979f931fef6c30",
}
ROOTS = (0,18)
ZERO = (0,)*17
ONE = (1,)*17
LIMIT = 9568


def checked(path,pin):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != pin:
        raise ValueError(f"Changed source {path.name}")
    return raw


def save(path,data):
    raw = (json.dumps(data,sort_keys=True,indent=2)+"\n").encode()
    temp = path.with_suffix(".tmp")
    temp.write_bytes(raw)
    temp.replace(path)
    return sha256(raw).hexdigest()


def identify(rows):
    occupied = [r for r,row in enumerate(rows) if row]
    terms = [(r,q,body,scalar) for r in occupied for (q,body),scalar in sorted(rows[r].items())]
    assert terms and all(0 <= q < 4 and len(body) == 17 and any(scalar) for _,q,body,scalar in terms)
    origin,phase,body,_ = terms[0]
    base = {"column_rows":occupied,"terms":len(terms)}
    first = [origin,phase,list(body)]
    for r,q,m,_ in terms:
        if m != body:
            return {**base,"status":"mixed_body_exponents","conflicting_terms":[first,[r,q,list(m)]]}
    for r,q,m,_ in terms:
        if (q-phase)%2:
            return {**base,"status":"mixed_central_parity","conflicting_terms":[first,[r,q,list(m)]]}
    if any(x not in (0,1) for x in body):
        return {**base,"status":"non_squarefree_body","common_term":first}
    central = phase%2
    prefix_rank = 8*sum(body)+central
    ranks = [prefix_rank,137-prefix_rank]
    base.update(body=body,central_parity=central,ranks=ranks)
    if not 0 < prefix_rank < 137:
        return {**base,"status":"zero_rank_side"}
    coefficients = [[r,(q-central)%4,*map(str,scalar)] for r,q,m,scalar in terms]
    assert all(q in (0,2) for _,q,_,_ in coefficients)
    return {**base,"status":"positive_column_only","ordinary_even_coefficients":coefficients}


def controls(reverse):
    body = (1,)*8+(0,)*9
    active = [{(1,body):(Q(1),Q(0)),(3,body):(Q(0),Q(1,2))},
              {(3,body):(Q(-3,2),Q(1,3))}]
    positive = identify(active)
    assert positive["status"] == "positive_column_only" and positive["ranks"] == [65,72]
    assert len(positive["column_rows"]) == 2 and len(positive["ordinary_even_coefficients"]) == 3
    assert identify([*active,{(2,body):(Q(1),Q(0))}])["status"] == "mixed_central_parity"
    assert identify([*active,{(3,ZERO):(Q(1),Q(0))}])["status"] == "mixed_body_exponents"
    assert identify([{(1,(2,)+(0,)*16):(Q(1),Q(0))}])["status"] == "non_squarefree_body"
    assert identify([{(2,ZERO):(Q(1),Q(0))}])["status"] == "zero_rank_side"
    assert identify([{(3,ONE):(Q(1),Q(0))}])["status"] == "zero_rank_side"
    return [*reverse["control"](),"noncoordinate_even_residual_positive","mixed_body_rejected",
            "mixed_central_parity_rejected","repeated_body_rejected","zero_rank_both_sides"]


def price_record(frozen):
    assert (frozen["head"],frozen["caller_head"],frozen["copies"],frozen["ports_per_root"]) == (
        HEAD,CALLER_HEAD,17,96)
    assert tuple(frozen["root_roles"]) == ROOTS
    assert sum(frozen["original_paid"].values()) == 110536
    assert sum(frozen["original_productive"].values()) == 22461
    assert not frozen["paid_delta"]
    rows = frozen["stage_partition_classes"]
    assert len(rows) == 34 and len({r["ranks"][0] for r in rows}) == 34
    assert sum(r["stage_subset_multiplicity"] for r in rows) == 262142
    assert all(sum(row["ranks"]) == 137 and min(row["ranks"]) > 0 for row in rows)
    assert all(Q(row["complete_margin_interval"][0]) > 0 for row in rows)
    maximum = max(Q(row["credit_interval"][1]) for row in rows)
    assert 32 < maximum < 33
    assert Q(frozen["baseline_interval"][1])+maximum-96 < 0
    assert Q(frozen["baseline_interval"][1])+2*maximum-96 < 0
    return {
        "head":HEAD,"caller_head":CALLER_HEAD,"input_pins":{"caller":CALLER,**PINS},
        "scope":{"roots":ROOTS,"boundaries_per_root":4784,"case_cap":LIMIT,"hard_seconds":45},
        "old_invoice":frozen,
        "one_root_maximum_credit_upper":str(maximum),
        "both_roots_optimistic_credit_upper":str(2*maximum),
        "single_new_rank_one_job_debit_at_96_ports":"96",
        "one_root_margin_upper_with_one_rank_one_debit":
            str(Q(frozen["baseline_interval"][1])+maximum-96),
        "both_roots_margin_upper_with_one_rank_one_debit":
            str(Q(frozen["baseline_interval"][1])+2*maximum-96),
        "all_extra_ordinary_and_physical_work_granted_free_in_optimistic_quote":True,
        "predeclared_followup":{"max_cases":3,"paired_row_inverse_seconds":45,
                               "priced_compiler_ownership_seconds":90},
    }


def audit(caller,reverse,known,deadline):
    events = caller["events"]
    kind = caller["types"]["A"]
    assert len(events) == 4783 and kind["roles"] == 36 and len(kind["ports"]) == 96
    assert (Q(kind["alpha2"]),Q(kind["beta2"])) == (Q(-1),Q(0))
    expected = [(r,k) for r in ROOTS for k in reversed(range(len(events)+1))]
    assert len(expected) == LIMIT
    lookup = {(r["root"],r["boundary"]):r for r in known["records"]}
    assert len(lookup) == 241 and not known["positive_column_only"]
    matched = 0
    records = []
    completed_roots = []
    for r in ROOTS:
        assert kind["diagonal"][r][:2] == [-1,0] and tuple(kind["diagonal"][r][2:]) == ONE
        rows = [{} for _ in range(kind["roles"])]
        rows[r] = {(3,ONE):(Q(1),Q(0))}
        for boundary in reversed(range(len(events)+1)):
            if monotonic() >= deadline:
                break
            key = r,boundary
            row = {"root":r,"boundary":boundary,**identify(rows)}
            if key in lookup:
                prior = lookup[key]
                again = reverse["case"](rows,prior["slot"])
                assert again == {k:v for k,v in prior.items() if k not in ("root","boundary","slot")}
                matched += 1
            records.append(row)
            if boundary:
                reverse["undo"](rows,events[boundary-1],Q(kind["alpha2"]))
        else:
            assert rows[r] == {(0,ZERO):(Q(1),Q(0))}
            assert all(not row for i,row in enumerate(rows) if i != r)
            completed_roots.append(r)
            continue
        break
    assert [(r["root"],r["boundary"]) for r in records] == expected[:len(records)]
    if len(records) == LIMIT:
        assert matched == len(lookup) and completed_roots == list(ROOTS)
    return {
        "counts":dict(Counter(r["status"] for r in records)),
        "cases_visited":len(records),"unvisited":expected[len(records):],
        "old_coordinate_controls_matched":matched,"initial_endpoints_recovered":completed_roots,
        "survivors":[r for r in records if r["status"] == "positive_column_only"],
        "records":records,
    }


def main():
    start = monotonic()
    if not __debug__:
        raise RuntimeError("Assertions required")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--caller",type=Path,required=True)
    p.add_argument("--r54",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--seconds",type=float,default=42)
    p.add_argument("--price-only",action="store_true")
    args = p.parse_args()
    assert 0 < args.seconds <= 42
    raw_caller = checked(args.caller,CALLER)
    sources = {name:checked(args.r54/name,pin) for name,pin in PINS.items()}
    args.out.mkdir(parents=True,exist_ok=True)
    price_sha = save(args.out/"PRICE.json",price_record(json.loads(sources["lead/run/PRICE.json"])))
    if args.price_only:
        return
    reverse = runpy.run_path(str((args.r54/"independent/reverse.py").resolve()))
    known = json.loads(sources["independent/RESULT.json"])
    assert known["caller_sha256"] == CALLER
    checks = controls(reverse)
    result = audit(json.loads(raw_caller),reverse,known,start+args.seconds)
    save(args.out/"SUPPORT.json",{"head":HEAD,"caller_sha256":CALLER,"price_sha256":price_sha,
                                 "controls":checks,**result})


if __name__ == "__main__":
    main()
