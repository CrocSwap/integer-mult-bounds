"""Exact changed-demand p16 bill and all-subset relative moment bound.

Apache-2.0; substantial OpenAI Codex assistance. This rejects the returned
invoice, not every candidate or the optional solver model.
"""
from collections import Counter
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(value, message):
    if not value:
        raise ValueError(message)


def inputs():
    word = json.loads((ROOT / 'research/joint-helper-lattice/CONTROLLER.json').read_text())
    source = json.loads((ROOT / 'research/kappa-round3-warp-20261022/ARITHMETIC.json').read_text())
    return word, source


def profiles(changed):
    word, source = inputs()
    changed = set(changed)
    full = {e[1] for e in word['physical_events'] if e[0] == 'LOCAL'}
    need(changed <= full, 'Only original full stages change')
    p, h = Counter(), Counter()
    local_p = Counter({int(k): v for k, v in source['local_paid'].items()})
    local_h = Counter({int(k): v for k, v in source['local_helpers'].items()})
    for e in word['physical_events']:
        if e[0] == 'LOCAL':
            p.update(local_p)
            h.update(local_h)
            if e[1] in changed:
                p[1] += 120
        elif e[0] == 'QUERY_SHEAR':
            p[1] += 112
        elif e[0] == 'IDLE':
            r = 8 * len(e[2])
            drop = len(changed.intersection(e[2]))
            if r:
                p[r] += 104
                p[r - drop] += 120
    for term in word['diagonal']:
        stages = {i for i, value in enumerate(term[1:]) if value}
        r = 1 + 8 * len(stages)
        h[r] += 52
        h[r - len(stages.intersection(changed))] += 60
    return p, h


def all_subset_bound():
    word, _ = inputs()
    stages = sorted({e[1] for e in word['physical_events'] if e[0] == 'LOCAL'})
    counts = []
    for s in stages:
        main = sum(bool(term[s + 1]) for term in word['diagonal'])
        idle = sum(s in e[2] for e in word['physical_events'] if e[0] == 'IDLE')
        need(main - 2 * idle == 2, 'Exact stage multiplicity conservation')
        counts.append((s, main, idle))
    need(len(stages) == 18 and max(i for _, _, i in counts) <= 15,
         'Actual p16 full-stage and idle incidence bounds')
    # exp(5)>145 from the positive finite exponential Taylor polynomial.
    factorial = 1
    lower = Q(1)
    for n in range(1, 13):
        factorial *= n
        lower += Q(5 ** n, factorial)
    need(lower > 145, 'Exact log145<5 certificate')
    C = Q(17, 5000)
    derivative_lower = (1 - C) * (1 - 5 * C)
    need(derivative_lower > Q(97, 100), 'Rank-power derivative lower bound')
    # For every C in[0,.0034], every r in[1,145], r^(1-C) has
    # derivative in[alpha,1]. Charge native120 per changed stage and
    # conserve main-idle incidence. This applies to every subset together.
    alpha = Q(97, 100)
    loss = 120 * (1 + alpha - (1 - alpha) * max(i for _, _, i in counts))
    need(loss > 0, 'Every nonempty stage subset strictly worsens margin')
    return dict(stage_incidences=counts, saving_interval=['0', str(C)],
                derivative_lower=str(derivative_lower),
                proved_relative_margin_loss_per_changed_stage=str(loss),
                applies_to='Returned source+120H1 local invoice only, retaining all helpers; arbitrary subsets of the18 fixed p16 full stages.')


def run():
    word, source = inputs()
    p0, h0 = profiles([])
    need(p0 == Counter({int(k): v for k, v in source['paid'].items()}) and
         h0 == Counter({int(k): v for k, v in source['targets'].items()}),
         'Literal source p16 invoice')
    spec = importlib.util.spec_from_file_location(
        'partial_stage_intervals', ROOT / 'research/higher-moment-strictification/verify.py')
    E = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(E)
    C = Q('.00302177585')
    def margin(p, h):
        P, H = E.moment(p, 1 - C), E.moment(h, 1 - C)
        return [str(H[0] - P[1]), str(H[1] - P[0])]
    rows = []
    stages = sorted({e[1] for e in word['physical_events'] if e[0] == 'LOCAL'})
    for changed in ([s] for s in stages):
        p, h = profiles(changed)
        value = margin(p, h)
        need(Q(value[1]) < 0, 'Returned partial-stage profile fails complete moment')
        rows.append(dict(stages=changed, margin=value))
    bound = all_subset_bound()
    p, h = profiles(stages)
    report = dict(status='PASS_RETURNED_HETEROGENEOUS_INVOICE_REJECTION',
                  source_margin=margin(p0, h0), single_stage_margins=rows,
                  all_stages_margin=margin(p, h), all_subset_bound=bound,
                  all_stages_paid=dict(sorted(p.items())),
                  all_stages_targets=dict(sorted(h.items())),
                  scope='Exact price rejection of the returned invoice, not a solver optimum or native admission.')
    return report


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
