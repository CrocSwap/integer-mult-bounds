"""Replay one fixed chart-907 delayed correction exclusion."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path, PurePosixPath
from runpy import run_path
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent


def unique(pairs):
    values = dict(pairs)
    assert len(values) == len(pairs), 'duplicate JSON key'
    return values


def dot(row, probe):
    return sum(Fraction(value) * Fraction(probe.get(key, 0)) for key, value in row.items())


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    manifest = loads((ROOT / 'PINS.json').read_bytes(), object_pairs_hook=unique)
    names = {f.relative_to(ROOT).as_posix() for folder in ('engines', 'inputs', 'receipts')
             for f in (ROOT / folder).iterdir() if f.is_file()}
    assert set(manifest) == names | {'PROVENANCE.json'}
    for name, digest in manifest.items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        assert sha256((ROOT / path).read_bytes()).hexdigest() == digest, name

    output = run([executable, '-I', '-B', str(ROOT / 'engines/scalar.py'),
                  str(ROOT / 'inputs/7334-WORD.json.gz')], check=True,
                 capture_output=True, timeout=22).stdout
    actual = loads(output, object_pairs_hook=unique)
    expected = loads((ROOT / 'receipts/INDEPENDENT.json').read_bytes(), object_pairs_hook=unique)
    assert actual == expected
    lead = loads((ROOT / 'receipts/LEAD.json').read_bytes(), object_pairs_hook=unique)
    assert lead['clocks'] == actual['key'] == [41805, 41807, 43313]
    assert lead['bank_roles'] == [226, 931, 978, 990]
    assert list(map(int, actual['donor_values'])) == lead['bank_roles']
    assert lead['separator']['input'] == {k: str(v) for k, v in actual['probe'].items()}
    assert dot(lead['target'], actual['probe']) == dot(lead['target'], actual['mutant']) == 4
    assert [dot(lead['bank'][str(r)], actual['probe']) for r in lead['bank_roles']] == [0, 0, 0, 0]
    assert dot(lead['bank']['990'], actual['mutant']) == -4

    h = run_path(str(ROOT / 'engines/pricing.py'))['power_bounds']
    lo, hi = map(Fraction, ('0.00364665195644044790699554028334161', '0.00364665195644044790699554028334162'))
    lower = 17 * (h(3, hi)[0] + h(2, hi)[0] - h(5, lo)[1])
    upper = 17 * (h(3, lo)[1] + h(2, lo)[1] - h(5, hi)[0])
    assert Fraction('0.20766650') < lower < upper < Fraction('0.20766651') < 1
    print('PASS_CHART907_DELAYED_BANK: 4 donors zero, old source 4, one-component mutant rejected')


if __name__ == '__main__':
    main()
