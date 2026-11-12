"""Exact full-interval controls for the separately placed elementary term."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

from free_term import choices_free, term_window, two
from validate import exact_rows, inventory, read_word


def local_sequences(program, original, operations, cuts):
    insert = defaultdict(list)
    for cut, op in zip(cuts, operations):
        insert[cut].append(op)
    lo = min(original, *cuts)
    hi = max(original+1, *cuts)
    after = []
    for i in range(lo, hi+1):
        after.extend(insert[i])
        if i < hi and i != original:
            after.append(program[i])
    return program[lo:hi], after


def run(path):
    w = read_word(path)
    raw, scalar, child = inventory(w)
    program = w['program']
    history = two.contacts(program)
    stats, longest = Counter(), {}
    bad = None
    for candidate in choices_free(w, raw, scalar, child, stats):
        add, blockers, joint, ops, pairs, cuts = candidate
        terms = [j for j, cut in enumerate(cuts) if cut != joint]
        assert len(terms) == 1
        term, = terms
        k = cuts[term]
        for op, (a, b), cut in zip(ops, pairs, cuts):
            assert (raw[a][0], raw[b][0]) == op[1:3]
            assert max(raw[a][1], raw[b][1]) < cut
        direction = 'later' if blockers[0] > add else 'earlier'
        mode = 'term later' if k > joint else 'term earlier'
        before_len = max(add+1, *cuts)-min(add, *cuts)
        categories = [(direction, mode)]
        if min(k,joint) <= add < max(k,joint):
            categories.append((direction, 'crosses removed ADD'))
        for key in categories:
            if key not in longest or before_len > longest[key][0]:
                longest[key] = before_len, candidate
        if bad is None:
            lo, hi = term_window(program, history, add, joint, ops[term])
            for wrong_cut, blocker in ((lo-1,lo-1),(hi+1,hi)):
                if not 0 <= blocker < len(program) or program[blocker][0] not in ('ADD','SCALE'):
                    continue
                wrong = list(cuts)
                wrong[term] = wrong_cut
                before, after = local_sequences(program, add, ops, wrong)
                if exact_rows(before) != exact_rows(after):
                    bad = dict(add=add, joint=joint, term=term, blocker=blocker,
                               excluded_cut=wrong_cut, correct_cut=k)
                    break
    controls = []
    for (direction, mode), (n, (add, blockers, joint, ops, _, cuts)) in sorted(longest.items()):
        before, after = local_sequences(program, add, ops, cuts)
        assert len(before) == n and exact_rows(before) == exact_rows(after)
        controls.append(dict(direction=direction, mode=mode, add=add, blockers=blockers,
                             joint_cut=joint, cuts=cuts, original_events=n, ops=ops))
    assert bad is not None and len(controls) == 6
    return dict(status='PASS_EXACT_ONE_FREE_TERM_PLANNER', source_word_sha256=two.WORD_SHA,
                counts=stats, exact_full_intervals=controls, retained_blocker_control=bad)


if __name__ == '__main__':
    print(json.dumps(run(Path(sys.argv[1])), indent=2, sort_keys=True))
