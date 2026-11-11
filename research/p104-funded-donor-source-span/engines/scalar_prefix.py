"""Exact x863 replay for the literal and fused donor boundary charts."""
from argparse import ArgumentParser
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
WORD = 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9'
PRICE = '25205ad2cf4230bd2b2b704eec9f96ec4a5486fd575b5599861b28ffdd15b00b'
SOURCE, DONOR, CACHE = 863, 1355, 1568
CUTS = {48182: 739, 48185: 127}
SPLIT = [
    ['MOVE', DONOR, 739, 240, False],
    ['ADD', DONOR, CACHE, '-2', 240],
    ['MOVE', DONOR, 240, 127, False],
]


@cache
def q(value):
    return Fraction(value)


def pinned(path, digest):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError('changed dependency: ' + path.name)
    return raw


def trace(word, source, protected, cuts, replacement=None):
    chart = dict(enumerate(word['initial']))
    coefficients = {source: Fraction(1)}
    output = {}
    public = word['public']
    frames = word['frames']
    events = word['program']

    @cache
    def span(f):
        values = {0}
        for v in frames[f]:
            assert v not in values
            values.update(x ^ v for x in tuple(values))
        return values

    for clock in range(max(cuts) + 1):
        if clock in cuts:
            selected = cuts[clock]
            roles = sorted(r for r, f in chart.items() if f == selected and r not in protected)
            output[clock] = dict(chart=selected, roles=roles, owned=[r for r in roles if r >= public],
                                 nonzero={r:str(coefficients[r]) for r in roles if r in coefficients},
                                 protected_coefficients={r:str(coefficients.get(r,0)) for r in sorted(protected)})
        if clock == max(cuts):
            break
        event = (replacement or {}).get(clock, events[clock])
        if event is None:
            continue
        op, dest, *args = event
        if op == 'MOVE':
            a, b, owned = args
            assert chart[dest] == a and owned == (dest >= public)
            assert span(a) < span(b) or owned and span(b) < span(a)
            chart[dest] = b
        elif op == 'INIT':
            assert dest >= public and dest not in chart and dest not in coefficients
            chart[dest] = args[0]
        elif op == 'CLEAR':
            assert dest >= public and chart.pop(dest) == args[0]
            coefficients.pop(dest, None)
        else:
            assert op in ('ADD', 'COPY', 'SCALE') and chart[dest] == args[-1]
            src = dest if op == 'SCALE' else args[0]
            assert chart[src] == args[-1]
            assert op != 'COPY' or dest >= public
            old = coefficients.get(dest, 0) if op == 'ADD' else 0
            new = old + coefficients.get(src, 0) * q(args[-2])
            if new:
                coefficients[dest] = new
            else:
                coefficients.pop(dest, None)
    return output


def controls():
    toy = dict(public=2, initial=[0,0], frames=[[],[1]],
               program=[['INIT',2,0], ['COPY',2,0,'-3/2',0], ['ADD',1,2,'2',0],
                        ['MOVE',1,0,1,False], ['CLEAR',2,0]])
    data = trace(toy, 0, {0}, {2:0, 4:1, 5:0})
    assert data[2]['nonzero'] == {2:'-3/2'}
    assert data[4]['roles'] == [1] and data[4]['nonzero'] == {1:'-3'}
    assert data[5]['roles'] == [] and not data[5]['nonzero']
    changed = trace(toy, 0, {0}, {4:1}, {2:None})
    assert changed[4]['roles'] == [1] and not changed[4]['nonzero']
    return ['signed_copy_add_and_move', 'clear_releases_owned_role', 'omitted_add_changes_projection']


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument('word', type=Path, nargs='?')
    p.add_argument('price', type=Path, nargs='?')
    p.add_argument('--controls-only', action='store_true')
    args = p.parse_args()
    checks = controls()
    if args.controls_only:
        print(dumps(checks))
        return
    if args.word is None or args.price is None:
        p.error('exact word and price required')

    def stop(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM, stop)
    alarm(15)
    try:
        price = loads(pinned(args.price, PRICE))
        assert price['head'] == HEAD and price['word_sha256'] == WORD
        word = loads(decompress(pinned(args.word, WORD)))
        assert word['program'][48182:48185] == SPLIT
        assert word['program'][37764] == ['ADD', CACHE, SOURCE, '1', 240]
        protected = {SOURCE, DONOR, CACHE}
        original = trace(word, SOURCE, protected, CUTS)
        fused = trace(word, SOURCE, protected, CUTS,
                      {48182:['MOVE',DONOR,739,127,False],48183:None,48184:None})
        assert original[48182] == fused[48182]
        old, new = original[48185], fused[48185]
        assert {k:v for k,v in old.items() if k != 'protected_coefficients'} == {
            k:v for k,v in new.items() if k != 'protected_coefficients'}
        assert all(old['protected_coefficients'][r] == new['protected_coefficients'][r] for r in (SOURCE,CACHE))
        difference = q(old['protected_coefficients'][DONOR]) - q(new['protected_coefficients'][DONOR])
        assert old['protected_coefficients'][CACHE] == '1' and difference == -2
        assert not original[48182]['roles'] and len(old['roles']) == 673
        assert not old['owned'] and not old['nonzero']
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD, word_sha256=WORD, price_sha256=PRICE, controls=checks,
                     literal_prefix_events=48185, cuts=original, fused_cuts=fused,
                     missing_donor_coefficient=str(difference), unresolved=[]),
                sort_keys=True, indent=2))


if __name__ == '__main__':
    assert __debug__
    main()
