#!/usr/bin/env python3
"""Candidate-bound chart catalogue and two-modulus physical replay."""

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from fractions import Fraction
from functools import cache
import gzip
import hashlib
import json
from pathlib import Path
from time import monotonic
from types import ModuleType

from physical import evaluate, raw_ports


ROLE = 379
FIRST, STOP, LAST = 748, 1065, 1072
REPLACED_PAIRS = {(FIRST, STOP), (STOP, LAST), (FIRST, LAST)}
SOURCE = {
    7636: {
        "head": "7e68d8dd62d9a38c0f3c942262a7a85ca7125b75",
        "gzip": "1b4e33c3e3b69d1f1b42d019a2e372ac612fa28494bd8da18a734618f9bda659",
        "raw": "98b8c12ece2f323a6ff5cac8c7ed2f78ba3835438ea56b16bd7d4698ec5ad5b2",
        "clocks": (131142, 131294),
        "events": 202668,
        "clear": 180,
        "engine": "72dfc0f5435cea2630a0d4e8f466fbb7b866404a22804769c3e690845ca72d2b",
    },
    7658: {
        "head": "0a0e71c34a5ee5a1b59a8fe7bc6abd35a4d3dd82",
        "gzip": "dde0a987c2dd9e221208ca5043dfd6e2bdfbb8c4289fa20e2b93fae1696b3ea9",
        "raw": "fa84fcdecb534700cd00dc81b74889f549a653daa2fb3658cb8142e1eeb9b9e6",
        "clocks": (98054, 98204),
        "events": 150010,
        "clear": 234,
        "engine": "334e37a3fb31c8cd374bc4ecafcdb9fb2597eb3192d3d49373417830458cb696",
    },
}
OLD = {
    "word": "f9f9a485712c0c94c9d14370e2a8436414e1b53bdf86550d9d6436835e9e06cb",
    "gzip": "676c20c53ebd40120903af86bf17c2116f654ab8ce4aa1833f388a2fc400b511",
    "engine": "6ca9ec1b134f448fbed59158520c4225679500d5ceafb0410ef790e848fec4bc",
    "receipt": "a0bb80f9220fd6414d45e208af1e5571f51e6ac9f333d412dce19ef82854f541",
    "ascending": 2957,
    "directed": 2979,
    "moves": 6171,
}
MODULI = ((1000000009, 11), (998244353, 37))


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def pinned(path, expected):
    require(path.is_file() and not path.is_symlink(), f"missing or symlink input {path.name}")
    data = path.read_bytes()
    require(sha(data) == expected, f"byte pin {path.name}")
    return data


def word(path, packed_sha, raw_sha=None):
    raw = gzip.decompress(pinned(path, packed_sha))
    require(raw_sha is None or sha(raw) == raw_sha, f"word pin {path.name}")
    obj = json.loads(raw)
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return obj, {"gzip_sha256": packed_sha, "raw_sha256": sha(raw), "canonical_sha256": sha(canonical)}


def read_engine(path, expected):
    data = pinned(path, expected).decode()
    start, end = "NB = 9\n", "# Package-specific checks."
    require(data.count(start) == data.count(end) == 1, "phase engine extraction anchors")
    section = data.split(start, 1)[1].split(end, 1)[0]
    return start + "\n".join(line for line in section.splitlines()
                             if line.strip() and not line.lstrip().startswith("#")) + "\n"


def engine_from(code):
    module = ModuleType("pinned_phase_engine")
    module.require = require
    exec(compile(code, "<pinned-phase-engine>", "exec"), module.__dict__)
    return module


def dump(path, value):
    with path.open("x") as out:
        json.dump(value, out, sort_keys=True, indent=2)
        out.write("\n")


def mentions(event, role):
    return event[1] == role or (event[0] in ("ADD", "COPY") and event[2] == role)


def require_cut(source, candidate, clocks):
    i, j = clocks
    require(source.keys() == candidate.keys()
            and all(candidate[k] == v for k, v in source.items() if k != "program"),
            "header changed")
    old = source["program"]
    direct = ["MOVE", ROLE, FIRST, LAST, False]
    require(old[i] == ["MOVE", ROLE, FIRST, STOP, False]
            and old[j] == ["MOVE", ROLE, STOP, LAST, False], "source cut")
    require(not any(mentions(e, ROLE) for e in old[i + 1:j]), "non-idle source stop")
    require(candidate["program"] == old[:i] + old[i + 1:j] + [direct] + old[j + 1:],
            "candidate contains changes beyond the strict direct route")


def span(vectors):
    elements = {0}
    for v in vectors:
        require(type(v) is int and 0 < v < 512 and v not in elements, "invalid chart basis")
        elements |= {x ^ v for x in elements}
    return frozenset(elements)


def groups_for(program, frames):
    groups = defaultdict(list)
    for i, e in enumerate(program):
        if e[0] == "MOVE":
            _, r, a, b, flag = e
            require(len(frames[a]) != len(frames[b]), "equal-rank MOVE")
            key = (a, b) if len(frames[a]) < len(frames[b]) else (b, a)
            groups[key].append([i, r, a, b, flag])
    return dict(groups)


@cache
def scalar(value):
    require(type(value) is str, "literal scalar text")
    q = Fraction(value)
    require(q != 0, "zero literal scalar")
    return q


def schedule(w, count, clears, birth):
    p, n, k = w["program"], w["public"], w["owned_fields"]
    require(len(p) == count and n == 1501 and k == 68, "word/event denominator")
    require(len(w["initial"]) == len(w["final"]) == n
            and w["initial"][457] == birth, "initial or final frame boundary")
    spans = tuple(map(span, w["frames"]))
    available = range(len(spans))
    require(all(type(f) is int and f in available for f in w["initial"] + w["final"]),
            "out-of-range boundary frame")
    charts = w["initial"][:] + [None] * k
    starts, lives, peak = {}, [], 0
    counts, paid, owned_paid = Counter(), Counter(), Counter()
    for i, e in enumerate(p):
        op, r, *rest = e
        require(type(r) is int and 0 <= r < n + k, f"field index at {i}")
        counts[op] += 1
        if op == "MOVE":
            a, b, own = rest
            require(type(own) is bool and own == (r >= n), f"MOVE flag at {i}")
            require(type(a) is type(b) is int and a in available and b in available
                    and charts[r] == a, f"MOVE source at {i}")
            require(spans[a] < spans[b] or (own and spans[b] < spans[a]),
                    f"MOVE inclusion at {i}")
            charts[r] = b
            rank = abs(len(w["frames"][b]) - len(w["frames"][a]))
            paid[rank] += 1
            if own:
                require(r in starts, f"live owned MOVE at {i}")
                owned_paid[rank] += 1
        elif op in ("INIT", "CLEAR"):
            f, = rest
            require(r >= n and type(f) is int and f in available, f"owned frame at {i}")
            if op == "INIT":
                require(charts[r] is None and r not in starts, f"fresh owned birth at {i}")
                charts[r] = f
                starts[r] = f
                peak = max(peak, len(starts))
            else:
                require(charts[r] == f and r in starts, f"live owned CLEAR at {i}")
                lives.append([r, starts.pop(r), f])
                charts[r] = None
        elif op == "SCALE":
            value, f = rest
            require(type(f) is int and charts[r] == f, f"SCALE frame at {i}")
            scalar(value)
        elif op in ("ADD", "COPY"):
            s, value, f = rest
            require(type(s) is int and 0 <= s < n + k and r != s and type(f) is int
                    and charts[r] == charts[s] == f, f"{op} frame at {i}")
            require(op != "COPY" or r >= n, f"private COPY at {i}")
            scalar(value)
        else:
            raise ValueError(f"unknown event {op} at {i}")
    require(charts == w["final"] + [None] * k and not starts, "end charts or live owned state")
    require(counts["INIT"] == counts["CLEAR"] == len(lives) == clears and peak == 50,
            "owned lifetime denominator or peak")
    return {"event_counts": dict(counts), "paid": dict(paid), "owned_paid": dict(owned_paid),
            "peak": peak, "lifetime_trace": lives, "birth457": birth}


def verified_prior(oldword, folder):
    receipt = json.loads(pinned(folder / "ALL-PAIRS-RESULT.json", OLD["receipt"]))
    require(receipt["status"] == "PASS_ALL_LITERAL_MOVE_PAIR_COLUMNS"
            and receipt["engine_sha256"] == OLD["engine"]
            and receipt["canonical_word_sha256"] == OLD["word"]
            and receipt["unique_pairs"] == OLD["ascending"]
            and receipt["directed_pairs"] == OLD["directed"]
            and receipt["move_events"] == OLD["moves"]
            and receipt["shards"] == [986, 986, 985]
            and len(receipt["shard_sha256"]) == 3, "historical pair receipt completeness")
    manifest = json.loads(pinned(folder / "ALL-PAIRS-MANIFEST.json", receipt["manifest_sha256"]))
    groups = groups_for(oldword["program"], oldword["frames"])
    keys = sorted(groups)
    require(len(keys) == OLD["ascending"]
            and manifest["groups"] == [{"ascent": list(p), "occurrences": groups[p]} for p in keys]
            and manifest["canonical_word_sha256"] == OLD["word"]
            and manifest["gzip_sha256"] == OLD["gzip"]
            and manifest["engine_sha256"] == OLD["engine"], "historical literal census mismatch")
    by_pair = {}
    for shard, (digest, count) in enumerate(zip(receipt["shard_sha256"], receipt["shards"])):
        lines = pinned(folder / f"ALL-PAIRS-SHARD-{shard}.jsonl", digest).splitlines()
        require(len(lines) == count, "incomplete predecessor shard")
        for i, line in zip(range(shard, len(keys), 3), lines):
            p = keys[i]
            rank = len(oldword["frames"][p[1]]) - len(oldword["frames"][p[0]])
            expected = {"index": i, "ascent": list(p), "rank": rank, "forward_columns": 512,
                        "adjoint_columns": 512, "wrong_phase_rejected": True}
            require(json.loads(line) == expected and p not in by_pair, "bad prior phase row")
            by_pair[p] = (shard, i)
    require(set(by_pair) == set(groups), "incomplete prior phase table")
    return by_pair


def pair_job(job):
    code, frames, keys = job
    phase = engine_from(code)
    return [(pair, phase.pair_columns(frames, *pair, wrong_phase=True)) for pair in keys]


def pair_catalogue(code, base, changed, oldword, accepted, workers):
    frames = tuple(tuple(f) for f in base["frames"])
    oldframes = oldword["frames"]
    a, b = (groups_for(w["program"], frames) for w in (base, changed))
    keys = sorted(set(a) | set(b))
    reused = {}
    for i, j in keys:
        key = (i, j)
        if (key in accepted and key not in REPLACED_PAIRS
                and all(list(frames[f]) == oldframes[f] for f in key)):
            reused[key] = accepted[key]
    needs = [k for k in keys if k not in reused]
    require(REPLACED_PAIRS <= set(needs), "three route columns must run fresh")
    print(f"pair coverage: {len(a)} source, {len(b)} candidate, "
          f"{len(reused)} reused, {len(needs)} fresh", flush=True)
    if workers == 1:
        fresh = dict(pair_job((code, frames, needs)))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            chunks = pool.map(pair_job, [(code, frames, needs[i::workers]) for i in range(workers)])
            fresh = dict(item for batch in chunks for item in batch)
    require(set(fresh) == set(needs), "incomplete fresh phase table")
    rows = []
    for p in keys:
        rank = len(frames[p[1]]) - len(frames[p[0]])
        require(p in reused or fresh[p] == rank, "rank gate")
        rows.append({"ascent": p, "rank": rank, "forward_columns": 512, "adjoint_columns": 512,
                     "wrong_phase_rejected": True, "prior_shard_and_index": reused.get(p),
                     "source_occurrences": a.get(p, []), "candidate_occurrences": b.get(p, [])})

    def census(x):
        return {"ascent_groups": len(x), "directed_pairs":
                len({(row[2], row[3]) for entries in x.values() for row in entries}),
                "move_occurrences": sum(map(len, x.values()))}

    return {"counts": {"source": census(a), "candidate": census(b), "union": len(keys),
                       "reused": len(reused), "fresh": len(fresh)}, "rows": rows}


def route_identity(phase, frames):
    def direct(a, b):
        return phase.dagger(phase.frame_circuit(frames[a])) + phase.frame_circuit(frames[b])

    two_steps = direct(FIRST, STOP) + direct(STOP, LAST)
    one_step = direct(FIRST, LAST)
    require(phase.tableau(two_steps) == phase.tableau(one_step), "bypass signed action")
    for a, b in ((two_steps, one_step), (phase.dagger(two_steps), phase.dagger(one_step))):
        require(all(phase.column(a, j) == phase.column(b, j) for j in range(512)),
                "bypass exact operator column")
    wrong = one_step + (("phase", 1),)
    require(phase.tableau(wrong) == phase.tableau(two_steps)
            and phase.column(wrong) != phase.column(two_steps), "bypass phase mutation detected")
    return {"route": [FIRST, STOP, LAST], "direct": [FIRST, LAST],
            "all_forward": 512, "all_adjoint": 512, "wrong_phase": "rejected"}


def changed_event(w, clock, event):
    p = w["program"]
    return {**w, "program": p[:clock] + [event] + p[clock + 1:]}


def rejected(label, thunk):
    try:
        thunk()
    except ValueError as exc:
        require(str(exc).startswith(label), f"unexpected mutation rejection {exc}")
        return str(exc)
    raise ValueError(f"mutation accepted: {label}")


def controls(w, count, clears, birth, cut):
    def edit(event):
        return schedule(changed_event(w, cut, event), count, clears, birth)

    initial = w["initial"][:]
    initial[457] = 281 if birth != 281 else 3
    early, late = w["program"][:cut], w["program"][cut + 1:]
    own = next(i for i, e in enumerate(w["program"]) if e[0] == "MOVE" and e[4] is True)
    return {
        "wrong_direct_source": rejected("MOVE source", lambda: edit(["MOVE", ROLE, STOP, LAST, False])),
        "wrong_direct_flag": rejected("MOVE flag", lambda: edit(["MOVE", ROLE, FIRST, LAST, True])),
        "non_bool_flag": rejected("MOVE flag", lambda: edit(["MOVE", ROLE, FIRST, LAST, 0])),
        "wrong_owned_flag": rejected("MOVE flag", lambda: schedule(
            changed_event(w, own, w["program"][own][:4] + [False]), count, clears, birth)),
        "nonnested_ascent": rejected("MOVE inclusion", lambda: edit(["MOVE", ROLE, FIRST, FIRST, False])),
        "missing_direct": rejected("ADD frame", lambda: schedule(
            {**w, "program": early + late}, count - 1, clears, birth)),
        "wrong_birth457": rejected("initial or final frame", lambda: schedule(
            {**w, "initial": initial}, count, clears, birth)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", required=True, type=int, choices=SOURCE)
    for name in ("source", "candidate", "engine", "prior-engine", "prior-word", "prior-receipts", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--candidate-gzip", required=True)
    parser.add_argument("--candidate-raw", required=True)
    parser.add_argument("--workers", default=1, choices=(1, 2), type=int)
    args = parser.parse_args()
    start = monotonic()
    src = SOURCE[args.pr]
    direct_clock = src["clocks"][1] - 1
    pins = {args.source: src["gzip"], args.candidate: args.candidate_gzip,
            args.engine: src["engine"], args.prior_engine: OLD["engine"], args.prior_word: OLD["gzip"]}
    args.out.mkdir(exist_ok=False)
    dump(args.out / "START.json", {
        "started_at": stamp(), "pr": args.pr, "head": src["head"],
        "source_raw": src["raw"], "candidate_raw": args.candidate_raw,
        "source_gzip": src["gzip"], "candidate_gzip": args.candidate_gzip,
        "scripts": {p.name: sha(p.read_bytes()) for p in (Path(__file__), Path(__file__).with_name("physical.py"))},
        "primes_and_seeds": MODULI, "args": vars(args) | {
            k: str(v) for k, v in vars(args).items() if isinstance(v, Path)}})
    old, sb = word(args.source, src["gzip"], src["raw"])
    new, cb = word(args.candidate, args.candidate_gzip, args.candidate_raw)
    require_cut(old, new, src["clocks"])
    birth = 281
    os = schedule(old, src["events"], src["clear"], birth)
    ns = schedule(new, src["events"] - 1, src["clear"], birth)
    require(os["lifetime_trace"] == ns["lifetime_trace"] and os["owned_paid"] == ns["owned_paid"],
            "ordered owned schedule changed")
    ms = controls(new, src["events"] - 1, src["clear"], birth, direct_clock)
    code = read_engine(args.engine, src["engine"])
    require(code == read_engine(args.prior_engine, OLD["engine"]), "phase engines differ")
    oldword, pb = word(args.prior_word, OLD["gzip"])
    require(pb["canonical_sha256"] == OLD["word"], "historical canonical word")
    prior = verified_prior(oldword, args.prior_receipts)
    cat = pair_catalogue(code, old, new, oldword, prior, args.workers)
    dump(args.out / "MOVE-PAIRS.json", cat)
    phase = engine_from(code)
    route = route_identity(phase, old["frames"])
    ports = raw_ports(phase, old, require)
    dump(args.out / "OPERATORS.json", {"route": route, "raw_ports": ports, "controls": ms})
    def task(m):
        prime, seed = m
        ans = evaluate(phase, old, new, prime, seed, direct_clock, prime == MODULI[0][0], require)
        dump(args.out / f"PHYSICAL-{prime}.json", ans)
        return ans

    finite = [task(m) for m in MODULI]
    for path, h in pins.items():
        pinned(path, h)
    require(prior == verified_prior(oldword, args.prior_receipts), "historical proof custody")
    report = {
        "status": "PASS_STRICT_379_NATIVE_FINITE",
        "pr": args.pr, "head": src["head"], "source": sb, "candidate": cb, "historical": pb,
        "source_cut_clocks": src["clocks"], "candidate_direct_clock": direct_clock,
        "phase_code_sha256": sha(code.encode()),
        "prior_proof_sha256": OLD["receipt"], "pair_counts": cat["counts"],
        "route_columns": route, "raw_ports": ports, "controls": ms,
        "schedules": {"source": os, "candidate": ns},
        "finite_replays": [{"prime": x["prime"], "seed": x["seed"], "digests": x["digests"],
                            "endpoint_rows": x["endpoint_rows"]} for x in finite],
        "artifacts": {p.name: sha(p.read_bytes()) for p in sorted(args.out.glob("*.json"))},
        "completed_at": stamp(), "elapsed_seconds": monotonic() - start,
    }
    dump(args.out / "RESULT.json", report)
    print(f"PASS_STRICT_379_NATIVE_FINITE pr={args.pr} elapsed={report['elapsed_seconds']:.1f}", flush=True)


if __name__ == "__main__":
    main()
