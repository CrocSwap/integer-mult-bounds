"""Price and replay the exact #7314 guarded owned-capture exclusion."""
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

    round63 = root / 'round63'
    prior = round63 / 'price-inputs'
    prior.mkdir(parents=True)
    shutil.copytree(HERE / 'admission', prior / 'admission')
    for name in ('7113', '7298', '7314'):
        shutil.copytree(HERE / 'inputs' / name, prior / 'inputs' / name)
    compressed = prior / 'inputs/7113/CALLER.json.gz'
    compressed.with_suffix('').write_bytes(gzip.decompress(compressed.read_bytes()))
    shutil.copyfile(HERE / 'engines/entrance_price.py', prior / 'entrance_price.py')
    shutil.copyfile(HERE / 'engines/r63/price.py', round63 / 'price.py')
    prior_price = (HERE / 'inputs/r63/price.json').read_bytes()
    assert digest(prior_price) == decode((HERE / 'inputs/r63/SHA256.json').read_bytes())['price.json']
    (round63 / 'price.json').write_bytes(prior_price)
    shutil.copytree(HERE / 'inputs/r41', root / 'round41')
    (root / '7314').mkdir()
    shutil.copyfile(HERE / 'inputs/7314/construct.py', root / '7314/construct.py')
    return prior / 'inputs'


def run(engine, *args, timeout=25, check=True, cwd=None):
    argv = [sys.executable, '-I', '-B', str(HERE / 'engines' / engine), *map(str, args)]
    return subprocess.run(argv, check=check, capture_output=True, timeout=timeout, cwd=cwd)


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

    price_path = scratch / 'price-stock.json'
    price = record('price-stock.json', run('price.py', root).stdout, price_path)
    assert price['head'] == HEAD and price['copies'] == 17 and price['stock_edits_cap'] == 1
    assert (sum(price['paid'].values()), sum(price['targets'].values()), price['rank_surplus']) == (110536, 22461, 1424)
    assert price['paid_owned_histogram'] == {'1':20,'2':9,'3':2,'4':13,'5':2,'6':1}
    assert price['paid_owned_moves'] == 47 and price['owned_lifetimes'] == 72
    assert price['copy_capture_paid_lifetimes'] == price['empty_root_credits'] == 0
    assert Fraction(price['whole_stock_relaxation']['credit'][1]) == Fraction(price['one_edit_optimistic_upper_before_structure'])
    assert all(Fraction(row['credit'][0]) >= 17 for row in price['per_rank'].values())

    word = source / '7314/WORD.json.gz'
    lead_path = scratch / 'INVENTORY.json'
    price_sha = expected['price-stock.json']
    forward = record('INVENTORY.json', run('inventory.py', '--word', word, '--price', price_path,
                                          '--price-sha', price_sha, '--lifetimes', 72, '--seconds', 17).stdout, lead_path)
    reverse_path = scratch / 'REVERSE.json'
    reverse = record('REVERSE.json', run('reverse_lifetimes.py', source, '--price', price_path,
                                        '--price-sha', price_sha, '--seconds', 20).stdout, reverse_path)
    assert len(forward['controls']) == 4 and len(reverse['controls']) == 6
    compare = record('COMPARE.json', run('compare.py', lead_path, reverse_path, word).stdout)
    assert compare['lifetimes_compared'] == 72
    assert compare['unresolved'] == compare['structural_survivors'] == 0
    assert len(compare['strictly_lower_near_cases']) == 6
    sites = record('price-sites.json', run('price.py', root, '--stock', price_path, '--stock-sha', price_sha,
                                         '--inventory', lead_path, '--inventory-sha', expected['INVENTORY.json']).stdout)
    assert sites['structure_complete'] and sites['priced_survivors'] == 0 and not sites['prices']
    assert sites['one_edit_optimistic_upper'] == compare['compatible_saving_upper'] == '0'

    shutil.copyfile(lead_path, root / 'INVENTORY.json')
    lower_price = scratch / 'price-six.json'
    quoted = record('price-six.json', run('price-six.py', cwd=scratch).stdout, lower_price)
    assert len(quoted['cases']) == 6 and quoted['lifetime_cap'] == 1
    assert Fraction(quoted['one_edit_optimistic_upper']) > 0
    lower = record('LOWER.json', run('lower_projection.py', lower_price, word, timeout=15).stdout)
    assert lower['complete'] and not lower['unresolved'] and len(lower['controls']) == 3
    assert lower['price_sha256'] == expected['price-six.json']
    assert [(r['role'], r['move'], r['read']) for r in lower['cases']] == [
        (r['role'], r['move_clock'], r['reads'][0]['clock']) for r in compare['strictly_lower_near_cases']
    ]
    assert sum(len(r['donor_roles']) for r in lower['cases']) == 28
    assert sum(r['public_donors'] for r in lower['cases']) == 19

    stale = run('reverse_lifetimes.py', source, '--price', price_path, '--price-sha', '0' * 64, check=False)
    assert stale.returncode == 1 and b'changed price receipt' in stale.stderr and not stale.stdout
    caller = source / '7113/CALLER.json'
    caller.write_bytes(caller.read_bytes() + b'\n')
    changed = run('price.py', root, check=False)
    assert changed.returncode == 1 and b'Changed input inputs/7113/CALLER.json' in changed.stderr and not changed.stdout

    assert generated.keys() == expected.keys()
    if output is not None:
        output.mkdir()
        for name, raw in generated.items():
            (output / name).write_bytes(raw)
    print('PASS_P104_GUARDED_OWNED_CAPTURE_BOUND lifetimes=72 owned_paid=47 higher=0 lower_excluded=6 '
          'unresolved=0 saving_upper=0 kappa_change=0')


if __name__ == '__main__':
    assert __debug__ and sys.version_info[:2] == (3, 12), 'CPython 3.12 and assertions required'
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    options = parser.parse_args()
    with TemporaryDirectory(prefix='p104-guarded-owned-capture-') as tmp:
        replay(Path(tmp), options.out)
