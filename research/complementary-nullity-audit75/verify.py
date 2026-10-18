"""Source-bound exact audit of the classical complementary-block identity.
@woklerx, substantial OpenAI Codex assistance. Apache-2.0.
The original mixed-rank application is Douglas Colkitt's kappa-nine work.
"""
import argparse
import ast
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '2921874911956718fcaaaf9396fe8267b3cfa9f0'
FILES = ('research/kappa-nine/README.md', 'research/kappa-nine/MIXED-RANK-TEST.md',
         'research/kappa-nine/mixed_rank_obstruction.py',
         'research/kappa-nine/mixed-rank-obstruction.json',
         'docs/research/community-batch952-review.md')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(json.loads(json.dumps(value)), sort_keys=True, separators=(',', ':'), allow_nan=False)


def pins(package=HERE, root=ROOT):
    manifest = json.loads((package / 'SOURCES.json').read_text(encoding='utf-8'))
    need(manifest['base'] == BASE and set(manifest['files']) == set(FILES), 'exact source inventory/base')
    for name in FILES:
        raw = (root / name).read_bytes().replace(b'\r\n', b'\n')
        need(sha256(raw).hexdigest() == manifest['files'][name], 'source hash: ' + name)
    snapshot = (package / 'BASE-SELECTED.json').read_bytes().replace(b'\r\n', b'\n')
    need(sha256(snapshot).hexdigest() == manifest['selected_snapshot_sha256'], 'selected snapshot hash')
    selected = json.loads(snapshot)
    need(selected['kappa'] == '1661960547713947/1000000000000000000', 'frozen selected kappa')
    need(selected['audited_source_head'] == '1960cfa919a0945d0ca4cb14ea96237000037903', 'frozen source head')


def source_matrix():
    tree = ast.parse((ROOT / FILES[2]).read_text(encoding='utf-8'))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'local_control')
    nodes = [n for n in fn.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'a' for t in n.targets)]
    need(len(nodes) == 1, 'unique source matrix')
    matrix = ast.literal_eval(nodes[0].value)
    need(len(matrix) == 6 and all(len(r) == 6 and all(type(x) is int for x in r) for r in matrix), 'source matrix shape')
    receipt = json.loads((ROOT / FILES[3]).read_text(encoding='utf-8'))['local_exact_control']
    need(matrix == receipt['A'], 'source receipt matrix')
    return matrix, receipt


def det3(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])) % 3


def inverse3(a):
    d = det3(a)
    need(d != 0, 'singular matrix')
    result = [[0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            rows = [r for r in range(3) if r != j]
            cols = [c for c in range(3) if c != i]
            minor = a[rows[0]][cols[0]]*a[rows[1]][cols[1]] - a[rows[0]][cols[1]]*a[rows[1]][cols[0]]
            result[i][j] = ((-1)**(i+j)*minor*pow(d, -1, 3)) % 3
    return result


def small_rank(a, rows, cols):
    # Nontrivial proper 3x3 subblocks have at most two rows and columns.
    need(1 <= len(rows) <= 2 and 1 <= len(cols) <= 2, 'small rank domain')
    if len(rows) == len(cols) == 2:
        if (a[rows[0]][cols[0]]*a[rows[1]][cols[1]] - a[rows[0]][cols[1]]*a[rows[1]][cols[0]]) % 3:
            return 2
    return int(any(a[i][j] % 3 for i in rows for j in cols))


def finite_census():
    subsets = [tuple(i for i in range(3) if mask >> i & 1) for mask in range(1, 7)]
    blocks = [(i, j, tuple(k for k in range(3) if k not in j), tuple(k for k in range(3) if k not in i))
              for i in subsets for j in subsets]
    histogram, nullities = Counter(), Counter()
    trace = sha256()
    count, cases = 0, 0
    wrong_complement = None
    for flat in product(range(3), repeat=9):
        a = [list(flat[k:k+3]) for k in (0, 3, 6)]
        if det3(a) == 0:
            continue
        b = inverse3(a)
        for left, right in ((a, b), (b, a)):
            need(all(sum(left[i][k]*right[k][j] for k in range(3)) % 3 == int(i == j)
                     for i in range(3) for j in range(3)), 'adjugate inverse check')
        count += 1
        ranks = []
        for i, j, jc, ic in blocks:
            r, s = small_rank(a, i, j), small_rank(b, jc, ic)
            need(r - s == len(i) + len(j) - 3, 'complementary-block rank identity')
            histogram[(len(i), len(j), r, s)] += 1
            nullities[len(j)-r] += 1
            cases += 1
            ranks.extend((r, s))
            if wrong_complement is None and r - small_rank(b, ic, jc) != len(i)+len(j)-3:
                wrong_complement = {'A': a, 'B': b, 'I': list(i), 'J': list(j),
                                    'correct_inverse_rows': list(jc), 'correct_inverse_columns': list(ic)}
        trace.update(bytes(flat))
        trace.update(bytes(x for row in b for x in row))
        trace.update(bytes(ranks))
    need(count == 11232 and cases == 404352, 'complete GL3 F3 coverage')
    need(wrong_complement is not None, 'wrong-complement control found')
    return {'field': 3, 'all_matrices': 19683, 'invertible_matrices': count, 'proper_block_pairs_per_matrix': 36,
            'block_pairs': cases, 'rank_histogram': {','.join(map(str,k)): v for k,v in sorted(histogram.items())},
            'nullity_histogram': dict(sorted(nullities.items())), 'complete_trace_sha256': trace.hexdigest(),
            'wrong_complement_control': wrong_complement}


def run():
    pins()
    a, receipt = source_matrix()
    return {'schema': 1, 'base': BASE, 'seed': 75, 'status': 'PASS_CLASSICAL_COMPLEMENTARY_NULLITY',
            'source_matrix': a, 'source_claimed_block_ranks': [receipt['complement_ranks'], receipt['exceptional_distinguished_ranks']],
            'finite_census': finite_census(),
            'scope': 'Classical inverse-block rank identity and local six-by-six application; no new Fano exclusion or kappa'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    path = HERE / 'EXPECTED.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    else:
        need(canonical(result) == canonical(json.loads(path.read_text(encoding='utf-8'))), 'complete finite receipt mismatch')
    print('PASS_COMPLEMENTARY_NULLITY_F3 matrices=11232 block_pairs=404352 no_new_kappa')
