"""One exact J8 odd-return rank and directed-price decision."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    '7113-CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    '7481-APPLICATION.json': '1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799',
    '7481-WORD.json.gz': 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9',
    'independent.py': '21f46a8340331abb1486b50bd4e04453f1968b0a5950d86ff7780dd368590874',
    'upstream_application.py': 'd98987db98553dc55bfc80e3ca47abfcd51c57af6f8cda61101391d8eae94184',
    'physical_binding.py': '5c80c3b0415a7f91d216395248dd6f13297eed637732098e1ca8fb0548951b98',
    '7113-signed-child.py': 'ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b',
    'pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
}


def timeout(_signum, _frame):
    print('{"status":"unresolved_timeout","cases_completed":0}')
    raise SystemExit(124)


def determinant(matrix):
    if not matrix:
        return Q(1)
    return sum((-1)**j * coefficient * determinant([row[:j] + row[j + 1:] for row in matrix[1:]])
               for j, coefficient in enumerate(matrix[0]))


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(30)
    data = {name: (ROOT / name).read_bytes() for name in PINS}
    assert {name: sha256(blob).hexdigest() for name, blob in data.items()} == PINS
    caller = loads(data['7113-CALLER.json'])
    app = loads(data['7481-APPLICATION.json'])
    raw = decompress(data['7481-WORD.json.gz'])
    assert sha256(raw).hexdigest() == '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
    word = loads(raw)
    idle, host = (caller['events'][index] for index in (1339, 1423))
    assert idle == ['B', 'IDLE_ODD', 68, [8], -1]
    assert host == ['J', 8, [8, 0, 18, 26], [36, 37, '-1', '1/2']]
    touches = []
    for index, event in enumerate(caller['events']):
        if event[0] == 'J':
            assert 68 not in event[3][:2]
        elif event[0] == 'B':
            roles = event[2:4] if event[1] in ('ADD', 'SWAP', 'QUERY') else event[2:3]
            if 68 in roles:
                touches.append(index)
    assert touches == [1339]
    ports = caller['types']['B']['ports']
    port = ports[0]
    assert port == 15 and len(ports) == 8 and port not in word['hosted']['Dports']
    main_role = word['live'][port]
    native_pair = [main_role, main_role + 112]
    assert word['frames'][word['initial'][main_role]] == [word['ports'][port]]
    assert word['frames'][word['initial'][main_role + 112]] == []
    axes = [word['ports'][port]] + [1 << (9 + 8 * (host[1] - 1) + bit) for bit in range(8)]
    assert all((a & b).bit_count() % 2 == int(i == j) for i, a in enumerate(axes) for j, b in enumerate(axes))
    assert axes[0] == 81 and axes[1:] == [1 << bit for bit in range(65, 73)]
    physical = data['upstream_application.py'].decode()
    for formula in ('sub(x1,x0),body', 'sub(y1,y0),body', 'sub(y1,x0),terms(list(body.items())+[(q,-1)])',
                    'sub(x1,y0),terms(list(body.items())+[(q,1)])'):
        assert formula in physical
    model = data['independent.py'].decode()
    for formula in ('padd(rs,rows[t],(al,F(0)),q=1)', 'padd(rt,rows[s],(be,F(0)),q=-1)',
                    'rt=pscale(rows[t],(1+al*be,F(0)))'):
        assert formula in model
    alpha, beta = map(Q, host[3][2:])
    child = run_path(str(ROOT / '7113-signed-child.py'))
    c = child['C']
    for vector, eigenphase in (((1, 1), (1, 0)), ((1, -1), (0, 1))):
        applied = [tuple(sum(c[i][j][k] * vector[j] for j in range(2)) for k in range(2))
                   for i in range(2)]
        assert applied == [tuple(2 * x * v for x in eigenphase) for v in vector]
    # Two central Walsh bits yield 1*1 and i*i on the paired q sectors.
    # Set all sixteen body Walsh bits to zero to fix their multiplier at 1.
    multiply = child['multiply']
    assert multiply((1, 0), (1, 0)) == (1, 0)
    assert multiply((0, 1), (0, 1)) == (-1, 0)
    plus = [[Q(1), alpha], [beta, 1 + alpha * beta]]
    minus = [[Q(1), -alpha], [-beta, 1 + alpha * beta]]
    host_difference = [[a - b for a, b in zip(p, m)] for p, m in zip(plus, minus)]
    target = [row + [Q(0)] for row in host_difference] + [[Q(0), Q(0), Q(2)]]
    host_minor, target_minor = determinant(host_difference), determinant(target)
    assert host_minor == 2 and target_minor == 4
    assert determinant([row[:2] + [Q(0)] for row in target]) == 0
    lo, hi = map(Q, app['directed_crossing_bracket'])
    power = run_path(str(ROOT / 'pricing.py'))['power_bounds']
    gross = [len(ports) * power(9, hi)[0], len(ports) * power(9, lo)[1]]
    assert 71 < gross[0] <= gross[1] < 72
    receipt = {'status': 'EXACT_SECTOR_IDENTICAL_HOST_EXCLUSION', 'cases_completed': 1,
               'cap_seconds': 30, 'port': port, 'width': 2, 'central_walsh_bits': ['00', '11'],
               'body_walsh_bits': '0' * 16, 'idle_clock': 1339,
               'host_clock': 1423, 'host_roles': host[3][:2], 'extra_role': 68,
               'native_main_pair': native_pair, 'axes': axes, 'body_phase': 1,
               'host_difference': host_difference, 'required_difference': target,
               'host_rank': 2, 'required_rank': 3, 'host_minor': host_minor,
               'target_minor': target_minor, 'gross_full_caller': gross,
               'paid_delta_if_built_at_every_port': {9: -8}, 'productive_delta': {},
               'pins': PINS}
    print(dumps(receipt, indent=2, sort_keys=True, default=str))
    alarm(0)


if __name__ == '__main__':
    main()
