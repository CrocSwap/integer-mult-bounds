#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact local replay of the four normal-45 paired extractions on PR2917's words.

(a) producer.py reconstructs both WORD files from PARENT (= PR2917's words) and the four declared
    TRANSFORMs (complete decoded content);
(b) at every step, the unchanged PR2908/PR2917 structure.py (Jeremy Diviney) checks the seven exact
    two-sided free-operator identities on the step's (refit) parent and its literal input/output gates;
(c) the unchanged PR2833 auditor (vendor/audit_local.py, as vendored by PR2917) replays both final words
    forward and dual over all 632 independent inputs: PASS_INDEPENDENT_EXACT_BORROWING_WORD, 86 buffers;
(d) frame accounting: preload_move.frame_report(word) equals the word's report and the declared profile;
(e) five semantic mutants per step and provider (drop an input gate, flip an output coefficient, move the
    output change to a wrong hyperplane, stale cleanup without the new private buffer, omit the step's
    declared frame edits) must each be rejected by the auditor, and the two gate mutants also by the
    certificate;
(f) the overlay producer tools/wordedit.py round-trips PARENT -> WORD exactly (the recorded-spec stage).
Structure adapted from Mason Hale's PR2917 verify.py. Marius-Paul Dumitrean, with substantial AI
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
    assert local | {'producer.py', 'structure.py', 'tools/wordedit.py'} <= set(pins), 'every local input pinned'
    assert all(sha(P / n) == h for n, h in pins.items()), 'pinned bytes'
    out.mkdir(parents=True)
    pm = load('preload_move', P / 'vendor/preload_move.py')
    gen = load('normal45_producer', P / 'producer.py')
    aud = load('independent_paired_audit', P / 'vendor/audit_local.py')
    structural = load('independent_paired_structure', P / 'structure.py')
    we = load('normal45_wordedit', P / 'tools/wordedit.py')
    transforms = [read(P / f'data/TRANSFORM-{h}.json') for h in gen.HELPERS]
    assert all(t['normal'] == gen.NORMAL and t['after'][0][-1] == gen.FRAME == gen.hyperplane(gen.NORMAL) for t in transforms)
    wrong = gen.hyperplane(46)

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
            structural.check(gen.refit(parent, transform), transform, aud)
        except (AssertionError, KeyError, ValueError) as error:
            return type(error).__name__ + ' ' + str(error)[:160]
        raise AssertionError('mutant transform accepted by the certificate: ' + name)

    def recut(word, restored):
        z = copy.deepcopy(word)
        z['A'] = z['A'][z['prelude_events']:]
        return pm.derive_cleanup(z, restored)

    def rereport(word):
        try:
            profile, inventory = pm.frame_report(word)
        except ValueError:
            return word    # an illegal frame chain keeps the claimed report; the auditor recounts it
        word['report']['local_profile'], word['report']['width_inventory'] = profile, inventory
        return word

    records, controls = {}, {}
    for tag in ('base', 'extra'):
        parent = read(P / f'data/PARENT-{tag}.json.gz')
        assert len(parent['helper_final']) == gen.PARENT_BUFFERS
        w, steps = parent, []
        for k, t in enumerate(transforms, 1):
            h, n = t['helper'], w['prelude_events']
            cert = structural.check(gen.refit(w, t), t, aud)
            assert cert['status'] == 'PASS_EXACT_TWO_SIDED_SUBSPACE_CERTIFICATE' and cert['helper'] == h
            child = gen.apply_stage(w, t)
            profile, inventory = pm.frame_report(child)
            assert (profile, inventory) == (child['report']['local_profile'], child['report']['width_inventory'])
            assert child['helper_final'][str(h)] == gen.FRAME and len(child['helper_final']) == gen.PARENT_BUFFERS + k
            name = f'{tag}-step{k}-{h}'
            # (e1) drop the first literal input gate (the input change S no longer carries v)
            bad = copy.deepcopy(child); del bad['A'][n]
            bad['cleanup'] = recut(rereport(bad), set(map(int, bad['helper_final'])))
            bt = dict(t, before=t['before'][1:])
            controls[name + '-drop-input-gate'] = {'auditor': rejected(bad, name + '-drop-input-gate'),
                                                   'certificate': cert_rejects(w, bt, name + '-drop-input-gate')}
            # (e2) flip the sign of the first output addition (T no longer has row alpha / column e_h)
            i = next(j for j, g in enumerate(t['after']) if g[0] == 'add')
            bad = copy.deepcopy(child); g = bad['restore'][len(w['restore']) + i]; g[3] = -g[3]
            bad['cleanup'] = recut(rereport(bad), set(map(int, bad['helper_final'])))
            after = copy.deepcopy(t['after']); after[i][3] = -after[i][3]
            controls[name + '-flip-output-coefficient'] = {'auditor': rejected(bad, name + '-flip-output-coefficient'),
                                                           'certificate': cert_rejects(w, dict(t, after=after), name + '-flip-output-coefficient')}
            # (e3) the whole output change and the endpoint on the wrong hyperplane E_46
            bad = copy.deepcopy(child)
            for g in bad['restore'][len(w['restore']):]:
                g[-1] = list(wrong)
            bad['helper_final'][str(h)] = list(wrong)
            bad['cleanup'] = recut(rereport(bad), set(map(int, bad['helper_final'])))
            controls[name + '-wrong-hyperplane'] = {'auditor': rejected(bad, name + '-wrong-hyperplane')}
            # (e4) stale cleanup: re-derived without the new endpoint's private zero buffer
            bad = copy.deepcopy(child)
            bad['cleanup'] = recut(bad, set(map(int, w['helper_final'])))
            controls[name + '-stale-cleanup'] = {'auditor': rejected(bad, name + '-stale-cleanup')}
            # (e5) omit the step's declared frame edits (keep the claimed report and cleanup)
            assert t['frame_changes']
            bad = copy.deepcopy(child)
            for e in t['frame_changes']:
                assert bad[e['section']][e['candidate_index']][:-1] == e['gate'] and bad[e['section']][e['candidate_index']][-1] == e['new_frame']
                bad[e['section']][e['candidate_index']][-1] = list(e['old_frame'])
            controls[name + '-omit-frame-edits'] = {'auditor': rejected(bad, name + '-omit-frame-edits')}
            steps.append({'step': k, 'helper': h, 'normal': t['normal'], 'hyperplane': gen.FRAME,
                          'inputs': len(t['before']), 'outputs': len(t['after']), 'frame_edits': len(t['frame_changes']),
                          'certificate': {key: cert[key] for key in ('status', 'helper', 'alpha', 'y', 'u', 'v')},
                          'local_profile': profile, 'width_inventory': inventory, 'buffers': len(child['helper_final'])})
            w = child
        word_path = P / f'data/WORD-{tag}.json.gz'
        shipped = read(word_path)
        assert gen.apply(parent, transforms) == w == shipped, 'complete producer reconstruction'
        changed = sorted(key for key in parent if parent[key] != shipped[key])
        assert set(changed) == gen.ALLOWED, 'exact changed sections'
        report = audit(shipped, f'AUDIT-{tag}')
        assert report['status'] == 'PASS_INDEPENDENT_EXACT_BORROWING_WORD'
        assert report['orientations'] == {'forward': 'PASS', 'dual': 'PASS'}
        assert report['independent_inputs'] == 632 and report['restored_cold'] == report['zero_buffers'] == gen.BUFFERS
        assert {str(r): c for r, c in report['local_profile'].items()} == gen.PROFILE
        assert {str(r): c for r, c in report['width_inventory'].items()} == gen.INVENTORY
        profile, inventory = pm.frame_report(shipped)
        assert profile == shipped['report']['local_profile'] == gen.PROFILE and inventory == shipped['report']['width_inventory'] == gen.INVENTORY
        spec = we.make_spec(parent, shipped)
        assert we.apply_spec(parent, spec) == shipped and shipped['cleanup'] == we.derive_cleanup(shipped), 'overlay spec round trip'
        records[tag] = {'parent_sha256': sha(P / f'data/PARENT-{tag}.json.gz'), 'word_sha256': sha(word_path),
                        'changed_sections': changed, 'steps': steps,
                        'audit': {key: report[key] for key in ('status', 'independent_inputs', 'restored_cold', 'zero_buffers',
                                                               'local_profile', 'width_inventory', 'local_mass', 'orientations', 'content_sha256')},
                        'frame_report': {'local_profile': profile, 'width_inventory': inventory},
                        'overlay_spec_sections': {sec: {k_: len(v_) for k_, v_ in s.items()} for sec, s in spec['sections'].items()}}
    assert len(controls) == 5 * len(transforms) * 2
    assert all(sha(P / n) == h for n, h in pins.items()), 'input drift'
    result = {'status': 'PASS_FOUR_NORMAL45_PAIRED_EXTRACTIONS', 'providers': records, 'semantic_controls': controls,
              'local_profile': gen.PROFILE, 'width_inventory': gen.INVENTORY, 'buffers': gen.BUFFERS,
              'seconds': round(time.monotonic() - begin, 1),
              'scope': 'Exact finite local identities, frame invoice and all-input forward/dual replay; native, owner and outer admission are separate.'}
    (out / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], 'controls', len(controls), 'seconds', result['seconds'], flush=True)


if __name__ == '__main__':
    main()
