"""Check the exact chart-652 reconstruction after allowing receiver erasure."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    'inputs/r159_reverse.py': '4f304c3eed2950677247d7e0736f31c859ad3d6ee1ea299c7b43c3a8a0b0dd58',
    'inputs/RESULT.json': 'a7b794a3a3d1f79c1f277334a03bf6ff98044d132a9e8fdb1122a8cc59d3f9ac',
    'inputs/GATE.json': '80159b185c223fba77118d61a72bb0cf533d6b5bc7b0591dcc681ef6144c03fd',
}
CUT, SOURCE, RECEIVER = 42651, 930, 793
DONORS = (165, 586)


def check(root, name):
    raw = (root / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f'changed dependency {name}')
    return raw


def coefficient(row, axis):
    vector, denominator = row
    return Q(vector.get(axis, 0), denominator)


def signed_return(engine, source, receiver, bank):
    target = engine['sum_scaled'](receiver, source, (1, 2))
    result = engine['exact_span'](bank, target)
    if result['status'] == 'absent_exterior_coordinate':
        j = result['coordinate']
        dual = {j: Q(1)}
    elif result['status'] == 'exact_rank_exclusion':
        dual = {j: Q(x) for j, x in result['separating_covector'].items()}
    else:
        return target, result, None
    dot = engine['dot']
    assert all(dot(row, dual) == 0 for _, row in bank)
    assert dot(target, dual) != 0
    witness = {
        'covector': {str(j): str(x) for j, x in sorted(dual.items())},
        'source': str(dot(source, dual)), 'receiver': str(dot(receiver, dual)),
        'target': str(dot(target, dual)),
        'donors': {str(r): str(dot(row, dual)) for r, row in bank},
    }
    return target, result, witness


def controls(engine):
    source, receiver = ({0: -1}, 1), ({0: 1, 2: 3}, 2)
    donor = (165, ({1: 1}, 1))
    exact = (586, ({2: 3}, 2))
    blocked = (586, ({3: 3}, 2))
    _, result, _ = signed_return(engine, source, receiver, [donor, exact])
    assert result['status'] == 'exact_span'
    _, result, witness = signed_return(engine, source, receiver, [donor, blocked])
    assert result['status'] == 'absent_exterior_coordinate'
    assert witness['target'] == '3/2' and witness['covector'] == {'2': '1'}
    return ['exact cancellation at the forced zero-diagonal input',
            'synthetic surviving receiver return', 'synthetic absent coordinate']


def stop(*_):
    raise TimeoutError('hard 20-second cap')


def main():
    assert __debug__
    p = ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--controls-only', action='store_true')
    args = p.parse_args()
    signal(SIGALRM, stop)
    alarm(20)
    deadline = monotonic() + 19
    for name in PINS:
        check(args.root, name)
    prior = run_path(str(args.root / 'inputs/r159_reverse.py'))
    raw = prior['checked'](args.root)
    engine = run_path(str(args.root / 'inputs/reverse_span.py'))
    tests = controls(engine)
    if args.controls_only:
        print(dumps(tests))
        return
    result = {'head': prior['HEAD'], 'caller': prior['CALLER'],
              'key': [CUT, RECEIVER, 652], 'cases': 1, 'cap_seconds': 20,
              'pins': PINS | prior['PINS'], 'controls': tests}
    try:
        gate = loads(check(args.root, 'inputs/GATE.json'), object_pairs_hook=prior['unique'])
        assert gate['status'] == 'excluded' and gate['necessary_receiver_diagonal'] == '0'
        word = loads(decompress(raw['inputs/7334-WORD.json.gz']), object_pairs_hook=prior['unique'])
        assert word['program'][CUT] == ['ADD', RECEIVER, SOURCE, '1/2', 652]
        assert prior['bank_at'](word, deadline) == [*DONORS, RECEIVER]
        roles = (SOURCE, RECEIVER, *DONORS)
        rows = engine['transpose_prefix'](word, {CUT: [(r, i) for i, r in enumerate(roles)]}, len(roles), deadline)
        source, receiver, *donor_rows = rows
        bank = list(zip(DONORS, donor_rows, strict=True))
        assert [coefficient(row, SOURCE) for row in rows] == [Q(-1), Q(1, 2), Q(0), Q(0)]
        target, proof, witness = signed_return(engine, source, receiver, bank)
        assert not coefficient(target, SOURCE)
        result.update(roles=roles, rows=rows, target=target, proof=proof, witness=witness,
                      status='excluded' if witness else 'exact normalized span survives')
    except TimeoutError as exc:
        result.update(status='unresolved', reason=str(exc), cases=0)
    finally:
        alarm(0)
    print(dumps(result, indent=2, sort_keys=True))
    if not result['cases']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
