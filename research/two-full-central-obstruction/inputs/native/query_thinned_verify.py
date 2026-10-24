#!/usr/bin/env python3
"""Exact finite replay for the conditional query-thinned construction.

Apache-2.0. Prepared for Cinna Davis with substantial OpenAI Codex assistance.
Retains zxv's native/factor/tail work and Jacob Alan Sussman's integer flow.
"""
from fractions import Fraction as Q
from hashlib import sha1, sha256
import argparse
import json
import sys
sys.dont_write_bytecode = True
import controller as C
HERE, ROOT, need = C.HERE, C.ROOT, C.need


def encode(x):
    if isinstance(x, Q): return str(x)
    if isinstance(x, dict): return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [encode(v) for v in x]
    return x


def authenticate():
    count = 0
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input': continue
        path = ROOT/row['path']; raw = path.read_bytes()
        need(not path.is_symlink(), 'No source alias')
        need(sha256(raw).hexdigest() == row['sha256'], 'Changed source: '+row['path'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'Changed Git blob')
        count += 1
    return count


def controllers():
    B, E = C.engines(); result = {}
    for kind, p, a in [('complex', 17, 8), ('bit', 16, 7)]:
        row = json.loads((HERE/(kind.upper()+'-CONTROLLER.json')).read_text())
        thick, mask = C.thick_stages(p), C.keep_mask(p, a)
        if kind == 'complex':
            coefficients, events, idles = E.controller(p, mask)
            coefficients = C.specialize_complex(coefficients, thick)
            left = [[Q(x) for x in r] for r in row['boundaries']['left']]
            right = [[Q(x) for x in r] for r in row['boundaries']['right']]
            diagonal = [tuple(term) for term in row['diagonal']]
            transformed = {k: B.matrix_multiply(B.matrix_multiply(left, m), right) for k, m in coefficients.items()}
            expected = {k: [[Q(i == j and diagonal[i] == k) for j in range(2*p)] for i in range(2*p)] for k in set(diagonal)}
            need(transformed == expected, 'All exact rational Laurent coefficients, including signs and Q powers')
            for name, matrix in [('left', left), ('right', right)]:
                need(E.scalar_program(matrix) == row['boundaries'][name+'_program'], 'Literal unit scalar boundary program')
            changed = dict(coefficients)
            k = next(iter(changed)); changed[k] = [r[:] for r in changed[k]]; changed[k][0][0] += 1
            need(B.matrix_multiply(B.matrix_multiply(left, changed[k]), right) != expected.get(k), 'A changed physical coefficient is rejected')
        else:
            coefficients, events, idles = B.physical_controller(p, mask)
            coefficients = C.specialize_bit(coefficients, thick)
            fresh = B.simultaneous_monomial_factor(coefficients)
            need(fresh == row['boundaries'], 'Exact binary physical operator and scalar boundaries')
            diagonal = fresh['diagonal_monomials']
        need(C.replay_events(row['physical_events'], p, kind) == coefficients,
             'Emitted native/query/idle word equals the specialized physical source')
        mutant = json.loads(json.dumps(row['physical_events']))
        # Every removed stage is forward; changing its direction must change
        # the actual operator rather than merely a tariff field.
        next(ev for ev in mutant if ev[0] == 'QUERY_SHEAR')[3] = True
        need(C.replay_events(mutant, p, kind) != coefficients, 'Wrong query orientation rejected')
        invoice = C.inventories(kind, p, a, diagonal, idles)
        ports = 112 if kind == 'complex' else 111
        boundary_records = (sum(len(row['boundaries'][name+'_program']) for name in ('left', 'right'))
                            if kind == 'complex' else row['boundaries']['boundary_unit_ADDs_per_port'])
        scalar_upper = (p+2)*10**6+16*invoice['thin_queries']+32*ports*(len(row['physical_events'])+boundary_records)
        need(scalar_upper < invoice['raw_scalar_record_bound'], 'Conservative complete scalar/route count fits')
        need(encode(invoice) == row['invoice'], 'Literal and closed-form complete '+kind+' invoice')
        result[kind] = invoice
    return result


def native_contacts():
    n = C.load(ROOT/'research/pr4359-p7-padding/native_inventory.py', 'thinned_native_phases')
    phases = json.loads((ROOT/'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json').read_text())
    axes = tuple(1 << i for i in range(17)); old = [(a, 1) for a in axes[:9]]; fresh = [(a, 1) for a in axes[9:]]
    checks = 0
    for recipe in phases['recipes']:
        q = recipe['q']; basis = recipe['idle_children'][0]['orthogonal_axes'][:8]
        need(all((b&q).bit_count() % 2 == 0 for b in basis), 'Old eight-space perpendicular to q')
        swaps = [b ^ axes[9+i] for i, b in enumerate(basis)]
        route = tuple(e ^ n.act(swaps, sum(((e&v).bit_count() % 2) << i for i, v in enumerate(swaps))) for e in axes)
        need(all(n.act(route, route[i]) == axes[i] for i in range(17)), 'Exact physical route inverse')
        need(all((a&b).bit_count() % 2 == int(i == j) for i, a in enumerate(route) for j, b in enumerate(route)), 'Orthogonal physical route')
        need(n.act(route, q) == q, 'Central query direction fixed')
        need(n.polynomial(n.norm([(q, -1)]), 17) == n.polynomial(n.norm([(q, 1), (q, 2)]), 17),
             'Inverse thin Gaussian is one positive query and a physical translation')
        for sign in (-1, 1):
            raw = (n.norm(old), n.norm(old+[(q, -1)]))
            entry = (n.norm(fresh+[(q, sign)]), n.norm(fresh))
            out0 = n.norm(fresh+[(a, sign) for a in axes[:9]])
            local_out = (out0, n.norm(list(out0)+[(q, -sign)]))
            out = (n.norm(old+fresh), n.norm(old+fresh+[(q, -1)]))
            for x, y in list(zip(raw, entry))+list(zip(local_out, out)):
                n.contact(x, y, route, 17); checks += 1
            for x, y in zip(raw, out):
                need(n.polynomial(n.norm(list(y)+[(a, -c) for a, c in x]), 17) == n.polynomial(n.norm(fresh), 17), 'Exactly the fresh eight-axis multiplier')
    bit = C.load(ROOT/'research/kappa-rebuild/bit/bit_native_binding.py', 'thinned_binary_charts')
    ports = json.loads((ROOT/'research/kappa-rebuild/bit/BIT-P3-NATIVE-BINDING.json').read_text())['ports']
    local = json.loads((ROOT/'research/kappa-rebuild/bit/MIXED-PRODUCTIVE-BIT.json').read_text())['local']
    for direction in local['signed_directions']:
        need({int(k): v for k, v in direction['profile'].items()} == C.engines()[0].LOCAL,
             'Every actual binary local child remains charged')
        need(direction['unit_ADDs'] < 10**6 and direction['owned_COPY_episodes'] == 9,
             'Native binary scalar and owned-center bills retained')
    for row in ports:
        p = [[Q(x) for x in r] for r in row['central_projector']]; rho = [[Q(x) for x in r] for r in row['chart_15']]
        active = [[p[i][j] if i < 8 and j < 8 else Q(i == j and i >= 8) for j in range(15)] for i in range(15)]
        full = [[Q(i == j and i < 8) for j in range(15)] for i in range(15)]
        need(bit.multiply(rho, rho) == bit.ident(15) and bit.multiply(bit.multiply(rho, active), rho) == full, 'BIT exact arbitrary-column chart')
        need(bit.multiply(p, p) == p and sum(p[i][i] for i in range(8)) == 1, 'BIT query rank one')
    # Formal independent X,Y,Z columns. Mutants execute the same word with
    # an actual omitted operation; they are not merely different receipts.
    for e in (-1, 1):
        def execute(clear=True, erase=True):
            x, y, z = {('X', 0): 1}, {('Y', 0): 1}, {('Z', 0): 1}
            if clear: z = {}
            for key, value in x.items(): z[key] = z.get(key, 0)+value
            z = {(name, power+e): value for (name, power), value in z.items()}
            for key, value in z.items(): y[key] = y.get(key, 0)+(-1 if e == 1 else 1)*value
            if erase: z = {}
            return x, y, z
        expected = ({('X', 0): 1}, {('Y', 0): 1, ('X', e): -1 if e == 1 else 1}, {})
        need(execute() == expected, 'Completed arbitrary-input owned-query shear')
        need(execute(clear=False) != expected and execute(erase=False) != expected, 'Clear/erase omission controls rejected')
    return {'complex_contacts_and_inverses': checks, 'binary_charts': len(ports),
            'thin_paid_rank_per_port': 1, 'thin_productive_credit': 0, 'owned_stream_restored_zero': True}


def tail(E, invoice, tested, uniform, cutoff, floor, alpha_gap):
    T, P = invoice['targets'], invoice['paid']; t, u, v = 1-tested, Q(1, 5), 1024
    target, paid = E.moment(T, t), E.moment(P, t)
    alpha = E.divide(paid, target)
    other = C.load(ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py', 'separate_rational_moment_engine')
    tl, th = other.moment(T, tested); pl, ph = other.moment(P, tested)
    need(tl > ph and max(target[0], tl) <= min(target[1], th)
         and max(paid[0], pl) <= min(paid[1], ph), 'Separate rational interval engine agrees')
    gamma = E.divide(E.moment(P, t+u), E.mul(E.power(cutoff, u), target))
    delta = E.divide((Q(sum(T.values())*floor),)*2, E.mul(E.power(cutoff, tested), target))
    need(alpha[1] < 1-alpha_gap and gamma[1] < Q(31, 32) and delta[1] < Q(19, 20), 'Three completely charged tail ratios')
    need(Q(31, 32)**128 < Q(1, 16) and Q(19, 20)**128 < Q(1, 16), 'Exact decay blocks')
    surplus = 1-Q(1)/(1+v*alpha_gap)-Q(4, 2**32)
    need(surplus > 0, 'Original and completion tails both fit')
    need(cutoff**64 < floor**63 and max(T) < 256, 'Strict ranks after completion and splitting')
    h = Q(1, 64); z, z0 = 1-uniform, (t+1-uniform)/2; gap = z0-t
    B, debt = (5+8*h)*v, 1+8*v*(1-z0)
    x = (gap*B+debt)/(h*gap); H0 = -((-x.numerator)//x.denominator)
    x = H0*(1-z0)/(z-z0); H1 = x.numerator//x.denominator+1
    need(H0 >= 8*v and H0*h*gap >= gap*B+debt and H1*(z-z0) > H0*(1-z0), 'Effective integer compiler bound')
    return {'tested_saving': tested, 'uniform_saving': uniform, 'alpha': E.display(alpha),
            'gamma': E.display(gamma), 'delta': E.display(delta), 'tensor_power': v,
            'cutoff_base': cutoff, 'target_floor_base': floor, 'tail_exponent': u,
            'normalized_surplus_lower': surplus, 'compiler_H0': H0, 'uniform_H1': H1,
            'uniform_N': '2^'+str(H1), 'winning_word_materialized': False}


def run():
    count = authenticate(); rows = controllers(); native = native_contacts()
    E = C.load(ROOT/'research/higher-moment-strictification/verify.py', 'credited_exact_intervals')
    kappa, tested = Q('.00296'), Q('.00296030'); d = (tested-kappa)/7
    complex_ = tail(E, rows['complex'], tested, kappa+6*d, 20, 21, Q(1, 30000000))
    bit = tail(E, rows['bit'], Q('.00346'), Q('.003459'), 17, 18, Q(1, 250000))
    before, after, atom, old = Q('.003459'), Q('.00345'), Q('.004'), Q('.0000384599')
    ordinary, admitted = (1-atom)*after+atom*old, Q('.0034')
    need(before > after and atom > ordinary > admitted and atom < 1-ordinary, 'Complete ordinary BIT conversion')
    need(Q('.003') < ordinary and 2**26 > 256/(before-after), 'Old atom rejected and finite prime bound')
    L = C.load(ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py', 'complete_outer_ledger')
    params = {'kappa': kappa, 'tested_saving': tested, 'complex_uniform_saving': kappa+6*d,
              'b': kappa+5*d, 'a': kappa+4*d, 'q': kappa+3*d, 'bit_saving': admitted,
              'epsilon': 1-d, 'beta': 1-3*d, 'r0': d/10, 'stop': d, 'layout': d, 'd': d}
    outer = L.ledger(params)
    outer['functional_checks']['actual_new_BIT_stock_sublinear'] = params['beta']*(1-atom)
    need(len(outer['strict_checks']) == 54 and len(outer['functional_checks']) == 4, 'Complete predicate inventory')
    need(all(x > 0 for group in ('strict_checks', 'functional_checks') for x in outer[group].values()), 'All outer predicates')
    controls = {}
    for label, changes in [('old_BIT_cap', {'bit_saving': Q('.0027')}), ('closed_uniform_gap', {'complex_uniform_saving': params['b']}),
                            ('unfunded_kappa', {'kappa': tested}), ('closed_epsilon', {'epsilon': Q(1)}), ('missing_layout', {'layout': Q(0)})]:
        bad = L.ledger(dict(params, **changes)); failed = [k for k, v in bad['strict_checks'].items() if v <= 0]
        need(failed, 'Reject '+label); controls[label] = failed
    return encode({'schema': 'query-thinned-productive-controllers/1', 'status': 'PASS_CONDITIONAL_QUERY_THINNED_KAPPA_00296',
                   'kappa': kappa, 'relative_gain_over_p7': kappa/Q('.00268647')-1,
                   'source_inputs_authenticated': count, 'native': native, 'complex_invoice': rows['complex'], 'bit_invoice': rows['bit'],
                   'complex_strictification': complex_, 'bit_strictification': bit,
                   'ordinary_BIT': {'before_cover': before, 'after_cover': after, 'atom': atom, 'ordinary_saving': ordinary,
                                    'admitted': admitted, 'prime_rule': 'odd q > 2^26*N^5 avoiding all fixed denominators and rank witnesses'},
                   'outer': outer, 'minimum_outer_margin_minus_kappa': min(outer['margins'].values())-kappa,
                   'negative_controls': controls, 'old_atom_rejected': True,
                   'scope': 'Conditional native construction; all-column, erasure, whole-job matching, fixed-tape, precision, analytic, prime and exact-recovery premises retained. No unconditional theorem or selected promotion.'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--write', action='store_true'); args = parser.parse_args()
    result = run(); output = HERE/'RESULT.json'
    if args.write: output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else: need(result == json.loads(output.read_text()), 'Complete receipt matches exact replay')
    print(json.dumps({k: result[k] for k in ('status', 'kappa', 'source_inputs_authenticated', 'minimum_outer_margin_minus_kappa')}, sort_keys=True))
