#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Deterministic PR2673 priority-fill / PR2679 pre-life-word composition.

No solver and no native execution. Match helper indices in increasing order
within each width queue, delete seven surplus width-4 roles per call, then
compact each physical bin. Helper indices are width-registry positions, not
register identities. Final whole-call geometry is checked separately by both
literal implementations in verify.py; full_replay.py binds actual natives.

Credit Jeremy Kothe's PR2673 fill and PR2621's priority scheduling idea,
PR2679's pre-life/refit words, PR2588/PR2530 and retained supplier lineage.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def transform(old, new, fill, order, initial_dispatch, words):
    """Reconstruct the full candidate and mapping from authenticated inputs."""
    need(set(old) == set(new) == set(words) == {'gauge44', 'extra'}, 'provider identities')
    need(len(order) == 666 and len(set(map(tuple, order))) == 666, 'composition call count')
    need(len(fill['rows']) == 281052, 'source role count')
    dispatch = dict(initial_dispatch)
    for s, r, pid in fill['dispatch_overrides']:
        need((s, r) in dispatch and pid in new, 'source dispatch override')
        dispatch[s, r] = pid
    need(set(dispatch) == set(map(tuple, order)), 'source dispatch coverage')
    maps, dropped, bindings = {}, {}, {}
    for pid in sorted(new):
        oldq, newq = defaultdict(list), defaultdict(list)
        for i, width in enumerate(old[pid]['widths']):
            oldq[width].append(i)
        for i, width in enumerate(new[pid]['widths']):
            newq[width].append(i)
        need(len(old[pid]['widths']) == 422 and len(new[pid]['widths']) == 415, 'old/new helper counts')
        need(set(oldq) == set(newq) == {4, 5, 7, 8, 9}, 'width support')
        need({w:len(oldq[w])-len(newq[w]) for w in oldq} == {4:7, 5:0, 7:0, 8:0, 9:0}, 'seven surplus width-4 roles')
        maps[pid] = {i:j for w in sorted(newq) for i,j in zip(oldq[w], newq[w])}
        dropped[pid] = sorted(set(range(422)) - set(maps[pid]))
        need(len(maps[pid]) == 415 and set(maps[pid].values()) == set(range(415)), 'new helper bijection')
        need(all(old[pid]['widths'][i] == new[pid]['widths'][j] for i,j in maps[pid].items()), 'width-preserving bijection')
        need(len(dropped[pid]) == 7 and all(old[pid]['widths'][i] == 4 for i in dropped[pid]), 'deleted widths')
        # This binds declared widths/report to the raw word, without claiming
        # that reading its report proves the actual native program semantics.
        word = words[pid]
        remaining = [r for r in range(224, 704) if r not in set(word['removed'])]
        final = {int(k):v for k,v in word['helper_final'].items()}
        extra = {int(k):v for k,v in word['start_extra'].items()}
        actual = [len(final.get(r, range(9))) - len(extra.get(r, [])) for r in remaining]
        need(actual == new[pid]['widths'], 'raw-word ordered width binding')
        need(word['report']['local_profile'] == new[pid]['actual_paid_profile'], 'raw-word reported profile binding')
        bindings[pid] = dict(helpers=len(remaining),
                            width_inventory=dict(sorted(Counter(actual).items())))
    rows, removed, bins, oldbins, per_call = [], [], defaultdict(list), defaultdict(list), defaultdict(set)
    for i, row in enumerate(fill['rows']):
        need(len(row) == 6 and all(type(v) is int for v in row), 'source role shape')
        t, h, owner, child, port, offset = row
        need(0 <= t < 666 and 0 <= h < 422, 'source role bounds')
        need(h not in per_call[t], 'source duplicate helper')
        per_call[t].add(h)
        pid = dispatch[tuple(order[t])]
        oldbins[owner, child, port].append(old[pid]['widths'][h])
        if h not in maps[pid]:
            removed.append((owner, child, port))
            continue
        bins[owner, child, port].append(len(rows))
        rows.append([t, maps[pid][h], owner, child, port, offset])
    need(set(per_call) == set(range(666)) and all(x == set(range(422)) for x in per_call.values()), 'source helper coverage')
    need(len(removed) == 4662 and len(set(removed)) == 4662, '4662 distinct affected bins')
    need(all(sorted(oldbins[key]) == [4, 9, 9, 9] for key in removed), 'source deletion-bin patterns')
    for indices in bins.values():
        offset = 0
        for i in sorted(indices, key=lambda j:rows[j][5]):
            row = rows[i]
            row[5] = offset
            offset += new[dispatch[tuple(order[row[0]])]]['widths'][row[1]]
    need(len(rows) == 276390, 'composed role count')
    candidate = dict(fill, rows=rows)
    mapping = dict(keep_maps=maps, dropped=dropped)
    report = dict(status='PASS_DETERMINISTIC_WIDTH_QUEUE_COMPOSITION', removed_roles=4662,
                  affected_bins=4662, source_bin_widths=[4, 9, 9, 9], remaining_bin_widths=[9, 9, 9],
                  roles=len(rows), calls=666, helpers_per_call=415, width_bindings=bindings,
                  fill_canonical_sha256=hashlib.sha256(canonical(candidate)).hexdigest())
    return candidate, mapping, report


def check(data):
    obj = data['objects']
    original_order = obj['source/pr2673/ORDER.json']
    initial = {(s,r):p for s,r,p in obj['source/pr2673/DISPATCH.json.gz']}
    need(initial == data['dispatch'], 'unchanged source dispatch')
    candidate, mapping, report = transform(
        obj['source/pr2673/PROVIDERS.json'], data['providers'],
        obj['source/pr2673/FILL.json.gz'], original_order, initial,
        {'gauge44':obj['source/pr2679/WORD-base.json.gz'], 'extra':obj['source/pr2679/WORD-extra.json.gz']})
    need(data['candidate_order'] == original_order, 'unchanged priority order')
    need(candidate == data['candidate_fill'], 'complete deterministic candidate equality')
    need(json.loads(canonical(mapping)) == obj['candidate/MAPPING.json'], 'complete deterministic mapping equality')
    report['mapping_canonical_sha256'] = hashlib.sha256(canonical(json.loads(canonical(mapping)))).hexdigest()
    return report
