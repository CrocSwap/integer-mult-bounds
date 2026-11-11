"""Forward literal first-contact and nesting screen for public helpers."""

from argparse import ArgumentParser
from collections import Counter
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from time import monotonic

HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
WORD = 'inputs/7314/WORD.json.gz'
PIN = 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9'
EXCLUDE = {863, 1355, 1568}


def unique(items):
    result = dict(items)
    if len(items) != len(result):
        raise ValueError('Duplicate JSON key')
    return result


def roles(word):
    main = set(word['live'])
    main |= {i + 112 for i in word['live']}
    main.update(word['hosted']['X2'], word['hosted']['Y2'])
    assert len(main) == 400
    return sorted(set(range(word['public'])) - main)


def scan(word, helpers, deadline, excluded):
    first = {}
    labels = dict(enumerate(word['initial']))
    frames = word['frames']
    tape = word['program']

    @cache
    def span(index):
        subspace = {0}
        for bit in frames[index]:
            assert bit not in subspace
            subspace.update(bit ^ value for value in tuple(subspace))
        return subspace

    for i, event in enumerate(tape):
        if monotonic() >= deadline:
            return {'events': i, 'unvisited_roles': helpers, 'rows': []}
        op, dest, *args = event
        if op == 'INIT':
            assert dest >= word['public'] and dest not in labels
            labels[dest] = args[0]
        elif op == 'CLEAR':
            assert dest >= word['public'] and labels.pop(dest) == args[0]
        elif op == 'MOVE':
            a, b, owned = args
            assert labels[dest] == a and owned == (dest >= word['public'])
            labels[dest] = b
            first.setdefault(dest, (i, op, 'destination', a, b))
        elif op in ('ADD','COPY'):
            src = args[0]
            assert labels[dest] == labels[src] == args[-1] and src != dest
            first.setdefault(dest, (i, op, 'destination'))
            first.setdefault(src, (i, op, 'source'))
        else:
            assert op == 'SCALE' and labels[dest] == args[-1]
            first.setdefault(dest, (i, op, 'destination'))
    assert labels == dict(enumerate(word['final']))

    rows = []
    for role in helpers:
        if len(rows) == 1101 or monotonic() >= deadline:
            break
        a, z = word['initial'][role], word['final'][role]
        rank = len(frames[z]) - len(frames[a])
        event = first.get(role)
        assert rank >= 1 and span(a) < span(z)
        if role in excluded:
            status = 'excluded_role'
        elif rank < 2:
            status = 'rank_one_target'
        elif not event or event[1] != 'MOVE':
            status = 'first_contact_not_move'
        else:
            _, _, _, old, b = event
            assert old == a
            rank_one = len(frames[b]) == len(frames[a]) + 1
            status = 'survivor' if rank_one and span(a) < span(b) < span(z) else 'move_rank_or_nesting'
        rows.append({'role': role, 'initial': a, 'final': z, 'rank': rank,
                     'first': event, 'status': status})
    return {'events': len(tape), 'unvisited_roles': helpers[len(rows):], 'rows': rows}


def controls():
    sample = {'public':2, 'initial':[0,0], 'final':[2,0], 'frames':[[],[1],[1,2]],
              'program':[['MOVE',0,0,1,False],['MOVE',0,1,2,False]]}
    a = scan(sample,[0],float('inf'),set())['rows'][0]
    altered = sample | {'program':[['ADD',1,0,'1',0],*sample['program']]}
    b = scan(altered,[0],float('inf'),set())['rows'][0]
    assert a['status'] == 'survivor' and b['status'] == 'first_contact_not_move' and b['first'][2] == 'source'
    return ['nested_rank_two', 'earlier_source_contact']


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--price-sha', required=True)
    args = parser.parse_args()
    deadline = monotonic() + 18
    price = (args.root / 'PRICE.json').read_bytes()
    assert sha256(price).hexdigest() == args.price_sha
    pre = loads(price, object_pairs_hook=unique)
    assert pre['head'] == HEAD and pre['input_sha256'][WORD] == PIN
    raw = (args.root / WORD).read_bytes()
    if sha256(raw).hexdigest() != PIN:
        raise ValueError('Changed literal word')
    word = loads(decompress(raw), object_pairs_hook=unique)
    check = controls()
    helpers = roles(word)
    assert len(helpers) == 1101
    result = scan(word, helpers, deadline, EXCLUDE)
    rows = result['rows']
    if not result['unvisited_roles']:
        assert Counter(str(r['rank']) for r in rows) == pre['helpers']
    result.update({'head':HEAD, 'price_sha256':args.price_sha, 'word_sha256':PIN,
                   'controls':check, 'counts':dict(Counter(r['status'] for r in rows)),
                   'survivors':[r for r in rows if r['status']=='survivor']})
    print(dumps(result, sort_keys=True, indent=2))
