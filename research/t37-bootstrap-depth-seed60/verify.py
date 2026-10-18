"""Exact selected-T37 six-level audit. @woklerx; substantial OpenAI Codex assistance.

Apache-2.0. The envelope argument credits BagMan9's PR768; the source replay
retains the selected PR942 and PR144/23/547/548 balanced outer implementation.
"""
import argparse
import ast
import copy
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '8bddbee377e2f3ce1f1247196c4b290d55767d20'
RECEIPT = 'research/community-frontier942-audit/ASSEMBLY.json'
ASSEMBLER = 'research/complex-t21-owners/vendor/pr870/code/assemble.py'
ADAPTER = 'research/complex-t37-owners/prepare.py'
ENGINE = 'research/complex-sw4-frame8/vendor/main/research/complex-k492-owner-repair/vendor/multicold/engines/outer.py'
REQUIRED_INPUTS = {RECEIPT, ASSEMBLER, ADAPTER, ENGINE, 'docs/research/community-batch952-review.md'}
A0 = Q(384599, 10**10)
ETA = BETA = Q(1, 10**24)
BRIDGE = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1},
          'rows': {'degree_gap': Q(10**6) - Q(51*20161, 25)}}


def need(condition, label):
    if not condition:
        raise ValueError(label)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def normalized(path):
    return path.read_bytes().replace(b'\r\n', b'\n')


def source_pins():
    pins = read(HERE / 'SOURCES.json')
    need(pins['base_commit'] == BASE, 'base pin')
    need(set(pins['files']) == REQUIRED_INPUTS, 'exact consumed source inventory')
    for name, wanted in pins['files'].items():
        need(hashlib.sha256(normalized(ROOT / name)).hexdigest() == wanted, 'source pin: ' + name)
    return pins


def module(path):
    spec = importlib.util.spec_from_file_location('pinned_outer', path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def original_outer_function(engine, bit, depth):
    """Extract only the pinned nested function, preserving its assertions.

    T37's adapter changes two payload literals 512->1024 in this function.
    The only experiment edit is range(7)->range(depth), in memory.
    Exact equality with all seven recorded levels and 47 slacks checks the
    reconstruction before any six-level result is accepted.
    """
    tree = ast.parse((ROOT / ASSEMBLER).read_text(encoding='utf-8'))
    found = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'outer_witness']
    need(len(found) == 1, 'unique source bootstrap function')
    function = copy.deepcopy(found[0])
    payloads = levels = 0
    for node in ast.walk(function):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value == 512:
            node.value = 1024
            payloads += 1
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'range':
            need(len(node.args) == 1 and isinstance(node.args[0], ast.Constant) and node.args[0].value == 7,
                 'unique seven-level loop')
            node.args[0].value = depth
            levels += 1
    need(payloads == 2 and levels == 1, 'scoped AST changes')
    adapter = (ROOT / ADAPTER).read_text(encoding='utf-8')
    need("('(4+512)','(4+1024)',2)" in adapter, 'T37 payload adaptation binding')
    space = {'Q': Q, 'c': bit, 'A': engine}
    isolated = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))
    exec(compile(isolated, ASSEMBLER + ':outer_witness', 'exec'), space)
    return space['outer_witness']


def independent_levels(s, count, payload=1024):
    """Closed form plus integer cross-products; no predecessor imports."""
    old, rows = A0, []
    for depth in range(1, count+1):
        a = s - (s-A0)*s**depth
        need(a == s*(1-s+old), 'closed form versus affine step')
        need(old < a < s < 1-a, 'strict recurrence interface')
        gaps = [s-a, 1-a-s, 1-a-s*(1-old), 1-s]
        gap = min(gaps)
        need(gap > 0, 'positive recursive gap')
        n, d = gap.numerator, gap.denominator
        quadratic = (36*d*d+n*n-1)//(n*n)
        linear = (2*(4+payload)*d+n-1)//n
        cutoff = max(quadratic, linear)
        need(cutoff*n*n >= 36*d*d and cutoff*n >= 2*(4+payload)*d, 'both cutoff obligations')
        need((cutoff-1)*n*n < 36*d*d or (cutoff-1)*n < 2*(4+payload)*d,
             'smallest integer satisfying these two sufficient inequalities')
        rows.append({'exponent': str(a), 'gap': str(gap), 'cutoff_log2': str(cutoff)})
        old = a
    return rows


def strict_grid(margin):
    scaled = margin*10**18
    return Q((scaled.numerator-1)//scaled.denominator, 10**18)


def run():
    need(__debug__, 'run without -O: pinned engine uses assertions')
    pins = source_pins()
    original = read(ROOT / RECEIPT)
    selected = read(HERE / 'SELECTED-SNAPSHOT.json')
    b, c, k = map(Q, [original['complex_lower'], original['bit_lower'], original['kappa']])
    need(selected['base_commit'] == BASE and selected['certificate'] == RECEIPT and
         str(k) == selected['kappa'] and k == Q(1661960547713947, 10**18), 'selected snapshot grid binding')
    need(hashlib.sha256(normalized(ROOT / ENGINE)).hexdigest() == original['input_sha256']['engines/outer.py'],
         'selected receipt outer-engine identity')
    engine = module(ROOT / ENGINE)
    baseline = original_outer_function(engine, c, 7)(b)
    need(baseline[0] == k and baseline[1] == original['bootstrap'], 'all seven baseline levels')
    need({n: str(v) for n, v in baseline[2]['strict_constraints'].items()} == original['outer'],
         'all 47 baseline outer slacks')
    s = min(c, (1-BETA)*b)-Q(1, 10**27)
    levels = independent_levels(s, 7)
    need(levels == baseline[1], 'independent seven-level reconstruction')
    candidate = original_outer_function(engine, c, 6)(b)
    need(candidate[0] == k and candidate[1] == levels[:6], 'six levels retain selected grid and cutoffs')
    a6 = Q(levels[5]['exponent'])
    margins = candidate[2]['strict_constraints']
    need(len(margins) == 47 and all(v > 0 for v in margins.values()), 'all 47 six-level strict interfaces')
    q = a6*(1-2*ETA)
    compact = (1-ETA)*q/(1+q)
    need(compact == candidate[2]['minimum_margin'] and strict_grid(compact) == k, 'independent compact/grid arithmetic')

    # The published moment interval admits b and excludes u=b+10^-24. The
    # moments themselves are inherited inputs, not rerun by this depth audit.
    u = b+Q(1, 10**24)
    next_moment = [r for r in original['moments'] if r['side'] == 'complex' and Q(r['endpoint']) == u]
    need(len(next_moment) == 1 and next_moment[0]['accept'] is False, 'upper moment grid receipt')
    need(all(Q(x) > 0 for key in ('mercator', 'base_two') for x in next_moment[0][key]),
         'both inherited upper-endpoint sign intervals')
    need(0 < A0 < u < Q(1, 32), 'monotone envelope domain')
    envelopes = []
    for depth in range(6):
        upper_a = u-(u-A0)*u**depth
        upper_margin = upper_a/(1+upper_a)
        need(upper_margin < k, 'depth <=5 must fail even optimistic upper ceiling')
        envelopes.append({'depth': depth, 'saving_upper': str(upper_a),
                          'compact_upper': str(upper_margin), 'shortfall': str(k-upper_margin)})

    controls = []
    def rejected(label, fn, expected=None):
        try:
            fn()
        except (ValueError, AssertionError) as error:
            if expected is not None:
                need(expected in str(error), 'wrong rejection reason: '+label)
            controls.append(label)
            return
        raise ValueError('accepted negative control: '+label)

    a5 = Q(levels[4]['exponent'])
    rejected('five levels at selected kappa', lambda: engine.assembly(a5, b, BRIDGE, k, eta=ETA, beta=BETA),
             'compact_phase_layer_above_kappa')
    rejected('six levels at next grid', lambda: engine.assembly(a6, b, BRIDGE, k+Q(1, 10**18), eta=ETA, beta=BETA),
             'compact_phase_layer_above_kappa')
    rejected('zero eta is not an admitted witness', lambda: engine.assembly(a6, b, BRIDGE, k, eta=Q(0), beta=BETA),
             'q_below_reservations')
    rejected('zero beta is not an admitted witness', lambda: engine.assembly(a6, b, BRIDGE, k, eta=ETA, beta=Q(0)),
             'beta_positive')
    for index, row in enumerate(levels[:6], 1):
        gap, low = Q(row['gap']), int(row['cutoff_log2'])-1
        rejected('level %d cutoff decreased by one'%index,
                 lambda gap=gap, low=low: need(low*gap*gap >= 36 and low*gap >= 2*(4+1024), 'cutoff obligations'),
                 'cutoff obligations')
    damaged = copy.deepcopy(candidate[1])
    damaged[-1]['exponent'] = str(a6+Q(1, 10**24))
    rejected('changed sixth exponent', lambda: need(damaged == independent_levels(s, 6), 'recurrence binding'))
    # Prevent extending this fixed-seed obstruction to all starting suppliers.
    required_start = u-(u-k/(1-k))/u**5
    stronger_start = (required_start+u)/2
    stronger_a5 = u-(u-stronger_start)*u**5
    need(A0 < required_start < stronger_start < u and stronger_a5/(1+stronger_a5) > k,
         'stronger-start positive boundary control')
    controls.append('stronger initial saving can cross the five-level ceiling (positive control)')
    return {'status': 'PASS_T37_BOOTSTRAP_DEPTH_S60', 'base_commit': BASE, 'assignment_seed': 60,
            'source_manifest_sha256': hashlib.sha256(normalized(HERE/'SOURCES.json')).hexdigest(),
            'kappa': str(k), 'complex_admitted_endpoint': str(b), 'complex_inherited_upper_endpoint': str(u),
            'bit_endpoint': str(c), 'starting_saving': str(A0), 's': str(s), 'eta': str(ETA), 'beta': str(BETA),
            'original_levels': 7, 'candidate_levels': 6, 'least_levels_in_stated_class': 6,
            'original_bootstrap': levels, 'candidate_bootstrap': candidate[1],
            'original_compact_slack': str(baseline[2]['minimum_margin']-k),
            'candidate_compact_slack': str(compact-k),
            'candidate_outer_slacks': {name: str(value) for name, value in margins.items()},
            'depth_0_through_5_upper_envelopes': envelopes,
            'five_level_required_initial_saving': str(required_start),
            'controls': controls, 'source_controls_at_six': candidate[3],
            'scope': 'Exact affine-bootstrap accounting and 47 finite outer inequalities only; moment brackets, all-size supplier/compiler, physical realization, hosting, precision/tape and analytic transfer remain inherited.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', action='store_true')
    args = parser.parse_args()
    result = run()
    path = HERE/'CERTIFICATE.json'
    if args.write_certificate:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    else:
        need(canonical(result) == canonical(read(path)), 'certificate mismatch')
    print('PASS_T37_BOOTSTRAP_DEPTH_S60 original=7 minimum=6 excluded=0..5 outer=47 negative_controls=11 positive_controls=1 kappa=0.001661960547713947')


if __name__ == '__main__':
    main()
