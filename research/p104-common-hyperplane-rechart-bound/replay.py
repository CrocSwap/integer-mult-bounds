"""Reproduce both exact dual-chart demotion solvers."""
from hashlib import sha256
from json import loads
from pathlib import Path, PurePosixPath
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent


def unique(pairs):
    out = dict(pairs)
    assert len(out) == len(pairs), 'duplicate JSON field'
    return out


def read(path):
    return loads((ROOT / path).read_bytes(), object_pairs_hook=unique)


def check_bytes(data, expected):
    assert sha256(data).hexdigest() == expected, 'immutable input mismatch'


def execute(script, receipt):
    output = run([executable, '-I', '-B', str(ROOT / script)], check=True,
                 capture_output=True, timeout=64).stdout
    actual = loads(output, object_pairs_hook=unique)
    assert actual == read('receipts/' + receipt + '.json')
    return actual


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    pins = read('PINS.json')
    expected = {'demotion.py', 'shrink_flow.py', 'endpoint_replay.py', 'reverse_inventory.py',
                'cut_flow.py', 'PROVENANCE.json'}
    expected |= {f.relative_to(ROOT).as_posix() for n in ('inputs','receipts') for f in (ROOT/n).iterdir()}
    assert set(pins) == expected
    for name, digest in pins.items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        check_bytes((ROOT / path).read_bytes(), digest)
    name = 'inputs/pricing.py'
    try:
        check_bytes((ROOT / name).read_bytes() + b'\n', pins[name])
    except AssertionError:
        pass
    else:
        raise AssertionError('altered tariff passed its pin')

    lead = execute('demotion.py', 'LEAD')
    independent = execute('shrink_flow.py', 'INDEPENDENT')
    assert not lead['capped'] and not independent['capped'] and lead['witness'] is None
    assert lead['max'] == independent['max'] == 0
    assert lead['rows'] == independent['rows']
    assert lead['vectors_checked'] == independent['vectors'] == 511
    assert lead['vertex_count'] == independent['vertices'] == 18
    assert lead['eligible_groups'] == independent['eligible_groups'] == 553
    assert (independent['groups'], independent['paid_edges'], independent['target_edges']) == (1517, 2573, 193)
    assert lead['scale'] == independent['scale'] and lead['radius'] == independent['radius']
    assert list(lead['center'].values()) == independent['center']
    assert list(lead['directed_increment_box'].values()) == independent['box']
    assert [r[0] for r in lead['rows']] == list(range(1,512))
    assert all(len(values) == 18 and not any(values) for _,values in lead['rows'])
    print('PASS_COMMON_HYPERPLANE_RECHART_BOUND: 511 normals x 18 price vertices, exact upper 0')


if __name__ == '__main__':
    main()
