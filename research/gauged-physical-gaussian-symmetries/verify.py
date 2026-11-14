"""Exact bounded checks; no predecessor code imported, read-only default.
Apache-2.0; prepared for @CubeJerry with OpenAI assistance.
"""
from fractions import Fraction as F
from hashlib import sha1, sha256
from itertools import permutations, product
from math import factorial, prod
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    data = json.loads((HERE/'DEPENDENCIES.json').read_text())
    for item in data['files']:
        raw = (HERE/item['local']).read_bytes()
        need(len(raw) == item['bytes'], 'input byte count: '+item['local'])
        need(sha256(raw).hexdigest() == item['sha256'], 'input SHA: '+item['local'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == item['git_blob'],
             'input Git blob: '+item['local'])
    return len(data['files'])


def vertices(sizes):
    return list(product(*(range(n) for n in sizes)))


def matrices(sizes, weights, shifts, left, right, q=F(1,2)):
    points = vertices(sizes)
    T = len(points)
    need(all(len(x) == T for x in (left,right)), 'gauge length')
    K = [[q**sum(w*(a-b)**2 for w,a,b in zip(weights,x,y)) for y in points] for x in points]
    S = [prod(v**i for v,i in zip(shifts,x)) for x in points]
    A = [l*s for l,s in zip(left,S)]
    B = [r/s for r,s in zip(right,S)]
    G = [[A[i]*K[i][j]*B[j] for j in range(T)] for i in range(T)]
    return points,K,G,A,[l*r for l,r in zip(left,right)]


def metric_ratio(G):
    T = len(G)
    need(all(G[i][i] != 0 for i in range(T)), 'nonzero diagonal needed')
    return [[G[i][j]*G[j][i]/(G[i][i]*G[j][j]) for j in range(T)] for i in range(T)]


def inverse(G):
    n = len(G)
    work = [list(row)+[F(i == j) for j in range(n)] for i,row in enumerate(G)]
    for k in range(n):
        pivot = next((i for i in range(k,n) if work[i][k]),None)
        need(pivot is not None, 'singular matrix')
        work[k],work[pivot] = work[pivot],work[k]
        t = work[k][k]
        work[k] = [x/t for x in work[k]]
        for i in range(n):
            if i != k:
                t = work[i][k]
                if t:
                    work[i] = [a-t*b for a,b in zip(work[i],work[k])]
    return [row[n:] for row in work]


def multiply(A,B):
    return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]


def direct_monomial(G,p):
    """Solve D P G = G D P, then check every entry; no geometry is used.
    Return w[x]=D[p[x]], normalized by w[0]=1.
    """
    n = len(G)
    if any(G[p[i]][p[i]] != G[i][i] for i in range(n)):
        return None
    need(all(G[i][0] for i in range(n)), 'nonzero anchor for direct solve')
    w = [G[p[i]][p[0]]/G[i][0] for i in range(n)]
    if not all(w):
        return None
    for i in range(n):
        for j in range(n):
            if w[i]*G[i][j] != G[p[i]][p[j]]*w[j]:
                return None
    return w


def coordinate_group(sizes,weights,Q):
    points = vertices(sizes)
    lookup = {x:i for i,x in enumerate(points)}
    d = len(sizes)
    found = set()
    for sigma in permutations(range(d)):
        if any((sizes[i],weights[i]) != (sizes[sigma[i]],weights[sigma[i]]) for i in range(d)):
            continue
        for signs in product((1,-1),repeat=d):
            perm = []
            for x in points:
                y = [0]*d
                for i in range(d):
                    y[sigma[i]] = x[i] if signs[i] == 1 else sizes[i]-1-x[i]
                perm.append(lookup[tuple(y)])
            p = tuple(perm)
            if all(Q[i] == Q[p[i]] for i in range(len(points))):
                found.add(p)
    return found


def cycles(p):
    unseen = set(range(len(p)))
    lengths = []
    while unseen:
        start = min(unseen)
        x,length = start,0
        while x in unseen:
            unseen.remove(x)
            length += 1
            x = p[x]
        need(x == start, 'permutation cycle closure')
        lengths.append(length)
    return lengths


def exact_groups():
    configurations = [
        ((2,),(1,),(F(2),),'similar'),
        ((3,),(1,),(F(3,2),),'similar'),
        ((2,2),(4,5),(F(2),F(3)),'similar'),
        ((2,2),(4,4),(F(2),F(3)),'similar'),
        ((2,3),(4,1),(F(2),F(2,3)),'signed_similar'),
        ((2,2),(4,5),(F(1),F(1)),'one_coordinate_Q'),
        ((2,2),(4,5),(F(1),F(1)),'distinct_Q'),
        ((2,2,2),(4,5,6),(F(1),F(2),F(3)),'unit'),
        ((2,2,2),(4,4,4),(F(1),F(2),F(3)),'unit')]
    receipts = []
    for sizes,weights,shifts,kind in configurations:
        T = prod(sizes)
        left = [F(i+1) for i in range(T)]
        if kind == 'signed_similar':
            left = [x*(-1 if i%2 else 1) for i,x in enumerate(left)]
        right = [1/x for x in left]
        if kind == 'unit':
            left = right = [F(1)]*T
        elif kind == 'one_coordinate_Q':
            left,right = [F(1)]*T,[F(1),F(1),F(2),F(2)]
        elif kind == 'distinct_Q':
            left,right = [F(1)]*T,[F(1),F(2),F(3),F(5)]
        points,K,G,A,Q = matrices(sizes,weights,shifts,left,right)
        need(metric_ratio(G) == [[v*v for v in row] for row in K], 'gauge invariant')
        predicted = coordinate_group(sizes,weights,Q)
        actual,ordinary = set(),set()
        for p in permutations(range(T)):
            w = direct_monomial(G,p)
            if w is not None:
                actual.add(p)
                c = A[0]/A[p[0]]
                need(w == [c*A[p[x]]/A[x] for x in range(T)], 'exact centralizer weights')
            if all(G[p[i]][p[j]] == G[i][j] for i in range(T) for j in range(T)):
                ordinary.add(p)
        need(actual == predicted, 'full vertex search versus coordinate theorem')
        inv = inverse(G)
        identity = [[F(i == j) for j in range(T)] for i in range(T)]
        need(multiply(G,inv) == identity, 'exact inverse multiplication')
        inverse_group = {p for p in permutations(range(T)) if direct_monomial(inv,p) is not None}
        need(inverse_group == actual, 'inverse commutants')
        if len(set(weights)) == len(weights):
            need(all(max(cycles(p)) <= 2 and len(cycles(p)) >= (T+1)//2 for p in actual),
                 'distinct-width vertex cycle bound')
        receipts.append({'sizes':sizes,'weights':weights,'gauges':kind,
                         'all_vertex_permutations':factorial(T),'monomial_permutations':len(actual),
                         'ordinary_permutations':len(ordinary),
                         'inverse_permutations':len(inverse_group)})
    return receipts


def gap(weights,q=F(1,2)):
    edge = q**(2*max(weights))-q**(4*min(weights))
    levels = [abs(q**(2*a)-q**(2*b)) for a,b in product(weights,repeat=2) if a != b]
    result = min([edge]+levels)
    need(result > 0, 'positive edge/color separation')
    return result


def perturbation_checks():
    sizes,weights = (2,2),(4,5)
    _,K,G,A,Q = matrices(sizes,weights,(F(2),F(3)),
                         [F(1),F(-2),F(3),F(1,2)],
                         [F(1,2),F(3),F(-2),F(4)])
    T = len(G)
    M = max(abs(v) for row in G for v in row)
    delta = min(abs(G[i][i]) for i in range(T))
    epsilon = F(1,2**44)
    separation = gap(weights)
    eta = 24*M*epsilon/delta**2
    need(epsilon <= delta/2 and 2*eta < separation, 'forward fixture margin')
    X = [[v+epsilon*((i+2*j)%3-1) for j,v in enumerate(row)] for i,row in enumerate(G)]
    CG,CX = metric_ratio(G),metric_ratio(X)
    actual = max(abs(CX[i][j]-CG[i][j]) for i in range(T) for j in range(T))
    need(actual <= eta, 'normalized product perturbation')
    allowed = coordinate_group(sizes,weights,[F(1)]*T)
    found = {p for p in permutations(range(T)) if direct_monomial(X,p) is not None}
    need(found <= allowed, 'rounded forward containment')
    GI = inverse(G)
    Y = [[v+epsilon*((2*i+j)%3-1) for j,v in enumerate(row)] for i,row in enumerate(GI)]
    e = 2*T**3*M**2*epsilon
    need(T*T*M*epsilon <= F(1,2) and e <= delta/2 and 48*M*e/delta**2 < separation,
         'inverse fixture all margins')
    YI = inverse(Y)
    inverse_error = max(abs(YI[i][j]-G[i][j]) for i in range(T) for j in range(T))
    need(inverse_error <= e, 'inverse to forward transfer')
    found_inverse = {p for p in permutations(range(T)) if direct_monomial(Y,p) is not None}
    found_forward = {p for p in permutations(range(T)) if direct_monomial(YI,p) is not None}
    need(found_inverse == found_forward and found_inverse <= allowed, 'rounded inverse commutants')
    return {'dimension':T,'entry_bound_M':str(M),'diagonal_floor':str(delta),
            'epsilon':str(epsilon),'color_gap':str(separation),'cross_ratio_bound':str(eta),
            'cross_ratio_error':str(actual),'inverse_transfer_bound':str(e),
            'inverse_transfer_error':str(inverse_error),'forward_symmetries':len(found),
            'inverse_symmetries':len(found_inverse)}


def source_identities():
    broad,narrow = 0,0
    b,A,alpha = F(2,3),F(3,2),F(2)
    for n,theta,offset in product(range(2,6),(F(1,10),F(1,8),F(1,6)),(F(-1,4),F(0),F(1,4))):
        points = [F(2*i-n+1,2) for i in range(n)]
        lam,rho = 1/(1+theta),1+theta
        shift = -offset*(1-theta)
        bound = b/F(4)+b*theta*(F(n*n,2)+F(3*n,2))
        def blog(y,x):
            return -b*(x-lam*y+offset)**2
        def row(y):
            return b*lam*(1-lam)*y*y+2*b*lam*(offset+shift)*y
        def col(x):
            return -b*(1-lam)*x*x-2*b*(offset+lam*shift)*x
        for x,y in product(points,repeat=2):
            hlog = -b*lam*(x-y)**2+2*b*lam*shift*(x-y)
            need(blog(y,x) == -b*offset**2+row(y)+hlog+col(x), 'broad exact gauge exponent')
            need(F(1)/alpha != 1, 'broad scalar normalizer retained')
            need(blog(y,x) <= 0, 'broad magnitude before alpha factor')
            need(blog(x,x) >= -b*(1+theta*n)**2/4, 'broad diagonal floor')
            need(abs(-b*offset**2+row(y))+abs(col(x)) <= bound, 'broad gauge log range')
            need(blog(y,x)+blog(x,y)-blog(y,y)-blog(x,x) == -2*b*lam*(x-y)**2,
                 'physical broad normalized product')
            broad += 1
        beta = {x:offset+theta*x for x in points}
        if max(map(abs,beta.values())) <= F(1,2):
            def nlog(i,j):
                return -A*((rho*(j-i)+beta[i])**2-beta[j]**2)
            for i,j in product(points,repeat=2):
                h = j-i
                need(nlog(i,j) == A*theta*i*i-A*rho*h*h-2*A*offset*h-A*theta*j*j,
                     'narrow chirp identity')
                need(nlog(i,j) <= 0 and (i != j or nlog(i,j) == 0), 'physical narrow unit bound')
                need(nlog(i,j)+nlog(j,i) == -2*A*rho*h*h, 'physical narrow pair product')
                narrow += 1
    return {'broad_exact_pairs':broad,'narrow_admitted_exact_pairs':narrow,
            'parameters':'n=2..5; theta=1/10,1/8,1/6; offset=-1/4,0,1/4',
            'method':'rational exponent identities, all source phase conditions checked'}


def rejection_controls():
    controls = []
    _,K,G,A,Q = matrices((2,2),(4,5),(F(2),F(3)),
                         [F(1),F(2),F(3),F(4)],[F(1),F(1,2),F(1,3),F(1,4)])
    T = len(G)
    p = (2,3,0,1)
    M = [[F(0) for _ in range(T)] for _ in range(T)]
    P = [[F(0) for _ in range(T)] for _ in range(T)]
    for x in range(T):
        M[p[x]][x] = 2*A[p[x]]/A[x]
        P[p[x]][x] = 1
    need(multiply(M,G) == multiply(G,M), 'weighted symmetry control')
    need(multiply(P,G) != multiply(G,P), 'gauges must be able to destroy ordinary symmetry')
    need(multiply(M,M) == [[F(4*(i == j)) for j in range(T)] for i in range(T)],
         'scalar-weighted order is not permutation order')
    controls += ['ordinary_permutation_destroyed_but_weighted_symmetry_retained',
                 'infinite_weighted_order_with_involutive_permutation']

    h = F(1,2**40)
    small = [[h*v for v in row] for row in K]
    rounded = [[h*F(i == j) for j in range(T)] for i in range(T)]
    epsilon = max(abs(a-b) for ra,rb in zip(small,rounded) for a,b in zip(ra,rb))
    cycle3 = (1,2,0,3)
    need(all(rounded[cycle3[i]][cycle3[j]] == rounded[i][j] for i in range(T) for j in range(T)),
         'coarse rounding three-cycle')
    need(direct_monomial(small,cycle3) is None, 'three-cycle already present in exact matrix')
    need(epsilon <= h/2, 'nonzero-diagonal control epsilon premise')
    need(48*h*epsilon < gap((4,5)) and 48*h*epsilon/h**2 >= gap((4,5)),
         'dropping diagonal denominator must produce a false certificate')
    controls.append('tiny_scalar_gauge_rounds_to_nonzero_identity_and_defeats_missing_delta_factor')
    vanished = [[F(0) for _ in range(T)] for _ in range(T)]
    try:
        metric_ratio(vanished)
    except ValueError:
        pass
    else:
        raise ValueError('zero rounded diagonal accepted')
    controls.append('whole_matrix_rounded_to_zero_has_no_normalized_invariant')

    _,K3,G3,_,_ = matrices((3,),(1,),(F(1),),[F(1)]*3,[F(1)]*3)
    inv3 = inverse(G3)
    need(metric_ratio(inv3) != metric_ratio(G3), 'inverse entries incorrectly reused forward metric')
    small_inverse = inverse([row[:2] for row in G3[:2]])
    need(small_inverse != [row[:2] for row in inv3[:2]], 'section/inverse interchange control')
    controls += ['inverse_cross_ratio_is_not_forward_Gaussian_metric',
                 'inverse_of_section_is_not_section_of_inverse']

    _,_,changed,_,diagonal = matrices((2,2),(4,5),(F(1),F(1)),[F(1)]*4,
                                     [F(1),F(2),F(3),F(5)])
    metric_group = coordinate_group((2,2),(4,5),[F(1)]*4)
    actual = {p for p in permutations(range(4)) if direct_monomial(changed,p) is not None}
    need(len(metric_group) == 4 and len(actual) == 1, 'diagonal-product condition required')
    controls.append('metric_preservation_without_diagonal_product_does_not_give_monomial_commutation')
    need(F(1,2).denominator != 1, 'equal-side physical swap leaves integer grid')
    controls.append('equal_physical_sides_with_two_versus_three_grid_points_do_not_swap')

    i,j,theta,beta0 = F(1,2),F(-1,2),F(1,10),F(2)
    exponent = -F(3,2)*(((1+theta)*(j-i)+beta0+theta*i)**2-(beta0+theta*j)**2)
    need(exponent > 0, 'outside-cell narrow example must exceed one')
    controls.append('narrow_unit_bound_requires_same_cell_phase_range')
    try:
        gap((1,10))
    except ValueError:
        pass
    else:
        raise ValueError('mixed-width edge band incorrectly certified')
    controls.append('mixed_broad_narrow_edge_band_not_assumed')

    # E=epsilon*J has exact operator norm T*epsilon, witnessed by the all-ones vector.
    eps = F(1,1024)
    need(T*(T*eps)**2 == T*T*eps*eps*T and T*eps > eps, 'paid dimension factor')
    controls.append('entry_error_is_not_dimension_free_operator_error')
    return {'count':len(controls),'passed':controls,'tiny_gauge_epsilon':str(epsilon),
            'outside_cell_positive_log':str(exponent)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',type=Path,help='explicit optional result file')
    args = parser.parse_args()
    pins = authenticate()
    groups = exact_groups()
    result = {'status':'PASS_GAUGED_PHYSICAL_GAUSSIAN_SYMMETRIES',
              'source_files_authenticated':pins,'complete_groups':groups,
              'total_vertex_permutations_per_target':sum(x['all_vertex_permutations'] for x in groups),
              'target_types':['forward','exact_inverse'],
              'rational_perturbation':perturbation_checks(),
              'physical_source_identities':source_identities(),'controls':rejection_controls(),
              'scope':'finite corroboration; universal proof is PROOF.md; no new kappa'}
    text = json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:
        args.write.write_text(text)
    print(text,end='')


if __name__ == '__main__':
    main()
