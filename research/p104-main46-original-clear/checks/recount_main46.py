"""Independently recount the literal main-46 candidate and its signed invoice."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal

PINS = {
    "word.json.gz": "37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "invoice-new.json": "b38afd7ca590b5c4c301ee4fbe0e123f0c7220c2bd1f40c66adf208652e3ce15",
    "FINAL.json": "f24baa73a60d084a6d613dad914f1237a5890a049a183b993af39c75dde99add",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
OLD_CANONICAL = "e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd"
NEW_CANONICAL = "aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916"


def sha(data):
    return sha256(data).hexdigest()


def rank(generators):
    pivots = {}
    for vector in generators:
        while vector:
            degree = vector.bit_length()
            if degree in pivots:
                vector ^= pivots[degree]
            else:
                pivots[degree] = vector
                break
    return len(pivots)


def scaled(counter, n):
    return Counter({k: v*n for k, v in counter.items()})


def difference(new, old):
    items = set(new) | set(old)
    return {r: new[r] - old[r] for r in sorted(items) if new[r] != old[r]}


def invoice(word, caller):
    frames = word["frames"]
    ranks = [rank(frame) for frame in frames]
    assert ranks == list(map(len, frames))
    public = word["public"]
    active = dict(enumerate(word["initial"]))
    paid, scalar_counts, move_pairs, owned_rise = Counter(), Counter(), Counter(), Counter()
    life, peak, scalar_upper = 0, 0, 0
    events = Counter(event[0] for event in word["program"])
    paid_rank = {}
    for op, role, *tail in word["program"]:
        if op == "INIT":
            assert role >= public and role not in active
            active[role] = tail[0]
            life += 1
            peak = max(peak, len(active) - public)
            continue
        if op == "MOVE":
            old, new, owned = tail
            assert active[role] == old and owned == (role >= public)
            if (old, new) not in paid_rank:
                joined_rank = rank(frames[old] + frames[new])
                assert joined_rank == max(ranks[old], ranks[new])
                paid_rank[old, new] = abs(ranks[old] - ranks[new])
                assert paid_rank[old, new] != 0
            assert owned or ranks[new] > ranks[old]
            rk = paid_rank[old, new]
            move_pairs[old, new] += 1
            paid[rk] += 1
            if owned and ranks[new] > ranks[old]:
                owned_rise[rk] += 1
            active[role] = new
            continue
        assert active[role] == tail[-1]
        if op == "CLEAR":
            assert role >= public
            del active[role]
            continue
        if op in ("ADD", "COPY"):
            assert tail[0] != role and active[tail[0]] == active[role]
        else:
            assert op == "SCALE"
        q = Q(tail[-2])
        a, d = abs(q.numerator), q.denominator
        assert 0 < abs(q) < 65535
        scalar_counts[(op, str(q))] += 1
        scalar_upper += 4*(a.bit_length() + d.bit_length() + 1 +
                           (a.bit_count() if op != "SCALE" else 0))
    assert active == dict(enumerate(word["final"]))
    hosted = word["hosted"]
    mains = set(word["live"]) | {r+112 for r in word["live"]} | set(hosted["X2"]) | set(hosted["Y2"])
    targets = Counter(ranks[word["final"][r]] - ranks[word["initial"][r]]
                      for r in range(public) if r not in mains)
    assert min(targets) > 0
    caller_paid, caller_targets = Counter(), Counter()
    calls = 0
    for event in caller["events"]:
        typ, op, *_ = event
        if typ == "J":
            calls += 1
            continue
        count = len(caller["types"][typ]["ports"])
        if op == "QUERY":
            caller_paid[1] += count
        if op in ("IDLE_ONE", "IDLE_ODD"):
            caller_paid[8*len(event[3]) + (op == "IDLE_ODD")] += count
    assert calls == caller["stages"] == 17
    assert caller["types"]["A"]["ports"] == hosted["Dports"]
    assert sorted(set(range(104)) - set(hosted["Dports"])) == caller["types"]["B"]["ports"]
    for typ in caller["types"].values():
        for diag in typ["diagonal"]:
            caller_targets[diag[0] % 2 + 8*sum(diag[2:])] += len(typ["ports"])
    assert min(caller_targets) > 0
    return {"paid": scaled(paid, calls) + caller_paid, "targets": scaled(targets, calls) + caller_targets,
            "native_paid": paid, "native_targets": targets, "caller_paid": caller_paid,
            "caller_targets": caller_targets, "owned_rise": owned_rise, "life": life,
            "peak": peak, "events": events, "scalar_counts": scalar_counts, "scalar_upper": scalar_upper,
            "move_pairs": move_pairs, "calls": calls}


def main():
    assert __debug__
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    args = p.parse_args()
    signal.alarm(30)
    data = {path: (args.baseline / path).read_bytes() for path in PINS}
    assert {k: sha(v) for k, v in data.items()} == PINS
    old, candidate = decompress(data["word.json.gz"]), decompress(args.candidate.read_bytes())
    assert sha(old) == OLD_CANONICAL and sha(candidate) == NEW_CANONICAL
    old, candidate = json.loads(old), json.loads(candidate)
    assert {k:v for k,v in old.items() if k != "program"} == {k:v for k,v in candidate.items() if k != "program"}
    caller = json.loads(data["7113-CALLER.json"])
    before, after = (invoice(w, caller) for w in (old, candidate))
    source = json.loads(data["invoice-new.json"])
    for label in ("paid", "targets"):
        assert before[label] == {int(k):v for k,v in source[label].items()}
    assert all(before[k] == after[k] for k in ("owned_rise", "life", "peak", "targets", "native_targets", "caller_paid", "caller_targets"))
    native_delta = difference(after["native_paid"], before["native_paid"])
    paid_delta = difference(after["paid"], before["paid"])
    coefficient_delta = difference(after["scalar_counts"], before["scalar_counts"])
    event_delta = difference(after["events"], before["events"])
    pair_delta = difference(after["move_pairs"], before["move_pairs"])
    assert native_delta == {1:-2, 2:1} and paid_delta == {1:-34,2:17}
    assert coefficient_delta == {("ADD", "-1"):6, ("ADD", "1"):5}
    assert event_delta == {"ADD":11, "MOVE":-1}
    assert pair_delta == {(245,127):-1, (914,245):-1, (914,127):1} and before["move_pairs"][914,127] == 1
    assert before["scalar_upper"] == 2196644 and after["scalar_upper"] - before["scalar_upper"] == 176

    # The remaining caller terms are unchanged under the inherited exact boundary proof.
    # Each native MOVE contributes 1000 routing units under the source ordinary formula.
    final = json.loads(data["FINAL.json"])
    old_ordinary = final["ordinary_bound"]
    ordinary_delta = before["calls"] * (after["scalar_upper"] - before["scalar_upper"] + 1000*event_delta["MOVE"])
    assert ordinary_delta == -14008 and old_ordinary + ordinary_delta < 10**9
    old_lo, old_hi = map(Q, final["raw_crossing"])
    priced = run_path(str(args.baseline / "pricing.py"))
    power, cost = priced["power_bounds"], priced["cost"]
    gain_bounds = [17*(2-power(2, old_lo)[1]), 17*(2-power(2, old_hi)[0])]
    assert gain_bounds[0] > 0
    signed = []
    for row in (before, after):
        margin = row["targets"].copy()
        margin.subtract(row["paid"])
        assert sum(r*n for r,n in margin.items()) == 1424
        signed.append(margin)
    floor = Q("0.0036506661664")
    assert floor > old_hi
    old_moment, new_moment = (cost(m, floor) for m in signed)
    assert old_moment[1] < 0 < new_moment[0]
    print(json.dumps({
        "status": "DIRECTED_SIGNED_INVOICE_PASS_NATIVE_AND_FULL_APPLICATION_PENDING",
        "pins": PINS, "old_canonical": OLD_CANONICAL, "candidate_canonical": NEW_CANONICAL,
        "calls": before["calls"], "native_paid_delta": native_delta, "full_paid_delta": paid_delta,
        "paid_positions": [sum(row["paid"].values()) for row in (before, after)],
        "target_positions": sum(after["targets"].values()), "surplus": 1424,
        "old_native_paid": before["native_paid"], "new_native_paid": after["native_paid"],
        "old_full_paid": before["paid"], "new_full_paid": after["paid"],
        "productive_targets": after["targets"], "static_caller_paid": after["caller_paid"],
        "static_caller_targets": after["caller_targets"], "event_delta": event_delta,
        "coefficient_delta": [[*pair, n] for pair,n in coefficient_delta.items()],
        "pair_delta": [[*pair,n] for pair,n in pair_delta.items()],
        "new_pairs": [], "owned_rises": after["owned_rise"], "lifetimes": after["life"],
        "peak": after["peak"], "ordinary_before": old_ordinary, "ordinary_delta": ordinary_delta,
        "ordinary_projected_after": old_ordinary + ordinary_delta,
        "signed_moment_gain_at_old_crossing": list(map(str, gain_bounds)), "test_floor": str(floor),
        "old_moment_at_test_floor": list(map(str, old_moment)), "new_moment_at_test_floor": list(map(str, new_moment)),
        "still_required": ["complete native and arbitrary-input replay", "precision and tape", "compiler and outer conditions"],
    }, sort_keys=True))
    signal.alarm(0)


if __name__ == "__main__":
    main()
