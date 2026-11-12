"""Whole-word forward exact-prime audit of both frozen rank-five cohorts."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
FROZEN = "preflight/FROZEN.json"
WORD = "inputs/7334-WORD.json.gz"
OLD = "inputs/OLD-WITNESS.json"
MODULAR = "independent/second_prime.py"
PURE = "independent/pure_support.py"
PINS = {
    FROZEN: "3861fa02acfafd35f3c437397f8aecd282a21687d81e426e25e2289f21d54a4a",
    WORD: "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    OLD: "5be60a09485041744919696121ae27e57a1aa9de437a2c4494d5fc569af4cdb4",
    MODULAR: "21dbd96192e1f60c00ceddba01a7e8d0ddd7d6ad7da4ad3ed22ef2e47cc589c4",
    PURE: "38c796cbe1a73f386177faf88cd53294d4b911f6cde7fd47cd9fcef3b558373f",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
GROUPS = {(712, 127): 1360, (714, 127): 1361}
EVENTS, CAP, SECONDS, PRIME = 76466, 14, 25, 65537


def unique(rows):
    value = dict(rows)
    if len(value) != len(rows):
        raise ValueError("duplicate metadata key")
    return value


def read(root, name):
    raw = (root/name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"changed dependency {name}")
    return raw


def stop(*_):
    raise TimeoutError("hard 25-second cap")


def deadline_check(deadline):
    if monotonic() >= deadline:
        raise TimeoutError("cooperative cap")


def cohort_cases(price):
    assert price["head"] == HEAD and price["caller"] == CALLER
    assert price["word_sha256"] == PINS[WORD] and price["case_count"] == CAP
    assert price["caps"]["initial_seconds"] == SECONDS
    assert price["max_distinct_compatible_edits"] == 2 and not price["paid_delta"]
    assert Q(price["complete_one_probe"][0]) > 0 > Q(price["complete_two_target"][1])
    assert {tuple(r["endpoints"]):r["pivot"] for r in price["cohorts"]} == GROUPS
    cases = {tuple(row["key"]):row for row in price["cases"]}
    assert len(cases) == CAP
    assert Counter(k[2:] for k in cases) == {g:7 for g in GROUPS}
    for k, row in cases.items():
        assert row["pivots"] == [GROUPS[k[2:]]] and row["owned"] == []
        assert row["productive_parent_rank"] == 5 and row["productive_child_ranks_sorted"] == [2,3]
    return cases


def forward(word, cases, mod, deadline, out, progress, denoms):
    n, owners, tape = (word[k] for k in ("public", "owned_fields", "program"))
    assert (n, owners, len(tape)) == (1501, 68, EVENTS)
    frames = word["frames"]

    @cache
    def span(chart):
        return mod["span"](frames[chart])

    requests = defaultdict(list)
    for k, row in cases.items():
        t, mid, low, high = k
        pivot, = row["pivots"]
        assert (word["initial"][pivot], word["final"][pivot]) == (low, high)
        assert span(low) < span(mid) < span(high)
        ordered = [len(frames[mid])-len(frames[low]), len(frames[high])-len(frames[mid])]
        assert sorted(ordered) == [2,3]
        requests[t].append((k, ordered))
    state = word["initial"] + [None]*owners
    rows = [{r:1} for r in range(n)] + [None]*owners
    fresh = set()
    for t in range(EVENTS+1):
        if t % 128 == 0:
            deadline_check(deadline)
        for k, ordered in requests.get(t, ()):
            _, mid, *_ = k
            frozen = cases[k]
            bank = [r for r in range(n) if state[r] == mid]
            owned = [r for r in range(n,n+owners) if state[r] == mid]
            assert bank == frozen["public"] and owned == frozen["owned"] == []
            pivot, = frozen["pivots"]
            assert pivot in bank
            cert = mod["classify"](bank, rows, {pivot})
            exterior = [{r:v for r,v in rows[b].items() if r != pivot} for b in bank]
            if not cert["kernel"]:
                assert cert["rank"] == len(bank)
                assert mod["verify_minor"](exterior, cert["minor_axes"]) == cert["determinant"] != 0
            out[k] = dict(key=k, public=bank, owned=owned, pivot=pivot,
                ordered_child_ranks=ordered, exterior_rows=exterior, prefix_minor=cert,
                disposition="modular prefix drop" if cert["kernel"] else "exact full prefix rank")
        if t == EVENTS:
            assert state == word["final"] + [None]*owners and not fresh
            break
        op, _, *args = tape[t]
        if op == "MOVE":
            old, new, owner = args
            assert span(old) < span(new) or owner and span(new) < span(old)
        mod["apply"](tape[t], state, rows, fresh, n, denoms, False)
        progress["events"] = t+1


@cache
def scalar(raw):
    return Q(raw)


def put(vector, role, value):
    if value:
        vector[role] = value
    else:
        vector.pop(role, None)


def impulse(tape, cut, role, before, deadline):
    """Exact one-axis row before cut or column after cut."""
    v = {role:Q(1)}
    times = range(cut-1,-1,-1) if before else range(cut,len(tape))
    for t in times:
        if t % 128 == 0:
            deadline_check(deadline)
        op, dest, *a = tape[t]
        if op == "MOVE":
            continue
        if op in ("INIT", "CLEAR"):
            v.pop(dest, None)
            continue
        if op == "SCALE":
            if dest in v:
                put(v,dest,v[dest]*scalar(a[0]))
            continue
        assert op in ("ADD","COPY")
        source, q, _ = a
        if before:
            current = v.get(dest,0)
            if op == "COPY":
                v.pop(dest,None)
            if current:
                put(v,source,v.get(source,0)+scalar(q)*current)
        else:
            current = scalar(q)*v.get(source,0)
            if op == "ADD":
                current += v.get(dest,0)
            put(v,dest,current)
    return v


def pair_kind(local, endpoint):
    entries = [(x,y) for lr,er in zip(local,endpoint,strict=True) for x,y in zip(lr,er,strict=True)]
    nonzero = next(((x,y) for x,y in entries if y), None)
    if nonzero is None:
        return "zero endpoint pairing", None
    u,v = nonzero
    mu = u/v
    if all(x == mu*y for x,y in entries):
        return ("relaxed rational pairing" if mu == 1 else "unequal proportional pairing"), mu
    return "relaxed rational pairing", None


def exact_on_drop(word, row, pure, deadline):
    t = row["key"][0]
    p, bank = row["pivot"], row["public"]
    tape = word["program"]
    fp = {r:impulse(tape,t,r,True,deadline) for r in bank}
    _, f = pure["pure_kernel"](fp,{p},deadline)
    row["exact_prefix_dimension"] = len(f)
    if not any(c for _,c in f):
        row["disposition"] = "no nonzero exact prefix"
        return
    n = word["public"]
    sp = {r:{i:v for i,v in impulse(tape,t,r,False,deadline).items() if i<n} for r in bank}
    _, s = pure["pure_kernel"](sp,{p},deadline)
    row["exact_suffix_dimension"] = len(s)
    local = [[pure["dot"](a,b) for b,_ in s] for a,_ in f]
    boundary = [[c.get(p,0)*d.get(p,0) for _,d in s] for _,c in f]
    disposition, ratio = pair_kind(local,boundary)
    row.update(disposition=disposition, exact_local=[[str(x) for x in y] for y in local],
               exact_endpoint=[[str(x) for x in y] for y in boundary],
               proportionality=str(ratio) if ratio is not None else None)


def controls(mod, pure, old):
    tests = mod["controls"]()
    maps = {k:{int(j):Q(v) for j,v in old[k].items()} for k in "abcd"}
    d = pure["dot"]
    assert d(maps["a"],maps["b"]) == d(maps["c"],maps["d"]) == 1
    assert pair_kind([[Q(1)]],[[Q(1)]]) == ("relaxed rational pairing",1)
    assert pair_kind([[Q(2)]],[[Q(1)]]) == ("unequal proportional pairing",2)
    assert pair_kind([[Q(0),Q(1)]],[[Q(1),Q(0)]]) == ("relaxed rational pairing",None)
    tape = [("ADD",1,0,"-3/2",0),("SCALE",0,"2",0)]
    assert impulse(tape,2,1,True,float("inf")) == {0:Q(-3,2),1:Q(1)}
    assert impulse(tape,0,0,False,float("inf")) == {0:Q(2),1:Q(-3,2)}
    return tests + ["historical exact unit pair","singleton unequal proportional exclusion",
                    "singleton nonproportional positive","exact direct prefix and suffix impulses"]


def main():
    ap = ArgumentParser()
    ap.add_argument("--root",type=Path,default=ROOT)
    ap.add_argument("--controls-only",action="store_true")
    args = ap.parse_args()
    assert __debug__
    root = args.root
    read(root,MODULAR)
    read(root,PURE)
    mod, pure = (run_path(str(root/rel)) for rel in (MODULAR,PURE))
    assert mod["PRIME"] == PRIME
    price = loads(read(root,FROZEN),object_pairs_hook=unique)
    cases = cohort_cases(price)
    tests = controls(mod,pure,loads(read(root,OLD),object_pairs_hook=unique))
    if args.controls_only:
        print(dumps(dict(controls=tests,keys=list(cases)),indent=2,sort_keys=True))
        return 0
    progress = {"events":0}
    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline = monotonic()+23
    out, denoms, reason = {}, set(), None
    try:
        payload = decompress(read(root,WORD))
        assert sha256(payload).hexdigest() == PAYLOAD
        word = loads(payload,object_pairs_hook=unique)
        forward(word,cases,mod,deadline,out,progress,denoms)
        for row in out.values():
            if row["disposition"] == "modular prefix drop":
                exact_on_drop(word,row,pure,deadline)
    except (TimeoutError,pure["Capped"]) as error:
        reason = str(error) or "exact support cap"
    finally:
        alarm(0)
    pending = [k for k in cases if k not in out or out[k]["disposition"] in
               ("modular prefix drop","relaxed rational pairing")]
    print(dumps(dict(head=HEAD,caller=CALLER,prime=PRIME,pins=PINS,
        controls=tests,case_cap=CAP,runner_cap_seconds=SECONDS,progress=progress,timeout=reason,
        denominator_units=sorted(denoms),counts=Counter(x["disposition"] for x in out.values()),
        rows=list(out.values()),unresolved=pending),sort_keys=True,indent=2))
    return 124 if reason else 0


if __name__ == "__main__":
    raise SystemExit(main())
