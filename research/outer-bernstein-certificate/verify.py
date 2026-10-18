#!/usr/bin/env python3
"""Independently check all 47 retained outer inequalities by exact algebra.

Gareth Davidson / OpenAI Codex, Apache-2.0. Arithmetic certificate only;
supplier, bridge construction and full multiplication assumptions are inherited.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from algebra import (Poly, VARIABLES, check_certificate, nominate, require,
                     symbolic_inputs)
from source_model import Model

BASE = '66849e1475c930fd7732b1a0067ffee7e1e95f60'
FILES = {
    'selected': 'certificates/checkpoints/k492626.json',
    'inventory': 'research/community-k492-audit/SELECTED-SOURCE.json',
    'receipt': 'research/community-k492-audit/pr626/replay/ASSEMBLY.json',
    'engine': 'research/complex-k492-owner-repair/vendor/multicold/engines/outer.py',
    'builder': 'research/complex-k492-owner-repair/code/assemble.py',
    'review': 'docs/research/community-k492-review.md',
}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def parse_json(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def inputs(root=ROOT):
    pins = parse_json((HERE / 'SOURCES.json').read_bytes())
    require(pins['base_commit'] == BASE and set(pins['files']) == set(FILES.values()),
            'source inventory differs')
    raw = {}
    for role, path in FILES.items():
        value = (root / path).read_bytes()
        require(sha256(value).hexdigest() == pins['files'][path], 'source hash: ' + role)
        raw[role] = value
    selected, inventory, receipt = (parse_json(raw[n]) for n in ('selected', 'inventory', 'receipt'))
    require(selected['certificate'] == FILES['receipt'] and
            selected['certificate_sha256'] == sha256(raw['receipt']).hexdigest(),
            'selected receipt binding')
    require(selected['source_manifest'] == FILES['inventory'], 'selected inventory binding')
    require(selected['audited_source_head'] == pins['selected_source_head'], 'selected head binding')
    require(selected['kappa'] == receipt['kappa'], 'selected kappa binding')
    for role in ('engine', 'builder'):
        require(inventory['files'][FILES[role]] == sha256(raw[role]).hexdigest(),
                'selected source inventory binding: ' + role)
    require(selected['proof_supplements'][FILES['review']] == sha256(raw['review']).hexdigest(),
            'selected review binding')
    require(receipt['input_sha256']['engines/outer.py'] == sha256(raw['engine']).hexdigest(),
            'consumed outer-engine binding')
    return raw['engine'].decode(), receipt, pins


def obligations(source):
    environment, denominator = symbolic_inputs()
    model = Model(source, environment)
    rows = {'denominator': (denominator, True)}
    for label, values in (('slack', model.env['slacks']), ('branch', model.branches),
                          ('margin', model.margin_gaps)):
        for name, expression in values.items():
            poly = expression.cleared()
            strict = not (label == 'margin' and name == 'compact_phase_layer')
            rows[label + ':' + name] = (poly, strict)
    require(len(rows) == 57, 'proof obligation inventory')
    require(model.margin_gaps['compact_phase_layer'].cleared() == Poly(0),
            'minimum is not attained by compact phase')
    for name, gap in model.identities.items():
        require(gap.cleared() == Poly(0), 'source identity fails: ' + name)
    return model, rows


def check_proof(source, certificates):
    model, rows = obligations(source)
    require(set(certificates) == set(rows), 'incomplete or surplus proof rows')
    for name, (poly, strict) in rows.items():
        check_certificate(poly, certificates[name], strict=strict)
    return model, rows


def ceil(value):
    return -(-value.numerator // value.denominator)


def admit(a, b, beta, eta, kappa, literal, row):
    require(all(type(x) is F for x in (a, b, beta, eta, kappa, literal, row)),
            'parameters must be exact fractions')
    require(0 < beta < 1 and 0 < eta < F(1, 2), 'backoff domain')
    require(0 < a < (1 - beta) * b and 0 < b < F(1, 32), 'supplier domain')
    require(literal > 0 and row > 0, 'bridge gaps')
    q = a * (1 - 2 * eta)
    gain = (1 - eta) * q / (1 + q)
    require(0 < kappa < gain, 'strict target ceiling')
    return (beta, 32 * b, a / ((1 - beta) * b), 2 * eta, kappa / gain, literal, row)


def witness(source, model, receipt, conservative=False):
    prefix = 'conservative_' if conservative else ''
    b = F(receipt[prefix + 'complex_lower'])
    bit = F(receipt['bit_lower'])
    eta = beta = F(1, 10**24)
    s = min(bit, (1 - beta) * b) - F(1, 10**27)
    initial = F(384599, 10**10)
    require(0 < initial < s < bit and s < (1 - beta) * b, 'bootstrap premise')
    chain = []
    previous = initial
    for depth in range(1, 8):
        # Closed form, independently of the producer's recursive updates.
        a = s - s**depth * (s - initial)
        require(previous < a < s < 1 - a, 'bootstrap order')
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - previous), 1 - s)
        require(gap > 0, 'bootstrap gap')
        cut = max(ceil(36 / gap**2), ceil(F(1032) / gap))
        require(cut * gap**2 >= 36 and cut * gap >= 1032, 'bootstrap cutoff')
        chain.append(dict(exponent=str(a), gap=str(gap), cutoff_log2=str(cut)))
        previous = a
    require(chain == receipt[prefix + 'bootstrap'], 'bootstrap receipt differs')
    q = a * (1 - 2 * eta)
    gain = (1 - eta) * q / (1 + q)
    kappa = F(ceil(gain * 10**18) - 1, 10**18)
    require(kappa == F(receipt[prefix + 'kappa']), 'strict grid witness differs')
    require(kappa < gain <= kappa + F(1, 10**18), 'grid maximality')
    literal, row = F(1), F(10**6) - F(51 * 20161, 25)
    point = admit(a, b, beta, eta, kappa, literal, row)
    numeric = Model(source, dict(bit_saving=a, complex_saving=b, beta=beta,
        eta=eta, kappa=kappa, bridge={'semantic': {'strict_literal_gap': literal},
                                   'rows': {'degree_gap': row}}))
    saved = {name: F(value) for name, value in receipt[prefix + 'outer'].items()}
    direct = numeric.env['slacks']
    require(direct == saved, 'numeric source expressions differ from complete receipt')
    values = {name: expr.evaluate(point) for name, expr in model.env['slacks'].items()}
    require(values == direct and all(v > 0 for v in values.values()), 'polynomial witness differs')
    require(all(value == 0 for value in numeric.identities.values()), 'numeric identities')
    return dict(kappa=str(kappa), gain=str(gain), grid_successor_rejected=True,
                unit_coordinates=[str(x) for x in point[:5]],
                bridge_gaps=[str(literal), str(row)], bootstrap=chain,
                slacks={name: str(value) for name, value in values.items()})


def rejected(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('control unexpectedly accepted: ' + label)


def controls(source, certificates, model, receipt):
    labels = []
    name = 'slack:compact_phase_layer_above_kappa'
    poly = model.env['slacks']['compact_phase_layer_above_kappa'].cleared()
    for label, change in (
        ('negative_weight', lambda c: c['weights'].__setitem__(0, -1)),
        ('no_positive_weight', lambda c: c.update(weights=[0] * len(c['weights']))),
        ('changed_positive_weight', lambda c: c['weights'].__setitem__(0, c['weights'][0] + 1)),
        ('missing_weight', lambda c: c['weights'].pop()),
        ('negative_scale', lambda c: c.update(scale=-c['scale'])),
        ('floating_weight', lambda c: c['weights'].__setitem__(0, 0.0)),
    ):
        cert = deepcopy(certificates[name])
        change(cert)
        labels.append(rejected(lambda: check_certificate(poly, cert), label))
    missing = dict(certificates)
    del missing[name]
    labels.append(rejected(lambda: check_proof(source, missing), 'missing_source_row'))
    surplus = dict(certificates, unexpected=certificates[name])
    labels.append(rejected(lambda: check_proof(source, surplus), 'surplus_source_row'))
    for label, before, after in (
        ('wrong_max_branch', 'max(sigma-tau,Q(0))', 'max(tau-sigma,Q(0))'),
        ('wrong_min_branch', 'min(1-eps-delta,r-delta)', 'min(r-delta,1-eps-delta)'),
        ('missing_target_charge', 'val-kappa', 'val'),
        ('changed_gaussian_cap', 'Q(1,4)-r', 'Q(1,8)-r'),
    ):
        require(source.count(before) == 1, 'mutation anchor')
        mutant = source.replace(before, after)
        labels.append(rejected(lambda: check_proof(mutant, certificates), label))
    for label, edit in (
        ('altered_outer_receipt', lambda r: r['outer'].update(bit_positive='1')),
        ('altered_bootstrap_cutoff', lambda r: r['bootstrap'][0].update(cutoff_log2='1')),
    ):
        mutant = deepcopy(receipt)
        edit(mutant)
        labels.append(rejected(lambda: witness(source, model, mutant), label))
    args = [F(1, 100), F(1, 50), F(1, 4), F(1, 10), F(1, 1000), F(1), F(2)]
    a, b, beta, eta, _, literal, row = args
    q = a * (1 - 2 * eta)
    gain = (1 - eta) * q / (1 + q)
    for label, index, value in (
        ('target_at_ceiling', 4, gain), ('target_above_ceiling', 4, gain + F(1, 10**12)),
        ('zero_backoff', 3, F(0)), ('half_backoff', 3, F(1, 2)),
        ('zero_beta', 2, F(0)), ('unit_beta', 2, F(1)),
        ('cap_equality', 1, F(1, 32)), ('zero_literal_gap', 5, F(0)),
        ('zero_row_gap', 6, F(0)), ('nonexact_parameter', 0, 0.01),
    ):
        altered = list(args)
        altered[index] = value
        labels.append(rejected(lambda: admit(*altered), label))
    return labels


def compute(root=ROOT, expected_certificates=None):
    source, receipt, pins = inputs(root)
    model, rows = obligations(source)
    certificates = {name: nominate(poly) for name, (poly, _) in rows.items()}
    check_proof(source, certificates if expected_certificates is None else expected_certificates)
    witnesses = {name: witness(source, model, receipt, conservative)
                 for name, conservative in (('native', False), ('conservative', True))}
    rejected_controls = controls(source, certificates, model, receipt)
    return dict(format='outer-bernstein-certificate-v1', base_commit=BASE,
                source_hashes=pins['files'], variables=list(VARIABLES),
                certificates=certificates,
                identities={name: '0' for name in model.identities},
                witnesses=witnesses, controls=rejected_controls,
                counts=dict(slacks=47, witnesses=2, coefficient_rows=len(certificates),
                            weights=sum(len(c['weights']) for c in certificates.values()),
                            controls=len(rejected_controls)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='write a new certificate; never overwrite')
    args = parser.parse_args()
    if args.write:
        require(not args.write.exists(), 'output already exists')
    expected = None if args.write else parse_json((HERE / 'EXPECTED.json').read_bytes())
    report = compute(expected_certificates=None if expected is None else expected['certificates'])
    if args.write:
        with args.write.open('x') as out:
            out.write(json.dumps(report, indent=2, sort_keys=True) + '\n')
    else:
        # Preserve JSON numeric types: Python otherwise equates 0, 0.0 and False.
        require(json.dumps(expected, sort_keys=True) == json.dumps(report, sort_keys=True),
                'committed certificate differs')
    counts = report['counts']
    print('PASS_OUTER_BERNSTEIN_CERTIFICATE '
          f"slacks=47 witnesses=2 coefficient_rows={counts['coefficient_rows']} "
          f"weights={counts['weights']} controls={counts['controls']} kappa=unchanged")


if __name__ == '__main__':
    main()
