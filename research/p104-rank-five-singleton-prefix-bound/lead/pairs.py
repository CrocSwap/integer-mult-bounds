"""Check exact paired support on the two singleton rank-five cohorts."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "preflight/FROZEN.json": "3861fa02acfafd35f3c437397f8aecd282a21687d81e426e25e2289f21d54a4a",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/OLD-WITNESS.json": "5be60a09485041744919696121ae27e57a1aa9de437a2c4494d5fc569af4cdb4",
    "inputs/bank_trace.py": "681fda5cc1d4b1ac07c62601ceb052f167a51fb73d28b23f454f8f50f6a8e27b",
    "inputs/paired_rank.py": "d1b7c34e6f8c8a7b810414762015e6e300a8292422af66ff671ae09741141f09",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError("duplicate JSON key")
    return out


def checked(path):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def span(frame):
    values = {0}
    for a in frame:
        assert a not in values
        values.update(v ^ a for v in tuple(values))
    return values


def topology(word, cases):
    n = word["public"]
    frames = word["frames"]
    state = word["initial"][:] + [None] * word["owned_fields"]
    by_cut = {row["key"][0]: row for row in cases}
    assert len(by_cut) == len(cases)
    ranks, copies = {}, []
    for t, (op, r, *a) in enumerate(word["program"]):
        if t in by_cut:
            row = by_cut[t]
            _, mid, lo, hi = row["key"]
            pivot, = row["pivots"]
            assert [j for j in range(n) if (word["initial"][j],word["final"][j]) == (lo,hi)] == [pivot]
            assert [j for j,c in enumerate(state) if c == mid] == row["public"] and not row["owned"]
            assert max(row["public"]) < n and pivot in row["public"]
            assert span(frames[lo]) < span(frames[mid]) < span(frames[hi])
            a0,a1,a2 = map(lambda c:len(frames[c]), (lo,mid,hi))
            ranks[t] = [a1-a0,a2-a1]
            assert sorted(ranks[t]) == row["productive_child_ranks_sorted"]
        before = state[r]
        if op == "MOVE":
            assert a[0] == before and a[2] == (r >= n)
            state[r] = a[1]
        elif op == "INIT":
            assert before is None and r >= n
            state[r] = a[0]
        elif op == "CLEAR":
            assert before == a[0] and r >= n
            state[r] = None
        else:
            assert op in {"ADD","COPY","SCALE"} and before == a[-1]
            if op != "SCALE":
                assert r != a[0] and state[a[0]] == before
            if op == "COPY":
                copies.append(t)
    assert state == word["final"] + [None] * word["owned_fields"]
    assert set(ranks) == set(by_cut) and all(t < min(by_cut) for t in copies)
    return ranks, copies


def pair(left, right, pivot, dot, engine):
    local = [[dot(a,b) for b,_ in right] for a,_ in left]
    end = [[c.get(pivot,0)*d.get(pivot,0) for _,d in right] for _,c in left]
    first = next(((i,j) for i,row in enumerate(end) for j,v in enumerate(row) if v), None)
    if first is None:
        return local,end,"absent pure suffix direction",None
    i,j = first
    q = local[i][j] / end[i][j]
    proportional = all(v == q*x for a,b in zip(local,end,strict=True) for v,x in zip(a,b,strict=True))
    possible = not proportional or q == 1
    defect = [[a-b for a,b in zip(x,y,strict=True)] for x,y in zip(local,end,strict=True)]
    wedge, dr, sr = engine(local,defect)
    assert possible == (wedge or dr != sr)
    return local,end,"unit pairing survivor" if possible else "no unit pairing",str(q) if proportional else None


def main():
    assert __debug__
    data = {path:checked(path) for path in PINS}
    frozen = loads(data["preflight/FROZEN.json"],object_pairs_hook=unique)
    old = loads(data["inputs/OLD-WITNESS.json"],object_pairs_hook=unique)
    assert not frozen["literal_decode"] and frozen["case_count"] == len(frozen["cases"]) == 14
    assert Q(frozen["complete_one_probe"][0])>0 and Q(frozen["complete_two_target"][1])<0
    helper = run_path(str(ROOT/"inputs/bank_trace.py"))
    engine = run_path(str(ROOT/"inputs/paired_rank.py"))["pairing"]
    dot = helper["dot"]
    controls = helper["controls"](old)
    toy = [({1:Q(1)},{0:Q(1)})]
    assert pair(toy,toy,0,dot,engine)[2] == "unit pairing survivor"
    assert pair(toy,[({2:Q(1)},{0:Q(1)})],0,dot,engine)[2] == "no unit pairing"
    raw = decompress(data["inputs/7334-WORD.json.gz"])
    assert sha256(raw).hexdigest()==PAYLOAD
    word = loads(raw,object_pairs_hook=unique)
    assert len(word["program"])==76466
    deadline = monotonic()+23
    ranks,copies = topology(word,frozen["cases"])
    rows = []
    for case in frozen["cases"]:
        if monotonic()>=deadline:
            break
        cut,chart,*_ = case["key"]
        pivot, = case["pivots"]
        bank = case["public"]
        try:
            fp,left = helper["kernel"](helper["trace"](word,cut,bank,deadline,True),{pivot})
            sp,right,local,end,q = None,[],[],[],None
            decision = "absent pure prefix direction"
            if any(c for _,c in left):
                sp,right = helper["kernel"](helper["trace"](word,cut,bank,deadline,False),{pivot})
                local,end,decision,q = pair(left,right,pivot,dot,engine)
        except TimeoutError:
            break
        def matrix(m):
            return [[str(v) for v in r] for r in m]
        def basis(value):
            return [[helper["printed"](a),helper["printed"](c)] for a,c in value]
        rows.append(dict(key=case["key"],pivot=pivot,bank=bank,child_ranks=ranks[cut],
            prefix_exterior_rank=fp,suffix_exterior_rank=sp,pure_prefix=basis(left),pure_suffix=basis(right),
            local=matrix(local),endpoint=matrix(end),proportional_ratio=q,disposition=decision))
    pending = [x["key"] for x in frozen["cases"][len(rows):]]
    print(dumps(dict(head=frozen["head"],caller=frozen["caller"],pins=PINS,controls=controls,
        old_copy_clocks=copies,case_cap=14,runner_seconds_cap=25,tested=rows,unvisited=pending,
        survivors=[x["key"] for x in rows if x["disposition"]=="unit pairing survivor"]),
        indent=2,sort_keys=True))
    if pending:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
