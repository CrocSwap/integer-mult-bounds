"""Find removable MOVE stops after commuting scalar contacts to another chart.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""

from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import chain
from pathlib import Path
import gzip
import json


SOURCE = Path(__file__).resolve().parents[1] / "shared-wire-split-composition/data/final.json.gz"
HEAD = "93effe2a135bf57b9e484cb630d8dd057159aec9"
PAYLOAD_SHA = "91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097"


def need(value, why):
    if not value:
        raise ValueError(why)


def payload(word):
    return json.dumps(word, sort_keys=True, separators=(",", ":")).encode()


def span(basis):
    space = {0}
    for x in basis:
        need(0 < x < 512 and x not in space, "Invalid binary basis")
        space.update(x ^ y for y in tuple(space))
    return frozenset(space)


def roles(event):
    return event[1:3] if event[0] in {"ADD", "COPY"} else event[1:2]


def commute(left, right):
    """MOVE is chart transport, hence identity in normalized coordinates."""
    if right[0] == "MOVE" or not set(roles(left)).intersection(roles(right)):
        return True
    if left[0] == right[0] == "ADD":
        return left[2] != right[1] and right[2] != left[1]
    if left[0] == right[0] == "SCALE":
        return True
    return False


def inventory(word, spaces):
    program = word["program"]
    public = len(word["initial"])
    all_roles = public + word["owned_fields"]
    history = defaultdict(list)
    transitions = [[-1] for _ in range(all_roles)]
    charts = [[f] for f in word["initial"]] + [[None] for _ in range(word["owned_fields"])]
    for i, event in enumerate(program):
        op, role = event[:2]
        for touched in roles(event):
            history[touched].append(i)
        current = charts[role][-1]
        if op == "MOVE":
            a, b, private = event[2:]
            need(current == a and private == (role >= public), ("MOVE frame", i))
            need(spaces[a] < spaces[b] or (private and spaces[b] < spaces[a]), ("MOVE nested", i))
            transitions[role].append(i)
            charts[role].append(b)
        elif op == "INIT":
            need(current is None and role >= public, ("INIT", i))
            transitions[role].append(i)
            charts[role].append(event[2])
        elif op == "CLEAR":
            need(current == event[2] and role >= public, ("CLEAR", i))
            transitions[role].append(i)
            charts[role].append(None)
        elif op in {"ADD", "COPY", "SCALE"}:
            need(all(charts[s][-1] == event[-1] for s in roles(event)), ("Scalar chart", i))
        else:
            raise ValueError(("Unknown event", i))
    need([c[-1] for c in charts] == word["final"] + [None] * word["owned_fields"], "Final charts")
    return history, transitions, charts


def scalar_interval(index, program, history, moved):
    event = program[index]
    conflicts = set(chain.from_iterable(history[r] for r in roles(event))) - moved
    incompatible = [i for i in conflicts if not commute(event, program[i])]
    lo = max((i + 1 for i in incompatible if i < index), default=0)
    hi = min((i for i in incompatible if i > index), default=len(program))
    return lo, hi


def first_slot(lo, hi, role, chart, transitions, charts):
    if lo > hi:
        return None
    for j in range(bisect_left(transitions[role], lo) - 1, bisect_left(transitions[role], hi)):
        if charts[role][j] == chart:
            cut = max(lo, transitions[role][j] + 1)
            if cut <= hi:
                return cut
    return None


def placement(role, contacts, bounds, frame, program, trans, charts):
    lo, hi = bounds
    chosen = []
    for index, available_lo, available_hi in contacts:
        left = max(lo, available_lo)
        right = min(hi, available_hi)
        event = program[index]
        if event[0] == "SCALE":
            cut = left if left <= right else None
        else:
            other = event[1] if event[2] == role else event[2]
            cut = first_slot(left, right, other, frame, trans, charts)
        if cut is None:
            return None
        lo = cut
        chosen.append((index, cut, frame))
    return chosen


def plans(word, spaces, history, trans, charts):
    program = word["program"]
    stats = Counter()
    hits = []
    for role, route in enumerate(trans):
        for idx, (first, second) in enumerate(zip(route, route[1:])):
            if first < 0 or program[first][0] != "MOVE" or program[second][0] != "MOVE":
                continue
            e, f = program[first], program[second]
            a, b, c = e[2], e[3], f[3]
            need(b == f[2], "Consecutive MOVE endpoint")
            stats["two_hops"] += 1
            if not (a == c or spaces[a] < spaces[c] or (e[4] and spaces[c] < spaces[a])):
                stats["unnested_shortcut"] += 1
                continue
            start = bisect_right(history[role], first)
            stop = bisect_left(history[role], second)
            contacts = history[role][start:stop]
            stats[f"eligible_{len(contacts)}_contacts"] += 1
            if any(program[i][0] not in {"ADD", "SCALE"} for i in contacts):
                stats["exclusive_middle_contact"] += 1
                continue
            moved = set(contacts)
            contacts = [(i, *scalar_interval(i, program, history, moved)) for i in contacts]
            prev_event = route[idx - 1]
            next_event = route[idx + 2] if idx + 2 < len(route) else len(program)
            for pivot in range(len(contacts) + 1):
                left = placement(role, contacts[:pivot], (prev_event + 1, first), a, program, trans, charts)
                if left is None:
                    continue
                right = placement(role, contacts[pivot:], (second + 1, next_event), c, program, trans, charts)
                if right is None:
                    continue
                remove_ranks = [abs(len(word["frames"][a]) - len(word["frames"][b])),
                                abs(len(word["frames"][b]) - len(word["frames"][c]))]
                replacement_rank = abs(len(word["frames"][a]) - len(word["frames"][c]))
                hits.append({"role": role, "moves": [first, second], "frames": [a, b, c],
                             "repositioned": left + right, "old_move_ranks": remove_ranks,
                             "replacement_rank": replacement_rank})
                break
    return stats, hits


def controls():
    e = ["ADD", 1, 2, "1", 0]
    need(commute(e, ["ADD", 1, 3, "-1", 0]), "Shared destination commutes")
    need(commute(e, ["ADD", 3, 2, "-1", 0]), "Shared source commutes")
    need(not commute(e, ["ADD", 2, 3, "-1", 0]), "Source version must be preserved")
    need(not commute(e, ["COPY", 4, 1, "1", 0]), "Copy barrier")
    trans, charts = [[-1, 3, 6]], [[4, 7, 9]]
    need(first_slot(3, 6, 0, 7, trans, charts) == 4, "Correct cut after MOVE")
    need(first_slot(3, 3, 0, 7, trans, charts) is None, "Chart not reached")
    return 6


def main():
    count = controls()
    word = json.loads(gzip.decompress(SOURCE.read_bytes()))
    digest = sha256(payload(word)).hexdigest()
    need(digest == PAYLOAD_SHA, "Native word differs from pinned source")
    spans = [span(basis) for basis in word["frames"]]
    history, trans, charts = inventory(word, spans)
    stats, hits = plans(word, spans, history, trans, charts)
    print(json.dumps({"head": HEAD, "source_sha256": digest, "controls": count,
                      "stats": dict(stats), "nominations": hits}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
