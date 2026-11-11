"""Authenticate and reproduce the exact two-transfer Type B exclusion."""
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
UPPER = Fraction('72803865248455278947107190998539661213280058633/'
                 '625000000000000000000000000000000000000000000000')


def unique(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError('duplicate JSON key')
    return value


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique)


def authenticate(scratch):
    pins = decode((HERE / 'LOCAL-PINS.json').read_bytes())
    for name, expected in pins.items():
        rel = PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or rel.as_posix() != name:
            raise ValueError('invalid pinned path: ' + name)
        if sha256((HERE / name).read_bytes()).hexdigest() != expected:
            raise ValueError('changed pinned dependency: ' + name)
    for folder in ('inputs', 'admission'):
        shutil.copytree(HERE / folder, scratch / folder)
    sources = decode((HERE / 'PROVENANCE.json').read_bytes())['files']
    assert len(sources) == 5
    for name, source in sources.items():
        assert name in pins
        raw = (HERE / name).read_bytes()
        if source['uncompress']:
            raw = gzip.decompress(raw)
            (scratch / name).with_suffix('').write_bytes(raw)
        assert sha256(raw).hexdigest() == source['sha256']
        assert sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == source['git_blob']
    anchor = decode((scratch / 'admission/ANCHORED.json').read_bytes())
    for entry in anchor['evidence']:
        rel = PurePosixPath(entry['path'])
        assert len(rel.parts) == 1 and not rel.is_absolute() and '..' not in rel.parts
        assert pins['admission/' + rel.as_posix()] == entry['sha256']


def run(engine, *args, seconds=10, check=True):
    argv = [sys.executable, '-I', '-B', str(HERE / 'engines' / engine), *map(str, args)]
    return subprocess.run(argv, check=check, capture_output=True, timeout=seconds)


def replay(scratch, emit):
    authenticate(scratch)
    expected = decode((HERE / 'receipts/SHA256.json').read_bytes())
    generated = {}

    def record(name, raw, path=None):
        assert sha256(raw).hexdigest() == expected[name], ('different replay receipt', name)
        generated[name] = raw
        if path is not None:
            path.write_bytes(raw)
        return decode(raw)

    price = scratch / 'PRICE.json'
    price_sha = expected['PRICE.json']
    quoted = record('PRICE.json', run('two_phase.py', scratch, 'price').stdout, price)
    assert len(quoted['keys']) == 1950 and Fraction(quoted['whole_optimistic_upper']) == UPPER
    assert (sum(quoted['complete_paid'].values()), sum(quoted['complete_targets'].values()), quoted['copies']) == (110536, 22461, 17)
    for row in quoted['prices'].values():
        delta = {int(rank): units for rank, units in row['net_delta'].items()}
        assert sum(delta.values()) == sum(rank * units for rank, units in delta.items()) == 0
        assert Fraction(row['margin'][0]) > 0 > Fraction(row['extra_paid_rank_one_margin'][1])

    mod = record('BODY1.json', run('two_phase.py', scratch, 'body-one', '--price-sha', price_sha,
                                  seconds=25).stdout, scratch / 'BODY1.json')
    assert mod['visited'] == 1950 and not mod['survivors'] and not mod['unvisited']
    assert mod['controls'] == ['different_orthogonal_bases_cancel_jointly','one_replaced_reflection_fails']

    inputs = scratch / 'independent-inputs'
    inputs.mkdir()
    shutil.copyfile(scratch / 'inputs/7113/CALLER.json', inputs / 'CALLER.json')
    shutil.copyfile(scratch / 'admission/ADMITTED.json', inputs / 'ADMITTED.json')
    exact_out = scratch / 'independent' / 'RESULT.json'
    exact_out.parent.mkdir()
    argv = ('--inputs', inputs, '--price', price, '--price-sha')
    exact = record('EXACT.json', run('four_edits.py', *argv, price_sha, seconds=30).stdout, exact_out)
    assert exact['status'] == 'EXHAUSTED' and exact['tested'] == 1950
    assert exact['controls'] == {'fractional_noncommuting_direct_columns':9, 'two_individually_failing_pairs_cancel':True}
    comparison = record('COMPARE.json', run('compare.py', scratch).stdout)
    assert (comparison['all_keys_matched'], comparison['body_one_survivors'], comparison['unresolved'],
            comparison['compatible_saving_in_scope']) == (1950, 0, 0, 0)
    assert Fraction(comparison['whole_optimistic_upper']) == UPPER

    # Controls mutate disposable paths only. Neither invalid input reaches the endpoint test.
    stale = run('four_edits.py', *argv, '0' * 64, check=False)
    assert stale.returncode == 1 and b'changed input: PRICE.json' in stale.stderr and not stale.stdout
    caller = scratch / 'inputs/7113/CALLER.json'
    caller.write_bytes(caller.read_bytes() + b'\n')
    changed = run('two_phase.py', scratch, 'price', check=False)
    assert changed.returncode == 1 and b'Changed input inputs/7113/CALLER.json' in changed.stderr and not changed.stdout

    assert generated.keys() == expected.keys()
    if emit is not None:
        emit.mkdir()
        for name, raw in generated.items():
            (emit / name).write_bytes(raw)
    print('PASS_P104_TWO_TYPE_B_PHASE_TRANSFERS cases=1950 survivors=0 unresolved=0 '
          'compatible_saving=0 kappa_change=0')


if __name__ == '__main__':
    assert __debug__, 'assertions are required'
    assert sys.version_info[:2] == (3, 12), 'CPython 3.12 required'
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    options = parser.parse_args()
    with TemporaryDirectory(prefix='p104-two-type-b-phase-') as root:
        replay(Path(root), options.out)
