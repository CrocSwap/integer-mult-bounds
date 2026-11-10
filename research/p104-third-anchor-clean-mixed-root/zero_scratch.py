"""Exact zero-scratch exit check for declared (field, frame, count) obligations.

Written by the Claude Sonnet 5.5 main session for Erwan L. (Apache-2.0) as an independent re-implementation
of the check described in the PR6399/PR6417 sources (read, not executed): exact sparse Fraction rows over
all roles, every scalar event applied exactly, every declared CLEAR must find its row exactly zero, and
the number of declared CLEAR sites must equal the declared count.
"""
from collections import Counter
from fractions import Fraction as Q


def verify(word, obligations):
    n = word['public'] + word['owned_fields']
    rows = [{i: Q(1)} if i < word['public'] else {} for i in range(n)]
    expected = {(int(x['field']), int(x['frame'])): int(x['count']) for x in obligations}
    counts, sites = Counter(), []
    for t, e in enumerate(word['program']):
        op, d = e[:2]
        if op == 'MOVE':
            continue
        if op in ('INIT', 'CLEAR'):
            if op == 'CLEAR' and (d, e[2]) in expected:
                if rows[d]:
                    raise ValueError('Declared scratch not exactly zero before erasure at event ' + str(t))
                counts[d, e[2]] += 1
                sites.append(t)
            rows[d] = {}
            continue
        q = Q(e[-2])
        if q.denominator & (q.denominator - 1):
            raise ValueError('Non-dyadic scalar')
        if op == 'SCALE':
            rows[d] = {i: q * x for i, x in rows[d].items() if q * x}
        elif op in ('ADD', 'COPY'):
            s = e[2]
            row = {} if op == 'COPY' else dict(rows[d])
            for i, x in rows[s].items():
                z = row.get(i, 0) + q * x
                if z:
                    row[i] = z
                else:
                    row.pop(i, None)
            rows[d] = row
        else:
            raise ValueError('Unknown scalar opcode')
    if dict(counts) != expected:
        raise ValueError('Declared zero-scratch exit inventory differs')
    return dict(method='Exact sparse Fraction rows over all roles', all_input_columns=n,
                zero_owned_clear_sites=sites, obligations=obligations)
