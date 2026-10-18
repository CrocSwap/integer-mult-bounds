# SPDX-License-Identifier: Apache-2.0
# Marius-Paul Dumitrean, with substantial AI assistance (Anthropic Claude, via Claude Code).
"""retired7 tamper controls on a final BORROW-WORD (each mutant gets its inverse-reverse cleanup re-derived from its own forward
word; a rejection by a stale-cleanup/operator-id reason counts as a FAILURE):
  refit7: each new lender's last-gate refit undone must be rejected by 'warp frame mismatch';
  hostmove2: per moved hostee - warp lender reverted, move undone (hostee back on its old lender, which now hosts the new alias),
             warp before the new lender retires, G wrong;
  alias7 (the PR2679 alias suite per new alias): borrowed read sign flipped, read doubled, write sign flipped, warp dropped,
             G wrong, warp after the follower's first gate (the lender's own life ended in A, so 'before retirement' has no B position),
             helper kept with an entrance frame;
  refit7c: one certified frame corrupted.
usage: retired7_controls.py WORD INPUT_DIR TAG OUT   (INPUT_DIR holds refit7/hostmove2/alias7/refit7c_43TAG.json; audit_local.py and
word_patch.py are imported from this directory)"""
import copy, contextlib, gzip, io, json, sys, tempfile
from pathlib import Path
VACUOUS = ('explicit cleanup differs', 'warp operator id')
def regs(e): return e[1:3] if e[0] == 'add' else e[1:2]
def relabel(m, start, a, b):
    for i in range(start, len(m['B'])):
        e = m['B'][i]
        if e[0] == 'add':
            if e[1] == a: e[1] = b
            if e[2] == a: e[2] = b
        elif e[1] == a: e[1] = b
def controls(w0, p7, ph, pa, pc, audit, WP):
    """audit(word) -> None (accepted) or the rejection reason; returns (all_ok, results)"""
    def rederive(m):
        m2 = copy.deepcopy(m); A = m2['A']; m2['A'] = A[m2['prelude_events']:]; m2['cleanup'] = WP.derive_cleanup(m2, WP.restored_of(w0)); m2['A'] = A; return m2
    res = {}
    def expect(name, m, reason=None, fresh=True):
        r = audit(rederive(m) if fresh else m)
        ok = r is not None and not r.split(': ', 1)[-1].startswith(VACUOUS) and (reason is None or reason in r)
        res[name] = dict(rejected=r is not None, reason=(r or '')[:160], real_reason=ok)
    need = audit(w0); assert need is None, ('unmutated final word rejected', need)
    for sec, i, fr in p7['previous_frames']:
        m = copy.deepcopy(w0); m[sec][i][-1] = fr; expect(f'refit7 {sec}{i} lender refit undone', m, 'warp frame mismatch')
    for mv in ph['moves']:
        k = mv['op'] - 1; tag = f"move{mv['op']} {mv['L_old']}->{mv['L_new']}"
        m = copy.deepcopy(w0); m['warps'][k][1] = mv['L_old']; expect(tag + ' warp lender reverted', m)
        m = copy.deepcopy(w0); m['warps'][k] = copy.deepcopy(mv['old_record']); relabel(m, mv['old_pos'], mv['L_new'], mv['L_old']); expect(tag + ' move undone', m)
        m = copy.deepcopy(w0); m['warps'][k][0] = mv['pos'] - 400; expect(tag + ' warp before lender retirement', m)
        m = copy.deepcopy(w0); m['warps'][k][2][0] ^= m['warps'][k][2][1]; expect(tag + ' G wrong', m)
    for a in pa['aliases']:
        h, L = a['h'], a['L']; op = next(i for i, r in enumerate(w0['warps']) if r[1] == L and r[0] == a['pos']); tag = f'{h}<-{L}'
        reads = [i for i, g in enumerate(w0['B']) if i >= a['pos'] and g[0] == 'add' and g[2] == L]
        writes = [i for i, g in enumerate(w0['B']) if i >= a['pos'] and g[0] == 'add' and g[1] == L]
        m = copy.deepcopy(w0); m['B'][reads[0]][3] *= -1; expect(tag + ' borrowed read sign flipped', m)
        m = copy.deepcopy(w0); m['B'][reads[0]][3] *= 2; expect(tag + ' borrowed read doubled', m)
        if writes: m = copy.deepcopy(w0); m['B'][writes[0]][3] *= -1; expect(tag + ' borrowed write sign flipped', m)
        m = copy.deepcopy(w0); del m['warps'][op]
        for e in m['A'][:m['prelude_events']]:
            if e[0] == 'warp' and abs(e[2]) > op + 1: e[2] -= 1 if e[2] > 0 else -1
        expect(tag + ' warp dropped', m)
        m = copy.deepcopy(w0); m['warps'][op][2][0] ^= m['warps'][op][2][1]; expect(tag + ' G wrong', m)
        m = copy.deepcopy(w0); m['warps'][op][0] = a['pos'] + 1; expect(tag + " warp after the follower's first gate", m)
        m = copy.deepcopy(w0); m['start_extra'][str(h)] = a['E']; expect(f'{h} kept with an entrance frame', m)
    sec, i, fr = pc['frames'][0]; m = copy.deepcopy(w0); m[sec][i][-1] = [1]; expect('refit7c certified frame corrupted', m, fresh=False)
    return all(r['real_reason'] for r in res.values()), res
if __name__ == '__main__':
    here = Path(__file__).resolve().parent; sys.path.insert(0, str(here))
    import audit_local as al, word_patch as WP
    w0 = json.loads(gzip.decompress(Path(sys.argv[1]).read_bytes())); D = Path(sys.argv[2]); tag = sys.argv[3]; tmp = Path(tempfile.mkdtemp())
    p = {n: json.loads((D / f'{n}_43{tag}.json').read_text()) for n in ('refit7', 'hostmove2', 'alias7', 'refit7c')}
    def audit(w):
        q = tmp / 'm.json.gz'; q.write_bytes(gzip.compress(json.dumps(w, separators=(',', ':')).encode()))
        try:
            with contextlib.redirect_stdout(io.StringIO()): al.run(q, tmp / 'm.out.json', None, None)
            return None
        except (AssertionError, RuntimeError, ValueError, KeyError, IndexError) as e:
            return (type(e).__name__ + ': ' + str(e))[:200]
    ok, res = controls(w0, p['refit7'], p['hostmove2'], p['alias7'], p['refit7c'], audit, WP)
    Path(sys.argv[4]).write_text(json.dumps(dict(all_rejected_for_real_reasons=ok, controls=res), indent=1) + '\n')
    print(('ALL RETIRED7 CONTROLS REJECTED' if ok else 'RETIRED7 CONTROL FAILURE'), sum(r['real_reason'] for r in res.values()), 'of', len(res)); sys.exit(0 if ok else 1)
