"""Independently verify fixed-peer outward contacts on exact #7481."""
from bisect import bisect_left, bisect_right
from collections import defaultdict
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import exit
from time import monotonic

ROOT = Path(__file__).resolve().parent
PACKED = 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
PAYLOAD = '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
CAP = 30


def inputs(event):
    return event[1:3] if event[0] in ('ADD', 'COPY') else event[1:2]


def overlap_barrier(add, other):
    dst, src = add[1:3]
    if other[0] == 'MOVE' or not (dst in inputs(other) or src in inputs(other)):
        return False
    if other[0] != 'ADD':
        return True
    return other[1] == src or other[2] == dst


def index(tape, initial, owned):
    active = list(initial) + [None] * owned
    visits = [[(-1, c)] for c in active]
    contacts = defaultdict(list)
    for t, event in enumerate(tape):
        for role in inputs(event):
            contacts[role].append(t)
        op, role, *args = event
        if op == 'MOVE':
            assert active[role] == args[0] and args[2] == (role >= len(initial))
            active[role] = args[1]
        elif op == 'INIT':
            assert active[role] is None and role >= len(initial)
            active[role] = args[0]
        elif op == 'CLEAR':
            assert active[role] == args[0] and role >= len(initial)
            active[role] = None
        else:
            assert all(active[j] == event[-1] for j in inputs(event))
            continue
        visits[role].append((t, active[role]))
    return visits, contacts, active


def select_slot(visits, chart, left, right, tape_end):
    if left > right:
        return None
    for i, (event, current) in enumerate(visits):
        if current != chart:
            continue
        next_event = visits[i+1][0] if i+1 < len(visits) else tape_end
        earliest = max(left, event+1)
        if earliest <= min(right, next_event):
            return earliest
    return None


def main():
    assert __debug__
    started = monotonic()
    tested = []
    def timeout(signum, frame):
        print(dumps({'status':'unresolved_timeout','checked':len(tested),'cap_seconds':CAP}))
        exit(124)
    signal(SIGALRM, timeout)
    alarm(CAP)
    packed = (ROOT / '7481-WORD.json.gz').read_bytes()
    assert sha256(packed).hexdigest() == PACKED
    raw = decompress(packed)
    assert sha256(raw).hexdigest() == PAYLOAD
    word = loads(raw)
    tape = word['program']
    frames = word['frames']
    public = word['public']
    visits, contacts, final = index(tape, word['initial'], word['owned_fields'])
    assert final == word['final'] + [None] * word['owned_fields']
    for role in range(public):
        route = visits[role]
        for i in range(1, len(route)-1):
            start, mid = route[i-1][1], route[i][1]
            first, second = route[i][0], route[i+1][0]
            end = route[i+1][1]
            points = contacts[role]
            between = points[bisect_right(points,first):bisect_left(points,second)]
            if len(between) != 1:
                continue
            clock, = between
            add = tape[clock]
            if add[0] != 'ADD' or add[2] != role:
                continue
            peer = add[1]
            candidates = sorted(set(contacts[peer]).union(points)-{clock})
            k = bisect_left(candidates,clock)
            left = next((t+1 for t in reversed(candidates[:k]) if overlap_barrier(add,tape[t])),0)
            right = next((t for t in candidates[k:] if overlap_barrier(add,tape[t])),len(tape))
            before = select_slot(visits[peer],start,max(left,route[i-1][0]+1),min(right,first),len(tape))
            final_cut = route[i+2][0] if i+2 < len(route) else len(tape)
            after = select_slot(visits[peer],end,max(left,second+1),min(right,final_cut),len(tape))
            r1,r2 = len(frames[mid])-len(frames[start]),len(frames[end])-len(frames[mid])
            assert r1 > 0 and r2 > 0
            tested.append({'role':role,'moves':[first,second],'contact':clock,'ranks':[r1,r2],
                           'earlier':None if before is None else [[clock,before,start]],
                           'later':None if after is None else [[clock,after,end]]})
    primary = [loads(row) for row in decompress((ROOT / 'receipts/PRIMARY.jsonl.gz').read_bytes()).splitlines()]
    assert primary[-1] == {'status':'SCOPED_EXHAUSTION','tested':958}
    assert len(tested) == len(primary)-1 == 958
    for actual, expected in zip(tested, primary):
        assert actual == {key:expected[key] for key in actual}, (actual,expected)
    assert not any(x['earlier'] or x['later'] for x in tested)
    assert monotonic()-started < CAP
    alarm(0)
    print(dumps({'status':'PASS_INDEPENDENT_OUTWARD_EXHAUSTION','cases':len(tested),
                 'cap_seconds':CAP,'unresolved':0,'survivors':0,'all_case_ids_agree':True,
                 'word_sha256':PACKED,'payload_sha256':PAYLOAD},sort_keys=True,indent=2))


if __name__ == '__main__':
    main()
