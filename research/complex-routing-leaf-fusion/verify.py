#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only complete-word/hosting replay for the credited frame composition.

Predecessor algorithms retain their notices in vendor/pr2751. The new generator
changes one frame in each complete word. Native/outer admission is separate.
Prepared for David Arias with substantial OpenAI Codex assistance.
"""
import copy
from fractions import Fraction
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'vendor/pr2751'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def module(name, path):
    # Compile the authenticated bytes, never a possibly stale bytecode cache.
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), 'exec'), result.__dict__)
    return result


def authenticate():
    pins = read(HERE / 'PREDECESSOR.json')
    need(pins['head'] == '4cfbb0cc8314d7fb4e8e754545a49a42eb590a69', 'predecessor head')
    need(pins['root'] == 'vendor/pr2751', 'predecessor root')
    for name, entry in pins['files'].items():
        path = SOURCE / name
        need(path.is_file() and not path.is_symlink(), 'predecessor file ' + name)
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == entry['sha256'], 'predecessor SHA256 ' + name)
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == entry['git_blob'], 'predecessor Git blob ' + name)
    return len(pins['files'])


def rejects(fn, label):
    try:
        fn()
    except (AssertionError, ValueError, RuntimeError):
        return
    raise ValueError('accepted negative control: ' + label)


def run():
    need(__debug__, 'run without -O: retained symbolic checker uses assertions')
    authenticated = authenticate()
    G = module('frame_composition_generator', HERE / 'generate.py')
    L = module('pr2751_literal', SOURCE / 'independent_local.py')
    I = module('pr2751_owners', SOURCE / 'independent_owners.py')
    C = module('pr2751_composition', SOURCE / 'composition.py')
    M = module('pr2751_moment', SOURCE / 'exact_moment.py')
    words, reports = {}, {}
    controls = []
    for tag, provider in (('base', 'gauge44'), ('extra', 'extra')):
        old = read(SOURCE / f'inputs/WORD-{tag}.json.gz')
        word = read(HERE / f'inputs/WORD-{tag}.json.gz')
        need(word == G.patch(old), 'complete generated word equality: ' + tag)
        old_frames, old_start, old_end = L.check_frames(old)
        frames, start, end = L.check_frames(word)
        need(start == old_start and end == old_end, 'unchanged complete boundary frames')
        need(frames['inventory'] == old_frames['inventory'], 'unchanged helper stock')
        need(L.check_cleanup(word) == L.check_cleanup(old), 'unchanged cleanup length')
        need(word['cleanup'] == old['cleanup'], 'byte-semantic unchanged cleanup')
        L.algebra(word)
        words[provider] = word
        reports[provider] = frames
        # Retain the predecessor's actual arbitrary-dirty-input failure controls.
        for label in ('drop_anticipatory', 'reverse_anticipatory', 'reverse_recovery'):
            bad = copy.deepcopy(word)
            if label == 'drop_anticipatory':
                bad['initial_corrections'].pop()
            elif label == 'reverse_anticipatory':
                bad['initial_corrections'][0]['coefficient'] = str(-Fraction(bad['initial_corrections'][0]['coefficient']))
            else:
                index = next(i for i, gate in enumerate(bad['B']) if gate[:5] == ['add', 49, 33, -1, 1])
                bad['B'][index][3] = 1
            rejects(lambda: L.algebra(bad), tag + ':' + label)
            controls.append(tag + ':' + label)
        # Pricing an unchanged source word as if it contained the refit is false.
        bad = copy.deepcopy(old)
        bad['report']['local_profile'] = copy.deepcopy(word['report']['local_profile'])
        rejects(lambda: L.check_frames(bad), tag + ':omitted_refit')
        controls.append(tag + ':omitted_refit')

    def inp(name):
        return read(SOURCE / 'inputs' / name)

    providers = inp('PROVIDERS.json')
    for provider, word in words.items():
        providers[provider]['actual_paid_profile'] = word['report']['local_profile']
    order, fill = inp('ORDER.json'), inp('FILL.json.gz')
    dispatch = {(s, r): p for s, r, p in inp('DISPATCH.json.gz')}
    need(order == inp('SOURCE-ORDER.json'), 'unchanged entire call order')
    reconstructed, _, _ = C.transform(inp('SOURCE-PROVIDERS.json'), providers,
                                      inp('SOURCE-FILL.json.gz'), order, dispatch, words)
    need(reconstructed == fill, 'unchanged complete physical allocation')
    profile = {int(k): v for k, v in read(HERE / 'PROFILE.json').items()}
    old_profile = {int(k): v for k, v in read(SOURCE / 'PROFILE.json').items()}
    expected = dict(old_profile)
    expected[1] -= 1332
    expected[2] += 666
    need(profile == expected, 'complete global delta 666*(H2-2H1)')
    owner = I.check(inp('PLAN.json.gz'), inp('GLOBAL-TEMPLATE.json.gz'), order,
                    fill, providers, dispatch, profile)
    bad_fill = copy.deepcopy(fill)
    bad_fill['rows'][0][5] = 999
    rejects(lambda: I.check(inp('PLAN.json.gz'), inp('GLOBAL-TEMPLATE.json.gz'),
                            order, bad_fill, providers, dispatch, profile), 'out_of_bin')
    controls.append('out_of_bin')
    rejects(lambda: I.check(inp('PLAN.json.gz'), inp('GLOBAL-TEMPLATE.json.gz'),
                            order, fill, providers, dispatch, old_profile), 'old_profile')
    controls.append('old_profile')
    claim = read(HERE / 'CLAIM.json')
    low, high = Fraction(claim['complex_lower']), Fraction(claim['complex_upper'])
    need(low == Fraction('0.001717256973467002308270') and high-low == Fraction(1, 10**24),
         'claim exact adjacent endpoint binding')
    need({int(k): v for k, v in claim['profile'].items()} == profile, 'claim complete profile binding')
    need(Fraction(claim['kappa']) == low-Fraction(1, 10**46)-Fraction(1, 10**70),
         'claim modern outer target binding')
    need(Fraction(claim['kappa']) > Fraction(read(SOURCE/'CLAIM.json')['kappa']),
         'strict improvement over source target')
    _, lower_hi = M.moment_bounds(profile, low)
    upper_lo, _ = M.moment_bounds(profile, high)
    source_lo, _ = M.moment_bounds(old_profile, low)
    need(lower_hi < 66304 < upper_lo and source_lo > 66304,
         'retained independent interval engine root and strict source comparison')
    return dict(status='PASS_COMPLETE_FRAME_COMPOSITION', authenticated_files=authenticated,
                providers=reports, roles=owner['roles'], calls=len(order),
                profile={str(k): v for k, v in sorted(profile.items())},
                rank_mass=sum(k*v for k, v in profile.items()), controls=controls,
                complex_lower=str(low), complex_upper=str(high), kappa=claim['kappa'],
                scope='Complete finite words and allocation; fresh native and outer release are separate.')


if __name__ == '__main__':
    actual = run()
    expected = read(HERE / 'RESULT.json')
    canonical = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':'))
    need(canonical(actual) == canonical(expected), 'complete typed RESULT.json equality')
    print(json.dumps(actual, sort_keys=True, indent=2))
