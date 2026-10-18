#!/usr/bin/env python3
"""Reproduce the scoped PR933/PR1392 continuation comparison, offline.

Hanson Sun with substantial OpenAI Codex assistance. Apache-2.0.
No selected-supplier exclusion or kappa improvement is claimed.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import independent as I

BASE = ((1, 2), (2, 3), (6, 2))
BETTER = ((1, 1), (2, 3), (6, 1), (7, 1))
WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def source_checks():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for item in manifest['files'] + manifest['external_sources']:
        if item.get('usage') == 'provenance':
            continue  # Historical Git provenance is checked by research_package.py.
        path = (ROOT if item.get('usage') == 'input' else HERE) / item['path']
        data = path.read_bytes()
        I.require(hashlib.sha256(data).hexdigest() == item['sha256'], 'source SHA256 mismatch: ' + item['path'])
        git_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        I.require(git_blob == item['git_blob'], 'source Git blob mismatch: ' + item['path'])
    return manifest


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def predecessor_tools():
    # Only authenticated source is imported. Original files are byte-identical.
    r = load('reframe', HERE / 'vendor/pr933/reframe.py')
    s = load('search', HERE / 'vendor/pr933/search.py')
    p = load('pairs', HERE / 'vendor/pr933/pairs.py')
    c = load('concordance_coverage', HERE / 'vendor/pr1392/coverage.py')
    return r, s, p, c


def convert(move):
    return (move[1], move[2], move[4] if len(move) == 6 else move[1], move[-1])


def predecessor_census(raw, r, s, p, expected):
    word = r.Word(raw)
    first = s.candidates(word) + s.cross_candidates(word)
    I.require(sorted(map(convert, first)) == expected['first'], 'independent first move disagreement')
    rows = []
    profiles = Counter()
    for m1 in first:
        a, b = s.apply(word, m1)
        first_optimum = r.optimum(word, a, b, 0.5)
        I.require(first_optimum is not None and tuple(sorted(first_optimum['profile'].items())) == BASE,
                  'source first-order admission changed')
        view = p.View(word, a, b)
        after = I.apply(I.operations(raw), convert(m1))
        registers = set(I.operations(raw)[m1[1]][m1[2]][1:])
        second = s.candidates(view, p.moved_regs(word, m1)) + s.cross_candidates(view, p.moved_regs(word, m1))
        I.require(sorted(map(convert, second)) == I.moves(raw, after, quotient=True, registers=registers),
                  'independent second move disagreement')
        for m2 in second:
            aa, bb = s.apply(view, m2)
            # Observe the unmodified source's chosen output at z=1/2. The exact
            # acceptance below is the separate all-frame majorization check.
            observed = r.optimum(word, aa, bb, 0.5)
            I.require(observed is not None, 'unexpected source frame rejection')
            profile = tuple(sorted(observed['profile'].items()))
            profiles[profile] += 1
            end = I.apply(after, convert(m2))
            rows.append((convert(m1), convert(m2), I.order_key(end)))
    I.require(sorted(rows) == sorted(expected['pairs']), 'source pair transcript mismatch')
    I.require(profiles == Counter({BASE: 101}), 'source synthetic result changed')
    # Also invoke the original pair worker, not just its constituent routines.
    p._W, p._Z = word, 0.5
    driver_rows = p._eval(first)
    driver_profiles = Counter()
    for _, _, _, _, observed_profiles in driver_rows:
        driver_profiles.update(observed_profiles)
    I.require(len(driver_rows) == 10 and sum(row[1] for row in driver_rows) == 101
              and sum(row[2] for row in driver_rows) == 101
              and driver_profiles == Counter({BASE: 101}), 'unmodified pair worker disagreement')
    return {'first_moves': len(first), 'pairs': len(rows),
            'original_pair_worker_rows': len(driver_rows), 'original_pair_worker_legal_pairs': 101,
            'observed_optimal_profiles': [[list(k), n] for k, n in sorted(profiles.items())],
            'pair_transcript_sha256': digest(sorted(rows)), 'observation_exponent': '1/2'}


def small_result(raw, r, s, p):
    quotient = I.census(raw, True)
    literal = I.census(raw, False)
    I.require((len(quotient['first']), len(quotient['pairs'])) == (10, 101), 'quotient coverage changed')
    I.require((len(literal['first']), len(literal['pairs'])) == (16, 194), 'literal coverage changed')
    I.require(all(I.majorizes(BASE, h) for h in quotient['single_profiles'] + quotient['pair_profiles']),
              'a quotient frame assignment beats the proposed baseline bound')
    I.require(all(I.majorizes(BASE, h) for h in literal['single_profiles']), 'fixture has a one-move escape')
    I.require(BETTER in literal['pair_profiles'] and not I.majorizes(BASE, BETTER),
              'literal two-move strict-improvement witness missing')
    I.require(I.majorizes(BETTER, BASE), 'strict merge dominance')
    I.require(sum(r*n for r, n in BASE) == sum(r*n for r, n in BETTER) == 20, 'rank mass')
    first = ('B', 1, 'B', 4)
    after = I.apply(I.operations(raw), first)
    second = ('B', 0, 'B', 3)
    final = I.apply(after, second)
    I.require(first in literal['first'] and first not in quotient['first'], 'omitted first position')
    I.require(second in I.moves(raw, after, quotient=False, registers={16, 17}), 'literal continuation')
    I.require(BETTER in I.frame_profiles(raw, final), 'attaining final order')
    # Every input is an independent dirty variable; helpers must restore.
    baseline = I.scalar_endpoint(raw)
    endpoint = I.scalar_endpoint(raw, {sec: [(t, (u,)) for _, t, u in final[sec]] for sec in 'AB'})
    expected = [1 << i for i in range(19)]
    for target in (8, 9, 10):
        expected[target] ^= 1 << 18
    I.require(baseline == endpoint == expected, 'synthetic full dirty endpoint')
    observed = predecessor_census(raw, r, s, p, quotient)
    return {'dimension': 8, 'registers': 19, 'gates': 5, 'all_dirty_columns': 19,
            'baseline_profile': BASE, 'attaining_profile': BETTER,
            'delta': [[1, -1], [6, -1], [7, 1]],
            'strict_cost_sign': '7^p - 6^p - 1 < 0 for 0 < p < 1',
            'child_count_delta': -1, 'first_move': first, 'second_move': second,
            'final_order': I.order_key(final), 'attaining_gate_masks': [3, 3, 3, 255, 255],
            'source_observation': observed,
            'independent': {name: {'first_moves': len(data['first']), 'pairs': len(data['pairs']),
                                  'distinct_orders_including_baseline': data['orders'],
                                  'all_legal_frame_assignments': data['frame_assignments'],
                                  'single_profiles': data['single_profiles'],
                                  'pair_profiles': data['pair_profiles'],
                                  'pair_transcript_sha256': digest(sorted(data['pairs']))}
                            for name, data in [('quotient', quotient), ('literal', literal)]}}


def itineraries(state):
    touches = {}
    for sec in 'AB':
        for frame, t, u, oid in state.sections[sec]:
            for reg in (t, u):
                touches.setdefault(reg, []).append((oid, frame))
    return {str(r): seq for r, seq in touches.items()}


def real_result(word, r, s, c):
    frames = c.Frames(word)
    base = c.State(word, frames)
    x, y = ('A', 250), ('A', 18)
    mask = 512
    I.require(base.sections['A'][250][1:3] == (243, 9), 'actual x identity')
    I.require(base.sections['A'][18][1:3] == (240, 9), 'actual y identity')
    I.require(any(q == 243 and f == mask for q, f, _ in c.legal_moves(base, x)), 'actual first legality')
    after = base.moved(x, 243, mask)
    I.require(itineraries(base) == itineraries(after), 'actual first itinerary equivalence')
    I.require(any(q == 243 and f == mask for q, f, _ in c.legal_moves(after, y)), 'actual second legality')
    final = after.moved(y, 243, mask)
    source = r.Word(word)
    op = source.A[250]
    rest = source.A[:250] + source.A[251:]
    representatives = s.slots(rest, op, 250)
    I.require(250 in representatives and 243 not in representatives, 'PR933 actual omitted position')
    # y cannot pass original A[244] = (482 <- 240), before original x.
    blocker = base.sections['A'][244]
    I.require(blocker[1:3] == (482, 240) and not c.commute(base.sections['A'][18], blocker),
              'actual noncommuting blocker')
    ys = c.legal_moves(base, y)
    I.require(all(q <= 244 for q, _, _ in ys), 'actual blocked baseline continuation')
    source9_final = [oid for _, t, u, oid in final.sections['A'] if 9 in (t, u)]
    I.require(source9_final.index(x) < source9_final.index(y), 'actual missing continuation order')
    scalar = []
    invoices = []
    for state in (base, after, final):
        framed = state.sections
        profile, copies = I.framed_profile(word, framed)
        I.require(copies == base.cp, 'actual COPY pins')
        I.require(dict(profile) == state.profile(), 'independent actual invoice disagreement')
        sections = {sec: [(t, (u,)) for _, t, u, _ in framed[sec]] for sec in 'AB'}
        scalar.append(I.scalar_endpoint(word, sections))
        invoices.append(profile)
    expected = [(1 << i) ^ ((1 << (i-word['v'])) if word['v'] <= i < 2*word['v'] else 0)
                for i in range(len(word['start']))]
    I.require(all(e == expected for e in scalar), 'actual full 661-column dirty identity')
    I.require(invoices[0] == invoices[1] == invoices[2], 'actual control unexpectedly changes paid profile')
    return {'x': x, 'y': y, 'first_full_slot': 243, 'second_full_slot': 243,
            'frame_mask': mask, 'original_first_slot': 250, 'blocker': ['A', 244, 482, 240],
            'first_itinerary_sha256': digest(itineraries(base)),
            'final_itinerary_sha256': digest(itineraries(final)),
            'profile': invoices[0], 'copy_frames': sorted(base.cp.items()),
            'dirty_columns': len(expected), 'checked_full_words': 3,
            'endpoint_sha256': digest(expected),
            'status': 'different continuation; equal paid profile; no PR589 cost counterexample'}


def controls(raw, real, r, s, p, c):
    passed = []

    def reject(label, action):
        try:
            action()
        except (ValueError, AssertionError):
            passed.append(label)
        else:
            raise ValueError('negative control was accepted: ' + label)

    reject('false_quotient_cost_exclusion', lambda: I.require(I.majorizes(BASE, BETTER), 'wrong exclusion'))
    reject('unpaid_cleanup_climb', lambda: I.require(sum(r*n for r, n in ((1, 1), (2, 3), (7, 1))) == 20,
                                                    'missing six-rank cleanup charge'))
    reject('noncommuting_transport', lambda: I.require(('B', 0, 'B', 4) in I.moves(raw, I.operations(raw), quotient=False),
                                                     'crosses x'))
    reject('unrestored_dirty_helper', lambda: I.require(I.scalar_endpoint(raw, omit_last_cleanup=True) == I.scalar_endpoint(raw),
                                                     'omitted inverse'))
    damaged = copy.deepcopy(raw)
    damaged['lines'][1] = damaged['lines'][0]
    reject('wrong_geometry', lambda: I.frame_profiles(damaged, I.operations(damaged)))
    state = c.State(real, c.Frames(real))
    reject('actual_noncommuting_crossing', lambda: I.require(any(q == 251 for q, _, _ in c.legal_moves(state, ('A', 18))),
                                                           'crosses actual blocker'))
    bad = state.moved(('A', 250), 243, 544)
    reject('actual_frame_descent', lambda: I.framed_profile(real, bad.sections))
    reject('actual_missing_cleanup', lambda: I.require(I.scalar_endpoint(real, omit_last_cleanup=True) == I.scalar_endpoint(real),
                                                     'actual helper not restored'))
    # With two forced-low readers the representative search really does see a
    # cheaper pair: it moves both readers before y. This is a positive control.
    two = copy.deepcopy(raw)
    two['B'].pop()
    two['final'][10] = 0
    result = I.census(two, True)
    two_base = ((1, 2), (2, 2), (6, 2))
    two_better = ((1, 1), (2, 2), (6, 1), (7, 1))
    I.require(two_better in result['pair_profiles'] and I.majorizes(two_better, two_base),
              'two-reader positive escape was not detected')
    source_two = r.Word(two)
    observed = set()
    for m1 in s.candidates(source_two) + s.cross_candidates(source_two):
        aa, bb = s.apply(source_two, m1)
        view = p.View(source_two, aa, bb)
        regs = p.moved_regs(source_two, m1)
        for m2 in s.candidates(view, regs) + s.cross_candidates(view, regs):
            aaa, bbb = s.apply(view, m2)
            opt = r.optimum(source_two, aaa, bbb, 0.5)
            if opt is not None:
                observed.add(tuple(sorted(opt['profile'].items())))
    I.require(two_better in observed, 'unmodified source missed positive two-reader control')
    passed.append('two_reader_positive_escape')
    return passed


def run():
    manifest = source_checks()
    r, s, p, c = predecessor_tools()
    raw = json.loads((HERE / 'fixtures/five-gate.json').read_text())
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    result = {'schema_version': 1, 'status': 'SCOPED_CONTINUATION_CONCORDANCE',
              'base_commit': manifest['base_commit'],
              'source_heads': sorted({row['commit'] for row in manifest['external_sources']}),
              'synthetic': small_result(raw, r, s, p), 'pr589': real_result(word, r, s, c),
              'controls': controls(raw, word, r, s, p, c), 'kappa': 'unchanged'}
    return json.loads(canonical(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-receipt', type=Path, help='explicitly generate a receipt at this path')
    args = parser.parse_args()
    result = run()
    if args.write_receipt:
        args.write_receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        expected = json.loads((HERE / 'CERTIFICATE.json').read_text())
        I.require(canonical(expected) == canonical(result), 'certificate does not match reconstructed evidence')
    print('PASS_TRANSPORT_CONCORDANCE quotient_pairs=101 literal_pairs=194 dirty_columns=19+661 controls=9 kappa=unchanged')


if __name__ == '__main__':
    main()
