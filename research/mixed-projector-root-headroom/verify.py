"""Check the exact linear algebra used in the mixed-root headroom proof.

The written proof supplies the quantified arguments. This replay checks
their finite matrices and identities, with no numerical search inputs.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, permutations, product
from pathlib import Path
import json
import importlib.util
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Laurent:
    """A finite rational Laurent polynomial in the endpoint parameter r."""
    def __init__(self, terms):
        self.terms = {k: Q(v) for k, v in terms.items() if v}

    @staticmethod
    def cast(value):
        return value if isinstance(value, Laurent) else Laurent({0: value})

    def __add__(self, other):
        out = dict(self.terms)
        for k, v in self.cast(other).terms.items():
            out[k] = out.get(k, 0)+v
        return Laurent(out)

    __radd__ = __add__

    def __neg__(self):
        return Laurent({k: -v for k, v in self.terms.items()})

    def __sub__(self, other):
        return self+-self.cast(other)

    def __rsub__(self, other):
        return self.cast(other)+-self

    def __mul__(self, other):
        out = {}
        for a, x in self.terms.items():
            for b, y in self.cast(other).terms.items():
                out[a+b] = out.get(a+b, 0)+x*y
        return Laurent(out)

    __rmul__ = __mul__

    def __eq__(self, other):
        return self.terms == self.cast(other).terms


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def mul(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def add(a, b, factor=1):
    return [[x+factor*y for x, y in zip(row, other)] for row, other in zip(a, b)]


def hcat(*matrices):
    return [sum((list(m[i]) for m in matrices), []) for i in range(len(matrices[0]))]


def rref(a):
    out = [[Q(x) for x in row] for row in a]
    pivots = []
    for col in range(len(out[0])):
        pos = next((i for i in range(len(pivots), len(out)) if out[i][col]), None)
        if pos is None:
            continue
        row = len(pivots)
        out[row], out[pos] = out[pos], out[row]
        scale = out[row][col]
        out[row] = [x/scale for x in out[row]]
        for i in range(len(out)):
            if i != row:
                scale = out[i][col]
                out[i] = [x-scale*y for x, y in zip(out[i], out[row])]
        pivots.append(col)
    return out, pivots


def rank(a):
    return len(rref(a)[1])


def columns(a):
    return [[row[j] for j in rref(a)[1]] for row in a]


def rows(a):
    return transpose(columns(transpose(a)))


def inverse(a):
    n = len(a)
    out, pivots = rref(hcat(a, eye(n)))
    need(pivots == list(range(n)), 'Invertible rational matrix')
    return [row[n:] for row in out]


def determinant(a):
    n = len(a)
    out = 0
    for order in permutations(range(n)):
        term = (-1)**sum(order[i] > order[j] for i in range(n) for j in range(i+1, n))
        for i, j in enumerate(order):
            term *= a[i][j]
        out += term
    return out


def canonical(n):
    identity, prefix = eye(n), eye(n)
    us, vs, prefixes = [], [], []
    for i in range(n+1):
        u = [[Q(j == i)] for j in range(n)] if i < n else [[Q(-(-1)**j)] for j in range(n)]
        v = [[Q((i > j)-(i < j)) for j in range(n)]]
        query = mul(u, v)
        need(mul(v, u) == [[0]], 'Every canonical query is square-zero')
        prefix = mul(add(identity, query, -2), prefix)
        us.append(u); vs.append(v); prefixes.append(prefix)
    need(prefix == [[-x for x in row] for row in identity], 'Complete canonical minus endpoint')
    return us, vs, prefixes


def closure(u, v, operators):
    a, b = columns(u), rows(v)
    while True:
        aa = columns(hcat(a, *(mul(p, a) for p in operators)))
        bb = rows(b+sum((mul(b, p) for p in operators), []))
        if len(aa[0]) == len(a[0]) and len(bb) == len(b):
            break
        a, b = aa, bb
    dims = [len(a[0]), len(b), rank(mul(b, a))]
    return a, b, dims, dims[0]+dims[1]-dims[2]


def structural_checks():
    g = [[Q((i > j)-(i < j)) for j in range(4)] for i in range(4)]
    need(determinant(g) == 1, 'Every ordered four-site Gram minor is invertible')
    need(determinant([row[:3] for row in g[:3]]) == 0, 'The three-site Gram minor is singular')
    need(g[0][1]*g[1][2]*g[2][0] == 1 and g[0][2]*g[2][1]*g[1][0] == -1,
         'The two directed triple products have opposite signs')
    small, star = 0, 0
    supports = [set(c) for c in combinations(range(4), 2)]
    for triple in combinations_with_replacement(supports, 3):
        a, b, c = triple
        if not (a & b and a & c and b & c):
            continue
        if len(a | b | c) <= 3:
            small += 1
        else:
            need(a & b == a & c == b & c and len(a & b) == 1,
                 'Three intersecting two-sets are small or a three-arm star')
            star += 1
    u, v, prefix = canonical(6)
    basic, unique = [], {}
    for i in range(7):
        a, b, dims, lower = closure(u[i], v[i], [prefix[i]])
        basic.append(dims+[lower])
        if dims == [2, 2, 2]:
            p = mul(mul(a, inverse(mul(b, a))), b)
            need(mul(p, p) == p and mul(p, prefix[i]) == mul(prefix[i], p), 'Unique rank-two interior projector')
            unique[i] = p
    need([x[-1] for x in basic] == [2, 2, 4, 2, 4, 2, 2], 'Exact single-site rank bounds')
    conditional = {str(i): [closure(u[j], v[j], [prefix[j], p])[3] for j in range(7)]
                   for i, p in unique.items()}
    expected = {'1': [2, 2, 4, 4, 6, 4, 4], '3': [4, 4, 4, 2, 4, 4, 4],
                '5': [4, 4, 6, 4, 4, 2, 2]}
    need(conditional == expected, 'All ranks forced by an interior rank-two site')
    a, b = hcat(u[0], u[6]), v[0]+v[6]
    coincident = mul(mul(a, inverse(mul(b, a))), b)
    same = [closure(u[j], v[j], [prefix[j], coincident])[3] for j in range(7)]
    need(same == [2, 4, 4, 6, 4, 4, 2], 'Coincident endpoint projectors allow no rank-three interior')

    # All computations below take place in Q[r,r^-1]. No parameter is sampled.
    r, ri = Laurent({1: 1}), Laurent({-1: 1})
    e0, un = u[0], u[6]
    w = add(e0, un, -r)
    mask_checks = []
    for i in (1, 3, 5):
        need(mul(v[i], w) == [[1+r]], 'An a-only mask first forces r=-1')
        wminus = add(e0, un)
        need(mul(mul(v[i], prefix[i]), wminus) == [[2]], 'The a-only exceptional parameter also fails')
        abc = closure(hcat(e0, un, u[i]), v[0]+v[6]+v[i], [prefix[i]])
        need(abc[3] >= 4, 'The abc mask cannot have rank three')
        a = hcat(w, u[i], mul(prefix[i], w))
        if i == 3:
            four = hcat(a, mul(prefix[i], u[i]))
            need(determinant([four[j] for j in (0, 1, 3, 4)]) == -4*r,
                 'The bc mask has a nonzero four-dimensional minor')
            mask_checks.append({'site': i, 'bc_rejection': 'minor -4r', 'abc_rank_lower': abc[3]})
            continue
        if i == 1:
            minor = determinant([a[j] for j in (0, 1, 2)])
            need(minor == 2*r*r, 'The site-one image has dimension three for every nonzero r')
            action = [[0, ri, 1-2*ri], [0, -1-2*ri, 4*ri], [1, -ri, 2*ri]]
        else:
            need(determinant([a[j] for j in (0, 1, 5)]) == 2, 'The site-five image has dimension three')
            action = [[0, 1, -1], [0, -1, 0], [1, 1, -2]]
        need(mul(prefix[i], a) == mul(a, action), 'Complete invariant image, with the parameter retained')
        need(mul(v[i], a) == [a[0]], 'The bc equations force a0=0, hence r=1')
        at_one = hcat(add(e0, un, -1), u[i], mul(prefix[i], add(e0, un, -1)))
        need(mul(at_one, [[Q(1, 2)], [0], [Q(-1, 2)]]) == e0,
             'At r=1 the image contains e0 and b, so it cannot kill the nonzero a')
        mask_checks.append({'site': i, 'bc_rejection': 'r=1, then a lies in both image and kernel',
                            'abc_rank_lower': abc[3]})
    # Two rank-three stages use one line each in the common endpoint kernel.
    # Equal L lines or equal R lines would contain three query pairs in rank 3.
    # Distinct same-type lines would instead force the following nonzero sums.
    need(((-1+ri)+(1+ri)) == 2*ri and ((-1-r)+(1-r)) == -2*r,
         'Distinct L,L and R,R lines cannot satisfy their cross pairings')
    shared = []
    for sign in (-1, 1):
        pairings = [[ri, sign+1], [-sign-1, -r]]
        value = determinant(pairings)
        need(value == (-1 if sign == -1 else 3), 'L and R lines are always distinct in characteristic zero')
        shared.append(-1 if sign == -1 else 3)

    # A positive family retains every nonzero value of r, not only r=-1.
    w0 = add(e0, un)
    z = add(add(add(add(w0, w0, r), u[1], -r), u[5], -1), add(u[2], u[3], -1))
    aa = add(add(e0, un, r), z, -1)
    bb, cc = add(e0, aa, -1), add(e0, z, -1)
    left, right = add(add(u[1], w0, -1), z, ri), add(add(u[5], w0, -1), z)
    f = hcat(aa, bb, cc, add(u[3], u[4], -1), right, left)
    fi = [[1,1,0,1,1,ri], [1,1-ri,-ri,1-ri,1-ri,0],
          [0,0,1,0,0,1-ri], [0,0,1,1,0,0], [0,0,1,0,0,1],
          [0,1,1,1-r,1-r,0]]
    need(mul(f, fi) == mul(fi, f) == eye(6), 'All-parameter positive family has an exact inverse')
    family = []
    for site, support in [(0, [0,1]), (1, [0,1,5]), (5, [0,2,4]), (6, [0,2])]:
        mask = [[int(j == k and j in support) for k in range(6)] for j in range(6)]
        p = mul(mul(f, mask), fi)
        query = mul(u[site], v[site])
        need(mul(p, p) == p and mul(p, query) == mul(query, p) == query,
             'Every member of the positive family has compatible full projectors')
        need(mul(p, prefix[site]) == mul(prefix[site], p), 'Every positive-family prefix commutes')
        need(all(mul(p, old) == mul(old, p) for old in family), 'Every positive-family stage pair commutes')
        family.append(p)

    def floors(limit_rank_three):
        out = [None]*8
        for ranks in product((0, 2, 3, 4, 5, 6), repeat=7):
            full = sum(x != 0 for x in ranks)
            if sum(x == 2 for x in ranks) > 2:
                continue
            if any(x and x < basic[i][-1] for i, x in enumerate(ranks)):
                continue
            if any(ranks[i] == 2 and any(x and x < conditional[str(i)][j] for j, x in enumerate(ranks))
                   for i in (1, 3, 5)):
                continue
            if limit_rank_three and ranks[0] == ranks[6] == 2 and sum(x == 3 for x in ranks) > 2:
                continue
            idle = sum(max(0, x-2) for x in ranks)
            if out[full] is None or idle < out[full]:
                out[full] = idle
        return out
    lower = floors(True)
    need(lower == [0, 0, 0, 1, 2, 4, 6, 8], 'All full-site counts obey the stated idle lower bounds')
    need(floors(False)[5] == 3, 'The three-interior exclusion is needed for the five-full bound')
    return {'rank_two_support_cases': {'small_union': small, 'star': star},
            'single_site_rank_data': basic, 'interior_rank_two_forces': conditional,
            'coincident_endpoint_rank_lower': same, 'rank_three_mask_checks': mask_checks,
            'shared_LR_line_determinants': shared, 'idle_lower_by_full_count': lower,
            'positive_family': 'An explicit invertible root for every nonzero r, with sites 0,1,5,6 and the classified masks.',
            'parameter_ring': 'Q[r,r^-1]; r is not fixed to -1',
            'scope': 'Shortest rank-one queries; commuting ordinary scalar coefficients; characteristic zero for the six-field classification.'}


def normalization_checks():
    def zadd(a, b):
        return a[0]+b[0], a[1]+b[1]
    def zmul(a, b):
        return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]
    one, zero = (Q(1), Q(0)), (Q(0), Q(0))
    a, b = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))
    need(zadd(zmul(a, a), zmul(b, b)) == zero and zmul((2, 0), zmul(a, b)) == one,
         'lambda squared equals X in the polynomial ring modulo X squared minus one')
    need(zadd(zmul(a, b), zmul(b, a)) == one and zadd(zmul(a, a), zmul(b, b)) == zero,
         'The conjugate normalizer is the inverse')
    for q in (one, (-1, 0), (0, 1), (0, -1)):
        lam = zadd(a, zmul(b, zmul(q, q)))
        s = zmul(lam, q)
        need(zmul(s, s) == one and zmul(zadd(b, zmul(a, zmul(q, q))), s) == q,
             'All four central characters normalize and restore')
    # Two one-column characters q=-i give S=1 separately, but S=-1 globally.
    local = zmul(zadd(a, zmul(b, (-1, 0))), (0, -1))
    global_s = zmul(zadd(a, b), (-1, 0))
    need(local == one and global_s == (-1, 0) and zmul(local, local) != global_s,
         'Tensoring the one-column normalizer is not the global normalization')
    pair_checks = 0
    for width in range(1, 7):
        size = 1 << width
        for shift in range(1, size):
            pivot = shift & -shift
            pairs = [(x, x ^ shift) for x in range(size) if not x & pivot]
            need(sorted(x for pair in pairs for x in pair) == list(range(size)),
                 'Each nonzero binary translation is partitioned into disjoint pairs')
            pair_checks += len(pairs)
    return {'formal_identity': 'lambda^2=X, S^2=I, lambda^-1*S=q whenever q^2=X and X^2=I',
            'characters': 4, 'translation_pairs_checked': pair_checks,
            'tensor_of_one_column_normalizers_rejected': True,
            'scope': 'The polynomial identity proves all widths; the address enumeration is a finite control.'}


def central_free_checks():
    """Check coupled examples for the active-space reduction in EXTENSIONS.md."""
    examples = []
    for active in (2, 4, 6, 8):
        us, vs, _ = canonical(active)
        for inactive in (1, 3):
            size = active+inactive
            extended_u = [u+[[Q(0)] for _ in range(inactive)] for u in us]
            extended_v = [v[0]+[Q(j+2) for j in range(inactive)] for v in vs]
            matrices = [mul(u, [v]) for u, v in zip(extended_u, extended_v)]
            endpoint = eye(size)
            for matrix in matrices:
                need(rank(matrix) == 1 and rank(mul(matrix, matrix)) == 0,
                     'Every coupled example has rank-one square-zero queries')
                endpoint = mul(add(eye(size), matrix, -2), endpoint)
            expected = [[Q((-1 if i < active else 1) if i == j else 0)
                         for j in range(size)] for i in range(size)]
            need(endpoint == expected, 'The coupled inactive inputs cancel at the endpoint')
            U = hcat(*extended_u)
            V = extended_v
            need(rank(U) == active and rank(V) == active+1,
                 'The column-contained example need not have contained query rows')
            G = mul(V, U)
            lower = [[G[i][j] if i > j else Q(0) for j in range(active+1)]
                     for i in range(active+1)]
            Z = add(add(eye(active+1), lower, 2), G, -1)
            need(rank(Z) == 1 and all(Z[i][i] == 1 for i in range(active+1)),
                 'The compressed shortest tuple has a rank-one defect')
            dual = eye(size)
            for matrix in reversed(matrices):
                dual = mul(add(eye(size), transpose(matrix), -2), dual)
            need(dual == expected, 'Reverse transpose gives the row-contained case')
            need(any(matrices[0][i][j] for i in range(active) for j in range(active, size)),
                 'An individual query need not preserve the inactive eigenspace')
            examples.append({'active_fields': active, 'inactive_fields': inactive,
                             'query_count': active+1, 'ranks_U_V': [rank(U), rank(V)]})
    # Compression is not a homomorphism without the one-sided containment.
    a, b = eye(3), eye(3)
    a[0][2], b[2][0] = 1, 1
    need(mul(a, b)[0][0] != 1, 'Unrestricted cross-block cancellation cannot be compressed')
    return {'coupled_examples': examples, 'dual_examples': len(examples),
            'claim': 'r+1 square-zero queries with endpoint diag(-I_r,+I_s) reduce to an r-field shortest tuple; extra central-free outputs have no positive signed price.',
            'scope': 'The rank proof and tariff argument in EXTENSIONS.md are quantified. These exact examples are controls, not the universal proof.'}


def read_inputs():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    out = {}
    for pin in sources['files']:
        if pin['usage'] == 'input':
            data = (ROOT/pin['path']).read_bytes()
            need(sha256(data).hexdigest() == pin['sha256'], 'Exact input bytes: '+pin['path'])
            if pin['path'].endswith('.json'):
                out[pin['path']] = json.loads(data)
    return out


def run():
    data = read_inputs()
    root = data['research/mixed-projector-query-root/ROOT.json']
    receipt = data['research/mixed-root-source-composition/RESULT.json']
    need([s['stage_rank'] for s in root['sites'] if s['full']] == [2, 3, 3, 2], 'The actual root attains the two-idle floor')
    need(root['masks'] == [[1,1,1,1],[1,1,0,0],[0,0,1,1],[0,0,0,0],[0,0,1,0],[0,1,0,0]],
         'The actual root has the classified stage supports')
    ceiling = receipt['fixed_root_ceiling']
    need(Q(ceiling['ceiling']) == Q('.00328554') and Q(ceiling['finite_margin_upper']) < 0
         and Q(ceiling['tail_margin_upper']) < 0 and Q(ceiling['tail_derivative_upper']) < 0,
         'The complete composition supplies the stated authenticated price ceiling')
    need(receipt['price']['kappa_decimal'] == '0.00328551', 'Exact complete conditional result')
    spec = importlib.util.spec_from_file_location('mixed_root_reverse_caller', HERE/'caller_reverse.py')
    reverse = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reverse)
    caller = reverse.run(data['research/mixed-projector-query-root/CONTROLLER.json'])
    def module(path, name):
        spec = importlib.util.spec_from_file_location(name, path)
        loaded = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded)
        return loaded
    E = module(ROOT/'research/higher-moment-strictification/verify.py', 'headroom_intervals')
    next_cost = module(HERE/'next_cost_ceiling.py', 'headroom_next_cost')
    extension_price = next_cost.run(receipt['local'], E, Q('.00328554'))
    boundary = module(HERE/'boundary_modules.py', 'headroom_boundary_modules')
    current = data['research/mixed-root-contact-composition/RESULT.json']
    saving = Q(current['price']['kappa_decimal'])
    need(saving == Q('.00328621476572836015146308'), 'Exact latest complete composition claim')
    latest_extension = next_cost.run(current['local'], E, saving)
    boundary_price = module(HERE/'boundary_prices.py', 'headroom_boundary_prices')
    return {'status': 'PASS_MIXED_ROOT_MINIMUM_IDLE_CLASSIFICATION',
            'structure': structural_checks(), 'normalization': normalization_checks(),
            'central_free_extension': central_free_checks(),
            'rank_four_extension_price': extension_price,
            'boundary_modules': boundary.run(sys.modules[__name__]),
            'latest_source_extensions': {'source_head': current['source_head'],
                                         'rank_four_extension_price': latest_extension,
                                         'boundary_prices': boundary_price.run(current['local'], E, saving)},
            'separate_reverse_caller': caller,
            'inherited_complete_claim': '0.00328551', 'broader_family_ceiling': '0.00328554',
            'ceiling_evidence': 'Authenticated composition receipt and its separately registered full replay; no price engine is replaced here.',
            'ceiling_scope': 'Every six-field seven-query root with four full stages and at most two extra whole idles, all positive binary child sizes and shapes, fixed PR6353 source.',
            'new_kappa_increment': False, 'selected_frontier_changed': False}


if __name__ == '__main__':
    result = run()
    if sys.argv[1:] == ['--write-result']:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    else:
        need(not sys.argv[1:], 'No unrecognized verifier arguments')
        need(result == json.loads((HERE/'RESULT.json').read_text()), 'Exact scientific receipt')
    print(result['status'])
