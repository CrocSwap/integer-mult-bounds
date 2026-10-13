"""Promotion controls: mutate the promoted word / recipe and require rejection at a pinned site.  Apache-2.0.
BlockInvert (Claude Code research agent).

usage: promo_controls.py --input BASE-FULL-WORD.json.gz --recipe PROMO-RECIPE.json --audit audit_local.py --out CONTROLS.json

Word-level mutants are checked by the independent audit (audit_local.py, imported from the given path; it shares no
code with the constructor); recipe-level mutants by build_promotion.apply / its pins.  Each mutant must raise with the
pinned message prefix; the honest word must pass both."""
import argparse, gzip, hashlib, importlib.util, json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_promotion as B

ap = argparse.ArgumentParser()
for k in ('input', 'recipe', 'audit', 'out'): ap.add_argument('--' + k, type=Path, required=True)
a = ap.parse_args()
s = importlib.util.spec_from_file_location('audit_local', a.audit); AL = importlib.util.module_from_spec(s); s.loader.exec_module(AL)
raw = gzip.decompress(a.input.read_bytes()); base = json.loads(raw); r = json.loads(a.recipe.read_text())
assert hashlib.sha256(raw).hexdigest() == r['input_content_sha256']
honest = B.apply(base, r)
v = base['report']['v']
tmp = Path(tempfile.mkdtemp())


def audit(w):
    p = tmp / 'w.json.gz'; p.write_bytes(gzip.compress(json.dumps(w, separators=(',', ':')).encode(), mtime=0))
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        AL.run(p, tmp / 'r.json')


def first_gate(w, h):
    for sec in ('A', 'B'):
        for i, e in enumerate(w[sec]):
            if h in B.regs(e): return sec, i
    raise AssertionError(h)


results = []


def expect(name, fn, prefix):
    try:
        fn(); got = 'ACCEPTED'
    except (RuntimeError, AssertionError) as e:
        got = str(e.args[0]) if e.args else type(e).__name__
    ok = got.startswith(prefix)
    results.append(dict(control=name, expected=prefix, got=got[:160], rejected_at_pinned_site=ok))
    print(('OK  ' if ok else 'BAD ') + name + ': ' + got[:120], flush=True)


# honest
audit(honest); print('honest word: audit PASS', flush=True)
H = sorted(int(h) for h in r['entrances'])
h0 = str(H[0]); E5 = B.span(r['entrances'][h0]); sec, i = first_gate(honest, int(h0)); F1 = B.span(honest[sec][i][-1])
full = B.span([1 << k for k in range(9)])


def mut(f):
    w = json.loads(json.dumps(honest)); f(w); return w


# 1. promoted entrance moved to a dim-5 frame NOT inside its first gate frame
def bad_entrance(w):
    for x in range(1, 512):
        G = B.span(list(B.span(base['start_extra'][h0])) + [x])
        if len(G) == 5 and B.span(list(G) + list(F1)) != F1:
            w['start_extra'][h0] = list(G); return
    raise AssertionError('no frame')
expect('entrance_outside_first_gate_frame', lambda: audit(mut(bad_entrance)), 'frame not monotone')
# 2. a raised gauge gate of a promoted helper left at its old (E4) frame
old_of = {(c[0], c[1]): c[2] for c in r['gate_frames']}
assert (sec, i) in old_of, 'first gate of a promoted helper is a raised gate'
expect('raised_gate_missing', lambda: audit(mut(lambda w: w[sec][i].__setitem__(-1, list(B.span(old_of[(sec, i)]))))), 'frame not monotone')
# 2b. per promoted group: its first helper's raised entry gate left at the old frame
for hg in H[4::4]:
    sg, ig = first_gate(honest, hg)
    if (sg, ig) in old_of:
        expect('raised_gate_missing_group_%d' % hg, lambda sg=sg, ig=ig: audit(mut(lambda w: w[sg][ig].__setitem__(-1, list(B.span(old_of[(sg, ig)]))))), 'frame not monotone')
# 3. every raised gate kept but one entrance reverted to E4 (report kept): the paid profile no longer matches
expect('entrance_reverted_profile', lambda: audit(mut(lambda w: w['start_extra'].__setitem__(h0, list(B.span(base['start_extra'][h0]))))), 'paid profile mismatch')
# 4. an E4 helper outside the promoted groups promoted alone (no raised gates)
others = sorted(int(h) for h, f in base['start_extra'].items() if len(B.span(f)) == 4 and h not in r['entrances'])
if others:
    h1 = str(others[0])
    expect('ungrouped_promotion', lambda: audit(mut(lambda w: w['start_extra'].__setitem__(h1, list(E5)))), 'frame not monotone')
# 5. recipe-level: wrong old frame for a raised gate; non-promotion entrance; input pin
def r_bad_old():
    q = json.loads(json.dumps(r)); q['gate_frames'][0][2] = list(full); B.apply(base, q)
expect('recipe_gate_old_frame', r_bad_old, "('gate frame mismatch'" if r['gate_frames'][0][0] != 'T' else "('tail frame mismatch'")
def r_demote():
    q = json.loads(json.dumps(r)); q['entrances'][h0] = base['start_extra'][h0]; B.apply(base, q)
expect('recipe_not_a_promotion', r_demote, "('not a promotion'")
def r_pin():   # the driver's own __main__ path on a tampered input word (one gate scalar changed)
    import subprocess
    t = json.loads(raw); e = t['B'][0]
    if e[0] == 'add': e[3] += e[4]
    else: e[2] = -e[2]
    p = tmp / 'tampered.json.gz'; p.write_bytes(gzip.compress(json.dumps(t, separators=(',', ':')).encode(), mtime=0))
    q = subprocess.run([sys.executable, '-B', str(Path(B.__file__)), '--input', str(p), '--recipe', str(a.recipe), '--out', str(tmp / 'o')],
                       capture_output=True, text=True)
    assert q.returncode == 0, q.stderr.strip().splitlines()[-1].split('AssertionError: ', 1)[-1]
expect('recipe_input_pin', r_pin, 'input word pin')
# 6. scalar tamper inside a promoted group's raised gate (frames intact): exactness must fail
def scal(w):
    e = w[sec][i]
    if e[0] == 'add': e[3] = e[3] + e[4]
    else: e[2] = -e[2]
expect('raised_gate_scalar_tamper', lambda: audit(mut(scal)), '')
results[-1]['rejected_at_pinned_site'] = results[-1]['got'] != 'ACCEPTED'
bad = [x for x in results if not x['rejected_at_pinned_site']]
a.out.write_text(json.dumps(dict(recipe=r['expected']['output_content_sha256'], honest='PASS', controls=results,
                                 rejected=len(results) - len(bad)), indent=1))
assert not bad, bad
print('PASS', len(results), 'controls rejected at pinned sites')
