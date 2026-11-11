"""Build the authenticated chart and role-contact index for exact #7314."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from time import monotonic

WORD = 'inputs/7314/WORD.json.gz'
WORD_SHA = 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9'


def word(root):
    raw = (root/WORD).read_bytes()
    if sha256(raw).hexdigest() != WORD_SHA:
        raise ValueError('Changed literal word')
    return loads(decompress(raw))


def helper_roles(w):
    main = set(w['live'])
    main |= {r+112 for r in w['live']}
    main.update(w['hosted']['X2'],w['hosted']['Y2'])
    assert len(main) == 400
    return sorted(set(range(w['public']))-main)


def spans(w):
    @cache
    def span(k):
        out = {0}
        for v in w['frames'][k]:
            assert v not in out
            out.update(v^a for a in tuple(out))
        return out
    return span


def build(w,deadline):
    pub = w['public']
    active = dict(enumerate(w['initial']))
    roles = defaultdict(list)
    counts, moves = Counter(), Counter()
    span = spans(w)
    complete = True
    for clock,e in enumerate(w['program']):
        if monotonic() >= deadline:
            complete = False
            break
        op,r,*a = e
        counts[op] += 1
        roles[r].append([clock,'destination'])
        if op == 'INIT':
            assert r >= pub and r not in active
            active[r] = a[0]
        elif op == 'CLEAR':
            assert r >= pub and active.pop(r) == a[0]
        elif op == 'MOVE':
            start,end,own = a
            assert active[r] == start and own == (r >= pub)
            assert span(start) < span(end) or (own and span(end) < span(start))
            moves[abs(len(w['frames'][start])-len(w['frames'][end]))] += 1
            active[r] = end
        elif op in ('ADD','COPY'):
            s = a[0]
            assert r != s and active[r] == active[s] == a[-1]
            roles[s].append([clock,'source'])
        else:
            assert op == 'SCALE' and active[r] == a[-1]
    if complete:
        assert active == dict(enumerate(w['final']))
    return {'word_sha256':WORD_SHA,'events_visited':sum(counts.values()),'complete':complete,
            'event_counts':dict(counts),'paid_native_moves':dict(moves),'roles':dict(roles)}


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    args = parser.parse_args()
    data = build(word(args.root),monotonic()+18)
    if data['complete']:
        assert data['events_visited'] == 76461
        assert sum(data['paid_native_moves'].values()) == 6280
    print(dumps(data,sort_keys=True,separators=(',',':')))
