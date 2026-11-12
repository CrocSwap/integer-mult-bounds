"""Exact combined endpoint-price check on the pinned 76,466-event word."""
from hashlib import sha256
from json import loads
from pathlib import Path, PurePosixPath
from subprocess import run
from sys import executable, implementation, version_info

ROOT = Path(__file__).resolve().parent


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON field'
    return result


def read(path):
    return loads((ROOT / path).read_bytes(), object_pairs_hook=unique)


def check_bytes(data, expected):
    assert sha256(data).hexdigest() == expected, 'immutable input mismatch'


def execute(name):
    result = run([executable, '-I', '-B', str(ROOT / name)], check=True,
                 capture_output=True, timeout=64).stdout
    return loads(result, object_pairs_hook=unique)


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    pins = read('PINS.json')
    expected = {'vertices.py', 'endpoint_replay.py', 'reverse_inventory.py', 'cut_flow.py', 'PROVENANCE.json'}
    expected |= {f.relative_to(ROOT).as_posix() for n in ('inputs', 'receipts') for f in (ROOT/n).iterdir()}
    assert set(pins) == expected
    for name, digest in pins.items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts
        check_bytes((ROOT / path).read_bytes(), digest)
    path = 'inputs/pricing.py'
    try:
        check_bytes((ROOT / path).read_bytes() + b'\n', pins[path])
    except AssertionError:
        pass
    else:
        raise AssertionError('altered tariff passed its pin')

    lead = execute('vertices.py')
    assert lead == read('receipts/LEAD-VERTICES.json')
    cap = read('receipts/INDEPENDENT-CAP.json')
    tail = read('receipts/INDEPENDENT-CONTINUATION.json')
    assert cap['capped'] and cap['vectors'] == 498 and cap['cap_seconds'] == 60
    assert cap['partial_row'][0] == tail['first_vector'] == 499
    assert not tail['capped'] and tail['cap_seconds'] == 10 and tail['mode'] == 'direct'
    assert len(cap['partial_row'][1]) == tail['skip_first_vertices'] == 7
    assert tail['last_vector'] == 511
    expected_rows = cap['rows'] + [[499, cap['partial_row'][1] + tail['rows'][0][1]]] + tail['rows'][1:]
    expected_rounding = cap['rounding'] + tail['rounding']
    assert sum(len(row[1]) for row in tail['rows']) == 227
    assert expected_rows == lead['rows'] and [r[0] for r in expected_rows] == list(range(1, 512))
    assert all(len(v) == 18 and not any(v) for _, v in expected_rows)

    actual = execute('endpoint_replay.py')
    assert not actual['capped'] and actual['max'] == lead['max'] == 0
    assert actual['rows'] == expected_rows and actual['rounding'] == expected_rounding
    for key in ('groups','eligible_groups','paid_edges','target_edges','scale','box','center','radius'):
        assert actual[key] == cap[key] == tail[key]
    assert (actual['groups'],actual['eligible_groups'],actual['paid_edges'],actual['target_edges']) == (1517,553,2573,193)
    assert actual['vectors'] == lead['vectors_checked'] == 511
    assert actual['vertices'] == lead['vertex_count'] == 18
    assert actual['scale'] == lead['scale'] and actual['radius'] == lead['radius']
    assert actual['center'] == list(lead['center'].values())
    assert actual['box'] == list(lead['directed_increment_box'].values())
    split = read('receipts/LEAD-ROUNDING.json')
    assert [r[:2] + r[3:] for r in expected_rounding] == split['results']
    assert max(r[2] for r in expected_rounding) == 0
    assert max(r[3] for r in expected_rounding) == 12669598508059006000
    print('PASS_ENDPOINT_VECTOR_GROWTH_BOUND: 511 vectors x 18 price vertices, exact upper 0')


if __name__ == '__main__':
    main()
