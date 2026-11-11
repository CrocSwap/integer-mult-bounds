"""Independent nonzero exterior minors over F_65521 prove exclusion over Q."""
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

P = 65521


def pinned(root, name, digest):
    raw = (root / name).read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError(f'pin mismatch: {name}')
    return raw


def add(dst, src, a):
    for j, b in src.items():
        value = (dst.get(j, 0) + a * b) % P
        if value:
            dst[j] = value
        else:
            dst.pop(j, None)


def minor(bank, rows, group):
    pivots = {}
    for field in bank:
        row = {j: a for j, a in rows[field].items() if j not in group}
        while row:
            j = min(row)
            if j not in pivots:
                pivots[j] = row
                break
            pivot = pivots[j]
            add(row, pivot, -row[j] * pow(pivot[j], -1, P))
        else:
            raise ValueError('exterior rank lost')
    return list(pivots)


def run(root):
    word = json.loads(gzip.decompress(pinned(root, 'price-inputs/inputs/7314/WORD.json.gz',
        'c404b9b61220e6cf740d85276df2828bbb4a9d68a4d44b5e283f8d96f78c0fd9')))
    geometry = json.loads(pinned(root, 'independent/RESULT.json',
        '3843042387401f281906d6b6eeeca1d7255b00cc327a863fd8070f0317eadc81'))
    assert geometry['scope_complete'] and not geometry['overflow_keys']
    assert not geometry['keys_by_tier']['mixed_863']
    group = set(geometry['cohort']) - {863}
    by_cut = {}
    for row in geometry['segments']:
        by_cut.setdefault(row['cut'], []).append(row)
    rows = [{j: 1} for j in range(word['public'])] + [{} for _ in range(word['owned_fields'])]
    charts = word['initial'] + [None] * word['owned_fields']
    result = []
    for t, (op, dst, *args) in enumerate(word['program']):
        for case in by_cut.get(t, ()):
            bank = [j for j, f in enumerate(charts[:word['public']]) if f == case['chart']]
            assert bank == case['public_bank']
            columns = minor(bank, rows, group)
            result.append(dict(cut=t, chart=case['chart'], columns=columns, rows=bank,
                               pivots=case['pivots']))
        if op == 'MOVE':
            assert charts[dst] == args[0]
            charts[dst] = args[1]
        elif op in ('INIT', 'CLEAR'):
            charts[dst] = args[0] if op == 'INIT' else None
            rows[dst] = {}
        else:
            q = Fraction(args[-2])
            q = q.numerator * pow(q.denominator, -1, P) % P
            if op in ('SCALE', 'COPY'):
                src = dst if op == 'SCALE' else args[0]
                rows[dst] = {j: v * q % P for j, v in rows[src].items() if v * q % P}
            else:
                assert op == 'ADD' and dst != args[0]
                add(rows[dst], rows[args[0]], q)
    assert charts == word['final'] + [None] * word['owned_fields']
    assert len(result) == len(geometry['segments']) == 28
    assert sum(len(row['pivots']) for row in result) == 35
    assert all(rows[j] == {j: 1} for j in group)
    assert minor([0], [{1: 1}], {0}) == [1]
    try:
        minor([0], [{1: 1}], {1})
    except ValueError:
        pass
    else:
        raise AssertionError('a pure exterior-zero direction must prevent a full minor')
    print(json.dumps(dict(modulus=P, decisions=result, unresolved=0), sort_keys=True, indent=2))


if __name__ == '__main__':
    run(Path(sys.argv[1]))
