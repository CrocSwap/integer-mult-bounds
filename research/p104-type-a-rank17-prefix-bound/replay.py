"""Replay the directed price and all exact Type A rank-17 prefix tests."""
from argparse import ArgumentParser
from collections import Counter
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


def read_json(raw):
    return loads(raw, object_pairs_hook=unique)


def digest(raw):
    return sha256(raw).hexdigest()


def source(name):
    path = Path(name)
    if path.is_absolute() or '..' in path.parts or path.as_posix() != name:
        raise ValueError(f'invalid package path {name}')
    return (ROOT / path).read_bytes()


def verify_inputs():
    pins = read_json(source('LOCAL-PINS.json'))
    for name, expected in pins.items():
        if digest(source(name)) != expected:
            raise ValueError(f'changed package dependency {name}')
    provenance = read_json(source('PROVENANCE.json'))
    for name, entry in provenance['files'].items():
        raw = source(name)
        if entry.get('uncompress'):
            raw = decompress(raw)
        assert digest(raw) == entry['sha256']
        assert sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == entry['git_blob']
    old_price = decompress(source('inputs/R92-PRICE.json.gz'))
    price_receipt = read_json(source('inputs/PR7362-SHA256.json'))
    assert digest(old_price) == price_receipt['R92-PRICE.json']
    admitted = read_json(source('inputs/ADMITTED.json'))
    assert admitted['head'] == 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
    assert admitted['caller'] == '07a76c5e2738882c0cb322278e56f6cae3c9885d'
    assert admitted['kappa'] == '0.00364665195644' and admitted['exit'] == 0
    assert admitted['caller_sha256'] == digest(decompress(source('inputs/CALLER.json.gz')))
    assert set(admitted['stages']) == {'native', 'caller', 'early', 'frontier'}
    return old_price


def write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def call(script, *, succeeds=True):
    p = run([sys.executable, '-I', '-B', str(script)], capture_output=True, timeout=28)
    if succeeds:
        if p.returncode:
            sys.stderr.write(p.stderr.decode(errors='replace'))
        p.check_returncode()
    return p


def compare_role10(reverse, forward):
    assert forward['tested_role'] == reverse['role'] == 10
    assert reverse['endpoint_recovered'] and not reverse['unvisited']
    assert [x['cut'] for x in reverse['rows']] == [1743, 1744]
    for a, b in zip(reverse['rows'], forward['cuts'], strict=True):
        assert a['cut'] == b['cut'] and a['status'] == 'foreign body'
        normalized = [[r, q, [stages.count(s) for s in range(1, 18)], re, im]
                      for r, q, stages, re, im in b['entries']]
        assert a['terms'] == sorted(normalized, key=lambda t: t[:3])
        assert a['first_foreign_body'] and b['status'] == 'prefix excluded'
        assert a['first_foreign_body'][2] == [0] * 17


def compare_role7(reverse, forward):
    assert forward['role'] == reverse['role'] == 7
    assert reverse['endpoint_recovered'] and not reverse['unvisited'] and not forward['survivors']
    assert [x['cut'] for x in reverse['rows']] == list(range(1139, 1467))
    assert reverse['counts'] == {'foreign body': 43, 'mixed central parity': 285}
    for a, b in zip(reverse['rows'], forward['rows'], strict=True):
        assert a['cut'] == b['cut'] and a['term_count'] == b['terms']
        assert a['column_sha256'] == b['sha256']
        assert a['first_foreign_body'] == b['first_foreign_body']
        assert not a['allowed_phase_parities'] and b['parity'] == [0, 1]
        assert b['parity_witnesses'] == [a['first_even_phase'], a['first_odd_phase']]


def replay(root, out):
    old_price = verify_inputs()
    expected = read_json(source('receipts/SHA256.json'))
    receipts = {}
    caller = decompress(source('inputs/CALLER.json.gz'))

    def record(name, script):
        raw = call(script).stdout
        assert digest(raw) == expected[name], f'changed deterministic receipt {name}'
        receipts[name] = raw
        return read_json(raw)

    quote = root / 'quote'
    write(quote / 'quote.py', source('engines/quote.py'))
    write(quote / 'inputs/R92-PRICE.json', old_price)
    write(quote / 'inputs/CALLER.json', caller)
    write(quote / 'inputs/pricing.py', source('inputs/pricing.py'))
    price = record('PRICE.json', quote / 'quote.py')
    assert (price['paid'], price['productive'], price['rank_surplus']) == (110519, 22557, 1424)
    assert price['delta'] == {'8': 96, '9': 96, '17': -96}

    stages = {}
    for key, engine in (
        ('ROLE10-REVERSE', 'role10_reverse.py'),
        ('ROLE10-FORWARD', 'forward.py'),
        ('ROLE7-REVERSE', 'role7_reverse.py'),
        ('ROLE7-FORWARD', 'role7_forward.py'),
    ):
        stage = root / key
        write(stage / engine, source(f'engines/{engine}'))
        write(stage / 'inputs/CALLER.json', caller)
        write(stage / 'inputs/PRICE.json', receipts['PRICE.json'])
        if key.endswith('REVERSE'):
            write(stage / 'inputs/reverse.py', source('inputs/reverse.py'))
        if key == 'ROLE7-FORWARD':
            write(stage / 'inputs/forward.py', source('engines/forward.py'))
        stages[key] = record(key + '.json', stage / engine)
    compare_role10(stages['ROLE10-REVERSE'], stages['ROLE10-FORWARD'])
    compare_role7(stages['ROLE7-REVERSE'], stages['ROLE7-FORWARD'])

    bad_caller = root / 'ROLE10-REVERSE'
    write(bad_caller / 'inputs/CALLER.json', caller + b' ')
    p = call(bad_caller / 'role10_reverse.py', succeeds=False)
    assert p.returncode == 1 and not p.stdout and b'changed dependency inputs/CALLER.json' in p.stderr
    bad_price = root / 'ROLE7-FORWARD'
    write(bad_price / 'inputs/PRICE.json', receipts['PRICE.json'] + b' ')
    p = call(bad_price / 'role7_forward.py', succeeds=False)
    assert p.returncode == 1 and not p.stdout and b'changed dependency inputs/PRICE.json' in p.stderr

    assert set(receipts) == set(expected)
    if out:
        for name, raw in receipts.items():
            write(out / name, raw)
    print(dumps({
        'cases': 330, 'excluded': 330, 'unresolved': 0,
        'role10': {'foreign body': 2},
        'role7': dict(Counter(r['status'] for r in stages['ROLE7-REVERSE']['rows'])),
        'deterministic_receipts': len(receipts), 'corrupted_inputs_rejected': 2,
        'kappa_delta': '0',
    }, sort_keys=True))
    print('PASS_P104_TYPE_A_RANK17_PREFIX_BOUND')


def main():
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise SystemExit('CPython 3.12 with assertions is required')
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    with TemporaryDirectory(prefix='p104-rank17-') as path:
        replay(Path(path), args.out)


if __name__ == '__main__':
    main()
