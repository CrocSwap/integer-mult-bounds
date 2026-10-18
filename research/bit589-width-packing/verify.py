# SPDX-License-Identifier: Apache-2.0
"""Replay the PR589 width-packing note and its negative controls.

Usage: python3 -B research/bit589-width-packing/verify.py --work NEW_EMPTY_DIR
Expected last line: PASS_BIT589_WIDTH_PACKING_REPLAY
"""
import argparse
import copy
import gzip
import json
import subprocess
import sys
import tarfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

import packing
from packing import HERE, ROOT, require, sha256

T37_ARCHIVE = ('research/community-frontier942-audit/t37-replay.tar.gz',
               '48285025105210b56a32d3d4d57a21b7591760acc709d38073e4dca339eb06fe')
T37_TEMPLATE = ('strict/global/hosted/GLOBAL-TEMPLATE.json.gz',
                '956e0c0e9b083806268bf93525441ccea143d5f78e46c5f6b793b22cfe11113d')


def rejects(name, fn, reason):
    try:
        fn()
    except ValueError as exc:
        require(reason in str(exc), f'control {name} rejected for another reason: {exc}')
        return name
    raise SystemExit(f'FAIL control {name} was accepted')


def one_level_windows_in_t37():
    """Supporting evidence on the same nine-stage template: in the selected complex T37 hosting,
    every one-level idle window (capacity one level = 8 coordinates) is completely hosted."""
    path = ROOT / T37_ARCHIVE[0]
    require(sha256(path.read_bytes()) == T37_ARCHIVE[1], 'T37 archive digest')
    with tarfile.open(path, 'r:gz') as tar:
        payload = gzip.decompress(tar.extractfile(tar.getmember(T37_TEMPLATE[0])).read())
    require(sha256(payload) == T37_TEMPLATE[1], 'T37 template digest')
    t = json.loads(payload)
    cap = Counter()
    hosted = Counter()
    for s in t['hosting']['pooled_slots']:
        cap[(s['family'], s['child'])] += s['width']
        hosted[s['child']] += s['width']
    for c in t['idle_children']:
        cap[(c['family'], c['child'])] += c['rank']
    by_child = {}
    for (f, ch), c in cap.items():
        by_child.setdefault(ch, Counter())[c] += 1
    one_level = sorted(ch for ch, cs in by_child.items() if set(cs) == {8})
    idle_in_one_level = sum(c['rank'] for c in t['idle_children'] if c['child'] in one_level)
    require(len(one_level) == 6 and idle_in_one_level == 0, 'one-level windows of T37 are fully hosted')
    return dict(one_level_children=one_level, families_per_child=sorted({sum(by_child[ch].values()) for ch in one_level}),
                hosted_coordinates=sum(hosted[ch] for ch in one_level), idle_coordinates=idle_in_one_level)


def controls():
    record = packing.pinned_json('bit_record')
    selection = packing.pinned_json('selection')
    model = packing.slot_model(record, selection)
    passed = []
    # C1: one width-8 residual moved between slot indices breaks the capacity reconstruction.
    sel = copy.deepcopy(selection)
    sel['bit']['patterns'][0][1] = [8, 8]

    def c1():
        packing.slot_model(record, sel)
    passed.append(rejects('C1_pattern_moved', c1, 'stage and pattern totals agree'))
    # C2: the per-unit argument refuses a slot capacity divisible by 8.
    m2 = dict(model)
    m2['slots'] = Counter(model['slots'])
    m2['slots'][48] = 1
    passed.append(rejects('C2_capacity_divisible_by_8',
                          lambda: packing.width8_optimality(m2, Q(1, 600)),
                          'no slot capacity is divisible by 8'))
    # C3: a corrupted record digest is rejected.
    src = dict(packing.SOURCES['inputs']['bit_record'])
    good = packing.SOURCES['inputs']['bit_record']
    packing.SOURCES['inputs']['bit_record'] = dict(src, sha256='0' * 64)
    try:
        passed.append(rejects('C3_record_pin', lambda: packing.pinned_json('bit_record'), 'digest mismatch'))
    finally:
        packing.SOURCES['inputs']['bit_record'] = good
    # C4: the next bit grid point is rejected by both engines (with the bad-residue surcharge).
    W = record['nine']['bit']['live']
    H = dict(model['H'])
    c0 = Q(record['nine']['bit_lower'])
    z = c0 + Q(1, 10 ** 24)
    lo, _ = packing.MOMENT.moment(H, 64, W, z, True)
    blo, _ = packing.BASE_TWO.moment(64, W, list(H.items()), z)
    flo, _ = packing.BASE_TWO.moment(64, W, [(1, 32 * 64 * 64 * sum(H.values()))], z)
    blo += flo / 10 ** 16          # the bit model keeps the inherited bad-residue surcharge
    require(lo > 1 and blo > 1, 'both engines exceed one at the next bit endpoint')

    def c4():
        require(lo < 1, 'next bit endpoint rejected')
    passed.append(rejects('C4_next_bit_endpoint', c4, 'next bit endpoint rejected'))
    # C5: a width-7 profile that forgets the freed coordinates changes rank mass.
    opt, _ = packing.local_bracket(model['local'], 1)

    def c5():
        Hx = Counter({r: n * model['calls'] for r, n in opt.items()})
        Hx.update({r: n * packing.T for r, n in model['idle_rep'].items()})
        require(sum(r * n for r, n in Hx.items()) == sum(r * n for r, n in model['H'].items()), 'rank mass changes')
    passed.append(rejects('C5_lost_coordinates', c5, 'rank mass changes'))
    # C6: more converted helpers than empty 7-slots is refused by the constructive placement.
    passed.append(rejects('C6_too_many_for_7_slots', lambda: packing.width7_partial_idle(model, 75),
                          'width-7 residuals in 7-slots only'))
    return passed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', required=True)
    work = Path(ap.parse_args().work).resolve()
    require(not work.exists(), 'work directory must not exist')
    work.mkdir(parents=True)
    proc = subprocess.run([sys.executable, '-B', str(HERE / 'packing.py'), str(work / 'RESULT.json')],
                          cwd=HERE, capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    require(proc.returncode == 0, 'packing.py failed:\n' + proc.stderr)
    require(json.loads((work / 'RESULT.json').read_text()) == json.loads((HERE / 'RESULT.json').read_text()),
            'RESULT.json differs from the committed result')
    evidence = one_level_windows_in_t37()
    print('T37 one-level windows fully hosted:', evidence)
    print('controls rejected as expected:', ', '.join(controls()))
    print('PASS_BIT589_WIDTH_PACKING_REPLAY')


if __name__ == '__main__':
    main()
