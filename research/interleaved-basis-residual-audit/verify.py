"""Verify the deposited residual certificates and independently counted price.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""

from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import gzip
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit
import price


def reject(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError('changed certificate was accepted')


def altered(entries):
    result = deepcopy(entries)
    result[0][1] = str(F(result[0][1]) + 1 if F(result[0][1]) != -1 else F(2))
    return result


def controls(g0, g, restriction, split, item):
    observation = audit.row(split['readout'])
    for field in ('multipliers', 'expansion'):
        changed = deepcopy(item['readout'])
        changed[field] = altered(changed[field])
        reject(lambda: audit.check_functional(g, observation, changed))
    reject(lambda: audit.check_response(g, audit.row(split['pulse']), {}, altered(item['pulse'])))
    reject(lambda: audit.check_response(g, {}, audit.row(split['source_direction']), altered(item['steering'])))
    identity = deepcopy(item['split_identity'])
    identity['column'] = altered(identity['column'])
    reject(lambda: audit.check_identity(g, split['role'], identity))
    half = deepcopy(restriction)
    source = audit.row(half['source'])
    audit.require(source.get(~549) == F(1, 2), 'role549 half-input source pin')
    source.pop(~549)
    half['source'] = audit.packed(source)
    reject(lambda: audit.check_functional(g0, audit.observations(half), item['restriction']))
    return 6


def price_controls(invoice, counts):
    low, high = price.rank_price(4, F(1, 2))
    audit.require(low <= 2 <= high and high - low < F(1, 10**9), 'closed-form square-root control')
    audit.require(price.margin(invoice, '0') == ('1328', '1328'), 'zero-saving rank-mass control')
    changed = deepcopy(invoice)
    for rank, count in counts['fixed_targets'].items():
        changed['targets'][str(rank)] -= count
    missing_roots = price.margin(changed, audit.read('PRICE.json')['claim'])
    audit.require(F(missing_roots[1]) < 0, 'omitted root targets must lose')
    changed = deepcopy(invoice)
    for rank, count in counts['fixed_paid'].items():
        changed['paid'][str(rank)] -= count
    missing_paid = price.margin(changed, audit.read('PRICE.json')['bracket'][1])
    audit.require(F(missing_paid[0]) > 0, 'omitted caller charges must change upper-point sign')
    return dict(closed_form_rank4_half=True, zero_saving_surplus=1328,
                missing_roots_at_claim=missing_roots, missing_fixed_paid_at_upper=missing_paid)


def calculate():
    for pin in json.loads((audit.ROOT / 'SOURCE-PINS.json').read_text()):
        raw = (audit.ROOT / pin['path']).read_bytes()
        audit.require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA-256 differs')
        audit.require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
                      == pin['git_blob'], 'source Git blob differs')
    raw = gzip.decompress((audit.ROOT / 'CERTIFICATE.json.gz').read_bytes())
    certificate = json.loads(raw)
    results, primal_equations, multipliers, rejected = [], 0, 0, 0
    for case, item in zip(audit.cases(), certificate, strict=True):
        role, variant, restriction, split, g0, g = case
        audit.require((item['role'], item['variant']) == (role, variant), 'certificate case differs')
        result = audit.check_case(g0, g, restriction, split, item)
        results.append(result)
        primal_equations += len(g0['forms']) + 3 * len(g['forms'])
        multipliers += sum(len(item[k]['multipliers']) for k in ('restriction', 'readout', 'calibration'))
        multipliers += len(item['restriction_identity']['row']['multipliers']) + len(item['split_identity']['row']['multipliers'])
        if role == 1409 and variant == 'chosen':
            rejected = controls(g0, g, restriction, split, item)
    expected = audit.read('results/witness.json')['alternate_restrictions']
    actual = []
    for result in results:
        if result['variant'] == 'alternate':
            failures = {k: dict(coordinates=v['coordinates'], first_coordinate=v['first_coordinate'],
                                actual=v['difference'], required='0') for k, v in result['failures'].items()}
            actual.append(dict(restriction=result['restriction'], split=result['split'], failures=failures))
    audit.require(actual == expected, 'published counterexamples differ')
    invoice, counts = price.invoice()
    result = dict(cases=results, invoice=invoice, counts=counts, prices=price.verify_prices(invoice),
                  controls=dict(rejected_certificates=rejected, price=price_controls(invoice, counts)),
                  certificate_sha256=hashlib.sha256(raw).hexdigest(),
                  certificate_counts=dict(dual_identities=30, primal_solutions=24,
                                          primal_equations=primal_equations, nonzero_multipliers=multipliers))
    return json.loads(json.dumps(result))


def main():
    actual = calculate()
    expected = json.loads((audit.ROOT / 'RESULT.json').read_text())
    audit.require(actual == expected, 'published audit receipt differs')
    print('PASS_INTERLEAVED_BASIS_RESIDUAL_AUDIT', actual['certificate_counts'], '96512 paid 17296 productive')


if __name__ == '__main__':
    main()
