"""Apply the frozen commuting ADD slides and emit a literal native candidate.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""

from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from slide_stops import HEAD, PAYLOAD_SHA, SOURCE, commute, inventory, need, payload, roles, span


def place(old, edit, spaces, history):
    need(edit["source_head"] == HEAD and edit["source_canonical_sha256"] == PAYLOAD_SHA, "Pinned edit manifest")
    events = old["program"]
    previous = set()
    move_replace, remove, add_at, shifted = {}, set(), defaultdict(list), {}
    changed = []
    for plan in edit["plans"]:
        role = plan["role"]
        need(type(role) is int and role < old["public"], "Only public MOVE contractions")
        first, second = (m["index"] for m in plan["old_moves"])
        need(type(first) is int and type(second) is int and 0 <= first < second < len(events), "Two ordered MOVE indices")
        left, right = events[first], events[second]
        need(all(events[m["index"]] == m["event"] for m in plan["old_moves"]), "Bound source MOVE")
        need(left[:2] == right[:2] == ["MOVE", role] and left[3] == right[2]
             and left[4] is False and right[4] is False, "Public MOVE chain")
        a, b, c = left[2], left[3], right[3]
        need(spaces[a] < spaces[b] < spaces[c], "Three strict nested charts")
        middle = [i for i in history[role] if first < i < second]
        need(middle == [s["index"] for s in plan["slides"]], "Every stop contact must be moved exactly once")
        footprints = {role}
        cuts = []
        for slide in plan["slides"]:
            i, j, frame = slide["index"], slide["before_event"], slide["new_frame"]
            need(type(i) is int and type(j) is int and 0 <= j <= len(events), "Slide cut")
            need(events[i] == slide["event"] and events[i][0] == "ADD" and events[i][-1] == b, "Bound scalar opcode")
            need((j <= first and frame == a) or (j > second and frame == c), "Slide outside the vacated chart")
            need(i not in shifted, "Unique shifted ADD")
            footprints.update(roles(events[i]))
            cuts.append(j)
            shifted[i] = (j, 0, i)
            add_at[j].append((i, [*events[i][:-1], frame]))
        need(cuts == sorted(cuts), "Original contact order is retained")
        need(not (footprints & previous), "Disjoint changed operand sets")
        previous.update(footprints)
        move_replace[first] = ["MOVE", role, a, c, False]
        remove.add(second)
        changed.append({"role": role, "direct_chart_pair": [a, c],
                        "retired_chart_pairs": [[a, b], [b, c]], "operand_roles": sorted(footprints)})
    require_crossings = Counter()
    for i, new_key in shifted.items():
        touched = set().union(*(history[r] for r in roles(events[i])))
        for j in touched - {i}:
            other_key = shifted.get(j, (j, 1, j))
            if (i < j) == (new_key < other_key):
                continue
            need(commute(events[i], events[j]), ("Noncommuting relative-order change", i, j))
            require_crossings[events[j][0]] += 1
    new_program = []
    for i in range(len(events) + 1):
        new_program.extend(e for _, e in sorted(add_at.get(i, ())))
        if i < len(events) and i not in remove and i not in shifted:
            new_program.append(move_replace.get(i, events[i]))
    new = old | {"program": new_program}
    inventory(new, spaces)
    return new, dict(require_crossings), changed


def moves(word):
    dim = list(map(len, word["frames"]))
    return Counter(abs(dim[e[3]] - dim[e[2]]) for e in word["program"] if e[0] == "MOVE")


def controls(old, edit, spaces, history):
    changes = [
        ("missing stop contact", lambda p: p["slides"].clear(), "Every stop contact"),
        ("changed coefficient", lambda p: p["slides"][0]["event"].__setitem__(3, "1"), "Bound scalar opcode"),
        ("wrong target frame", lambda p: p["slides"][0].__setitem__("new_frame", 246), "vacated chart"),
        ("changed original MOVE", lambda p: p["old_moves"][1]["event"].__setitem__(2, 0), "Bound source MOVE"),
        ("illegal coframe after slide", lambda p: p["slides"][0].__setitem__("before_event", 43418), "Scalar chart"),
        ("crossed noncommuting source write", lambda p: p["slides"][0].__setitem__("before_event", 45545),
         "Noncommuting relative-order change"),
    ]
    passed = []
    for label, mutation, expected in changes:
        bad = deepcopy(edit)
        mutation(bad["plans"][0])
        try:
            place(old, bad, spaces, history)
        except ValueError as exc:
            need(expected in str(exc), (label, "Wrong failure reason", str(exc)))
        else:
            raise ValueError((label, "negative control passed"))
        passed.append(label)
    return passed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--edit", type=Path, default=HERE / "EDITS.json")
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()
    old = json.loads(gzip.decompress(args.source.read_bytes()))
    need(sha256(payload(old)).hexdigest() == PAYLOAD_SHA, "Pinned source word")
    edit = json.loads(args.edit.read_bytes())
    spaces = [span(basis) for basis in old["frames"]]
    history, _, _ = inventory(old, spaces)
    new, reordered, changed = place(old, edit, spaces, history)
    passed = controls(old, edit, spaces, history)
    paid_old, paid_new = moves(old), moves(new)
    paid_delta = paid_new.copy()
    paid_delta.subtract(paid_old)
    paid_delta = {r: n for r, n in sorted(paid_delta.items()) if n}
    need(paid_delta == {1: -7, 2: 2, 4: -3, 5: 3}, "Literal paid rank change")
    need(sum(r * n for r, n in paid_delta.items()) == 0, "Paid rank mass unchanged")
    need(all(new[k] == old[k] for k in old if k != "program"), "Boundary and hosted metadata unchanged")
    raw = payload(new)
    compressed = gzip.compress(raw, mtime=0)
    args.candidate.write_bytes(compressed)
    print(json.dumps({
        "source_head": HEAD, "source_canonical_sha256": PAYLOAD_SHA,
        "edit_sha256": sha256(args.edit.read_bytes()).hexdigest(),
        "candidate_canonical_sha256": sha256(raw).hexdigest(),
        "candidate_gzip_sha256": sha256(compressed).hexdigest(),
        "old_events": len(old["program"]), "new_events": len(new["program"]),
        "old_paid": dict(sorted(paid_old.items())), "new_paid": dict(sorted(paid_new.items())),
        "native_paid_delta": paid_delta, "native_target_delta": {}, "owned_change": {},
        "crossed_common_operand_events": reordered,
        "changed": changed, "controls": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
