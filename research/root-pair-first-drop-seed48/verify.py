"""Exact first cost-six odd-root-pair boundary beyond PR968's <=24 theorem.

@woklerx with substantial OpenAI Codex assistance. Apache-2.0.
PR968/themilkman216 and PR717/DreamingOfClouds supply the credited model.
"""
import argparse
from collections import Counter, deque
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '2921874911956718fcaaaf9396fe8267b3cfa9f0'
SOURCES = {'research/complex-frame-pair-decoders/PROOF.md',
           'research/complex-frame-pair-decoders/verify.py',
           'research/complex-frame-pair-decoders/README.md'}
spec = importlib.util.spec_from_file_location('local_root_model', HERE/'explore.py')
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def dense_rank(matrix):
    """Independent rectangular elimination on literal 0/1 entries."""
    values = [list(row) for row in matrix]
    if not values:
        return 0
    pivot_row = 0
    for col in range(len(values[0])):
        pivot = next((i for i in range(pivot_row, len(values)) if values[i][col]), None)
        if pivot is None:
            continue
        values[pivot_row], values[pivot] = values[pivot], values[pivot_row]
        for row in range(len(values)):
            if row != pivot_row and values[row][col]:
                values[row] = [(x+y)%2 for x, y in zip(values[row], values[pivot_row])]
        pivot_row += 1
        if pivot_row == len(values):
            break
    return pivot_row


def dense_cost(roots, supports, a, b, puncture):
    rows = [i for i in range(120) if (supports[a]&~puncture)>>i&1]
    cols = [i for i in range(120) if (supports[b]&~puncture)>>i&1]
    return dense_rank([[(dot(roots[i], roots[j])//4+1)%2 for j in cols] for i in rows])


def inverse(matrix):
    rows = [[Q(x) for x in row]+[Q(i==j) for j in range(8)] for i, row in enumerate(matrix)]
    for col in range(8):
        pivot = next((i for i in range(col, 8) if rows[i][col]), None)
        need(pivot is not None, 'singular decoder basis')
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scalar = rows[col][col]
        rows[col] = [x/scalar for x in rows[col]]
        for i in range(8):
            if i != col:
                scalar = rows[i][col]
                rows[i] = [x-scalar*y for x, y in zip(rows[i], rows[col])]
    return [row[8:] for row in rows]


def decoder(roots, a, b):
    """One odd root pair plus a rational basis of the partner's perpendicular."""
    need(abs(dot(roots[a], roots[b])) == 4, 'odd root pair required')
    alpha, beta = roots[a], roots[b]
    pivot = next(i for i, value in enumerate(beta) if value)
    columns = [[Q(x, 2) for x in alpha]]
    for j in range(8):
        if j == pivot:
            continue
        column = [Q(0)]*8
        column[j] = 1
        column[pivot] = -Q(beta[j], beta[pivot])
        columns.append(column)
    A = [list(row) for row in zip(*columns)]
    inv = inverse(A)
    B = [[2*inv[j][i] for j in range(8)] for i in range(8)]
    need(all(dot(A[i], B[j]) == 2*(i==j) for i in range(8) for j in range(8)), 'A B transpose identity')
    return A, B


def decoder_check(roots, pairing, puncture, A, B):
    live = [i for i in range(120) if not puncture>>i&1]
    D = [[sum(Q(roots[i][r], 2)*A[r][k] for r in range(8)) for k in range(8)] for i in live]
    T = [[sum(Q(roots[i][r], 2)*B[r][k] for r in range(8)) for k in range(8)] for i in live]
    need(all(dot(D[ii], T[jj]) == Q(dot(roots[i], roots[j]), 2)
             for ii, i in enumerate(live) for jj, j in enumerate(live)), 'all-entry exact decoder identity')
    costs = []
    for k in range(8):
        row_ids = [live[i] for i, values in enumerate(D) if values[k]]
        col_ids = [live[i] for i, values in enumerate(T) if values[k]]
        mask = sum(1<<j for j in col_ids)
        fast = model.rank([pairing[i]&mask for i in row_ids])
        slow = dense_rank([[(dot(roots[i], roots[j])//4+1)%2 for j in col_ids] for i in row_ids])
        need(fast == slow, 'independent decoder term rank')
        costs.append(fast)
    return {'ports': len(live), 'terms': 8, 'identity_entries': len(live)**2,
            'term_costs': costs, 'copy_cost': sum(costs), 'cost_per_port': str(Q(sum(costs), len(live))),
            'A': [[str(x) for x in row] for row in A], 'B': [[str(x) for x in row] for row in B]}


def reflection_orbit(roots, pairing, a, b):
    simple = [(1,-1,-1,-1,-1,-1,-1,1), (2,2,0,0,0,0,0,0), (-2,2,0,0,0,0,0,0)]
    simple += [tuple(-2 if i == k else 2 if i == k+1 else 0 for i in range(8)) for k in range(1,6)]
    index = {root:i for i, root in enumerate(roots)}
    permutations = []
    for normal in simple:
        permutation = []
        for root in roots:
            product = dot(root, normal)
            need(product%4 == 0, 'integral reflection')
            reflected = tuple(x-product//4*y for x, y in zip(root, normal))
            representative = max(reflected, tuple(-x for x in reflected))
            need(representative in index, 'reflection closes root lines')
            permutation.append(index[representative])
        need(len(set(permutation)) == 120, 'reflection is a permutation')
        need(all(((pairing[i]>>j)&1) == ((pairing[permutation[i]]>>permutation[j])&1)
                 and (dot(roots[i], roots[j]) == 0) == (dot(roots[permutation[i]], roots[permutation[j]]) == 0)
                 for i in range(120) for j in range(120)), 'reflection preserves supports and pairing')
        permutations.append(permutation)
    queue, seen = deque([(a,b)]), {(a,b)}
    while queue:
        i,j = queue.popleft()
        for permutation in permutations:
            pair = (permutation[i], permutation[j])
            if pair not in seen:
                seen.add(pair)
                queue.append(pair)
    expected = {(i,j) for i in range(120) for j in range(120) if abs(dot(roots[i], roots[j])) == 4}
    need(seen == expected and len(seen) == 6720, 'complete ordered odd-pair orbit')
    return {'generators': 8, 'root_line_permutations_checked': 8,
            'ordered_pairs': len(seen), 'pairing_and_support_comparisons': 8*120*120}


def run():
    pins = read(HERE/'SOURCES.json')
    need(pins['base_commit'] == BASE and set(pins['files']) == SOURCES, 'exact source inventory')
    for name, expected in pins['files'].items():
        raw = (ROOT/name).read_bytes().replace(b'\r\n', b'\n')
        need(hashlib.sha256(raw).hexdigest() == expected, 'source pin: '+name)
    roots,pairing,labels,viol,supports = model.setup()
    need(len(roots) == 120 and len(set(roots)) == 120 and all(dot(r,r) == 8 for r in roots), 'E8 line model')
    need(model.rank(pairing) == model.rank(labels) == 9 and len(set(viol)) == 511, 'full label and functional spaces')
    a = 48
    b = next(i for i in range(120) if abs(dot(roots[a],roots[i])) == 4)
    need(b == 0, 'seeded canonical pair')
    orbit = reflection_orbit(roots, pairing, a, b)
    side_masks, pair_counts, minimum_unions = [], [], []
    for side in (a,b):
        restricted = [v&supports[side] for v in viol]
        unions = [x|y for i,x in enumerate(restricted) for y in restricted[i+1:]]
        need(len(unions) == 130305, 'all independent functional pairs')
        minimum_unions.append(min(x.bit_count() for x in unions))
        masks = {x for x in unions if x.bit_count() <= 25}
        side_masks.append(masks)
        pair_counts.append(sum(x.bit_count() <= 25 for x in unions))
    masks = side_masks[0]|side_masks[1]
    need(minimum_unions == [25,25] and len(masks) == 126, 'complete first-drop candidate census')
    costs = Counter()
    for mask in masks:
        fast = model.cost(pairing,supports,a,b,mask)
        slow = dense_cost(roots,supports,a,b,mask)
        need(fast == slow, 'independent 25-puncture pairing rank')
        costs[fast] += 1
    need(costs == Counter({7:126}), 'all p<=25 candidates retain cost seven')
    witness = None
    for mask in sorted(masks):
        for extra in range(120):
            if mask>>extra&1:
                continue
            puncture = mask|(1<<extra)
            if model.cost(pairing,supports,a,b,puncture) <= 6:
                witness = puncture
                witness_parent, witness_extra = mask, extra
                break
        if witness is not None:
            break
    need(witness is not None and witness.bit_count() == 26, '26-puncture witness')
    need(dense_cost(roots,supports,a,b,witness) == 6, 'independent witness rank six')
    A,B = decoder(roots,a,b)
    completion = decoder_check(roots,pairing,witness,A,B)
    need(completion['term_costs'][0] == 6, 'completion preserves root-pair term')

    controls = []
    def rejected(label, action, reason):
        try:
            action()
        except ValueError as error:
            need(reason in str(error), 'unexpected mutation failure: '+label)
            controls.append(label)
            return
        raise ValueError('accepted mutation: '+label)
    rejected('rank-six underclaim at 25 punctures', lambda: need(any(value<=6 for value in costs), 'no rank six'), 'no rank six')
    rejected('omit a candidate mask', lambda: need(len(masks-{min(masks)}) == 126, 'coverage count'), 'coverage count')
    orthogonal = next(i for i in range(120) if dot(roots[a],roots[i]) == 0)
    rejected('orthogonal pair outside decoder term class', lambda: decoder(roots,a,orthogonal), 'odd root pair')
    badB = [[x/2 if j==0 else x for j,x in enumerate(row)] for row in B]
    rejected('missing dual scale factor', lambda: decoder_check(roots,pairing,witness,A,badB), 'all-entry exact decoder identity')
    wrong_pairing = [sum(((dot(x,y)//4)&1)<<j for j,y in enumerate(roots)) for x in roots]
    rejected('omit unit label in pairing', lambda: need(model.rank(wrong_pairing) == 9, 'label rank'), 'label rank')
    for i in range(120):
        if witness>>i&1:
            smaller = witness^(1<<i)
            need(model.cost(pairing,supports,a,b,smaller) >= 7, 'every one-line restoration crosses boundary')
    controls.append('all 26 one-line restorations raise term cost to at least seven')
    return {'status':'PASS_ROOT_PAIR_FIRST_DROP_S48', 'base_commit':BASE, 'seed':48,
            'model':'PR717 B14 / PR968 exact label pairing; distinct nonorthogonal root normals',
            'canonical_pair':[a,b], 'root_vectors_doubled':[roots[a],roots[b]], 'orbit':orbit,
            'functional_pairs_per_support':130305, 'minimum_codimension_two_deletions':minimum_unions,
            'attaining_functional_pairs_per_support':pair_counts,
            'distinct_masks_per_support':[len(x) for x in side_masks],
            'common_masks':len(side_masks[0]&side_masks[1]), 'candidate_masks_at_25':126,
            'ranks_at_25':dict(sorted(costs.items())), 'candidate_masks_hex':sorted(hex(x) for x in masks),
            'threshold':26, 'witness_puncture':[i for i in range(120) if witness>>i&1],
            'parent_25_puncture':[i for i in range(120) if witness_parent>>i&1],
            'added_line':witness_extra,
            'parent_support_dimensions':[model.rank([pairing[i] for i in range(120) if (supports[k]&~witness_parent)>>i&1]) for k in (a,b)],
            'parent_pairing_rank':model.cost(pairing,supports,a,b,witness_parent),
            'witness_support_dimensions':[model.rank([pairing[i] for i in range(120) if (supports[k]&~witness)>>i&1]) for k in (a,b)],
            'witness_pairing_rank':6, 'exact_eight_term_completion':completion,
            'controls':controls,
            'scope':'First term-cost-six puncture threshold for odd root pairs only. No arbitrary-normal, whole-decoder optimum, compiled supplier, native replay, or kappa claim.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate',action='store_true')
    args=parser.parse_args()
    result=run()
    path=HERE/'CERTIFICATE.json'
    if args.write_certificate:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    else:
        need(canon(result)==canon(read(path)), 'certificate mismatch')
    print('PASS_ROOT_PAIR_FIRST_DROP_S48 threshold=26 candidates25=126 orbit=6720 rank26=6 completion_cost={} ports=94 controls=6'.format(result['exact_eight_term_completion']['copy_cost']))


if __name__=='__main__':main()
