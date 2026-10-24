"""Separately derived binary coset audit; Apache-2.0.
Prepared by the independent review agent for Dillon with OpenAI Codex assistance.
Packaging changes: portable root, authenticated inputs, explicit optimized-mode
checks and frozen receipt comparison. No Clifford engine is imported.
"""
import json, hashlib
from pathlib import Path
from fractions import Fraction
PACKAGE = Path(__file__).resolve().parent
root = PACKAGE.parent / 'coded-native-caller'
PINS = {'CODE.json': '8be7f3f073b7981ec91c6af43edff0ac8a89f4824ef6026ae758c287dd6c03d0', 'NORMALIZERS.json': 'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da'}
for name, digest in PINS.items():
    if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
        raise ValueError('Independent source hash: ' + name)
r = json.loads((root / 'NORMALIZERS.json').read_text())
a = [[Fraction(x) for x in row] for row in json.loads((root / 'CODE.json').read_text())['A']]
p = r['ports']
n = 9
e = 1

def par(x):
    return x.bit_count() & 1

def mv(g, x):
    return sum((par(row & x) << i for i, row in enumerate(g)))

def tr(g):
    return [sum(((g[j] >> i & 1) << j for j in range(n))) for i in range(n)]

def mul(g, h):
    return [sum((par(g[i] & col) << j for j, col in enumerate(tr(h)))) for i in range(n)]

def rank(rows):
    piv = {}
    for x in rows:
        while x:
            b = x.bit_length() - 1
            if b not in piv:
                piv[b] = x
                break
            x ^= piv[b]
    return len(piv)
if not (len(p) == 112 and len({x['q'] for x in p}) == 112):
    raise ValueError("Independent condition failed: len(p) == 112 and len({x['q'] for x in p}) == 112")
if not all((len(row) == 112 for row in a)):
    raise ValueError('Independent condition failed: all((len(row) == 112 for row in a))')
if not all((a[i][i] == 0 for i in range(112))):
    raise ValueError('Independent condition failed: all((a[i][i] == 0 for i in range(112)))')
if not all((sum((a[i][j] != 0 for i in range(112))) == 52 for j in range(112))):
    raise ValueError('Independent condition failed: all((sum((a[i][j] != 0 for i in range(112))) == 52 for j in range(112)))')
if not all((sum((a[i][j] != 0 for j in range(112))) == 52 for i in range(112))):
    raise ValueError('Independent condition failed: all((sum((a[i][j] != 0 for j in range(112))) == 52 for i in range(112)))')
for x in p:
    g = x['G_rows']
    if not mul(tr(g), g) == [1 << i for i in range(n)]:
        raise ValueError('Independent condition failed: mul(tr(g), g) == [1 << i for i in range(n)]')
    if not mv(g, e) == x['q']:
        raise ValueError("Independent condition failed: mv(g, e) == x['q']")
    if not x['K_word'][0] == ['P', g]:
        raise ValueError("Independent condition failed: x['K_word'][0] == ['P', g]")
    if not x['K_word'][1] == ['D', [0] * n, [2 * (x['Z_mask'] >> i & 1) for i in range(n)]]:
        raise ValueError("Independent condition failed: x['K_word'][1] == ['D', [0] * n, [2 * (x['Z_mask'] >> i & 1) for i in range(n)]]")
census = {}
for j in range(112):
    for k in range(112):
        o = mul(tr(p[j]['G_rows']), p[k]['G_rows'])
        u = mv(o, e)
        v = mv(tr(o), e)
        b = [(e if u >> i & 1 else 0) ^ (v if i == 0 else 0) for i in range(n)]
        z = rank(b)
        census[z] = census.get(z, 0) + 1
        if not z == (0 if j == k else 2):
            raise ValueError((j, k, z))
o = mul(tr(p[0]['G_rows']), p[0]['G_rows'])
if not mv(o, e) == e:
    raise ValueError('Independent condition failed: mv(o, e) == e')
out = {'status': 'PASS_INDEPENDENT_RIGHT_COSET_CENSUS', 'ports': 112, 'pair_grade_census': census, 'supported_offdiagonal_blocks': sum((x != 0 for row in a for x in row)), 'source_sha256': {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in ['NORMALIZERS.json', 'CODE.json']}, 'scope': 'Binary monomial/coset conditions only; no numerical group-algebra enumeration or circuit search.'}
expected = json.loads((PACKAGE / 'INDEPENDENT.json').read_text())
if json.loads(json.dumps(out)) != expected:
    raise ValueError('Independent finite receipt differs')
print('PASS_INDEPENDENT_RIGHT_COSET_CENSUS ports=112 distinct_grade2=12432 supported=5824')
