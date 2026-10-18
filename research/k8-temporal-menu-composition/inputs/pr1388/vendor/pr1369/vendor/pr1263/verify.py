"""Many-coordinate k8 diagonal gauges; Philipp / GPT-6 Astra, Apache-2.0.

Reuses the byte-identical attributed PR1161 loader, scalar replay and invoice.
The joint objective and bounded discovery are new; no global optimum is claimed.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def engine():
    pins = json.loads((HERE / 'PREDECESSORS.json').read_bytes())
    expected_vendor = {'engine.py', 'SOURCES.json', 'BASE-SELECTED.json', 'PROVENANCE.md', 'PROOF.md'}
    need(set(pins['vendor']) == {'vendor/pr1161/' + name for name in expected_vendor}, 'complete vendor inventory')
    need(pins['pr1161_head'] == 'd210969d3158a1e6c505e41f67dd84e555c88564', 'PR1161 head')
    need(pins['pr1214_head'] == '26162c56ec9c50a80e49949f36d4dd9a137a76a6', 'PR1214 head')
    for path, digest in pins['vendor'].items():
        need(sha((HERE / path).read_bytes()) == digest, 'vendor pin ' + path)
    spec = importlib.util.spec_from_file_location('credited_pr1161', HERE / 'vendor/pr1161/engine.py')
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)
    lib.ROOT = ROOT
    return lib


def domain(lib, word, programs):
    helpers, _ = lib.domain(word, programs)
    wrapped = {event[2] for stream in programs.values() for event in stream
               if event[0] == 'residual_adapter'}
    result = [h for h in helpers if word['start'][h] == 0 and word['final'][h] == 1
              and h not in wrapped]
    need(len(result) == 237, '237 eligible helpers')
    return result


def terms_from(lib, events, helpers):
    allowed = set(helpers)
    terms = []
    for event in events:
        if event[0] != 'scalar' or event[1][0] != 'add':
            continue
        gate = event[1]
        p, exponent = lib.parts(lib.Q(gate[3], gate[4]))
        target, source = [r[1] if r[0] == 'L' and r[1] in allowed else -1 for r in gate[1:3]]
        if target != -1 or source != -1:
            need(target != source, 'distinct eligible ADD operands')
            terms.append((p == 1, exponent, target, source))
    return terms


def f(unit, exponent):
    return abs(exponent) - int(unit and exponent == 0)


def objective(terms, gauges):
    return 2 * sum(abs(k) for k in gauges.values()) + sum(
        f(u, e + gauges.get(t, 0) - gauges.get(s, 0)) - f(u, e) for u, e, t, s in terms)


def coordinate_candidates(terms, gauges, helper):
    incident = [term for term in terms if helper in term[2:]]
    points = {0, gauges.get(helper, 0)} | {
        gauges.get(s, 0) - e if t == helper else gauges.get(t, 0) + e
        for _, e, t, s in incident}

    def cost(value):
        return 2 * abs(value) + sum(f(u, e + (value if t == helper else gauges.get(t, 0))
                                      - (value if s == helper else gauges.get(s, 0)))
                                    for u, e, t, s in incident)
    return sorted((k, cost(k)) for k in points)


def discover(terms, helpers):
    """Four deterministic restarts, at most 50 complete sweeps per restart."""
    rng = random.Random(29)
    incident = {h: [term for term in terms if h in term[2:]] for h in helpers}
    records = []
    best = None
    for restart in range(4):
        gauges = {h: 0 if restart == 0 else rng.randint(-2, 2) for h in helpers}
        trace = []
        for sweep in range(50):
            order = helpers.copy()
            rng.shuffle(order)
            changes = 0
            for helper in order:
                points = coordinate_candidates(incident[helper], gauges, helper)
                chosen, value = min(points, key=lambda row: (row[1], abs(row[0]), row[0]))
                old = dict(points)[gauges[helper]]
                if value < old:
                    gauges[helper] = chosen
                    changes += 1
            trace.append([sweep, changes, objective(terms, gauges)])
            if changes == 0:
                break
        need(trace[-1][1] == 0, 'discovery completed before stopping cap')
        record = {'restart': restart, 'delta_real': objective(terms, gauges), 'trace': trace,
                  'gauges': {str(h): k for h, k in gauges.items() if k}}
        records.append(record)
        if best is None or record['delta_real'] < best['delta_real']:
            best = record
    return {'seed': 29, 'restarts': records, 'chosen_restart': best['restart']}, best['gauges']


def transform(lib, word, events, gauges):
    result = copy.deepcopy(events)
    for event in result:
        if event[0] != 'scalar':
            continue
        gate = event[1]
        if gate[0] == 'add':
            shift = sum(sign * gauges.get(r[1], 0) for sign, r in zip((1, -1), gate[1:3]) if r[0] == 'L')
            q = lib.Q(gate[3], gate[4]) * lib.power(shift)
            gate[3:5] = [q.numerator, q.denominator]
        elif gate[0] in ('copy', 'clear'):
            need(not any(isinstance(r, list) and r[0] == 'L' and r[1] in gauges for r in gate[1:]),
                 'no gauge on COPY/clear register')
    entry, exit_events = [], []
    for helper, k in sorted(gauges.items()):
        need(224 <= helper < 704 and helper not in word['centers'], 'helper domain')
        need(word['start'][helper] == 0 and word['final'][helper] == 1, 'cold/FULL helper')
        need(not any(e[0] == 'residual_adapter' and e[2] == helper for e in events), 'unwrapped helper')
        q = lib.power(k)
        entry.append(['scalar', ['scale', ['L', helper], q.numerator, q.denominator], 0])
        exit_events.append(['scalar', ['scale', ['L', helper], q.denominator, q.numerator], 1])
    need(result[0] == ['phase', 'zero_frame_precondition'] and result[-1] == ['phase', 'done'], 'phases')
    return result[:1] + entry + result[1:-1] + exit_events + result[-1:]


def compute():
    lib = engine()
    word, programs, _, _ = lib.load()
    helpers = domain(lib, word, programs)
    gauges_raw = json.loads((HERE / 'GAUGES.json').read_bytes())
    need(set(gauges_raw) == {'forward', 'backward'}, 'gauge orientations')
    forward_terms = terms_from(lib, programs['forward'], helpers)
    discovery, discovered = discover(forward_terms, helpers)
    need(discovered == gauges_raw['forward'], 'frozen forward gauges match bounded discovery')
    need({h: -k for h, k in discovered.items()} == gauges_raw['backward'], 'inverse gauges')
    certificate = {'seed': 29, 'base': 'dadfea6e8a78ff6ba901705f87532a71c6f5bbb8',
                   'eligible_helpers': helpers, 'discovery': discovery, 'orientations': {}}
    candidates = {}
    for orientation in ('forward', 'backward'):
        events = programs[orientation]
        gauges = {int(h): k for h, k in gauges_raw[orientation].items()}
        need(set(gauges) <= set(helpers) and all(type(k) is int and k != 0 for k in gauges.values()), 'gauge domain')
        candidate = transform(lib, word, events, gauges)
        need([e for e in events if e[0] != 'scalar'] == [e for e in candidate if e[0] != 'scalar'], 'paid event identity')
        terms = terms_from(lib, events, helpers)
        rows = []
        for h in helpers:
            points = coordinate_candidates(terms, gauges, h)
            old = dict(points)[gauges.get(h, 0)]
            need(min(value for _, value in points) == old, 'coordinate stationary')
            rows.append([h, points])
        before = lib.invoice(events, 'copy-init')
        after = lib.invoice(candidate, 'copy-init')
        need(after['real_primitives'] - before['real_primitives'] == objective(terms, gauges), 'complete invoice delta')
        need(before['paid_profile'] == after['paid_profile'], 'paid profile equality')
        certificate['orientations'][orientation] = {
            'support': len(gauges), 'boundary_real_primitives': 2 * sum(abs(k) for k in gauges.values()),
            'delta_real': objective(terms, gauges), 'baseline': before, 'candidate': after,
            'saving_complex': before['complex_primitives'] - after['complex_primitives'],
            'candidate_sha256': sha(canonical(candidate)), 'coordinate_checks': rows,
            'baseline_endpoint': lib.replay(events, orientation), 'candidate_endpoint': lib.replay(candidate, orientation),
            'horner_saving_complex': lib.invoice(events, 'horner')['complex_primitives'] - lib.invoice(candidate, 'horner')['complex_primitives']}
        candidates[orientation] = candidate
    certificate['status'] = 'PASS_MANY_HELPER_DYADIC_CONSTRUCTION'
    return certificate, candidates


def main():
    result, _ = compute()
    path = HERE / 'CERTIFICATE.json'
    if '--write' in sys.argv:
        need(not path.exists(), 'refusing to overwrite certificate')
        path.write_bytes(canonical(result) + b'\n')
    else:
        need(canonical(result) == canonical(json.loads(path.read_bytes())), 'complete certificate equality')
    print(result['status'])
    for orientation, row in result['orientations'].items():
        print(orientation, 'support', row['support'], 'saving_complex', row['saving_complex'],
              'before', row['baseline']['complex_primitives'], 'after', row['candidate']['complex_primitives'])


if __name__ == '__main__':
    main()
