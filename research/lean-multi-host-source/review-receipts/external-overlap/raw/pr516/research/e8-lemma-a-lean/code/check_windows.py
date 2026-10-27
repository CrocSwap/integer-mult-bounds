# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
"""Instance check (W)/(A') (PROOF.md §4-5): every hosted block lies inside its pending child's open window, and the
hosted blocks of one pending child are pairwise disjoint.

These are the hypotheses of Variant A' (`LemmaA.lemmaA_async`, `async_window`, `gather`) that a schedule must meet, and,
for the lockstep words, the window part of (W).  Written independently of #484's audit_hosted_gk.py and #505's
audit_async.py; it reads only the emitted hosted template:
  * positions are indices into the template's `execution_schedule`; a local cover sweep of stage s touches the pair that
    stage s acts on (`recipe`), for each of its replicas; a bridge touches its src and dst pairs; an idle cover sweep of a
    pair runs that pair's pending children (`child_indices`, one per side);
  * the open window of (owner replica, child i) is (last touch of the child's pair by that replica before the idle
    sweep, the idle sweep): after the owner's previous data or bridge touch, before the child's deadline;
  * the windows of the children of one family group (replica, pair, side) are pairwise disjoint, so inside a window no
    idle sweep and no data or bridge touch acts on the family; only hosted blocks do;
  * a hosted route [3, i, off] (width 9) or [4, i, off, w, spectators] on family f is owned by replica f // 960 on pair
    side (f % 960) // 120 and port f % 120; the side must match child i, the call must lie strictly inside the window,
    and its block off .. off+w-1 must be disjoint from every other block on (owner replica, child i, port).
Lockstep (#484: events carry `replicas`) and asynchronous (#505: events carry one `replica`) templates are both read.

usage: check_windows.py T.json.gz [T2.json.gz ...] [--mutants]        Standard library only."""
import gzip, json, sys
from collections import defaultdict
from pathlib import Path


def reps(e, allreps):
    if 'replicas' in e: return list(e['replicas'])
    if 'replica' in e: return [e['replica']]
    return list(allreps)


def check(t):
    allreps = sorted({c['replica'] for c in t['calls']})
    stagepair = {e['stage']: e['pair'] for e in t['recipe'] if e.get('kind') == 'local'}
    last, windows, child, group = {}, {}, {}, {}; callpos = {}; bad = []
    for pos, e in enumerate(t['execution_schedule']):
        k = e.get('kind')
        if k == 'local_cover_sweep':
            for r in reps(e, allreps): callpos[e['stage'], r] = pos; last[r, stagepair[e['stage']]] = pos
        elif k == 'bridge':
            for r in reps(e, allreps): last[r, e['src']] = last[r, e['dst']] = pos
        elif k == 'idle_cover_sweep':
            for side, i in enumerate(e['child_indices']):
                for r in reps(e, allreps):
                    if (r, i) in windows: bad.append(f'child {i} of replica {r} run twice')
                    windows[r, i] = (last.get((r, e['pair']), -1), pos); group[r, i] = (r, e['pair'], side)
                child[i] = (e['pair'], side)
    by = defaultdict(list)                                  # children of one family group: pairwise disjoint windows
    for key, w in windows.items(): by[group[key]].append(w)
    for g, ws in by.items():
        ws.sort()
        if any(a[1] > b[0] for a, b in zip(ws, ws[1:])): bad.append(f'overlapping child windows in family group {g}')
    used = defaultdict(set); n = 0
    for c in t['calls']:
        pos = callpos.get((c['stage'], c['replica']))
        if pos is None: bad.append(f"call stage {c['stage']} replica {c['replica']} has no cover sweep"); continue
        for f, r in c['owners']:
            if r[0] not in (3, 4): continue
            i, off = r[1], r[2]; w = 9 if r[0] == 3 else r[3]; n += 1
            orep, ps, port = f // 960, (f % 960) // 120, f % 120
            if i not in child or ps != 2 * child[i][0] + child[i][1]: bad.append(f'call {c["stage"]},{c["replica"]}: family {f} is not on child {i}'); continue
            lo, hi = windows.get((orep, i), (None, None))
            if lo is None or not lo < pos < hi: bad.append(f'call {c["stage"]},{c["replica"]}: block on replica {orep} child {i} outside its window {lo},{hi} at {pos}')
            cells = set(range(off, off + w))
            if cells & used[orep, i, port]: bad.append(f'call {c["stage"]},{c["replica"]}: block overlaps on replica {orep} child {i} port {port}')
            used[orep, i, port] |= cells
    return n, len(windows), bad


def mutants(t):
    """necessity controls: each edit must be rejected"""
    import copy
    res = {}
    stagepair = {e['stage']: e['pair'] for e in t['recipe'] if e.get('kind') == 'local'}
    children = {}
    for e in t['execution_schedule']:
        if e.get('kind') == 'idle_cover_sweep':
            for side, i in enumerate(e['child_indices']): children[i] = (e['pair'], side)
    m = copy.deepcopy(t)                                   # a block moved onto another child of the same family group
    done = False
    for c in m['calls']:
        for f, r in c['owners']:
            if r[0] in (3, 4) and not done:
                alt = [j for j, ps in children.items() if ps == children[r[1]] and j != r[1]]
                if alt: r[1] = alt[0]; done = True
    res['block moved to another child (outside its window)'] = len(check(m)[2])
    m = copy.deepcopy(t)                                   # two blocks of one child made to overlap
    seen = {}
    for c in m['calls']:
        for f, r in c['owners']:
            if r[0] in (3, 4):
                key = (f, r[1])
                if key in seen and 'done' not in seen: r[2] = seen[key]; seen['done'] = 1
                seen.setdefault(key, r[2])
    res['two blocks of one child overlap'] = len(check(m)[2])
    return res


def main():
    ok = True
    for p in [a for a in sys.argv[1:] if not a.startswith('--')]:
        t = json.loads(gzip.decompress(Path(p).read_bytes()))
        n, nw, bad = check(t)
        ok &= not bad
        print(f'{p}: hosted blocks {n}; pending windows {nw}; violations {len(bad)} {bad[:3]}', flush=True)
        if '--mutants' in sys.argv:
            mu = mutants(t); ok &= all(v > 0 for v in mu.values()); print('  mutants (violations each):', mu, flush=True)
    print('PASS windows and blocks' if ok else 'FAIL windows and blocks')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
