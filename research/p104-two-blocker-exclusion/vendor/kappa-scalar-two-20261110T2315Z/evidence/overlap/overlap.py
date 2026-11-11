"""Five-factor exact packet for the final overlapping rank-one cases."""
from bisect import bisect_right
from collections import Counter, defaultdict
from fractions import Fraction as Q
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_spec = spec_from_file_location('overlap_two', Path(__file__).parents[1]/'planner/two_blockers.py')
two = module_from_spec(_spec)
_spec.loader.exec_module(two)


def normalized(event, inverse=False):
    op, *roles = event[:-2]
    coefficient = Q(event[-2])
    if inverse:
        coefficient = -coefficient if op == 'ADD' else 1/coefficient
    return op, *roles, str(coefficient)


def choices_overlap(word, raw, scalar, child, stats=None):
    stats = Counter() if stats is None else stats
    program, public = word['program'], word['public']
    history = two.contacts(program)
    visits = defaultdict(list)
    for j,(role,event,_) in enumerate(raw):
        visits[role].append((event+1,j))
    for h in visits.values():
        h.sort()
    end = len(raw)

    def visit(role,cut):
        h = visits[role]
        return h[bisect_right(h,(cut,end))-1][1]

    for i in scalar:
        a = program[i]
        if i not in child or a[0]!='ADD' or max(two.axes(a))>=public:
            continue
        d,s = two.axes(a)
        for later in (False,True):
            b1,one = two.next_contact(program,history,i,{d:Q(a[3])},{s:Q(1)},later)
            if one is None or max(two.axes(program[b1]))>=public:
                continue
            b2,two_step = two.next_contact(program,history,b1,*one,later)
            if two_step is None or max(two.axes(program[b2]))>=public:
                continue
            if not two_step[0].keys() & two_step[1].keys():
                continue
            stats['overlapping plans'] += 1
            p,q = program[b1],program[b2]
            ops = (normalized(q,later),normalized(p,later),normalized(a),
                   normalized(p,not later),normalized(q,not later))
            if not all(two.coefficient_admissible(Q(e[-1])) for e in ops):
                stats['inadmissible coefficient plans'] += 1
                continue
            stop,_ = two.next_contact(program,history,b2,*two_step,later)
            lo,hi = (b2+1,stop) if later else (stop+1,b2)
            cuts = {lo}
            for role in {r for e in ops for r in two.axes(e)}:
                h=visits[role]
                x,y=bisect_right(h,(lo,end)),bisect_right(h,(hi,end))
                cuts.update(cut for cut,_ in h[x:y])
            for cut in sorted(cuts):
                pairs = tuple((visit(e[1],cut),visit(e[2] if e[0]=='ADD' else e[1],cut)) for e in ops)
                stats['placements'] += 1
                yield i,(b1,b2),cut,ops,pairs,(cut,)*len(ops)
