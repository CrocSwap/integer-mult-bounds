"""Directed price of replacing #7314 donor 1355's paid 1+5 split by rank six."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from tempfile import NamedTemporaryFile

PINS = {
    'round63/price.py': 'ede3c496e0295481505136aa8411035cf7c2206df3bfe61d0bf0c9c47fea731c',
    'round63/price.json': '5943e27d6dd81d2c4b8feae2d8398da3b8cd0d218fa86e89cf6523e8fb4e61e9',
    '7314/construct.py': '2dec457c43300dbbdf4113db77b061c1e5363a76b79f49b786d95b64ab22c62b',
}
BIT = Fraction('0.00376669')
WORD = 'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9'


def checked(path, digest):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError(f'Changed input {path.name}')
    return raw


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError('Duplicate JSON key')
    return result


def read(raw):
    return loads(raw, object_pairs_hook=unique)


def encoded(value):
    return (dumps(value, indent=2, sort_keys=True) + '\n').encode()


def interval(values):
    return list(map(str, values))


def derivative_bounds(histogram, lo, hi, tariff):
    log, power = tariff['log_bounds'], tariff['power_bounds']
    ln2lo, ln2hi = log(Fraction(2))
    lower = upper = Fraction(0)
    for rank, count in histogram.items():
        shift = rank.bit_length() - 1
        lrlo, lrhi = log(Fraction(rank, 1 << shift))
        qlo, qhi = (lrlo + shift*ln2lo, lrhi + shift*ln2hi)
        a = -count * power(rank, hi)[0] * qlo
        b = -count * power(rank, lo)[1] * qhi
        lower += min(a, b)
        upper += max(a, b)
    return lower, upper


def quote(root):
    frozen = {path: checked(root / path, digest) for path, digest in PINS.items()}
    prior_root = root / 'round63/price-inputs'
    prior = run_path(str(root / 'round63/price.py'))['quote'](prior_root)
    assert encoded(prior) == frozen['round63/price.json']
    assert prior['input_sha256']['inputs/7314/WORD.json.gz'] == WORD
    pins = PINS.copy()
    for path, digest in prior['input_sha256'].items():
        key = f'round63/price-inputs/{path}'
        assert key not in pins
        pins[key] = digest
    witness = read((prior_root / 'inputs/7314/WITNESS.json').read_bytes())
    native = read((prior_root / 'inputs/7314/NATIVE-RESULT.json').read_bytes())
    assert witness['split'] == 48166
    assert [row for row in witness['corrections'] if row[0] == 48166] == [[48166, 1355, 240, -2]]
    chart_ranks = {tuple(row['pair']): row['rank'] for row in native['charts']['rechecked_pairs']}
    assert tuple(chart_ranks[p] for p in ((739, 240), (240, 127), (739, 127))) == (1, 5, 6)
    copies = prior['copies']
    assert copies == 17
    paid, targets = (Counter({int(r): n for r, n in prior[key].items()}) for key in ('paid', 'targets'))
    paid_delta = Counter({1: -copies, 5: -copies, 6: copies})
    new_paid = paid.copy()
    new_paid.update(paid_delta)
    assert all(n > 0 for n in new_paid.values()) and sum(new_paid.values()) == 110519
    net, new_net = targets.copy(), targets.copy()
    net.subtract(paid)
    new_net.subtract(new_paid)
    credit_hist = Counter({r: -n for r, n in paid_delta.items()})
    assert sum(r*n for r, n in net.items()) == sum(r*n for r, n in new_net.items()) == 1424
    assert sum(targets.values()) == 22461 and prior['empty_root_credits'] == 0
    tariff = run_path(str(prior_root / 'inputs/7298/pricing.py'))
    cost = tariff['cost']
    old_upper = Fraction(prior['crossing_upper'])
    old_margin = cost(net, old_upper)
    new_margin = cost(new_net, old_upper)
    credit = cost(credit_hist, old_upper)
    with_extra = new_net.copy()
    with_extra[1] -= 1
    extra_margin = cost(with_extra, old_upper)
    assert interval(old_margin) == prior['old_margin'] and old_margin[1] < 0
    assert 0 < credit[0] <= credit[1] < 1 and new_margin[0] > 0 > extra_margin[1]
    derivative = derivative_bounds(new_net, old_upper, BIT, tariff)
    assert derivative[1] < 0 and cost(new_net, BIT)[1] < 0
    lo, hi = old_upper, BIT
    for _ in range(32):
        probe = (lo + hi) / 2
        lower, upper = cost(new_net, probe)
        if lower > 0:
            lo = probe
        elif upper < 0:
            hi = probe
        else:
            break
    assert lo > old_upper and cost(new_net, lo)[0] > 0 > cost(new_net, hi)[1]
    probe = Fraction((lo*10**13).__floor__(), 10**13)
    trial = cost(new_net, probe)
    assert probe > old_upper and trial[0] > 0 > cost(net, probe)[1]
    return {
        'head': prior['head'], 'caller': prior['caller'], 'word_sha256': WORD,
        'claim': prior['claim'], 'crossing_upper': str(old_upper), 'input_sha256': pins,
        'copies': copies, 'stock_edits_cap': 1, 'rank_surplus': 1424, 'empty_root_credits': 0,
        'source_witness': {'role': 1355, 'cache_role': 1568, 'source_clock': 48166,
                           'old_chart_path': [739, 240, 127], 'restored_chart_path': [739, 127],
                           'moved_add_coefficient': '-2'},
        'old_paid': dict(paid), 'new_paid': dict(new_paid), 'paid_delta': dict(paid_delta),
        'productive': dict(targets), 'target_delta': {},
        'old_paid_positions': sum(paid.values()), 'new_paid_positions': sum(new_paid.values()),
        'productive_fields': sum(targets.values()), 'old_margin': interval(old_margin),
        'complete_new_margin_at_old_crossing_upper': interval(new_margin), 'credit': interval(credit),
        'one_edit_optimistic_upper': str(credit[1]),
        'complete_margin_with_one_extra_rank_one_position': interval(extra_margin),
        'bit_bound': str(BIT), 'price_only_derivative_bound': interval(derivative),
        'price_only_raw_crossing_bracket': interval((lo, hi)),
        'price_only_moment_pass_probe': str(probe), 'price_only_probe_new_margin': interval(trial),
        'price_only_probe_old_margin': interval(cost(net, probe)),
        'scope': 'Price before support. Grants feasible relocated response at existing coframes and no additional paid position. All physical, ordinary, precision, tape and compiler obligations remain.',
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error('Run with proof assertions enabled')
    raw = encoded(quote(args.root))
    if args.out is None:
        print(raw.decode(), end='')
        return
    with NamedTemporaryFile(mode='wb', dir=args.out.parent, prefix='price-', delete=False) as output:
        output.write(raw)
    temp = Path(output.name)
    temp.chmod(0o644)
    temp.replace(args.out)


if __name__ == '__main__':
    main()
