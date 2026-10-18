"""CK grid-preserving finite scalar construction; ToikY + substantial Codex assistance.

Sparse primitive interpreter adapted from Sagar Thakrar's PR696 verify.py.
Apache-2.0. Independent graph certificate checker is in independent.py.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / 'research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck'
WORK = ('W', 0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def step(rows, op):
    tag, target = op[:2]
    if tag == 'clear':
        rows[target] = {}
    elif tag == 'copy':
        rows[target] = rows[op[2]].copy()
    elif tag in ('double', 'halve', 'negate'):
        factor = {'double': Q(2), 'halve': Q(1, 2), 'negate': Q(-1)}[tag]
        rows[target] = {j: factor*x for j, x in rows[target].items()}
    elif tag in ('add', 'subtract'):
        row = rows[target]
        for j, x in rows[op[2]].items():
            value = row.get(j, Q(0)) + (x if tag == 'add' else -x)
            if value:
                row[j] = value
            else:
                row.pop(j, None)
    else:
        raise ValueError('unknown primitive')


def emit(op, census, reference):
    baseline = reference.lower(op)  # Retains all domain and alias checks.
    if op[0] != 'add' or abs(Q(op[3], op[4])) == 1:
        return baseline
    q = Q(op[3], op[4])
    entry = census[str(abs(q))]
    if entry['cost'] >= len(baseline):
        return baseline
    source, target = tuple(op[2]), tuple(op[1])
    word = [('copy', WORK, source)]
    for tag in entry['word']:
        word.append((tag, WORK, source) if tag in ('add', 'subtract', 'copy') else (tag, WORK))
    word.extend([('add' if q*entry['terminal_sign'] > 0 else 'subtract', target, WORK), ('clear', WORK)])
    return word


def macro_check(q, word, expected_cost=None):
    t, s = ('T', 0), ('S', 0)
    rows = {t: {0: Q(1)}, s: {1: Q(1)}, WORK: {2: Q(1)}}
    a, denominator = abs(q.numerator), q.denominator
    for index, op in enumerate(word):
        step(rows, op)
        require(rows[s] == {1: Q(1)}, 'source restoration')
        if index < len(word)-2:
            require(rows[t] == {0: Q(1)}, 'early target update')
            coefficient = rows[WORK].get(1, Q(0))
            require(set(rows[WORK]) <= {1}, 'dirty work initialization')
            require(abs(coefficient) <= a, 'magnitude envelope')
            require((coefficient*denominator).denominator == 1, 'fractional grid')
    require(rows == {t: {0: Q(1), 1: q}, s: {1: Q(1)}, WORK: {}}, 'macro endpoint')
    if expected_cost is not None:
        require(len(word) == expected_cost, 'macro cost')


def replay(orientation, events, census, reference, checks, inherited):
    n = 716
    rows = {('L', r): {r: Q(1)} for r in range(n)}
    rows.update({('C', r): {n+r: Q(1)} for r in range(8)})
    rows[WORK] = {724: Q(1)}
    env = {register: Q(1) for register in rows}
    peak = Q(1)
    paid, tags, changed = Counter(), Counter(), Counter()
    old = macros = new = 0
    word_hash = hashlib.sha256()
    for event in events:
        if event[0] == 'climb':
            paid[event[5]] += 1
        elif event[0] == 'center':
            paid[event[4]] += 1
        elif event[0] != 'scalar':
            require(event[0] in ('phase', 'adapter', 'residual_adapter'), 'unknown event')
        else:
            op, frame = event[1:]
            target = tuple(op[1])
            baseline, word = reference.lower(op), emit(op, census, reference)
            old += 2*len(baseline)
            new += 2*len(word)
            macros += 1
            if len(word) < len(baseline):
                changed[str(abs(Q(op[3], op[4])))] += 1
            if op[0] == 'add':
                source, q = tuple(op[2]), Q(op[3], op[4])
                peak = max(peak, abs(q.numerator)*env[source])
                env[target] = env[target] + abs(q)*env[source]
            elif op[0] == 'scale':
                env[target] *= abs(Q(op[2], op[3]))
            elif op[0] == 'clear':
                env[target] = Q(0)
            elif op[0] == 'copy':
                env[target] = env[tuple(op[2])]
            peak = max(peak, env[target])
            for primitive in word:
                step(rows, primitive)
                tags[primitive[0]] += 2
                word_hash.update(canonical([frame, primitive])+b'\n')
            if op[0] == 'add':
                require(not rows[WORK], 'work survived macro')
    for r in range(n):
        wanted = {r: Q(1)}
        if orientation == 'forward' and 112 <= r < 224:
            wanted[r-112] = Q(1)
        if orientation == 'backward' and r < 112:
            wanted[r+112] = Q(-1)
        require(rows[('L', r)] == wanted, 'full scalar endpoint')
    require(all(not row for register, row in rows.items() if register[0] != 'L'), 'private cleanup')
    require(dict(paid) == {int(k): v for k, v in checks['paid_profile'].items()}, 'paid profile')
    require(macros == checks['scalar_macros'], 'macro inventory')
    require(peak == Q(inherited['prefix_l1_upper']), 'original envelope')
    require(peak < 2**inherited['charged_payload_bits'], 'charged magnitude budget')
    return {'columns': 725, 'dirty_helpers': 492, 'baseline_real_primitives': old,
            'replacement_real_primitives': new, 'saving': old-new,
            'changed_coefficients': dict(sorted(changed.items())),
            'primitive_tags': dict(sorted(tags.items())), 'primitive_sha256': word_hash.hexdigest(),
            'paid_profile': dict(sorted(checks['paid_profile'].items())),
            'retained_original_envelope': str(peak),
            'charged_payload_bits': inherited['charged_payload_bits']}


def controls(census, reference):
    q = Q(5, 2)
    op = ['add', ['T', 0], ['S', 0], 5, 2]
    word = emit(op, census, reference)
    bad = {
        'missing_copy': word[1:], 'missing_clear': word[:-1],
        'wrong_accumulation': word[:-2]+[('subtract', ('T', 0), WORK)]+word[-1:],
        'endpoint_neutral_growth': word[:1]+[('double', WORK)]*5+[('halve', WORK)]*5+word[1:],
        'endpoint_neutral_finer_grid': word[:1]+[('halve', WORK)]*2+[('double', WORK)]*2+word[1:],
        'uncharged_redundant_ops': word[:1]+[('negate', WORK)]*2+word[1:],
    }
    rejected = {}
    for name, candidate in bad.items():
        try:
            macro_check(q, candidate, len(word))
        except ValueError as error:
            rejected[name] = str(error)
        else:
            raise ValueError('accepted control '+name)
    require(rejected['endpoint_neutral_growth'] == 'magnitude envelope', 'growth reason')
    require(rejected['endpoint_neutral_finer_grid'] == 'fractional grid', 'grid reason')
    require(rejected['uncharged_redundant_ops'] == 'macro cost', 'cost reason')
    return rejected


def verify():
    for name, sha in read(HERE/'SOURCES.json')['payload_sha256'].items():
        path = ROOT/name
        raw = path.read_bytes()
        if path.suffix == '.gz':
            raw = gzip.decompress(raw)
        require(hashlib.sha256(raw).hexdigest() == sha, 'source pin '+name)
    reference = load(ROOT/'research/complex-dyadic-lowering/lower.py', 'pr696')
    horner = load(ROOT/'research/dyadic-horner-direction/lower.py', 'pr837')
    programs = read(DATA/'LOCAL-PROGRAMS.json.gz')
    qs = sorted({abs(Q(e[1][3], e[1][4])) for es in programs.values()
                 for e in es if e[0] == 'scalar' and e[1][0] == 'add'})
    solve = load(HERE/'synth.py', 'synth_ck').solve
    census = {str(q): solve(q.numerator, q.denominator) for q in qs}
    require(canonical(census) == canonical(read(HERE/'CENSUS.json.gz')), 'census mismatch')
    independent = load(HERE/'independent.py', 'independent_ck')
    graph = independent.check(census)
    comparisons = {}
    for q in qs:
        op = ['add', ['T', 0], ['S', 0], q.numerator, q.denominator]
        word = emit(op, census, reference)
        macro_check(q, word)
        negative = ['add', ['T', 0], ['S', 0], -q.numerator, q.denominator]
        macro_check(-q, emit(negative, census, reference))
        four = horner.candidates(op)
        comparisons[str(q)] = {'copy_binary': len(reference.lower(op)),
                              'best_four_horner': min(map(len, four.values())),
                              'installed': len(word), 'bounded_class_cost': census[str(q)]['cost']}
    checks = read(DATA/'LOCAL-CHECKS.json')
    inherited = read(DATA/'INDEPENDENT-LOCAL-REPLAY.json')['local']
    result = {orientation: replay(orientation, programs[orientation], census, reference,
                                checks[orientation], inherited[orientation])
              for orientation in ('forward', 'backward')}
    baseline_receipt = read(ROOT/'research/complex-dyadic-lowering/EXPECTED.json')
    for orientation, events in programs.items():
        require(hashlib.sha256(canonical(events)).hexdigest() == checks[orientation]['sha256'],
                'program semantic hash')
        require(result[orientation]['baseline_real_primitives'] ==
                baseline_receipt['programs']['ck/'+orientation]['new_real_primitives'],
                'copy binary complete baseline')
    for orientation, events in programs.items():
        saving = 0
        four_total = 0
        cases = Counter()
        for event in events:
            if event[0] == 'scalar':
                four_total += 2*min(map(len, horner.candidates(event[1]).values()))
            if event[0] == 'scalar' and event[1][0] == 'add':
                q = str(abs(Q(event[1][3], event[1][4])))
                c = comparisons[q]
                if c['installed'] < c['best_four_horner']:
                    saving += 2*(c['best_four_horner']-c['installed'])
                    cases[q] += 1
        result[orientation]['selected_occurrence_saving_vs_four_horner'] = saving
        result[orientation]['strictly_beyond_four_horner'] = dict(sorted(cases.items()))
        result[orientation]['best_four_horner_complete_real_primitives'] = four_total
        result[orientation]['net_saving_vs_complete_four_horner'] = four_total-result[orientation]['replacement_real_primitives']
    return {'status': 'PASS_CK_GRID_SYNTHESIS', 'magnitudes': len(qs), 'graphs': graph,
            'programs': result, 'comparisons': comparisons, 'controls': controls(census, reference)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', action='store_true')
    args = parser.parse_args()
    result = verify()
    if args.write_certificate:
        (HERE/'EXPECTED.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        require(canonical(result) == canonical(read(HERE/'EXPECTED.json')), 'receipt mismatch')
    print('PASS_CK_GRID_SYNTHESIS magnitudes=103 programs=2 columns=725 savings='+
          ','.join(str(p['saving']) for p in result['programs'].values())+' no_new_kappa')
