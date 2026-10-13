"""Hyperplane-ended helpers (HPE) constructor.  Apache-2.0.  Prepared with Claude Code assistance.

usage: build_hpe.py --input FULL-WORD.json.gz --recipe RECIPE.json --out DIR

RECIPE: {"changes": [{"helper": h, "cleanup_index": i, "frame": [raw vectors]}, ...], "output_content_sha256": hex}.
Each change must be an admissible early-cleanup move:
  * h is an entering helper (start_extra) touched by exactly one cleanup gate, cleanup[i];
  * cleanup[i] commutes with every earlier cleanup gate on its registers (commute(): neither writes a register the
    other touches, or both add into one target without reading each other's target), so it commutes with the whole
    skipped cleanup prefix; in practice the skipped gates only read the partner (x -= p);
  * frame == join of the registers' last A/B frames and has dimension < 9.
The output word gets early_cleanup [[i, U]], helper_final {h: U} and the exact paid profile (only the two registers'
final chains change: h ends at U instead of FULL; the partner climbs through U).  Exactness of the reordered program,
the frame chains and the profile are re-checked independently by hpe_audit_and_transport.py; the paired control audit
is controls_hpe_atc.py."""
import argparse, gzip, hashlib, json
from collections import Counter
from pathlib import Path


def span(vs):
    p = {}
    for x in vs:
        for k in sorted(p, reverse=True):
            if x >> k & 1: x ^= p[k]
        if x:
            k = x.bit_length() - 1
            for j in p:
                if p[j] >> k & 1: p[j] ^= x
            p[k] = x
    return [p[k] for k in sorted(p, reverse=True)]


def regs(e): return [e[1]] + ([e[2]] if e[0] == 'add' else [])


def commute(a, b):
    """Sufficient syntactic commutation of two scalar gates (t += q*s, t *= q): neither writes a register the other
    touches, or both are additions into the same target with neither reading the other's target."""
    ra, rb = set(regs(a)), set(regs(b))
    if a[1] not in rb and b[1] not in ra: return True
    return a[0] == 'add' and b[0] == 'add' and a[1] == b[1] and a[2] != b[1] and b[2] != a[1]


def last_frames(w):
    v, R = w['report']['v'], w['report']['R']; n = 2*v + R
    cur = [[] for _ in range(n)]
    for i, p in enumerate(w['ports']): cur[i] = [p]
    for r, f in w.get('start_extra', {}).items(): cur[int(r)] = list(f)
    for part in ('A', 'B'):
        for e in w[part]:
            for r in regs(e): cur[r] = list(e[-1])
    return cur


def apply(w, changes):
    assert 'early_cleanup' not in w and 'helper_final' not in w, 'input already has hyperplane-ended helpers'
    v, R = w['report']['v'], w['report']['R']; n = 2*v + R
    cur = last_frames(w); count = Counter(); first = {}; on = {}
    for i, e in enumerate(w['cleanup']):
        for r in regs(e): count[r] += 1; first.setdefault(r, i); on.setdefault(r, []).append(i)
    lp = Counter({int(r): c for r, c in w['report']['local_profile'].items()})
    seen = set()
    for z in changes:
        h, i, U = z['helper'], z['cleanup_index'], z['frame']
        assert 2*v <= h < n and str(h) in w['start_extra'], ('not an entering helper', h)
        assert count[h] == 1 and first[h] == i, ('helper must have exactly this one cleanup gate', h)
        e = w['cleanup'][i]; rs = regs(e)
        assert all(commute(w['cleanup'][j], e) for r in rs for j in on[r] if j < i), ('cleanup gate does not commute with the skipped cleanup gates on its registers', i)
        assert not seen & set(rs), 'registers shared between changes'; seen |= set(rs)
        assert span([x for r in rs for x in cur[r]]) == U and len(U) < 9, ('frame is not the join of the last frames', h)
        for r in rs:  # old: last -> FULL; new: last -> U (-> FULL for the partner)
            d0 = 9 - len(span(cur[r]))
            if d0: lp[d0] -= 1
            d1 = len(U) - len(span(cur[r]))
            if d1: lp[d1] += 1
            if r != h and len(U) < 9: lp[9 - len(U)] += 1
    w['early_cleanup'] = [[z['cleanup_index'], z['frame']] for z in changes]
    w['helper_final'] = {str(z['helper']): z['frame'] for z in changes}
    w['report']['local_profile'] = {str(r): c for r, c in sorted(lp.items()) if c}
    w['report']['local_rank_mass'] = sum(r*c for r, c in lp.items())
    if 'width_inventory' in w['report']:  # descriptive metadata: one width-w helper becomes width w-(9-dim U)
        inv = Counter({int(k): c for k, c in w['report']['width_inventory'].items()})
        for z in changes:
            e = len(w['start_extra'][str(z['helper'])]); inv[9 - e] -= 1; inv[len(z['frame']) - e] += 1
        assert min(inv.values()) >= 0
        w['report']['width_inventory'] = {str(k): c for k, c in sorted(inv.items()) if c}
    assert min(lp.values()) >= 0
    return w


def candidates(w):
    v, R = w['report']['v'], w['report']['R']; n = 2*v + R
    cur = last_frames(w); count = Counter(); first = {}; on = {}
    for i, e in enumerate(w['cleanup']):
        for r in regs(e): count[r] += 1; first.setdefault(r, i); on.setdefault(r, []).append(i)
    out = []
    for h in range(2*v, n):
        if count[h] != 1 or str(h) not in w.get('start_extra', {}): continue
        i = first[h]; rs = regs(w['cleanup'][i])
        if not all(commute(w['cleanup'][j], w['cleanup'][i]) for r in rs for j in on[r] if j < i): continue
        U = span([x for r in rs for x in cur[r]])
        if len(U) < 9: out.append(dict(helper=h, cleanup_index=i, frame=U))
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--input', type=Path, required=True); ap.add_argument('--recipe', type=Path)
    ap.add_argument('--out', type=Path); ap.add_argument('--nominate', type=Path, help='write a recipe with every candidate')
    a = ap.parse_args()
    w = json.loads(gzip.decompress(a.input.read_bytes()))
    if a.nominate:
        a.nominate.write_text(json.dumps(dict(changes=candidates(w), output_content_sha256=''), indent=1) + '\n', newline='\n')
        raise SystemExit(0)
    r = json.loads(a.recipe.read_bytes())
    w = apply(w, r['changes'])
    raw = json.dumps(w, sort_keys=True, separators=(',', ':')).encode(); h = hashlib.sha256(raw).hexdigest()
    assert h == r['output_content_sha256'], h
    a.out.mkdir(parents=True, exist_ok=False)
    (a.out/'FULL-WORD.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    (a.out/'HPE-CONSTRUCTION.json').write_text(json.dumps(dict(status='PASS_HYPERPLANE_ENDED_HELPERS', helpers=[z['helper'] for z in r['changes']],
        local_profile=w['report']['local_profile']), indent=1) + '\n', newline='\n')
    print('PASS', len(r['changes']), 'hyperplane-ended helpers')
