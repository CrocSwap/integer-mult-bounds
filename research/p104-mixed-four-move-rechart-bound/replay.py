"""Replay the exact #7314 mixed four-MOVE rechart exclusion."""
from argparse import ArgumentParser
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
HEAD = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'


def unique(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError('duplicate JSON key')
    return value


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate(root):
    pins = decode((HERE / 'LOCAL-PINS.json').read_bytes())
    for name, expected in pins.items():
        rel = PurePosixPath(name)
        assert rel.as_posix() == name and not rel.is_absolute() and '..' not in rel.parts
        if digest((HERE / name).read_bytes()) != expected:
            raise ValueError('changed pinned dependency: ' + name)
    provenance = decode((HERE / 'PROVENANCE.json').read_bytes())['files']
    for name, ref in provenance.items():
        assert name in pins
        raw = (HERE / name).read_bytes()
        if ref['uncompress']:
            raw = gzip.decompress(raw)
        assert digest(raw) == ref['sha256']
        assert sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == ref['git_blob']

    anchor = decode((HERE / 'admission/ANCHORED.json').read_bytes())
    assert anchor['head'] == HEAD and anchor['base_ancestry'] == 'verified'
    for ref in anchor['evidence']:
        rel = PurePosixPath(ref['path'])
        assert len(rel.parts) == 1 and not rel.is_absolute() and '..' not in rel.parts
        assert pins['admission/' + rel.as_posix()] == ref['sha256']

    shutil.copytree(HERE / 'admission', root / 'admission')
    shutil.copytree(HERE / 'inputs', root / 'inputs')
    compressed = root / 'inputs/7113/CALLER.json.gz'
    compressed.with_suffix('').write_bytes(gzip.decompress(compressed.read_bytes()))
    shutil.copyfile(HERE / 'engines/entrance_price.py', root / 'entrance_price.py')
    return root / 'inputs'


def run(engine, *args, timeout=30, check=True):
    argv = [sys.executable, '-I', '-B', str(HERE / 'engines' / engine), *map(str, args)]
    return subprocess.run(argv, check=check, capture_output=True, timeout=timeout)


def replay(scratch, output):
    root = scratch / 'price-inputs'
    source = authenticate(root)
    expected = decode((HERE / 'receipts/SHA256.json').read_bytes())
    generated = {}

    def record(name, raw, path=None):
        assert digest(raw) == expected[name], ('different receipt', name)
        generated[name] = raw
        if path is not None:
            path.write_bytes(raw)
        return decode(raw)

    price_path = scratch / 'price.json'
    price = record('price.json', run('price.py', root).stdout, price_path)
    assert price['head'] == HEAD and price['copies'] == 17
    assert (sum(price['paid'].values()), sum(price['targets'].values())) == (110536, 22461)
    assert price['signed_rank_surplus'] == 1424 and price['empty_credits'] == 0
    assert (price['old_owned_paid'], price['structural_key_upper'], price['max_disjoint_edits']) == (47, 47, 23)
    cap = Fraction(price['one_edit_optimistic_upper'])
    assert 0 < cap < 1 and Fraction(price['all_disjoint_optimistic_upper']) == 23 * cap
    assert 0 < Fraction(price['example_margin'][0])
    assert Fraction(price['one_raw_rank_one_excess_upper']) < 0
    assert len(price['partition_caps']) == 15
    assert cap == 2 * max(Fraction(row['directed_credit'][1]) for row in price['partition_caps'])

    word_path = source / '7314/WORD.json.gz'
    price_sha = expected['price.json']
    forward = record('FORWARD.json', run('contact_gate.py', price_path, word_path, timeout=25).stdout)
    probe = scratch / 'probe'
    probe.mkdir()
    for item, name in (
        (word_path, 'WORD.json.gz'), (source / '7314/EARLY-RESULT.json', 'EARLY-RESULT.json'),
        (source / '7113/CALLER.json', 'CALLER.json'), (source / '7298/pricing.py', 'pricing.py'),
    ):
        shutil.copyfile(item, probe / name)
    reverse = record('REVERSE.json', run('mixed_geometry.py', '--inputs', probe, '--price',
                                       price_path, '--price-sha', price_sha, timeout=25).stdout)
    assert forward['head'] == reverse['head'] == HEAD
    assert forward['price_sha256'] == reverse['price_sha256'] == price_sha
    assert forward['word_sha256'] == reverse['input_sha256']['WORD.json.gz'] == price['word_sha256']
    assert forward['exhausted'] and reverse['status'] == 'EXHAUSTED'
    assert forward['literal_events'] == reverse['word_events'] == 76461
    assert len(forward['cases']) == reverse['mixed_adds'] == 374
    assert not (forward['all_four_moves'] or forward['eligible_four_move_sites'])
    assert not (reverse['structural'] or reverse['priced_dimensions'] or reverse['variants']
                or reverse['unvisited'] or reverse['unresolved'] or reverse['survivors'])
    assert reverse['first_unvisited_contact'] is None
    assert reverse['variant_count'] == reverse['tested_variants'] == 0
    assert reverse['status_counts'] == {'protected_operand': 65, 'neighbor_not_move': 309}
    assert len(forward['controls']) == 2 and len(reverse['controls']) == 3

    word = decode(gzip.decompress(word_path.read_bytes()))
    tape = word['program']
    assert max(map(len, word['frames'])) == 9
    assert sum(event[0] == 'MOVE' and event[-1] is True for event in tape) == 47
    compared = []
    for left, right in zip(forward['cases'], reverse['clock_rows'], strict=True):
        keys = ('clock', 'roles', 'old_chart', 'before', 'after')
        assert all(left[key] == right[key] for key in keys)
        assert not left['has_four_moves']
        assert right['status'] == ('protected_operand' if left['excluded_operand'] else 'neighbor_not_move')
        neighbors = left['before'] + left['after']
        assert any(clock is None or tape[clock][0] != 'MOVE' for clock in neighbors)
        event = tape[left['clock']]
        assert event[0] == 'ADD' and event[1:3] == left['roles'] and event[-1] == left['old_chart']
        compared.append({key:left[key] for key in keys})
    assert len({row['clock'] for row in compared}) == 374
    comparison = {
        'head':HEAD, 'price_sha256':price_sha, 'forward_sha256':expected['FORWARD.json'],
        'reverse_sha256':expected['REVERSE.json'], 'mixed_adds_compared':len(compared),
        'contact_slots_compared':4*len(compared), 'excluded_operands':65,
        'unexcluded_without_four_moves':309, 'full_diagnostic_with_four_moves':0,
        'compatible_saving_upper':'0', 'unresolved':0,
    }
    record('COMPARE.json', (json.dumps(comparison,indent=2,sort_keys=True)+'\n').encode())

    stale = run('mixed_geometry.py', '--inputs', probe, '--price', price_path, '--price-sha', '0'*64,
                timeout=15, check=False)
    assert stale.returncode == 1 and b'changed input: price.json' in stale.stderr and not stale.stdout
    caller = source / '7113/CALLER.json'
    caller.write_bytes(caller.read_bytes() + b'\n')
    rejected = run('price.py', root, check=False)
    assert rejected.returncode == 1 and b'Changed input inputs/7113/CALLER.json' in rejected.stderr
    assert not rejected.stdout

    assert generated.keys() == expected.keys()
    if output is not None:
        output.mkdir()
        for name, raw in generated.items():
            (output / name).write_bytes(raw)
    print('PASS_P104_MIXED_FOUR_MOVE_RECHART_BOUND mixed=374 protected=65 remaining=309 '
          'four_move_sites=0 unresolved=0 saving_upper=0 kappa_change=0')


if __name__ == '__main__':
    assert __debug__ and sys.version_info[:2] == (3, 12), 'CPython 3.12 and assertions required'
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    options = parser.parse_args()
    with TemporaryDirectory(prefix='p104-mixed-four-move-rechart-') as tmp:
        replay(Path(tmp), options.out)
