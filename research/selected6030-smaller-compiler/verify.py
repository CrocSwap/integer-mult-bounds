#!/usr/bin/env python3
"""Source-bound selected #6030 compiler-size application.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The exact intervals, net taxes, concentration and compiler are zxv's unchanged
#4480 sources. The outer ledger is reused with its retained attribution.
This checks an application, not a new theorem or native supplier admission.
"""
import argparse
import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
VENDOR = HERE / 'vendor'
MARKER = 'PASS_SELECTED6030_SMALLER_COMPILER'
C, KAPPA, GAP = Q('0.003125809'), Q('0.003125804'), Q(1, 1400000000)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_bytes())


def authenticate_bytes(raw, row):
    need(sha256(raw).hexdigest() == row['sha256'], 'source SHA256: ' + row['filename'])
    blob = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    need(blob == row['git_blob'], 'source Git blob: ' + row['filename'])


def authenticate():
    rows = read(HERE / 'VENDOR.json')['files']
    need(len({r['filename'] for r in rows}) == len(rows), 'unique source exports')
    need({p.name for p in VENDOR.iterdir()} == {r['filename'] for r in rows},
         'complete exported source inventory')
    for row in rows:
        authenticate_bytes((VENDOR / row['filename']).read_bytes(), row)
    return rows


def load(name, filename):
    """Execute authenticated source bytes directly; never cached bytecode."""
    module = types.ModuleType(name)
    module.__file__ = str(VENDOR / filename)
    sys.modules[name] = module
    exec(compile(Path(module.__file__).read_bytes(), module.__file__, 'exec', optimize=0), module.__dict__)
    return module


def rejected(action, expected):
    try:
        action()
    except ValueError as error:
        need(expected in str(error), 'wrong control failure: ' + str(error))
        return str(error)
    raise ValueError('invalid control accepted: ' + expected)


def invoice(result, controller):
    """Recount every caller event using the selected local admission receipt."""
    local, native = result['local'], result['native']
    paid, target, kinds = Counter(), Counter(), Counter()
    for event in controller['physical_events']:
        kinds[event[0]] += 1
        if event[0] == 'LOCAL':
            need(event[3] is False, 'all eighteen actual calls are forward')
            paid.update({int(k): n for k, n in local['paid'].items()})
            target.update({int(k): n for k, n in local['helpers'].items()})
        elif event[0] == 'QUERY_SHEAR':
            paid[1] += 104
        elif event[0] == 'IDLE':
            paid[8 * len(event[2])] += 208
    for term in controller['diagonal']:
        target[1 + 8 * sum(term[1:])] += 104
    need((kinds['LOCAL'], kinds['QUERY_SHEAR'], kinds['IDLE']) == (18, 15, 15), 'complete caller invocation census')
    need(local['helpers'] == native['helpers'], 'native helper targets agree')
    published = result['complete_cost']
    need(paid == {int(k): n for k, n in published['paid'].items()}, 'full paid invoice')
    need(target == {int(k): n for k, n in published['targets'].items()}, 'full target invoice')
    need((sum(paid.values()), sum(target.values())) == (66834, 13444), 'call/field census')
    mass = lambda inv: sum(r*n for r, n in inv.items())
    need((mass(paid), mass(target), max(paid), max(target)) == (240152, 240912, 72, 145), 'complete masses and extreme ranks')
    # Reuse the original assemble function unchanged, with explicit dependency injection.
    path = VENDOR / 'pr6030-pricing.py'
    tree = ast.parse(path.read_bytes())
    body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'assemble']
    need(len(body) == 1, 'unique original invoice assembly')
    env = {'Counter': Counter, 'L': types.SimpleNamespace(need=need)}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(path), 'exec', optimize=0), env)
    converted = deepcopy(result)
    for key in ('local', 'native'):
        for field in ('paid', 'helpers'):
            if field in converted[key]:
                converted[key][field] = {int(k): v for k, v in converted[key][field].items()}
    for field in ('whole_idle_jobs', 'main_targets'):
        converted['physical_caller'][field] = {int(k): v for k, v in converted['physical_caller'][field].items()}
    source_target, source_paid, _ = env['assemble'](converted['local'], converted['native'], controller, converted['physical_caller'])
    need(source_target == target and source_paid == paid, 'reused source independent path-length recount')
    signed = Counter(target)
    signed.subtract(paid)
    return {'targets': dict(target), 'paid': dict(paid)}, signed


def outer(result, E):
    """Re-evaluate all unchanged nine rows, 54 strict and four functional checks."""
    endpoint = load('selected_outer_source', 'outer-endpoint.py')
    params = {'kappa': KAPPA, 'tested_saving': C, 'complex_uniform_saving': KAPPA+6*GAP,
              'b': KAPPA+5*GAP, 'a': KAPPA+4*GAP, 'q': KAPPA+3*GAP,
              'bit_saving': Q(17, 5000), 'epsilon': 1-GAP, 'beta': 1-3*GAP,
              'r0': GAP/10, 'stop': GAP, 'layout': GAP, 'd': GAP}
    bit = result['complete_cost']['ordinary_BIT']
    atom = Q(bit['atom'])
    ordinary = (1-atom)*Q(bit['after_cover'])+atom*Q('.0000384599')
    need(ordinary == Q(bit['ordinary_saving']), 'same complete ordinary BIT bound')
    need(atom > ordinary > Q(bit['admitted']) > C and atom < 1-ordinary, 'same admitted BIT/stock gate')
    value = endpoint.ledger(params)
    value['functional_checks']['actual_new_BIT_stock_sublinear'] = params['beta']*(1-atom)
    need(E.encoded(value) == result['complete_cost']['outer'], 'unchanged complete outer payload')
    need(len(value['strict_checks']) == 54 and len(value['functional_checks']) == 4, 'complete outer predicate census')
    need(all(v > 0 for key in ('strict_checks', 'functional_checks') for v in value[key].values()), 'all outer gates strict')
    bad = endpoint.ledger(dict(params, bit_saving=Q('.0027')))
    need(any(v <= 0 for v in bad['strict_checks'].values()), 'underfunded BIT rejected')
    return value


def literal_completion_control():
    """Exact formal signed-inventory identity, including all owner completions."""
    def tensor(inv):
        out = Counter()
        for r, n in inv.items():
            for s, m in inv.items():
                out[r*s] += n*m
        return out

    def split(inv, cutoff):
        out = Counter()
        for r, n in inv.items():
            q, s = divmod(r, cutoff)
            out[cutoff] += n*q
            if s:
                out[s] += n
        return +out

    def signed_sum(*terms):
        out = Counter()
        for inv, sign in terms:
            for r, n in inv.items():
                out[r] += sign*n
        return {r: n for r, n in out.items() if n}

    T, P = tensor({2: 1, 5: 1}), tensor({1: 2, 4: 1})
    J, L = 4, 9
    completed, completion = Counter(), Counter()
    for rank, count in T.items():
        completed[max(L, rank)] += count
        if rank < L:
            completion[L-rank] += count
    split_raw, split_completion = split(P, J), split(completion, J)
    final = split_raw + split_completion
    tax = signed_sum((split_raw, 1), (P, -1))
    completion_tax = signed_sum((T, 1), (split_completion, 1), (completed, -1))
    need(signed_sum((completed, 1), (final, -1)) ==
         signed_sum((T, 1), (P, -1), (tax, -1), (completion_tax, -1)),
         'literal exact net gap identity as a formal power sum')
    mass = lambda inv: sum(r*n for r, n in inv.items())
    need(final == Counter({1: 5, 4: 9}) and mass(completed)-mass(final) == 13, 'complete literal split/completion inventory')
    need(sum(completed.values()) == sum(T.values()), 'completion creates no productive owner')
    error = rejected(lambda: need(mass(completed)-mass(split_raw) == 13,
                                 'free completion changes rank surplus'), 'free completion')
    return {'raw_targets': T, 'raw_paid': P, 'completion_jobs': completion,
            'final_targets': completed, 'final_paid': final, 'preserved_surplus': 13,
            'free_completion_rejection': error}


def main_result():
    rows = authenticate()
    E = load('intervals', 'net-intervals.py')
    compiler = load('selected_net_compiler_source', 'net-compiler.py')
    selected = read(VENDOR / 'selected-result.json')
    result = read(VENDOR / 'pr6030-result.json')
    need(selected['source_certificate_sha256'] == sha256((VENDOR/'pr6030-result.json').read_bytes()).hexdigest(),
         'selected record binds actual source receipt')
    need(Q(selected['kappa']) == KAPPA == Q(result['complete_cost']['kappa']), 'unchanged selected kappa')
    need((C-KAPPA)/7 == GAP, 'unchanged compiler and outer gap')
    need(sha256((VENDOR/'pr6030-review.md').read_bytes()).hexdigest() ==
         selected['proof_supplements'][selected['proof']], 'selected review binding')
    controller = read(VENDOR / 'pr6030-controller.json')
    profile, signed = invoice(result, controller)
    witness = read(HERE / 'WITNESS.json')
    need(witness['saving'] == str(C) and witness['kappa'] == str(KAPPA), 'fixed tested and declared saving')
    certificate = compiler.certify(profile, witness)
    need(certificate['uniform']['uniform_saving'] == str(KAPPA+6*GAP), 'unchanged uniform saving')
    need(certificate['uniform']['H'] == 1449000000000, 'specified new sufficient height')
    need(witness['v'] == 370 and witness['p'] == 37 and witness['log_shift'] == 5550,
         'specified changed finite construction')
    value = outer(result, E)
    old = result['complete_cost']['compiler']
    need(old['H'] == 65807000000000 and old['logarithm_power'] == 1024, 'selected comparison bound')
    t = 1-C
    target = E.moment(profile['targets'], t)
    alpha = E.divide(E.moment(profile['paid'], t), target)
    gamma = E.divide(E.moment(profile['paid'], t+Q(1, 7)), E.mul(E.power(16, Q(1, 7)), target))
    delta = E.divide((Q(13444*17),)*2, E.mul(E.power(16, C), target))
    for name, computed in (('alpha', alpha), ('gamma', gamma), ('delta', delta)):
        saved = result['complete_cost']['strictification'][name]
        need(Q(saved['lower']) <= computed[0] <= computed[1] <= Q(saved['upper']), 'original displayed ' + name + ' interval')
    need(alpha[1] < 1-Q(1, 10**12) and gamma[1] < Q(125, 128) and delta[1] < Q(125, 128), 'original selected tail envelope')
    need(Q(125, 128)**128 < Q(1, 16) and 1/(1+Q(1024, 10**12))+Q(4, 2**32) < 1, 'original selected complete charge')
    need((old['H']+1)**1024 < 2**47005 and (old['H']-GAP.denominator+1)**1024 >= 2**47004,
         'original selected integer threshold and preceding-grid failure')
    controls = {}
    controls['smaller_product'] = rejected(lambda: compiler.certify(profile, dict(witness, v=369)), 'strict net moment certificate')
    controls['smaller_log_power'] = rejected(lambda: compiler.certify(profile, dict(witness, p=36)), 'polynomial coefficients below capacity')
    controls['sublinear_tail'] = rejected(lambda: compiler.certify(profile, dict(witness, u=str(C/2))), 'net tax exponent domain')
    bad_result = deepcopy(result)
    bad_result['local']['paid']['1'] -= 1
    controls['missing_paid_job'] = rejected(lambda: invoice(bad_result, controller), 'full paid invoice')
    bad_controller = deepcopy(controller)
    index = next(i for i, event in enumerate(bad_controller['physical_events']) if event[0] == 'IDLE')
    del bad_controller['physical_events'][index]
    controls['omitted_whole_idle'] = rejected(lambda: invoice(result, bad_controller), 'complete caller invocation census')
    mean_only = deepcopy(witness)
    mean_only['uniform_method'] = 'weighted'
    mean_only['weighted']['mean_upper'] = '871/1000'
    controls['discarded_concentration'] = rejected(lambda: compiler.certify(profile, mean_only), 'polynomial coefficients below capacity')
    data = compiler.tax_data(profile, witness)
    need(data['old_bound'][0] > 1, 'old full-tail sufficient charge fails this new product')
    incomplete = E.add(E.ipow(data['alpha'], 369), E.sub(
        E.add(E.ipow(data['delta'], 369), E.scale(E.mul(data['concavity_remainder'], E.ipow(data['epsilon'], 369)), 2)),
        E.ipow(data['delta0'], 369)))
    need(incomplete[1] < 1, 'missing-tail false positive is discriminating')
    controls['missing_original_tail_false_positive'] = E.display(incomplete)
    full_excess = E.add(data['original_tax'], E.scale(E.ipow(data['delta'], witness['v']), 2))
    net_excess = E.add(data['original_tax'], data['completion_tax'])
    need(full_excess[0] > net_excess[1], 'full paid excess strictly exceeds net gap tax')
    controls['net_completion_not_a_paid_log_budget'] = 'full paid excess separately charged and strictly larger'
    controls['changed_source'] = rejected(lambda: authenticate_bytes(b'changed'+(VENDOR/rows[0]['filename']).read_bytes(), rows[0]), 'source SHA256')
    toy = literal_completion_control()
    shifted_witness = dict(witness, uniform_method='shifted', theta='183/187', p=267, log_shift=50000)
    shifted = compiler.certify(profile, shifted_witness)
    native_count = (66834**370-13444**370)//(66834-13444)
    need(native_count*(66834-13444) == 66834**370-13444**370, 'integer chronological raw-instance count')
    strictified_counts = {
        'raw_instance_count_encoding': '(66834^370-13444^370)/(66834-13444)',
        'productive_fields_encoding': '13444^370',
        'paid_call_upper_encoding': '240152^370+(13444*17)^370',
        'raw_ordinary_pass_upper_encoding': '10^9*(66834^370-13444^370)/(66834-13444)',
        'rank_mass_surplus_encoding': '240912^370-240152^370',
        'full_compiled_word_counts_materialized': False,
        'fresh_constant_prescription': 'PROOF.md section 5; count the new word, not old selected constants'}
    return E.encoded({'status': MARKER,
        'scope': 'Conditional selected-source compiler arithmetic and finite prescription; no new native admission or complete physical threshold.',
        'kappa': KAPPA, 'tested_saving': C, 'uniform_saving': KAPPA+6*GAP,
        'invoice': {'paid': profile['paid'], 'targets': profile['targets'], 'signed_target_minus_paid': signed,
                    'paid_calls': 66834, 'productive_fields': 13444, 'paid_rank_mass': 240152, 'target_rank_mass': 240912},
        'witness': witness, 'certificate': certificate, 'shifted_log_comparison': shifted,
        'selected_H': old['H'], 'height_reduction_factor': Q(old['H'], certificate['uniform']['H']),
        'tensor_power_reduction_factor': Q(1024, witness['v']), 'outer': value,
        'controls': controls, 'literal_completion': toy, 'strictified_count_bounds': strictified_counts,
        'source_sha256': {r['filename']: r['sha256'] for r in rows},
        'verifier_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'witness_sha256': sha256((HERE/'WITNESS.json').read_bytes()).hexdigest(),
        'limitations': ['All five selected framework assumptions remain.',
            'Original native/operator/ownership admission receipt is inherited, not replayed.',
            'No selected cold replay, rounded multiplier, full uniform word, numerical full-word constants, or independent human/proof-kernel acceptance.']})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='authoring only: regenerate deterministic receipt')
    args = parser.parse_args()
    output = main_result()
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(output, indent=2, sort_keys=True)+'\n')
    else:
        need(read(HERE/'RESULT.json') == output, 'complete deterministic saved receipt')
    print(json.dumps({'status': MARKER, 'kappa': output['kappa'], 'H': output['certificate']['uniform']['H'],
                      'reduction_factor': output['height_reduction_factor'],
                      'tensor_power': output['witness']['v'], 'log_power': output['witness']['p']}, sort_keys=True))


if __name__ == '__main__':
    main()
