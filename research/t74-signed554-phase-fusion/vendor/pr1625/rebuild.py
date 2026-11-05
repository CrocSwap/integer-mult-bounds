"""rebuild.py: standard-library exactness check of the pivot-566 helper-donor kernel on PR1297's two local words.

For each word (gauge44 = base, extra) it
  1. applies inputs/EDITS.json to PR1297's pinned word with the build_tri/harness edit semantics (B deletes and inserts
     indexed by the ORIGINAL B; early-cleanup tail inserts appended to cleanup and spliced into early_cleanup in
     ascending order) and checks that the scalar program (every gate without its frame annotation, the cleanup list
     and the early-cleanup order) equals the shipped word in inputs/;
  2. checks that A, cut, precondition, ports, centres, start_extra and helper_final are byte-identical (interfaces);
  3. computes the complete linear map of B + early cleanup over every register with exact Fractions for both words
     and checks equality (the edit only rewires reads of pivot 566), and that the remaining cleanup is identical;
  4. checks that every inserted read of 566 lies where 566 holds its initial value (before its B write at the
     original B866, or after the early-cleanup gate that restores it).
Frame annotations of the shipped words are NOT rederived here; the unchanged audit_local.py and the native chain
check them (see verify.py).  usage: python3 -B rebuild.py [--edits PATH] [--json OUT]"""
import argparse, gzip, json, sys
from fractions import Fraction as Q
from pathlib import Path
PKG = Path(__file__).resolve().parent; ROOT = PKG.parents[1]
SRC = ROOT / 'research/global-mixed-t74-exact-fill/vendor/pr1297'
WORDS = {'gauge44': (SRC / 'gauge44-word.json.gz', PKG / 'inputs/gauge44-word-566.json.gz'),
         'extra': (SRC / 'extra-word.json.gz', PKG / 'inputs/extra-word-566.json.gz')}
INTERFACE = ('A', 'cut', 'precondition', 'ports', 'centers', 'center_frames', 'start_extra', 'helper_final', 'root_lines', 'scatter', 'target_levels')
def load(p): return json.loads(gzip.decompress(Path(p).read_bytes()))
def ops(g): return list(g[:-1])
def compile_edits(w, ed):
    B = w['B']; dele = set(ed['delete']); at = {}
    for p, g in ed['insert']: at.setdefault(p, []).append(ops(g))
    out = []
    for i, e in enumerate(B):
        out.extend(at.get(i, []))
        if i not in dele: out.append(ops(e))
    out.extend(at.get(len(B), []))
    assert not ed.get('prepend'), 'this package uses no cleanup prepends'
    C = [ops(g) for g in w['cleanup']]; early = [i for i, U in w['early_cleanup']]; ins = []
    for j, g in ed['tail']: C.append(ops(g)); ins.append((j, len(C) - 1))
    for j, ci in sorted(ins): early.insert(j, ci)
    return out, C, early
def coef(g): return Q(g[3], g[4]) if g[0] == 'add' else Q(g[2], g[3])
def rows(seq):
    R = {}
    for g in seq:
        t = g[1]
        if g[0] == 'add':
            src = R.get(g[2], {g[2]: Q(1)}); d = dict(R.get(t, {t: Q(1)})); c = coef(g)
            for k, x in src.items():
                y = d.get(k, 0) + c * x
                if y: d[k] = y
                else: d.pop(k, None)
            R[t] = d
        else:
            c = coef(g); R[t] = {k: x * c for k, x in R.get(t, {t: Q(1)}).items()}
    return R
def analyse(base, B1, C1, E1, q):
    """Exactness and pivot-window facts of a compiled program (B1, cleanup C1, early order E1) against the base word."""
    res = {}
    seq0 = [ops(g) for g in base['B']] + [ops(base['cleanup'][i]) for i, U in base['early_cleanup']]
    seq1 = list(B1) + [C1[i] for i in E1]
    r0, r1 = rows(seq0), rows(seq1); keys = set(r0) | set(r1)
    res['b_tail_map_rows'] = len(keys); res['b_tail_map_rows_differing'] = sum(1 for k in keys if r0.get(k, {k: Q(1)}) != r1.get(k, {k: Q(1)}))
    rest0 = [ops(g) for i, g in enumerate(base['cleanup']) if i not in {j for j, U in base['early_cleanup']}]
    rest1 = [g for i, g in enumerate(C1) if i not in set(E1)]
    res['remaining_cleanup_identical'] = rest0 == rest1
    writes = [i for i, g in enumerate(seq1) if g[1] == q]
    reads = [i for i, g in enumerate(seq1) if g[0] == 'add' and g[2] == q]
    original = [ops(x) for x in base['B'] if x[0] == 'add' and x[2] == q] + [ops(base['cleanup'][i]) for i, U in base['early_cleanup'] if base['cleanup'][i][0] == 'add' and base['cleanup'][i][2] == q]
    new_reads = [i for i in reads if seq1[i] not in original]
    res['pivot'] = q; res['pivot_writes'] = writes; res['new_read_positions'] = new_reads
    # q holds its initial value before its single B write and again after the early-cleanup gate that restores it
    ok = len(writes) == 2 and rows(seq1[:writes[1] + 1]).get(q, {q: Q(1)}) == {q: Q(1)}
    res['inserted_reads_where_pivot_is_initial'] = ok and all(p < writes[0] or p > writes[1] for p in new_reads)
    res['exact'] = res['b_tail_map_rows_differing'] == 0 and res['remaining_cleanup_identical'] and res['inserted_reads_where_pivot_is_initial']
    return res
def check(name, base, new, ed, q):
    B1, C1, E1 = compile_edits(base, ed)
    res = dict(word=name)
    res['scalar_program_matches'] = (B1 == [ops(g) for g in new['B']] and C1 == [ops(g) for g in new['cleanup']] and E1 == [i for i, U in new['early_cleanup']])
    res['interfaces_identical'] = all(base.get(k) == new.get(k) for k in INTERFACE)
    res.update(analyse(base, B1, C1, E1, q))
    res['pass'] = res['scalar_program_matches'] and res['interfaces_identical'] and res['exact']
    return res
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--edits', default=str(PKG / 'inputs/EDITS.json')); ap.add_argument('--json'); a = ap.parse_args()
    E = json.load(open(a.edits)); out = []
    for name, (bp, npth) in WORDS.items():
        r = check(name, load(bp), load(npth), E['edit'], E['pivot']); out.append(r)
        print(name, 'PASS' if r['pass'] else 'FAIL', {k: v for k, v in r.items() if k not in ('word', 'new_read_positions')}, flush=True)
    if a.json: Path(a.json).write_text(json.dumps(out, indent=1, sort_keys=True) + '\n')
    sys.exit(0 if all(r['pass'] for r in out) else 1)
