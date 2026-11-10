#!/usr/bin/env python3
"""Bounded exact verification of the bridge-carrier package, including controls.

Jerry Chen / @CubeJerry, with substantial OpenAI GPT-6 Astra Pro assistance.
Apache-2.0. Mathematical universality is established in PROOF.md; replay is finite.
"""
import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

from model import (CapacityModel, INTERVALS, add, basis, build, dot, eye, mm,
                   moment, need, outer, power_bounds, rank, source_complete,
                   source_outer, transpose, zero)

ROOT = Path(__file__).resolve().parent
KAPPA = Q('.00337180')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pins():
    obj = json.loads((ROOT/'retained/SOURCE-PINS.json').read_text())
    for row in obj['files']:
        payload = (ROOT/'retained'/row['path']).read_bytes()
        need(digest(payload) == row['sha256'], 'retained source SHA256')
        blob = hashlib.sha1(b'blob '+str(len(payload)).encode()+b'\0'+payload).hexdigest()
        need(blob == row['git_blob'], 'retained source Git blob')
        need(row['source_commit'] == '51f54e3c31f2f3a3e056a483b3ed66ae916ad06a', 'source head')
    tree = ast.parse((ROOT/'retained/chain_root.py').read_text())
    names = {'fields', 'vector', 'thin_vectors', 'sites', 'outer_formula'}
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    need({node.name for node in functions} == names, 'all retained formula dependencies selected')
    env = {'Q':Q, 'Counter':Counter}
    exec(compile(ast.Module(body=functions, type_ignores=[]), '<pinned-constructor-functions>', 'exec'), env)
    price_tree = ast.parse((ROOT/'retained/pricing.py').read_text())
    data = {}
    for node in price_tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {'HELPERS', 'LOCAL_PAID'}:
                    data[target.id] = ast.literal_eval(node.value)
    need(set(data) == {'HELPERS','LOCAL_PAID'}, 'complete fixed native profile')
    return env, data


def algebra(root):
    n, m = root['n'], root['m']
    I, Z = eye(n), zero(n)
    E, v, z, u, w = (root[key] for key in ('E','v','z','u','w'))
    PE, PV, J = outer(E,E), outer(v,z), outer(u,w)
    need(dot(z,v) == 1 and dot(w,u) == dot(z,u) == dot(w,v) == 0, 'bridge pairings')
    need(mm(PE,PV) == mm(PV,PE) == Z, 'orthogonal common-idle projectors')
    for P in (PE,PV):
        need(mm(P,P) == P and mm(P,J) == mm(J,P) == Z, 'projector/nilpotent splitting')
    need(mm(J,J) == Z and rank(J) == 1, 'nonzero square-zero residual')
    expected = add(add(add(I,PE,-2),PV,-2),J,-2)
    need(root['B'] == expected, 'literal three-query bridge decomposition')
    need(mm(root['B'],root['B']) == add(I,J,-4), 'bridge square')
    need(mm(mm(add(root['B'],I,-1),add(root['B'],I,-1)),add(root['B'],I)) == Z,
         'degree-three closure polynomial')
    need(n-rank(add(root['B'],I)) == 2, 'bridge minus-one eigenspace dimension')
    need(mm(root['B'],transpose([E,v])) == transpose([[-x for x in E],[-x for x in v]]), 'minus-one columns')
    need(mm([E,z],root['B']) == [[-x for x in E],[-x for x in z]], 'minus-one rows')
    xs = [s[0] for s in root['full']]
    ys = [s[1] for s in root['full']]
    need(rank(xs) == rank(ys) == m and rank([[dot(y,x) for x in xs] for y in ys]) == m,
         'native primal, dual and even sign-Gram ranks')
    for x,y,_ in root['full']:
        need(dot(y,E) == dot(y,v) == dot(E,x) == dot(z,x) == 0, 'native common-idle plane')
    R = add(add(I,PE,-1),PV,-1)
    need(mm(R,R) == R and rank(R) == m, 'native invariant complement')
    need(mm(root['B'],R) == mm(add(I,J,-2),R), 'bridge becomes one query on quotient')
    K = I
    for x,y,_ in root['sites']:
        need(dot(y,x) == 0, 'each source query square-zero')
        K = mm(add(I,outer(x,y),-2),K)
    need(K == add(Z,I,-1), 'complete source root endpoint')
    short = root['left']+[(u,w,None)]+root['right']
    K = I
    for x,y,_ in short:
        K = mm(add(I,outer(x,y),-2),K)
    need(K == add(I,R,-2), 'quotient word is minus identity on W and identity on idle plane')
    return R


def quotient(root, R):
    n = root['n']; Qs = []
    idempotence_defects, quotient_defects = [], []
    for x,y,mask in root['full']:
        P = [[int(i == j and i in mask) for j in range(n)] for i in range(n)]
        comp = mm(mm(R,P),R); Qs.append(comp)
        N = outer(x,y)
        need(mm(comp,N) == mm(N,comp) == N, 'compressed query containment survives')
        idempotence_defects.append(rank(add(mm(comp,comp),comp,-1)))
        quotient_defects.append(rank(add(mm(P,R),mm(R,P),-1)))
    need(idempotence_defects == [1]*18, 'all compressed stages fail idempotence')
    need(quotient_defects == [2]*18, 'all source stages fail to preserve the splitting')
    commutators = Counter(rank(add(mm(a,b),mm(b,a),-1)) for j,a in enumerate(Qs) for b in Qs[j+1:])
    need(commutators == Counter({2:153}), 'all compressed stage pairs fail to commute')
    return {'stage_idempotence_defect_rank':1, 'stages':18, 'pair_commutator_rank':2, 'pairs':153}


def expect_failure(callback, label):
    try:
        callback()
    except (ValueError, AssertionError):
        return label
    raise ValueError('negative control unexpectedly accepted: '+label)


def dual_check(row, scale, caps, demands, kappa):
    alpha, beta = row['alpha'], row['beta']
    need(len(alpha) == len(INTERVALS) and len(beta) == 18, 'dual dimensions')
    need(all(type(x) is int and x <= 0 for x in alpha) and all(type(x) is int for x in beta), 'dual sign and exact integers')
    for a,b in INTERVALS:
        column = sum(alpha[k] for k,(c,d) in enumerate(INTERVALS) if a <= c and d <= b)+sum(beta[a:b+1])
        lo,_ = power_bounds(8*(b-a+1),str(kappa))
        need(Q(column,scale) <= lo, 'dual column inequality')
    return Q(sum(x*y for x,y in zip(alpha,caps))+sum(x*y for x,y in zip(beta,demands)),scale)


def dense_cases(profile):
    cert = json.loads((ROOT/'dual-certificate.json').read_text())
    scale = cert['scale']; rows = cert['cases']
    need(scale == 10**8 and len(rows) == 81, 'full finite domain')
    need([(r['a'],r['b']) for r in rows] == [(a,b) for a in range(9) for b in range(9,18)], 'domain order, no duplicate or omitted mask')
    engine = CapacityModel()
    fixed_t, fixed_p = moment(profile['HELPERS'],KAPPA), moment(profile['LOCAL_PAID'],KAPPA)
    native_upper = 18*(fixed_t[1]-fixed_p[0])
    result = []
    for row in rows:
        caps, demands, targets = engine.case(row['a'],row['b'])
        lower_paid = dual_check(row,scale,caps,demands,KAPPA)
        target_upper = moment(targets,KAPPA)[1]
        complete_upper = native_upper+104*(target_upper-3-lower_paid)
        need(complete_upper < 0, 'dense-mask complete upper bound loses at the pending source benchmark')
        result.append({'a':row['a'],'b':row['b'],'complete_gain_upper':str(complete_upper)})
    best = max(result,key=lambda x:Q(x['complete_gain_upper']))
    row = rows[0]; caps, demands, _ = engine.case(row['a'],row['b'])
    wrong = deepcopy(row); wrong['alpha'][0] = 1
    sign_control = expect_failure(lambda:dual_check(wrong,scale,caps,demands,KAPPA), 'positive inequality multiplier rejected')
    wrong = deepcopy(row); wrong['beta'][0] += 1000*scale
    col_control = expect_failure(lambda:dual_check(wrong,scale,caps,demands,KAPPA), 'overstated dual price rejected')
    need(engine.capacity(8,9,set(range(19))) == 15, 'whole-block central capacity is 15')
    # Requiring annihilation of all three thin queries gives the older stricter class.
    x = [s[0] for s in engine.full[8:10]]+[s[0] for s in engine.root['thin']]+[[int(i==19) for i in range(20)]]
    y = [s[1] for s in engine.full[8:10]]+[s[1] for s in engine.root['thin']]+[[int(i==19) for i in range(20)]]
    xb,yb = basis(x),basis(y)
    old_cap = 20-len(xb)-len(yb)+rank([[dot(yr,xr) for xr in xb] for yr in yb])
    need(old_cap == 14, 'strictly larger new block-preserved capacity')
    return {'cases':81,'dual_column_inequalities':81*len(INTERVALS),'best':best,
            'old_central_capacity':14,'block_central_capacity':15}, [sign_control,col_control]


def controls(root):
    result = []
    I = eye(20)
    wrong = deepcopy(root)
    wrong['B'] = I
    for x,y,_ in reversed(root['thin']):
        wrong['B'] = mm(add(I,outer(x,y),-2),wrong['B'])
    result.append(expect_failure(lambda:algebra(wrong),'reversed bridge order rejected'))
    PE = outer(root['E'],root['E'])
    need(any(mm(PE,outer(x,y)) != zero(20) or mm(outer(x,y),PE) != zero(20) for x,y,_ in root['thin']),
         'whole-block positive fixture fails per-query annihilation')
    need(mm(PE,root['B']) == mm(root['B'],PE), 'whole-block positive fixture passes')
    result.append('whole-block carrier separates new and old contracts')
    e = [[1,0],[0,0]]; f = [[0,0],[0,1]]; swap = [[0,1],[1,0]]
    need(mm(swap,e) == mm(f,swap) and e != f, 'minus-leg-only relocation passes but neutral leg fails')
    result.append('minus-leg-only transport rejected by neutral specialization')
    shear = [[1,1],[0,1]]
    need(mm(shear,[[1],[0]]) == [[1],[0]] and mm(shear,e) != mm(e,shear), 'image-only carrier check misses dual change')
    result.append('image-only transport rejected by full projector test')
    x,y = [[1,0]], [[0,1]]
    cap = 2-rank(x)-rank(y)+rank([[dot(y[0],x[0])]])
    need(cap == 0, 'primal and dual nullities do not imply a paired line')
    result.append('unpaired nullspace dimension rejected')
    # Native-common for the two central full queries, but not bridge-invariant.
    phi = [0]*20; phi[1],phi[2] = 1,-1
    gamma = [Q(v,2) for v in phi]
    E = outer(phi,gamma)
    need(all(dot(y,phi) == dot(gamma,x) == 0 for x,y,_ in root['full'][8:10]), 'closure control has native annihilation')
    need(mm(root['B'],E) != mm(E,root['B']), 'omitting whole-block closure admits an illegal carrier')
    result.append('native-only annihilation rejected by bridge closure')
    return result


def run():
    source, profile = pins()
    shapes = []
    for a in (1,3,5,7,9):
        for b in (1,3,5,7,9):
            root = build(a,b)
            expected = [(x,y,m) for x,y,m,*_ in source['sites']([1]*a,[1]*b)]
            need(root['sites'] == expected,'independent formulas match exact retained source')
            need(source_outer(a,b) == source['outer_formula']([1]*a,[1]*b),'complete source outer invoice')
            algebra(root); shapes.append([a,b])
    root = build(); R = algebra(root)
    qdiag = quotient(root,R)
    source_margin = source_complete(KAPPA,profile['HELPERS'],profile['LOCAL_PAID'])
    need(source_margin[0] > 0, 'pending source is positive at its stated kappa')
    t,p = source_outer()
    source_gain = (moment(t,KAPPA)[0]-moment(p,KAPPA)[1],moment(t,KAPPA)[1]-moment(p,KAPPA)[0])
    f145,p144 = power_bounds(145,str(KAPPA)),power_bounds(144,str(KAPPA))
    ideal_upper = 19*f145[1]-17*p144[0]-2
    need(source_gain[0]-ideal_upper > 0, 'full-span ideal is strictly inferior')
    dense, dual_controls = dense_cases(profile)
    report = {'status':'PASS','claim':'No new kappa','source_head':'51f54e3c31f2f3a3e056a483b3ed66ae916ad06a',
              'kappa':str(KAPPA),'odd_odd_shapes':shapes,
              'source_complete_margin':[str(x) for x in source_margin],
              'full_span_per_port_loss_lower':str(source_gain[0]-ideal_upper),
              'quotient':qdiag,'dense_masks':dense,'controls':controls(root)+dual_controls}
    expected_path = ROOT/'EXPECTED.json'
    if expected_path.exists():
        need(json.loads(expected_path.read_text()) == report, 'deterministic exact expected report')
    print(json.dumps(report,indent=2))
    return report


if __name__ == '__main__':
    run()
