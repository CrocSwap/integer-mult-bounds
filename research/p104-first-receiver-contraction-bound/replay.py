"""Reproduce both chart-652 first-receiver exclusions and the complete price."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError('duplicate JSON key')
    return result


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def source(name):
    path = Path(name)
    if path.is_absolute() or '..' in path.parts or path.as_posix() != name:
        raise ValueError(f'invalid package path {name}')
    return (ROOT / path).read_bytes()


def dependencies():
    pins = decode(source('LOCAL-PINS.json'))
    for name, expected in pins.items():
        if digest(source(name)) != expected:
            raise ValueError(f'changed package dependency {name}')
    for name, entry in decode(source('PROVENANCE.json'))['files'].items():
        raw = source(name)
        assert digest(raw) == entry['sha256']
        assert sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == entry['git_blob']
    price = decompress(source('inputs/R92-PRICE.json.gz'))
    assert digest(price) == decode(source('inputs/PR7362-SHA256.json'))['R92-PRICE.json']
    a = decode(source('inputs/ADMITTED.json'))
    assert a['head'] == 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
    assert a['caller'] == '07a76c5e2738882c0cb322278e56f6cae3c9885d'
    assert a['kappa'] == '0.00364665195644' and a['exit'] == 0
    assert a['inputs']['WORD.json.gz'] == digest(source('inputs/7334-WORD.json.gz'))
    assert set(a['stages']) == {'native', 'early', 'caller', 'frontier'}
    return price


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def call(script, *args, succeeds=True):
    result = run([sys.executable, '-I', '-B', str(script), *map(str, args)],
                 capture_output=True, timeout=22)
    if succeeds:
        if result.returncode:
            sys.stderr.write(result.stderr.decode(errors='replace'))
        result.check_returncode()
    return result


def verify_agreement(price, left, raw, gate, right, full):
    assert price['paid_delta'] == {'1': -17, '2': -17, '4': -17, '7': 17}
    assert (price['paid_after'], price['productive'], price['rank_surplus']) == (110485, 22461, 1424)
    assert price['ordinary_reserve'] == 64328 and price['one_owned_slot_at_cut']
    assert Q('0.4127144682830787') < Q(price['complete']['old_crossing_upper'][0])
    assert Q(price['complete']['old_crossing_upper'][1]) < Q('0.4127144682830788') < 1
    assert Q(price['complete']['probe'][0]) > Q('0.4123270058096044')
    assert Q(price['complete']['moonshot'][1]) < Q('-139.3135861810168')
    assert left['cut'] == raw['cut'] == gate['cut'] == right['cut'] == full['key'][0] == 42651
    assert left['carrier'] == raw['source_coordinate'] == '-1'
    assert left['receiver'] == raw['receiver_old_coordinate'] == gate['old_receiver'] == '1/2'
    assert left['required'] == raw['required_coordinate'] == gate['required_add'] == '-1/2'
    assert left['post_receiver'] == gate['required_receiver_return'] == gate['necessary_receiver_diagonal'] == '0'
    assert raw['bank_owned'] == [] and raw['bank_public'] == [165, 586, 793]
    assert left['donors'] == gate['distinct_donor_values'] == {'165': '0', '586': '0'}
    assert gate['status'] == full['status'] == 'excluded'
    assert price == right['price'] and right['donor_roles'] == [165, 586]
    assert right['exact']['separator'] == full['witness']['covector'] == {'893': '1'}
    assert right['target_coefficient'] == full['witness']['target'] == '1/2'
    assert right['donor_coefficients'] == list(full['witness']['donors'].values()) == ['0', '0']
    assert full['witness']['receiver'] == '1/2' and full['witness']['source'] == '0'
    assert (full['proof']['donor_rank'], full['proof']['augmented_rank']) == (2, 3)
    assert len(full['rows']) == 4


def replay(tmp, out):
    price_source = dependencies()
    expected = decode(source('receipts/SHA256.json'))
    outputs = {}
    word = source('inputs/7334-WORD.json.gz')

    def record(name, script, *args):
        data = call(script, *args).stdout
        assert digest(data) == expected[name]
        assert data == source(f'receipts/{name}')
        outputs[name] = data
        return decode(data)

    forward159, reverse, forward160 = (tmp / name for name in ('forward159', 'reverse', 'forward160'))
    for root, script in ((forward159, 'r159_forward.py'), (forward160, 'r160_forward.py'),
                         (reverse, 'first_receiver.py'), (reverse, 'local_gate.py'), (reverse, 'full_receiver.py')):
        write(root / script, source(f'engines/{script}'))
    for name in ('7334-WORD.json.gz', '7274-WORD.json.gz', 'R29-RESULT.json', 'PLAN.md', 'reverse_span.py'):
        write(reverse / 'inputs' / name, source(f'inputs/{name}'))
    write(forward159 / 'inputs/CURRENT.json.gz', word)
    write(forward160 / 'inputs/WORD.json.gz', word)
    write(forward160 / 'inputs/R92-PRICE.json', price_source)
    for name in ('pricing.py', 'aggregate.py', 'donor_span.py'):
        write(forward160 / 'inputs' / name, source(f'inputs/{name}'))

    price = record('PRICE.json', forward160 / 'r160_forward.py', '--price')
    f159 = record('R159-FORWARD.json', forward159 / 'r159_forward.py')
    r159 = record('R159-REVERSE.json', reverse / 'first_receiver.py')
    write(reverse / 'inputs/RESULT.json', outputs['R159-REVERSE.json'])
    gate = record('R159-GATE.json', reverse / 'local_gate.py', reverse / 'inputs/RESULT.json')
    write(reverse / 'inputs/GATE.json', outputs['R159-GATE.json'])
    write(reverse / 'inputs/r159_reverse.py', source('engines/first_receiver.py'))
    write(forward160 / 'inputs/R159-IMPULSE.json', outputs['R159-FORWARD.json'])
    f160 = record('R160-FORWARD.json', forward160 / 'r160_forward.py')
    r160 = record('R160-REVERSE.json', reverse / 'full_receiver.py')
    verify_agreement(price, f159, r159, gate, f160, r160)

    for name, driver in (('inputs/GATE.json', 'full_receiver.py'),
                         ('inputs/7334-WORD.json.gz', 'first_receiver.py')):
        path = reverse / name
        raw = path.read_bytes()
        path.write_bytes(raw + b' ')
        check = call(reverse / driver, succeeds=False)
        assert check.returncode == 1 and not check.stdout and b'changed dependency' in check.stderr
        path.write_bytes(raw)

    assert set(outputs) == set(expected)
    if out:
        for name, data in outputs.items():
            write(out / name, data)
    print(dumps({'cases': 1, 'repair_scopes_excluded': 2, 'kappa_delta': '0',
                 'deterministic_receipts': len(outputs), 'corrupted_inputs_rejected': 2}, sort_keys=True))
    print('PASS_P104_FIRST_RECEIVER_CONTRACTION_BOUND')


def main():
    if sys.implementation.name != 'cpython' or sys.version_info[:2] != (3, 12) or not __debug__:
        raise SystemExit('CPython 3.12 with assertions is required')
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    with TemporaryDirectory(prefix='p104-first-receiver-') as path:
        replay(Path(path), args.out)


if __name__ == '__main__':
    main()
