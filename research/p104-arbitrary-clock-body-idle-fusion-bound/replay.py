"""Replay the exact Type A disjoint-mask body idle exclusion."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path, PurePosixPath
from subprocess import run
from sys import executable, implementation, version_info
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parent
CALLER = 'inputs/CALLER.json'


def no_duplicates(items):
    values = dict(items)
    assert len(values) == len(items), 'duplicate JSON key'
    return values


def checked(path, digest):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == digest, f'input SHA-256 mismatch: {path.name}'
    return data


def regenerate(engine, expected, args=()):
    result = run([executable, '-I', '-B', str(ROOT / engine), *args],
                 check=True, capture_output=True, timeout=35)
    actual = loads(result.stdout, object_pairs_hook=no_duplicates)
    frozen = loads((ROOT / expected).read_bytes(), object_pairs_hook=no_duplicates)
    assert actual == frozen, f'changed exact receipt: {expected}'
    return actual


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    manifest = loads((ROOT / 'PINS.json').read_bytes(), object_pairs_hook=no_duplicates)
    files = {path.relative_to(ROOT).as_posix() for directory in ('engines', 'inputs', 'receipts')
             for path in (ROOT / directory).iterdir() if path.is_file()}
    assert set(manifest) == files | {'PROVENANCE.json'}
    for name, digest in manifest.items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        checked(ROOT / path, digest)

    lead = regenerate('engines/lead.py', 'receipts/LEAD.json')
    independent = regenerate('engines/independent.py', 'receipts/INDEPENDENT.json', (str(ROOT),))
    left = [(case['clocks'], case['roles'], [8 * len(mask) for mask in case['masks']],
             case['projector_inequality']) for case in lead['pairs']]
    right = [(case['clocks'], case['roles'], case['ranks'], case['witness'])
             for case in independent['cases']]
    assert left == right and len(left) == len({tuple(case[0]) for case in left}) == 224
    assert all(case[3] is not None for case in left)
    assert lead['survivors'] == independent['survivors'] == []
    assert lead['profile']['negative_body_stages'] == independent['profile']['negative_D'] == [8, 9]
    assert lead['profile']['q'] == independent['profile']['q'] == 1
    assert lead['best']['clocks'] == independent['best']['clocks'] == [1448, 1763]
    assert lead['literal_best_difference'] == independent['literal_omission_first_wrong'] == [1, 0, '0', '-4']
    assert lead['max_pairs'] == 14 and Fraction(lead['disjoint_matching_upper']) < Fraction('238.182')

    # A different byte at the source boundary must fail the same guard.
    with TemporaryDirectory() as directory:
        mutant = Path(directory) / 'CALLER.json'
        caller = (ROOT / CALLER).read_bytes()
        mutant.write_bytes(bytes([caller[0] ^ 1]) + caller[1:])
        try:
            checked(mutant, manifest[CALLER])
        except AssertionError as error:
            assert str(error).startswith('input SHA-256 mismatch:')
        else:
            raise AssertionError('mutated caller passed source authentication')

    print('PASS_TYPE_A_BODY_IDLE_FUSION: 224 excluded, 0 unresolved, literal best control and input mutation checked')


if __name__ == '__main__':
    main()
