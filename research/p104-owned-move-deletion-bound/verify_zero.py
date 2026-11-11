"""Audit normalized owned-MOVE inputs using exact signed rational rows."""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from math import gcd
from pathlib import Path
import time

SHA = "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756"
HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
OWNED_PAID = {1: 20, 2: 9, 3: 2, 4: 13, 5: 2, 6: 1}


def reduced(denominator, numerators):
    if not numerators:
        return 1, {}
    factor = denominator
    for n in numerators.values():
        factor = gcd(factor, n)
        if factor == 1:
            return denominator, numerators
    return denominator // factor, {k: n // factor for k, n in numerators.items()}


def scaled(row, q):
    denominator, numerators = row
    return reduced(denominator * q.denominator, {k: q.numerator * n for k, n in numerators.items()})


def plus(destination, source, q):
    denominator, numerators = destination
    s_den, s_num = source
    right_denominator = s_den * q.denominator
    common_factor = gcd(denominator, right_denominator)
    left_scale = right_denominator // common_factor
    right_scale = denominator // common_factor * q.numerator
    sums = {k: left_scale * n for k, n in numerators.items()} if left_scale != 1 else numerators
    for k, n in s_num.items():
        value = sums.get(k, 0) + right_scale * n
        if value:
            sums[k] = value
        else:
            sums.pop(k, None)
    return reduced(denominator * left_scale, sums)


def frame_space(rows):
    space = {0}
    for row in rows:
        space |= {v ^ row for v in space}
    assert len(space) == 1 << len(rows)
    return space


def audit(word, start, seconds):
    public = word["public"]
    roles = public + word["owned_fields"]
    events = word["program"]
    frames = [frame_space(f) for f in word["frames"]]
    charts = word["initial"] + [None] * (roles - public)
    rows = [(1, {r: 1}) for r in range(public)] + [None] * (roles - public)
    fresh = set()
    live = set()
    owned_paid = Counter()
    nonzero_clears = owned_copies = lifetimes = peak = visited = 0
    found, token_hits = [], []
    cap = start + seconds
    for index, event in enumerate(events):
        if index % 64 == 0 and time.monotonic() >= cap:
            break
        visited = index + 1
        op, d, *args = event
        if op == "INIT":
            frame, = args
            assert d >= public and charts[d] is None and rows[d] is None and d not in live
            rows[d], charts[d] = (1, {}), frame
            fresh.add(d)
            live.add(d)
            lifetimes += 1
            peak = max(peak, len(live))
        elif op == "CLEAR":
            frame, = args
            assert d in live and charts[d] == frame
            nonzero_clears += bool(rows[d][1])
            fresh.discard(d)
            live.remove(d)
            rows[d], charts[d] = None, None
        elif op == "MOVE":
            source, target, owned = args
            assert charts[d] == source and owned == (d in live) == (d >= public)
            assert frames[source] < frames[target] or (owned and frames[target] < frames[source])
            if owned:
                rank = abs(len(word["frames"][target]) - len(word["frames"][source]))
                owned_paid[rank] += 1
                if not rows[d][1]:
                    found.append({"literal_index": index, "role": d, "from": source, "to": target, "rank": rank})
                if d in fresh:
                    assert not rows[d][1]
                    token_hits.append(index)
            fresh.discard(d)
            charts[d] = target
        elif op == "SCALE":
            coefficient, frame = args
            q = Fraction(coefficient)
            assert charts[d] == frame and q
            rows[d] = scaled(rows[d], q)
        else:
            s, coefficient, frame = args
            q = Fraction(coefficient)
            assert op in ("ADD", "COPY") and d != s and charts[d] == frame == charts[s] and q
            if op == "COPY":
                assert d in live and d in fresh and not rows[d][1]
                rows[d] = scaled(rows[s], q)
                owned_copies += 1
            else:
                rows[d] = plus(rows[d], rows[s], q)
            fresh.discard(d)
    first_unvisited = None if visited == len(events) else visited
    remaining_move = next((i for i in range(visited, len(events)) if events[i][0] == "MOVE" and events[i][-1]), None)
    if first_unvisited is None:
        assert not live and not fresh and charts == word["final"] + [None] * (roles - public)
    return {
        "scope_exhausted": first_unvisited is None,
        "literal_events": len(events), "literal_events_visited": visited,
        "first_unvisited_literal_index": first_unvisited,
        "first_unvisited_owned_move_index": remaining_move,
        "paid_owned_histogram": owned_paid, "paid_owned_moves": sum(owned_paid.values()),
        "exact_zero_moves": found, "fresh_zero_moves": len(token_hits),
        "owned_lifetimes": lifetimes, "peak_owned": peak, "checked_copies": owned_copies,
        "nonzero_owned_clears": nonzero_clears,
    }


def control():
    # Same public input reaches an owned role with two different signed rational paths.
    word = {
        "public": 1, "owned_fields": 1, "initial": [0], "final": [0], "frames": [[], [1]],
        "program": [
            ["INIT", 1, 0], ["COPY", 1, 0, "2/3", 0],
            ["ADD", 1, 0, "-1/2", 0], ["ADD", 1, 0, "-1/6", 0],
            ["MOVE", 1, 0, 1, True], ["CLEAR", 1, 1],
        ],
    }
    observed = audit(word, time.monotonic(), 1)
    assert observed["scope_exhausted"]
    assert observed["exact_zero_moves"] == [{"literal_index": 4, "role": 1, "from": 0, "to": 1, "rank": 1}]
    assert observed["fresh_zero_moves"] == 0
    word["program"][3][3] = "1/6"
    changed = audit(word, time.monotonic(), 1)
    assert changed["scope_exhausted"] and not changed["exact_zero_moves"]
    return {"cancellation_detected": True, "changed_sign_rejected": True, "test_owned_move_index": 4}



def main():
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    start = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", required=True, type=Path)
    parser.add_argument("--cap", default=22.0, type=float)
    args = parser.parse_args()
    assert 0 < args.cap <= 22.0
    raw = args.word.read_bytes()
    if sha256(raw).hexdigest() != SHA:
        raise ValueError("Unexpected compressed word SHA-256")
    result = audit(json.loads(gzip.decompress(raw)), start, args.cap)
    if result["scope_exhausted"]:
        assert result["paid_owned_histogram"] == OWNED_PAID
        assert tuple(result[k] for k in ("owned_lifetimes", "peak_owned", "checked_copies")) == (70, 49, 1)
    print(json.dumps({"scientific_head": HEAD, "compressed_word_sha256": SHA,
                      **result, "control": control()}, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
