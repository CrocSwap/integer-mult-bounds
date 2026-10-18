"""Cold low-frame-ended helpers with a refactored exact cleanup: constructor.  Apache-2.0.
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

usage: build_cold_end.py --input FULL-WORD.json.gz --recipe RECIPE.json.gz --out DIR

The input is a hyperplane-ended (HPE) provider word.  RECIPE (all data, no code):
  premix        rank-0 gates on helpers at their start frame (frame [] for cold helpers, E for entering ones); they become the
                head of section A, i.e. they run after the entry
                adapters and paid wrappers, so every gate on a cold-ended helper follows its wrapper R_{0,U}^-1;
  cleanup       the complete new cleanup gate list (an exact refactorisation of the inverse, not the literal one);
  early_cleanup [[cleanup index, frame], ...]: gates run right after B at the given frame (the multi-gate tail);
  cold_ends     {helper: frame}: cold helpers (no entrance) that end at that frame instead of FULL;
  entering_ends optional {helper: frame}: further entering helpers ending below FULL under the same refactored cleanup;
  refactored_cleanup  descriptive metadata copied into the word (it also switches the transport audit from the literal
                cleanup assertion to exact replay of the refactored one);
  output_content_sha256.
The constructor only splices.  It checks the recipe's shape (premix on cold helpers at frame [], cold ends on cold
helpers, every inherited hyperplane-end gate and terminal frame kept) and recomputes the paid local profile and the
descriptive width inventory from the actual frame chains.  Exactness of the scalar program, all frame chains, the cone
pre-check, the wrapper order and the profile are re-checked independently by hpe_audit_and_transport.py; the paired
raw-word mutation audit is cold_end_controls.py."""
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
    return tuple(p[k] for k in sorted(p, reverse=True))


def regs(e): return [e[1]] + ([e[2]] if e[0] == 'add' else [])


def chain_profile(w):
    """Paid climbs of the A, B, tail and final chains (centre descents are unchanged by this step and not counted)."""
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
        if v <= r < 2*v: continue      # targets end at their port level; unchanged by this step (same A/B chains)
        climb(r, final.get(r, full))
    return prof, cur


def apply(w, r):
    assert 'helper_final' in w and 'early_cleanup' in w and 'refactored_cleanup' not in w, 'input must be an HPE word'
    v, R = w['report']['v'], w['report']['R']; n = 2*v + R
    entering = set(map(int, w['start_extra']))
    cold = {x for x in range(2*v, n) if x not in entering}
    start = lambda x: span(w['start_extra'].get(str(x), []))
    for e in r['premix']:   # rank 0: every register is a helper still at its start frame (cold: [], entering: E) = the gate frame
        assert e[0] in ('add', 'scale') and all(2*v <= x < n and start(x) == span(e[-1]) for x in regs(e)), ('premix gate not rank-0 on helpers at their start frame', e)
    ends = {int(h): f for h, f in r['cold_ends'].items()}
    assert ends and all(h in cold and str(h) not in w['helper_final'] for h in ends), 'cold ends must be new cold helpers'
    eends = {int(h): f for h, f in r.get('entering_ends', {}).items()}   # optional: further ENTERING helpers ending below FULL
    assert all(h in entering and str(h) not in w['helper_final'] for h in eends), 'entering ends must be new entering helpers'
    assert all(len(span(f)) < 9 for f in list(ends.values()) + list(eends.values()))
    new_early = [(i, f) for i, f in r['early_cleanup']]
    kept = {(json.dumps(r['cleanup'][i][:-1]), json.dumps(f)) for i, f in new_early}
    for i, f in w['early_cleanup']:     # every inherited hyperplane-end gate stays in the tail at its frame
        assert (json.dumps(w['cleanup'][i][:-1]), json.dumps(f)) in kept, ('inherited HPE gate missing', i)
    old_prof, _ = chain_profile(w)
    out = dict(w)
    out['A'] = [list(e) for e in r['premix']] + w['A']
    out['cleanup'] = r['cleanup']
    out['early_cleanup'] = [[i, f] for i, f in new_early]
    out['helper_final'] = dict(w['helper_final'], **{str(h): f for h, f in sorted({**ends, **eends}.items())})
    out['refactored_cleanup'] = r['refactored_cleanup']
    new_prof, cur = chain_profile(out)
    assert all(cur[h] == span(f) for h, f in {**ends, **eends}.items()), 'end frame is not the last frame of the helper'
    lp = Counter({int(k): c for k, c in w['report']['local_profile'].items()})
    lp.subtract(old_prof); lp.update(new_prof)
    assert min(lp.values()) >= 0
    rep = dict(w['report'])
    rep['local_profile'] = {str(k): c for k, c in sorted(lp.items()) if c}
    rep['local_rank_mass'] = sum(k*c for k, c in lp.items())
    inv = Counter({int(k): c for k, c in w['report']['width_inventory'].items()})
    for h, f in ends.items(): inv[9] -= 1; inv[len(span(f))] += 1      # cold: width = |U| - 0
    for h, f in eends.items():                                          # entering: width = |U| - |E|
        e = len(span(w['start_extra'][str(h)])); inv[9 - e] -= 1; inv[len(span(f)) - e] += 1
    assert min(inv.values()) >= 0
    rep['width_inventory'] = {str(k): c for k, c in sorted(inv.items()) if c}
    out['report'] = rep
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--input', type=Path, required=True); ap.add_argument('--recipe', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    rd = lambda p: json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())
    w, r = rd(a.input), rd(a.recipe)
    w = apply(w, r)
    raw = json.dumps(w, sort_keys=True, separators=(',', ':')).encode(); h = hashlib.sha256(raw).hexdigest()
    assert h == r['output_content_sha256'], h
    a.out.mkdir(parents=True, exist_ok=False)
    (a.out/'FULL-WORD.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    (a.out/'COLD-END-CONSTRUCTION.json').write_text(json.dumps(dict(status='PASS_COLD_LOW_FRAME_ENDS_SPLICED',
        cold_ended_helpers=sorted(int(x) for x in r['cold_ends']), terminal_dims=sorted(Counter(len(span(f)) for f in r['cold_ends'].values()).items()),
        premix_gates=len(r['premix']), early_cleanup_gates=len(r['early_cleanup']), cleanup_gates=len(r['cleanup']),
        local_profile=w['report']['local_profile'], width_inventory=w['report']['width_inventory']), indent=1) + '\n', newline='\n')
    print('PASS', len(r['cold_ends']), 'cold low-frame-ended helpers;', len(r['premix']), 'premix gates;', len(r['cleanup']), 'cleanup gates')
