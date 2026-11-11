"""Compare both exact #7314 owned-lifetime inventories."""
from argparse import ArgumentParser
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path

REASONS = {
    'protected role': 'protected_owned_role',
    'no paid MOVE': 'no_paid_move',
    'no immediate ADD capture': 'no_immediate_nonzero_capture',
    'other lifetime contact': 'other_owned_contact',
    'no source ADD': 'no_source_add',
    'several read charts': 'mixed_use_charts',
    'read chart does not have higher rank': 'use_not_strictly_higher_rank',
    'survives': 'structural_only',
}


def compare(lead_path, reverse_path, word_path):
    lead_raw = lead_path.read_bytes()
    reverse_raw = reverse_path.read_bytes()
    word_raw = word_path.read_bytes()
    lead, reverse = json.loads(lead_raw), json.loads(reverse_raw)
    word = json.loads(decompress(word_raw))
    assert lead['complete'] and reverse['complete']
    assert lead['head'] == reverse['head'] and lead['price_sha256'] == reverse['price_sha256']
    assert lead['word_sha256'] == reverse['word_sha256'] == sha256(word_raw).hexdigest()
    assert lead['visited_events'] == reverse['visited_events'] == len(word['program']) == 76461
    assert lead['lifetimes'] == reverse['matched_lifetimes'] == 72
    assert lead['owned_move_histogram'] == reverse['owned_paid_histogram_visited']
    assert not (lead['open_lifetimes'] or reverse['unmatched_clear_keys'] or reverse['unresolved_lifetimes'])
    assert not (lead['survivors'] or reverse['survivors'])

    forward_contacts = {}
    inventory = run_path(str(Path(__file__).with_name('inventory.py')))['inventory']
    namespace = inventory.__globals__
    original_classify = namespace['classify']

    def capture_contacts(role, init, clear, contacts, ranks):
        identity = (role, init[0], clear[0])
        assert identity not in forward_contacts
        classified = []
        for clock, op, dest, source, _, _ in contacts:
            if op == 'MOVE':
                access = 'move'
            elif op == 'SCALE':
                access = 'unary'
            elif role == dest:
                access = 'destination'
            else:
                assert role == source and op in ('ADD', 'COPY')
                access = 'source'
            classified.append([clock, access])
        forward_contacts[identity] = classified
        return original_classify(role, init, clear, contacts, ranks)

    namespace['classify'] = capture_contacts
    generated = inventory(word, 72, 17)
    assert generated['complete'] and generated['decisions'] == lead['decisions']

    details = []
    for f, r in zip(lead['decisions'], reverse['rows'], strict=True):
        identity = (f['role'], f['init'], f['clear'])
        assert identity == (r['owner'], r['birth'], r['clear'])
        assert (f['initial_chart'], f['final_chart']) == (r['birth_chart'], r['clear_chart'])
        assert r['contacts'] == forward_contacts[identity]
        assert len(r['contacts']) == f['contacts']
        assert [m['clock'] for m in f['moves']] == r['move_clocks']
        assert [{k: m[k] for k in ('clock', 'rank')} for m in f['moves']] == r['moves']
        for move in f['moves']:
            assert word['program'][move['clock']] == ['MOVE', r['owner'], move['old'], move['new'], True]
        assert [row['clock'] for row in f['reads']] == r['use_clocks']
        for read in f['reads']:
            assert word['program'][read['clock']] == [
                'ADD', read['destination'], r['owner'], read['coefficient'], read['chart'],
            ]
        assert REASONS[f['decision']] == r['status']
        if f['capture'] == f['init'] + 1:
            assert r['capture_clock'] == f['capture']
            assert r['capture'] == word['program'][f['capture']]
        if r['status'] == 'use_not_strictly_higher_rank':
            assert len(f['moves']) == 1
            m = f['moves'][0]
            assert len(word['frames'][r['use_chart']]) < len(word['frames'][r['birth_chart']])
            assert m['old'] == r['birth_chart'] and m['new'] == r['use_chart']
            assert r['use_clocks'][0] == m['clock'] + 1
            details.append(dict(role=r['owner'], init=r['birth'], clear=r['clear'],
                                move_clock=m['clock'], move_rank=m['rank'],
                                birth_chart=r['birth_chart'], use_chart=r['use_chart'],
                                reads=f['reads']))

    assert {REASONS[k]: n for k, n in lead['dispositions'].items()} == reverse['status_counts']
    assert len(details) == 6 and len(forward_contacts) == 72
    copy_clock, = [i for i, event in enumerate(word['program']) if event[0] == 'COPY']
    copy_event = word['program'][copy_clock]
    copy_lifetime, = [row for row in reverse['rows']
                      if [copy_clock, 'destination'] in row['contacts']]
    assert copy_event[1] == copy_lifetime['owner']
    assert copy_clock == copy_lifetime['birth'] + 1 and not copy_lifetime['moves']
    return dict(head=lead['head'], lead_sha256=sha256(lead_raw).hexdigest(),
                reverse_sha256=sha256(reverse_raw).hexdigest(), lifetimes_compared=72,
                contact_accesses_compared=sum(map(len, forward_contacts.values())),
                owned_paid_histogram=lead['owned_move_histogram'], strictly_lower_near_cases=details,
                unresolved=0, structural_survivors=0, compatible_saving_upper='0')


if __name__ == '__main__':
    assert __debug__
    p = ArgumentParser(description=__doc__)
    p.add_argument('lead', type=Path)
    p.add_argument('reverse', type=Path)
    p.add_argument('word', type=Path)
    args = p.parse_args()
    print(json.dumps(compare(args.lead, args.reverse, args.word), sort_keys=True, indent=2))
