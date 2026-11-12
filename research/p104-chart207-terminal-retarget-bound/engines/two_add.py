"""Preprice and check the two fixed-partner terminal ADD pairs."""
from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
PINS = {
    'inputs/7334-WORD.json.gz': '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'inputs/R100-GEOMETRY.json': '075301daf545c8021800c36af19d05517e3c4136dac4e2114cb85204d0b31c64',
    'inputs/R130-retime.py': '90d3cb0e0079244265320b77e1a3e67fd61dbaa837390f1ba8bce59edd7fd91f',
    'inputs/R132-PRICE.json': '66d7496dfebb3373aae7c702641877134f1caf48e0dca7bfc13f33a15999d489',
    'inputs/R132-RESULT.json': 'd8f2d00bae5781188ec420c8756a727ab6b760129053e3a2b68ede1ccf64ff57',
}
PAYLOAD = '9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
EVENTS, CUTS, STEPS, SECONDS = 76466, 5084, 17398, 20


def authenticate(name, digest=None):
    raw = (ROOT / name).read_bytes()
    assert sha256(raw).hexdigest() == (digest or PINS[name]), ('changed input', name)
    return raw


def unique(pairs):
    obj = dict(pairs)
    assert len(pairs) == len(obj), 'duplicate JSON key'
    return obj


def read(name, digest=None):
    return loads(authenticate(name, digest), object_pairs_hook=unique)


def quote():
    r132 = read('inputs/R132-PRICE.json')
    scoped = read('inputs/R132-RESULT.json')
    g = read('inputs/R100-GEOMETRY.json')
    authenticate('inputs/R130-retime.py')
    assert r132['head'] == scoped['head'] == g['head'] == HEAD
    assert scoped['price_sha256'] == PINS['inputs/R132-PRICE.json']
    candidates = []
    for role, result in sorted(scoped['dispositions'].items()):
        if len(result['post_terminal_contacts']) != 2:
            continue
        role = int(role)
        terminal = result['terminal_clock']
        row, = [x for x in g['pairs'] if x['key'][1:] == [terminal, role]]
        assert row['charts'][1:] == [207,127]
        contacts = result['post_terminal_contacts']
        assert all(event[0] == 'ADD' and role in event[1:3] and event[4] == 127
                   for _, _, event in contacts)
        candidates.append({'role': role, 'entry_clock': row['key'][0],
                           'terminal_clock': terminal, 'entry_chart': row['charts'][0],
                           'contacts': contacts})
    assert [x['role'] for x in candidates] == [1453, 532]
    assert sum(2*(r['terminal_clock']-r['entry_clock']) for r in candidates) == CUTS
    assert sum(c-r['entry_clock']-1 for r in candidates for c,_,_ in r['contacts']) == STEPS
    quotes = {}
    for label,q in r132['quotes'].items():
        gross = list(map(Fraction, q['one_edit_gross']))
        old = list(map(Fraction, q['old_margin']))
        quotes[label] = {'kappa': q['kappa'], 'one_edit_margin': q['one_edit_margin'],
                         'whole_two_gross_upper': str(2*gross[1]),
                         'full_two_margin_upper': str(old[1]+2*gross[1]),
                         'whole_two_with_one_extra_raw_rank_one_upper': str(old[1]+2*gross[1]-1)}
    assert Fraction(quotes['probe']['one_edit_margin'][0]) > 0
    assert Fraction(quotes['old_crossing_upper']['whole_two_with_one_extra_raw_rank_one_upper']) < 0
    assert Fraction(quotes['moonshot']['full_two_margin_upper']) < 0
    return {'head': HEAD, 'caller_head': CALLER, 'pins': PINS, 'candidates': candidates,
            'cases': 2, 'event_cap': EVENTS, 'typed_cut_cap': CUTS, 'commutator_step_cap': STEPS,
            'runner_seconds': SECONDS, 'quotes': quotes, 'productive_count': 22461,
            'paid_count_by_edits': [110519,110502,110485], 'signed_rank_surplus': 1424,
            'delta_paid_per_edit': {1:-17}, 'delta_productive_per_edit': {8:17,9:-17}}


def partner(role, event):
    dst, src = event[1:3]
    assert dst != src and role in (dst, src)
    return src if dst == role else dst


def ordered(first, second):
    return next(([first[0], t] for t in second if first and first[0] <= t), None)


def inspect(word, price, deadline, shared):
    program = word['program']
    assert len(program) == EVENTS
    wanted = {p for row in price['candidates'] for _,_,event in row['contacts']
              for p in (row['role'], partner(row['role'], event))}
    charts = shared['positions'](word, wanted)
    rows, steps, cuts = [], 0, 0
    for row in price['candidates']:
        if monotonic() >= deadline:
            break
        role = row['role']
        entry, terminal = row['entry_clock'], row['terminal_clock']
        assert program[entry] == ['MOVE', role, row['entry_chart'], 207, False]
        assert program[terminal] == ['MOVE', role, 207, 127, False]
        assert all(chart == 207 for chart in charts[role][entry+1:terminal+1])
        actual_tail = [[t, 'source' if e[0] in ('ADD','COPY') and e[2] == role else 'destination', e]
                       for t,e in enumerate(program[terminal+1:], terminal+1)
                       if e[1] == role or e[0] in ('ADD','COPY') and e[2] == role]
        assert actual_tail == row['contacts']
        witnesses = []
        for clock, _, add in row['contacts']:
            other, = [c for c,_,_ in row['contacts'] if c != clock]
            assert program[clock] == add
            peer = partner(role, add)
            barrier = None
            for t in range(clock-1, entry, -1):
                steps += 1
                assert steps <= STEPS
                if t != other and not shared['commute'](add, program[t]):
                    barrier = [t, program[t]]
                    break
            all_slots = [t for t in range(entry+1,terminal+1) if charts[peer][t] == 207]
            cuts += terminal-entry
            assert cuts <= CUTS
            surviving = [t for t in all_slots if barrier is None or barrier[0] < t]
            witnesses.append({'old_clock': clock, 'event': add, 'partner': peer,
                              'partner_chart207_anywhere': 207 in charts[peer],
                              'coframe_slots_before_commutation': all_slots,
                              'first_noncommuting_barrier': barrier,
                              'allowed_slots': surviving})
        slot0, slot1 = (r['allowed_slots'] for r in witnesses)
        rows.append({'role': role, 'terminal_clock': terminal, 'placements': witnesses,
                     'witness': ordered(slot0,slot1)})
    return {'rows': rows, 'typed_cuts': cuts, 'commutator_steps': steps,
            'unresolved': [r['role'] for r in price['candidates'][len(rows):]]}


def controls(shared):
    old = shared['controls']()
    assert ordered([2,4],[1,4]) == [2,4]
    assert ordered([3],[1,2]) is None
    assert ordered([4],[4]) == [4,4]
    assert ordered([], [4]) is None
    return old + ['ordered common slot', 'reversed slots rejected', 'absent coframe rejected']


def main():
    cli = ArgumentParser(description=__doc__)
    cli.add_argument('mode', choices=('price','support','controls'))
    cli.add_argument('--price-sha')
    args = cli.parse_args()
    if args.mode == 'price':
        result = quote()
    else:
        authenticate('inputs/R130-retime.py')
        shared = run_path(str(ROOT/'inputs/R130-retime.py'))
        checked = controls(shared)
        if args.mode == 'controls':
            print(dumps(checked))
            return
        if args.price_sha is None:
            cli.error('--price-sha is required')
        def stop(*_):
            raise TimeoutError('20 second hard cap')
        signal(SIGALRM, stop)
        alarm(SECONDS)
        deadline = monotonic()+SECONDS-1
        try:
            price = read('lead/PRICE.json', args.price_sha)
            assert price == loads(dumps(quote()))
            raw = decompress(authenticate('inputs/7334-WORD.json.gz'))
            assert sha256(raw).hexdigest() == PAYLOAD
            result = inspect(loads(raw, object_pairs_hook=unique), price, deadline, shared)
        except TimeoutError:
            result = {'hard_timeout': True, 'unresolved': [1453,532]}
        finally:
            alarm(0)
        result |= {'head': HEAD, 'caller': CALLER, 'price_sha256': args.price_sha,
                   'input_sha256': PINS, 'controls': checked, 'runner_cap': SECONDS}
    print(dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    assert __debug__
    main()
