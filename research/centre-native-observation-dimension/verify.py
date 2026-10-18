"""Whole-payload owner-local repair dimension, with exact native factors."""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
import argparse, json, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import HERE, load, need
from audit import audit

def encoded(x):
    return json.dumps(x, indent=2, sort_keys=True) + '\n'

def run():
    data, C, prior, native_prior = load()
    # Re-run the unchanged source/route premises; no new scalar theorem claimed.
    prior.load = lambda: data
    scalar = prior.build()
    word, programs = data['word'], data['programs']
    audits = {k: audit(word, v, k) for k, v in programs.items()}
    R = [{p: q for p, q in row.items() if p < 112} for row in audits['forward']['cuts']]
    H = [{p-112: q for p, q in row.items()} for row in audits['backward']['cuts']]
    need(all(all(112 <= p < 224 for p in row) for row in audits['backward']['cuts']),
         'backward query contains only target inputs')
    need(H == [{p: q/4 for p, q in row.items()} for row in R], 'pure target quarter matrix')
    need([[str(row.get(p, 0)) for p in range(112)] for row in R] == scalar['R'], 'old scalar source agreement')
    merged = {'edges': set().union(*(x['edges'] for x in audits.values())),
              'wrapped': set().union(*(x['wrapped'] for x in audits.values()))}
    native_receipt, _, adapters = native_prior.check_operators(word, data['recipes'], data['residuals'], merged, C)
    # Explicit old-source and completed first D->T blocks, all 112 ports.
    factors = []
    for p, q in enumerate(word['ports']):
        source_label = C.canonical_frame(word['frames'][word['start'][p]]) + C.adjoint(C.monomial(adapters['source', p]['left']))
        target_label = C.canonical_frame(word['frames'][word['final'][112+p]]) + C.adjoint(C.monomial(adapters['target', p]['left']))
        need(C.same_operator(source_label, [('C', q, 1)]), 'old source normalization')
        need(C.same_operator(target_label, [('C', q, -1)] + C.fourier(9)), 'first target final label')
        first_to_target = C.adjoint(source_label) + target_label
        expected = [('C', q, -1), ('C', q, -1)] + C.fourier(9)
        need(C.same_operator(first_to_target, expected), 'completed native source-to-target block')
        need(C.same_operator(first_to_target + C.adjoint(first_to_target), []) and
             C.same_operator(C.adjoint(first_to_target) + first_to_target, []), 'both native block inverses')
        factors.append({'port': p, 'normal': q, 'old_normalization': ['C_q^-1'],
                        'first_source_to_target': ['C_q^-1', 'C_q^-1', 'F9'],
                        'circuit_order': 'listed in execution order'})
    routes = [prior.route(r) for r in data['phases']['recipes']]
    need(len(set(routes)) == 112, 'distinct old-owner destinations')
    pivots = sorted(prior.echelon(R))
    complementary = [p for p in range(112) if p not in pivots]
    minor = [[row.get(p, Q(0)) for p in pivots] for row in R]
    inverse, determinant = native_prior.inverse_and_det(minor)
    need(len(complementary) == 104, '104 whole-array recovery')

    # Independent finite block-operator instance: port-dependent invertible
    # maps act on two payload coordinates, so this is not a constant-only test.
    maps = [((1,0),(0,1)), ((0,-1),(1,0)), ((-1,0),(0,-1)), ((0,1),(-1,0))]
    old, later, extra = [], [], []
    for k, row in enumerate(R):
        for a in range(2):
            out = {}
            for p, q in row.items():
                for b in range(2):
                    if maps[p % 4][a][b]:
                        out[2*p+b] = q*maps[p % 4][a][b]
            old.append(out)
    for p in range(112):
        for k in range(8):
            q = H[k].get(p, Q(0))
            for a in range(2):
                later.append({2*p+b: q*maps[(p+1) % 4][a][b]
                              for b in range(2) if q*maps[(p+1) % 4][a][b]})
    for p in complementary:
        for a in range(2):
            extra.append({2*p+b: Q(maps[p % 4][a][b]) for b in range(2) if maps[p % 4][a][b]})
    ranks = {'old': len(prior.echelon(old)), 'later': len(prior.echelon(later)),
             'completed': len(prior.echelon(old+extra)), 'missing_one_coordinate': len(prior.echelon(old+extra[:-1]))}
    need(ranks == dict(old=16, later=224, completed=224, missing_one_coordinate=223), 'full block-operator dimension witness')
    controls = {}
    def rejects(name, action, reason):
        try:
            action()
        except ValueError as error:
            need(reason in str(error), 'wrong rejection ' + name + ': ' + str(error))
            controls[name] = reason
        else:
            raise ValueError('ineffective control ' + name)
    changed = deepcopy(programs['backward'])
    e = next(e for e in changed if e[0] == 'scalar' and e[1][0] == 'add' and e[2] != 0)
    e[2] = 0
    rejects('wrong_backward_frame', lambda: audit(word, changed, 'backward'), 'common frame')
    changed = deepcopy(programs['backward'])
    e = next(e for e in changed if e[0] == 'center')
    e[2], e[3] = e[3], e[2]
    rejects('wrong_backward_direction', lambda: audit(word, changed, 'backward'), 'centre source frame')
    changed = deepcopy(programs['forward'])
    j = next(i for i, e in enumerate(changed) if e[0] == 'climb')
    del changed[j]
    rejects('missing_forward_transport', lambda: audit(word, changed, 'forward'), 'frame')
    need(ranks['missing_one_coordinate'] < 224, 'one missing repair coordinate control')
    controls['missing_one_repair_coordinate'] = 'rank223 below224'
    # Use the kernel's supported phase-bearing monomial rather than an unknown
    # primitive; the changed native map is unitary but no longer the pinned map.
    rec = deepcopy(adapters['source', 0]['left'])
    rec['phase'] = (rec['phase']+1) % 4
    need(not C.same_operator([('C', word['ports'][0], 1)] + C.monomial(rec),
                            C.canonical_frame(word['frames'][word['start'][0]])), 'native global phase control')
    controls['wrong_native_global_phase'] = 'all-column identity differs'
    # Rank-one averaging fixes constants and kills the nonconstant direction.
    projection = [[Q(1,2), Q(1,2)], [Q(1,2), Q(1,2)]]
    need([sum(row) for row in projection] == [1,1] and
         [row[0]-row[1] for row in projection] == [0,0], 'constant-preserving singular control')
    rejects('constant_only_endpoint_acceptance', lambda: native_prior.inverse_and_det(projection), 'singular minor')
    controls['distinct_owner_collapse'] = 'same routes and same port factors give y=z/4, zero extra information'
    need(len(prior.echelon(R + H)) == 8, 'collapsed owner positive control')
    native_d = 512
    return {'status': 'PASS_NATIVE_OWNER_OBSERVATION_DIMENSION',
            'calls': [0,4], 'source_child_dimension': native_d,
            'audits': {k: {name: v[name] for name in ('events','bill','scalar_columns','conversions')} for k,v in audits.items()},
            'native_operator_checks': native_receipt, 'native_port_factors': factors,
            'backward_D_coefficients': 0, 'backward_helper_coefficients': 0, 'backward_T_matrix': 'R/4',
            'route_sha256': scalar['route_sha256'], 'distinct_owner_routes': 112,
            'old_rank_per_payload_dimension': 8, 'later_rank_per_payload_dimension': 112,
            'additional_dimension_floor_per_payload_dimension': 104,
            'local_native_dimension_example': {'old':8*native_d,'later':112*native_d,'additional':104*native_d},
            'pivot_ports': pivots, 'pivot_determinant': str(determinant),
            'pivot_inverse': [[str(q) for q in row] for row in inverse], 'complementary_ports': complementary,
            'independent_two_coordinate_block_ranks': ranks, 'controls': controls,
            'scope': 'Conditional native whole-payload owner-local linear observation theorem for equal finite payload spaces and invertible admitted views. Sharp104*d information dimension; not104 recursive children, paid ranks, physical reads or a supplied global compiler.'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    if args.write and args.write.exists():
        raise FileExistsError(args.write)
    saved = None if args.write else json.loads((HERE/'RESULT.json').read_bytes())
    result = run()
    if args.write:
        with args.write.open('x',encoding='utf-8',newline='\n') as out:
            out.write(encoded(result))
    else:
        need(encoded(saved) == encoded(result), 'complete receipt mismatch')
    print('PASS_NATIVE_OWNER_OBSERVATION_DIMENSION old=8*d later=112*d additional=104*d controls=7')

if __name__ == '__main__':
    main()
