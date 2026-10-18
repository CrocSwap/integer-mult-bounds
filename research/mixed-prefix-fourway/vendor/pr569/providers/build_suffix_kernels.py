#!/usr/bin/env python3
"""Apply independently rechecked suffix-kernel recipes to a literal word.

Prepared with OpenAI Codex assistance. Apache-2.0. This constructor does not
certify phase semantics, physical hosting, or the resulting recurrence.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

from search_suffix_kernels import add, basis


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--recipe', type=Path, action='append', required=True)
    parser.add_argument('--gk-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert __debug__ and not args.out.exists()
    sys.path.insert(0, str(args.gk_dir.resolve()))
    import gk_word as g
    import gk_common as co
    g.V = co.V = 112
    g.DATA = co.DATA = 7168
    raw = gzip.decompress(args.word.read_bytes())
    word = json.loads(raw)
    old_profile = g.profile(word)
    old_widths = co.widths_of(word)
    recipes = [json.loads(path.read_text()) for path in args.recipe]
    assert all(recipe['part'] == 'B' for recipe in recipes)
    assert len({recipe['pivot'] for recipe in recipes}) == len(recipes)
    checks = []
    for recipe in sorted(recipes, key=lambda value: -value['index']):
        index, pivot = recipe['index'], recipe['pivot']
        frame = basis(tuple(recipe['frame']))
        assert 224 <= pivot < 728 and str(pivot) not in word['start_extra']
        assert not any(pivot in (event[1:3] if event[0] == 'add' else event[1:2])
                       for event in word['A'] + word['cut'] + word['B'][:index])
        columns = [{} for _ in range(728)]
        for target in range(112):
            columns[112 + target] = {target: Q(1)}
        for event in reversed(word['B'][index:]):
            if event[0] == 'add':
                add(columns[event[2]], columns[event[1]], Q(event[3], event[4]))
            else:
                columns[event[1]] = {t: q * Q(event[2], event[3])
                                     for t, q in columns[event[1]].items()}
        residual = columns[pivot].copy()
        gates = []
        for donor, coefficient in sorted(recipe['coefficients'].items(), key=lambda pair: int(pair[0])):
            donor, q = int(donor), Q(coefficient)
            assert donor != pivot and not 112 <= donor < 224
            assert q and not q.denominator & (q.denominator - 1)
            add(residual, columns[donor], -q)
            gates.append(['add', donor, pivot, -q.numerator, q.denominator, list(frame)])
        assert not residual, ('invalid exact suffix relation', pivot)
        word['B'][index:index] = gates
        word['start_extra'][str(pivot)] = list(frame)
        # Checking the full chain after each insertion also rejects interactions
        # with any previously applied kernel's donors and pivots.
        profile = g.profile(word)
        checks.append(dict(pivot=pivot, index=index, entrance_frame=frame,
                           inserted_gates=len(gates), suffix_relation_exact=True))
    word['cleanup'] = [g.inverse(event, g.FULL) for event in reversed(word['A'] + word['B'])
                       if not 112 <= event[1] < 224]
    profile = g.profile(word)
    widths = co.widths_of(word)
    delta = {r: profile[r] - old_profile[r] for r in set(profile) | set(old_profile)
             if profile[r] != old_profile[r]}
    assert sum(r * n for r, n in delta.items()) == sum(widths) - sum(old_widths)
    word['report']['local_profile'] = dict(profile)
    word['report']['entrance_rank'] = sum(9 - width for width in widths)
    word['report']['entering_helpers'] = sum(width < 9 for width in widths)
    args.out.mkdir(parents=True)
    encoded = g.dump(word)
    (args.out / 'FULL-WORD.json.gz').write_bytes(encoded)
    receipt = dict(status='PASS_EXACT_MULTIKERNEL_CONSTRUCTION',
                   source_content_sha256=hashlib.sha256(raw).hexdigest(),
                   word_content_sha256=hashlib.sha256(gzip.decompress(encoded)).hexdigest(),
                   checks=checks, inserted_gates=sum(check['inserted_gates'] for check in checks),
                   profile_before=dict(old_profile), profile_after=dict(profile),
                   profile_delta=delta, widths_before=dict(Counter(old_widths)),
                   widths_after=dict(Counter(widths)),
                   scope='Every suffix identity and all frame chains are rechecked after composition. '
                         'Full native, phase, hosting, invoice and recurrence checks remain separate.')
    (args.out / 'CONSTRUCTION.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
