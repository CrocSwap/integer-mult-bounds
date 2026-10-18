"""Phase-local one-helper dyadic gauges; Philipp / OpenAI Codex, Apache-2.0."""
import argparse
from collections import defaultdict
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'dadfea6e8a78ff6ba901705f87532a71c6f5bbb8'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def sha(x):
    return hashlib.sha256(x).hexdigest()


def engine():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    need(pins['base'] == BASE, 'base pin')
    need(set(pins['vendor']) == {'engine.py', 'SOURCES.json', 'BASE-SELECTED.json',
                                'PROVENANCE.md', 'PROOF.md'}, 'vendor inventory')
    frame_checker = pins['frame_checker']
    need(frame_checker['path'] == 'research/complex-sw4-frame8/local/hpe_audit_local.py', 'frame checker path')
    need(sha((ROOT / frame_checker['path']).read_bytes()) == frame_checker['sha256'], 'frame checker pin')
    for name, digest in pins['vendor'].items():
        need(sha((HERE / 'vendor/pr1161' / name).read_bytes()) == digest, 'vendor pin ' + name)
    need(sha((HERE / 'vendor/pr1214/CERTIFICATE.json').read_bytes()) ==
         pins['pr1214_certificate_sha256'], 'PR1214 certificate pin')
    need(sha((HERE / 'vendor/pr1259/CERTIFICATE.json').read_bytes()) ==
         pins['pr1259_certificate_sha256'], 'PR1259 certificate pin')
    spec = importlib.util.spec_from_file_location('pr1161', HERE / 'vendor/pr1161/engine.py')
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)
    lib.ROOT = ROOT
    return lib


def terms(lib, events, helpers):
    """Partition by *all* non-scalar events, including wraps and phase markers."""
    result = {h: defaultdict(list) for h in helpers}
    run = 0
    for index, event in enumerate(events):
        if event[0] != 'scalar':
            run += 1
            continue
        gate = event[1]
        if gate[0] != 'add':
            continue
        p, e = lib.parts(lib.Q(gate[3], gate[4]))
        for role, sign in ((gate[1], 1), (gate[2], -1)):
            if role[0] == 'L' and role[1] in result:
                result[role[1]][run].append([index, -sign * e, p == 1])
    return result


def solve_run(rows, extra=0):
    """Integer shortest path; exact all-Z coverage follows the clipping lemma."""
    lo = min([0] + [r[1] for r in rows]) - extra
    hi = max([0] + [r[1] for r in rows]) + extra
    states = list(range(lo, hi + 1))
    dp = {0: 0}
    links = []
    baseline = 0
    for _, b, unit in rows:
        baseline += abs(b) - int(unit and b == 0)
        new, prev = {}, {}
        for k in states:
            value, _, j = min((v + abs(k - j), abs(j), j) for j, v in dp.items())
            new[k] = value + abs(k - b) - int(unit and k == b)
            prev[k] = j
        links.append(prev)
        dp = new
    best, _, k = min((v + abs(k), abs(k), k) for k, v in dp.items())
    path = []
    for back in reversed(links):
        path.append(k)
        k = back[k]
    path.reverse()
    return {'delta': best - baseline, 'bounds': [lo, hi], 'states': len(states),
            'path': path, 'vertices': len(rows) * len(states)}


def census(lib, events, helpers):
    all_terms = terms(lib, events, helpers)
    rows, schedules = [], {}
    for helper in helpers:
        delta, vertices, runs, plan = 0, 0, 0, []
        for run, stream in sorted(all_terms[helper].items()):
            answer = solve_run(stream)
            need(answer['delta'] <= 0, 'zero path available')
            delta += answer['delta']
            vertices += answer['vertices']
            runs += 1
            if any(answer['path']):
                plan.append({'run': run, 'terms': stream, **answer})
        rows.append([helper, delta, runs, vertices])
        schedules[helper] = plan
    winner = min(rows, key=lambda row: (row[1], row[0]))
    return {'helpers': len(helpers), 'rows': rows, 'helper': winner[0], 'delta': winner[1],
            'total_vertices': sum(row[3] for row in rows), 'schedule': schedules[winner[0]]}


def construct(lib, events, helper, schedule):
    before, after = {}, {}
    for run in schedule:
        previous = 0
        for term, exponent in zip(run['terms'], run['path']):
            index = term[0]
            if exponent != previous:
                before[index] = exponent - previous
            previous = exponent
        if previous:
            after[run['terms'][-1][0]] = -previous
    answer, k = [], 0

    def scale(exponent, frame):
        q = lib.power(exponent)
        return ['scalar', ['scale', ['L', helper], q.numerator, q.denominator], frame]

    for index, original in enumerate(events):
        event = copy.deepcopy(original)
        if event[0] != 'scalar':
            need(k == 0, 'gauge reset at every non-scalar boundary')
        if index in before:
            answer.append(scale(before[index], event[2]))
            k += before[index]
        if event[0] == 'scalar' and event[1][0] == 'add':
            g = event[1]
            shift = k * (int(g[1] == ['L', helper]) - int(g[2] == ['L', helper]))
            q = lib.Q(g[3], g[4]) * lib.power(shift)
            g[3:5] = [q.numerator, q.denominator]
        answer.append(event)
        if index in after:
            answer.append(scale(after[index], event[2]))
            k += after[index]
    need(k == 0, 'final gauge reset')
    return answer


def compute():
    lib = engine()
    word, programs, _, _ = lib.load()
    helpers, excluded = lib.domain(word, programs)
    receipt = {'base': BASE, 'seed': 26, 'status': 'PASS_K8_PHASE_LOCAL_GAUGES',
               'scope': 'one helper, all integer exponents, reset at every non-scalar event',
               'excluded_helpers': excluded, 'orientations': {}, 'on_pr1214': {}, 'wrapped_example': {}}
    witnesses = {}
    for orientation, events in programs.items():
        result = census(lib, events, helpers)
        candidate = construct(lib, events, result['helper'], result['schedule'])
        need([x for x in candidate if x[0] != 'scalar'] ==
             [x for x in events if x[0] != 'scalar'], 'non-scalar stream unchanged')
        result['baseline_endpoint'] = lib.replay(events, orientation)
        result['candidate_endpoint'] = lib.replay(candidate, orientation)
        before, after = lib.invoice(events, 'copy-init'), lib.invoice(candidate, 'copy-init')
        need(before['paid_profile'] == after['paid_profile'], 'recursive profile unchanged')
        need(after['real_primitives'] - before['real_primitives'] == result['delta'], 'full price agrees with DP')
        result['before'], result['after'] = before, after
        result['candidate_sha256'] = sha(canonical(candidate))
        result['inserted_scales'] = len(candidate) - len(events)
        receipt['orientations'][orientation] = result
        witnesses[orientation] = candidate
        wrapped = {event[2] for event in events if event[0] == 'residual_adapter'}
        wrapped_rows = [row for row in result['rows'] if row[0] in wrapped]
        need(len(wrapped_rows) == 240, 'wrapped helper domain')
        best_wrapped = min(wrapped_rows, key=lambda row: (row[1], row[0]))
        h = best_wrapped[0]
        stream = terms(lib, events, [h])[h]
        plan = []
        for run, rs in sorted(stream.items()):
            answer = solve_run(rs)
            if any(answer['path']):
                plan.append({'run': run, 'terms': rs, **answer})
        wrapped_word = construct(lib, events, h, plan)
        wrapped_price = lib.invoice(wrapped_word, 'copy-init')
        need(wrapped_price['real_primitives'] - before['real_primitives'] == best_wrapped[1],
             'wrapped candidate full invoice')
        need(wrapped_price['paid_profile'] == before['paid_profile'], 'wrapped profile')
        receipt['wrapped_example'][orientation] = {
            'helper': h, 'delta': best_wrapped[1], 'rows': [best_wrapped], 'schedule': plan,
            'wrapped_helpers_checked': 240, 'before': before, 'after': wrapped_price,
            'candidate_endpoint': lib.replay(wrapped_word, orientation),
            'candidate_sha256': sha(canonical(wrapped_word)),
            'inserted_scales': len(wrapped_word) - len(events)}
        witnesses['wrapped_' + orientation] = wrapped_word
        # Retain the predecessor's fixed two-helper witness, independently
        # reconstruct and price it; do not inherit its optimum as a new claim.
        pair_info = json.loads((HERE / 'vendor/pr1214/CERTIFICATE.json').read_text())
        pair_winner = pair_info['orientations'][orientation]['winner']
        pair = events
        for h, exponent in zip(pair_winner['helpers'], pair_winner['exponents']):
            pair = lib.transform(pair, word, h, exponent)
        pair_price = lib.invoice(pair, 'copy-init')
        need(canonical(pair_price) == canonical(pair_info['orientations'][orientation]['prices']['copy-init']['after']),
             'PR1214 independently reconstructed invoice')
        composed = census(lib, pair, helpers)
        final = construct(lib, pair, composed['helper'], composed['schedule'])
        composed['baseline_endpoint'] = lib.replay(pair, orientation)
        composed['candidate_endpoint'] = lib.replay(final, orientation)
        final_price = lib.invoice(final, 'copy-init')
        need(final_price['paid_profile'] == before['paid_profile'], 'composed profile unchanged')
        need(final_price['real_primitives'] - pair_price['real_primitives'] == composed['delta'],
             'composed full price agrees with DP')
        composed['before'], composed['after'] = pair_price, final_price
        composed['original_before'] = before
        composed['candidate_sha256'] = sha(canonical(final))
        composed['inserted_scales'] = len(final) - len(pair)
        receipt['on_pr1214'][orientation] = composed
        witnesses['pr1214_' + orientation] = final
    return receipt, witnesses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    receipt, _ = compute()
    path = HERE / 'CERTIFICATE.json'
    if args.write:
        path.write_bytes(canonical(receipt) + b'\n')
    else:
        need(canonical(receipt) == canonical(json.loads(path.read_text())), 'certificate mismatch')
    print(receipt['status'])
    for orientation, result in receipt['orientations'].items():
        print(orientation, 'helper', result['helper'], 'real saving', -result['delta'],
              'scales', result['inserted_scales'], 'helpers checked', result['helpers'])
    for orientation, result in receipt['on_pr1214'].items():
        print('on_pr1214', orientation, 'helper', result['helper'], 'extra per-component saving',
              -result['delta'], 'complete complex invoice', result['after']['complex_primitives'])
    for orientation, result in receipt['wrapped_example'].items():
        print('wrapped', orientation, 'helper', result['helper'], 'per-component saving', -result['delta'])


if __name__ == '__main__':
    main()
