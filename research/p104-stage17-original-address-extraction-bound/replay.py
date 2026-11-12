"""Replay the exact stage-17 original-address exclusion."""
from fractions import Fraction
from hashlib import sha256
from json import loads
from pathlib import Path, PurePosixPath
from subprocess import run
from sys import executable, implementation, version_info
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
CALLER = 'inputs/CALLER.json'


def unique(pairs):
    values = dict(pairs)
    assert len(values) == len(pairs), 'duplicate JSON key'
    return values


def checked(path, digest):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == digest, f'input SHA-256 mismatch: {path.name}'
    return raw


def regenerate(name, args=()):
    engine = ROOT / f'engines/{name.lower()}.py'
    output = run([executable, '-I', '-B', str(engine), *args], check=True,
                 capture_output=True, timeout=22).stdout
    actual = loads(output, object_pairs_hook=unique)
    expected = loads((ROOT / f'receipts/{name}.json').read_bytes(), object_pairs_hook=unique)
    assert actual == expected, f'changed exact receipt: {name}'
    return actual


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    manifest = loads((ROOT / 'PINS.json').read_bytes(), object_pairs_hook=unique)
    names = {f.relative_to(ROOT).as_posix() for folder in ('engines', 'inputs', 'receipts')
             for f in (ROOT / folder).iterdir() if f.is_file()}
    assert set(manifest) == names | {'PROVENANCE.json'}
    for name, digest in manifest.items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        checked(ROOT / path, digest)

    lead = regenerate('LEAD')
    independent = regenerate('INDEPENDENT', (str(ROOT),))
    assert lead['clocks'] == independent['clocks'] == [4646, 4660]
    assert lead['window'] == independent['window'] and len(lead['window']) == 13
    assert lead['body_axes'] == independent['inherited_axis_ids'] == list(range(137, 145))
    assert lead['neighbour_D_minus_E'] == independent['residual_entry'] == ['0', '-1/16']
    assert lead['arbitrary_coordinate_extraction_volume'] == independent['coordinate_only_minimum_old_lane_volumes'] == 2
    assert independent['normalized_residual_lanes'] == 2
    assert independent['literal_address_basis_bridge_in_window'] is False
    assert Fraction(lead['two_volume_gross_upper']) < Fraction('-126.39')
    assert Fraction(independent['two_lane_raw_interval_from_7416'][1]) < Fraction('-126.39')

    with TemporaryDirectory() as directory:
        original = (ROOT / CALLER).read_bytes()
        altered = Path(directory) / 'CALLER.json'
        altered.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
        try:
            checked(altered, manifest[CALLER])
        except AssertionError as error:
            assert str(error).startswith('input SHA-256 mismatch:')
        else:
            raise AssertionError('mutated caller passed source authentication')

    print('PASS_STAGE17_ORIGINAL_ADDRESS: exact neighbour, 13 scalar events, two full lane volumes required')


if __name__ == '__main__':
    main()
