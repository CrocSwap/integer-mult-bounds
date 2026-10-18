"""Source-bound replay of 43 exact helper-lifetime reuses in the E8 word.

The source word/frames are Dylan Crow's PR370, first retimed by the accompanying
frame witness. Helper reuse and replay prepared with OpenAI Codex assistance.
Apache-2.0. Usage: reuse_replay.py RETIMED.json SELECTION.json OUTPUT.json
"""
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import bisect
import copy
import json
import sys

assert __debug__, 'Assertions are required; do not use -O'


def reconstruct(source_bytes, selection):
    assert sha256(source_bytes).hexdigest() == selection['retimed_input_sha256']
    c = json.loads(source_bytes)
    v = c['v']
    n = 2 * v + c['R']
    ops = c['A'] + c['B']
    masks = [sum(1 << s for s in f) for f in c['frames']]
    writes, uses = defaultdict(list), defaultdict(list)
    for i, (f, d, sources) in enumerate(ops):
        writes[d].append((i, f, sources))
        for r in [d] + sources:
            uses[r].append(i)
    pairs = selection['pairs']
    assert len(pairs) == selection['merged_helpers'] == 43
    assert len({p['at'] for p in pairs}) == len(pairs)
    used = [r for p in pairs for r in (p['old'], p['new'])]
    assert len(set(used)) == 2 * len(pairs), 'Reuses must have disjoint old/new helpers'
    protected = {r for p in pairs for r in p['sources']}
    assert not protected.intersection(used), 'Uncompute sources cannot be aliased'
    by_at = {p['at']: p for p in pairs}
    for p in pairs:
        q, d, i, f, sources = p['old'], p['new'], p['at'], p['frame'], p['sources']
        assert 2 * v <= q < n and 2 * v <= d < n
        assert q not in c['ret'] and d not in c['ret']
        assert i < len(c['A']), 'The frozen witness reuses only before the scatter'
        assert ops[i][0] == f and ops[i][1] == d
        assert uses[d][0] == writes[d][0][0] == i
        assert len(writes[q]) == 1 and uses[q][-1] < i
        assert writes[q][0][2] == sources
        assert c['start'][q] == c['start'][d] and c['final'][q] == c['final'][d]
        assert all(r >= 2 * v for r in sources), 'Frozen undo sources are helpers'

    # Exact F2 symbolic values certify that each source at uncompute equals its
    # value at the old helper's unique write. All selected sites precede scatter.
    values = [1 << r for r in range(n)]
    birth_sources = {}
    cur = list(c['start'])

    def next_frame(r, i):
        p = bisect.bisect_left(uses[r], i)
        return ops[uses[r][p]][0] if p < len(uses[r]) else c['final'][r]

    for i, (f, d, sources) in enumerate(ops):
        if i in by_at:
            p = by_at[i]
            q = p['old']
            assert all(values[s] == birth_sources[q][s] for s in p['sources'])
            assert all(masks[cur[r]] & ~masks[f] == 0 for r in [q] + p['sources'])
            assert all(masks[f] & ~masks[next_frame(s, i)] == 0 for s in p['sources'])
        if len(writes[d]) == 1:
            birth_sources[d] = {s: values[s] for s in sources}
        for s in sources:
            values[d] ^= values[s]
        for r in [d] + sources:
            assert masks[cur[r]] & ~masks[f] == 0
            cur[r] = f

    out = copy.deepcopy(c)
    alias = {p['new']: p['old'] for p in pairs}
    physical = [r for r in range(n) if r not in alias]
    index = {r: i for i, r in enumerate(physical)}

    def remap(r):
        return index[alias.get(r, r)]

    newops = []
    split = None
    for i, (f, d, sources) in enumerate(ops):
        if i == len(c['A']):
            split = len(newops)
        if i in by_at:
            p = by_at[i]
            newops.append([f, remap(p['old']), [remap(s) for s in p['sources']]])
        newops.append([f, remap(d), [remap(s) for s in sources]])
    assert split is not None
    out['A'], out['B'] = newops[:split], newops[split:]
    out['R'] -= len(pairs)
    assert out['R'] == 822
    out['start'] = [c['start'][r] for r in physical]
    out['final'] = [c['final'][r] for r in physical]
    out['ret'] = [remap(r) for r in c['ret']]
    full, zero = c['final'][0], c['start'][v]
    out['C'] = [[full, d, list(sources)] for _, d, sources in reversed(newops) if d >= 2 * v]
    # Recompute target compensation for the surviving independent helper dirt.
    # A/B never read target registers, so these initial target offsets survive.
    assert all(s < v or s >= 2 * v for _, _, sources in newops for s in sources)
    assert all(d < v or d >= 2 * v for _, d, _ in out['A'])
    dirt = [0] * (2 * v + out['R'])
    for r in range(2 * v, len(dirt)):
        dirt[r] = 1 << (r - 2 * v)
    for _, d, sources in out['A']:
        for s in sources:
            dirt[d] ^= dirt[s]
    copied = [dirt[q] for q in out['ret']]
    for t, row in enumerate(out['scatter']):
        for k in row:
            dirt[v + t] ^= copied[k]
    for _, d, sources in out['B']:
        for s in sources:
            dirt[d] ^= dirt[s]
    out['D'] = [[zero, v + t, [2 * v + j for j in range(out['R']) if dirt[v + t] >> j & 1]]
                for t in range(v) if dirt[v + t]]
    assert out['frames'] == c['frames'] and out['scatter'] == c['scatter']
    data = json.dumps(out, sort_keys=True, separators=(',', ':')).encode()
    assert sha256(data).hexdigest() == selection['output_sha256']
    return data


def negative_controls(source_bytes, selection):
    result = []
    for name, key, value in [('wrong reuse site', 'at', -1), ('wrong undo source', 'sources', [0]),
                             ('overlapping old/new helper', 'new', selection['pairs'][0]['old'])]:
        bad = copy.deepcopy(selection)
        bad['pairs'][0][key] = value
        try:
            reconstruct(source_bytes, bad)
        except (AssertionError, KeyError):
            result.append(name)
        else:
            raise AssertionError(('invalid helper witness accepted', name))
    return result


if __name__ == '__main__':
    assert len(sys.argv) == 4, __doc__
    source, selection, target = map(Path, sys.argv[1:])
    data = reconstruct(source.read_bytes(), json.loads(selection.read_text()))
    target.write_bytes(data)
    print('PASS_SOURCE_BOUND_HELPER_REUSE', 43, sha256(data).hexdigest())
