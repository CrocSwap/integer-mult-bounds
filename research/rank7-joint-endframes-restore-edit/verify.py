#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact local replay of the three declared stages on our PR2942 words.

(a) producer.py rebuilds both WORD files from PARENT (= PR2942's words, byte-identical) and the declared records
    (complete decoded content), and every intermediate stage word is replayed;
(b) stage 1 (joint rank-7 end frames, frame-only): every lowered end frame is a hyperplane of the previous one and
    equals its group's shared subspace W, every gate touching a lowered helper lies in W, no gate or scalar changes,
    the cleanup contract is unchanged; the stage-1 word passes the PR2833 auditor;
(c) stage 2: at every step, the unchanged PR2908/PR2917 structure.py (Jeremy Diviney) checks the seven exact two-sided
    free-operator identities on the step's parent and its literal input/output gates; every step word passes the auditor;
(d) stage 3: PR2957's vendored applier (Jeremy Kothe) on the re-based rewrite list, with report and cleanup re-derived;
(e) the unchanged PR2833 auditor (vendor/audit_local.py, as vendored by PR2917) replays both final words forward and dual
    over all 632 independent inputs: PASS_INDEPENDENT_EXACT_BORROWING_WORD, 91 restored endpoints and buffers;
(f) frame accounting: preload_move.frame_report(word) equals each word's report and the declared invoice;
(g) semantic controls, each rejected (stage 1: one helper of a group lowered alone, wrong subspace, an omitted gate or
    partner frame edit, stale and widened reports; stage 2 per step: drop an input gate, flip an output coefficient (both
    also by the certificate), wrong hyperplane, stale cleanup, stale compensation, the omitted frame change; stage 3: a
    rewrite's deletion removed, its insertion dropped, a transported coefficient flipped, a stale preimage, unshifted warp
    positions, a stale cleanup, an unresolved swap frame);
(h) evidence (not a gate): lane A's group-joint price table (construction/STAGE-PRICES.json) against the literal stage
    prices recomputed from the frame-report profiles with the solver's integer weights;
(i) the overlay producer tools/wordedit.py round-trips PARENT -> WORD exactly.
Structure adapted from Mason Hale's PR2917 verify.py via our PR2942 verify.py. Marius-Paul Dumitrean, with substantial AI
assistance (Anthropic Claude via Claude Code). Local only: native, owner and outer admission are separate.
"""
import argparse, contextlib, copy, gzip, hashlib, io, json, sys, time, types
from pathlib import Path

P = Path(__file__).resolve().parent


def read(p):
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, p):
    m = types.ModuleType(name)
    m.__file__ = str(p)
    sys.modules[name] = m
    exec(compile(p.read_bytes(), str(p), 'exec'), m.__dict__)
    return m


def save_word(p, w):
    p.write_bytes(gzip.compress(json.dumps(w, separators=(',', ':')).encode(), mtime=0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', type=Path, required=True)
    a = ap.parse_args()
    if not __debug__:
        raise SystemExit('refusing python -O: the structural checker relies on assertions')
    begin = time.monotonic()
    out = a.work.resolve()
    assert not out.exists() and not out.is_relative_to(P)
    pins = read(P / 'PINS.json')
    local = {f.relative_to(P).as_posix() for d in ('vendor', 'data') for f in (P / d).rglob('*') if f.is_file()}
    assert local | {'producer.py', 'structure.py', 'tools/wordedit.py', 'construction/STAGE-PRICES.json'} <= set(pins), 'every local input pinned'
    assert all(sha(P / n) == h for n, h in pins.items()), 'pinned bytes'
    out.mkdir(parents=True)
    pm = load('preload_move', P / 'vendor/preload_move.py')
    dr = load('declared_rewrites', P / 'vendor/declared_rewrites.py')
    gen = load('rank7_producer', P / 'producer.py')
    aud = load('independent_paired_audit', P / 'vendor/audit_local.py')
    structural = load('independent_paired_structure', P / 'structure.py')
    we = load('rank7_wordedit', P / 'tools/wordedit.py')
    record = read(P / 'data/STAGE1-FRAME-EDITS.json')
    transforms = [read(P / f'data/TRANSFORM-{h}.json') for h in gen.HELPERS]
    rewrites = read(P / 'data/REWRITES-2957.json')
    prices = read(P / 'construction/STAGE-PRICES.json')
    weight = {int(r): c for r, c in prices['weights']['c'].items()}
    BE = prices['weights']['break_even']

    def cost(profile):
        return sum(weight[int(r)] * n for r, n in profile.items())

    def audit(word, name):
        path = out / (name + '.json.gz')
        save_word(path, word)
        with contextlib.redirect_stdout(io.StringIO()):
            return aud.run(path, out / (name + '.json'))

    def rejected(word, name):
        try:
            audit(word, name)
        except (AssertionError, RuntimeError, ValueError) as error:
            return str(error)[:240]
        raise AssertionError('semantic mutant accepted by the auditor: ' + name)

    def cert_rejects(parent, transform, name):
        try:
            structural.check(parent, transform, aud)
        except (AssertionError, KeyError, ValueError) as error:
            return type(error).__name__ + ' ' + str(error)[:160]
        raise AssertionError('mutant transform accepted by the certificate: ' + name)

    def producer_rejects(fn, name):
        try:
            fn()
        except (AssertionError, KeyError, ValueError) as error:
            return type(error).__name__ + ' ' + str(error)[:200]
        raise AssertionError('mutant accepted by the producer: ' + name)

    def rereport(word):
        try:
            profile, inventory = pm.frame_report(word)
        except ValueError:
            return word    # an illegal frame chain keeps the claimed report; the auditor recounts it
        word['report']['local_profile'], word['report']['width_inventory'] = profile, inventory
        return word

    def joint_claim(word):
        if (word['report']['local_profile'], word['report']['width_inventory']) != (gen.STAGE1_PROFILE, gen.STAGE1_INVENTORY):
            raise ValueError('declared joint stage-1 invoice %s' % word['report']['local_profile'])

    def hyperplanes_of(frame):
        vectors = [v for v in range(1, 512) if gen.inside([v], frame)]
        for m in range(1, 512):
            Hm = list(pm.basis([v for v in vectors if (v & m).bit_count() % 2 == 0]))
            if len(Hm) == len(pm.basis(frame)) - 1:
                yield Hm

    def recut(word, restored):
        z = copy.deepcopy(word)
        z['A'] = z['A'][z['prelude_events']:]
        return pm.derive_cleanup(z, restored)

    def ok_audit(word, name, buffers, profile=None, inventory=None):
        r = audit(word, name)
        assert r['status'] == 'PASS_INDEPENDENT_EXACT_BORROWING_WORD' and r['orientations'] == {'forward': 'PASS', 'dual': 'PASS'}
        assert r['independent_inputs'] == 632 and r['restored_cold'] == r['zero_buffers'] == buffers
        if profile is not None:
            assert {str(k): v for k, v in r['local_profile'].items()} == profile
            assert {str(k): v for k, v in r['width_inventory'].items()} == inventory
        return {key: r[key] for key in ('status', 'independent_inputs', 'restored_cold', 'zero_buffers', 'local_profile',
                                        'width_inventory', 'local_mass', 'orientations', 'content_sha256')}

    records, controls = {}, {}
    for tag in ('base', 'extra'):
        parent = read(P / f'data/PARENT-{tag}.json.gz')
        shipped = read(P / f'data/WORD-{tag}.json.gz')
        words = gen.stages(parent, record, transforms, rewrites)
        assert words[-1] == gen.apply(parent, record, transforms, rewrites) == shipped, 'complete producer reconstruction'
        rec = {'parent_sha256': sha(P / f'data/PARENT-{tag}.json.gz'), 'word_sha256': sha(P / f'data/WORD-{tag}.json.gz')}
        # ---------------- stage 1: joint rank-7 end frames (frame-only)
        x1 = words[0]
        lowered = {}
        for gname, (W, hs) in gen.GROUPS.items():
            for h in hs:
                old, new = parent['helper_final'][str(h)], x1['helper_final'][str(h)]
                assert new == W and gen.inside(new, old) and len(new) == len(old) - 1, ('hyperplane of the old end frame', h)
                lowered[h] = {'group': gname, 'old_dim': len(old), 'new_dim': len(new), 'entering': str(h) in parent['start_extra']}
        assert gen.lowered_fit(x1) == [], 'every gate touching a lowered helper fits'
        touching = sum(1 for s in ('A', 'B', 'restore') for g in x1[s] if g[0] in ('add', 'scale') and set(gen.roles(g)) & set(lowered))
        assert all(p_[:-1] == q_[:-1] for s in ('A', 'B', 'restore') for p_, q_ in zip(parent[s], x1[s])) and x1['cleanup'] == parent['cleanup']
        a1 = ok_audit(x1, f'{tag}-stage1', gen.PARENT_BUFFERS, gen.STAGE1_PROFILE, gen.STAGE1_INVENTORY)
        d1 = cost(x1['report']['local_profile']) - cost(parent['report']['local_profile'])
        rec['stage1'] = {'groups': {g: {'W': W, 'helpers': hs} for g, (W, hs) in gen.GROUPS.items()}, 'lowered': lowered,
                         'frame_edits': len(record['frame_edits']), 'frame_edits_by_section': {s: sum(1 for e in record['frame_edits'] if e['section'] == s) for s in ('A', 'B', 'restore')},
                         'gates_touching_lowered_helpers_all_inside_W': touching, 'audit': a1, 'local_profile': x1['report']['local_profile'],
                         'width_inventory': x1['report']['width_inventory'], 'literal_price_units': d1}
        # stage-1 controls
        name = f'{tag}-stage1'
        for gname, (W, hs) in gen.GROUPS.items():
            bad = copy.deepcopy(x1)
            for h in hs[1:]:
                bad['helper_final'][str(h)] = list(parent['helper_final'][str(h)])
            rereport(bad)
            verdict = audit(bad, f'{name}-one-alone-{gname}')['status']        # a valid word, priced below the joint claim
            extra = cost(bad['report']['local_profile']) - cost(x1['report']['local_profile'])
            joint = next(r for r in prices['stage1']['groups'] if r['group'] == gname)
            alone_margin = joint['joint_margin'] - extra + (len(hs) - 1) * BE
            assert alone_margin < 0 < joint['joint_margin'], ('one helper alone must lose', gname, alone_margin)
            claim = producer_rejects(lambda: joint_claim(bad), 'one-alone')
            controls[f'{name}-one-helper-alone-{gname}'] = {'auditor': verdict + ' (a valid word)', 'joint_claim': claim,
                                                           'kept_helper': hs[0], 'reverted_helpers': hs[1:],
                                                           'margin_alone_units': alone_margin, 'margin_joint_units': joint['joint_margin']}
        # wrong subspace: group A's helpers end at another hyperplane of their old end frame that misses their gates
        Wa, ha = gen.GROUPS['A']
        old = parent['helper_final'][str(ha[0])]
        last = [g[-1] for s in ('A', 'B', 'restore') for g in x1[s] if g[0] in ('add', 'scale') and ha[0] in gen.roles(g)][-1]
        wrong = next(Hm for Hm in hyperplanes_of(old) if Hm != Wa and not gen.inside(last, Hm))
        bad = copy.deepcopy(x1)
        for h in ha:
            bad['helper_final'][str(h)] = list(wrong)
        controls[f'{name}-wrong-subspace'] = {'auditor': rejected(rereport(bad), f'{name}-wrong-subspace'),
                                              'fit_check': 'rejected: %d gates outside the end frame' % len(gen.lowered_fit(bad, {'A': (wrong, ha)})), 'W_wrong': wrong}
        assert gen.lowered_fit(bad, {'A': (wrong, ha)})
        # an omitted gate frame edit on a lowered helper, and an omitted partner-only edit (claimed report kept)
        touch = [e for e in record['frame_edits'] if set(gen.roles(e['gate'])) & set(lowered)]
        partner = [e for e in record['frame_edits'] if not set(gen.roles(e['gate'])) & set(lowered)]
        for label, e in (('omit-gate-frame-edit', touch[-1]), ('omit-partner-frame-edit', partner[0])):
            bad = copy.deepcopy(x1)
            assert bad[e['section']][e['index']][:-1] == e['gate'] and bad[e['section']][e['index']][-1] == e['new_frame']
            bad[e['section']][e['index']][-1] = list(e['old_frame'])
            controls[f'{name}-{label}'] = {'auditor': rejected(bad, f'{name}-{label}'), 'edit': [e['section'], e['index'], e['gate']]}
        bad = copy.deepcopy(x1)
        bad['report'] = copy.deepcopy(parent['report'])
        controls[f'{name}-stale-report'] = {'auditor': rejected(bad, f'{name}-stale-report')}
        bad = copy.deepcopy(x1)
        bad['helper_final'][str(ha[0])] = list(parent['helper_final'][str(ha[0])])
        controls[f'{name}-widened-end-frame-claimed-report'] = {'auditor': rejected(bad, f'{name}-widened-end-frame')}
        # ---------------- stage 2: five paired extractions
        steps, w = [], x1
        for k, t in enumerate(transforms, 1):
            h, n = t['helper'], w['prelude_events']
            cert = structural.check(w, t, aud)
            assert cert['status'] == 'PASS_EXACT_TWO_SIDED_SUBSPACE_CERTIFICATE' and cert['helper'] == h
            child = words[k]
            assert child == gen.apply_stage(w, t)
            frame = gen.hyperplane(t['normal'])
            assert child['helper_final'][str(h)] == frame and len(child['helper_final']) == gen.PARENT_BUFFERS + k
            ak = ok_audit(child, f'{tag}-stage2-step{k}-{h}', gen.PARENT_BUFFERS + k)
            name = f'{tag}-stage2-step{k}-{h}'
            bad = copy.deepcopy(child); del bad['A'][n]
            bad['cleanup'] = recut(rereport(bad), set(map(int, bad['helper_final'])))
            controls[name + '-drop-input-gate'] = {'auditor': rejected(bad, name + '-drop-input-gate'),
                                                   'certificate': cert_rejects(w, dict(t, before=t['before'][1:]), name + '-drop-input-gate')}
            i = next(j for j, g in enumerate(t['after']) if g[0] == 'add')
            bad = copy.deepcopy(child); g = bad['restore'][len(w['restore']) + i]; g[3] = -g[3]
            bad['cleanup'] = recut(rereport(bad), set(map(int, bad['helper_final'])))
            after = copy.deepcopy(t['after']); after[i][3] = -after[i][3]
            controls[name + '-flip-output-coefficient'] = {'auditor': rejected(bad, name + '-flip-output-coefficient'),
                                                           'certificate': cert_rejects(w, dict(t, after=after), name + '-flip-output-coefficient')}
            wrong = gen.hyperplane(t['normal'] ^ 1)
            bad = copy.deepcopy(child)
            for g in bad['restore'][len(w['restore']):]:
                g[-1] = list(wrong)
            bad['helper_final'][str(h)] = list(wrong)
            bad['cleanup'] = recut(rereport(bad), set(map(int, bad['helper_final'])))
            controls[name + '-wrong-hyperplane'] = {'auditor': rejected(bad, name + '-wrong-hyperplane'), 'normal': t['normal'] ^ 1}
            bad = copy.deepcopy(child)
            bad['cleanup'] = recut(bad, set(map(int, w['helper_final'])))
            controls[name + '-stale-cleanup'] = {'auditor': rejected(bad, name + '-stale-cleanup')}
            assert child['compensation'] != w['compensation']
            bad = copy.deepcopy(child); bad['compensation'] = copy.deepcopy(w['compensation'])
            controls[name + '-stale-compensation'] = {'auditor': rejected(bad, name + '-stale-compensation')}
            for e in t['frame_changes']:
                bad = copy.deepcopy(child)
                assert bad[e['section']][e['index']][:-1] == e['gate'] and bad[e['section']][e['index']][-1] == e['new_frame']
                bad[e['section']][e['index']][-1] = list(e['old_frame'])
                controls[name + '-omit-frame-change'] = {'auditor': rejected(bad, name + '-omit-frame-change')}
            dk = cost(child['report']['local_profile']) - cost(w['report']['local_profile'])
            steps.append({'step': k, 'helper': h, 'normal': t['normal'], 'hyperplane': frame, 'inputs': len(t['before']), 'outputs': len(t['after']),
                          'frame_changes': len(t['frame_changes']), 'certificate': {key: cert[key] for key in ('status', 'helper', 'alpha', 'y', 'u', 'v')},
                          'audit': ak['status'], 'local_profile': child['report']['local_profile'], 'width_inventory': child['report']['width_inventory'],
                          'buffers': len(child['helper_final']), 'literal_price_units': dk})
            w = child
        rec['stage2'] = {'steps': steps, 'local_profile': w['report']['local_profile'], 'width_inventory': w['report']['width_inventory'],
                         'literal_price_units': cost(w['report']['local_profile']) - cost(x1['report']['local_profile'])}
        # ---------------- stage 3: fourteen declared PR2957 rewrites (Jeremy Kothe)
        x2, x3 = words[-2], words[-1]
        y, ledger = gen.apply_rewrites(x2, rewrites)
        assert y == x3
        a3 = ok_audit(x3, f'{tag}-final', gen.BUFFERS, gen.PROFILE, gen.INVENTORY)
        name = f'{tag}-stage3'
        by = {r['id']: r for r in rewrites}

        def edits(rid, kind):
            return [e for e in by[rid]['edits'] if (e['new'] if kind == 'insert' else e['old']) and not (e['new'] and e['old'])]

        def where(word, sec, gate):
            hits = [i for i, g in enumerate(word[sec]) if g == gate]
            assert len(hits) >= 1
            return hits[0]
        restored = set(map(int, x3['helper_final']))

        def own(word):          # each gate mutant carries the report and cleanup re-derived from its own forward word
            rereport(word)
            word['cleanup'] = recut(word, restored)
            return word
        ins, dele = edits('5997', 'insert')[0], edits('5997', 'delete')[0]
        bad = copy.deepcopy(x3)
        shift = len(ins['new']) if ins['section'] == dele['section'] and ins['start'] <= dele['start'] else 0
        bad[dele['section']].insert(dele['start'] + shift, copy.deepcopy(dele['old'][0]))
        controls[name + '-remove-one-deletion-5997'] = {'auditor': rejected(own(bad), name + '-remove-one-deletion')}
        bad = copy.deepcopy(x3); bad[ins['section']].pop(where(bad, ins['section'], ins['new'][0]))
        controls[name + '-drop-inserted-gate-5997'] = {'auditor': rejected(own(bad), name + '-drop-inserted-gate')}
        g6004 = edits('6004', 'insert')[0]
        bad = copy.deepcopy(x3); j = where(bad, g6004['section'], g6004['new'][0]); bad[g6004['section']][j][3] = -bad[g6004['section']][j][3]
        controls[name + '-flip-transported-coefficient-6004'] = {'auditor': rejected(own(bad), name + '-flip-transported-coefficient')}
        stale = copy.deepcopy(rewrites)
        e3779 = next(e for r in stale if r['id'] == '3779' for e in r['edits'] if e['old'])
        e3779['start'] += 1; e3779['stop'] += 1
        controls[name + '-stale-preimage-3779'] = {'applier': producer_rejects(lambda: dr.apply(x2, stale, check_declared=False), 'stale-preimage')}
        assert x3['warps'] != x2['warps']
        bad = copy.deepcopy(x3); bad['warps'] = copy.deepcopy(x2['warps'])
        controls[name + '-warp-positions-not-shifted'] = {'auditor': rejected(own(bad), name + '-warp-positions-not-shifted')}
        bad = copy.deepcopy(x3); bad['cleanup'] = copy.deepcopy(x2['cleanup'])
        assert bad != x3
        controls[name + '-stale-cleanup'] = {'auditor': rejected(bad, name + '-stale-cleanup')}
        sw = by['swap3749']; moved_new = next(e for e in sw['edits'] if e['new'])['new'][0]; moved_old = next(e for e in sw['edits'] if e['old'])['old'][0]
        assert moved_new[:-1] == moved_old[:-1] and moved_new[-1] != moved_old[-1]
        bad = copy.deepcopy(x3); bad['A'][where(bad, 'A', moved_new)] = copy.deepcopy(moved_old)
        controls[name + '-swap-frame-not-resolved-3749'] = {'auditor': rejected(bad, name + '-swap-frame-not-resolved')}
        rec['stage3'] = {'rewrites': ledger['rewrites'], 'classes': sorted({r['cls'] for r in rewrites}), 'edits': ledger['edits'],
                         'A_len': ledger['A_len'], 'restore_len': ledger['restore_len'], 'local_profile': x3['report']['local_profile'],
                         'literal_price_units': cost(x3['report']['local_profile']) - cost(x2['report']['local_profile']),
                         'credit': 'Jeremy Kothe (jeremykothe2), PR2957: rewrites and applier (vendor/declared_rewrites.py, byte-identical)'}
        # ---------------- final word
        changed = sorted(key for key in parent if parent[key] != shipped[key])
        assert set(changed) == {'A', 'B', 'restore', 'warps', 'helper_final', 'compensation', 'report', 'cleanup'}, changed
        profile, inventory = pm.frame_report(shipped)
        assert profile == shipped['report']['local_profile'] == gen.PROFILE and inventory == shipped['report']['width_inventory'] == gen.INVENTORY
        spec = we.make_spec(parent, shipped)
        assert we.apply_spec(parent, spec) == shipped and shipped['cleanup'] == we.derive_cleanup(shipped), 'overlay spec round trip'
        rec.update(changed_sections=changed, audit=a3, frame_report={'local_profile': profile, 'width_inventory': inventory},
                   total_literal_price_units=cost(profile) - cost(parent['report']['local_profile']),
                   overlay_spec_sections={sec: {k_: len(v_) for k_, v_ in s.items()} for sec, s in spec['sections'].items()})
        records[tag] = rec
    # evidence (not a gate): lane A's certified group-joint table against the literal stage-1 price
    groups = prices['stage1']['groups']
    assert all(g['joint_margin'] == -g['joint_delta'] - len(g['helpers']) * BE for g in groups)
    assert sum(g['joint_delta'] for g in groups) == records['base']['stage1']['literal_price_units'] == records['extra']['stage1']['literal_price_units']
    assert all(r[k]['literal_price_units'] == prices[k]['literal_price_units'] for r in records.values() for k in ('stage1', 'stage2', 'stage3'))
    n_s1 = sum(1 for k in controls if '-stage1-' in k); n_s2 = sum(1 for k in controls if '-stage2-' in k); n_s3 = sum(1 for k in controls if '-stage3-' in k)
    assert n_s1 == 2 * 10 and n_s2 == 2 * (5 * 5 + 1) and n_s3 == 2 * 7, (n_s1, n_s2, n_s3)
    assert all(sha(P / n) == h for n, h in pins.items()), 'input drift'
    result = {'status': 'PASS_RANK7_JOINT_ENDFRAMES_THREE_STAGE_REPLAY', 'providers': records, 'semantic_controls': controls,
              'control_counts': {'stage1': n_s1, 'stage2': n_s2, 'stage3': n_s3},
              'price_evidence': {'weights': prices['weights'], 'stage1_groups': groups,
                                 'note': 'Search-time certified prices (lane A); evidence only. The literal stage prices above are recomputed from the frame-report profiles.'},
              'local_profile': gen.PROFILE, 'width_inventory': gen.INVENTORY, 'buffers': gen.BUFFERS,
              'seconds': round(time.monotonic() - begin, 1),
              'scope': 'Exact finite local identities, frame invoices and all-input forward/dual replay of every stage word; native, owner and outer admission are separate.'}
    (out / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], 'controls', len(controls), 'seconds', result['seconds'], flush=True)


if __name__ == '__main__':
    main()
