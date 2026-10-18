#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact composition checks; complete releases remain mandatory for PASS.

Geometry, frame accounting, cleanup and interval engines retain predecessor
credit. New here is their source-bound T148/PR3042 composition and its checks.
"""
import argparse
import copy
import gzip
import hashlib
import json
import sys
import types
from fractions import Fraction as Q
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
PROFILE = {1: 3275388, 2: 948384, 3: 318948, 4: 143856,
           5: 27416, 8: 10656, 32: 1, 48: 56380}
LOCAL = {1: 2433, 2: 712, 3: 232, 4: 108, 5: 18, 8: 8}
HEAD = '84cc406ad91ec53fff329a11a445d7effe564a77'
SOURCE_SHA = '130650ad8833f6df88528c560e4d1cfbae084f4b15a64788a332ddcaff472a17'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def authenticate():
    for row in read(P / 'SOURCES.json')['files']:
        if row.get('usage') == 'input':
            need(sha(ROOT / row['path']) == row['sha256'], 'input drift: ' + row['path'])
    for row in read(P / 'VENDOR.json'):
        need(row['head'] == HEAD and sha(P / row['path']) == row['sha256'], 'exact PR3042 input')


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def baseline_modules():
    directory = ROOT / 'research/rank7-t740-release'
    sys.path.insert(0, str(directory))
    materializer = load(directory / 'materialize.py', 'credited_materializer')
    geometry = load(directory / 'verify.py', 'credited_geometry')
    return materializer, geometry


def restore_action(gates):
    rows = [{r: Q(1)} for r in range(704)]
    for gate in gates:
        if gate[0] == 'add':
            _, target, source, n, d, _ = gate
            scale = Q(n, d)
            for key, value in list(rows[source].items()):
                result = rows[target].get(key, Q(0)) + scale * value
                if result:
                    rows[target][key] = result
                else:
                    rows[target].pop(key, None)
        else:
            need(gate[0] == 'scale', 'restore primitive')
            rows[gate[1]] = {k: Q(gate[2], gate[3]) * v for k, v in rows[gate[1]].items()}
    return rows


def check_word(old, new, frames):
    need(set(old) == set(new) and {k for k in old if old[k] != new[k]} <=
         {'restore', 'report', 'cleanup'}, 'declared restore-only source change')
    need(len(new['helper_final']) == 91 and new['helper_final'] == old['helper_final'] and
         new['start_extra'] == old['start_extra'], 'same ordered native endpoint/entrance widths and91 buffers')
    need(restore_action(old['restore']) == restore_action(new['restore']), 'exact704-column restore equality')
    paid, inventory = frames.frame_report(new)
    need(paid == new['report']['local_profile'] == {str(k): n for k, n in LOCAL.items()}, 'actual complete local tariff')
    need(inventory == old['report']['width_inventory'] == new['report']['width_inventory'], 'unchanged inventory')
    trimmed = copy.deepcopy(new)
    trimmed['A'] = trimmed['A'][trimmed['prelude_events']:]
    need(frames.derive_cleanup(trimmed, set(map(int, new['helper_final']))) == new['cleanup'], 'actual inverse cleanup')


def calculate(include_owners=True):
    authenticate()
    materializer, geometry = baseline_modules()
    frames = load(ROOT / 'research/rank7-joint-endframes/vendor/preload_move.py', 'credited_frames')
    controls = 0
    for tag in ['base', 'extra']:
        old = read(ROOT / ('research/rank7-t740-release/vendor/pr3015/edits/FINAL-WORD-' + tag + '.json.gz'))
        new = read(P / ('vendor/WORD-' + tag + '.json.gz'))
        check_word(old, new, frames)
        for kind in ['sign', 'price']:
            bad = copy.deepcopy(new)
            if kind == 'sign':
                index = next(i for i, g in enumerate(bad['restore']) if g[0] == 'add' and g[3])
                bad['restore'][index][3] *= -1
            else:
                bad['report']['local_profile']['1'] -= 1
            try:
                check_word(old, bad, frames)
            except ValueError:
                controls += 1
            else:
                raise ValueError('word corruption accepted')
    claim = read(P / 'vendor/PR3042-CLAIM.json')
    providers = read(P / 'vendor/PROVIDERS.json')
    old_providers = read(ROOT / 'research/rank7-t740-release/vendor/pr3015/allocation/PROVIDERS.json')
    for name, provider in providers.items():
        need(provider['widths'] == old_providers[name]['widths'], 'every ordered helper width unchanged')
        need({int(k): n for k, n in provider['actual_paid_profile'].items()} == LOCAL, 'provider actual tariff')
    if include_owners:
        producer = load(ROOT / 'research/rank7-t148-restore-release/verify.py', 'credited_t148_producer')
        _, _, _, order, _, fill, dispatch = producer.allocation()
        checker = producer.retained('geometry')
        owner = checker.check(order, fill, {(s,r):p for s,r,p in dispatch},
            producer.read(producer.SOURCE / 'vendor/PLAN.json.gz'),
            producer.read(producer.SOURCE / 'vendor/TEMPLATE.json.gz'), providers)
        need(owner['profile'] == PROFILE and owner['roles'] == 543456, 'all actual T148 roles and paid children')
        need(producer.stock(148)['physical'] == 133117, 'every physical family and91 buffers')
    root = load(ROOT / 'research/rank7-joint-endframes/tools/root.py', 'credited_exact_root')
    lower, upper = root.kappa_from_profile(PROFILE, 148)
    C = Q((lower * 10**24).__floor__(), 10**24)
    kappa = C - Q(1, 10**46) - Q(1, 10**70)
    prior = Q(claim['kappa'])
    need(kappa > prior and kappa < C <= lower < upper, 'strict exact gain over full PR3042 point')
    need(root.moment(PROFILE, C + Q(1, 10**24), 132608)[0] > 1, 'larger endpoint rejected')
    wrong = dict(PROFILE)
    wrong[48] += 1
    need(root.moment(wrong, C, 132608)[0] > 1, 'unpaid rank48 charge rejected')
    cap = materializer.load('vendor/pr3024/cap_proof.py', 'credited_cap')
    cap.LOCAL = LOCAL
    certificate = read(ROOT / 'research/rank7-joint-endframes/certificates/RELAX-CAP.json')
    cap_lower, cap_upper = map(Q, [claim['fixed_inventory_cap']['cap_lower'], claim['fixed_inventory_cap']['cap_upper']])
    certificate.update(local_per_call={str(r): n for r, n in LOCAL.items()}, cap_lower=str(cap_lower), cap_upper=str(cap_upper))
    cap.verify_cap(certificate, root)
    need(upper < cap_lower < cap_upper, 'honest positive gap below the fixed-inventory cap')
    return dict(kappa=kappa, complex_lower=C, previous=prior, gain=kappa-prior,
                root_lower=lower, root_upper=upper, word_controls=controls)


def run(math_only=False):
    arithmetic = calculate()
    if math_only:
        print('PASS_FINITE_T148_CARRIER_COMPOSITION_NOT_A_RELEASE', str(arithmetic['gain']))
        return
    claim = read(P / 'CLAIM.json')
    need(claim['status'] == 'PASS_T148_CARRIER_SKIPS_COMPLETE_RELEASE', 'completed composition release')
    for key in ['kappa', 'complex_lower', 'previous', 'gain']:
        need(Q(claim[key]) == arithmetic[key], 'exact claim field: ' + key)
    evidence = read(P / 'evidence/VALIDATION.json')
    need(evidence['baseline_complete_release'] is True and evidence['composition_complete_release'] is True,
         'both complete release gates')
    for filename, point, field in [('BASELINE-RELEASE-RECEIPT.json',
        Q('0.001729152756004330934535')-Q(1,10**46)-Q(1,10**70), 'baseline_release_sha256'),
        ('RELEASE-RECEIPT.json', arithmetic['kappa'], 'release_sha256')]:
        receipt = read(P / 'evidence' / filename)
        need(sha(P / 'evidence' / filename) == evidence[field] and receipt['status'] == 'PASS_RELEASE'
             and Q(receipt['kappa_decimal']) == point, 'complete terminal release binding')
    need(evidence['controls'] == dict(admission=139, bit=12, controller=25, independent_owner=8, geometry=6),
         'all actual rejecting controls')
    print('PASS_T148_CARRIER_SKIPS', str(arithmetic['kappa']), 'gain=' + str(arithmetic['gain']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--math-only', action='store_true')
    run(parser.parse_args().math_only)
