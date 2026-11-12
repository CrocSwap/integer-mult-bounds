"""Independent reverse signed aggregate and forward separator for the role-532 terminal corridor."""
from argparse import ArgumentParser
from collections import Counter
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
    'inputs/R132-RESULT.json': 'd8f2d00bae5781188ec420c8756a727ab6b760129053e3a2b68ede1ccf64ff57',
    'inputs/R134-PRICE.json': '76fe970dde53c19b1a068d705344a50afbd3c9a1a1dcd863d6fd605451119ac8',
    'inputs/R134-RESULT.json': '26d1dd900720a87cbc483bd79538066d45f1a52a0801e25e1bce1617e52032eb',
    'inputs/R135-PRICE.json': '707b3ddcb55842bb7d701ff02bd5dd9141ab3d2f1a8ec494029a7c8b47d2b9ba',
    'inputs/R135-LEAD-RESULT.json': 'f563c28c2dfe49e25adea6ca073d08d31d447dcfd9c00cd985bf9189e9f7ce69',
}
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
PAYLOAD = '9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
ROLE, CHART, ENTER, TERM = 532, 207, 44611, 46018
OLD_ADDS = {46019: ['ADD',ROLE,363,'-1',127], 58282: ['ADD',ROLE,232,'2',127]}
EVENTS, CUTS, SECONDS = 76466, 1407, 25


def unique(items):
    obj = dict(items)
    if len(obj) != len(items):
        raise ValueError('duplicate JSON key')
    return obj


def checked(root, path):
    raw = (root / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError('changed dependency ' + path)
    return raw


def predecessor(root):
    old_price, old, price, prior = (loads(checked(root, 'inputs/' + path + '.json'), object_pairs_hook=unique)
                                    for path in ('R132-PRICE','R132-RESULT','R134-PRICE','R134-RESULT'))
    assert all(r['head'] == HEAD for r in (old_price, old, price, prior))
    assert old['caller_head'] == price['caller_head'] == prior['caller'] == CALLER
    assert old['price_sha256'] == PINS['inputs/R132-PRICE.json']
    assert prior['price_sha256'] == PINS['inputs/R134-PRICE.json']
    assert price['delta_paid_per_edit'] == {'1':-17}
    assert price['delta_productive_per_edit'] == {'8':17,'9':-17}
    assert price['paid_count_by_edits'][:2] == [110519,110502]
    assert price['productive_count'] == 22461 and price['signed_rank_surplus'] == 1424
    assert Q(price['quotes']['probe']['one_edit_margin'][0]) > 0
    r, = [r for r in price['candidates'] if r['role'] == ROLE]
    prior_r, = [r for r in prior['rows'] if r['role'] == ROLE]
    assert r['entry_clock'] == ENTER and r['terminal_clock'] == TERM
    assert old['dispositions'][str(ROLE)]['post_terminal_contacts'] == r['contacts']
    assert {t: e for t,access,e in r['contacts'] if access == 'destination'} == OLD_ADDS
    assert prior_r['witness'] is None and not prior['unresolved']
    quote = loads(checked(root, 'inputs/R135-PRICE.json'), object_pairs_hook=unique)
    assert quote['head'] == HEAD and quote['caller'] == CALLER and quote['scope'] == r
    assert quote['cut_cap'] == CUTS and quote['seconds_cap'] == SECONDS and quote['compatible_cap'] == 1
    assert quote['paid_delta'] == price['delta_paid_per_edit']
    assert quote['productive_delta'] == price['delta_productive_per_edit']
    assert (quote['paid'], quote['productive'], quote['surplus']) == (110502,22461,1424)
    assert quote['gross'] == old_price['quotes']['old_crossing_upper']['one_edit_gross']
    return quote


@cache
def scalar(v):
    return Q(v)


def set_value(weights, role, value):
    if value:
        weights[role] = value
    else:
        weights.pop(role, None)


def reverse_event(weights, event):
    op,d,*args = event
    if op in ('INIT','CLEAR'):
        weights.pop(d, None)
    elif d in weights and op in ('ADD','COPY'):
        s,q,_ = args
        set_value(weights, s, weights.get(s,0) + scalar(q)*weights[d])
        if op == 'COPY':
            weights.pop(d)
    elif d in weights and op == 'SCALE':
        set_value(weights, d, scalar(args[0])*weights[d])


def time_check(clock, deadline):
    if clock % 128 == 0 and monotonic() >= deadline:
        raise TimeoutError('soft time cap')


def span(basis):
    vs = {0}
    for v in basis:
        assert v not in vs
        vs |= {u^v for u in vs}
    return vs


def reverse_trace(word, deadline, progress):
    tape, n, m = (word[k] for k in ('program','public','owned_fields'))
    assert (len(tape), n, m) == (EVENTS,1501,68)
    assert word['initial'][ROLE] == 3 and word['final'][ROLE] == 127
    assert span(word['frames'][3]) < span(word['frames'][CHART]) < span(word['frames'][127])
    assert len(word['frames'][CHART]) == 8 and len(word['frames'][127]) == 9
    assert tape[ENTER] == ['MOVE',ROLE,746,207,False]
    assert tape[TERM] == ['MOVE',ROLE,207,127,False]
    state = word['final'] + [None]*m
    donors = {r for r,c in enumerate(state[:n]) if c == CHART and r != ROLE}
    weights, banks, old_contacts = {}, {}, {}
    pre_terminal_contact = None
    for t in range(EVENTS-1,-1,-1):
        progress['reverse_first_unvisited'] = t
        time_check(t, deadline)
        op,d,*args = tape[t]
        touches = d == ROLE or op in ('ADD','COPY') and args[0] == ROLE
        if touches and t > TERM:
            old_contacts[t] = tape[t]
        if op == 'MOVE':
            before,after,owned = args
            assert owned == (d >= n) and state[d] == after
            state[d] = before
            if d < n and d != ROLE:
                if before == CHART:
                    donors.add(d)
                if after == CHART:
                    donors.remove(d)
        elif op == 'INIT':
            assert d >= n and state[d] == args[0]
            state[d] = None
        elif op == 'CLEAR':
            assert d >= n and state[d] is None
            state[d] = args[0]
        else:
            assert op in ('ADD','COPY','SCALE') and state[d] == args[-1]
            if op != 'SCALE':
                assert args[0] != d and state[args[0]] == state[d]
            assert op != 'COPY' or d >= n
        reverse_event(weights,tape[t])
        if t in OLD_ADDS:
            assert tape[t] == OLD_ADDS[t]
            _,_,s,q,_ = tape[t]
            set_value(weights,s,weights.get(s,0)+scalar(q))
        if touches and ENTER <= t < TERM and pre_terminal_contact is None:
            pre_terminal_contact = [t,tape[t]]
        if ENTER < t <= TERM and pre_terminal_contact is None:
            assert state[ROLE] == CHART
            banks[t] = tuple(sorted(donors))
            assert len(banks) <= CUTS
        progress['reverse_events'] += 1
    progress['reverse_first_unvisited'] = None
    assert old_contacts == OLD_ADDS and state == word['initial']+[None]*m
    assert all(r < n for r in weights)
    assert pre_terminal_contact is not None
    assert sorted(banks) == list(range(pre_terminal_contact[0]+1,TERM+1))
    assert banks
    return weights, banks, pre_terminal_contact


def forward_event(values, event):
    op,d,*args = event
    if op in ('INIT','CLEAR'):
        values.pop(d, None)
    elif op in ('ADD','COPY'):
        s,q,_ = args
        set_value(values,d,(values.get(d,0) if op == 'ADD' else 0) + scalar(q)*values.get(s,0))
    elif op == 'SCALE':
        set_value(values,d,scalar(args[0])*values.get(d,0))


def one_impulse(word, banks, impulse, deadline, progress):
    assert impulse and all(0 <= j < word['public'] and v for j,v in impulse.items())
    values = impulse.copy()
    seen, source_values = {}, {}
    for t,e in enumerate(word['program']):
        progress['forward_first_unvisited'] = t
        time_check(t, deadline)
        if t in banks:
            seen[t] = {r:str(values[r]) for r in banks[t] if r in values}
            progress['cuts_replayed'] += 1
        if t in OLD_ADDS:
            source_values[t] = values.get(e[2], Q(0))
        if t == max(OLD_ADDS):
            break
        forward_event(values,e)
        progress['forward_events'] += 1
    progress['forward_first_unvisited'] = None
    return seen, source_values


def controls():
    tape = [['ADD',1,0,'-2',207], ['COPY',2,1,'1/2',207],
            ['SCALE',2,'-3',207], ['ADD',3,2,'1',207]]
    weight = {3:Q(1)}
    for event in reversed(tape):
        reverse_event(weight,event)
    expected = {3:Q(1), 1:Q(-3,2), 0:Q(3)}
    assert weight == expected
    impulse = {0:Q(1)}
    for event in tape:
        forward_event(impulse,event)
    assert impulse[3] == expected[0]
    set_value(weight,0,weight[0]-Q(3))
    assert 0 not in weight
    set_value(weight,0,weight.get(0,0)+Q(6))
    assert weight[0] == Q(6)
    return ['signed reverse ADD/COPY/SCALE', 'matching signed forward impulse',
            'exact cancellation', 'sign mutation restores a nonzero coordinate']


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--controls-only',action='store_true')
    args = parser.parse_args()
    price = predecessor(args.root)
    tests = controls()
    if args.controls_only:
        print(dumps(tests))
        return
    lead = loads(checked(args.root, 'inputs/R135-LEAD-RESULT.json'), object_pairs_hook=unique)
    assert lead['head'] == HEAD and lead['caller'] == CALLER and not lead['unvisited_cuts']
    assert lead['pins']['inputs/R134-RESULT.json'] == PINS['inputs/R134-RESULT.json']
    separator = {int(j):Q(v) for j,v in lead['disposition']['separator'].items()}
    assert separator == {2:Q(1),3:Q(-1,2),27:Q(-1),28:Q(1)}
    def stop(*_):
        raise TimeoutError('hard 25-second cap')
    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline = monotonic()+SECONDS-1
    progress = {'reverse_events':0,'forward_events':0,'cuts_replayed':0}
    result = dict(head=HEAD,caller=CALLER,pins=PINS,separator={j:str(v) for j,v in sorted(separator.items())},controls=tests,progress=progress,
                  caps={'events_per_pass':EVENTS,'cuts':CUTS,'seconds':SECONDS},
                  invoice={k:price[k] for k in ('gross','probe','fixed_target','paid_delta','productive_delta')})
    try:
        raw = decompress(checked(args.root,'inputs/7334-WORD.json.gz'))
        assert sha256(raw).hexdigest() == PAYLOAD
        word = loads(raw,object_pairs_hook=unique)
        aggregate,banks,last = reverse_trace(word,deadline,progress)
        result |= dict(aggregate={r:str(v) for r,v in sorted(aggregate.items())},last_old_contact=last,
                       cuts=[{'cut':t,'public_donors':rs} for t,rs in sorted(banks.items())],
                       unique_public_donors=sorted({r for rs in banks.values() for r in rs}),
                       donor_stock=Counter(map(len,banks.values())))
        coverage = {'cut_count':len(banks),'cut_role_pairs':sum(map(len,banks.values())),
                    'first_last_cuts':[min(banks),max(banks)]}
        assert (coverage['cut_count'],coverage['cut_role_pairs'],coverage['first_last_cuts']) == (
            lead['cut_count'],lead['cut_role_pairs'],lead['cuts'])
        assert {str(r):str(v) for r,v in aggregate.items()} == lead['aggregate'] and last == lead['last_contact']
        for cut,chart,role in lead['slots'].values():
            assert chart == CHART and role in banks[cut]
        values,sources = one_impulse(word,banks,separator,deadline,progress)
        y = sum(scalar(OLD_ADDS[t][3])*v for t,v in sources.items())
        assert y == sum(q*aggregate.get(j,0) for j,q in separator.items()) == Q(lead['disposition']['separator_value'])
        usable = bool(y) and not any(values.values())
        result |= dict(coverage=coverage, lead_aggregate_and_coverage_agree=True,
                       lead_representatives_are_literal_slots=True, separator_verified=usable,
                       separator_on_aggregate=str(y), separator_on_sources={t:str(v) for t,v in sorted(sources.items())},
                       nonzero_donors={t:rs for t,rs in sorted(values.items()) if rs},
                       unresolved_cuts=[] if usable else sorted(banks))
    except TimeoutError as e:
        result |= dict(timeout=str(e),unresolved_cuts='incomplete at cap, no exclusion')
    finally:
        alarm(0)
    print(dumps(result,indent=2,sort_keys=True))
    if 'timeout' in result:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
