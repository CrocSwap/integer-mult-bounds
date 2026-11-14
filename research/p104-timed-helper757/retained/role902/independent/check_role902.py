"""Authenticate one #7544 splice and compare its exact Gaussian columns."""
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal
import sys

WORD_SHA = '926bbb01254b96e9f8a67d4b7c616f89105686ef1acd14438ac2aad06ba58a1c'
CANONICAL_SHA = '2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef'
CHART_SHA = 'e1fc3cc6f701604560f9ede4f3d536cbf733bf30379628f6fc3f31b62ddfeefd'
CUT = 40950


def read_pinned(path, digest):
    data = Path(path).read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError(f'input digest mismatch: {Path(path).name}')
    return data


def main(word_path, chart_path):
    packed = read_pinned(word_path, WORD_SHA)
    data = decompress(packed)
    assert sha256(data).hexdigest() == CANONICAL_SHA
    word = json.loads(data)
    e = word['program']
    source, middle, target = 618, 789, 913
    assert e[CUT:CUT+3] == [
        ['MOVE', 902, source, middle, False],
        ['MOVE', 902, middle, target, False],
        ['ADD', 985, 902, '-1', target],
    ]
    assert 902 in word['hosted']['Y2'] and 902 < word['public']
    a, m, b = (word['frames'][f] for f in (source, middle, target))
    assert list(map(len, (a, m, b))) == [3, 5, 7]
    check = run_path(str(chart_path)) if read_pinned(chart_path, CHART_SHA) else None
    frame, inv, compile_gate, run = (check[s] for s in ('frame', 'inverse_circuit', 'compile_gate', 'run'))
    ca, cm, cb = map(frame, (a, m, b))
    old, new = inv(ca) + cm + inv(cm) + cb, inv(ca) + cb
    assert check['child_rank'](a, b) == 4

    def compare(left, right, lower, upper):
        left, right = [list(map(compile_gate, circuit)) for circuit in (left, right)]
        for x in range(1 << 9):
            lv, lp = run(left, x)
            rv, rp = run(right, x)
            assert lv.keys() == rv.keys(), (lower, upper, x, 'support')
            for y, (re, im) in lv.items():
                rr, ri = rv[y]
                assert (re << rp, im << rp) == (rr << lp, ri << lp), (lower, upper, x, y, 'phase')

    compare(old, new, source, target)
    compare(inv(old), inv(new), target, source)
    print(json.dumps({'status': 'PASS_ONE_ROLE902_CHART', 'zero_based_cut': CUT,
                      'forward_columns': 512, 'adjoint_columns': 512,
                      'rank_delta_per_native_invocation': {2: -2, 4: 1}}, sort_keys=True))


if __name__ == '__main__':
    signal.alarm(30)
    main(*sys.argv[1:])
