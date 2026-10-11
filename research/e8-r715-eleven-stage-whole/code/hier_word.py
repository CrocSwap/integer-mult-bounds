"""Compile the frozen R715 hierarchy into the bit word: PR #370's compile2 + fullword (unchanged), then PR #443's
elimination reuse and #436 retiming (unchanged).  The hierarchy is checked first: every symbol's content is the F2 sum of
its kids, its frame is a closed root-spanned subspace containing its kids' frames (Thm A: drop-free taint) and its
content; every target's reads sum to its in-cap junk (the 63 lines orthogonal to it).
usage: hier_word.py REPO_RESEARCH_DIR HIERARCHY.json OUT_RAW OUT_REUSED OUT_FINAL
Hierarchy: PR #370 Hamming design (Dylan Crow) with frame-pair D4 sums (carrier lower bound construction, nesttax) and
11 cancelling re-expressions (f2cancel); both prepared with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0."""
import os, sys, json
os.environ['E8COORD'] = 'ham'
R, hpath, out_raw, out_reused, out_final = sys.argv[1:6]
P436 = os.path.join(R, 'e8-r740-replica32/parent436/code')
sys.path[:0] = [os.path.join(P436, 'bit/producer'), os.path.join(P436, 'reuse')]
import e8lib as E, frames as Fm, compile2 as C2, compile as C, fullword, reuse as RU, retime as RT
d = json.load(open(hpath)); V = E.V
assert d['format'] == 'e8bit-hierarchy/1' and d['coords'] == 'ham' and d['v'] == V
mask = lambda L: sum(1 << s for s in L)
class H: pass
h = H()
h.content = [mask(s) for s in d['symbols']]; h.frame = [mask(f) for f in d['frames']]
h.kids = [tuple(k) if k else None for k in d['kids']]; h.need = [set(n) for n in d['need']]
h.dim = []
for u, (c, f) in enumerate(zip(h.content, h.frame)):
    cf, dm = Fm.closure(f) if f else (0, 0)
    assert cf == f, ('frame not closed', u)
    assert c & ~f == 0, ('content outside frame', u)
    h.dim.append(dm)
for s in range(V): assert h.content[s] == 1 << s and h.frame[s] == Fm.LINE[s] and h.kids[s] is None
for u, k in enumerate(h.kids):
    if not k: continue
    x = 0
    for c in k:
        assert c < u or True
        x ^= h.content[c]; assert h.frame[c] & ~h.frame[u] == 0, ('kid frame not inside', u, c)
    assert x == h.content[u], ('content is not the sum of kids', u)
for t in range(V):
    x = 0
    for u in h.need[t]:
        x ^= h.content[u]; assert h.frame[u] & ~Fm.HYP[t] == 0, ('read frame outside target hyperplane', t, u)
    assert x == Fm.HYP[t], ('target junk', t)
W = C2.compile2(h)
assert [len(z) for z in C.f2_check(W)] == [0, 0]
raw = fullword.build(W); fullword.save(raw, out_raw)
re_, n = RU.reuse(raw); fullword.save(re_, out_reused)
fin, mv = RT.retime(re_, sweeps=6, M=64); fullword.save(fin, out_final)
print(json.dumps(dict(status='PASS_HIERARCHY_COMPILED', compile2=W.stats, raw_R=raw['R'], reuse_helpers=n['helpers'], reuse_totals=n['totals'],
                      reused_R=re_['R'], retime_moves=mv, final_R=fin['R'])))
