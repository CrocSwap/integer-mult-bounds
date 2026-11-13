"""Full truth-table state search; imports no primary or predecessor code."""

import heapq
import json


def check(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    # Bit t of each table is the row value on input assignment t in {0,...,15}.
    identity = tuple(sum(((t >> i) & 1) << t for t in range(16)) for i in range(3))
    common = sum(((t >> 3) & 1) << t for t in range(16))
    start = (0, identity)
    goal = (1, tuple(row ^ common for row in identity))
    distance = {start: 0}
    pending = [(0, start)]
    scanned = 0
    transitions = 0
    for _ in range(1344 * 7 + 1):
        if not pending:
            break
        value, state = heapq.heappop(pending)
        if value != distance[state]:
            continue
        phase, rows = state
        scanned += 1
        successors = []
        for destination in range(3):
            for source in range(3):
                if destination == source:
                    continue
                cheap = ((1, 0), (2, 1)) if phase == 0 else ((2, 0), (1, 2))
                cost = 1 if (destination, source) in cheap else 3
                changed = list(rows)
                changed[destination] ^= changed[source]
                successors.append(((phase, tuple(changed)), cost))
        if phase == 0:
            successors.append(((1, (rows[0] ^ common, rows[1], rows[2])), 1))
        for target, cost in successors:
            transitions += 1
            candidate = value + cost
            if candidate < distance.get(target, 10**9):
                distance[target] = candidate
                heapq.heappush(pending, (candidate, target))
    check(not pending, "search capacity exhausted")
    check(len(distance) == scanned == 1344, "state inventory mismatch")
    check(transitions == 8232, "transition inventory mismatch")
    check(distance[goal] == 7, "unrestricted optimum mismatch")
    print(json.dumps({"status": "PASS_INDEPENDENT_TWO_EPOCH_FANOUT", "errors": 0,
                      "truth_assignments_per_state": 16, "states": scanned,
                      "transitions": transitions, "optimal_total": distance[goal]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
