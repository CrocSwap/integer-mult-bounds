"""Check the local pair error formula. Ali Romman with OpenAI Codex assistance.
Apache-2.0. The written proof gives the all-width statement.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
from types import SimpleNamespace
import argparse

def need(ok, why):
    if not ok:
        raise ValueError(why)

HERE = Path(__file__).resolve().parent
root = HERE.parents[1]
for pin in json.loads((HERE/'SOURCES.json').read_text())['files']:
    if pin['usage'] == 'input':
        need(sha256((root/pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'Declared source pin')

paths = ['research/native-center-free-code/CODE.json',
         'research/coded-native-caller/NORMALIZERS.json',
         'research/coded-inverse-fixed-grid/kernel.py']
raw = [(root / p).read_bytes() for p in paths]
need([sha256(b).hexdigest() for b in raw] == [
    '8be7f3f073b7981ec91c6af43edff0ac8a89f4824ef6026ae758c287dd6c03d0',
    'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da',
    'bc0e9f705665d6981c0f9176dad0f2d71471735e866c44643cb6835423435303'], 'Source pins')
a = [[F(v) for v in row] for row in json.loads(raw[0])['A']]
records = json.loads(raw[1])['ports']
n = len(a)
need(n == 112 and len(records) == n, 'Owner count')
need(all(sum(map(abs, row)) == 26 for row in a), 'Absolute code row sums')
modes = json.loads(raw[1])['mode_columns']
need(all(sum(a[i][j]*m[j] for j in range(n)) == -13*m[i]
         for m in modes for i in range(n)), 'Error modes have eigenvalue -13')
# A^2 + 12A = 13I gives the inverse used below.
need(all(sum(a[i][k]*a[k][j] for k in range(n)) + 12*a[i][j]
         == 13*(i == j) for i in range(n) for j in range(n)), 'Inverse identity')

def add(x, y, s=1):
    return [(p[0]+s*q[0], p[1]+s*q[1]) for p,q in zip(x,y)]

def phase(x, exponents):
    out = []
    for (r,i), e in zip(x, exponents):
        out.append(((r,i),(-i,r),(-r,-i),(i,-r))[e % 4])
    return out

def code(x, inverse=False):
    y = [(sum(aij*v[0] for aij,v in zip(row,x)),
          sum(aij*v[1] for aij,v in zip(row,x))) for row in a]
    if inverse:
        return [((u[0]+12*v[0])/13,(u[1]+12*v[1])/13) for u,v in zip(y,x)]
    return y

def mv(rows, u):
    return sum(((r & u).bit_count() % 2) << i for i,r in enumerate(rows))

def trans(rows):
    return [sum(((r >> i)&1)<<j for j,r in enumerate(rows)) for i in range(9)]

namespace = {'__name__': 'source_kernel', '__file__': str(root/'research/coded-inverse-fixed-grid/kernel.py')}
exec(compile((root/'research/coded-inverse-fixed-grid/kernel.py').read_bytes(), namespace['__file__'], 'exec'), namespace)
kernel = SimpleNamespace(**namespace)
for seed in range(1,13):
    inp = [((i*i+seed*11)%103)-51 for i in range(n)]
    width = kernel.word_width(51)
    words = [kernel.encode(v,width) for v in inp]
    scratch = [[0]*width for _ in range(9)]
    kernel.recode(words,modes,51,scratch)
    actual = [(F(kernel.decode(w)),F(0)) for w in words]
    exact = code([(F(v),F(0)) for v in inp],True)
    err = add(actual,exact,-1)
    need(code(err) == [(-13*r,-13*i) for r,i in err], 'Actual kernel error mode')
    need(max(abs(r) for r,i in err) <= 2, 'Kernel error bound')
    need(all(not any(w) for w in scratch), 'Owned cleanup')
fibers = [(0,), (1,), (19,), (511,), (0,1), (1,19,256), (17,256,3,98,511)]
rejected = {'entry_error_in_X':False, 'thin_order':False, 'exit_error_before_C':False}
for us in fibers:
    v = [[mv(trans(r['G_rows']), u ^ r['Z_mask']) for u in us] for r in records]
    q = [sum(z&1 for z in vs) for vs in v]
    d = [sum((z>>1).bit_count() for z in vs) for vs in v]
    need(all((qi+di-sum(u.bit_count() for u in us))%4 == 0 for qi,di in zip(q,d)),
         'Physical DQ phase')
    qi = [-e for e in q]
    fixtures = [[(F((i*i+3*s)%29,7+s), F((7*i+s)%19,11+s)) for i in range(n)]
                for s in range(1,6)]
    x,y,e0,e1,e2 = fixtures
    y1 = add(code(y, True), e0)
    x2 = phase(add(x, phase(code(y1),q),-1),d)
    y2 = phase(y1,d)
    query = phase(add(code(x2,True),e1),qi)
    y3 = add(y2,query)
    out = phase(add(code(phase(y3,q)),e2),qi)
    idealx = phase(add(x,phase(y,q),-1),d)
    idealy = phase(phase(x,qi),d)
    dx = phase(phase(code(e0),q),d)
    dy = phase(add(code(e1),e2),qi)
    need(x2 == add(idealx,dx,-1), 'Entry error in X')
    need(out == add(idealy,dy), 'Exact local Y residual')
    rejected['entry_error_in_X'] |= x2 != idealx
    wrong = phase(add(code(phase(add(y2,add(code(phase(x2,qi),True),phase(e1,qi))),q)),e2),qi)
    rejected['thin_order'] |= wrong != out
    rejected['exit_error_before_C'] |= out != add(idealy,phase(code(add(e1,e2)),qi))
need(all(rejected.values()), 'Controls must fail')
# Build a literal row of G^tensor k and sum real and imaginary magnitudes.
row = [(F(1),F(0))]
for k in range(1,13):
    row = [((r-s*i)/2,(i+s*r)/2) for r,i in row for s in (1,-1)]
    need(sum(abs(r)+abs(i) for r,i in row) == 2**((k+1)//2), 'Real component norm')
for f in range(1,101):
    guard = (9*f+1)//2 + 5
    need(F(26*2**((9*f+1)//2),2**guard) < 1, 'Precision guard')
result = {'status':'PASS_PHYSICAL_PAIR_ERROR_TRANSFER',
 'source_sha256':dict(zip(paths,map(lambda b:sha256(b).hexdigest(),raw))),
 'fibers':[list(u) for u in fibers], 'code_rows':n, 'code_abs_row_sum':26,
 'actual_kernel_fixtures':12, 'gaussian_tensor_rows':12, 'guard_widths_checked':100,
 'controls':rejected}
parser = argparse.ArgumentParser()
parser.add_argument('--write-result', action='store_true')
args = parser.parse_args()
if args.write_result:
    (HERE/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
else:
    need(json.loads((HERE/'RESULT.json').read_text()) == result, 'Receipt mismatch')
print(json.dumps(result, sort_keys=True))
