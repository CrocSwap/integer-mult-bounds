#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Marius-Paul Dumitrean, with substantial AI assistance (Anthropic Claude, via Claude Code).
# retired7 extension of verify_retired5.py (same author).
"""Bounded replay of retired7 on PR2751's words: the five retired-lender aliases (retired5 stages) plus two hostee moves that free
two more retired lenders (retired7 stages refit7 -> hostmove2 -> alias7 -> refit7c). Read-only, standard library only.

1. Rebuilds both candidate words from PR2751's words through the seven declared stages (refit5, alias5, refit5c, refit7, hostmove2,
   alias7, refit7c) and checks each stage's declared structure exactly.
2. Runs the pinned PR2679 BORROW-WORD auditor (vendor/audit_local_pr2679.py, byte-identical) on every state.
3. Tamper controls, each rejected by that auditor for a real reason: every lender refit undone (warp frame mismatch), every
   follower raise undone, the PR2679 alias suite (7 mutations per alias, cleanup re-derived), one certified frame corrupted.
4. Literal owner check of the complete fill (independent_owners.py, integer chronology and bit-mask bins).
5. Exact endpoint: rational adjacent bracket of the moment root at 1e-24, an 80-digit decimal root, and
   kappa = C - 10^-46 - 10^-70 strictly above the pinned exact claims of PR2751, PR2766 and PR2767.
"""
import contextlib, copy, gzip, hashlib, importlib.util, io, json, sys, tempfile
from decimal import Decimal, getcontext
from fractions import Fraction as F
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
ALIASES = [(606, 550), (635, 551), (637, 552), (638, 553), (639, 562)]
MOVES = [(30, 401, 564, 911), (31, 403, 565, 912)]   # retired7: (warp op, old lender, new lender, new lender's last B gate)
NEW7 = [(667, 401), (669, 403)]
H5 = [h for h, _ in ALIASES]; L5 = [L for _, L in ALIASES]
def need(ok, msg):
    if not ok: raise ValueError(msg)
def rd(name):
    p = HERE / name; b = p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)
def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def regs(e): return e[1:3] if e[0] == 'add' else e[1:2]
def refit_apply(w0, p):
    w = copy.deepcopy(w0)
    for sec, i, fr in p['frames']:
        need(w[sec][i][:-1] == w0[sec][i][:-1], 'refit changes a gate'); w[sec][i][-1] = fr
    w['report']['local_profile'] = p['local_profile']; return w
def frames_only(x, y):
    need(set(x) == set(y) and all(x[k] == y[k] for k in x if k not in ('A', 'B', 'restore', 'report')), 'non-frame field changed')
    need(all(len(x[k]) == len(y[k]) and all(a[:-1] == b[:-1] for a, b in zip(x[k], y[k])) for k in ('A', 'B', 'restore')), 'gate changed')
    return {(k, i) for k in ('A', 'B', 'restore') for i, (a, b) in enumerate(zip(x[k], y[k])) if a != b}
def main():
    need(__debug__, 'run without -O: the pinned auditor and these checks use assertions')
    pins = rd('INPUT-PINS.json')
    for path, digest in pins.items(): need(hashlib.sha256((HERE / path).read_bytes()).hexdigest() == digest, 'input digest ' + path)
    for name, digest in (('vendor/audit_local_pr2679.py', AUDITOR_SHA), ('vendor/word_patch_pr2679.py', WORD_PATCH_SHA)):
        need(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, 'vendored source pin ' + name)
    AU = load('audit_local_pr2679', HERE / 'vendor/audit_local_pr2679.py'); WP = load('word_patch_pr2679', HERE / 'vendor/word_patch_pr2679.py')
    import independent_owners as I, exact_moment as M, retired7_controls as R7
    tmp = Path(tempfile.mkdtemp(prefix='retired5-'))
    def audit(w, name):
        p = tmp / (name + '.json.gz'); p.write_bytes(gzip.compress(json.dumps(w, separators=(',', ':')).encode(), mtime=0))
        try:
            with contextlib.redirect_stdout(io.StringIO()): AU.run(p, tmp / (name + '.out.json'), None, None)
            return None
        except (AssertionError, RuntimeError, ValueError, KeyError, IndexError) as exc:
            return (type(exc).__name__ + ': ' + str(exc))[:200]
    def rederive(m, ref):
        m2 = copy.deepcopy(m); A = m2['A']; m2['A'] = A[m2['prelude_events']:]; m2['cleanup'] = WP.derive_cleanup(m2, WP.restored_of(ref)); m2['A'] = A; return m2
    out = dict(words={}, controls={})
    for tag in ('base', 'extra'):
        w0 = rd(f'inputs/WORD2751-{tag}.json.gz'); final = rd(f'inputs/WORD-{tag}.json.gz')
        p1, p2, p3 = rd(f'inputs/refit5_43{tag}.json'), rd(f'inputs/alias5_43{tag}.json'), rd(f'inputs/refit5c_43{tag}.json')
        s1 = refit_apply(w0, p1); ch1 = frames_only(w0, s1); need(ch1 == {(s, i) for s, i, _ in p1['frames']}, 'refit5 declared frames')
        lastL = {L: max(p for p, e in enumerate(w0['B']) if L in regs(e)) for L in L5}; firstH = {h: min(p for p, e in enumerate(w0['B']) if h in regs(e)) for h in H5}
        need(all(lastL[L] < firstH[h] for h, L in ALIASES) and not any(L in regs(e) for L in L5 for e in w0['restore']), 'lenders retired before their followers enter')
        need(all(len(s1['B'][p][-1]) == len(w0['B'][p][-1]) - 1 == 5 for p in lastL.values()), 'lender last gates lowered 6 -> 5')
        need(all(len(s1['B'][p][-1]) == len(w0['B'][p][-1]) + 1 == 5 for p in firstH.values()), 'follower first gates raised 4 -> 5')
        s2 = WP.apply_lowfour(s1, p2)
        need(WP.kernel_gate_edit(s1['B'], s2['B']) == p2['declared_gate_edit'] and sorted(set(s2['removed']) - set(s1['removed'])) == H5, 'alias5 declared edit and removed helpers')
        need(s2['warps'][:len(s1['warps'])] == s1['warps'] and [x[1] for x in s2['warps'][len(s1['warps']):]] == L5 and all(len(x[3]) == len(x[4]) == 5 for x in s2['warps'][-5:]), 'alias5 warps')
        need([[a['pos'], a['L'], a['G'], a['U'], a['E']] for a in p2['aliases']] == s2['warps'][-5:] and s2['A'] == s1['A'] and s2['restore'] == s1['restore'], 'alias5 records')
        need(s2['start_extra'] == {k: v for k, v in s1['start_extra'].items() if int(k) not in H5} and not any(h in regs(e) for h in H5 for e in s2['B'] + s2['restore']), 'helpers fully removed')
        need(all(s2[k] == s1[k] for k in ('helper_final', 'compensation', 'initial_corrections', 'precondition', 'cut', 'target_levels', 'centers', 'center_frames', 'ports', 'prelude_events')), 'alias5 changes nothing else')
        s3 = refit_apply(s2, p3); ch3 = frames_only(s2, s3); need(ch3 == {(s, i) for s, i, _ in p3['frames']}, 'refit5c declared frames')
        p4, p5, p6, p7 = (rd(f'inputs/{n}_43{tag}.json') for n in ('refit7', 'hostmove2', 'alias7', 'refit7c'))
        s4 = refit_apply(s3, p4); ch4 = frames_only(s3, s4); need(ch4 == {('B', g) for _, _, _, g in MOVES} == {(s, i) for s, i, _ in p4['frames']}, 'refit7 declared frames')
        need(all(len(s3['B'][g][-1]) == 6 and len(s4['B'][g][-1]) == 5 and L1 in regs(s3['B'][g]) and max(p for p, e in enumerate(s3['B']) if L1 in regs(e)) == g for _, _, L1, g in MOVES), 'new lenders: last gates lowered 6 -> 5')
        need(not any(L1 in regs(e) for _, _, L1, _ in MOVES for e in s3['restore']) and p4['previous_frames'] == [[s, i, s3[s][i][-1]] for s, i, _ in p4['frames']], 'new lenders retired; previous frames recorded')
        s5 = WP.apply_lowfour(s4, p5)
        need(WP.kernel_gate_edit(s4['B'], s5['B']) == p5['declared_gate_edit'] and s5['removed'] == s4['removed'] and s5['start_extra'] == s4['start_extra'], 'hostmove2 declared edit')
        for i, (a, b) in enumerate(zip(s4['B'], s5['B'])):
            c = list(a)
            for op, L0, L1, _ in MOVES:
                if i >= s4['warps'][op - 1][0]: c = [L1 if (j in (1, 2) if c[0] == 'add' else j == 1) and x == L0 else x for j, x in enumerate(c)]
            need(c[:-1] == b[:-1], 'hostmove2 is exactly the relabel of the hostees from their warp positions')
        need([i for i, (x, y) in enumerate(zip(s4['warps'], s5['warps'])) if x != y] == [op - 1 for op, _, _, _ in MOVES] and len(s5['warps']) == len(s4['warps']), 'hostmove2 replaces exactly warps 30 and 31 in place')
        need(all(s4['warps'][op - 1][1] == L0 and s5['warps'][op - 1][1] == L1 and len(s5['warps'][op - 1][3]) == len(s5['warps'][op - 1][4]) == 5 and s5['warps'][op - 1][0] > g for op, L0, L1, g in MOVES), 'moved warps: new lenders, dim 5, after the lenders retire')
        need([[m['pos'], m['L_new'], m['G'], m['U'], m['E']] for m in p5['moves']] == [s5['warps'][op - 1] for op, _, _, _ in MOVES] and [m['old_record'] for m in p5['moves']] == [s4['warps'][op - 1] for op, _, _, _ in MOVES], 'hostmove2 records')
        need(all(not any(L0 in regs(e) for e in s5['B'] + s5['restore']) for _, L0, _, _ in MOVES), 'old lenders untouched after their A lives')
        need(all(s5[k] == s4[k] for k in ('A', 'restore', 'helper_final', 'compensation', 'initial_corrections', 'precondition', 'cut', 'target_levels', 'centers', 'center_frames', 'ports', 'prelude_events')), 'hostmove2 changes nothing else')
        s6 = WP.apply_lowfour(s5, p6); H7 = [h for h, _ in NEW7]; L7 = [L for _, L in NEW7]
        need(WP.kernel_gate_edit(s5['B'], s6['B']) == p6['declared_gate_edit'] and s6['removed'] == s5['removed'] + H7, 'alias7 declared edit and removed helpers')
        need(s6['warps'][:len(s5['warps'])] == s5['warps'] and [x[1] for x in s6['warps'][len(s5['warps']):]] == L7 and all(len(x[3]) == len(x[4]) == 4 for x in s6['warps'][-2:]), 'alias7 warps')
        need([[a['pos'], a['L'], a['G'], a['U'], a['E']] for a in p6['aliases']] == s6['warps'][-2:] and [a['h'] for a in p6['aliases']] == H7 and s6['A'] == s5['A'] and s6['restore'] == s5['restore'], 'alias7 records')
        need(all(max([p for p, e in enumerate(s5['B']) if L in regs(e)], default=-1) < min(p for p, e in enumerate(s5['B']) if h in regs(e)) for h, L in NEW7) and not any(L in regs(e) for L in L7 for e in s5['restore']), 'alias7 lenders retired before their followers enter')
        need(s6['start_extra'] == {k: v for k, v in s5['start_extra'].items() if int(k) not in H7} and not any(h in regs(e) for h in H7 for e in s6['B'] + s6['restore']), 'alias7 helpers fully removed')
        need(all(s6[k] == s5[k] for k in ('helper_final', 'compensation', 'initial_corrections', 'precondition', 'cut', 'target_levels', 'centers', 'center_frames', 'ports', 'prelude_events')), 'alias7 changes nothing else')
        s7 = refit_apply(s6, p7); ch7 = frames_only(s6, s7); need(ch7 == {(s, i) for s, i, _ in p7['frames']}, 'refit7c declared frames')
        need(s7 == final, 'declared stages rebuild the candidate word ' + tag)
        for j, (name, w) in enumerate((('pr2751', w0), ('refit5', s1), ('alias5', s2), ('retired5', s3), ('refit7', s4), ('hostmove2', s5), ('alias7', s6), ('candidate', s7))):
            r = audit(w, f'{tag}-{name}'); need(r is None, f'auditor rejects {tag} {name}: {r}')
        c = {}
        for L, p in lastL.items():
            m = copy.deepcopy(final); m['B'][p][-1] = w0['B'][p][-1]; r = audit(m, f'{tag}-lender{L}'); c[f'lender {L} refit undone'] = r; need(r is not None and 'warp frame mismatch' in r, f'{tag} lender {L} refit undone not rejected by warp frame mismatch: {r}')
        for h, p in firstH.items():
            m = copy.deepcopy(final); m['B'][p][-1] = w0['B'][p][-1]; r = audit(m, f'{tag}-follower{h}'); c[f'follower {h} raise undone'] = r; need(r is not None, f'{tag} follower {h} raise undone accepted')
        for a in p2['aliases']:
            h, L = a['h'], a['L']; op = next(i for i, x in enumerate(final['warps']) if x[1] == L and x[0] == a['pos'])
            reads = [i for i, g in enumerate(final['B']) if i >= a['pos'] and g[0] == 'add' and g[2] == L]
            writes = [i for i, g in enumerate(final['B']) if i >= a['pos'] and g[0] == 'add' and g[1] == L]
            muts = []
            m = copy.deepcopy(final); m['B'][reads[0]][3] *= -1; muts.append(('borrowed read sign flipped', m))
            m = copy.deepcopy(final); m['B'][reads[0]][3] *= 2; muts.append(('borrowed read doubled', m))
            if writes: m = copy.deepcopy(final); m['B'][writes[0]][3] *= -1; muts.append(('borrowed write sign flipped', m))
            m = copy.deepcopy(final); del m['warps'][op]
            for e in m['A'][:m['prelude_events']]:
                if e[0] == 'warp' and abs(e[2]) > op + 1: e[2] -= 1 if e[2] > 0 else -1
            muts.append(('warp dropped', m))
            m = copy.deepcopy(final); m['warps'][op][2][0] ^= m['warps'][op][2][1]; muts.append(('G wrong', m))
            m = copy.deepcopy(final); m['warps'][op][0] = a['pos'] - 400; muts.append(('warp before lender retirement', m))
            m = copy.deepcopy(final); m['start_extra'][str(h)] = a['E']; muts.append(('helper kept with an entrance frame', m))
            for nm, m in muts:
                r = audit(rederive(m, final), f'{tag}-{h}-{nm.replace(" ", "_")}'); c[f'{h}<-{L} {nm}'] = r
                need(r is not None and not r.split(': ', 1)[-1].startswith(('explicit cleanup differs', 'warp operator id')), f'{tag} {h}<-{L} {nm}: not rejected for a real reason: {r}')
        sec, i, fr = p3['frames'][len(p3['frames']) // 2]; m = copy.deepcopy(final); m[sec][i][-1] = [1]; r = audit(m, f'{tag}-refit5c-tamper'); c['certified frame corrupted'] = r; need(r is not None, f'{tag} refit5c tamper accepted')
        ok7, c7 = R7.controls(final, p4, p5, p6, p7, lambda w: audit(w, f'{tag}-r7'), WP); need(ok7, f'{tag} retired7 controls: ' + json.dumps({k: v['reason'] for k, v in c7.items() if not v['real_reason']})[:300])
        c.update({k: v['reason'] for k, v in c7.items()})
        out['words'][tag] = dict(refit5_frames=len(ch1), alias5_gate_edits=len(p2['declared_gate_edit']), refit5c_frames=len(ch3), refit7_frames=len(ch4), hostmove2_gate_edits=len(p5['declared_gate_edit']), alias7_gate_edits=len(p6['declared_gate_edit']), refit7c_frames=len(ch7), retired7_controls=len(c7), local_profile=final['report']['local_profile'])
        out['controls'][tag] = {k: v[:90] for k, v in c.items()}
    # literal owner check of the complete candidate fill
    order, fill, providers = rd('inputs/ORDER.json'), rd('inputs/FILL.json.gz'), rd('inputs/PROVIDERS.json')
    dispatch = {(s, r): p for s, r, p in rd('inputs/DISPATCH.json.gz')}
    profile = {int(k): v for k, v in rd('CLAIM.json')['profile'].items()}
    owner = I.check(rd('inputs/PLAN.json.gz'), rd('inputs/GLOBAL-TEMPLATE.json.gz'), order, fill, providers, dispatch, profile)
    need(owner['roles'] == 666 * 408 and owner['helpers_per_call'] == 408, 'owner fill size')
    # exact endpoint and kappa
    claim = rd('CLAIM.json'); C = F(claim['complex_lower'])
    need(F(claim['complex_upper']) == C + F(1, 10 ** 24) and C.denominator <= 10 ** 24 and (C * 10 ** 24).denominator == 1, 'endpoint is a 1e-24 grid point')
    _, a = M.moment_bounds(profile, C); b, _ = M.moment_bounds(profile, C + F(1, 10 ** 24)); need(a < 66304 < b, 'exact adjacent root bracket')
    getcontext().prec = 90
    def g(z): return sum(Decimal(n) * (Decimal(r) / 73) ** (1 - z) for r, n in profile.items()) - 66304
    def dg(z): return sum(-Decimal(n) * (Decimal(r) / 73) ** (1 - z) * (Decimal(r) / 73).ln() for r, n in profile.items())
    z = Decimal(C.numerator) / Decimal(C.denominator)
    for _ in range(8): z -= g(z) / dg(z)
    need(F(str(z)) >= C and F(str(z)) < C + F(1, 10 ** 24), '80-digit root inside the certified bracket')
    K = F(claim['kappa']); need(K == C - F(1, 10 ** 46) - F(1, 10 ** 70), 'claim kappa = C - 1e-46 - 1e-70')
    margins = {}
    for name, rel in (('PR2751', 'evidence/PR2751-CLAIM.json'), ('PR2766', 'evidence/PR2766-CLAIM.json'), ('PR2767', 'evidence/PR2767-OUTER-CLAIM.json')):
        k = F(rd(rel)['kappa']); need(K > k, 'strict improvement over ' + name); d = K - k
        margins[name] = dict(decimal=str(Decimal(d.numerator) / Decimal(d.denominator))[:40], exact=str(d) if len(str(d)) < 120 else 'K - kappa(' + rel + ')')
    out.update(status='PASS_T74_JOINT_TWELVE_RETIRED7_STAGES_AUDITOR_CONTROLS_OWNERS_ENDPOINT', owner=dict(status=owner['status'], roles=owner['roles']),
               complex_lower=str(C), root_80_digits=str(+z)[:82], kappa=str(K), margins=margins,
               scope='Finite construction replay only: word stages, the pinned PR2679 auditor and its controls, the literal owner fill and exact moment arithmetic. Native providers, strict supplier and outer release are the full replay (full_replay.py).')
    print(json.dumps(out, indent=1))
AUDITOR_SHA = 'a38940094f7d19cd6376aafdd4734fa68eabc9aff4c98c3c4a3e9540328b1c90'
WORD_PATCH_SHA = '9b3287f189c4f29c1a8bdb1ba01fdcfe14a57d87b50fa4f2f646fb2346ab01ce'
if __name__ == '__main__':
    main()
