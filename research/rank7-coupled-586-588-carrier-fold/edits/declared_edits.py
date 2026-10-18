# SPDX-License-Identifier: Apache-2.0
"""Declared literal gate-edit and coupled carrier-fold stage on PR2979's words (mdumitrean; joint rank-7 end frames, paired extractions, fourteen rewrites).

Edits R1_E42, R2_E7, B_586_438 and B_588_440 by dcharb78 (with AI assistance) on PR2979's words (mdumitrean), extending Stack2979 / Jeremy Kothe's
(jeremykothe2) declared edit stage (PR3015). Pure module. A spec is a LIST of declared edits: either a single hunk {id, section, start, stop, old, new}
or a coupled multi-hunk rewrite {id, helper, partner, helper_final, edits: [{section, start, stop, old, new}, ...]}. The literal old gates
at [start:stop) of the source word are replaced by the literal new gates (frames included, so frames are re-solved by the author and literal
here). Edits are addressed in the SOURCE word and must not touch or be adjacent. Phase warps address B positions and are shifted by the net
length change of B edits strictly before them; declared helper_final lowerings must be canonical hyperplanes of the old end frames.
Compensation, cut, start_extra, removed, prelude_events and private buffer count are unchanged; profile, inventory and cleanup are
re-derived by the inherited frame rules. Exactness is decided by the inherited exact auditor, not by this module.
"""
import copy
import preload_move as pm

SECTIONS = ('A', 'B', 'restore')
ALLOWED = {'A', 'B', 'restore', 'warps', 'helper_final', 'report', 'cleanup'}


def inside(small, big):
    return pm.basis(list(big) + list(small)) == pm.basis(list(big))


def apply(word, spec, declared=None):
    x = copy.deepcopy(word)
    taken = {s: [] for s in SECTIONS}
    edits = []
    hf_changes = {}
    if declared is not None and 'helper_final' in declared:
        for h, chg in declared['helper_final'].items():
            hf_changes[str(h)] = chg
    for e in spec:
        if 'helper_final' in e:
            for h, chg in e['helper_final'].items():
                pm.require(str(h) not in hf_changes or hf_changes[str(h)] == chg, ('conflicting helper_final', e['id'], h))
                hf_changes[str(h)] = chg
        hunks = e['edits'] if 'edits' in e else [e]
        for h in hunks:
            s, a, b = h['section'], h['start'], h['stop']
            pm.require(s in SECTIONS and 0 <= a <= b <= len(word[s]), 'edit address')
            pm.require(s != 'A' or a >= word['prelude_events'], 'no prelude edit')
            pm.require(word[s][a:b] == h['old'] and h['old'] != h['new'], ('old gates differ from the declared preimage', e['id'], s, a))
            for (c, d) in taken[s]:
                pm.require(b < c or d < a, ('overlapping or adjacent edits', e['id'], s, a))
            taken[s].append((a, b))
            edits.append((s, a, b, h['new']))
    for s, a, b, new in sorted(edits, key=lambda t: (t[0], -t[1], -t[2])):
        x[s][a:b] = copy.deepcopy(new)
    bedits = [(a, b, len(new) - (b - a)) for s, a, b, new in edits if s == 'B']
    for rec in x['warps']:
        p = rec[0]
        pm.require(not any(a < p < b for a, b, _ in bedits), 'no warp inside an edited B span')
        rec[0] = p + sum(d for a, b, d in bedits if b <= p and a < p)
    for h, chg in sorted(hf_changes.items()):
        old, new = word['helper_final'][h], chg['new']
        pm.require(chg['old'] == old and list(pm.basis(new)) == new, ('exact helper_final preimage and canonical basis', h))
        pm.require(inside(new, old) and len(new) == len(old) - 1, ('lowered helper_final is a hyperplane of old', h))
        x['helper_final'][h] = list(new)
    profile, inventory = pm.frame_report(x)
    x['report']['local_profile'], x['report']['width_inventory'] = profile, inventory
    z = copy.deepcopy(x)
    z['A'] = z['A'][z['prelude_events']:]
    x['cleanup'] = pm.derive_cleanup(z, pm.restored_of(word))
    pm.require({k for k in word if word[k] != x[k]} <= ALLOWED, 'only A, B, restore, warps, helper_final, report and cleanup change')
    for k in ('cut', 'compensation', 'start_extra', 'removed', 'prelude_events'):
        pm.require(x[k] == word[k], ('unchanged section', k))
    pm.require(set(x['helper_final']) == set(word['helper_final']), 'same restored helper set')
    for h in word['helper_final']:
        if h not in hf_changes:
            pm.require(x['helper_final'][h] == word['helper_final'][h], ('unchanged helper_final', h))
    if declared is not None:
        pm.require(profile == declared['local_profile'] and inventory == declared['width_inventory'], ('declared profile/inventory', profile, inventory))
    return x, dict(edits=len(spec), hunks=len(edits), lowered_helpers=sorted(map(int, hf_changes)), local_profile=profile, width_inventory=inventory)
