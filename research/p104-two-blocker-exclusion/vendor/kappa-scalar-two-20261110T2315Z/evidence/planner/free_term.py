"""Allow one expanded ADD term to use a separate commuting cut."""
from bisect import bisect_right
from collections import Counter, defaultdict
from fractions import Fraction as Q
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_spec = spec_from_file_location('exact_two_blocker', Path(__file__).with_name('two_blockers.py'))
two = module_from_spec(_spec)
_spec.loader.exec_module(two)


def term_window(program, history, add, cut, operation):
    _, d, s, text = operation
    u, v = {d: Q(text)}, {s: Q(1)}

    def boundary(index, later):
        contact, _ = two.next_contact(program, history, index, u, v, later)
        if contact == add:
            contact, _ = two.next_contact(program, history, add, u, v, later)
        return contact

    return boundary(cut, False) + 1, boundary(cut-1, True)


def choices_free(word, raw, scalar, child, stats=None):
    """Yield one free term, with its cut appended in an aligned per-term tuple."""
    stats = Counter() if stats is None else stats
    program = word['program']
    contacts = two.contacts(program)
    histories = defaultdict(list)
    for j, (role, event, _) in enumerate(raw):
        histories[role].append((event+1, j))
    for history in histories.values():
        history.sort()
    end = len(raw)

    def visit(role, cut):
        h = histories[role]
        return h[bisect_right(h, (cut, end))-1][1]

    for add, blockers, joint_cut, ops, pairs in two.choices(word, raw, scalar, child):
        if len(ops) == 1:
            continue
        stats['eligible joint placements'] += 1
        for term, op in enumerate(ops):
            _, d, s, _ = op
            lo, hi = term_window(program, contacts, add, joint_cut, op)
            assert lo <= joint_cut <= hi
            cuts = {lo}
            for role in (d, s):
                h = histories[role]
                a, b = bisect_right(h, (lo, end)), bisect_right(h, (hi, end))
                cuts.update(cut for cut, _ in h[a:b])
            for cut in sorted(cuts):
                pair = visit(d, cut), visit(s, cut)
                if pair == pairs[term]:
                    continue
                new_pairs = (*pairs[:term], pair, *pairs[term+1:])
                new_cuts = (joint_cut,)*term + (cut,) + (joint_cut,)*(len(ops)-term-1)
                stats['one-free placements'] += 1
                stats['term earlier than joint cut' if cut < joint_cut else 'term later than joint cut'] += 1
                if min(cut,joint_cut) <= add < max(cut,joint_cut):
                    stats['term crosses original removed ADD'] += 1
                yield add, blockers, joint_cut, ops, new_pairs, new_cuts
