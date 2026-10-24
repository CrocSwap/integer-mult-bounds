"""Check the controller source and the residual factorization."""

from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import io
import json
import subprocess
import tarfile


BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
ARCHIVE_HASH = "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754"
MEMBER = "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz"
MEMBER_HASH = "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518"
INTERFACE_HASH = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return list(map(list, zip(*a)))


def multiply(a, b):
    bt = transpose(b)
    return [[sum(x*y for x, y in zip(row, col)) for col in bt] for row in a]


def subtract(a, b):
    return [[x-y for x, y in zip(row, col)] for row, col in zip(a, b)]


def rank(a):
    b = [list(map(Q, row)) for row in a]
    r = 0
    for j in range(len(b[0])):
        k = next((i for i in range(r, len(b)) if b[i][j]), None)
        if k is None:
            continue
        b[r], b[k] = b[k], b[r]
        d = b[r][j]
        b[r] = [x/d for x in b[r]]
        for i in range(r+1, len(b)):
            d = b[i][j]
            if d:
                b[i] = [x-d*y for x, y in zip(b[i], b[r])]
        r += 1
        if r == len(b):
            break
    return r


def inverse(a):
    n = len(a)
    b = [list(map(Q, row))+e for row, e in zip(a, eye(n))]
    for j in range(n):
        k = next(i for i in range(j, n) if b[i][j])
        b[j], b[k] = b[k], b[j]
        d = b[j][j]
        b[j] = [x/d for x in b[j]]
        for i in range(n):
            if i != j:
                d = b[i][j]
                if d:
                    b[i] = [x-d*y for x, y in zip(b[i], b[j])]
    return [row[n:] for row in b]


def omega(n):
    out = [[Q(0) for _ in range(8*n)] for _ in range(8*n)]
    for pair in range(4):
        for j in range(n):
            x, y = (2*pair)*n+j, (2*pair+1)*n+j
            out[x][y], out[y][x] = Q(1), Q(-1)
    return out


def controller(recipe, kernels, include_terminal=False):
    n = len(kernels[0])
    c = eye(8*n)
    for event in recipe:
        kind = event['kind']
        if kind == 'local':
            pair, stage = event['pair'], event['stage']
            source = 2*pair+int(event['reverse'])
            target = 2*pair+int(not event['reverse'])
            sign = -1 if event['reverse'] else 1
            old = [row.copy() for row in c[source*n:(source+1)*n]]
            delta = multiply(kernels[stage], old)
            for j, row in enumerate(delta):
                t = target*n+j
                c[t] = [a+sign*b for a, b in zip(c[t], row)]
        elif kind == 'bridge':
            i, j, q = event['dst'], event['src'], event['coefficient']
            for bank_t, bank_s, factor in ((2*i, 2*j, q), (2*j+1, 2*i+1, -q)):
                for p in range(n):
                    t, s = bank_t*n+p, bank_s*n+p
                    c[t] = [a+factor*b for a, b in zip(c[t], c[s])]
        elif kind == 'terminal' and include_terminal:
            for pair in range(event['pairs']):
                for p in range(n):
                    x, y = 2*pair*n+p, (2*pair+1)*n+p
                    c[x], c[y] = c[y], [-q for q in c[x]]
    return c


def bank_sources(recipe):
    c = eye(8)
    rows = []
    for event in recipe:
        if event['kind'] == 'local':
            i = event['pair']
            source = 2*i+int(event['reverse'])
            target = 2*i+int(not event['reverse'])
            sign = -1 if event['reverse'] else 1
            rows.append(c[source].copy())
            c[target] = [a+sign*b for a, b in zip(c[target], c[source])]
        elif event['kind'] == 'bridge':
            i, j, q = event['dst'], event['src'], event['coefficient']
            c[2*i] = [a+q*b for a, b in zip(c[2*i], c[2*j])]
            c[2*j+1] = [a-q*b for a, b in zip(c[2*j+1], c[2*i+1])]
    return rows, c


def toy_check(recipe, sources, distinct):
    # These exact rows have norm squared 56. They are not cover data.
    rows = [[Q(6), Q(4), Q(2)] for _ in range(9)]
    if distinct:
        rows[1] = [Q(2), Q(6), Q(4)]
    require(all(sum(x*x for x in row) == 56 for row in rows), 'Toy row norm')
    kernels = [subtract(eye(3), [[x*y/4 for y in row] for x in row]) for row in rows]
    actual = controller(recipe, kernels)
    ideal = controller(recipe, [eye(3)]*9)
    residual = subtract(multiply(inverse(ideal), actual), eye(24))
    v = [[b*x for b in source for x in row] for source, row in zip(sources, rows)]
    om = omega(3)
    g = multiply(multiply(v, om), transpose(v))
    b = [[4*Q(i == j)-(g[i][j] if i > j else 0) for j in range(9)] for i in range(9)]
    predicted = multiply(multiply(multiply(om, transpose(v)), inverse(b)), v)
    require(residual == predicted, 'The residual factorization failed')
    expected = 9 if distinct else 8
    require(rank(v) == rank(residual) == expected, 'The residual rank is wrong')
    wrong = [[4*Q(i == j)+(g[i][j] if i > j else 0) for j in range(9)] for i in range(9)]
    rejected = residual != multiply(multiply(multiply(om, transpose(v)), inverse(wrong)), v)
    require(rejected, 'The wrong-sign control did not fail')
    return {'syndrome_rank': rank(v), 'residual_rank': rank(residual),
            'wrong_triangular_sign_rejected': rejected}


def run(repo, interface):
    raw = subprocess.run(['git', 'show', BASE+':'+ARCHIVE], cwd=repo,
                         check=True, capture_output=True).stdout
    require(sha256(raw).hexdigest() == ARCHIVE_HASH, 'The archive pin changed')
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        member = archive.extractfile(MEMBER).read()
    require(sha256(member).hexdigest() == MEMBER_HASH, 'The controller pin changed')
    recipe = json.loads(gzip.decompress(member))['recipe']
    source = interface.read_bytes()
    require(sha256(source).hexdigest() == INTERFACE_HASH, 'The interface pin changed')
    data = json.loads(source)
    r = [[Q(row.get(str(p), '0')) for p in range(112)] for row in data['R']]
    require(multiply(r, transpose(r)) == [[56*Q(i == j) for j in range(8)] for i in range(8)],
            'The centre matrix Gram identity failed')
    require([event['stage'] for event in recipe if event['kind'] == 'local'] == list(range(9)),
            'The selected stages changed')
    sources, ideal = bank_sources(recipe)
    require(controller(recipe, [eye(1)]*9, True) == eye(8), 'The ideal controller is not identity')
    require(ideal == [[-x for x in row] for row in omega(1)], 'The ideal preterminal map changed')
    relation = [Q(x) for x in (1, -1, -1, 1, 1, -1, -1, 1, 1)]
    require(all(sum(relation[i]*sources[i][j] for i in range(9)) == 0 for j in range(8)),
            'The stated bank relation failed')
    require(all(rank(sources[:i]+sources[i+1:]) == 8 for i in range(9)),
            'A proper subset of the bank rows is dependent')
    bank_g = multiply(multiply(sources, omega(1)), transpose(sources))
    area = sum(relation[i]*relation[j]*bank_g[i][j] for i in range(9) for j in range(i))
    require(area == 4, 'The bank relation area changed')
    compression = sum(x*x for x in relation)*Q(4, 56)-area
    require(compression == Q(-47, 14), 'The relation compression changed')
    first_bridge = next(i for i, event in enumerate(recipe) if event['kind'] == 'bridge')
    omitted = recipe[:first_bridge]+recipe[first_bridge+1:]
    require(controller(omitted, [eye(1)]*9, True) != eye(8), 'The missing-bridge control did not fail')
    return {
        'status': 'PASS_SELECTED_CONTROLLER_RESIDUAL_FACTORIZATION',
        'base': BASE, 'archive': ARCHIVE, 'archive_sha256': ARCHIVE_HASH,
        'controller_member': MEMBER, 'controller_member_sha256': MEMBER_HASH,
        'interface_sha256': INTERFACE_HASH,
        'bank_sources': [[int(x) for x in row] for row in sources],
        'bank_relation': [int(x) for x in relation],
        'bank_source_rank': 8, 'independent_eight_row_subsets': 9,
        'bank_relation_area': str(area), 'relation_compression': str(compression),
        'same_centre_space_toy': toy_check(recipe, sources, False),
        'distinct_centre_space_toy': toy_check(recipe, sources, True),
        'missing_bridge_rejected': True,
        'proved_in_note': {
            'full_residual_rank': '72 |G| - dim(intersection_s im(R_s^*))',
            'proper_subset_residual_rank': '8 |S| |G| for every proper set S of omitted stages',
            'conditional_two_stage_bound': 'rank / |G| >= 13168/183 > 71',
            'relation_compression': '-47/14 times the ambient common-image inner product',
        },
        'scope': 'Exact controller algebra and finite rational checks. The group rank bound uses the separate routed-projection theorem. No native correction, child-cost lower bound, supplier admission, or kappa claim.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--interface', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.repo, args.interface)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'])
    print('proper_subsets=independent residual_rank=72|G|-common_image_dimension')
    print('native_supplier_or_kappa_claim=false')
