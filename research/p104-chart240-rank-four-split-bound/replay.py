"""Price and replay the exact #7314 chart-240 prefix obstruction."""
from argparse import ArgumentParser
from fractions import Fraction
import gzip
from hashlib import sha1, sha256
import json
from math import isqrt
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
    for tree in ('admission', 'inputs'):
        shutil.copytree(HERE / tree, root / tree)
    provenance = decode((HERE / 'PROVENANCE.json').read_bytes())['files']
    assert len(provenance) == 8
    for name, ref in provenance.items():
        assert name in pins
        raw = (HERE / name).read_bytes()
        if ref['uncompress']:
            raw = gzip.decompress(raw)
            (root / name).with_suffix('').write_bytes(raw)
        assert digest(raw) == ref['sha256'] and sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == ref['git_blob']
    anchor = decode((root / 'admission/ANCHORED.json').read_bytes())
    assert anchor['head'] == HEAD and anchor['base_ancestry'] == 'verified'
    for ref in anchor['evidence']:
        rel = PurePosixPath(ref['path'])
        assert len(rel.parts) == 1 and not rel.is_absolute() and '..' not in rel.parts
        assert pins['admission/' + rel.as_posix()] == ref['sha256']
    shutil.copyfile(HERE / 'engines/entrance_price.py', root / 'entrance_price.py')


def run(engine, *args, timeout=15, check=True):
    command = [sys.executable, '-I', '-B', str(HERE / 'engines' / engine), *map(str, args)]
    return subprocess.run(command, check=check, capture_output=True, timeout=timeout)


def replay(scratch, output):
    inputs = scratch / 'price-inputs'
    inputs.mkdir()
    authenticate(inputs)
    expected = decode((HERE / 'receipts/SHA256.json').read_bytes())
    generated = {}

    def record(name, raw, path=None):
        assert digest(raw) == expected[name], ('different receipt', name)
        generated[name] = raw
        if path is not None:
            path.write_bytes(raw)
        return decode(raw)

    price_path = scratch / 'price.json'
    price = record('price.json', run('price.py', inputs).stdout, price_path)
    assert price['head'] == HEAD and price['copies'] == 17 and price['stock_edits_cap'] == 1
    assert (sum(price['paid'].values()), sum(price['targets'].values()), price['rank_surplus']) == (110536, 22461, 1424)
    assert len(price['split_prices']) == 2
    for row in price['split_prices'].values():
        assert not row['paid_delta'] and sum(row['targets'].values()) == 22478
        assert Fraction(row['margin'][0]) > 0 > Fraction(row['margin_with_one_extra_rank_one_position'][1])
    assert Fraction(price['one_edit_optimistic_upper']) == Fraction(price['split_prices']['2+2']['credit'][1]) < Fraction(51, 125)

    price_sha = expected['price.json']
    geometry_path = scratch / 'independent/RESULT.json'
    geometry_path.parent.mkdir()
    geometry = record('GEOMETRY.json', run('reverse_banks.py', inputs / 'inputs', '--price', price_path,
                                           '--price-sha', price_sha, '--seconds', 15).stdout, geometry_path)
    assert geometry['scope_complete'] and geometry['visited_events'] == 76461 and not geometry['overflow_keys']
    assert not geometry['keys_by_tier']['mixed_863']
    assert geometry['covered_cuts'] == {'cohort_rank_two': 4126, 'mixed_863_without_peer': 25}
    assert geometry['occupied_segments'] == {'cohort_rank_two': 28, 'mixed_863_without_peer': 6}
    assert len(geometry['representative_keys']) == 35 and len(geometry['controls']) == 4
    assert len(geometry['rank_two_charts']) == 11
    assert {r['chart'] for r in geometry['segments']} == {385, 388, 389}

    word = inputs / 'inputs/7314/WORD.json.gz'
    exact = record('EXACT.json', run('exact_prefix.py', word, geometry_path, '--seconds', 15).stdout)
    modular = record('MODULAR.json', run('modular_prefix.py', scratch).stdout)
    prime = modular['modulus']
    assert prime == 65521 and all(prime % i for i in range(2, isqrt(prime) + 1))
    assert not (exact['unresolved'] or exact['prefix_survivors'] or modular['unresolved'])
    assert len(exact['controls']) == 2
    keys = []
    for bank, q, f in zip(geometry['segments'], exact['decisions'], modular['decisions'], strict=True):
        cut, chart = bank['cut'], bank['chart']
        assert (q['cut'], q['chart']) == (f['cut'], f['chart']) == (cut, chart)
        assert q['public_basis'] == f['rows'] == bank['public_bank']
        assert not q['pure_prefix'] and not q['nonzero_prefix']
        assert q['exterior_rank'] == len(f['rows']) == len(set(f['columns']))
        assert q['pivots'] == f['pivots'] == bank['pivots']
        keys.extend([cut, chart, pivot] for pivot in bank['pivots'])
    assert sorted(keys) == sorted(geometry['representative_keys'])

    stale = run('reverse_banks.py', inputs / 'inputs', '--price', price_path, '--price-sha', '0' * 64, check=False)
    assert stale.returncode == 1 and b'changed price receipt' in stale.stderr and not stale.stdout
    caller = inputs / 'inputs/7113/CALLER.json'
    caller.write_bytes(caller.read_bytes() + b'\n')
    changed = run('price.py', inputs, check=False)
    assert changed.returncode == 1 and b'Changed input inputs/7113/CALLER.json' in changed.stderr and not changed.stdout
    assert generated.keys() == expected.keys()
    if output is not None:
        output.mkdir()
        for name, raw in generated.items():
            (output / name).write_bytes(raw)
    print('PASS_P104_CHART240_FIXED_PAID_SPLIT mixed_peers=0 rank_two_keys=35 '
          'prefix_survivors=0 unresolved=0 saving_upper=0 kappa_change=0')


if __name__ == '__main__':
    assert __debug__ and sys.version_info[:2] == (3, 12), 'CPython 3.12 and assertions required'
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    options = parser.parse_args()
    with TemporaryDirectory(prefix='p104-chart240-fixed-paid-split-') as tmp:
        replay(Path(tmp), options.out)
