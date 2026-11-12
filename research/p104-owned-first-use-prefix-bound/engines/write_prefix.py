"""Check paid owner reconstruction after the last private write."""
from collections import Counter,defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R137-PRICE.json":"1e8270d9a48728327f7eab9610a272fbb8ef09518dc4ddc5ceb573be00ae2beb",
    "inputs/R137-RESULT.json":"a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
    "inputs/R92-PRICE.json":"05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/aggregate.py":"8bf1b91d7fc0937305466686522f5fb3920c66c71830acfc94adde84ba4f49e1",
    "inputs/donor_span.py":"4d5306e2c0b7e91c79d22c82e8e760aed2c311979298c558e631975d4d1ae5b1",
    "inputs/pricing.py":"f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def unique(pairs):
    obj=dict(pairs)
    if len(obj)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return obj


def read(path):
    data=(ROOT/path).read_bytes()
    if sha256(data).hexdigest()!=PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return data


def private(event, role):
    return event[0] in {"ADD","SCALE"} and event[1]==role


def quote():
    old,pre,source=(loads(read(p),object_pairs_hook=unique) for p in
                    ("inputs/R92-PRICE.json","inputs/R137-PRICE.json","inputs/R137-RESULT.json"))
    assert old["head"]==pre["head"]==source["head"] and source["counts"]=={"outside donor span":47}
    rows=[{k:r[k] for k in ("role","move_clock","chart_from","chart_to","rank","first_clock","first_event")}
          for r in source["records"] if private(r["first_event"],r["role"])]
    assert all(r["first_clock"]==r["move_clock"]+1 for r in rows)
    ranks=Counter(r["rank"] for r in rows)
    read("inputs/pricing.py")
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    at,moon=Q(old["old_crossing_upper"]),Q(old["moonshot"])
    paid,target=(Counter({int(r):v for r,v in old[k].items()}) for k in ("old_paid","old_targets"))
    target.subtract(paid)
    delta={r:17*n for r,n in ranks.items()}
    full=target.copy()
    full.update(delta)
    return dict(head=old["head"],caller=old["caller_head"],pins=PINS,rows=rows,
        rank_counts=ranks,one=pre["one"],whole_gross_upper=str(cost(delta,at)[1]),
        fixed_target_complete_upper=str(cost(full,moon)[1]),
        case_cap=len(rows),event_cap=76466,runner_seconds_cap=30)


def cases(word,p):
    tape=word["program"]
    for row in p["rows"]:
        role,move,chart=row["role"],row["move_clock"],row["chart_to"]
        assert tape[move]==["MOVE",role,row["chart_from"],chart,True]
        assert tape[row["first_clock"]]==row["first_event"]
        writes=[]
        for t in range(move+1,len(tape)):
            e=tape[t]
            op,r,*a=e
            if role not in (e[1:3] if op in {"ADD","COPY"} else e[1:2]):
                continue
            if private(e,role):
                assert e[-1]==chart and Q(e[-2])
                assert op!="ADD" or a[0]!=role
                writes.append([t,e])
                continue
            assert writes and writes[0][0]==row["first_clock"]
            yield dict(**row,writes=writes,barrier_clock=t,barrier=e)
            break
        else:
            raise AssertionError("lost terminal contact")


def main():
    assert __debug__
    p=quote()
    if sys.argv[1:]==["--price-only"]:
        print(dumps(p,indent=2,sort_keys=True))
        return
    assert not sys.argv[1:]
    deadline=monotonic()+27
    data=decompress(read("inputs/7334-WORD.json.gz"))
    assert sha256(data).hexdigest()=="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    word=loads(data,object_pairs_hook=unique)
    assert len(word["program"])==p["event_cap"]
    rows=list(cases(word,p))
    assert len(rows)==p["case_cap"]
    requests,refs=defaultdict(set),defaultdict(set)
    for row in rows:
        t,r,c=row["barrier_clock"],row["role"],row["chart_to"]
        op=row["barrier"][0]
        if op=="CLEAR":
            assert row["barrier"]==["CLEAR",r,c]
            row["disposition"]="no-observer clear survivor"
        elif op in {"ADD","MOVE"}:
            assert (op=="ADD" and row["barrier"][2]==r and row["barrier"][-1]==c or
                    op=="MOVE" and row["barrier"][1:3]==[r,c])
            requests[t].add((c,r))
            refs[t].add(r)
        else:
            row["disposition"]="first barrier outside scope"
    read("inputs/aggregate.py")
    read("inputs/donor_span.py")
    helper=run_path(str(ROOT/"inputs/donor_span.py"))
    algebra=run_path(str(ROOT/"inputs/aggregate.py"))
    controls=algebra["controls"](helper)
    banks,values=helper["snapshot"](word,requests,refs,deadline)
    for row in rows:
        if "disposition" in row:
            continue
        t,r,c=row["barrier_clock"],row["role"],row["chart_to"]
        key=t,c,r
        answer=None
        if key in banks and (t,r) in values and monotonic()<deadline:
            value=values[t,r]
            answer=algebra["exact_span"](value,banks[key],deadline,helper)
        if answer is None:
            row["disposition"]="capped"
        else:
            if "rank" in answer:
                answer["span_rank"]=answer.pop("rank")
            row.update(answer)
            row["disposition"]=row.pop("decision")
            row["bank_roles"]=sorted(banks[key])
            row["row"]={i:str(q) for i,q in value.items()}
    counts=Counter(r["disposition"] for r in rows)
    print(dumps(dict(head=p["head"],caller=p["caller"],pins=PINS,controls=controls,
        rows=rows,counts=counts,unvisited=[r["move_clock"] for r in rows if r["disposition"]=="capped"]),
        indent=2,sort_keys=True))
    if counts["capped"]:
        raise SystemExit(2)


if __name__=="__main__":
    main()
