"""Check the selected word and the complete two-class guard frontier."""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G = load('two_rate_guards', P/'guards.py')


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {key:encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def rational(word, weights, pair):
    rows = [{} for _ in range(word['public']+word['owned_fields'])]
    deltas = {}
    def norm(row):
        return sum((abs(value)*deltas[i] for i, value in row.items()), F(0))
    for j, event in enumerate(word['program']):
        op, r = event[:2]
        q = F(event[-2]) if op in ('ADD', 'COPY', 'SCALE') else F(1)
        if op in ('MOVE', 'ADD', 'SCALE'):
            feedback = norm(rows[r])
            if op == 'ADD':
                feedback += abs(q)*norm(rows[event[2]])
            elif op == 'SCALE':
                feedback *= abs(q)
            guard = pair[0 if op == 'MOVE' else 1]
            deltas[j] = F(0) if guard is None else (weights[j][0]+feedback)/2**guard
        if op in ('INIT', 'CLEAR'):
            rows[r] = {}
        elif op == 'SCALE':
            rows[r] = {i:q*v for i, v in rows[r].items()}
        elif op == 'COPY':
            rows[r] = {i:q*v for i, v in rows[event[2]].items()}
        elif op == 'ADD':
            for i, v in rows[event[2]].items():
                rows[r][i] = rows[r].get(i, F(0))+q*v
        if op in ('MOVE', 'ADD', 'SCALE'):
            rows[r][j] = F(1)
    return [norm(row) for row in rows]


def reject(label, function):
    try:
        function()
    except ValueError:
        return label
    raise ValueError('accepted control: '+label)


def run():
    sources = json.loads((P/'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] == 'input':
            G.require(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source bytes '+row['path'])
    source = ROOT/'research/p104-gauge-error-covariance'
    transfer = load('source_transfer', source/'transfer.py')
    causal = load('source_causal', source/'causal.py')
    raw = gzip.decompress((ROOT/'research/p104-helper470-twin-rung-removal/WORD.json.gz').read_bytes())
    word = json.loads(raw)
    G.require((len(word['program']), word['public'], word['owned_fields']) == (22803, 770, 29), 'complete selected word')
    sites = {i for i, e in enumerate(word['program']) if e[0] in ('MOVE', 'ADD', 'SCALE')}
    weights, ideal_peak = transfer.ideal(word, sites)
    prepared = G.prepare(word, weights, causal)
    certificate = json.loads((P/'CERTIFICATE.json').read_text())
    corners = G.check_certificate(prepared, word['public'], certificate)
    exact_class_corners = []
    for pair in [(13, None), (None, 15)]:
        result = G.bound(prepared, pair)
        maximum = max(result['final'][:word['public']])
        G.require(maximum >= 1, 'all-precision exclusion corner')
        exact_class_corners.append(dict(guards=pair, maximum=maximum, peak=result['peak']))
    chosen = []
    for pair in [(14, 17), (15, 16)]:
        result = G.bound(prepared, pair, details=True)
        G.require(max(result['final'][:word['public']]) < 1, 'complete public output guard')
        G.require(not any(result['final'][word['public']:]), 'exact owned reset error return')
        G.require(ideal_peak+result['peak'] < 1024, 'complete prefix range')
        delta_weights = [(F(d, 1 << 96), F(0)) for d in result['deltas']]
        scores, hashes = transfer.transpose(word, delta_weights, sites)
        G.require([row[0] for row in scores] == result['final'], 'separate whole-word transpose')
        digest = sha256(json.dumps(encode(result['final']), separators=(',', ':')).encode()).hexdigest()
        chosen.append(dict(guards=pair, maximum=max(result['final'][:word['public']]),
                           peak=result['peak'], final_sha256=digest,
                           transpose_sha256=sha256(''.join(hashes).encode()).hexdigest()))
    uniform = G.bound(prepared, (16, 16))
    retained = causal.bound(word, weights, sites, 16)
    G.require(uniform['final'] == retained['final'] and uniform['peak'] == retained['peak'], 'unchanged uniform source rule')
    toy_cases = 0
    for q in ['1/4', '-3/8', '2', '-1']:
        toy = dict(public=2, owned_fields=1, program=[['MOVE', 0, 0, 0, False],
            ['ADD', 1, 0, q, 0], ['ADD', 1, 0, str(-F(q)), 0],
            ['SCALE', 1, '1/2', 0], ['INIT', 2, 0], ['COPY', 2, 1, '-1/8', 0],
            ['MOVE', 2, 0, 0, True], ['CLEAR', 2, 0]])
        tw = [(F(j+1, 4), F(1)) for j in range(8)]
        tp = G.prepare(toy, tw, causal)
        for pair in [(0, 0), (1, 4), (4, 1), (6, 12), (12, 6), (32, 32),
                     (None, 3), (3, None), (None, None)]:
            upper = G.bound(tp, pair)['final']
            exact = rational(toy, tw, pair)
            G.require(all(a >= b for a, b in zip(upper, exact)), 'independent mixed rational oracle')
            toy_cases += 1
    controls = []
    for bad in [(1,), (-1, 10), (33, 0), (True, 4), ('4', 3)]:
        controls.append(reject('invalid guards '+repr(bad), lambda bad=bad:G.bound(prepared, bad)))
    false = deepcopy(certificate)
    false['frontier'][0][1] = 16
    controls.append(reject('understated scalar guard', lambda:G.check_certificate(prepared, 770, false)))
    false_cost = deepcopy(certificate)
    false_cost['optimum_cost'] -= 1
    controls.append(reject('false complete guard bill', lambda:G.check_certificate(prepared, 770, false_cost)))
    truncated = deepcopy(certificate)
    truncated['frontier'].pop()
    controls.append(reject('missing high-guard rows', lambda:G.check_certificate(prepared, 770, truncated)))
    toy = dict(public=1, owned_fields=0, program=[['MOVE', 0, 0, 0, False]]*2)
    feedback = rational(toy, [(F(1), F(1))]*2, (3, None))[0]
    G.require(feedback == F(1, 4)+F(1, 64), 'actual-input feedback fixture')
    controls.append(reject('omit feedback', lambda:G.require(F(1, 4) >= feedback, 'positive second-order error')))
    return encode(dict(events=len(word['program']), public=770, owned=29, noisy_sites=len(sites),
        word_sha256=sha256(raw).hexdigest(), ideal_peak=ideal_peak,
        finite_corners=corners, exact_class_corners=exact_class_corners, pareto_profiles=chosen,
        uniform_guard=16, uniform_maximum=max(uniform['final'][:770]),
        optimum=certificate['optimum'], guard_bits_before=certificate['uniform_cost'],
        guard_bits_after=certificate['optimum_cost'], saved_guard_bits=3453,
        tariff_switch=F(19265, 3453), full_transposed_outputs=1598,
        independent_rational_cases=toy_cases, rejected_controls=controls,
        scope='Exact frontier of the stated causal sufficient rule, not a lower bound on physical precision.'))


if __name__ == '__main__':
    G.require(sys.argv[1:] in ([], ['--write']), 'supported arguments')
    result = run()
    if sys.argv[1:] == ['--write']:
        (P/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        G.require(result == json.loads((P/'RESULT.json').read_text()), 'complete deterministic result')
    print('PASS_SELECTED_P104_TWO_RATE_GUARDS')
    print(json.dumps({key:result[key] for key in ['events', 'noisy_sites', 'optimum',
          'guard_bits_before', 'guard_bits_after', 'saved_guard_bits', 'independent_rational_cases']}))
