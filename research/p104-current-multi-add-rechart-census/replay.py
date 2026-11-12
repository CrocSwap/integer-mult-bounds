"""Authenticate and independently census literal common-chart components."""
from fractions import Fraction
from hashlib import sha1, sha256
from json import loads
from pathlib import Path, PurePosixPath
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent
WORD = 'inputs/7334-WORD.json.gz'


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def checked(name, data, pins):
    assert sha256(data).hexdigest() == pins[name], name
    return data


def matched_prior(forward, reverse, old):
    assert forward['cases'] == reverse['cases'] and forward['counts'] == reverse['counts']
    assert forward['counts'] == {'closed_pure': 434, 'dimension_nonpositive': 420,
                                 'fixed_endpoint': 43, 'geometry_exclusion': 14,
                                 'main_or_owned': 824, 'multi_add': 1301}
    assert len(reverse['exact_prior_7361_keys']) == 13
    assert not reverse['new_price_positive_keys']
    assert reverse['exact_prior_7369_key'] == [746, 40834]
    changed, = (r for r in forward['cases'] if r['old_chart'] == 746)
    assert changed['feasible_ranks'] == old['dimension_interval'] == [5, 6]
    assert changed['price_positive_relaxed'][0][0] == old['rejected_rank'] == 4
    assert len(changed['roles']) == old['matched_roles'] == 3
    assert old['head'] == 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
    assert old['matched_positive_offsets'] == 1
    assert all(not r['price_positive_feasible'] for r in forward['cases'])
    quotes = [max(Fraction(q[1][1]) for q in r['price_positive_relaxed']) for r in forward['cases']]
    assert max(quotes) < Fraction('0.106305391209185')
    assert sum(quotes) < Fraction('0.993184112588')


def expect_rejection(action):
    try:
        action()
    except AssertionError:
        return
    raise AssertionError('mutated control passed')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    pins = loads((ROOT / 'PINS.json').read_bytes(), object_pairs_hook=unique)
    members = {f.relative_to(ROOT).as_posix() for d in ('inputs', 'receipts')
               for f in (ROOT / d).iterdir() if f.is_file()}
    assert set(pins) == members | {'rechart.py', 'reverse.py', 'PROVENANCE.json'}
    inputs = {}
    for name in sorted(pins):
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        inputs[name] = checked(name, (ROOT / name).read_bytes(), pins)
    found = []
    for engine, result in (('rechart.py', 'FORWARD'), ('reverse.py', 'REVERSE')):
        output = run([executable, '-I', '-B', str(ROOT / engine)], check=True,
                     capture_output=True, timeout=40).stdout
        observed = loads(output, object_pairs_hook=unique)
        assert observed == loads(inputs[f'receipts/{result}.json'], object_pairs_hook=unique)
        found.append(observed)
    raw = inputs['inputs/7369-AGREEMENT.json']
    assert sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest() == '3aaa7aea617109f65272694e2026609395928030'
    old = loads(raw, object_pairs_hook=unique)
    matched_prior(*found, old)
    damaged = bytes([inputs[WORD][0] ^ 1]) + inputs[WORD][1:]
    expect_rejection(lambda: checked(WORD, damaged, pins))
    expect_rejection(lambda: matched_prior(*found, dict(old, dimension_interval=[4, 6])))
    print('PASS_CURRENT_MULTI_ADD_RECHART_CENSUS: 434 closed, 420 price exclusions, 14 geometry exclusions, zero unresolved')


if __name__ == '__main__':
    main()
