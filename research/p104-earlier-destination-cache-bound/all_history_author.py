#!/usr/bin/env python3
"""Incremental modular history certificates with exact-Q zero-support replay.
A modular miss is lifted only with a generator-count rank upper bound.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from fractions import Fraction
from pathlib import Path
from math import isqrt
import gzip
import json

ROOT = Path(__file__).resolve().parent
PRIME = 1000003
PIN = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def add(row, other, q):
    for h, a in other.items():
        v = (row.get(h, 0)+q*a) % PRIME
        if v:
            row[h] = v
        else:
            row.pop(h, None)


def reduce(row, basis):
    row = row.copy()
    while row:
        p = min(row)
        if p not in basis:
            break
        add(row, basis[p], -row[p])
    return row


def insert(row, basis):
    v = reduce(row, basis)
    if v:
        p = min(v)
        q = pow(v[p], -1, PRIME)
        basis[p] = {h: q*a % PRIME for h, a in v.items()}


def certifies_miss(row, basis, generators):
    return bool(reduce(row,basis)) and len(basis)==generators


def frame_key(f):
    s = {0}
    for v in f:
        s |= {u ^ v for u in s}
    return tuple(sorted(s))


def run_mode(source, neutral_mode, neutral, exact_zero_events):
    need(all(PRIME % d for d in range(2, isqrt(PRIME)+1)), "prime modulus")
    raw = Path(source).read_bytes()
    need(sha256(raw).hexdigest() == PIN, "native source pin")
    w = json.loads(gzip.decompress(raw))
    queries = {i: dict(event=i, literal=e,
        rank=abs(len(w["frames"][e[2]])-len(w["frames"][e[3]])))
        for i,e in enumerate(w["program"]) if e[0]=="MOVE"}
    frames = list(map(frame_key, w["frames"]))
    banks = {f: {} for f in frames}
    generator_count = {f: 0 for f in banks}
    n = w["public"]
    zero_record_pin = None
    if not neutral_mode:
        neutral, exact_zero_events = set(), set()
    rows = [{h: 1} if h not in neutral else {} for h in range(n)]+[None]*w["owned_fields"]
    current = w["initial"].copy()+[None]*w["owned_fields"]
    for h, f in enumerate(w["initial"]):
        if frames[f] in banks:
            insert(rows[h], banks[frames[f]])
            generator_count[frames[f]] += bool(rows[h])
    scalars = {}
    done = []
    hits = []
    controls = 0
    complete = True
    for event, ins in enumerate(w["program"]):
        op, a = ins[:2]
        if op == "MOVE":
            old, new = ins[2:4]
            need(current[a] == old and rows[a] is not None, "MOVE source")
            if event in queries:
                bank = banks[frames[new]]
                if event in exact_zero_events:
                    need(not rows[a], "exact zero event reduces to zero")
                hit = not reduce(rows[a], bank)
                record = dict(event=event, literal=ins, rank=queries[event]["rank"],
                              history_rank_mod_prime=len(bank), hit_mod_prime=hit,
                              original_history_generator_count=generator_count[frames[new]],
                              rational_nonmembership_certified=certifies_miss(rows[a], bank, generator_count[frames[new]]),
                              zero_mod_prime=not rows[a])
                done.append(record)
                if hit:
                    hits.append(record)
            current[a] = new
            if frames[new] in banks:
                insert(rows[a], banks[frames[new]])
                generator_count[frames[new]] += event not in exact_zero_events
                if event in queries:
                    need(not reduce(rows[a], banks[frames[new]]), "inserted-arrival control")
                    controls += 1
        elif op == "INIT":
            need(a >= n and current[a] is None and rows[a] is None, "INIT")
            current[a], rows[a] = ins[2], {}
        elif op == "CLEAR":
            need(a >= n and current[a] == ins[2] and rows[a] is not None, "CLEAR")
            current[a], rows[a] = None, None
        else:
            value = ins[2] if op == "SCALE" else ins[3]
            if value not in scalars:
                q = Fraction(value)
                need(q.denominator % PRIME and q.numerator % PRIME, "valid nonzero scalar reduction")
                scalars[value] = q.numerator*pow(q.denominator, -1, PRIME) % PRIME
            q = scalars[value]
            if op == "SCALE":
                need(current[a] == ins[3], "SCALE chart")
                rows[a] = {h: q*x % PRIME for h, x in rows[a].items()}
            elif op in ("ADD", "COPY"):
                b = ins[2]
                need(a != b and current[a] == current[b] == ins[4], "ordinary chart")
                if op == "COPY":
                    need(a >= n and not rows[a], "COPY zero destination")
                add(rows[a], rows[b], q)
            else:
                raise ValueError("unknown instruction")
    if complete:
        need(current == w["final"]+[None]*w["owned_fields"], "complete final map")
        need(len(done) == len(queries), "all selected queries completed")
    need(complete and len(done)==6279, "all6279 original MOVE queries")
    expected = 6207 if neutral_mode else 6279
    need(sum(x["rational_nonmembership_certified"] for x in done)==expected,
         "full characteristic-zero nonmembership coverage")
    need(all(x["event"] in exact_zero_events for x in hits), "no nonzero history hit")
    need(sum(generator_count.values())==(7636 if neutral_mode else 7780),
         "exact final generator-count rank totals")
    # Rank-drop counterexample: a rational nonzero row may vanish modulo p.
    vanished_history = {h:v%PRIME for h,v in {0:PRIME}.items() if v%PRIME}
    rank_dropped_bank = {}; insert(vanished_history,rank_dropped_bank)
    need(reduce({0:1},rank_dropped_bank) and not certifies_miss({0:1},rank_dropped_bank,1),
         "modular history-rank drop must not be lifted to rational nonmembership")
    return dict(source_sha256=PIN,prime=PRIME,queries=6279,
        rational_nonmembership_certified=expected,exact_zero_MOVEs=len(exact_zero_events),
        final_total_history_rank=sum(generator_count.values()),
        strict_before_arrival_controls=controls,
        query_digest=sha256(json.dumps(done,sort_keys=True,separators=(",",":")).encode()).hexdigest())


def exact_neutral_data(source):
    raw=Path(source).read_bytes();need(sha256(raw).hexdigest()==PIN,"native exact-Q source pin")
    w=json.loads(gzip.decompress(raw));n=w['public'];main=set(w['live'])|{h+112 for h in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2']);helpers=set(range(n))-main
    need((len(main),len(helpers))==(400,1101),"exact main/helper partition")
    target={h:abs(len(w['frames'][w['final'][h]])-len(w['frames'][w['initial'][h]])) for h in helpers}
    rows=[{h:Fraction(1)} for h in range(n)]+[None]*w['owned_fields'];current=w['initial'].copy()+[None]*w['owned_fields']
    pure=defaultdict(list);supports={};coframes={};keys=list(map(frame_key,w['frames']))
    for event,e in enumerate(w['program']):
        op,a=e[:2]
        if op=='MOVE':
            need(current[a]==e[2] and rows[a],"exact MOVE source")
            r=abs(len(w['frames'][e[2]])-len(w['frames'][e[3]]));supports[event]=(set(rows[a]),r);coframes[event]=keys[e[3]]
            if len(rows[a])==1:
                h=next(iter(rows[a]))
                if h in helpers:pure[h].append((event,r))
            current[a]=e[3]
        elif op=='INIT':
            need(a>=n and current[a] is None and rows[a] is None,"exact INIT")
            current[a],rows[a]=e[2],{}
        elif op=='CLEAR':
            need(a>=n and current[a]==e[2] and rows[a] is not None,"exact CLEAR")
            current[a],rows[a]=None,None
        elif op=='SCALE':
            need(current[a]==e[3] and Fraction(e[2]),"exact SCALE frame")
            rows[a]={h:Fraction(e[2])*v for h,v in rows[a].items()}
        elif op in ('ADD','COPY'):
            b=e[2];need(a!=b and current[a]==current[b]==e[4],"exact scalar coframes")
            if op=='COPY':need(a>=n and not rows[a],"exact COPY")
            q=Fraction(e[3])
            for h,v in rows[b].items():
                value=rows[a].get(h,Fraction(0))+q*v
                if value:rows[a][h]=value
                else:rows[a].pop(h,None)
        else:raise ValueError('unknown exact source opcode')
    need(current==w['final']+[None]*w['owned_fields'],"exact final map")
    neutral={h for h in helpers if Counter(r for _,r in pure[h])==Counter({target[h]:1})}
    zeros={e:next(iter(support)) for e,(support,_) in supports.items() if support<=neutral}
    need(len(neutral)==len(zeros)==72 and all(len(supports[e][0])==1 for e in zeros),"exact72 singleton zero MOVEs")
    need(set(zeros.values())==neutral and all(supports[e][1]==target[h] for e,h in zeros.items()),"bijection and individual price cancellation")
    seen=defaultdict(set)
    for h in neutral:seen[keys[w['initial'][h]]].add(h)
    for e,h in zeros.items():
        need(h not in seen[coframes[e]],"zero units distinct within coframe")
        seen[coframes[e]].add(h)
    return neutral,set(zeros),Counter(target[h] for h in neutral)


def run(source=None):
    source=Path(source) if source is not None else ROOT/'inputs/WORD.json.gz'
    neutral,zeros,hist=exact_neutral_data(source)
    full=run_mode(source,False,neutral,zeros);projected=run_mode(source,True,neutral,zeros)
    # Maximal-zero testing alone is not sufficient: history x+y, target x,
    # neutral{x,y}. Setting only y=0 creates a nonzero cache.
    toy={};insert({0:1,1:1},toy);need(reduce({0:1},toy),"unrestricted toy miss")
    smaller={};insert({0:1},smaller);need(not reduce({0:1},smaller),"nonunit maximal-zero shortcut rejected")
    return dict(status='PASS_ALL_HISTORY_INCREMENTAL_RATIONAL_CERTIFICATE',
        unrestricted=full,maximal_neutral=projected,neutral_helpers=sorted(neutral),
        zero_MOVE_events=sorted(zeros),neutral_target_histogram=dict(sorted(hist.items())),
        neutral_paid_histogram=dict(sorted(hist.items())),zero_units_distinct_within_each_coframe=True,
        all_subsets='2^72 by written unit-extension lemma, not exhaustive enumeration',
        nonunit_all_subsets_shortcut_rejected=True,writes_files=False)


if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True))
