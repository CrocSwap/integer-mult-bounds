"""Check the omitted-centre map by exact input-column propagation."""
import argparse
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path

if not __debug__:
    raise SystemExit("Run this verifier without -O. Historical sources use assert.")
parser = argparse.ArgumentParser()
parser.add_argument("--base", type=Path, required=True)
args = parser.parse_args()
BASE = args.base
PATH = BASE / 'retimed-4/split-centres/CANONICAL-WORD.json.gz'
raw = PATH.read_bytes()
w = json.loads(gzip.decompress(raw))
n = 240 + w['R']
ops = w['precondition'] + w['compensation'] + w['A'] + w['B'] + w['cleanup']
steps = [(e[0], e[1], e[2] if e[0] == 'add' else -1,
          F(e[3], e[4]) if e[0] == 'add' else F(e[2], e[3])) for e in ops]
S = [[F(0) for _ in range(120)] for _ in range(120)]
D = [[F(0) for _ in range(n - 240)] for _ in range(120)]
for column in range(n):
    v = [F(0)] * n
    v[column] = F(1)
    for kind, dst, src, coefficient in steps:
        if kind == 'add':
            if v[src]:
                v[dst] += coefficient * v[src]
        else:
            v[dst] *= coefficient
    assert all(v[i] == int(column == i) for i in range(120))
    assert all(v[i] == int(column == i) for i in range(240, n))
    if column < 120:
        for i in range(120):
            S[i][column] = v[120 + i]
    elif column < 240:
        assert all(v[120 + i] == int(column == 120 + i) for i in range(120))
    else:
        for i in range(120):
            D[i][column - 240] = v[120 + i]
            if v[120 + i]:
                assert w['start'][column] == 0
                assert v[120 + i].denominator.bit_count() == 1

C = [[F(0) for _ in range(120)] for _ in range(8)]
for column in range(120):
    v = [F(0)] * n
    v[column] = F(1)
    for e in w['precondition'] + w['A']:
        if e[0] == 'add':
            v[e[1]] += F(e[3], e[4]) * v[e[2]]
        else:
            v[e[1]] *= F(e[2], e[3])
    for i, register in enumerate(w['centers'][:8]):
        C[i][column] = v[register]
assert [[sum(x*y for x, y in zip(a, b)) for b in C] for a in C] == [
    [56 * int(i == j) for j in range(8)] for i in range(8)]
code = [i for i, row in enumerate(S) if any(row)]
assert len(code) == 112
for i in range(120):
    for j in range(120):
        gram = sum(row[i]*row[j] for row in C) / 4
        assert S[i][j] == (int(i == j) - gram if i in code else 0)
        if i not in code:
            assert gram == 0
helpers = list(range(758, 750, -1))
assert all(w['start'][r] == 0 and w['final'][r] == 1 for r in helpers)
assert all(w['start'][120 + j] == 0 and w['final'][j] == 1
           for row in C for j, coefficient in enumerate(row) if coefficient)

# Compose the four block maps symbolically. P inserts C into eight helper rows.
# preload: h1=h+P Y; correction: Y1=Y-D h1.
# base: Y2=Y1+S X+D h1=Y+S X; h2=h1; X2=X.
# postload: h3=h2+(59/4)P X=h+P(Y+(59/4)X).
result = dict(status='PASS_INDEPENDENT_EXACT_CAPTURE_MAP',
              source_sha256=hashlib.sha256(raw).hexdigest(),
              method='800 exact input columns; symbolic composition of boundary maps',
              columns=n, scalar_operations=len(steps), code_ports=len(code),
              dirty_correction_terms=sum(bool(x) for row in D for x in row),
              C_row_gram=56, captured_forms=8,
              boundary_frames='preload and dirt correction at zero; postload at full',
              scope='Local label map only; no routed endpoint decoder or global cost claim.')
print(json.dumps(result, indent=2))
