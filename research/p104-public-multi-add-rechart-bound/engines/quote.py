"""Price closed public multi-ADD midpoint components from frozen contact evidence."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
OLD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
TARGET = Q("0.0040075385047236")
PINS = {
    "inputs/ADMITTED.json": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "inputs/READBACK.json": "337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/7314-HELPERS.json": "bf353b3e05d0bf5fe3e49c15673c4cb9203251329bd594009303541cf7fecc09",
    "inputs/7334-CHANGED.json": "f4d3f6ca2d87f8cd68c01ac9f77b69bd5a796f92bd567cea8afe3ac7c72e8e4b",
    "inputs/7277-SUPPORT.json.gz": "a63d766dce9ccc5b7a97057fb298350617cbf78833f0ebc5bb488dec00e71159",
}
PAYLOAD = "32d05c4efa4c3f6e3cf08fc9dd21478e0fb5218a38556e290966e64193fe2d80"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def read(root, name):
    raw = (root/name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError("changed dependency: " + name)
    if name.endswith(".gz"):
        raw = decompress(raw)
        assert sha256(raw).hexdigest() == PAYLOAD
    return None if name.endswith(".py") else json.loads(raw,object_pairs_hook=unique)


def partition(rows):
    incidence, adjacent, open_routes = defaultdict(list), defaultdict(set), set()
    for i,row in enumerate(rows):
        a,b = row["moves"]
        evidence = row["scalar_evidence"]
        assert all(a<t<b for t in row["contacts"])
        assert row["contacts"] == [t for t,_ in evidence]
        assert len(set(row["contacts"])) == len(evidence)
        for t,kind in evidence:
            if kind == "nonzero_add_source":
                incidence[t].append(i)
            else:
                assert kind == "nonzero_scale_row"
    for t,members in incidence.items():
        assert len(members) in (1,2)
        if len(members)==1:
            open_routes.update(members)
            continue
        a,b=members
        assert rows[a]["charts"][1]==rows[b]["charts"][1]
        assert rows[a]["role"]!=rows[b]["role"]
        adjacent[a].add(b)
        adjacent[b].add(a)
    remaining = set(range(len(rows)))
    while remaining:
        todo = {min(remaining)}
        group = set()
        while todo:
            a = todo.pop()
            group.add(a)
            todo.update(adjacent[a]-group)
        remaining.difference_update(group)
        yield sorted(group),not bool(group&open_routes)


def matching(cases, key):
    clocks = [set(case["paid_clocks"]) for case in cases]
    conflicts = [sum(1<<j for j,b in enumerate(clocks) if a&b) for a in clocks]
    weights = [Q(case[key][1]) for case in cases]

    @cache
    def best(remaining):
        if not remaining:
            return Q(0),()
        bit = remaining & -remaining
        i = bit.bit_length()-1
        rest = best(remaining^bit)
        value, chosen = best(remaining & ~conflicts[i])
        return max(rest,(value+weights[i],(i,*chosen)))

    value, chosen=best((1<<len(cases))-1)
    return dict(upper=str(value),case_keys=[cases[i]["key"] for i in chosen])


def main(root):
    d = {name:read(root,name) for name in PINS}
    adm, base, helpers, changed, inherited = (d["inputs/"+name] for name in
        ("ADMITTED.json","READBACK.json","7314-HELPERS.json","7334-CHANGED.json","7277-SUPPORT.json.gz"))
    assert base["head"]==adm["head"]==HEAD and adm["exit"]==0 and base["copies"]==17
    assert base["caller_head"]==adm["caller"]==CALLER
    assert inherited["head"]==OLD and inherited["scope_exhausted"]
    rows=inherited["records"]
    assert len(rows)==4732 and len({(r["role"],*r["moves"]) for r in rows})==4732
    allowed={row["role"] for row in helpers["rows"]}
    protected=set(changed["roles"])|{863,1355,1531,1567,1568}
    assert helpers["complete"] and len(allowed)==1101 and 319 in protected
    paid,targets=(Counter({int(k):v for k,v in base[name].items()}) for name in ("paid","targets"))
    old=targets.copy();old.subtract(paid)
    assert (sum(paid.values()),sum(targets.values()),sum(k*v for k,v in old.items()))==(110519,22461,1424)
    assert not base["empty_root_credits"]
    cost=run_path(str(root/"inputs/pricing.py"))["cost"]
    incumbent=Q(base["new_raw_interval"][1])
    assert incumbent==Q(adm["crossing"][1])
    probe=incumbent+Q(1,10**9)
    assert cost(old,probe)[1]<0
    counts=Counter()
    all_prices=[]
    cases=[]
    for indexes, closed in partition(rows):
        component=[rows[i] for i in indexes]
        add=sorted({t for row in component for t,kind in row["scalar_evidence"] if kind=="nonzero_add_source"})
        if len(add)<2:
            continue
        counts["multi_add_graph_components"]+=1
        if not closed:
            continue
        counts["closed_multi_add_components"]+=1
        if any(r["role"] not in allowed-protected or r["hard_contacts"] for r in component):
            continue
        counts["closed_unprotected_helper_components"]+=1
        scales=sorted({t for row in component for t,kind in row["scalar_evidence"] if kind=="nonzero_scale_row"})
        if not scales:
            counts["closed_unprotected_ADD_only_components"]+=1
        midpoint=component[0]["charts"][1]
        assert all(r["charts"][1]==midpoint for r in component)
        assert len({r["role"] for r in component})==len(component)
        clocks=sorted(t for row in component for t in row["moves"])
        assert len(set(clocks))==len(clocks)
        route=sorted((dict(role=r["role"],moves=r["moves"],charts=r["charts"],ranks=r["ranks"],contacts=r["contacts"])
                       for r in component),key=lambda r:r["role"])
        shifts=[delta for delta in range(1-min(r["ranks"][0] for r in component),
                                                min(r["ranks"][1] for r in component)) if delta]
        if shifts:
            counts["components_with_positive_rank_stock"]+=1
        for delta in shifts:
            counts["rank_variants"]+=1
            shift=Counter()
            for row in component:
                p,q=row["ranks"]
                shift.update((p+delta,q-delta));shift.subtract((p,q))
            assert not sum(shift.values()) and not sum(k*v for k,v in shift.items())
            paid_delta={k:v*17 for k,v in sorted(shift.items()) if v}
            credit={k:-v for k,v in paid_delta.items()}
            gross=cost(credit,incumbent)
            new=old.copy();new.subtract(paid_delta)
            record=dict(key=[midpoint,add[0],delta],roles=[r["role"] for r in route],routes=route,
                add_clocks=add,scale_clocks=scales,paid_clocks=clocks,paid_delta=paid_delta,
                gross_incumbent=list(map(str,gross)),gross_moonshot=list(map(str,cost(credit,TARGET))),
                complete_probe=list(map(str,cost(new,probe))))
            all_prices.append(record)
            if gross[0]>0:
                counts["strictly_positive_rank_variants"]+=1
                assert cost(new,probe)[0]>0
                cases.append(record)
            elif gross[1]>0:
                counts["unresolved_price_variants"]+=1
    cases.sort(key=lambda row:(-Q(row["gross_incumbent"][0]),row["key"]))
    moonshot_margin=cost(old,TARGET)
    optimistic_moonshot=matching([r for r in all_prices if Q(r["gross_moonshot"][1])>0],"gross_moonshot")
    result=dict(head=HEAD,caller_head=CALLER,predecessor_head=OLD,source_sha256=PINS,
        word_sha256=adm["inputs"]["WORD.json.gz"],contact_payload_sha256=PAYLOAD,
        scope="Closed maximal connected components of at least two ADD contacts, with independent public helper windows between fixed paid MOVEs; scalar-only diagonal contacts permitted and recorded; current word unopened.",
        counts=counts,protected=sorted(protected),variants=all_prices,positive=cases,
        whole_incumbent=matching([r for r in all_prices if Q(r["gross_incumbent"][1])>0],"gross_incumbent"),
        whole_moonshot=optimistic_moonshot,incumbent=str(incumbent),probe=str(probe),moonshot=str(TARGET),
        old_moonshot_margin=list(map(str,moonshot_margin)),complete_moonshot_upper=str(moonshot_margin[1]+Q(optimistic_moonshot["upper"])),
        case_cap=len(cases),runner_cap_seconds=20,build_cap=1)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
