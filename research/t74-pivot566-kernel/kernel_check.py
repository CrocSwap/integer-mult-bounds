"""kernel_check.py: the pivot-566 kernel's restoration argument, checked exactly over the whole program (standard library).

Program semantics are those of the unchanged independent audit_local.py (#645): precondition + compensation + A + cut +
B + early-cleanup tail + remaining cleanup, where the compensation is derived from the helper columns of the port rows of
the A + cut + B map. For PR1297's two words (gauge44, extra) and the kernel words shipped in inputs/, with exact Fractions:
  1. Edits. inputs/EDITS.json applied to PR1297's word gives the shipped word's scalar program; precondition, A, cut,
     remaining cleanup and interfaces are unchanged; no inserted gate writes q = 566.
  2. Lemma. Every inserted read of q (new program) and the deleted read B755 (old program) happens while q holds its
     initial value x_q (q's row is e_q from the start of the program). Then new - old = x_q * D with
     D = sum_i c_i S_i e_{t_i}, where term i adds c_i * q to t_i and S_i runs the common gates after it. So only the q
     column can change, and D is the whole difference.
  3. Ledger. The nine terms are propagated separately. D = 0 at the end of the tail. At the end of B, D touches no port
     register, so the derived compensation (helper columns of the port rows) cannot change; the compensation gates are
     also derived for both words and compared.
  4. Frames. The paid profile is recounted from each word's frames (audit_local's climb rules); the register chains
     whose paid jumps change are listed. They give the per-call H1 +1, H2 -2, H3 +1.
  5. Controls. Dropping the 98 restore, restoring 98 before q's own restoration, flipping a donor sign and keeping the
     deleted read each break step 2 or 3.
usage: python3 -B kernel_check.py [--json OUT]"""
import argparse, copy, gzip, json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
if not __debug__:
    raise SystemExit('kernel_check.py: run without -O / PYTHONOPTIMIZE (its assert statements are the checks)')
PKG = Path(__file__).resolve().parent; ROOT = PKG.parents[1]
SRC = ROOT / 'research/global-mixed-t74-exact-fill/vendor/pr1297'
WORDS = {'gauge44': (SRC / 'gauge44-word.json.gz', PKG / 'inputs/gauge44-word-566.json.gz'),
         'extra': (SRC / 'extra-word.json.gz', PKG / 'inputs/extra-word-566.json.gz')}
INTERFACE = ('A', 'cut', 'precondition', 'ports', 'centers', 'center_frames', 'start_extra', 'helper_final', 'root_lines', 'scatter', 'target_levels')
def load(p): return json.loads(gzip.decompress(Path(p).read_bytes()))
def ops(g): return list(g[:-1])
def coef(g): return Q(g[3], g[4]) if g[0] == 'add' else Q(g[2], g[3])
def apply(g, rows):
    """state rows: rows[r] = linear form of register r in the initial values (dict register -> Fraction)."""
    t = g[1]; c = coef(g); assert c != 0
    if g[0] == 'add':
        assert g[2] != t, 'self add'
        d = rows.setdefault(t, {t: Q(1)})
        for k, x in rows.get(g[2], {g[2]: Q(1)}).items():
            y = d.get(k, 0) + c * x
            if y: d[k] = y
            else: d.pop(k, None)
    else:
        rows[t] = {k: x * c for k, x in rows.get(t, {t: Q(1)}).items()}
def push(g, delta):
    """propagate a state difference through one gate (the gate is linear, so differences propagate alone)."""
    t = g[1]; c = coef(g)
    if g[0] == 'add':
        x = delta.get(g[2])
        if x:
            y = delta.get(t, 0) + c * x
            if y: delta[t] = y
            else: delta.pop(t, None)
    elif t in delta: delta[t] = delta[t] * c
def compensation(w):
    v = w['report']['v']; raw = {}
    for g in w['A'] + w['cut'] + w['B']: apply(ops(g), raw)
    dirt = {y: {k: a for k, a in raw.get(y, {y: Q(1)}).items() if k >= 2 * v} for y in range(v, 2 * v)}
    for g in w['precondition']:                       # as audit_local: the precondition acts on the dirt rows
        g = ops(g); t = g[1]; c = coef(g)
        if g[0] == 'add':
            d = dirt.setdefault(t, {})
            for k, x in dirt.get(g[2], {}).items():
                y = d.get(k, 0) + c * x
                if y: d[k] = y
                else: d.pop(k, None)
        else: dirt[t] = {k: x * c for k, x in dirt.get(t, {}).items()}
    return [['add', y, k, -a.numerator, a.denominator] for y in range(v, 2 * v) for k, a in sorted(dirt.get(y, {}).items())]
def compile_tagged(w, ed):
    """the edited B and tail with provenance: ('com', original index) for kept gates, ('ins', j) / ('tins', j) for inserts."""
    dele = set(ed['delete']); at = {}
    for j, (p, g) in enumerate(ed['insert']): at.setdefault(p, []).append((('ins', j), ops(g)))
    B = []
    for i, e in enumerate(w['B']):
        B.extend(at.get(i, []))
        if i not in dele: B.append((('com', i), ops(e)))
    B.extend(at.get(len(w['B']), []))
    C = [ops(g) for g in w['cleanup']]; early = [(('com', i), i) for i, U in w['early_cleanup']]; ins = []
    for j, (pos, g) in enumerate(ed['tail']): C.append(ops(g)); ins.append((pos, len(C) - 1, j))
    for pos, ci, j in sorted(ins): early.insert(pos, (('tins', j), ci))
    return B, C, early
def climb_profile(w):
    """audit_local's paid-jump recount, also returning each register's list of paid jumps (and the centre-path jumps)."""
    def basis(vs):
        piv = {}
        for a in vs:
            while a:
                b = a.bit_length() - 1
                if b in piv: a ^= piv[b]
                else: piv[b] = a; break
        for k in sorted(piv):
            for j in piv:
                if j > k and piv[j] >> k & 1: piv[j] ^= piv[k]
        return tuple(piv[k] for k in sorted(piv, reverse=True))
    v, h, R = w['report']['v'], w['report']['h'], w['report']['R']; n = 2 * v + R; full = basis([1 << i for i in range(h)])
    end = [full] * v + [basis([x for x in range(1, 1 << h) if (x & p).bit_count() % 2 == 0]) for p in w['ports']] + [full] * R
    for q, U in w.get('helper_final', {}).items(): end[int(q)] = basis(U)
    cur = [(p,) for p in w['ports']] + [()] * (v + R)
    for q, U in w.get('start_extra', {}).items(): cur[int(q)] = basis(U)
    jumps = {r: [] for r in range(n)}; centre = []
    def climb(q, U):
        U = basis(U); d = len(U) - len(cur[q]); assert basis(cur[q] + U) == U, 'frame not monotone'
        if d: jumps[q].append(d)
        cur[q] = U
    for section in ('A', 'B'):
        if section == 'B':
            lev = {int(t): basis(U) for t, U in w.get('target_levels', {}).items()}
            for q, U in zip(w['centers'], w['center_frames']):
                U = basis(U)
                for T in sorted({lev.get(e[1] - v, ()) for e in w['cut'] if e[2] == q}, key=lambda x: -len(x)):
                    if T != U: centre.append(len(U) - len(T))
                    U = T
        for e in w[section]:
            for q in (e[1:3] if e[0] == 'add' else e[1:2]): climb(q, e[-1])
    for i, U in w['early_cleanup']:
        e = w['cleanup'][i]
        for q in (e[1:3] if e[0] == 'add' else e[1:2]): climb(q, U)
    for q, U in enumerate(end): climb(q, U)
    prof = Counter(d for r in jumps for d in jumps[r]) + Counter(centre)
    return dict(sorted(prof.items())), jumps
def scalar(base, B1, C1, E1, ed, q):
    """steps 2-3 for the edited program (B1, C1, E1) of `base`."""
    v = base['report']['v']; res = {}
    inserted = [g for t, g in B1 if t[0] == 'ins'] + [C1[ci] for t, ci in E1 if t[0] == 'tins']
    res['inserted_gates_read_only_q'] = all(g[0] == 'add' and g[2] == q and g[1] != q for g in inserted)
    # 2. lemma: q's row at every new read (new program) and at the deleted read (old program), from the program start
    pre = [ops(g) for g in base['precondition']] + compensation(base) + [ops(g) for g in base['A'] + base['cut']]
    def run(seq, probe):
        rows = {}
        for g in pre: apply(g, rows)
        seen = []
        for tag, g in seq:
            if probe(tag): seen.append(rows.get(q, {q: Q(1)}) == {q: Q(1)})
            apply(g, rows)
        return seen, rows
    new_seq = B1 + [(t, C1[ci]) for t, ci in E1]
    old_seq = [(('del', i) if i in ed['delete'] else ('com', i), ops(g)) for i, g in enumerate(base['B'])] + \
              [(('com', i), ops(base['cleanup'][i])) for i, U in base['early_cleanup']]
    seen_new, rows_new = run(new_seq, lambda t: t[0] in ('ins', 'tins'))
    seen_old, rows_old = run(old_seq, lambda t: t[0] == 'del')
    res['lemma_new_reads_see_initial_q'] = len(seen_new) == len(inserted) and all(seen_new)
    res['lemma_deleted_read_sees_initial_q'] = len(seen_old) == len(ed['delete']) and all(seen_old)
    # 3. ledger: each term's offset (the coefficient of x_q) propagated through the common gates after it
    terms = []
    for pos, (tag, g) in enumerate(new_seq):
        if tag[0] in ('ins', 'tins'):
            terms.append(dict(term=('B insert %d' if tag[0] == 'ins' else 'tail insert %d') % tag[1], target=g[1], coefficient=coef(g), seq=new_seq, nB=len(B1), pos=pos))
    for pos, (tag, g) in enumerate(old_seq):
        if tag[0] == 'del': terms.append(dict(term='deleted B%d' % tag[1], target=g[1], coefficient=-coef(g), seq=old_seq, nB=len(base['B']), pos=pos))
    total_B, total = Counter(), Counter(); ledger = []
    for term in terms:
        delta = {term['target']: term['coefficient']}; dB = {} if term['pos'] >= term['nB'] else None
        for k in range(term['pos'] + 1, len(term['seq'])):
            if k == term['nB']: dB = dict(delta)
            tag, g = term['seq'][k]
            if tag[0] == 'com': push(g, delta)
        if dB is None: dB = dict(delta)
        total_B.update(dB); total.update(delta)
        ledger.append(dict(term=term['term'], gate='%d += (%s) q' % (term['target'], term['coefficient']),
                           offset_end_of_B={str(k): str(x) for k, x in sorted(dB.items())}, offset_end_of_tail={str(k): str(x) for k, x in sorted(delta.items())}))
    total = {k: x for k, x in total.items() if x}; total_B = {k: x for k, x in total_B.items() if x}
    res['ledger'] = ledger
    res['D_end_of_tail'] = {str(k): str(x) for k, x in sorted(total.items())}
    res['D_end_of_tail_zero'] = not total
    res['D_end_of_B'] = {str(k): str(x) for k, x in sorted(total_B.items())}
    res['D_end_of_B_touches_no_port'] = all(not (v <= k < 2 * v) for k in total_B)
    keys = set(rows_new) | set(rows_old)
    res['b_tail_rows_differing'] = sum(1 for k in keys if rows_new.get(k, {k: Q(1)}) != rows_old.get(k, {k: Q(1)}))
    edited = dict(base, B=[g + [[]] for t, g in B1])
    c0, c1 = compensation(base), compensation(edited)
    res['compensation_gates'] = len(c0); res['compensation_identical'] = c0 == c1
    res['scalar_pass'] = all(res[k] for k in ('inserted_gates_read_only_q', 'lemma_new_reads_see_initial_q', 'lemma_deleted_read_sees_initial_q',
                                              'D_end_of_tail_zero', 'D_end_of_B_touches_no_port', 'compensation_identical')) and res['b_tail_rows_differing'] == 0
    return res
def analyse(base, new, ed, q):
    """steps 1-4 for one shipped word pair."""
    B1, C1, E1 = compile_tagged(base, ed); res = {}
    res['scalar_program_matches'] = ([g for t, g in B1] == [ops(g) for g in new['B']] and C1 == [ops(g) for g in new['cleanup']]
                                     and [ci for t, ci in E1] == [i for i, U in new['early_cleanup']])
    res['unchanged_outside_B_and_tail'] = all(base.get(k) == new.get(k) for k in INTERFACE)
    rest = lambda w: [ops(g) for i, g in enumerate(w['cleanup']) if i not in {j for j, U in w['early_cleanup']}]
    res['remaining_cleanup_identical'] = rest(base) == rest(new)
    res.update(scalar(base, B1, C1, E1, ed, q))
    res['compensation_identical_shipped_word'] = compensation(base) == compensation(new)
    p0, j0 = climb_profile(base); p1, j1 = climb_profile(new)
    res['paid_profile'] = dict(ancestor={str(k): x for k, x in p0.items()}, kernel={str(k): x for k, x in p1.items()})
    res['paid_profile_matches_reports'] = (p0 == {int(k): x for k, x in base['report']['local_profile'].items()} and p1 == {int(k): x for k, x in new['report']['local_profile'].items()})
    dp = Counter(p1); dp.subtract(Counter(p0)); res['paid_profile_delta'] = {str(k): x for k, x in sorted(dp.items()) if x}
    res['changed_chains'] = {str(r): dict(ancestor=j0[r], kernel=j1[r]) for r in sorted(j0) if Counter(j0[r]) != Counter(j1[r])}
    res['pass'] = res['scalar_pass'] and all(res[k] for k in ('scalar_program_matches', 'unchanged_outside_B_and_tail', 'remaining_cleanup_identical',
                                                              'compensation_identical_shipped_word', 'paid_profile_matches_reports'))
    return res
CONTROLS = {
    'dropped 98 restore (tail insert removed)': lambda ed: ed.update(tail=[]),
    '98 restored before q is restored (tail position 85)': lambda ed: ed['tail'][0].__setitem__(0, 85),
    'donor 672 opened with +2q': lambda ed: ed['insert'][3][1].__setitem__(3, 2),
    'deleted read B755 kept': lambda ed: ed.update(delete=[]),
}
def controls(base, ed, q):
    out = {}
    for name, mutate in CONTROLS.items():
        e = copy.deepcopy(ed); mutate(e); r = scalar(base, *compile_tagged(base, e), e, q)
        out[name] = dict(rejected=not r['scalar_pass'], broken=[k for k in ('lemma_new_reads_see_initial_q', 'D_end_of_tail_zero', 'D_end_of_B_touches_no_port', 'compensation_identical') if not r[k]],
                         b_tail_rows_differing=r['b_tail_rows_differing'])
    return out
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--json'); a = ap.parse_args()
    E = json.loads((PKG / 'inputs/EDITS.json').read_text(encoding='utf-8')); out = {}
    for name, (bp, npth) in WORDS.items():
        base = load(bp); r = analyse(base, load(npth), E['edit'], E['pivot']); r['controls'] = controls(base, E['edit'], E['pivot'])
        r['pass'] = r['pass'] and all(c['rejected'] for c in r['controls'].values()); out[name] = r
        print(name, 'PASS' if r['pass'] else 'FAIL', {k: v for k, v in r.items() if k not in ('ledger', 'changed_chains', 'paid_profile', 'controls')}, flush=True)
        for c, x in r['controls'].items(): print('   control', c, x, flush=True)
    if a.json: Path(a.json).write_text(json.dumps(out, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    sys.exit(0 if all(r['pass'] for r in out.values()) else 1)
