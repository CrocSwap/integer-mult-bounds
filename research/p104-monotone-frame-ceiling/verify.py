"""Check the rational frame-cost certificate and the all-size caller bound.

No solver or floating arithmetic is used to decide a proof condition.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import argparse
import gzip
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exact import UNIT, log_rank, power
from model import model
from frames import bounds, dimension, graph, invoice, span

HERE = Path(__file__).resolve().parent
HELPERS = {1:14, 2:8, 3:4, 4:107, 5:15, 6:3, 7:9, 8:39, 9:363}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def model_hash(variables, eq, ub, tariffs):
    payload = [variables, [[sorted(a.items()), b] for a, b in eq],
               [[sorted(a.items()), b] for a, b in ub], tariffs]
    return sha256(json.dumps(payload, separators=(',', ':')).encode()).hexdigest()


def dual_bound(variables, eq, ub, tariffs, certificate, kappa, derivative=False):
    need(certificate['model_sha256'] == model_hash(variables, eq, ub, tariffs),
         'The dual must bind the reconstructed model')
    scale = certificate['scale']
    need(isinstance(scale, int) and scale > 0, 'A positive integer dual scale')
    residual = [0]*len(variables)
    for j, weight, rank in tariffs:
        if derivative:
            if not rank:
                value = 0
            elif weight >= 0:
                value = -weight*rank*log_rank(rank)[1]
            else:
                value = (-weight)*power(rank, Q('.0034'))[0]*log_rank(rank)[0]//UNIT
        else:
            lo, hi = power(rank, kappa)
            value = weight*(lo if weight >= 0 else hi)
        residual[j] = scale*value
    rhs = 0
    for name, rows in [('eq', eq), ('ub', ub)]:
        seen = set()
        for i, value in certificate[name]:
            need(isinstance(i, int) and 0 <= i < len(rows) and i not in seen,
                 'Each dual row index must be valid and distinct')
            need(isinstance(value, int), 'Each dual coefficient must be an integer')
            need(name == 'eq' or value <= 0, 'Upper-bound dual signs must be nonpositive')
            seen.add(i)
            row, b = rows[i]
            rhs += UNIT*value*b
            for j, a in row.items():
                residual[j] -= UNIT*value*a
    correction = sum(min(0, r) for r in residual)
    return Q(rhs+correction, UNIT*scale), Q(correction, UNIT*scale)


def source_model_control(variables, eq, ub, tariffs, dims, source):
    x = []
    for v in variables:
        if v[0] == 'node':
            x.append(int(dims[v[1]] == v[2]))
        else:
            x.append(int((dims[v[1]], dims[v[2]]) == (v[3], v[4])))
    need(all(sum(a*x[j] for j, a in row.items()) == rhs for row, rhs in eq),
         'The original word must satisfy every equality')
    need(all(sum(a*x[j] for j, a in row.items()) <= rhs for row, rhs in ub),
         'The original word must satisfy every inequality')
    histogram = Counter()
    for j, w, r in tariffs:
        histogram[r] += w*x[j]
    expected = Counter(source['paid'])
    expected.subtract(source['helpers'])
    histogram.pop(0, None)
    need(dict(+histogram) == dict(+expected) and dict(-histogram) == dict(-expected),
         'The model must reproduce the complete original signed invoice')


def caller_bound(native_lower, kappa):
    # The recurrence and tail are from PR6398, section 5. All helper
    # targets, binary queries and paired or individual idles remain paid.
    tail = 100
    h = {r: tuple(Q(x, UNIT) for x in power(r, kappa)) for r in range(1, 8*tail+2)}
    lower = [Q(0)]*tail
    binary_splits = 0
    for n in range(2, tail):
        node = 2*h[8*n][0]+1-2*h[8*n+1][1]
        lower[n] = min(lower[a]+lower[n-a]+node for a in range(1, n))
        binary_splits += n-1
    pairs = {}
    for n in range(2, tail-1):
        pairs[n] = max(h[8*n+1][1]-n*native_lower/104-lower[n-b]-lower[b]
                       +h[8*b+1][1]-h[8*b][0] for b in range(1, n))
    margins = [(h[8*n+1][1]+pairs[a]+pairs[n-a]-2, n, a)
               for n in range(4, tail) for a in range(2, n-1)]
    finite, total, first_pair = max(margins)
    bound = (h[8*tail+1][1]+2*h[4*tail+1][1]-tail*(native_lower/104-1)
             +2*(h[9][1]-h[8][0])-6)
    derivative = (8*(1-kappa)*(h[8*tail+1][1]/(8*tail+1)
                               +h[4*tail+1][1]/(4*tail+1))-(native_lower/104-1))
    need(finite < 0, 'Every finite root must have negative raw margin')
    need(bound < 0 and derivative < 0, 'The concave tail must be negative and decreasing')
    return {'binary_splits': binary_splits, 'root_pair_checks': len(margins),
            'finite_margin_upper': str(finite), 'finite_total': total,
            'finite_first_pair': first_pair, 'tail_from': tail,
            'tail_margin_upper': str(bound), 'tail_derivative_upper': str(derivative)}


def positive_caller_control(source, kappa):
    """Check the retained 7,2,2,7 caller with outward lower margins."""
    h = {r: tuple(Q(x, UNIT) for x in power(r, kappa)) for r in range(1, 146)}
    native_upper = (sum(c*h[r][1] for r, c in source['paid'].items())
                    -sum(c*h[r][0] for r, c in source['helpers'].items()))/104
    upper = [Q(0)]*8
    for n in range(2, 8):
        node = 2*h[8*n][1]+1-2*h[8*n+1][0]
        upper[n] = min(upper[a]+upper[n-a]+node for a in range(1, n))
    margin = (h[145][0]+2*h[73][0]+1+2*h[17][0]
              -18*native_upper-2*upper[7]-2*upper[2]-3-2*h[16][1])
    need(margin > 0, 'The source must pass its published raw caller price')
    return str(margin)


def reject(action, message):
    try:
        action()
    except ValueError:
        return
    raise ValueError('A negative control passed: '+message)


def controls(variables, eq, ub, tariffs, certificate, dims, source, kappa):
    bad = dict(certificate, model_sha256='0'*64)
    reject(lambda: dual_bound(variables, eq, ub, tariffs, bad, kappa), 'wrong model hash')
    bad = dict(certificate, ub=[[0, 1]])
    reject(lambda: dual_bound(variables, eq, ub, tariffs, bad, kappa), 'wrong dual sign')
    bad = dict(certificate, eq=[[0, 0], [0, 0]])
    reject(lambda: dual_bound(variables, eq, ub, tariffs, bad, kappa), 'duplicate row')
    bad = dict(certificate, eq=[[len(eq), 0]])
    reject(lambda: dual_bound(variables, eq, ub, tariffs, bad, kappa), 'invalid row')
    changed = dict(source, paid=dict(source['paid']))
    changed['paid'][1] -= 1
    reject(lambda: source_model_control(variables, eq, ub, tariffs, dims, changed),
           'one omitted paid rank-one call')
    changed = dict(source, helpers=dict(source['helpers']))
    changed['helpers'][9] += 1
    reject(lambda: source_model_control(variables, eq, ub, tariffs, dims, changed),
           'one unpaid productive target')
    reject(lambda: caller_bound(Q(0), kappa), 'zero native bill')
    return 7


def source_bytes(path, expected):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == expected, 'The exact source word hash')
    return raw


def child_cap(native_per_port_lower, kappa, cap):
    upper = (2*Q(power(8*(cap+1), kappa)[1]-power(8*cap, kappa)[0], UNIT)
             -native_per_port_lower+1)
    need(upper < 0, 'The universal child increment must be negative')
    return {'kappa_from': str(kappa), 'child_cap': cap, 'increment_upper': str(upper)}


def general_child_caps(results):
    base = Q(results[1]['native_cost_lower'])
    k0 = Q(results[1]['kappa'])
    derivative = min(Q(row['native_derivative_lower']) for row in results)
    rows = []
    for kappa, cap in [(k0, 22), (Q('.003288299')*Q(101, 100), 21)]:
        native_lower = (base+derivative*(kappa-k0))/104
        rows.append(child_cap(native_lower, kappa, cap))
    reject(lambda: child_cap(Q(0), k0, 22), 'a free native word in the child cap')
    return {'scope': 'Any root with fresh stage incidence and charged whole idles; raw budget only',
            'tiers': rows, 'extra_negative_controls': 1}


def run_case(spec):
    raw = source_bytes(HERE/'input'/spec['word'], spec['sha256'])
    w = json.loads(gzip.decompress(raw))
    g = graph(w)
    lo, hi = bounds(w, g)
    old = [span(w['frames'][f]) for f in g['old']]
    source = invoice(w, g, old)
    need(source['owned_rank'] == 56, 'The source owned rank control')
    need(source['paid'] == spec['paid'], 'The source paid invoice control')
    need(source['helpers'] == HELPERS, 'The source helper invoice control')
    variables, _, eq, ub, tariffs = model(w, g, None)
    dims = list(map(dimension, old))
    source_model_control(variables, eq, ub, tariffs, dims, source)
    kappa = Q(spec['kappa'])
    certificate = json.loads((HERE/spec['dual']).read_text())
    lower, correction = dual_bound(variables, eq, ub, tariffs, certificate, kappa)
    derivative_certificate = json.loads((HERE/spec['derivative']).read_text())
    derivative_lower, _ = dual_bound(variables, eq, ub, tariffs, derivative_certificate, kappa, True)
    need(derivative_lower > 3866, 'Every legal native deficit must increase up to the BIT cap')
    source_upper = Q(sum(c*power(r, kappa)[1] for r, c in source['paid'].items())
                     -sum(c*power(r, kappa)[0] for r, c in source['helpers'].items()), UNIT)
    need(source_upper-lower < Q('.055'), 'The maximum native saving bound')
    return {'source': spec['name'], 'kappa': str(kappa), 'source_sha256': spec['sha256'],
            'components': len(g['old']), 'flexible_components': sum(a != b for a, b in zip(lo, hi)),
            'variables': len(variables), 'equalities': len(eq), 'inequalities': len(ub),
            'model_sha256': certificate['model_sha256'], 'native_cost_lower': str(lower),
            'native_saving_upper': str(source_upper-lower), 'dual_correction': str(correction),
            'native_derivative_lower': str(derivative_lower), 'saving_cap': '17/5000',
            'positive_caller_margin_lower': positive_caller_control(source, Q(spec['source_kappa'])),
            'negative_controls': controls(variables, eq, ub, tariffs, certificate, dims, source, kappa),
            'caller': caller_bound(lower, kappa)}


def run():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    for row in sources['retained_predecessors']:
        source_bytes(HERE/row['retained_path'], row['sha256'])
    specs = json.loads((HERE/'CASES.json').read_text())
    for spec in specs:
        spec['paid'] = {int(r): c for r, c in spec['paid'].items()}
    results = [run_case(spec) for spec in specs]
    need(Q(results[0]['kappa']) <= Q(results[1]['kappa']), 'The source ceiling order')
    need(Q(results[0]['native_cost_lower']) > Q(results[1]['native_cost_lower']),
         'The latest bound must also cover the earlier source by monotonicity')
    return {'status': 'PASS_EXACT_MONOTONE_FRAME_CALLER_EXCLUSION',
            'mixed_source_ceiling': results[1]['kappa'], 'cases': results,
            'general_child_caps': general_child_caps(results)}



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, indent=2)+'\n'
    if args.write:
        (HERE/'RESULT.json').write_text(text)
    else:
        need(result == json.loads((HERE/'RESULT.json').read_text()), 'The exact retained receipt')
    print(text, end='')
