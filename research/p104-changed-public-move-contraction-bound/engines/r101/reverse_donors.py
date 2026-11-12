"""Verify the twelve R101 endpoint donor banks using exact reverse covectors."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS = {
    "inputs/PRICE.json": "ac5ecb17f0e9f3c068423998b350a78c1a4769b6f61b50838be5f3e0d0b1a00c",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "reused/reverse_span.py": "f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff",
}
PRIMARY = "b7700e618ce3c69cbe7544842f265e980f87903dea30121df118861d104b2c51"
CASE_CAP = 12
SECONDS = 20
EVENTS = 76466


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return obj


def checked(path, pin):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != pin:
        raise ValueError(f"Changed input {path.name}")
    return raw


def touches(role, event):
    return role == event[1] or event[0] in ("ADD", "COPY") and role == event[2]


def ring_ok(q):
    d = q.denominator
    for p in (2, 3, 5):
        while d % p == 0:
            d //= p
    return d == 1 and abs(q)+1 < 2**16


def requests_for(word, price):
    n = word["public"]
    tape = word["program"]
    frames = word["frames"]

    @cache
    def span(label):
        values = {0}
        for v in frames[label]:
            assert type(v) is int and 0 < v < 512 and v not in values
            values |= {v ^ u for u in values}
        return values

    specs = []
    for row in price["candidates"]:
        l, r, mover = row["key"]
        a, b, c = row["charts"]
        clock, event = row["add"]
        source = event[2]
        assert b != 207 and 0 <= mover < n and l < clock < r
        assert tape[l] == ["MOVE", mover, a, b, False]
        assert tape[r] == ["MOVE", mover, b, c, False]
        assert tape[clock] == event and event == ["ADD", mover, source, event[3], b]
        assert source != mover and Fraction(event[3])
        assert [t for t in range(l+1,r) if touches(mover, tape[t])] == [clock]
        assert span(a) < span(b) < span(c)
        for side, chart in (("entrance", a), ("exit", c)):
            specs.append(dict(key=row["key"]+[side], clock=clock, mover=mover, original_chart=b,
                              chart=chart, source=source, source_multiplier=event[3]))
    assert len(specs) == len({tuple(row["key"]) for row in specs}) == CASE_CAP
    return specs


def collect(word, specs, engine, deadline, progress):
    tape = word["program"]
    n, owned = word["public"], word["owned_fields"]
    assert (len(tape), n, owned) == (EVENTS,1501,68)
    requests = defaultdict(list)
    for row in specs:
        requests[row["clock"]].append(row)
    active = word["final"] + [None] * owned
    fresh_copy_dest = set()
    bank_at = {}
    for clock in range(EVENTS - 1, -1, -1):
        progress["last_unvisited_event"] = clock
        if clock % 128 == 0 and monotonic() >= deadline:
            raise TimeoutError("reverse chart walk")
        op, d, *args = tape[clock]
        assert 0 <= d < len(active) and (d not in fresh_copy_dest or op == "INIT")
        if op == "MOVE":
            a,b,is_owned = args
            assert active[d] == b and is_owned == (d >= n)
            active[d] = a
        elif op == "INIT":
            assert d >= n and active[d] == args[0]
            active[d] = None
            fresh_copy_dest.discard(d)
        elif op == "CLEAR":
            assert d >= n and active[d] is None
            active[d] = args[0]
        else:
            assert op in ("ADD", "COPY", "SCALE") and active[d] == args[-1]
            engine["coefficient"](args[-2])
            if op in ("ADD", "COPY"):
                src = args[0]
                assert src != d and active[src] == args[-1]
            if op == "COPY":
                assert d >= n
                fresh_copy_dest.add(d)
        for row in requests.get(clock, ()):
            assert active[row["mover"]] == active[row["source"]] == row["original_chart"]
            bank = [role for role, label in enumerate(active) if label == row["chart"] and role != row["mover"]]
            bank_at[tuple(row["key"])] = ([r for r in bank if r < n], [r for r in bank if r >= n])
        progress["events_checked"] += 1
    assert active == word["initial"] + [None] * owned and not fresh_copy_dest
    progress["last_unvisited_event"] = None
    assert len(bank_at) == CASE_CAP
    return bank_at


def evaluate(word, specs, banks, engine, deadline, rows_out, results):
    requests = defaultdict(list)
    ids = {}

    def demand(clock, role):
        key = clock, role
        if key not in ids:
            ids[key] = len(ids)
            requests[clock].append((role,ids[key]))
        return ids[key]

    setups = []
    for row in specs:
        clock = row["clock"]
        public, owned = banks[tuple(row["key"])]
        target_id = demand(clock, row["source"])
        donors = [(r,demand(clock,r)) for r in public]
        setups.append((target_id, donors, owned))
    rows = engine["transpose_prefix"](word, requests, len(ids), deadline)
    rows_out.extend(rows)
    for row,(target_id,donors,owned) in zip(specs,setups,strict=True):
        if monotonic() >= deadline:
            raise TimeoutError("exact span gate")
        target = rows[target_id]
        bank = [(r,rows[i]) for r,i in donors]
        proof = engine["exact_span"](bank,target)
        status, replacement = "outside donor span", None
        if proof["status"] == "exact_span":
            replacement = {r: Fraction(row["source_multiplier"])*Fraction(v) for r,v in proof["coefficients"].items()}
            status = "exact legal coefficients" if all(map(ring_ok,replacement.values())) else "coefficient gate unresolved"
            replacement = {r:str(v) for r,v in replacement.items()}
        elif proof["status"] == "absent_exterior_coordinate":
            j = proof["coordinate"]
            assert all(j not in vector for _, (vector,_) in bank)
            proof["separating_covector"] = {j:"1"}
            proof["separated_target"] = proof["target_coefficient"]
        results.append(dict(key=row["key"],chart=row["chart"],source=[row["clock"],row["source"]],
            source_nnz=len(target[0]),bank_roles=[r for r,_ in bank],owned_donors_excluded=owned,
            target_row_id=target_id,donor_role_row_ids=donors,status=status,replacement_coefficients=replacement,
            proof=proof))


def audit(root,engine):
    price = loads(checked(root / "inputs/PRICE.json",PINS["inputs/PRICE.json"]),object_pairs_hook=unique)
    assert price["head"] == HEAD and price["caller_head"] == CALLER
    assert price["word_sha256"] == PINS["inputs/7334-WORD.json.gz"] and price["payload_sha256"] == PAYLOAD
    assert price["limits"]["cases"] == CASE_CAP and price["limits"]["runner_seconds"] == SECONDS
    tests = engine["controls"]()
    assert ring_ok(Fraction(-3,5)) and not ring_ok(Fraction(1,7))
    tests += ["bounded signed coefficient ring"]
    keys = [p["key"]+[side] for p in price["candidates"] for side in ("entrance","exit")]
    assert len(keys) == len({tuple(k) for k in keys}) == CASE_CAP
    results, rows = [], []
    progress = dict(events_checked=0,last_unvisited_event=EVENTS-1)
    reason = None

    def stop(*_):
        raise TimeoutError("Hard 20-second cap")

    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline = monotonic()+SECONDS-2
    try:
        raw = decompress(checked(root / "inputs/7334-WORD.json.gz",PINS["inputs/7334-WORD.json.gz"]))
        assert sha256(raw).hexdigest() == PAYLOAD
        word = loads(raw,object_pairs_hook=unique)
        specs = requests_for(word,price)
        assert [r["key"] for r in specs] == keys
        banks = collect(word,specs,engine,deadline,progress)
        evaluate(word,specs,banks,engine,deadline,rows,results)
    except TimeoutError as error:
        reason = str(error)
    finally:
        alarm(0)
    return dict(head=HEAD,caller_head=CALLER,pins=PINS,cases_cap=CASE_CAP,runner_seconds_cap=SECONDS,
        controls=tests,timeout=reason,progress=progress,unvisited=keys[len(results):],
        results=results,exact_integer_rows=rows,
        counts=dict(Counter(r["status"] for r in results)))


def compare(path, result):
    primary = loads(checked(path,PRIMARY),object_pairs_hook=unique)
    assert primary["head"] == result["head"]
    assert primary["pins"]["lead/PRICE.json"] == PINS["inputs/PRICE.json"]
    assert primary["pins"]["inputs/7334-WORD.json.gz"] == PINS["inputs/7334-WORD.json.gz"]
    assert primary["timeout"] is result["timeout"] is None and not primary["unvisited"] and not result["unvisited"]
    assert primary["counts"] == result["counts"] == {"outside donor span": CASE_CAP}
    cases = []
    for a,b in zip(primary["results"],result["results"],strict=True):
        fields = ("key","chart","source","source_nnz","bank_roles","owned_donors_excluded","status",
                  "replacement_coefficients")
        assert all(a[k] == b[k] for k in fields)
        assert a["rank"] == b["proof"]["donor_rank"]
        cases.append(dict(key=b["key"],donor_count=len(b["bank_roles"]),donor_rank=a["rank"],
            exact_rank_obstruction=b["proof"]["status"],source=b["source"],chart=b["chart"],
            owned_donors_excluded=b["owned_donors_excluded"]))
    return dict(head=HEAD,primary_sha256=PRIMARY,bank_status_agreement=CASE_CAP,
        rank_agreement=CASE_CAP,cases=cases,counts=result["counts"])


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--primary",type=Path)
    parser.add_argument("--controls-only",action="store_true")
    args=parser.parse_args()
    source="reused/reverse_span.py"
    checked(ROOT/source,PINS[source])
    engine=run_path(str(ROOT/source))
    if args.controls_only:
        print(dumps(engine["controls"]()))
        return
    result=audit(args.root,engine)
    print(dumps(compare(args.primary,result) if args.primary else result,indent=2,sort_keys=True))
    if result["timeout"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
