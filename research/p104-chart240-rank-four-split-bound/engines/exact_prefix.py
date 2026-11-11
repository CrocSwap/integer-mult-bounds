"""Independent exact pure-prefix prerequisite on the sealed R63 banks."""
from argparse import ArgumentParser
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

WORD_SHA = 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9'
GEOMETRY_SHA = '3843042387401f281906d6b6eeeca1d7255b00cc327a863fd8070f0317eadc81'


@cache
def q(text):
    return Fraction(text)


def add(dst, src, coefficient):
    for index, value in src.items():
        total = dst.get(index, 0) + coefficient * value
        if total:
            dst[index] = total
        else:
            dst.pop(index, None)


def kernel(rows, inside):
    reduced = {}
    pure = []
    for i, row in enumerate(rows):
        exterior = {r: c for r, c in row.items() if r not in inside}
        combo = {i: Fraction(1)}
        while exterior:
            key = min(exterior)
            if key not in reduced:
                leading = exterior[key]
                reduced[key] = ({r: c / leading for r, c in exterior.items()},
                                {r: c / leading for r, c in combo.items()})
                break
            other, ops = reduced[key]
            coefficient = -exterior[key]
            add(exterior, other, coefficient)
            add(combo, ops, coefficient)
        else:
            projected = {}
            for r, c in combo.items():
                add(projected, rows[r], c)
            assert projected.keys() <= inside
            pure.append((combo, projected))
    return len(reduced), pure


def control():
    a = {0: q('1'), 1: q('1/2')}
    b = {0: q('2'), 1: q('1/3')}
    rank, pairs = kernel([a,b], {1})
    assert rank == 1 and pairs == [({0: q('-2'), 1: q('1')}, {1: q('-2/3')})]
    assert kernel([a,b], set()) == (2, [])
    return ['exact_pure_combination', 'exterior_leakage_rejected']


def scan(word, geometry, deadline):
    decisions = []
    public = word['public']
    rows = {r: {r: q('1')} for r in range(public)}
    checked = 0
    protected = set(geometry['protected_roles'])
    allowed = set(geometry['cohort']) - protected
    by_cut = {}
    for row in geometry['segments']:
        by_cut.setdefault(row['cut'], []).append(row)
    for clock, event in enumerate(word['program']):
        if monotonic() >= deadline:
            break
        for bank in by_cut.get(clock, []):
            assert bank['tier'] == 'cohort_rank_two'
            coordinates = [r for r in bank['public_bank'] if r not in protected]
            rank, pure = kernel([rows[r] for r in coordinates], allowed)
            decisions.append(dict(cut=clock, chart=bank['chart'], pivots=bank['pivots'],
                                  public_basis=coordinates, exterior_rank=rank,
                                  pure_prefix=[dict(a={coordinates[r]:str(v) for r,v in a.items()},
                                                    c={r:str(v) for r,v in c.items()}) for a,c in pure],
                                  nonzero_prefix=any(c for _,c in pure)))
        checked = clock
        if clock >= max(by_cut):
            break
        op, dest, *rest = event
        if op == 'ADD':
            add(rows[dest], rows[rest[0]], q(rest[1]))
        elif op == 'COPY':
            rows[dest] = {}
            add(rows[dest], rows[rest[0]], q(rest[1]))
        elif op == 'SCALE':
            coefficient = q(rest[0])
            rows[dest] = {r: c * coefficient for r, c in rows[dest].items()}
        elif op == 'INIT':
            rows[dest] = {}
        elif op == 'CLEAR':
            del rows[dest]
        else:
            assert op == 'MOVE'
    visited = {(row['cut'],row['chart']) for row in decisions}
    unresolved = [[row['cut'],row['chart']] for row in geometry['segments']
                  if (row['cut'],row['chart']) not in visited]
    return dict(visited_through_cut=checked, decisions=decisions,
                prefix_survivors=[[row['cut'],row['chart']] for row in decisions if row['nonzero_prefix']],
                unresolved=unresolved)


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument('word', type=Path, nargs='?')
    p.add_argument('geometry', type=Path, nargs='?')
    p.add_argument('--seconds', type=int, default=15, choices=range(2,16), metavar='2..15')
    p.add_argument('--controls-only', action='store_true')
    args = p.parse_args()
    check = control()
    if args.controls_only:
        print(dumps(check))
        return
    if args.word is None or args.geometry is None:
        p.error('sealed word and geometry required')

    def stop(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM, stop)
    alarm(args.seconds)
    try:
        word = args.word.read_bytes()
        geometry = args.geometry.read_bytes()
        assert sha256(word).hexdigest() == WORD_SHA
        assert sha256(geometry).hexdigest() == GEOMETRY_SHA
        result = scan(loads(decompress(word)), loads(geometry), monotonic()+args.seconds-1)
    except TimeoutError:
        print(dumps(dict(status='hard_timeout')))
        raise SystemExit(2)
    finally:
        alarm(0)
    print(dumps(dict(word_sha256=WORD_SHA, geometry_sha256=GEOMETRY_SHA, controls=check,
                     seconds_cap=args.seconds, **result),sort_keys=True,indent=2))


if __name__=='__main__':
    assert __debug__
    main()
