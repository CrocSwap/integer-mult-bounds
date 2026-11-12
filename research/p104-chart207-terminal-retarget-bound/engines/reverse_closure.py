"""Independently derive terminal coframe closure from reverse native chronology."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    'inputs/7334-WORD.json.gz': '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'inputs/R132-PRICE.json': '66d7496dfebb3373aae7c702641877134f1caf48e0dca7bfc13f33a15999d489',
    'inputs/R92-PRICE.json': '05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f',
    'inputs/R136-PRICE.json': '203e56f3f6e371336d96b265f59c9c25a14ba2cc2ff01b98e99b4b5cb63570e3',
    'inputs/R136-PLAN.md': 'f0374873829f57ce9c4bc0544a76f83fdd080e7b109599016a38e8d13ca9b910',
}
PAYLOAD = '9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
EVENTS, ROLES, SECONDS = 76466,615,25


def unique(items):
    obj = dict(items)
    if len(items) != len(obj):
        raise ValueError('duplicate JSON key')
    return obj


def authenticated(root, path):
    data = (root/path).read_bytes()
    if sha256(data).hexdigest() != PINS[path]:
        raise ValueError('changed dependency '+path)
    return data


def read(root,path):
    return loads(authenticated(root,path), object_pairs_hook=unique)


def freeze(root):
    stock, one, current = (read(root,'inputs/'+s+'-PRICE.json') for s in ('R92','R132','R136'))
    authenticated(root,'inputs/R136-PLAN.md')
    assert stock['head'] == one['head'] == current['head'] == HEAD
    assert stock['caller_head'] == one['caller_head'] == current['caller'] == CALLER
    assert current['roles'] == stock['endpoint_cohort']
    assert len(set(current['roles'])) == current['case_cap'] == ROLES
    assert (current['event_cap'],current['runner_seconds_cap']) == (EVENTS,SECONDS)
    assert current['paid_delta'] == one['delta_paid_per_edit'] == {'1':-17}
    assert current['productive_delta'] == one['delta_productive_per_edit'] == {'8':17,'9':-17}
    assert current['one_gross'] == one['quotes']['old_crossing_upper']['one_edit_gross']
    assert Q(current['whole_gross_upper']) == ROLES*Q(current['one_gross'][1])
    moon = one['quotes']['moonshot']
    assert Q(current['fixed_target_complete_upper']) == Q(moon['old_margin'][1])+ROLES*Q(moon['one_edit_gross'][1]) < 0
    assert (current['paid_before'],current['productive'],current['rank_surplus']) == (110519,22461,1424)
    return current


@cache
def span(basis):
    out = {0}
    for bit in basis:
        assert bit not in out
        out |= {v^bit for v in out}
    return out


def capture(word, roles, deadline, progress):
    initial, final, n, owned = (word[k] for k in ('initial','final','public','owned_fields'))
    assert (n, owned) == (1501,68)
    endpoint_roles = {r for r,(a,b) in enumerate(zip(initial,final,strict=True)) if (a,b) == (3,127)}
    assert endpoint_roles == roles | {319} and 319 not in roles
    assert len(roles) == ROLES
    frozen = set(word['live']) | {r+112 for r in word['live']}
    frozen.update(word['hosted']['X2'],word['hosted']['Y2'])
    assert roles.isdisjoint(frozen)
    assert span(tuple(word['frames'][3])) < span(tuple(word['frames'][207])) < span(tuple(word['frames'][127]))
    assert [len(word['frames'][c]) for c in (3,207,127)] == [0,8,9]
    tape = word['program']
    assert len(tape) == EVENTS
    state = final + [None]*owned
    latest, late_binary, late_unary = {},[],[]
    for t in range(EVENTS-1,-1,-1):
        progress['first_unvisited_reverse_event'] = t
        if t%128 == 0 and monotonic() >= deadline:
            raise TimeoutError('reverse traversal cap')
        op,d,*a = tape[t]
        if op == 'MOVE':
            before, after, flag = a
            assert state[d] == after and flag == (d >= n)
            left,right = (span(tuple(word['frames'][c])) for c in (before,after))
            assert left < right or flag and right < left
            state[d] = before
            if (d in roles or d == 319) and d not in latest:
                latest[d] = (t,before,after)
        elif op == 'INIT':
            assert d >= n and state[d] == a[0]
            state[d] = None
        elif op == 'CLEAR':
            assert d >= n and state[d] is None
            state[d] = a[0]
        elif op == 'SCALE':
            assert state[d] == a[-1] and Q(a[0])
            if d in roles and d not in latest:
                late_unary.append([t,d,a[0]])
        else:
            s,q,chart = a
            assert op in ('ADD','COPY') and (op != 'COPY' or d >= n)
            assert state[d] == state[s] == chart and d != s and Q(q)
            if d in roles and d not in latest or s in roles and s not in latest:
                late_binary.append([t,d,s,op,q,chart])
        progress['events_visited'] += 1
    progress['first_unvisited_reverse_event'] = None
    assert latest.keys() == roles | {319}
    protected = latest.pop(319)
    assert protected[1:] == (1089,127)
    assert state == initial + [None]*owned
    anchors = {r:t for r,(t,b,a) in latest.items() if (b,a) == (207,127)}
    return anchors, sorted(late_binary), [item for item in reversed(late_unary) if item[1] in anchors], protected


def classify(anchors, binary):
    parent = {role:role for role in anchors}
    def root(role):
        while parent[role] != role:
            role = parent[role]
        return role

    def join(left,right):
        a,b = sorted((root(left),root(right)))
        parent[b] = a

    exterior = []
    edges = []
    for t,d,s,op,q,chart in binary:
        d_lowered = d in anchors and anchors[d] < t
        s_lowered = s in anchors and anchors[s] < t
        if not (d_lowered or s_lowered):
            continue
        assert chart == 127
        if d_lowered and s_lowered:
            assert op == 'ADD'
            edges.append([t,d,s,q])
            join(d,s)
        else:
            a,b = (d,s) if d_lowered else (s,d)
            why = 'partner_terminal_later' if b in anchors else 'partner_endpoint_fixed'
            exterior.append(([t,a,b,op,q],why))
    members, contact = defaultdict(list), defaultdict(list)
    for role in sorted(anchors):
        members[root(role)].append(role)
    for edge, reason in exterior:
        contact[root(edge[1])].append((edge,reason))
    groups = []
    for r, roles in sorted(members.items()):
        first = min(contact[r], default=(None,None))
        groups.append({'roles':roles,'first_exterior':first[0],
                       'first_exterior_reason':first[1], 'exterior_event_count':len(contact[r])})
    survivors = [g['roles'] for g in groups if g['first_exterior'] is None]
    assert sum(len(g['roles']) for g in groups) == len(anchors)
    return {'edges':edges,'groups':groups,'survivors':survivors,'external_contacts':exterior}


def controls():
    anchors = {2:2,3:5,7:3}
    edges = [[6,2,3,'ADD','-1/2',127]]
    result = classify(anchors,edges)
    assert result['survivors'] == [[2,3],[7]]
    mutated = edges + [[7,9,3,'COPY','1',127]]
    result = classify(anchors,mutated)
    assert result['survivors'] == [[7]]
    assert result['groups'][0]['first_exterior'] == [7,3,9,'COPY','1']
    early = [[4,2,3,'ADD','2',127]] + edges
    result = classify(anchors,early)
    assert result['groups'][0]['first_exterior_reason'] == 'partner_terminal_later'
    assert result['survivors'] == [[7]]
    return ['closed two-role group', 'owned COPY exterior mutation propagates', 'later terminal blocks at earlier ADD']


def main():
    assert __debug__
    cli = ArgumentParser(description=__doc__)
    cli.add_argument('--root',type=Path,default=ROOT)
    cli.add_argument('--controls-only',action='store_true')
    args = cli.parse_args()
    quote = freeze(args.root)
    tests = controls()
    if args.controls_only:
        print(dumps(tests))
        return
    def stop(*_):
        raise TimeoutError('hard 25-second cap')
    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline = monotonic()+SECONDS-1
    progress = {'events_visited':0}
    outcome = {'head':HEAD,'caller':CALLER,'controls':tests,'pins':PINS,'progress':progress,
               'caps':{'events':EVENTS,'roles':ROLES,'seconds':SECONDS}}
    try:
        payload = decompress(authenticated(args.root,'inputs/7334-WORD.json.gz'))
        assert sha256(payload).hexdigest() == PAYLOAD
        word = loads(payload,object_pairs_hook=unique)
        anchors, binary, unary, protected = capture(word,set(quote['roles']),deadline,progress)
        outcome |= {'anchors':anchors,'unary':unary,'unresolved':[],
                    'roles_visited':ROLES,'protected_role319_last_move':protected,**classify(anchors,binary)}
        if monotonic() >= deadline:
            raise TimeoutError('closure classification cap')
    except TimeoutError as exc:
        outcome = {'head':HEAD,'pins':PINS,'progress':progress,'timeout':str(exc),
                   'unresolved':quote['roles']}
    finally:
        alarm(0)
    print(dumps(outcome,indent=2,sort_keys=True))
    if outcome['unresolved']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
