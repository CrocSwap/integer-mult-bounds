"""Replay the exact #7314 funded-donor source-bank exclusion."""
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
    (root / '7314').mkdir()
    shutil.copyfile(HERE / 'inputs/7314/construct.py', root / '7314/construct.py')
    return prior / 'inputs'


def run(engine, *args, timeout=30, check=True):
    argv = [sys.executable, '-I', '-B', str(HERE / 'engines' / engine), *map(str, args)]
    return subprocess.run(argv, check=check, capture_output=True, timeout=timeout)


def replay(scratch, output):
    root = scratch / 'price-inputs'
    source = authenticate(root)
    expected = decode((HERE / 'receipts/SHA256.json').read_bytes())
    predecessor = decode((HERE / 'inputs/r65/SHA256.json').read_bytes())
    assert predecessor['price.json'] == expected['price.json']
    generated = {}

    def record(name, raw, path=None):
        assert digest(raw) == expected[name], ('different receipt', name)
        generated[name] = raw
        if path is not None:
            path.write_bytes(raw)
        return decode(raw)

    price_path = scratch / 'price.json'
    price = record('price.json', run('price.py', root).stdout, price_path)
    assert price['head'] == HEAD and price['copies'] == 17 and price['stock_edits_cap'] == 1
    assert (price['old_paid_positions'], price['new_paid_positions']) == (110536, 110519)
    assert (price['productive_fields'], price['rank_surplus'], price['empty_root_credits']) == (22461, 1424, 0)
    assert price['paid_delta'] == {'1': -17, '5': -17, '6': 17} and not price['target_delta']
    assert 0 < Fraction(price['credit'][0]) <= Fraction(price['one_edit_optimistic_upper']) < 1
    assert Fraction(price['complete_new_margin_at_old_crossing_upper'][0]) > 0
    assert Fraction(price['complete_margin_with_one_extra_rank_one_position'][1]) < 0
    assert Fraction(price['price_only_derivative_bound'][1]) < 0
    lo, hi = map(Fraction, price['price_only_raw_crossing_bracket'])
    assert Fraction(price['crossing_upper']) < lo < hi < Fraction(price['bit_bound'])

    word = source / '7314/WORD.json.gz'
    price_sha = expected['price.json']
    (scratch / 'inputs').mkdir()
    shutil.copyfile(HERE / 'inputs/replay_core.py', scratch / 'inputs/replay_core.py')
    shutil.copyfile(HERE / 'inputs/r66/support.json', scratch / 'support.json')
    shutil.copyfile(HERE / 'engines/source_span.py', scratch / 'source_span.py')
    first = decode((scratch / 'support.json').read_bytes())
    assert first['unvisited_cuts'] == [48185]
    assert first['price_sha256'] == price_sha and first['records'][0]['eligible_roles'] == []
    controls = record('CONTROLS.json', run('source_span.py', scratch, '--controls-only', timeout=15).stdout)
    assert len(controls['controls']) == 5

    post_path = scratch / 'POST.json'
    run('post_span.py', scratch, '--out', post_path, timeout=15)
    post = record('POST.json', post_path.read_bytes())
    assert post['price_sha256'] == price_sha and post['first_support_sha256'] == digest((scratch / 'support.json').read_bytes())
    assert post['visited_prefix_events'] == 48185 and post['checked_copies'] == 1
    assert not post['unvisited_cuts'] and len(post['controls']) == 4
    before, after = post['records']
    assert (before['cut'], before['chart'], before['disposition']) == (48182, 739, 'confirmed_empty_first_bank')
    assert (after['cut'], after['chart'], after['disposition']) == (48185, 127, 'exact_coordinate_dual')
    assert len(after['eligible_roles']) == len(set(after['eligible_roles'])) == 673
    assert after['dual'] == {'863': '1'} and after['dual_target_value'] == '1'
    assert not (after['eligible_owned_roles'] or after['roles_with_x863'])

    projection = record('SCALAR.json', run('scalar_prefix.py', word, price_path, timeout=15).stdout)
    assert projection['price_sha256'] == price_sha and projection['word_sha256'] == post['word_sha256']
    assert projection['literal_prefix_events'] == 48185 and not projection['unresolved']
    assert len(projection['controls']) == 3 and projection['missing_donor_coefficient'] == '-2'
    for trace in (projection['cuts'], projection['fused_cuts']):
        assert trace['48182']['chart'] == 739 and not trace['48182']['roles']
        bank = trace['48185']
        assert bank['chart'] == 127 and bank['roles'] == after['eligible_roles']
        assert not (bank['owned'] or bank['nonzero'])

    price_path.write_bytes(price_path.read_bytes() + b'\n')
    rejected = run('scalar_prefix.py', word, price_path, timeout=15, check=False)
    assert rejected.returncode == 1 and b'changed dependency: price.json' in rejected.stderr
    assert not rejected.stdout
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
    print('PASS_P104_FUNDED_DONOR_SOURCE_SPAN cuts=2 pre_donors=0 post_donors=673 '
          'nonzero_x863=0 missing=-2 unresolved=0 saving_upper=0 kappa_change=0')


if __name__ == '__main__':
    assert __debug__ and sys.version_info[:2] == (3, 12), 'CPython 3.12 and assertions required'
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    options = parser.parse_args()
    with TemporaryDirectory(prefix='p104-funded-donor-source-') as tmp:
        replay(Path(tmp), options.out)
