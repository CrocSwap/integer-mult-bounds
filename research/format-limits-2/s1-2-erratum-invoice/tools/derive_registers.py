"""Derivation of inputs/derived/k492_registers.json (NOT run by verify.part.sh; it needs the rebuilt CANONICAL-WORD files).
usage: derive_registers.py <dir containing ck-local/ and jp8-local/ with CANONICAL-WORD.json.gz> <out.json>

Replays the monotone frame climbs of a CANONICAL-WORD (parts A, centers, B, tail, final) exactly as the hub's emit() does
(same logic as cards/B15/reg.py) and writes, per provider, the list of climb widths of every register, the class sizes
and the word's own local_profile.  Widths are |frame after| - |frame before| (centre cut climbs are the descents to
level 0).  The input words are the ck / jp8 local words rebuilt from the research/complex-k492-owner-repair code of #626."""
import gzip, hashlib, json, sys

def climbs(d):
    F = {(p, i): e[-1] for p in ('A', 'B', 'tail') for i, e in enumerate(d[p])}
    fr = d['frames']; cur = list(d['start']); out = []
    L = lambda f: len(fr[f])
    def climb(r, f):
        if cur[r] == f: return
        out.append((r, L(f) - L(cur[r]))); cur[r] = f
    for part in ('A', 'centers', 'B', 'tail', 'final'):
        if part in ('A', 'B', 'tail'):
            for i, e in enumerate(d[part]):
                for r in [e[1]] + ([e[2]] if e[0] == 'add' else []): climb(r, F[part, i])
        elif part == 'centers':
            for k, r in enumerate(d['centers']):
                cf = d['center_frames'][k]
                terms = [e for e in d['cut'] if e[2] == r]
                path = [cf] + sorted({0 for e in terms} - {cf}, key=lambda x: -L(x))
                for a in range(1, len(path)): out.append((r, L(path[a - 1]) - L(path[a])))
        else:
            for r, f in enumerate(d['final']): climb(r, f)
    return out

res = {}
for prov in ('ck', 'jp8'):
    path = '%s/%s-local/CANONICAL-WORD.json.gz' % (sys.argv[1], prov)
    raw = gzip.open(path).read(); d = json.loads(raw)
    n = 2 * d['v'] + d['R']; regs = [[] for _ in range(n)]
    for r, w in climbs(d): regs[r].append(w)
    res[prov] = {'word_sha256_decompressed': hashlib.sha256(raw).hexdigest(), 'v': d['v'], 'R': d['R'],
                 'centers': d['centers'], 'local_profile': d['local_profile'], 'regs': regs}
json.dump(res, open(sys.argv[2], 'w'), separators=(',', ':'))
