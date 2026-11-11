"""Replay the exact #7314 fixed-chart ADD contraction exclusion."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ENGINES = HERE / 'engines'
HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'


def unique(pairs):
    values = dict(pairs)
    if len(values) != len(pairs):
        raise ValueError('duplicate JSON key')
    return values


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate(scratch):
    pins = decode((HERE / 'LOCAL-PINS.json').read_bytes())
    for name, expected in pins.items():
        relative = PurePosixPath(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        assert relative.as_posix() == name, name
        assert digest((HERE / name).read_bytes()) == expected, ('changed dependency', name)
    for tree in ('inputs', 'admission'):
        shutil.copytree(HERE / tree, scratch / tree)

    provenance = decode((HERE / 'PROVENANCE.json').read_bytes())['files']
    for name, ref in provenance.items():
        assert name in pins
        raw = (HERE / name).read_bytes()
        if ref['uncompress']:
            raw = gzip.decompress(raw)
            (scratch / name).with_suffix('').write_bytes(raw)
        assert digest(raw) == ref['sha256'], name
        assert sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == ref['git_blob'], name

    anchor = decode((scratch / 'admission/ANCHORED.json').read_bytes())
    assert anchor['head'] == HEAD and anchor['base_ancestry'] == 'verified'
    for ref in anchor['evidence']:
        relative = PurePosixPath(ref['path'])
        assert len(relative.parts) == 1 and not relative.is_absolute() and '..' not in relative.parts
        assert pins[f'admission/{relative.as_posix()}'] == ref['sha256']

    r58 = decode((scratch / 'inputs/r58/SHA256.json').read_bytes())
    assert pins['inputs/r58/PRICE.json'] == r58['PRICE.json']
    # The independent engine names the same historical price snapshot at its input root.
    shutil.copyfile(scratch / 'inputs/r58/PRICE.json', scratch / 'inputs/BASE-PRICE.json')


def run(engine, *args, seconds=35, check=True):
    argv = [sys.executable, '-I', '-B', str(ENGINES / engine), *map(str, args)]
    return subprocess.run(argv, check=check, capture_output=True, timeout=seconds)


def check_decisions(price, support, geometry, independent):
    assert {r['head'] for r in (price, support, geometry, independent)} == {HEAD}
    assert price['stock']['complete'] and price['stock']['visited'] == 76461
    counts = {
        'consecutive_add_triples': 64080,
        'cross_chart_triples': 5467,
        'three_role_cross_chart_triples': 215,
        'directed_triangle_any_middle': 2,
    }
    assert price['stock']['counts'] == counts
    assert geometry['structural_filter_counts'] == {
        'normalized_windows': 70179,
        'all_add_triples': counts['consecutive_add_triples'],
        'cross_chart': counts['cross_chart_triples'],
        'exactly_three_roles': counts['three_role_cross_chart_triples'],
        'directed_triangles': counts['directed_triangle_any_middle'],
    }
    assert geometry['old_native_paid_histogram'] == price['stock']['native_paid']
    assert sum(geometry['old_native_paid_histogram'].values()) == 6280

    paid, targets = (Counter({int(r): n for r, n in price[name].items()})
                     for name in ('paid', 'targets'))
    assert (sum(paid.values()), sum(targets.values())) == (110536, 22461)
    assert sum(r * (targets[r] - paid[r]) for r in paid.keys() | targets.keys()) == 1424
    assert geometry['baseline_interval'] == price['old_margin']
    assert Fraction(price['old_margin'][1]) < 0
    assert price['whole_one_edit_upper_for_visited_keys'] == '0'
    assert not (price['stock']['keys'] or price['rows'] or price['unvisited_keys'])
    assert not (support['all_verified_keys'] or support['survivors'] or support['unresolved'])
    assert geometry['structural_count'] == geometry['geometry_checked'] == 0
    assert geometry['unknown_inventory_clock'] is geometry['reverse_unvisited_clock'] is None
    assert not (geometry['rows'] or geometry['unresolved_geometry'])
    assert independent['scope_exhausted']
    assert not (independent['rows'] or independent['surviving'] or independent['unresolved'])
    assert set(price['controls']) == {
        'exact_signed_a2', 'wrong_correction_sign', 'funded_hypothetical_price',
        'extra_paid_rank_one_kills',
    }
    assert set(independent['controls']) == {
        'exact_signed_correction_and_two_old_four_new_moves',
        'wrong_correction_sign_rejected', 'public_descent_rejected',
        'reverse_entry_exit_and_ownership',
    }

    diagnostics = geometry['excluded_public_middle_diagnostics']
    assert len(diagnostics) == 2
    observed = []
    for row in diagnostics:
        g = row['geometry']
        middle = row['middle']
        assert middle not in row['owned_roles'] and not g['legal']
        assert len(g['invalid_edges']) == 1
        edge = g['invalid_edges'][0]
        assert edge['role'] == middle and edge['anchor'] == 'before_add'
        observed.append((row['clocks'], [a[-1] for a in row['literal_adds']],
                         middle, edge['from_chart'], edge['to_chart'], edge['clock']))
    assert observed == [
        ([35646, 35648, 35650], [3, 1031, 1031], 699, 1031, 3, 35650),
        ([36496, 36498, 36500], [3, 595, 595], 581, 595, 3, 36498),
    ]


def replay(scratch, emit):
    authenticate(scratch)
    expected = decode((HERE / 'receipts/SHA256.json').read_bytes())
    generated = {}

    def record(name, raw):
        assert digest(raw) == expected[name], name
        generated[name] = raw
        return decode(raw)

    price_path = scratch / 'PRICE.json'
    price_raw = run('a2.py', scratch, 'price').stdout
    price = record('PRICE.json', price_raw)
    price_path.write_bytes(price_raw)
    price_sha = expected['PRICE.json']
    support = record('SUPPORT.json',
                     run('a2.py', scratch, 'support', '--price-sha', price_sha).stdout)
    (scratch / 'SUPPORT.json').write_bytes(generated['SUPPORT.json'])
    reverse = scratch / 'independent/run'
    reverse.parent.mkdir()
    run('reverse_windows.py', scratch / 'inputs', reverse,
        '--primary-price', price_path, '--primary-price-sha', price_sha,
        '--cap', 128, '--seconds', 30)
    geometry = record('GEOMETRY.json', (reverse / 'GEOMETRY.json').read_bytes())
    independent = record('RESULT.json', (reverse / 'RESULT.json').read_bytes())
    assert support['price_sha256'] == geometry['primary_price_sha256'] == price_sha
    assert independent['geometry_sha256'] == expected['GEOMETRY.json']
    check_decisions(price, support, geometry, independent)
    comparison = record('COMPARE.json', run('compare.py', scratch).stdout)
    assert comparison['compatible_saving_upper'] == comparison['unresolved'] == 0

    stale = run('reverse_windows.py', scratch / 'inputs', scratch / 'stale',
                '--primary-price', price_path, '--primary-price-sha', '0' * 64,
                '--seconds', 10, check=False)
    assert stale.returncode == 1 and b'changed primary price' in stale.stderr
    assert not (scratch / 'stale/GEOMETRY.json').exists()
    caller = scratch / 'inputs/7113/CALLER.json'
    caller.write_bytes(caller.read_bytes() + b'\n')
    changed = run('a2.py', scratch, 'price', check=False)
    assert changed.returncode == 1 and b'Changed input inputs/7113/CALLER.json' in changed.stderr
    assert not changed.stdout

    assert generated.keys() == expected.keys()
    if emit is not None:
        emit.mkdir()
        for name, raw in generated.items():
            (emit / name).write_bytes(raw)
    print('PASS_P104_CROSS_CHART_ADD_CONTRACTION_BOUND add_triples=64080 cross_chart=5467 '
          'three_roles=215 public_middle_illegal=2 owned_middle=0 unresolved=0 '
          'saving_upper=0 kappa_change=0')


if __name__ == '__main__':
    assert __debug__, 'assertions are required'
    assert sys.version_info[:2] == (3, 12), 'Python 3.12 required'
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    with TemporaryDirectory(prefix='p104-add-contraction-') as temp:
        replay(Path(temp), args.out)
