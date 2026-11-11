"""Replay the exact #7314 funded-donor fusion span exclusion."""
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
    span = record('SPAN.json', run('span.py', price_path, word, '--cap', 512, '--seconds', 27).stdout)
    assert span['stage'] == 'exhausted' and span['omitted'] is None and not span['witness']
    assert (span['cut_count'], span['visits'], span['distinct'], span['rank']) == (52, 1003, 39, 25)
    assert span['zeros'] == 0 and span['duplicates'] == 964
    assert len(span['keys']) == len({tuple(key) for key in span['keys']}) == 39
    assert span['residual'] and len(span['controls']) == 2

    probe = scratch / 'probe'
    probe.mkdir()
    shutil.copyfile(price_path, probe / 'price.json')
    shutil.copyfile(word, probe / 'WORD.json.gz')
    independent = record('DUAL.json', run('suffix_dual.py', '--inputs', probe).stdout)
    assert independent['status'] == 'EXACT_SEPARATION' and len(independent['controls']) == 2
    assert not (independent['unvisited_keys'] or independent['nonzero_candidate_pairings'])
    assert independent['unvisited_clock'] is None and len(independent['representative_cuts']) == 82
    assert len(independent['tested']) == independent['eligible_representative_sites'] == 59
    assert all(Fraction(row[2]) == 0 for row in independent['tested'])
    assert span['price_sha256'] == independent['price_sha256'] == price_sha
    assert span['word_sha256'] == independent['word_sha256'] == price['word_sha256']
    assert span['target'] == independent['target_response']
    assert span['separator']['dual'] == independent['terminal_covector'] == {'1109': '1'}
    assert span['separator']['target_value'] == independent['target_pairing'] == '-8'

    stale = probe / 'price.json'
    stale.write_bytes(stale.read_bytes() + b'\n')
    rejected = run('suffix_dual.py', '--inputs', probe, check=False)
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
    print('PASS_P104_FUNDED_DONOR_FUSION_SPAN visits=1003 distinct=39 rank=25 '
          'independent_cuts=82 target_e1109=-8 unresolved=0 saving_upper=0 kappa_change=0')


if __name__ == '__main__':
    assert __debug__ and sys.version_info[:2] == (3, 12), 'CPython 3.12 and assertions required'
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    options = parser.parse_args()
    with TemporaryDirectory(prefix='p104-funded-donor-fusion-') as tmp:
        replay(Path(tmp), options.out)
