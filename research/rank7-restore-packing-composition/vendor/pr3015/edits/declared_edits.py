# SPDX-License-Identifier: Apache-2.0
"""Declared literal gate-edit stage on PR2979's words (mdumitrean; joint rank-7 end frames, paired extractions, fourteen rewrites).

Edits found by Stack2979 / Jeremy Kothe (jeremykothe2), with AI assistance. Pure module. A spec is a LIST of edits
{id, section, start, stop, old, new}: the literal old gates at [start:stop) of the source word are replaced by the literal new gates
(frames included, so frames are re-solved by the author and literal here). Edits are addressed in the SOURCE word and must not touch
or be adjacent. Compensation, cut, A/B (unless edited), helper endpoints, warps and buffers are unchanged; profile, inventory and
cleanup are re-derived by the inherited frame rules. Exactness is decided by the inherited exact auditor, not by this module.
"""
import copy
import preload_move as pm

SECTIONS = ('A', 'B', 'restore')
ALLOWED = {'A', 'B', 'restore', 'report', 'cleanup'}


def apply(word, spec, declared=None):
    x = copy.deepcopy(word)
    taken = {s: [] for s in SECTIONS}
    edits = []
    for e in spec:
        s, a, b = e['section'], e['start'], e['stop']
        pm.require(s in SECTIONS and 0 <= a <= b <= len(word[s]), 'edit address')
        pm.require(s != 'A' or a >= word['prelude_events'], 'no prelude edit')
        pm.require(word[s][a:b] == e['old'] and e['old'] != e['new'], ('old gates differ from the declared preimage', e['id'], s, a))
        for (c, d) in taken[s]:
            pm.require(b < c or d < a, ('overlapping or adjacent edits', e['id']))
        taken[s].append((a, b))
        edits.append((s, a, b, e['new']))
    for s, a, b, new in sorted(edits, key=lambda t: (t[0], -t[1], -t[2])):
        x[s][a:b] = copy.deepcopy(new)
    pm.require(not any(s == 'B' for s, *_ in edits), 'B edits would move warps; not supported by this stage')
    profile, inventory = pm.frame_report(x)
    x['report']['local_profile'], x['report']['width_inventory'] = profile, inventory
    z = copy.deepcopy(x)
    z['A'] = z['A'][z['prelude_events']:]
    x['cleanup'] = pm.derive_cleanup(z, pm.restored_of(word))
    pm.require({k for k in word if word[k] != x[k]} <= ALLOWED, 'only A, B, restore, report and cleanup change')
    for k in ('cut', 'compensation', 'helper_final', 'start_extra', 'removed', 'prelude_events', 'warps'):
        pm.require(x[k] == word[k], ('unchanged section', k))
    if declared is not None:
        pm.require(profile == declared['local_profile'] and inventory == declared['width_inventory'], ('declared profile/inventory', profile, inventory))
    return x, dict(edits=len(edits), local_profile=profile, width_inventory=inventory)
