"""Audit exact INIT/ADD, paid MOVE, source ADD and CLEAR lifetime stock."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
WORD = '7314/WORD.json.gz'
CALLER = '7113/CALLER.json'
PINS = {
    WORD: 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9',
    CALLER: '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
}
PROTECTED = {863, 1355, 1568}
LIFETIME_CAP = 72


def decode(raw):
    def unique(pairs):
        obj = dict(pairs)
        if len(obj) != len(pairs):
            raise ValueError('Duplicate JSON key')
        return obj

    return loads(raw, object_pairs_hook=unique)


def classify(owner, birth, clear, contacts, tape, move_ranks, dimensions):
    all_moves = [clock for clock, access in contacts if access == 'move']
    uses = [clock for clock, access in contacts if access == 'source' and tape[clock][0] == 'ADD']
    chart = tape[birth][-1]
    capture = tape[birth + 1]
    row = dict(owner=owner, birth=birth, clear=clear, birth_chart=chart,
               clear_chart=tape[clear][-1], capture_clock=birth+1,
               capture=capture, contacts=contacts, move_clocks=all_moves,
               move_ranks=dict(Counter(move_ranks[clock] for clock in all_moves)), use_clocks=uses,
               moves=[dict(clock=clock, rank=move_ranks[clock]) for clock in all_moves],
               protected_contacts=[clock for clock, _ in contacts
                                   if any(r in PROTECTED for r in tape[clock][1:3]
                                          if isinstance(r, int))
                                   and tape[clock][0] in ('ADD', 'COPY')])
    if owner in PROTECTED:
        status = 'protected_owned_role'
    elif not all_moves:
        status = 'no_paid_move'
    elif not (capture[0] == 'ADD' and capture[1] == owner and Fraction(capture[3])
              and capture[2] != owner and capture[4] == chart and contacts[0] == (birth+1, 'destination')):
        status = 'no_immediate_nonzero_capture'
    elif any(access != 'move' and not (access == 'source' and tape[clock][0] == 'ADD')
             for clock, access in contacts[1:]):
        status = 'other_owned_contact'
    elif not uses:
        status = 'no_source_add'
    else:
        use_charts = {tape[clock][-1] for clock in uses}
        if len(use_charts) != 1:
            status = 'mixed_use_charts'
        else:
            z, = use_charts
            row['use_chart'] = z
            if dimensions[z] <= dimensions[chart]:
                status = 'use_not_strictly_higher_rank'
            else:
                status = 'structural_only'
    return row | {'status': status}


def audit(word, deadline, lifetime_cap):
    public = word['public']
    frames = word['frames']
    dims = [len(basis) for basis in frames]

    @cache
    def span(chart):
        vectors = {0}
        for v in frames[chart]:
            assert v not in vectors, 'dependent chart basis'
            vectors.update(x ^ v for x in tuple(vectors))
        return frozenset(vectors)

    state = dict(enumerate(word['final']))
    tape = word['program']
    opened = {}
    decisions = []
    move_ranks = {}
    paid_owned = Counter()
    paid_all = Counter()
    visited = 0
    for clock in range(len(tape)-1, -1, -1):
        if monotonic() >= deadline or len(decisions) >= lifetime_cap and lifetime_cap < LIFETIME_CAP:
            break
        visited += 1
        event = tape[clock]
        op, dest, *args = event
        if op == 'CLEAR':
            chart, = args
            assert dest >= public and dest not in state and dest not in opened
            state[dest] = chart
            opened[dest] = (clock, [])
            continue
        if op == 'INIT':
            chart, = args
            assert dest >= public and state.pop(dest) == chart
            clear, contacts = opened.pop(dest)
            assert len(decisions) < lifetime_cap, 'more owned lifetimes than declared'
            decisions.append(classify(dest, clock, clear, list(reversed(contacts)), tape, move_ranks, dims))
            continue
        if op == 'MOVE':
            start, end, owned = args
            assert state[dest] == end and owned == (dest >= public)
            assert span(start) < span(end) or owned and span(end) < span(start), 'invalid MOVE nesting'
            size = abs(dims[end] - dims[start])
            paid_all[size] += 1
            if owned:
                paid_owned[size] += 1
                move_ranks[clock] = size
            state[dest] = start
            contacts = ((dest, 'move'),)
        else:
            assert op in ('ADD', 'COPY', 'SCALE') and Fraction(args[-2])
            if op in ('ADD', 'COPY'):
                assert args[0] != dest
                assert op != 'COPY' or dest >= public
                contacts = ((dest, 'destination'), (args[0], 'source'))
            else:
                contacts = ((dest, 'unary'),)
            assert all(state[r] == args[-1] for r, _ in contacts)
        for role, access in contacts:
            if role >= public:
                opened[role][1].append((clock, access))

    complete = visited == len(tape)
    if complete:
        assert state == dict(enumerate(word['initial'])) and not opened
    decisions.sort(key=lambda row: row['birth'])
    structural = [row for row in decisions if row['status'] == 'structural_only']
    survivors = [dict(role=row['owner'], init=row['birth'], capture=row['capture_clock'],
                      clear=row['clear'], moves=row['moves'], birth_chart=row['birth_chart'],
                      use_chart=row['use_chart'], use_clocks=row['use_clocks']) for row in structural]
    return dict(complete=complete, visited_events=visited, literal_events=len(tape),
                first_unvisited_reverse_clock=None if complete else len(tape)-visited-1,
                matched_lifetimes=len(decisions),
                unmatched_clear_keys=sorted([r, entry[0]] for r, entry in opened.items()),
                all_paid_histogram_visited=dict(paid_all), owned_paid_histogram_visited=dict(paid_owned),
                status_counts=dict(Counter(row['status'] for row in decisions)), rows=decisions,
                structural_survivors=structural, survivors=survivors)


def controls():
    word = dict(public=2, frames=[[], [1], [1, 2]], initial=[0, 1], final=[0, 1],
                program=[['INIT',2,0], ['ADD',2,0,'-1/2',0], ['MOVE',2,0,1,True],
                         ['ADD',1,2,'3',1], ['CLEAR',2,1]])
    data = audit(word, float('inf'), LIFETIME_CAP)
    assert data['complete'] and len(data['structural_survivors']) == 1
    one = data['structural_survivors'][0]
    assert (one['birth'],one['capture_clock'],one['clear'],one['use_chart']) == (0,1,4,1)
    assert one['move_ranks'] == {1:1} and one['use_clocks'] == [3]
    write = ['ADD',2,1,'-1',1]
    changed = word | {'program':word['program'][:3]+[write]+word['program'][3:]}
    assert audit(changed,float('inf'),LIFETIME_CAP)['rows'][0]['status'] == 'other_owned_contact'
    changed = word | {'program':word['program'][:1]+[['SCALE',0,'2',0]]+word['program'][1:]}
    assert audit(changed,float('inf'),LIFETIME_CAP)['rows'][0]['status'] == 'no_immediate_nonzero_capture'
    changed = word | {'program':word['program'][:3]+word['program'][4:]}
    assert audit(changed,float('inf'),LIFETIME_CAP)['rows'][0]['status'] == 'no_source_add'
    changed = word | {'program':word['program']+word['program']}
    result = audit(changed,float('inf'),LIFETIME_CAP)
    assert result['complete'] and [r['birth'] for r in result['structural_survivors']] == [0,5]
    capped = audit(changed,float('inf'),1)
    assert not capped['complete'] and capped['matched_lifetimes'] == 1
    return ['paid_capture_and_source_use', 'second_write_rejected', 'literal_capture_adjacency',
            'use_required', 'reused_label_split_into_lifetimes', 'case_cap_preserves_unvisited']


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument('inputs', type=Path, nargs='?', default=Path(__file__).resolve().parent/'inputs')
    p.add_argument('--price', type=Path)
    p.add_argument('--price-sha')
    p.add_argument('--seconds', type=int, default=20, choices=range(2,21), metavar='2..20')
    p.add_argument('--controls-only', action='store_true')
    args = p.parse_args()
    if args.controls_only:
        print(dumps(controls()))
        return
    if args.price is None or args.price_sha is None:
        p.error('sealed whole-stock price and SHA-256 required')

    def stop(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM,stop)
    alarm(args.seconds)
    deadline = monotonic()+min(17,args.seconds-1)
    try:
        price = args.price.read_bytes()
        assert sha256(price).hexdigest() == args.price_sha, 'changed price receipt'
        assert decode(price)['head'] == HEAD, 'wrong price comparator'
        material = {}
        for path,pin in PINS.items():
            raw = (args.inputs/path).read_bytes()
            assert sha256(raw).hexdigest() == pin, ('changed input',path)
            material[path] = raw
        caller = decode(material[CALLER])
        assert [e[1] for e in caller['events'] if e[0] == 'J'] == list(range(1,18))
        check = controls()
        result = audit(decode(decompress(material[WORD])),deadline,LIFETIME_CAP)
        assert result['matched_lifetimes'] <= LIFETIME_CAP
        if result['complete']:
            assert result['visited_events'] == 76461 and result['matched_lifetimes'] == LIFETIME_CAP
            assert result['owned_paid_histogram_visited'] == {1:20,2:9,3:2,4:13,5:2,6:1}
            assert sum(result['all_paid_histogram_visited'].values()) == 6280
    except TimeoutError:
        print(dumps(dict(head=HEAD,status='hard_timeout',complete=False,unverified_lifetimes=LIFETIME_CAP)))
        raise SystemExit(2)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD, word_sha256=PINS[WORD], input_sha256=PINS, price_sha256=args.price_sha,
                     controls=check, structural_only=True, seconds_cap=args.seconds, lifetime_cap=LIFETIME_CAP,
                     unresolved_lifetimes=LIFETIME_CAP-result['matched_lifetimes'], **result),
                sort_keys=True,indent=2))


if __name__ == '__main__':
    assert __debug__
    main()
