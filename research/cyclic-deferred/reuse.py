"""Deterministic compensated birth-cut scratch reuse.

Birth-cut reuse follows jamesyc PR124. Composition with saturated deferrals
and physical hull frames prepared for eumemic with OpenAI Codex assistance.
Apache-2.0; inherited authorship remains in the surrounding package.
"""
from collections import defaultdict
from functools import lru_cache


def basis(vectors):
    piv = {}
    for x in vectors:
        for p in sorted(piv, reverse=True):
            if x >> p & 1:
                x ^= piv[p]
        if x:
            p = x.bit_length() - 1
            for q in piv:
                if piv[q] >> p & 1:
                    piv[q] ^= x
            piv[p] = x
    return tuple(piv[p] for p in sorted(piv, reverse=True))


def contained(A, B):
    return len(basis(tuple(A) + tuple(B))) == len(B)


def complement(A, h):
    A = basis(A)
    piv = {x.bit_length() - 1: x for x in A}
    out = []
    for j in range(h):
        if j not in piv:
            x = 1 << j
            for p, row in piv.items():
                if row >> j & 1:
                    x |= 1 << p
            out.append(x)
    return basis(out)


def nondeg(A):
    return len(basis(sum(((x & y).bit_count() & 1) << j
                         for j, y in enumerate(A)) for x in A)) == len(A)


def check_pairs(data, pairs):
    """Reject aliases, unfinished donors and unavailable recipient births."""
    donors = [row['donor'] for row in pairs]
    recipients = [row['recipient'] for row in pairs]
    assert (len(set(donors)) == len(donors) and
            len(set(recipients)) == len(recipients) and
            not set(donors) & set(recipients)), 'Reuse pair alias'
    early = set(data['Anc'])
    first = {}
    late_touched = set()
    for i, op in enumerate(data['ops']):
        if op[0] == 'src':
            first.setdefault(op[1], i)
            continue
        for s in op[1:3]:
            first.setdefault(s, i)
        if i not in early:
            late_touched.update(op[1:3])
    for row in pairs:
        a, b = row['donor'], row['recipient']
        assert type(a) is int and type(b) is int, 'Reuse role type'
        assert 0 <= a < data['R'] and 0 <= b < data['R'], 'Reuse role range'
        assert (a not in data['placed'] and a not in data['role_root'] and
                data['last'].get(a) in early and a not in late_touched), 'Reuse nondead donor'
        assert (b in data['placed'] and b not in data['leaf_of'] and
                b not in data['touched'] and first.get(b) not in early), 'Reuse unavailable birth'
        birth = data['ops'][first[b]]
        assert birth[0] == 'copy' and birth[2] == b, 'Reuse unavailable birth'
        A = basis(data['op_frames'][data['last'][a]])
        F = basis(data['placed'][b])
        B = basis(data['op_frames'][first[b]])
        assert nondeg(A) and nondeg(F) and nondeg(B), 'Reuse degenerate frame'
        assert contained(A, F) and contained(F, B), 'Reuse frame containment'
        assert basis(row['donor_frame']) == A and basis(row['birth_frame']) == F, 'Reuse recorded frames'
        assert (row['e'], row['s']) == (len(A), len(F)), 'Reuse recorded dimensions'
    return dict(zip(recipients, donors))


def check_compensation(merge, compensated):
    assert set(merge) <= set(compensated), 'Reuse omitted compensation'


def select_reuse(data):
    groups = defaultdict(list)
    for a, i in data['last'].items():
        if i in data['Anc'] and a not in data['role_root']:
            A = basis(data['op_frames'][i])
            assert nondeg(A)
            groups[A].append(a)
    frames = sorted(groups, key=lambda F: (-len(F), F))
    pool = [groups[F][:] for F in frames]
    births = defaultdict(list)
    for b, F in data['placed'].items():
        if b not in data['leaf_of']:
            births[basis(F)].append(b)
    allgroups = (1 << len(frames)) - 1

    @lru_cache(None)
    def annihilated(q):
        return sum(1 << i for i, A in enumerate(frames)
                   if all(not ((a & q).bit_count() & 1) for a in A))

    eligible, capacity = {}, {}
    for F in births:
        mask = allgroups
        for q in complement(F, data['h']):
            mask &= annihilated(q)
            if not mask:
                break
        eligible[F] = mask
        capacity[F] = sum(len(pool[i]) for i in range(len(frames)) if mask >> i & 1)
    available, pairs = allgroups, []
    for F in sorted(births, key=lambda F: (capacity[F], len(F), F)):
        for b in sorted(births[F]):
            mask = eligible[F] & available
            if not mask:
                break
            i = (mask & -mask).bit_length() - 1
            a = pool[i].pop()
            A = frames[i]
            if not pool[i]:
                available ^= 1 << i
            pairs.append(dict(donor=a, recipient=b, donor_frame=A,
                              birth_frame=F, e=len(A), s=len(F)))
    check_pairs(data, pairs)
    return pairs


def mutation_controls(data, pairs):
    """Mutate the actual selected finite pairing, not a synthetic inventory."""
    import copy
    rejected = []
    occupied = {row[key] for row in pairs for key in ('donor', 'recipient')}
    for failure in ('nondead-donor', 'unavailable-birth', 'pair-alias'):
        changed = copy.deepcopy(pairs)
        if failure == 'nondead-donor':
            changed[0]['donor'] = next(s for s in data['role_root'] if s not in occupied)
        elif failure == 'unavailable-birth':
            changed[0]['recipient'] = next(s for s in data['leaf_of'] if s not in occupied)
        else:
            changed[0]['recipient'] = changed[0]['donor']
        try:
            check_pairs(data, changed)
        except AssertionError as error:
            expected = {'nondead-donor': 'nondead donor',
                        'unavailable-birth': 'unavailable birth',
                        'pair-alias': 'pair alias'}[failure]
            assert expected in str(error), (failure, error)
            rejected.append(failure)
        else:
            raise AssertionError('Accepted reuse mutation: ' + failure)
    merge = check_pairs(data, pairs)
    try:
        check_compensation(merge, set(merge) - {pairs[0]['recipient']})
    except AssertionError:
        rejected.append('omitted-compensation')
    else:
        raise AssertionError('Accepted omitted birth compensation')
    return rejected
