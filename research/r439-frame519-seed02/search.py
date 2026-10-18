#!/usr/bin/env python3
"""Exhaust two fixed factors of PR589's frame-519 block.

Ross Richardson with substantial OpenAI Codex assistance; Apache-2.0.
Only positive, destination-once schedules with distinct donors are searched.
"""
import gzip
import hashlib
import json
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
START, SPLIT, END, FRAME = 163, 182, 205, 519


def matrix(gates, registers):
    index = {r: i for i, r in enumerate(registers)}
    rows = [[int(i == j) for j in range(len(registers))] for i in range(len(registers))]
    for _, dst, donors in gates:
        for src in donors:
            rows[index[dst]] = [a + b for a, b in zip(rows[index[dst]], rows[index[src]])]
    return rows


def solve(gates, registers):
    n = len(registers)
    rows = matrix(gates, registers)
    if any(x not in (0, 1) for row in rows for x in row):
        raise ValueError("search requires binary positive factor rows")
    if any(rows[i][i] != 1 for i in range(n)):
        raise ValueError("search requires unit diagonal")
    masks = [sum(x << j for j, x in enumerate(row)) for row in rows]
    goals = [mask ^ (1 << i) for i, mask in enumerate(masks)]

    @lru_cache(None)
    def cover(dst, restricted_state):
        goal = goals[dst]
        donors = [(j, masks[j] if restricted_state >> j & 1 else 1 << j)
                  for j in range(n) if goal >> j & 1]
        donors = [(j, bits) for j, bits in donors if not bits & ~goal]

        @lru_cache(None)
        def exact(left):
            if left == 0:
                return ()
            bit = left & -left
            best = None
            for j, bits in donors:
                if not bits & bit or bits & ~left:
                    continue
                tail = exact(left ^ bits)
                if tail is not None:
                    proposal = tuple(sorted((j, *tail)))
                    if best is None or (len(proposal), proposal) < (len(best), best):
                        best = proposal
            return best

        return exact(goal)

    size = 1 << n
    infinity = 10**9
    costs = [infinity] * size
    paths = [None] * size
    costs[0], paths[0] = 0, ()
    edges = feasible = 0
    for state in range(size):
        for dst in range(n):
            if state >> dst & 1:
                continue
            edges += 1
            selected = cover(dst, state & goals[dst])
            if selected is None:
                continue
            feasible += 1
            new_state = state | 1 << dst
            new_cost = costs[state] + len(selected)
            if new_cost < costs[new_state]:
                costs[new_state] = new_cost
                paths[new_state] = (*paths[state], (dst, selected)) if paths[state] is not None else None
    if paths[-1] is None:
        raise ValueError("no schedule in the fixed-factor class")
    program = [[FRAME, registers[d], [registers[s]]] for d, ss in paths[-1] for s in ss]
    if matrix(program, registers) != rows:
        raise ValueError("discovery produced an incorrect integer map")
    return dict(original_adds=sum(len(g[2]) for g in gates), minimum=costs[-1],
                states=size, state_destination_pairs=edges, feasible_edges=feasible,
                cover_states=cover.cache_info().currsize, matrix=rows, program=program)


def discover():
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    block = word["B"][START:END]
    if any(g[0] != FRAME for g in block):
        raise ValueError("source block moved")
    registers = sorted({r for _, d, ss in block for r in [d, *ss]})
    factors = [solve(word["B"][a:b], registers) for a, b in ((START, SPLIT), (SPLIT, END))]
    return dict(schema="r439-frame519-two-factor/1", assignment_seed=2,
                base_commit="f567884aeb8851b6e794af1184119a3bfbe1e631",
                source_word=str(WORD.relative_to(ROOT)),
                source_sha256=hashlib.sha256(WORD.read_bytes()).hexdigest(),
                frame=FRAME, slice=[START, END], split=SPLIT, registers=registers,
                search_class="two fixed binary integer factors; destination-once; distinct positive donors",
                stopping_rule="all 2^12 states and all unrealized destinations in each factor",
                factors=factors)


def main():
    result = discover()
    output = HERE / "CANDIDATE.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("SEARCH_R439_FRAME519", " + ".join(str(f["minimum"]) for f in result["factors"]),
          "=", sum(f["minimum"] for f in result["factors"]), "before=42")


if __name__ == "__main__":
    main()
