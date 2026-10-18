"""idle_optimum.py: group census of #1305's completely idle rank-48 non-owner children and exact per-group optimum of the
donor-star class admitted by verify_idle_overlay.py (receiver gets exactly one 3-axis triple -> rank 51).
Every assignment of donors to receivers in each (replica, port) group is enumerated (as #1305's builder does), but axis triples
are chosen by exact backtracking instead of greedily.  Group weights are #1305's own selection weights.
usage: idle_optimum.py STRICT_GLOBAL_DIR OWNERS.json.gz OUT.json  (STRICT_GLOBAL_DIR = <#1305 verify work>/strict/global)"""
import gzip, json, sys, itertools, collections
from pathlib import Path
import hashlib
G = Path(sys.argv[1]); OWN = Path(sys.argv[2]); OUT = Path(sys.argv[3])
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rd = lambda p: json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())
dot = lambda a, b: (int(a) & int(b)).bit_count() & 1
frames = rd(G / 'hosted-baseline/IDLE-REMAINDER-FRAMES.json.gz')
phases = rd(G / 'base/work/complex-nine-native/DATA-PHASES.json'); recipes = {r['port']: r for r in phases['recipes']}
owners = rd(OWN); owner_slots = {(x['owner_replica'], x['port'], x['child']) for x in owners}
ov = json.loads((G / 'hosted/IDLE-PAIR-OVERLAY.json').read_text())
print('idle frames', len(frames), 'rank hist', sorted(collections.Counter(r['rank'] for r in frames).items())[:12], '...')
elig = collections.defaultdict(list); why = collections.Counter()
for r in frames:
    k = (r['replica'], r['port'], r['child'])
    if r['rank'] != 48: why['rank!=48'] += 1; continue
    if r['hosted'] != 0: why['hosted'] += 1; continue
    if r['pending_offset'] != 0: why['pending'] += 1; continue
    if k in owner_slots: why['owner'] += 1; continue
    elig[r['replica'], r['port']].append(r)
print('rank48 exclusions', dict(why), 'eligible', sum(map(len, elig.values())), 'groups', len(elig))
print('group sizes', sorted(collections.Counter(map(len, elig.values())).items()))
Gw = {36: -2.4520183911866953e-09, 39: -1.9171680322068257e-09, 42: -1.3276966099980976e-09, 45: -6.875123312271499e-10, 48: 0.0, 51: 7.318804853566615e-10}
cur = collections.defaultdict(list)
for d in ov['donors']: cur[d['replica'], d['port']].append(len(d['receivers']))
def feasible(lists):
    """disjoint 3-subsets, one per receiver, from the given axis lists (exact backtracking)."""
    lists = sorted(lists, key=len)
    def bt(i, used):
        if i == len(lists): return True
        cand = [v for v in lists[i] if v not in used]
        if len(cand) < 3: return False
        for t in itertools.combinations(cand, 3):
            if bt(i + 1, used | set(t)): return True
        return False
    return bt(0, frozenset())
better = []; stats = collections.Counter(); tot_cur = tot_opt = 0.0
for (rep, port), rows in sorted(elig.items()):
    rec = recipes[port]; m = len(rows)
    ys = [int(s[k]) for s in rec['stage_alignment'] for k in ('entry_Y', 'exit_Y')] + [int(rec['terminal_Y_translation'])]
    xs = [int(s[k]) for s in rec['stage_alignment'] for k in ('entry_X', 'exit_X')]
    ax = [list(map(int, r['orthogonal_axes'])) for r in rows]
    mov = {}
    for i in range(m):
        for j in range(m):
            if i != j:
                tr = [int(rec['idle_children'][c]['translation_after']) for c in (rows[i]['child'], rows[j]['child'])]
                mov[i, j] = [v for v in ax[i] if all(dot(v, x) == 0 for x in ax[j] + ys + xs + tr)]
    best = 0.0; bestshape = ()
    for assign in itertools.product(range(-1, m), repeat=m):
        if any(assign[j] == j for j in range(m)): continue
        donors = set(d for d in assign if d >= 0)
        if any(assign[d] >= 0 for d in donors): continue
        serve = {d: [j for j in range(m) if assign[j] == d] for d in donors}
        val = sum(Gw[48 - 3 * len(v)] + len(v) * Gw[51] for v in serve.values())
        if val <= best + 1e-30: continue
        if all(feasible([mov[d, j] for j in rs]) for d, rs in serve.items()):
            best = val; bestshape = tuple(sorted(len(v) for v in serve.values()))
    c = sum(Gw[48 - 3 * k] + k * Gw[51] for k in cur.get((rep, port), []))
    tot_cur += c; tot_opt += best
    stats[(m, tuple(sorted(cur.get((rep, port), []))), bestshape)] += 1
    if best > c + 1e-25: better.append(((rep, port), m, sorted(cur.get((rep, port), [])), bestshape, best - c))
print('value current %.6e optimum %.6e  groups improvable %d' % (tot_cur, tot_opt, len(better)))
for k, v in sorted(stats.items()): print('  m=%d current=%s optimum=%s : %d groups' % (k[0], k[1], k[2], v))
for b in better[:10]: print('  better', b)

rec = dict(status='PASS_1305_IDLE_SELECTION_EQUALS_EXACT_GROUP_OPTIMUM' if not better else 'IMPROVABLE_GROUPS_FOUND',
           inputs={n: sha(G / n) for n in ('hosted-baseline/IDLE-REMAINDER-FRAMES.json.gz', 'hosted/IDLE-PAIR-OVERLAY.json', 'base/work/complex-nine-native/DATA-PHASES.json')},
           owners_sha256=sha(OWN), eligible=sum(map(len, elig.values())), groups=len(elig),
           group_sizes={str(k): v for k, v in sorted(collections.Counter(map(len, elig.values())).items())},
           shapes=[dict(size=k[0], current=list(k[1]), optimum=list(k[2]), groups=v) for k, v in sorted(stats.items())],
           value_current=repr(tot_cur), value_optimum=repr(tot_opt), improvable_groups=len(better),
           donors=len(ov['donors']), receivers=sum(len(d['receivers']) for d in ov['donors']), profile=ov['profile'])
OUT.write_text(json.dumps(rec, indent=2, sort_keys=True) + '\n'); print(rec['status'])
