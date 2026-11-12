"""Directly replay every maximal fixed-anchor interval of the 17 signed J calls."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/PRICE.json": "1ad9852ecff0b3780770cbf4e500731e65214a9c438f8b1ed2c0cbe484d9b36b",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
LOWER = Q("0.00364665195644044790699554028334161")
BIT_CAP = Q("0.00376669")
N = 36


def unique(pairs):
    d = dict(pairs)
    assert len(d) == len(pairs)
    return d


def checked(name):
    data = (ROOT / name).read_bytes()
    assert sha256(data).hexdigest() == PINS[name], name
    return data


def add(row, source, amount):
    for j,v in source.items():
        value = row.get(j, 0) + amount*v
        if value:
            row[j] = value
        else:
            row.pop(j,None)


def propagate(matrix, e, q):
    if e[0] == "J":
        x,y,u,v = e[2]
        add(matrix[y], matrix[x], q)
        add(matrix[u], matrix[v], -q)
        return
    assert e[0] == "A"
    op,dst = e[1:3]
    if op == "ADD":
        add(matrix[dst], matrix[e[3]], Q(e[4]))
    elif op == "QUERY":
        add(matrix[dst], matrix[e[3]], Q(q)**e[4])
    elif op == "SCALE":
        amount = Q(e[3])
        assert amount
        matrix[dst] = {j: amount*v for j,v in matrix[dst].items()}
    elif op == "SWAP":
        src = e[3]
        matrix[dst],matrix[src] = matrix[src],matrix[dst]
    else:
        assert op in ("IDLE_ONE","LAMBDA")


def pivots(rows):
    basis = {}
    witnesses = []
    for i,row in enumerate(rows):
        work = row.copy()
        while work:
            j = min(work)
            if j not in basis:
                basis[j] = work
                witnesses.append((i,j,work[j]))
                break
            add(work, basis[j], -work[j]/basis[j][j])
    return witnesses


def stop(*_):
    raise TimeoutError("60-second exact window cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(60)
    caller = loads(checked("inputs/CALLER.json"),object_pairs_hook=unique)
    preflight = loads(checked("inputs/PRICE.json"),object_pairs_hook=unique)
    checked("inputs/pricing.py")
    engine = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    events = caller["events"]
    clocks = [t for t,e in enumerate(events) if e[0]=="J"]
    assert len(events)==4783 and len(clocks)==17 and clocks[:3]==preflight["clocks"]==[43,137,268]
    assert [events[t][1] for t in clocks]==list(range(1,18))
    assert caller["types"]["A"]["roles"] == N and len(caller["types"]["A"]["ports"])==96
    assert len(caller["types"]["B"]["ports"])==8
    ends = [t-1 for t in clocks[1:]] + [len(events)-1]
    total = [(i,j) for i in range(17) for j in range(i,17)]
    terms = Counter({int(r): n for r,n in preflight["per_J_old_P"].items()})
    terms.subtract({int(r): n for r,n in preflight["per_J_old_helper_T"].items()})
    terms.subtract({1:16,8:400})
    crossing = Q(preflight["exact_crossing_upper"])
    exact = engine(terms,crossing)
    pos = {r:n for r,n in terms.items() if n>0}
    neg = {r:n for r,n in terms.items() if n<0}
    uniform_upper = engine(pos,LOWER)[1] + engine(neg,BIT_CAP)[1]
    uniform_lower = engine(pos,BIT_CAP)[0] + engine(neg,LOWER)[0]
    assert uniform_lower < exact[0] <= exact[1] < uniform_upper < 149
    assert len(pivots([{0:Q(1),1:Q(2)},{0:Q(2),1:Q(4)}]))==1
    cases = []
    capped = False
    try:
        for first in range(17):
            start = 0 if first==0 else clocks[first-1]+1
            forward = {q:[{i:Q(1)} for i in range(N)] for q in (1,-1)}
            retained = 0
            last = first
            for t in range(start,len(events)):
                e = events[t]
                if e[0] in ("J","A"):
                    for q,mat in forward.items():
                        propagate(mat,e,q)
                    retained += e[:2]==["A","QUERY"]
                if t != ends[last]:
                    continue
                rows = [row.copy() for row in forward[1]]
                for row,minus in zip(rows,forward[-1],strict=True):
                    add(row,minus,-1)
                proof = pivots(rows)
                rank = len(proof)
                required = max(0,rank-retained)
                stages = last-first+1
                gross = [stages*value-96*required for value in exact]
                cases.append({"first_last":[first+1,last+1],"clocks":[start,t],
                              "required_phase_rank":rank,"retained_queries_per_port":retained,
                              "new_queries_lower_per_port":required,"rank_pivots":proof,
                              "incumbent_gross_interval":gross,
                              "uniform_gross_upper":stages*uniform_upper-96*required})
                if last==16:
                    break
                last+=1
    except TimeoutError:
        capped=True
    finally:
        alarm(0)
    assert [(r["first_last"][0]-1,r["first_last"][1]-1) for r in cases]==total[:len(cases)]
    assert capped or len(cases)==153
    print(dumps({"pins":PINS,"unit_bodies":True,"signs":[1,-1],"stage_clocks":clocks,
                 "rows_per_matrix":N,"windows_total":153,"windows_checked":len(cases),"capped":capped,
                 "unresolved_keys":[[i+1,j+1] for i,j in total[len(cases):]],
                 "per_stage_gross_interval_at_crossing_upper":exact,
                 "per_stage_uniform_lower_upper":[uniform_lower,uniform_upper],
                 "uniform_kappa_interval":[LOWER,BIT_CAP],"cap_seconds":60,"cases":cases},
                default=str,sort_keys=True,indent=2))
    if capped:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
