# SPDX-License-Identifier: Apache-2.0
"""Proof checks added to Ali Romman's #7605 application for the #7611 chart-1062 component.
Retained compiler, interpreter, and application keep their original authors and attribution.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json


def digest(blob):
    return sha256(blob).hexdigest()


def differences(left, right):
    out = Counter(left)
    out.subtract(right)
    return {key: n for key, n in out.items() if n}


def reconstruct(base, edits):
    tape = base['program']
    deletes = dict(edits['delete'])
    inserts = dict(edits['insert_before'])
    assert len(deletes) == len(edits['delete']) and len(inserts) == len(edits['insert_before'])
    assert not edits['append'] and edits.get('base_events', len(tape)) == len(tape)
    assert all(type(i) is int and 0 <= i < len(tape) and tape[i] == e for i, e in deletes.items())
    assert all(type(i) is int and 0 <= i < len(tape) for i in inserts)
    added, tagged = 0, []
    for i, old in enumerate(tape):
        for event in inserts.get(i, ()):
            added += 1
            tagged.append((-added, event))
        if i not in deletes:
            tagged.append((i, old))
    return tagged


def routes(word):
    out = [[] for _ in range(word['public'])]
    for op in word['program']:
        if op[0] == 'MOVE' and not op[4]:
            out[op[1]].append(tuple(op[2:4]))
    return out


def chart_contract(base, word):
    old, new = routes(base), routes(word)
    bypasses = {82:(740, 1062, 1071), 185:(401, 1062, 922)}
    changed = [i for i in range(base['public']) if old[i] != new[i]]
    assert changed and set(changed) <= set(bypasses)
    paid = Counter()
    for role in changed:
        a,b,c = bypasses[role]
        at = old[role].index((a,b))
        assert old[role][at:at+2] == [(a,b),(b,c)]
        assert old[role][:at] + [(a,c)] + old[role][at+2:] == new[role]
        dims = [len(base['frames'][x]) for x in (a,b,c)]
        for rank, charge in ((dims[2]-dims[0],1),(dims[1]-dims[0],-1),(dims[2]-dims[1],-1)):
            assert rank > 0
            paid[rank] += charge
    return [bypasses[i] for i in changed], {r:v for r,v in paid.items() if v}


def inspect_owned_contacts(base, word, tagged, audit):
    original = list(enumerate(base['program']))
    def protected(items):
        result = {}
        for i,e in items:
            operands = e[1:3] if e[0] in ('ADD','COPY') else e[1:2]
            if any(r >= base['public'] for r in operands):
                result[i] = e
        return result
    contacts = protected(original)
    assert list(contacts.items()) == list(protected(tagged).items()), 'All owned operand clocks and literal events'
    checked = {i for i,e in contacts.items() if e[0] in ('ADD','COPY','SCALE')}
    before, base_grid = audit.replay(base, original, checked)
    after, grid = audit.replay(word, tagged, checked)
    assert len(before[0]) == 1569 and len(before[2]) == 74
    assert before == after, 'Exact endpoints, protected source versions, all ordered erasures, guarded COPY products, owned lifetimes and owned MOVE events'
    return after, grid, before, checked


def physical(v, recipes, triples):
    counts = []
    for a,b,c in triples:
        via = recipes[a,b] + recipes[b,c]
        direct = recipes[a,c]
        for left,right in ((via,direct),(v.adjoint(via),v.adjoint(direct))):
            v.equal(left,right,'Composed signed action and absolute phase')
            for column in range(512):
                assert v.state(left,column) == v.state(right,column), 'All composed Gaussian columns'
        counts.append({'frames':[a,b,c], 'forward_columns':512, 'adjoint_columns':512})
    return counts


def negatives(word, tagged, baseline, checked, audit, native, rejects, triples):
    controls = {}
    for a,b,c in triples:
        event = next(e for e in word['program'] if e[0] == 'MOVE' and not e[4] and e[2:4] == [a,c] and e[1] in (82,185))
        assert word['program'].count(event) == 1
        role = event[1]
        for fault in ('missing', 'wrong_source'):
            bad = deepcopy(word)
            idx = bad['program'].index(event)
            if fault == 'missing':
                del bad['program'][idx]
            else:
                bad['program'][idx][2] = b
            controls[f'{fault}_role_{role}_direct_move'] = rejects(lambda: native(bad))
    scalar_index = next(i for i,(origin,e) in enumerate(tagged) if origin < 0 and e[:2] == ['ADD',185])
    mutant = tagged[:scalar_index]+tagged[scalar_index+1:]
    def check_removed():
        result, _ = audit.replay(dict(word,program=[e for _,e in mutant]), mutant, checked)
        assert result == baseline, 'Exact protected rows and return functions'
    controls['removed_role185_compensation'] = rejects(check_removed)
    return controls
