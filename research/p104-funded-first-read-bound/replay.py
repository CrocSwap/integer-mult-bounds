"""Replay the exact #7314 funded-first-read contact and price gates."""
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
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError('duplicate JSON key')
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate(scratch):
    pins = decode((HERE / 'LOCAL-PINS.json').read_bytes())
    for name, expected in pins.items():
        relative = PurePosixPath(name)
        assert relative.as_posix() == name and not relative.is_absolute() and '..' not in relative.parts
        if digest((HERE / name).read_bytes()) != expected:
            raise ValueError('changed pinned dependency: ' + name)
    for tree in ('inputs', 'admission'):
        shutil.copytree(HERE / tree, scratch / tree)
    provenance = decode((HERE / 'PROVENANCE.json').read_bytes())['files']
    assert len(provenance) == 8
    for name, ref in provenance.items():
        assert name in pins
        raw = (HERE / name).read_bytes()
        if ref['uncompress']:
            raw = gzip.decompress(raw)
            (scratch / name).with_suffix('').write_bytes(raw)
        assert digest(raw) == ref['sha256'] and sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == ref['git_blob']
    anchor = decode((scratch / 'admission/ANCHORED.json').read_bytes())
    assert anchor['head'] == HEAD and anchor['base_ancestry'] == 'verified'
    for ref in anchor['evidence']:
        relative = PurePosixPath(ref['path'])
        assert len(relative.parts) == 1 and not relative.is_absolute() and '..' not in relative.parts
        assert pins['admission/' + relative.as_posix()] == ref['sha256']
    preceding = decode((scratch / 'inputs/r58/SHA256.json').read_bytes())
    assert preceding['PRICE.json'] == pins['inputs/r58/PRICE.json']
    shutil.copyfile(HERE / 'engines/entrance_price.py', scratch / 'entrance_price.py')


def run(engine, *args, seconds=20, check=True):
    argv = [sys.executable, '-I', '-B', str(HERE / 'engines' / engine), *map(str, args)]
    return subprocess.run(argv, check=check, capture_output=True, timeout=seconds)


def replay(scratch, emit):
    authenticate(scratch)
    expected = decode((HERE / 'receipts/SHA256.json').read_bytes())
    generated = {}

    def record(name, raw, path=None):
        assert digest(raw) == expected[name], ('different receipt', name)
        generated[name] = raw
        if path is not None:
            path.write_bytes(raw)
        return decode(raw)

    price_path = scratch / 'PRICE.json'
    price = record('PRICE.json', run('price.py', scratch).stdout, price_path)
    assert price['head'] == HEAD and price['copies'] == 17
    assert price['paid_positions_after'] == 110519 and price['productive_positions_after'] == 22461
    assert (sum(price['paid'].values()), sum(price['targets'].values())) == (110536, 22461)
    assert price['eligible_stock_upper_before_contact'] == 1083
    assert Fraction(price['old_margin'][1]) < 0 < Fraction(price['one_edit_optimistic_upper']) < 1
    assert all(Fraction(row['margin'][0]) > 0 for row in price['rank_prices'].values())

    index = record('INDEX.json', run('contact_index.py', scratch).stdout, scratch / 'INDEX.json')
    assert index['complete'] and index['events_visited'] == 76461
    assert sum(index['paid_native_moves'].values()) == 6280
    price_sha, index_sha = expected['PRICE.json'], expected['INDEX.json']
    forward = record('CONTACT.json', run('funded.py', scratch, '--price-sha', price_sha,
                                         '--index-sha', index_sha).stdout, scratch / 'CONTACT.json')
    assert forward['visited'] == 1101 and not forward['survivors'] and not forward['unvisited']
    assert len(forward['controls']) == 4

    independent_inputs = scratch / 'reverse-inputs'
    independent_inputs.mkdir()
    for source in ('inputs/7113/CALLER.json', 'inputs/7314/WORD.json.gz', 'admission/ADMITTED.json'):
        shutil.copyfile(scratch / source, independent_inputs / Path(source).name)
    independent_result = scratch / 'independent/RESULT.json'
    independent_result.parent.mkdir()
    reverse = record('REVERSE.json', run('reverse_funded_read.py', '--inputs', independent_inputs,
                                         '--price', price_path, '--price-sha', price_sha).stdout,
                     independent_result)
    assert reverse['status'] == 'EXHAUSTED' and reverse['visited_helpers'] == 1101
    assert not reverse['survivors'] and not reverse['unvisited_roles'] and all(reverse['controls'].values())

    comparison = record('COMPARE.json', run('compare.py', scratch).stdout)
    assert generated['COMPARE.json'] == (HERE / 'receipts/COMPARE.json').read_bytes()
    assert comparison['scope_exhausted'] and comparison['matched_helpers'] == 1101
    assert comparison['remaining'] == comparison['compatible_saving_upper'] == 0
    pairs = comparison['terminal_coincidences']
    assert [(r['h'], r['g'], r['add'], r['final'], r['ascent_rank']) for r in pairs] == [
        (751, 1276, 36439, 115, 5), (1478, 758, 45105, 127, 2)]
    assert all(r['full_lift_deletion_signed_delta_if_legal'] == 0 for r in pairs)
    splits = [s for pair in pairs for s in pair['proper_split_price_only']]
    assert len(splits) == 5 and all(Fraction(s['credit'][1]) < 0 for s in splits)

    stale_price = run('reverse_funded_read.py', '--inputs', independent_inputs, '--price', price_path,
                      '--price-sha', '0' * 64, check=False)
    assert stale_price.returncode == 1 and b'changed input: PRICE.json' in stale_price.stderr and not stale_price.stdout
    stale_index = run('funded.py', scratch, '--price-sha', price_sha, '--index-sha', '0' * 64, check=False)
    assert stale_index.returncode == 1 and b'AssertionError' in stale_index.stderr and not stale_index.stdout
    changed_caller = scratch / 'inputs/7113/CALLER.json'
    changed_caller.write_bytes(changed_caller.read_bytes() + b'\n')
    invalid = run('price.py', scratch, check=False)
    assert invalid.returncode == 1 and b'Changed input inputs/7113/CALLER.json' in invalid.stderr and not invalid.stdout

    assert generated.keys() == expected.keys()
    if emit is not None:
        emit.mkdir()
        for name, raw in generated.items():
            (emit / name).write_bytes(raw)
    print('PASS_P104_FUNDED_FIRST_READ_BOUND helpers=1101 coincidences=2 splits_rejected=5 '
          'eligible=0 unresolved=0 saving_upper=0 kappa_change=0')


if __name__ == '__main__':
    assert __debug__, 'assertions are required'
    assert sys.version_info[:2] == (3, 12), 'CPython 3.12 required'
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    options = parser.parse_args()
    with TemporaryDirectory(prefix='p104-funded-first-read-') as directory:
        replay(Path(directory), options.out)
