#!/usr/bin/env python3
"""Deterministic builder: PR2226 LOW (anticipatory) aliases + the 5 omitted high aliases on the two
T74 pivot-566+554 borrow words of PR2269.

Construction-time oracle: the exact free-operator replay of PR2226 (replay_core.py, a function
form of PR2226 replay.py with only the 80/32 count assertion parameterised).  Emission: PR2269's
BORROW-WORD builder (vendor/pr2269/emit_word.py, build_word.py, byte copies).  Independent audit:
PR2269's audit_local.py (byte copy, run as a subprocess; it re-derives frames, profile, inverse
cleanup and both free-algebra orientations from the emitted word alone).  Exact Gaussian handoff
products: PR2226 operators.py (byte copy; needs numpy).

usage: python3 -B build_ext.py [--skip-gaussian] [--skip-audit] [--controls]
Writes witness/, words/, receipts/ under this directory.  Exit 0 only if every check passes.

Credits: PR2226 anticipatory dirty borrowing (Cinna Davis, @1337isnot1337, with OpenAI Codex
assistance): mechanism, alias rule, initial compensation, replay, operators.  PR2269 (Jeremy
Kothe, research/gmx-t74-borrow43): T74 canonical words, 43-alias witnesses, BORROW-WORD emitter
and auditor.  PR2260 (Dugongue): concurrent high-alias application on the T8 parent.
Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.
"""
import argparse, gzip, hashlib, json, os, subprocess, sys, time
from fractions import Fraction as Q
from pathlib import Path

if not __debug__:
    raise RuntimeError('assertions must remain enabled')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'vendor' / 'pr2269'))
from replay_core import replay, span, frame_basis, incident, ReplayError  # noqa: E402

INP = HERE / 'inputs'
CASES = [('gauge44', 'base', 'eeb6a236'), ('extra', 'extra', 'cd417b90')]
PINS = {  # git blob ids at PR2269 head b479fc55 / PR2226 head dacaf3d8
    'blocks.json': 'c683574b3861678081fd5c5944dbd7a47309f6fd',
    'gauge44.canonical.json.gz': '4abb6e28f02c95b41ed345d4e4401d16d58ae791',
    'extra.canonical.json.gz': 'e0d670d4351229ce6921ecfbecf180070b17616b',
    'witness_43_base.json': '9f4b93f3bc52d4f4ffaa128cfd7ae574fd36c462',
    'witness_43_extra.json': '864ba533f50c2f1f639a6a3559b185bd321b923a',
    'PR2226-WITNESS.json': '62edbcce166f7cf388231078c2cd7f75939b97e2',
}
OMITTED_HIGH = [639, 638, 635, 606, 637]   # PR2226 order; PR2269 omitted these five


def git_blob(path):
    data = Path(path).read_bytes()
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(canon, wt):
    w = json.loads(gzip.decompress((INP / f'{canon}.canonical.json.gz').read_bytes()))
    blocks = json.loads((INP / 'blocks.json').read_text())['sources'][0]['blocks']
    wit = json.loads((INP / f'witness_43_{wt}.json').read_text())
    return w, blocks, wit


def deferred_sets(w, blocks):
    deferred = {}; skip = set()
    for b in blocks:
        ss = set(b['helpers']); part = []
        for i in range(b['first_correction'], b['first_input']):
            e = w['B'][i]
            if set(incident(e)) <= ss:
                part.append(e); skip.add(i)
        deferred[b['first_input']] = part
    return deferred, skip


def prefix_plan(w, block, L, skip):
    """PR2226 section 3: pre-handoff events touching a low helper must be echoes (target += c L)
    or temporary external additions (L += a ext) with zero net change.  Echoes are deleted;
    an echo that reads a nonzero temporary part is rewritten as direct reads of the sources."""
    v = w['v']; i0 = block['first_input']
    events = [(j, w['B'][j]) for j in range(i0) if j not in skip and L in incident(w['B'][j])]
    tmp = {}; deleted = []; echoes = []; rewrites = {}
    for j, e in events:
        if e[0] == 'add' and e[2] == L and v <= e[1] < 2 * v:
            c = Q(e[3], e[4]); gates = []
            for ext, a in sorted(tmp.items()):
                if a:
                    cc = c * a
                    gates.append(['add', e[1], ext, cc.numerator, cc.denominator, e[-1]])
            deleted.append(j); echoes.append(j); rewrites[str(j)] = gates
        elif e[0] == 'add' and e[1] == L and e[2] != L and not (v <= e[2] < 2 * v):
            tmp[e[2]] = tmp.get(e[2], Q(0)) + Q(e[3], e[4]); deleted.append(j)
        else:
            return None, {'condition': 'prefix events are echoes or temporary external additions',
                          'witness_event': [j, e]}
    if any(a for a in tmp.values()):
        return None, {'condition': 'net temporary change is zero',
                      'witness': {str(k): str(a) for k, a in tmp.items() if a}}
    return {'deleted_prefix_indices': deleted, 'deleted_echo_indices': echoes,
            'early_prefix_rewrites': rewrites}, None


def touches(w, wit, deferred, skip):
    t = {}
    for e in wit['early_tail_events']:
        for r in incident(e['gate']):
            t.setdefault(r, []).append(('tail', e['before_B']))
    for i, e in enumerate(w['B']):
        for d in deferred.get(i, []):
            for r in incident(d):
                t.setdefault(r, []).append(('B', i))
        if i not in skip:
            for r in incident(e):
                t.setdefault(r, []).append(('B', i))
    return t


def first_frame(w, i, L, deferred, skip, removed_echoes, rewrites):
    for j in range(i, len(w['B'])):
        gl = list(deferred.get(j, [])) + list(rewrites.get(j, []))
        if j not in skip and j not in removed_echoes:
            gl.append(w['B'][j])
        for g in gl:
            if L in incident(g):
                return j, g[-1]
    raise AssertionError(('helper never used after handoff', L))


class Builder:
    def __init__(self, canon, wt):
        self.canon, self.wt = canon, wt
        self.w, self.blocks, self.wit = load(canon, wt)
        w = self.w
        self.v = w['v']; self.n = 2 * w['v'] + w['R']; self.h = w['h']
        self.frames = list(map(span, w['frames']))
        self.frame_index = {}
        for k, f in enumerate(self.frames):
            self.frame_index.setdefault(f, k)
        self.deferred, self.skip = deferred_sets(w, self.blocks)
        self.tch = touches(w, self.wit, self.deferred, self.skip)
        self.block_of = {L: b for b in self.blocks for L in b['helpers']}
        self.probe = {b['first_input']: None for b in self.blocks}
        r0 = replay(w, self.blocks, self.wit, expect_pairs=43, probe=self.probe)
        # the shipped PR2269 witness replays to its recorded profile
        assert r0['local_profile'] == {int(k): c for k, c in self.wit['replay']['local_profile'].items()}
        self.base43 = r0

    def retired(self, r, i):
        return all((t == 'B' and x < i) or (t == 'tail' and x <= i) for t, x in self.tch.get(r, []))

    def lender_facts(self, r, i, L_first_dim):
        w = self.w; snap = self.probe[i]
        return {'register': r, 'target_register': self.v <= r < 2 * self.v,
                'entrance_dim': len(w['frames'][w['start'][r]]),
                'final_dim': len(w['frames'][w['final'][r]]),
                'retired_before_handoff': self.retired(r, i),
                'equals_initial_input_at_handoff': r in snap['pristine'],
                'dim_at_handoff': len(snap['cur'].get(r, [])) if r in snap['cur'] else None,
                'zero_rank_handoff_possible': r in snap['cur'] and len(snap['cur'][r]) <= L_first_dim}

    def make_pair(self, L, lender, low, plan):
        w = self.w; b = self.block_of[L]; i = b['first_input']; snap = self.probe[i]
        plan = plan or {'deleted_prefix_indices': [], 'deleted_echo_indices': [], 'early_prefix_rewrites': {}}
        rew = {int(k): g for k, g in plan['early_prefix_rewrites'].items()}
        j, f1 = first_frame(w, i, L, self.deferred, self.skip, set(plan['deleted_prefix_indices']), rew)
        fb = frame_basis(self.frames[f1]); du = len(snap['cur'][lender])
        assert len(fb) >= du, 'paid handoff'
        E = fb[:du]
        last = self.tch.get(lender, [])
        lastB = max([x for t, x in last if t == 'B'], default=-1)
        lastT = max([x for t, x in last if t == 'tail'], default=-1)
        cb = frame_basis(span(b['common_frame']))
        p = {'register': L, 'base': b['base'], 'common_basis': cb, 'dimension': len(cb), 'deadline': i,
             'deleted_echo_indices': plan['deleted_echo_indices'], 'low': low, 'borrow_from': lender,
             'retirement_B_event': max(lastB, lastT - 1),
             'retirement_frame': self.frame_index[span(snap['cur'][lender])],
             'retirement_dimension': du, 'old_final_dimension': len(w['frames'][w['final'][lender]]),
             'handoff_B': i, 'handoff_basis': E, 'handoff_paid_rank': 0, 'anticipate': low,
             'retirement_basis': snap['cur'][lender], 'first_use_B': j}
        if low:
            p['deleted_prefix_indices'] = plan['deleted_prefix_indices']
            p['early_prefix_rewrites'] = plan['early_prefix_rewrites']
        return p

    def solve_corrections(self, pairs):
        inv = {'pairs': pairs, 'initial_corrections': [], 'early_tail_events': self.wit['early_tail_events']}
        d = replay(self.w, self.blocks, inv, diagnose=True)
        bad = [op for op, old, ok in d['lender_check'] if not ok]
        assert not bad, ('low lender not its restored initial input', bad)
        lender = {k + 1: x['borrow_from'] for k, x in enumerate(pairs)}
        low_ops = {k + 1 for k, x in enumerate(pairs) if x['low']}
        corr = []; foreign = {}
        for t, row in sorted(d['residual'].items()):
            for (var, word), c in sorted(row.items(), key=lambda kv: (kv[0][1], kv[0][0])):
                ok = (len(word) == 1 and word[0] in low_ops and var == lender[word[0]]
                      and c.denominator & (c.denominator - 1) == 0)
                if not ok:
                    foreign.setdefault(t, []).append([var, list(word), str(c)])
                    continue
                corr.append({'target': t, 'source': var, 'operator_word': [word[0]], 'coefficient': str(-c)})
        return corr, foreign

    def high_candidates(self, L):
        b = self.block_of[L]; i = b['first_input']; snap = self.probe[i]
        _, f1 = first_frame(self.w, i, L, self.deferred, self.skip, set(), {})
        d1 = len(self.w['frames'][f1])
        return i, d1, snap


def gaussian_records(pairs, w, keep):
    import importlib.util
    spec = importlib.util.spec_from_file_location('pr2226_operators', HERE / 'vendor' / 'pr2226' / 'operators.py')
    ops = importlib.util.module_from_spec(spec); spec.loader.exec_module(ops)
    import numpy as np
    h = w['h']; size = 1 << h; out = []; negative_rejected = False
    for k, x in enumerate(pairs, 1):
        U = w['frames'][x['retirement_frame']]; E = x['handoff_basis']
        assert len(U) == len(E)
        G = ops.change(U, E, h); K = ops.monomial(G, h)
        z = (np.eye(size, dtype=np.int64), np.zeros((size, size), dtype=np.int64), 0)
        z = ops.frame(z, U, h, -1); z = ops.apply_mono(z, K); z = ops.frame(z, E, h, 1)
        hh = ops.check(z)
        if not negative_rejected:
            zb = (np.eye(size, dtype=np.int64), np.zeros((size, size), dtype=np.int64), 0)
            zb = ops.frame(zb, U, h, -1); zb = ops.frame(zb, E, h, 1)
            try:
                ops.check(zb)
            except AssertionError:
                negative_rejected = True
        z = (np.eye(size, dtype=np.int64), np.zeros((size, size), dtype=np.int64), 0)
        z = ops.coord(z, range(h), -1); z = ops.apply_mono(z, K, -1); z = ops.coord(z, range(h), 1)
        eh = ops.check(z)
        rec = {'operator': k, 'G_columns': G, 'handoff_exact_monomial_sha256': hh,
               'full_exit_exact_monomial_sha256': eh}
        if k in keep:   # PR2269's recorded products for its 43 operators are reproduced exactly
            assert keep[k] == rec, ('PR2269 gaussian record not reproduced', k)
        out.append(rec)
    return out, negative_rejected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--skip-gaussian', action='store_true')
    ap.add_argument('--skip-audit', action='store_true')
    ap.add_argument('--controls', action='store_true')
    a = ap.parse_args()
    t0 = time.monotonic()
    for name, pin in PINS.items():
        assert git_blob(INP / name) == pin, ('input pin', name)
    w8 = json.loads((INP / 'PR2226-WITNESS.json').read_text())
    P8 = {x['register']: x for x in w8['pairs']}
    summary = {'status': None, 'pins_git_blob': PINS, 'words': {}}
    for d in ('witness', 'words', 'receipts'):
        (HERE / d).mkdir(exist_ok=True)
    ok = True
    for canon, wt, hname in CASES:
        B = Builder(canon, wt); w = B.w; v = B.v
        pairs = [dict(x) for x in B.wit['pairs']]
        used = {x['borrow_from'] for x in pairs} | {x['register'] for x in pairs}
        rec = {'base_43': {'local_profile': B.base43['local_profile'], 'local_mass': B.base43['local_mass'],
                           'helpers': w['R'] - 43}}
        # ---------- 1. low candidates: all 48 low helpers of the 12 blocks ----------
        low_report = {}; low_pairs = []
        handoffs = sorted({b['first_input'] for b in B.blocks})
        pools = {}
        for i in handoffs:
            snap = B.probe[i]
            pools[i] = sorted(r for r in range(B.n) if not (v <= r < 2 * v) and r not in used
                              and r in snap['pristine'] and len(w['frames'][w['start'][r]]) == 0
                              and B.retired(r, i))
        assert len({tuple(p) for p in pools.values()}) == 1, 'pool differs between handoffs'
        pool = pools[handoffs[0]]
        t8_low = [x for x in w8['pairs'] if x['low']]
        assert sorted(x['borrow_from'] for x in t8_low) == pool, 'eligible low lenders != PR2226 low lenders'
        for x8 in t8_low:   # PR2226 order, PR2226 lender
            L = x8['register']; b = B.block_of[L]
            plan, why = prefix_plan(w, b, L, B.skip)
            assert why is None, (L, why)
            facts = B.lender_facts(x8['borrow_from'], b['first_input'], 9)
            assert facts['retired_before_handoff'] and facts['equals_initial_input_at_handoff'] and facts['entrance_dim'] == 0
            p = B.make_pair(L, x8['borrow_from'], True, plan)
            low_pairs.append(p); used |= {L, p['borrow_from']}
            low_report[L] = {'status': 'ALIASED', 'lender': p['borrow_from'], 'lender_source': 'PR2226 lender transfers',
                             'deleted_prefix_indices': plan['deleted_prefix_indices'],
                             'early_prefix_rewrites': {k: g for k, g in plan['early_prefix_rewrites'].items() if g}}
        for b in B.blocks:
            for L in b['low']:
                if L in low_report:
                    continue
                plan, why = prefix_plan(w, b, L, B.skip)
                i = b['first_input']
                free = [r for r in pools[i] if r not in used]
                low_report[L] = {'status': 'BLOCKED', 'prefix_plan_legal': why is None,
                                 'prefix_events_deleted': plan['deleted_prefix_indices'] if plan else None,
                                 'blocker': 'no eligible lender: the set of non-target registers that are retired '
                                            'before the handoff, have a zero-dimensional entrance frame (so K_G z is free '
                                            'to read into the frame-zero target) and equal their own initial dirty input '
                                            'at the handoff has exactly %d members at every one of the 12 handoffs; all '
                                            '%d are consumed by the 32 transferred low aliases (free now: %d)' % (len(pool), len(pool), len(free))}
        # ---------- 2. the five omitted high aliases ----------
        high_report = {}; high_pairs = []
        for L in OMITTED_HIGH:
            x8 = P8[L]; i, d1, snap = B.high_candidates(L)
            t8 = x8['borrow_from']
            entry = {'T8_lender': t8, 'T8_lender_dim_at_handoff': len(snap['cur'][t8]),
                     'helper_first_frame_dim_T74': d1,
                     'helper_entrance_dim_T74': len(w['frames'][w['start'][L]]),
                     'T8_lender_blocker': ('paid dimension-drop handoff %d->%d (outside PR2226 rank-zero scope)'
                                           % (len(snap['cur'][t8]), d1)) if len(snap['cur'][t8]) > d1 else None}
            cands = sorted((r for r in range(B.n) if not (v <= r < 2 * v) and r not in used and B.retired(r, i)
                            and r in snap['cur'] and 0 < len(snap['cur'][r]) <= d1),
                           key=lambda r: (-len(snap['cur'][r]), len(w['frames'][w['final'][r]]) < B.h, r))
            entry['zero_rank_candidates'] = len(cands)
            chosen = None
            for r in cands:
                p = B.make_pair(L, r, False, None)
                trial = pairs + low_pairs + high_pairs + [p]
                corr, foreign = B.solve_corrections(trial)
                if foreign:
                    continue
                chosen = p; break
            assert chosen is not None, ('no high lender', L)
            high_pairs.append(chosen); used |= {L, chosen['borrow_from']}
            entry.update(status='ALIASED', lender=chosen['borrow_from'],
                         lender_dim_at_handoff=chosen['retirement_dimension'],
                         lender_final_dim=chosen['old_final_dimension'])
            high_report[L] = entry
        # ---------- 3. corrections, exact replay of all variants ----------
        variants = {'low32': pairs + low_pairs, 'high5': pairs + high_pairs, 'ext80': pairs + low_pairs + high_pairs}
        results = {}
        for vn, prs in variants.items():
            corr, foreign = B.solve_corrections(prs)
            assert not foreign, (vn, foreign)
            inv = {'pairs': prs, 'initial_corrections': corr, 'early_tail_events': B.wit['early_tail_events']}
            r = replay(w, B.blocks, inv)
            assert all(ok_ for _, _, ok_ in r['lender_check'])
            # negative control: omit the initial compensation -> the exact replay must fail
            if corr:
                try:
                    replay(w, B.blocks, dict(inv, initial_corrections=[])); raise AssertionError('no-compensation control passed')
                except ReplayError:
                    pass
                bad = [dict(c) for c in corr]; bad[0]['coefficient'] = str(-Q(bad[0]['coefficient']))
                try:
                    replay(w, B.blocks, dict(inv, initial_corrections=bad)); raise AssertionError('sign control passed')
                except ReplayError:
                    pass
            results[vn] = (inv, r)
            rec[vn] = {'pairs': len(prs), 'low': sum(x['low'] for x in prs), 'initial_corrections': len(corr),
                       'helpers': w['R'] - len(prs), 'local_profile': r['local_profile'], 'local_mass': r['local_mass'],
                       'independent_input_columns': r['independent_input_columns'],
                       'zero_FULL_cleanup_buffers': r['zero_FULL_cleanup_buffers'],
                       'controls': 'omitted compensation and one flipped sign rejected' if corr else 'n/a'}
            print(canon, vn, rec[vn], flush=True)
        inv, r = results['ext80']
        # ---------- 4. exact Gaussian handoff products (PR2226 operators.py) ----------
        keep = {g['operator']: g for g in B.wit['gaussian']['records']}
        assert sorted(keep) == list(range(1, 44))
        if a.skip_gaussian:
            raise SystemExit('gaussian records are required to emit the word')
        recs, neg = gaussian_records(inv['pairs'], w, keep)
        assert neg, 'omitted logical basis map negative control did not fail'
        witness = {'credit': 'PR2226 anticipatory dirty borrowing (Cinna Davis / 1337isnot1337, OpenAI Codex); '
                             'PR2269 T74 words and 43-alias witness (Jeremy Kothe); low aliases + 5 high aliases '
                             'added by research/t74-low-alias-borrowing (Claude Code assistance)',
                   'variant': f'80_{wt}', 'pairs': inv['pairs'], 'initial_corrections': inv['initial_corrections'],
                   'early_tail_events': inv['early_tail_events'],
                   'replay': {k: r[k] for k in ('status', 'local_profile', 'local_mass', 'remaining_registers',
                                                 'zero_FULL_cleanup_buffers', 'exact_cold_restoration', 'symbolic_warps')},
                   'gaussian': {'status': 'PASS_EXACT_GAUSSIAN_BORROW_HANDOFFS', 'operators': len(recs),
                                'columns_per_operator': 1 << w['h'], 'physical_rank_zero_products_checked': 2 * len(recs),
                                'omitted_logical_basis_map_rejected': neg, 'records': recs}}
        witness['replay']['local_profile'] = {str(k): c for k, c in r['local_profile'].items()}
        wp = HERE / 'witness' / f'witness_80_{wt}.json'
        wp.write_text(json.dumps(witness, indent=1) + '\n')
        # ---------- 5. emit BORROW-WORD with PR2269's builder ----------
        import build_word
        out = HERE / 'words' / f'BORROW-WORD-80{wt}.json.gz'
        cwd = os.getcwd(); os.chdir(HERE / 'vendor' / 'pr2269')
        try:
            build_word.main(str(INP / f'{canon}.canonical.json.gz'), str(INP / 'blocks.json'), str(wp), str(out), hname)
        finally:
            os.chdir(cwd)
        # make the gzip deterministic (mtime 0)
        content = gzip.decompress(out.read_bytes())
        out.write_bytes(gzip.compress(content, mtime=0))
        rec['word'] = {'path': str(out.relative_to(HERE)), 'content_sha256': hashlib.sha256(content).hexdigest()}
        # ---------- 6. independent audit (PR2269 audit_local.py, subprocess) ----------
        if not a.skip_audit:
            ar = HERE / 'receipts' / f'AUDIT-80{wt}.json'
            pr = subprocess.run([sys.executable, '-B', str(HERE / 'vendor' / 'pr2269' / 'audit_local.py'), '--word', str(out),
                                 '--base', str(INP / f'{canon}.canonical.json.gz'), '--output', str(ar)],
                                capture_output=True, text=True)
            ok &= pr.returncode == 0
            rep = json.loads(ar.read_text()) if pr.returncode == 0 else {'stderr': pr.stderr[-2000:]}
            rec['independent_audit'] = {k: rep.get(k) for k in ('status', 'removed_helpers', 'independent_inputs', 'warps',
                                                                'corrections', 'restored_cold', 'local_profile', 'local_mass',
                                                                'width_inventory', 'orientations')} if pr.returncode == 0 else rep
            print(canon, 'audit', rec['independent_audit'], flush=True)
            if pr.returncode == 0:
                assert rep['local_mass'] == r['local_mass'] and {int(k): c for k, c in rep['local_profile'].items()} == r['local_profile']
                wi = rep['width_inventory']; rec['width_sum'] = sum(int(k) * c for k, c in wi.items())
                rec['mass_identity_1856_plus_width_sum'] = rep['local_mass'] == 1856 + rec['width_sum']
        if a.controls:
            cr = HERE / 'receipts' / f'CONTROLS-80{wt}.json'
            pr = subprocess.run([sys.executable, '-B', str(HERE / 'vendor' / 'pr2269' / 'borrow_controls.py'), str(out),
                                 str(INP / f'{canon}.canonical.json.gz'), str(cr)], capture_output=True, text=True)
            ok &= pr.returncode == 0; rec['controls_rc'] = pr.returncode
        rec['low_candidates'] = {str(k): low_report[k] for k in sorted(low_report)}
        rec['omitted_high'] = {str(k): high_report[k] for k in OMITTED_HIGH}
        rec['low_lender_pool'] = pool
        summary['words'][canon] = rec
    summary['status'] = 'PASS_T74_LOW_ALIAS_EXTENSION' if ok else 'FAIL'
    summary['seconds'] = round(time.monotonic() - t0, 1)
    (HERE / 'receipts' / 'BUILD.json').write_text(json.dumps(summary, indent=1, sort_keys=True) + '\n')
    print(summary['status'])
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
