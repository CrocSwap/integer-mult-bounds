"""Entrance promotions E4 -> E5 of whole kernel groups: deterministic constructor.  Apache-2.0.
BlockInvert (Claude Code research agent) for the gauge44 lineage.

usage: build_promotion.py --input FULL-WORD.json.gz --recipe PROMO-RECIPE.json --out DIR

The recipe is data only:
  input_content_sha256   sha256 of the decompressed input word (pinned);
  entrances              {helper: frame vectors}: new start frames (each strictly contains the old one);
  gate_frames            [[section, index, old frame, new frame], ...]: section 'A' / 'B' (main gates) or 'T'
                         (early_cleanup entry index); the old frame must match the input exactly (as a span);
  expected               output_content_sha256, local_profile, width_inventory.
The scalar program is unchanged (only frame annotations and start frames move), so the endpoint, the
zero-target-response entrance condition and every cone are those of the input; the independent audit
(audit_local.py) re-checks all of them, plus monotone chains and the recomputed profile/widths."""
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
            for j in list(p):
                if p[j] >> k & 1: p[j] ^= x
            p[k] = x
    return tuple(p[k] for k in sorted(p, reverse=True))


def regs(e): return [e[1]] + ([e[2]] if e[0] == 'add' else [])


def chain_profile(w):
    """paid climbs of the A, B, early-tail and final chains, target ends included (centre descents unchanged, not counted)."""
    v, R = w['report']['v'], w['report']['R']; n = 2*v + R
    cur = [() for _ in range(n)]
    for i, p in enumerate(w['ports']): cur[i] = span([p])
    for r, f in w.get('start_extra', {}).items(): cur[int(r)] = span(f)
    prof = Counter()

    def climb(r, F):
        assert span(list(cur[r]) + list(F)) == F, ('nonmonotone', r)
        if len(F) > len(cur[r]): prof[len(F) - len(cur[r])] += 1
        cur[r] = F
    for part in ('A', 'B'):
        for e in w[part]:
            for r in regs(e): climb(r, span(e[-1]))
    for i, f in w.get('early_cleanup', []):
        for r in regs(w['cleanup'][i]): climb(r, span(f))
    full = span([1 << i for i in range(9)])
    final = {int(r): span(f) for r, f in w.get('helper_final', {}).items()}
    for r in range(n):
        if v <= r < 2*v:     # targets end at their port hyperplane (as in the independent audit); counted on both sides
            climb(r, span([x for x in range(1, 512) if (x & w['ports'][r - v]).bit_count() % 2 == 0])); continue
        climb(r, final.get(r, full))
    return prof


def widths(w):
    v, R = w['report']['v'], w['report']['R']; full = [1 << i for i in range(9)]
    return Counter(len(span(w['helper_final'].get(str(r), full))) - len(span(w['start_extra'].get(str(r), [])))
                   for r in range(2*v, 2*v + R))


def apply(w, r):
    nw = json.loads(json.dumps(w))
    for h, F in r['entrances'].items():
        assert h in nw['start_extra'], ('not an entering helper', h)
        old, new = span(nw['start_extra'][h]), span(F)
        assert len(new) > len(old) and span(list(old) + list(new)) == new, ('not a promotion', h)
        nw['start_extra'][h] = list(new)
    for sec, i, old, new in r['gate_frames']:
        if sec in ('A', 'B'):
            assert span(nw[sec][i][-1]) == span(old), ('gate frame mismatch', sec, i)
            nw[sec][i][-1] = list(span(new))
        else:
            assert sec == 'T' and span(nw['early_cleanup'][i][1]) == span(old), ('tail frame mismatch', i)
            nw['early_cleanup'][i][1] = list(span(new))
    old_prof, new_prof = chain_profile(w), chain_profile(nw)
    lp = Counter({int(k): c for k, c in w['report']['local_profile'].items()}); lp.subtract(old_prof); lp.update(new_prof)
    assert min(lp.values()) >= 0
    inv = widths(nw)
    rep = dict(w['report'])
    rep['local_profile'] = {str(k): c for k, c in sorted(lp.items()) if c}
    rep['local_rank_mass'] = sum(k*c for k, c in lp.items())
    rep['width_inventory'] = {str(k): c for k, c in sorted(inv.items()) if c}
    nw['report'] = rep
    return nw


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--recipe', type=Path, required=True); ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    raw = gzip.decompress(a.input.read_bytes()); r = json.loads(a.recipe.read_text())
    assert hashlib.sha256(raw).hexdigest() == r['input_content_sha256'], 'input word pin'
    nw = apply(json.loads(raw), r)
    data = json.dumps(nw, separators=(',', ':')).encode()
    x = r['expected']
    assert nw['report']['local_profile'] == x['local_profile'], 'profile pin'
    assert nw['report']['width_inventory'] == x['width_inventory'], 'width pin'
    assert hashlib.sha256(data).hexdigest() == x['output_content_sha256'], 'output word pin'
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / 'FULL-WORD.json.gz').write_bytes(gzip.compress(data, mtime=0))
    print('PASS', len(r['entrances']), 'promoted entrances;', len(r['gate_frames']), 'gate frames;',
          'profile', x['local_profile'], 'sha', x['output_content_sha256'])
