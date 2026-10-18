# SPDX-License-Identifier: Apache-2.0
"""Compose four declared paired extractions at hyperplane normal 45 on Mason Hale's PR2917 words.

Pure composition PARENT -> WORD, modelled on PR2917's producer.py (Mason Hale), which hard-codes its
own nine helpers; this module declares the four new ones. The paired input/output construction, its
two-sided certificate and the compensation rule C*S are Jeremy Diviney's PR2908 method; the frame
accounting (frame_report) and inverse-reverse cleanup (derive_cleanup) are Jeremy Kothe's PR2894 code,
vendored byte-identical by PR2917 (vendor/preload_move.py). Marius-Paul Dumitrean, with substantial AI
assistance (Anthropic Claude via Claude Code). This module is pure: no file, process or output access.
"""
import collections
import copy
from fractions import Fraction as Q
import preload_move as pm

HELPERS = (249, 267, 251, 265)
NORMAL = 45
FRAME = [256, 128, 64, 33, 16, 9, 5, 2]            # E_45 = {x in F_2^9 : x . 45 = 0}, canonical basis
PARENT_PROFILE = {'1': 2416, '2': 640, '3': 280, '4': 110, '5': 26, '8': 8}     # PR2917
PARENT_INVENTORY = {'4': 26, '5': 2, '7': 62, '8': 96, '9': 222}
PARENT_BUFFERS = 82
PROFILE = {'1': 2434, '2': 632, '3': 286, '4': 104, '5': 26, '8': 8}
INVENTORY = {'4': 26, '5': 2, '7': 62, '8': 100, '9': 218}
BUFFERS = 86
ALLOWED = {'A', 'restore', 'helper_final', 'compensation', 'report', 'cleanup'}


def hyperplane(normal):
    """Canonical basis of the rank-8 hyperplane E_n of F_2^9 with the given nonzero normal."""
    pm.require(0 < normal < 512, 'nonzero nine-bit normal')
    return list(pm.basis([x for x in range(1, 512) if (x & normal).bit_count() % 2 == 0]))


def refit(word, transform):
    """Apply only the declared literal old-frame to new-frame substitutions (PR2917's rule)."""
    x = copy.deepcopy(word)
    seen = set()
    for edit in transform.get('frame_changes', []):
        section, index = edit['section'], edit['parent_index']
        pm.require(section in ('A', 'restore') and index >= 0 and
                   (section != 'A' or index >= x['prelude_events']) and
                   (section, index) not in seen, 'unique declared non-prelude frame edit')
        seen.add((section, index))
        gate = x[section][index]
        pm.require(gate[:-1] == edit['gate'] and gate[-1] == edit['old_frame'],
                   'exact frame edit preimage')
        pm.require(gate[0] in ('add', 'scale') and not 112 <= gate[1] < 224 and
                   list(pm.basis(edit['new_frame'])) == edit['new_frame'], 'canonical nontarget frame')
        gate[-1] = list(edit['new_frame'])
    return x


def apply_stage(word, transform):
    h = transform['helper']
    before, after = transform['before'], transform['after']
    pm.require(h in HELPERS and str(h) not in word['helper_final'], 'fresh declared helper')
    pm.require(str(h) not in word['start_extra'], 'zero entrance')
    protected = set(map(int, word['helper_final'])) | set(map(int, word['start_extra']))
    protected |= {c['source'] for c in word['initial_corrections']}
    for g in before:
        pm.require(g[0] in ('add', 'scale') and g[-1] == [], 'scalar zero-frame input change')
        roles = g[1:3] if g[0] == 'add' else g[1:2]
        pm.require(all(224 <= r < 704 and r not in protected and r not in word['removed']
                       for r in roles), 'unprotected live helpers only')
    frame = list(pm.basis(after[0][-1]))
    pm.require(transform['normal'] == NORMAL and frame == hyperplane(NORMAL) == FRAME, 'declared hyperplane E_45')
    pm.require(len(frame) == 8 and all(g[0] in ('add', 'scale') and g[-1] == frame
                                     for g in after), 'common terminal hyperplane')
    x = refit(word, transform)
    n = x['prelude_events']
    x['A'] = x['A'][:n] + copy.deepcopy(before) + x['A'][n:]
    x['restore'] += copy.deepcopy(after)
    x['helper_final'][str(h)] = frame
    C = collections.defaultdict(dict)
    for g in x['compensation']:
        C[g[2]][g[1]] = C[g[2]].get(g[1], Q(0)) + Q(g[3], g[4])
    # Right multiplication C*S uses the reverse order of the literal input gates.
    for g in reversed(before):
        if g[0] == 'scale':
            C[g[1]] = {t: a * Q(g[2], g[3]) for t, a in C[g[1]].items()}
        else:
            t, s = g[1:3]
            for target, a in C[t].items():
                C[s][target] = C[s].get(target, Q(0)) + Q(g[3], g[4]) * a
    x['compensation'] = [['add', t, r, a.numerator, a.denominator, []]
                         for r, col in sorted(C.items()) for t, a in sorted(col.items()) if a]
    pm.require(not any(g[2] == h for g in x['compensation']), 'new cold column has no compensation')
    profile, inventory = pm.frame_report(x)
    x['report']['local_profile'], x['report']['width_inventory'] = profile, inventory
    z = copy.deepcopy(x)
    z['A'] = z['A'][n:]
    x['cleanup'] = pm.derive_cleanup(z, set(map(int, x['helper_final'])))
    pm.require({k for k in word if word[k] != x[k]} == ALLOWED, 'exact changed sections')
    return x


def apply(word, transforms):
    pm.require(tuple(t['helper'] for t in transforms) == HELPERS, 'declared composition order')
    pm.require([t.get('step') for t in transforms] == [1, 2, 3, 4], 'declared step numbers')
    pm.require(len(word['helper_final']) == PARENT_BUFFERS, 'PR2917 cold endpoint count')
    pm.require(word['report']['local_profile'] == PARENT_PROFILE and
               word['report']['width_inventory'] == PARENT_INVENTORY, 'PR2917 local profile and inventory')
    x = word
    for transform in transforms:
        x = apply_stage(x, transform)
    pm.require(all(x['helper_final'].get(r) == U for r, U in word['helper_final'].items()), 'inherited endpoints retained')
    pm.require(len(x['helper_final']) == BUFFERS, 'all four added buffers charged')
    pm.require(x['report']['local_profile'] == PROFILE and
               x['report']['width_inventory'] == INVENTORY, 'complete local profile and inventory')
    return x
