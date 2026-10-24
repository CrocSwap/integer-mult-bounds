#!/usr/bin/env python3
"""Exact model/reported-invoice checks; no solver or native admission.

Apache-2.0; Cinna Davis / 1337isnot1337, substantial OpenAI Codex assistance.
"""
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as M


def independent_domains(space):
    points = {v for v in range(512) if space >> v & 1}
    images = ({0, 1, 2, 3}, {0, 2}, {0, 1}, {0, 3}, {0})
    return {frozenset(v for v in points if (v & 3) in image) for image in images}


def audit(model):
    payload = M.S.payload()
    source_paid = Counter(e[5] for e in payload['programs']['forward'] if e[0] == 'climb')
    source_paid.update(e[4] for e in payload['programs']['forward'] if e[0] == 'center')
    c = payload['canonical']
    source_helpers = Counter(len(c['frames'][v]) - len(c['frames'][u])
                             for u, v in zip(c['start'][224:], c['final'][224:]))
    M.need(M.invoice(model, {}) == (source_paid, source_helpers), 'Literal source bill')
    M.need(len(model['helpers']) == 408 and len(model['owned_copies']) == 8,
           'All helpers and owned lifetimes retained')
    for node in list(range(2, 226)) + list(range(len(model['nodes']) - 640,
                                               len(model['nodes']) - 416)):
        M.need(len(model['domains'][node]) == 1, 'Fixed main endpoints')
    centers = [(a, b, ranks) for kind, a, b, ranks in model['edges'] if kind == 'center']
    M.need(len(centers) == 8, 'Every full center charge retained')
    for a, b, ranks in centers:
        M.need(len(model['domains'][b]) == 1 and model['domains'][b][0] == 1,
               'Zero opposite center chart')
        M.need([r[0] for r in ranks] == [u.bit_count().bit_length() - 1
                                      for u in model['domains'][a]],
               'Full center rank, including every changed chart')
    return source_paid, source_helpers


def reject(call):
    try:
        call()
    except ValueError:
        return
    raise ValueError('Expected meaningful corruption rejection')


def main():
    model = M.build()
    paid, helpers = audit(model)
    distinct = set(M.S.M.mask(M.S.M.span(b)) for b in M.S.payload()['canonical']['frames'])
    for space in distinct:
        actual = {frozenset(v for v in range(512) if s >> v & 1)
                  for s in M.quotient_domains(space)}
        M.need(actual == independent_domains(space), 'All five quotient preimages')
    discovery = json.loads((M.HERE / 'DISCOVERY.json').read_text())
    assignment = {int(n): int(s) for n, s in discovery['assignment'].items()}
    p, h = M.invoice(model, assignment)
    M.need(p == paid and h == helpers, 'Returned complete histograms unchanged exactly')
    M.need(p == Counter({int(k): v for k, v in discovery['paid'].items()}) and
           h == Counter({int(k): v for k, v in discovery['helpers'].items()}),
           'Reported histograms match exact reassessment')
    M.need(any(model['domains'][n][s] != model['domains'][n][0]
               for n, s in assignment.items()), 'Witness changes a real contact')
    controls = 0
    for wrong in ({2: 1}, {-1: 0}, {len(model['nodes']): 0}, {11424: 99}):
        reject(lambda x=wrong: M.invoice(model, x))
        controls += 1
    broken = dict(model, edges=[e for e in model['edges'] if e[0] != 'center'])
    reject(lambda: audit(broken))
    controls += 1
    broken = dict(model, helpers=model['helpers'][:-1])
    reject(lambda: audit(broken))
    controls += 1
    broken = copy.deepcopy(model)
    center = next(e for e in broken['edges'] if e[0] == 'center')
    center[3][1][0] -= 1
    reject(lambda: audit(broken))
    controls += 1
    reject(lambda: M.quotient_domains(15, (1, 1), 2))
    controls += 1
    packed = json.dumps(dict(domains=[[str(s) for s in d] for d in model['domains']],
                             edges=model['edges'], helpers=model['helpers']),
                        separators=(',', ':')).encode()
    report = dict(status='PASS_EXACT_TWO_AXIS_MODEL_AND_REPORTED_BILL_ONLY',
                  model=M.summary(model), distinct_source_spaces=len(distinct),
                  table_sha256=hashlib.sha256(packed).hexdigest(),
                  paid=dict(sorted(p.items())), helpers=dict(sorted(h.items())),
                  changed_contacts=len(assignment), controls=controls,
                  scope='No exact optimality proof of numerical solver; no signed native endpoint or kappa admission.')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
