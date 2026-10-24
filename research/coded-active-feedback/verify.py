#!/usr/bin/env python3
"""Exact active coefficient, retained coupling, and bounded search replay.

Cinna Davis, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
from hashlib import sha256
import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import types

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
m = types.ModuleType('active_feedback_search')
m.__file__ = str(HERE / 'search.py')
exec(compile((HERE / 'search.py').read_bytes(), m.__file__, 'exec'), m.__dict__)


def canonical(value):
    return json.dumps(value, separators=(',', ':'), sort_keys=True).encode()


def serialized(row):
    return [[[list(w), list(d), str(v)] for (w, d), v in sorted(entry.items())]
            for entry in row]


def rejected(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError('Corrupt certificate accepted')


def run_search(directory, full=False):
    out = Path(directory) / ('full.json' if full else 'pilot.json')
    flags = ['-O'] if sys.flags.optimize else []
    command = [sys.executable, '-I', *flags, '-B', str(HERE / 'search.py'),
               '--length', '7' if full else '1',
               '--decoder-length', '7' if full else '3',
               '--coefficients=-2,-1,-1/2,1/2,1,2' if full else '--coefficients=-1,1',
               '--output', str(out)]
    if not full:
        command.append('--certificates')
    subprocess.run(command, capture_output=True, text=True, check=True, timeout=540)
    return json.loads(out.read_text())


def run(full=False):
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    inputs = [entry for entry in sources['files'] if entry['usage'] == 'input']
    m.need(len(inputs) == 4, 'Four source inputs')
    for entry in inputs:
        m.need(sha256((ROOT / entry['path']).read_bytes()).hexdigest() == entry['sha256'],
               'Changed inherited source: ' + entry['path'])
    a = m.algebra()
    q, c, e = a.gen(1), a.gen(2), a.gen(3)
    qi, d, f = a.inv(q), a.D(0), a.D(1)
    m.need(a.mul(q, q, q, q) == a.one and a.mul(q, q) != a.one, 'Q has order four')
    m.need(a.mul(c, c) == a.one and a.mul(e, e) == a.one, 'Source involutions')
    m.need(a.mul(c, d, q) == a.mul(d, q, c), 'Own DQ commutation')
    m.need(a.mul(c, f) == a.mul(f, c), 'Other-stage D commutation')
    m.need(a.mul(c, d) != a.mul(d, c) and a.mul(c, q) != a.mul(q, c),
           'Forbidden commutations remain absent')
    fixtures = 0
    for n in range(5):
        for word in itertools.product((-3, -2, -1, 1, 2, 3), repeat=n):
            reduced = m.reduce_word(word)
            m.need(m.reduce_word(reduced) == reduced, 'Reduction idempotence')
            for k in range(n + 1):
                m.need(m.reduce_word(m.reduce_word(word[:k]) + m.reduce_word(word[k:])) == reduced,
                       'Concatenation normal form')
            fixtures += 1
    observed, targets, _ = m.replay(a, a.one, a.mul(c, q, q))
    row = dict(observed)['query4:3']
    coupling = a.mul(qi, c, q, a.add(a.one, a.neg(q)), d)
    expected = [a.mul(d, qi), coupling,
                a.add(a.mul(a.add(a.mul(qi, c, q, c), a.neg(qi)), d),
                      a.mul(qi, e, d, f)), {}]
    m.need(row == expected, 'All four original-input coefficients')
    m.need(row[0] == targets[0][0] and coupling and row != targets[0],
           'Recovered coefficient is not an autonomous output')
    for first, second in (({}, {}), (a.one, c), (a.one, a.mul(e, q, q))):
        variant, _, _ = m.replay(a, first, second)
        m.need(dict(variant)['query4:3'][0] != targets[0][0],
               'Unchanged input / omitted Pauli / wrong stage code must fail')
    _, plain_targets, plain_rows = m.replay(a, {}, {}, codes=False)
    m.need(plain_rows == plain_targets, 'Full uncoded four-job positive control')
    residues = [1, 0, 0, 0]
    coupling_ranks = []
    for width in range(1, 65):
        residues = [residues[k] + residues[(k - 1) % 4] for k in range(4)]
        b0 = sum(math.comb(width, k) for k in range(0, width + 1, 4))
        m.need(b0 == residues[0], 'Independent central eigenvalue count')
        if width <= 12:
            m.need(sum(x.bit_count() % 4 == 0 for x in range(1 << width)) == b0,
                   'Direct central frequency enumeration')
        rank = 112 * (1 << (16 * width)) * ((1 << width) - b0)
        m.need(rank > 0, 'Coupling at every checked positive width')
        coupling_ranks.append({'width': width, 'central_eigenvalue_one': b0,
                               'complex_rank': str(rank)})
    retained = json.loads(gzip.decompress((HERE / 'SEARCH.json.gz').read_bytes()))
    choices = [(None, '0')] + [(list(w), z) for w in m.words(7)
               for z in ('-2', '-1', '-1/2', '1/2', '1', '2')]
    policies = {(json.dumps(w1), z1, json.dumps(w2), z2)
                for (w1, z1), (w2, z2) in itertools.product(choices, repeat=2)}
    actual = {(json.dumps(x['feedback1']), x['coefficient1'],
               json.dumps(x['feedback2_before_Pauli']), x['coefficient2'])
              for x in retained['cases']}
    m.need(len(actual) == len(retained['cases']) == 8281 and actual == policies,
           'Exact full search policy domain')
    m.need(all(x['attained'] == [False, True, False, False] for x in retained['cases'])
           and retained['attainment_histogram'] == {'1': 8281}, 'Retained search outcome')
    with tempfile.TemporaryDirectory(prefix='active-feedback-') as tmp:
        pilot = run_search(tmp)
        m.need(len(pilot['cases']) == 49 and pilot['attainment_histogram'] == {'1': 49},
               'Forty-nine exact certified pilot policies')
        baseline = pilot['cases'][0]['recipes']
        obs, t, _ = m.replay(a, {}, {})
        controls = [tuple(w) for w in pilot['decoder_controls']]
        rejected(lambda: m.verify_answer(a, obs, t[0], controls,
                 dict(baseline[0], target_pairing='0')))
        rejected(lambda: m.verify_answer(a, obs, t[1], controls,
                 dict(baseline[1], recipe=[])))
        if full:
            m.need(run_search(tmp, full=True) == retained, 'Every full-search policy and rank')
            print('PASS_FULL_ACTIVE_FEEDBACK_SEARCH 8281 policies')
    return {'status': 'PASS_ACTIVE_FEEDBACK_COMPONENT_AND_CERTIFIED_PILOT',
            'normal_form_fixtures': fixtures, 'complete_active_output_row': serialized(row),
            'coupling_ranks': coupling_ranks,
            'pilot_policies': 49, 'direct_span_certificates': 196,
            'pilot_canonical_sha256': sha256(canonical(pilot)).hexdigest(),
            'full_search_policies': 8281,
            'full_search_canonical_sha256': sha256(canonical(retained)).hexdigest(),
            'autonomous_Gaussian_job': False, 'physical_impossibility_claim': False,
            'new_kappa': None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--full-search', action='store_true')
    args = parser.parse_args()
    result = run(args.full_search)
    if args.write:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        m.need(json.loads((HERE / 'RESULT.json').read_text()) == result, 'Changed result receipt')
    print(result['status'])


if __name__ == '__main__':
    main()
