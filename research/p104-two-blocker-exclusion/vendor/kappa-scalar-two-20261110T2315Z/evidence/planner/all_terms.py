"""Cartesian products of individually safe cuts for the expanded scalar ADD."""
from bisect import bisect_right
from collections import Counter, defaultdict
from itertools import product
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_spec = spec_from_file_location('free_term_core', Path(__file__).with_name('free_term.py'))
free = module_from_spec(_spec)
_spec.loader.exec_module(free)
two = free.two


def choices_all(word, raw, scalar, child, stats=None):
    """Yield add, blockers, joint anchor, ops, raw pairs, and per-term cuts."""
    stats = Counter() if stats is None else stats
    program = word['program']
    history = two.contacts(program)
    visits = defaultdict(list)
    for j, (role, event, _) in enumerate(raw):
        visits[role].append((event+1, j))
    for h in visits.values():
        h.sort()
    end = len(raw)

    def visit(role, cut):
        h = visits[role]
        return h[bisect_right(h,(cut,end))-1][1]

    for add, blockers, anchor, joint_end, ops in two.plans(word,scalar,child):
        stats['algebraic plans'] += 1
        options = []
        for op in ops:
            _, d, s, _ = op
            lo, hi = free.term_window(program, history, add, anchor, op)
            # A stationary scalar commuting with the disjoint-support rank-one
            # aggregate commutes with each elementary term separately.
            assert lo <= anchor <= joint_end <= hi
            cuts = {lo}
            for role in (d,s):
                h = visits[role]
                a,b = bisect_right(h,(lo,end)),bisect_right(h,(hi,end))
                cuts.update(cut for cut,_ in h[a:b])
            options.append([(cut,(visit(d,cut),visit(s,cut))) for cut in sorted(cuts)])
        for placements in product(*options):
            cuts,pairs = map(tuple,zip(*placements))
            stats['products'] += 1
            yield add, blockers, anchor, ops, pairs, cuts
