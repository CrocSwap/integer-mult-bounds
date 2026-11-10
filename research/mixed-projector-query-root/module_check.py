"""Check the root independently of the emitted caller.

The shortest-query tuple is from five-call-projector-rigidity. The chosen
stage projectors, normalization and mixed root are new here. Ali Romman,
with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import json

from algebra import Q, add, eye, inverse, matrix, multiply, need, zadd, zmul

HERE = Path(__file__).resolve().parent


def run():
    d = json.loads((HERE/'ROOT.json').read_text())
    n, identity = 6, eye(6)
    zero = [[Q(0)]*n for _ in range(n)]
    f, fi = matrix(d['input_basis']), matrix(d['output_basis'])
    need(multiply(f, fi) == multiply(fi, f) == identity, 'Root bases are inverses')
    prefix, projectors, queries = identity, [], []
    for i, site in enumerate(d['sites']):
        u = [int(j == i) for j in range(n)] if i < n else [-(-1)**j for j in range(n)]
        v = [int(i > j)-int(i < j) for j in range(n)]
        r = matrix([[x*y for y in v] for x in u])
        need(multiply(r, r) == zero, 'Square-zero query')
        prefix = multiply(add(identity, r, -2), prefix)
        c, ci = matrix(site['basis']), matrix(site['inverse'])
        need(multiply(c, ci) == multiply(ci, c) == identity, 'Each native basis has an inverse')
        e = [[Q(0)]*n for _ in range(n)]
        e[0][1] = Q(1)
        need(multiply(multiply(c,e),ci) == r, 'Actual native two-field query plane')
        p = matrix(site['projector'])
        if site['full']:
            support = site['support']
            diagonal = [[int(j == k and j in support) for k in range(n)] for j in range(n)]
            need(p == multiply(multiply(f,diagonal),fi), 'Independent output stage mask')
            size = site['stage_rank']
            physical = [[int(j == k and j < size) for k in range(n)] for j in range(n)]
            need(p == multiply(multiply(c,physical),ci), 'Every complementary idle is included')
            need(multiply(p,p) == p and multiply(p,r) == multiply(r,p) == r, 'Stage projector')
            need(multiply(p,prefix) == multiply(prefix,p), 'Chronological commutation')
            for old in projectors:
                need(multiply(p,old) == multiply(old,p), 'Independent stages commute')
            projectors.append(p)
        else:
            need(p == zero, 'Thin sites have no free diagonal supplier')
        queries.append(r)
    need(prefix == [[-x for x in row] for row in identity], 'All minus-character outputs')
    masks = [[int(j in s['support']) for s in d['sites'] if s['full']] for j in range(n)]
    need(masks == d['masks'], 'Declared full-site masks')
    expected = {}
    for j,bits in enumerate(masks):
        mask = sum(bit << i for i,bit in enumerate(bits))
        expected.setdefault(mask, [[Q(0)]*n for _ in range(n)])[j][j] = Q(1)
    for sign in (1,-1):
        word, stage = {0: identity}, 0
        for r,site in zip(queries,d['sites']):
            next_word = {}
            p = matrix(site['projector'])
            for mask,old in word.items():
                a = multiply(add(identity,r,sign-1),old)
                if site['full']:
                    next_word[mask] = multiply(add(identity,p,-1),a)
                    next_word[mask | (1 << stage)] = multiply(p,a)
                else:
                    next_word[mask] = a
            word = {k:a for k,a in next_word.items() if a != zero}
            stage += int(site['full'])
        actual = {k:multiply(multiply(fi,a),f) for k,a in word.items()}
        need(actual == {k:[[sign*x for x in row] for row in a] for k,a in expected.items()},
             'Every independent full-stage polynomial coefficient')
    # The four ordinary operations act on each pair of translated addresses.
    # No whole field is copied or initialized for this normalization.
    pair_matrices = []
    for sign in (1,-1):
        a, b = (Q(1,2),Q(sign,2)), (Q(1,2),Q(-sign,2))
        columns = []
        for column in (0,1):
            x,y = (Q(int(column == 0)),Q(0)), (Q(int(column == 1)),Q(0))
            x = zadd(x,zmul((Q(0),Q(-sign)),y))
            x = zmul(a,x)
            y = zmul((Q(1),Q(sign)),y)
            y = zadd(y,zmul((Q(0),Q(-sign)),x))
            columns.append([x,y])
        m = list(map(list,zip(*columns)))
        need(m == [[a,b],[b,a]], 'Four-operation ordinary normalization')
        pair_matrices.append(m)
    def zmat(a,b):
        return [[zadd(zmul(a[i][0],b[0][j]),zmul(a[i][1],b[1][j])) for j in range(2)] for i in range(2)]
    need(zmat(*pair_matrices) == [[(1,0),(0,0)],[(0,0),(1,0)]], 'Normalization inverse')
    need(zmat(pair_matrices[0],pair_matrices[0]) == [[(0,0),(1,0)],[(1,0),(0,0)]],
         'Normalization square is the ordinary translation')
    for q in [(1,0),(-1,0),(0,1),(0,-1)]:
        square = zmul(q,q)
        lam = zadd((Q(1,2),Q(1,2)),zmul((Q(1,2),Q(-1,2)),square))
        lam_inv = zadd((Q(1,2),Q(-1,2)),zmul((Q(1,2),Q(1,2)),square))
        s = zmul(lam,q)
        need(zmul(s,s) == (1,0) and zmul(lam_inv,s) == q, 'All four Gaussian characters')
    def dense_product(a,b):
        size = len(a)
        out = [[(Q(0),Q(0)) for _ in range(size)] for _ in range(size)]
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    out[i][j] = zadd(out[i][j],zmul(a[i][k],b[k][j]))
        return out
    tensor_columns = 0
    wrong_tensor_rejected = False
    for width in (1,2,3):
        size = 1 << width
        ident = [[(Q(int(i == j)),Q(0)) for j in range(size)] for i in range(size)]
        gaussian,normalizer,restore = [],[],[]
        for i in range(size):
            row,norm,back = [],[],[]
            for j in range(size):
                value = (Q(1),Q(0))
                for bit in range(width):
                    c = (Q(1,2),Q(1 if (i^j)&(1 << bit) else -1,2))
                    value = zmul(value,c)
                row.append(value)
                norm.append((Q(1,2),Q(1,2)) if i == j else
                            (Q(1,2),Q(-1,2)) if i^j == size-1 else (Q(0),Q(0)))
                back.append((Q(1,2),Q(-1,2)) if i == j else
                            (Q(1,2),Q(1,2)) if i^j == size-1 else (Q(0),Q(0)))
            gaussian.append(row)
            normalizer.append(norm)
            restore.append(back)
        normalized = dense_product(normalizer,gaussian)
        need(dense_product(normalized,normalized) == ident, 'Actual tensor Gaussian normalizes to an involution')
        need(dense_product(restore,normalized) == gaussian, 'Actual tensor Gaussian is restored')
        if width == 1:
            need(normalized == ident, 'One-column normalization positive control')
        if width == 2:
            need(normalized != ident and dense_product(restore,ident) != gaussian,
                 'Tensoring the one-column normalization is rejected')
            wrong_tensor_rejected = True
        tensor_columns += size
    return {'fields':n,'full_sites':4,'thin_sites':3,'stage_ranks':[2,3,3,2],
            'polynomial_coefficients':2*16*n*n,'gaussian_characters':4,
            'actual_tensor_gaussian_columns':tensor_columns,
            'wrong_tensor_normalization_rejected':wrong_tensor_rejected,
            'ordinary_normalization_operations_per_pair':4,'owned_normalization_fields':0,
            'normalization_growth_per_operation_upper':2,
            'tensor_rule':'Normalize the complete field with its global Q squared translation; scalar coefficients stay outside tensor powers.'}


if __name__ == '__main__':
    print(run())
