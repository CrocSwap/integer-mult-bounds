"""Reproduce both exact solvers for the one-vector interior rechart family."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path, PurePosixPath
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
FILES = {'closure.py', 'cut_flow.py', 'reverse_inventory.py', 'PROVENANCE.json',
         'inputs/7334-WORD.json.gz', 'inputs/pricing.py', 'inputs/inventory.py',
         'receipts/LEAD.json', 'receipts/INDEPENDENT.json'}


def unique(pairs):
    out = dict(pairs)
    assert len(out) == len(pairs), 'duplicate JSON field'
    return out


def check_bytes(data, expected):
    assert sha256(data).hexdigest() == expected, 'immutable input mismatch'


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    manifest = loads((ROOT / 'PINS.json').read_bytes(), object_pairs_hook=unique)
    assert set(manifest) == FILES
    for name, digest in manifest.items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        check_bytes((ROOT / path).read_bytes(), digest)
    # Corrupt a proof-relevant source in memory and confirm the pin rejects it.
    name = 'inputs/pricing.py'
    try:
        check_bytes((ROOT / name).read_bytes() + b'\n', manifest[name])
    except AssertionError:
        pass
    else:
        raise AssertionError('altered tariff passed its pin')

    actual = []
    for script, expected in (('closure.py', 'LEAD'), ('cut_flow.py', 'INDEPENDENT')):
        output = run([executable, '-I', '-B', str(ROOT / script)], check=True,
                     capture_output=True, timeout=63).stdout
        result = loads(output, object_pairs_hook=unique)
        assert result == loads((ROOT / 'receipts' / (expected + '.json')).read_bytes(),
                               object_pairs_hook=unique)
        actual.append(result)

    lead, independent = actual
    for key, expected in (('groups', 1517), ('eligible_groups', 482), ('incident_edges', 2292)):
        assert lead[key] == independent[key] == expected
    assert not lead['capped'] and not independent['capped'] and lead['witness'] is None
    assert lead['vectors_checked'] == independent['vector_cap'] == 511
    assert {r: [Fraction(x, lead['scale']) for x in inc] for r, inc in lead['rounding_intervals'].items()} == {
        r: [Fraction(x, independent['scale']) for x in inc] for r, inc in independent['increments'].items()}
    assert list(range(1, 512)) == [r['vector'] for r in lead['results']]
    for a, b in zip(lead['results'], independent['results'], strict=True):
        for key in ('vector', 'variables', 'implications'):
            assert a[key] == b[key]
        assert a['upper_scaled'] == b['upper_scaled'] == 0
        assert b['source_benefit_scaled'] == b['flow_scaled'] > 0
    print('PASS_INTERIOR_VECTOR_GROWTH_BOUND: 511 vectors, 482 groups, 2292 edges, exact upper 0')


if __name__ == '__main__':
    main()
