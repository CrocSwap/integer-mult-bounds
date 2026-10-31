#!/usr/bin/env python3
"""Separate set-valued whole-emitter check of new-route and neutral cases.

Prepared for @CubeJerry with substantial OpenAI Codex assistance by worker B.
Apache-2.0. No author/predecessor executable is imported. This independently
checks the 20 newly reachable outcomes and 22 neutral attainers, not the full
2,270-case outcome census.
"""
import argparse
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
from heapq import heappop, heappush
import json
from pathlib import Path


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def altered(records, row):
    first, last = row["first"], row["last"]
    a, b = row["gate"]
    need(records[first][:3] == records[last][:3] == ["ADD", a, b], "outer pair")
    output, contacts = [], 0
    for index, event in enumerate(records):
        if index in (first, last):
            continue
        output.append(event)
        if first < index < last:
            if event[0] != "ADD":
                need(event[1] not in (a, b), "destructive barrier")
            else:
                d, s, frame = event[1:]
                need((d, s) != (b, a), "reverse barrier")
                if d == b:
                    output.append(["ADD", a, s, frame]); contacts += 1
                elif s == a:
                    output.append(["ADD", d, b, frame]); contacts += 1
    need(contacts == row["contacts"], "every correction counted")
    return output


def checker(word, paths):
    edges, adjacent = {}, defaultdict(list)
    for key, value in paths.items():
        need(len(value) == 1, "singleton source route")
        a, b, rank = value[0]
        edges[a, b] = rank
        adjacent[a].append((b, rank))
    distance_cache = {}

    def distance(a, b):
        if a not in distance_cache:
            dist, queue = {a: 0}, [(0, a)]
            while queue:
                value, vertex = heappop(queue)
                if value != dist[vertex]:
                    continue
                for target, rank in adjacent[vertex]:
                    proposal = value + rank
                    if proposal < dist.get(target, 10**9):
                        dist[target] = proposal
                        heappush(queue, (proposal, target))
            distance_cache[a] = dist
        need(b in distance_cache[a], "unreachable requested route")
        return distance_cache[a][b]

    owned = set(word["owned"])
    width = len(word["start"])
    expected = [{i} if i not in owned else set() for i in range(width)]
    for i in range(111, 222):
        expected[i].symmetric_difference_update({i - 111})

    def emit(records):
        states, rows = list(word["start"]), [{i} for i in range(width)]
        bill, new, paid_new = Counter(), set(), set()

        def move(role, target):
            source = states[role]
            if source == target:
                return
            if source is None:
                need(role in owned and not rows[role], "zero owned header")
            else:
                rank = distance(source, target)
                if (source, target) not in edges:
                    new.add((source, target))
                if rows[role]:
                    bill[rank] += 1
                    if (source, target) not in edges:
                        paid_new.add((source, target))
            states[role] = target

        for event in records:
            op, d = event[:2]
            if op in ("ERASE", "INIT"):
                need(d in owned and (op != "INIT" or not rows[d]), "owned boundary")
                rows[d] = set()
                states[d] = event[2]
            else:
                need(op == "ADD", "scalar opcode")
                s, target = event[2:]
                if rows[s]:
                    move(d, target); move(s, target)
                    rows[d].symmetric_difference_update(rows[s])
        for role, target in enumerate(word["final"]):
            if role in owned:
                need(not rows[role], "owned return")
                states[role] = target
            else:
                move(role, target)
        need(states == word["final"] and rows == expected, "complete frames and every input column")
        return bill, new, paid_new
    return emit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--paths", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    args = parser.parse_args()
    word_raw, paths_raw = args.word.read_bytes(), args.paths.read_bytes()
    need(sha256(word_raw).hexdigest() == "8dd441fdb9c8923df06eb5ebfda37d03e4539f2305763e688d8c7025d196c4b1", "word source")
    need(sha256(paths_raw).hexdigest() == "f4dd58b78121040b1f054c0f7a626b25f6ef8d39f3de044d3456ea7dea8a6a5e", "route source")
    word = json.loads(gzip.decompress(word_raw))
    paths, certificate = json.loads(paths_raw), json.loads(args.certificate.read_text())
    records = [e for e in word["records"] if e[0] not in ("Q", "ZERO_Q")]
    emit = checker(word, paths)
    baseline, new, paid_new = emit(records)
    need(not new and not paid_new, "source direct routes")
    need(baseline == Counter(e[4] for e in word["records"] if e[0] == "Q"), "complete source bill")
    selected = [row for row in certificate["outcomes"] if row.get("new_requests") or row.get("sign") == "zero"]
    need(len(selected) == 42 and len({(r["first"], r["last"]) for r in selected}) == 42, "42 distinct selected cases")
    counts = Counter()
    for row in selected:
        bill, new, paid_new = emit(altered(records, row))
        delta = [[r, bill[r] - baseline[r]] for r in sorted(bill.keys() | baseline.keys()) if bill[r] != baseline[r]]
        need(delta == row["collapsed_delta"], "independent whole invoice")
        need(sorted(map(list, new)) == row["new_requests"], "all new routes")
        if row["sign"] == "zero":
            need(not delta and not paid_new, "direct paid attainer")
            counts["neutral"] += 1
        else:
            need(bool(new), "new route case")
            negative = [(r, c) for r, c in delta if c < 0]
            positive = [(r, c) for r, c in delta if c > 0]
            need((not negative and bool(positive)) or
                 (len(negative) == 1 and negative[0][1] == -1
                  and sum(r*c for r,c in positive) == negative[0][0]
                  and sum(c for r,c in positive) >= 2), "strict positive partition or terms")
            counts["new_route_strict"] += 1
    need(counts == {"neutral": 22, "new_route_strict": 20}, "selected outcome counts")
    print(json.dumps(dict(counts), sort_keys=True))
    print("PASS_INDEPENDENT_G20_CRITICAL_CASES")


if __name__ == "__main__":
    main()
