"""Both-orientation extended-label audit, adapting credited PR2048's audit.

All ordinary columns are exact. Captures the actual private pre-transport cuts,
including the backward gather, without imposing the forward scatter grammar.
"""
from collections import Counter
from fractions import Fraction as Q
from source import need

def add(dst, src, coefficient):
    for i, v in list(src.items()):
        w = dst.get(i, Q(0)) + coefficient*v
        if w:
            dst[i] = w
        else:
            dst.pop(i, None)

def audit(word, events, orientation):
    v, n = word['v'], 2*word['v'] + word['R']
    need((word['h'], v, n) == (9, 112, 704), 'selected dimensions')
    wrapped = {i for i in range(2*v, n) if (word['start'][i], word['final'][i]) != (0, 1)}
    labels = {('L', i): ('preS', i) if i < v else ('preW', i) if i in wrapped
              else ('T', word['start'][i]) for i in range(n)}
    rows = {('L', i): {i: Q(1)} for i in range(n)}
    phases, conversions, edges, bill, cuts = [], Counter(), set(), Counter(), {}
    private = set()
    phase = None
    for e in events:
        tag = e[0]
        if tag == 'phase':
            phase = e[1]
            phases.append(phase)
        elif tag == 'climb':
            _, part, r, old, new, rank = e
            need(part == phase and labels['L', r] == ('T', old), 'climb source frame')
            need(rank == len(word['frames'][new])-len(word['frames'][old]) > 0, 'climb rank')
            labels['L', r] = ('T', new)
            edges.add((old, new, rank))
        elif tag == 'center':
            _, k, old, new, rank = e
            need(phase == 'centers' and labels.get(('C', k)) == ('T', old), 'centre source frame')
            need(k not in cuts, 'unique centre cut')
            need((old, new) == ((word['center_frames'][k], 0) if orientation == 'forward'
                                else (0, word['center_frames'][k])), 'centre direction')
            need(abs(len(word['frames'][old])-len(word['frames'][new])) == rank == 8, 'centre rank')
            cuts[k] = dict(rows['C', k])
            labels['C', k] = ('T', new)
            edges.add((old, new, rank))
            bill['rank8'] += 1
        elif tag == 'adapter':
            _, direction, r, frame = e
            need(direction in ('old_to_new', 'new_to_old'), 'adapter direction')
            conversions[direction, r] += 1
            if direction == 'old_to_new':
                need(phase == 'entry_adapters' and frame == word['start'][r], 'entry adapter')
                if r < v:
                    need(labels['L', r] == ('preS', r), 'source conversion label')
                    labels['L', r] = ('T', frame)
                else:
                    need(labels['L', r] == ('T', 0) and frame == 0, 'identity entry')
            else:
                need(phase == 'exit_adapters' and frame == word['final'][r], 'exit adapter')
                need(labels['L', r] == ('T', frame), 'exit conversion frame')
                if v <= r < 2*v:
                    labels['L', r] = ('postT', r)
                else:
                    need(frame == 1, 'identity exit')
        elif tag == 'residual_adapter':
            direction, r, a = e[1:4]
            b = e[4] if len(e) == 5 else 1
            need(len(e) in (4, 5), 'wrapper syntax')
            need(r in wrapped and (a, b) == (word['start'][r], word['final'][r]), 'wrapper binding')
            need(direction in ('pre', 'post'), 'wrapper direction')
            conversions[direction, r] += 1
            if direction == 'pre':
                need(phase == 'entry_adapters' and labels['L', r] == ('preW', r), 'pre-wrapper label')
                labels['L', r] = ('T', a)
            else:
                need(phase == 'full_frame_cleanup' and labels['L', r] == ('T', b), 'post-wrapper label')
                labels['L', r] = ('doneW', r)
        elif tag == 'scalar':
            _, op, frame = e
            kind, dest = op[0], tuple(op[1])
            if dest[0] == 'C' and dest not in private:
                need(kind == 'clear', 'private initialization')
                private.add(dest)
            if phase == 'centers':
                bill[kind] += 1
            if kind == 'clear':
                need(dest[0] == 'C', 'only private clears')
                rows[dest] = {}
                labels[dest] = ('T', frame)
            elif kind == 'copy':
                src = tuple(op[2])
                need(dest[0] == 'C' and labels[src] == ('T', frame), 'copy frame')
                need(orientation == 'forward' and phase == 'centers'
                     and src == ('L', word['centers'][dest[1]]), 'centre copy binding')
                rows[dest] = dict(rows[src])
                labels[dest] = ('T', frame)
            elif kind == 'scale':
                need(labels[dest] == ('T', frame), 'scale frame')
                q = Q(op[2], op[3])
                need(q != 0, 'invertible scale')
                rows[dest] = {i: q*x for i, x in rows[dest].items()}
            elif kind == 'add':
                src = tuple(op[2])
                need(dest != src and labels[dest] == labels[src] == ('T', frame), 'common frame')
                add(rows[dest], rows[src], Q(op[3], op[4]))
            else:
                raise ValueError('unknown scalar')
        else:
            raise ValueError('unknown event')
    need(phases == ['zero_frame_precondition', 'entry_adapters', 'A', 'centers', 'B',
                    'cleanup_tail', 'final', 'exit_adapters', 'full_frame_cleanup', 'done'], 'phase order')
    expected_conversions = Counter()
    for i in range(n):
        if i in wrapped:
            expected_conversions['pre', i] = expected_conversions['post', i] = 1
        else:
            expected_conversions['old_to_new', i] = 1
        if i < 2*v or word['final'][i] == 1:
            expected_conversions['new_to_old', i] = 1
        final = (('T', 1) if i < v else ('postT', i) if i < 2*v else
                 ('doneW', i) if i in wrapped else ('T', 1))
        need(labels['L', i] == final, 'final extended label')
        expected = {i: Q(1)}
        if orientation == 'forward' and v <= i < 2*v:
            expected[i-v] = Q(1)
        if orientation == 'backward' and i < v:
            expected[i+v] = Q(-1)
        need(rows['L', i] == expected, 'complete scalar endpoint')
    need(conversions == expected_conversions, 'complete conversion inventory')
    need(private == {('C', i) for i in range(8)} and set(cuts) == set(range(8)), 'private inventory')
    need(all(not row for r, row in rows.items() if r[0] == 'C'), 'private exit')
    expected_bill = Counter(add=176, copy=8, clear=16, rank8=8) if orientation == 'forward' else Counter(add=184, clear=16, rank8=8)
    need(bill == expected_bill, 'unchanged phase invoice')
    return {'cuts': [cuts[k] for k in range(8)], 'edges': edges, 'wrapped': wrapped,
            'events': len(events), 'bill': dict(bill), 'scalar_columns': n, 'conversions': len(conversions)}
