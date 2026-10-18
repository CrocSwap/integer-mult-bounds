#!/usr/bin/env python3
"""Generate or check a witness: WITNESS.json (inputs) and EXPECTED.json (expected values).

  python3 spec.py generate --package PKG --witness WITNESS.json --work NEW_DIR --out-dir DIR [--source NAME=DIR ...]
  python3 spec.py check    --package PKG [--witness W.json] [--expected E.json] [--source NAME=DIR ...]

generate  completes the input hash pins of WITNESS.json (PLAN/OWNERS hashes, dispatch and call order from PLAN,
          recipe hashes) and writes it to DIR/WITNESS.json. It then runs the verifier once in discovery mode, which
          builds every provider word from the pinned sources and runs every check without comparing anything. Each
          recomputed value is copied into DIR/EXPECTED.json. No value is typed by hand.
check     validates both files and compares every pin that needs no replay: package MANIFEST, source manifests and
          files, PLAN/OWNERS, recipes, the dispatch against PLAN, and EXPECTED's binding to this WITNESS.
          verify.py does the full comparison.
"""
import argparse, hashlib, json, sys
from collections import Counter
from pathlib import Path

import verify as V

WITNESS_SCHEMA, EXPECTED_SCHEMA = 'witness/1', 'witness-expected/1'
GEOMETRY = ('v', 'h', 'helpers', 'centres', 'stages', 'replicas', 'cold_helpers')
UNPINNED_ARTIFACTS = ('CLIFFORD-REVIEW.json', 'SCALAR-FRAME-AUDIT.json')  # both record seconds; the phase review is pinned semantically
STEP_EXPECTED = ('input_content_sha256', 'output_content_sha256', 'omission_controls')
JOINT_EXPECTED = ('rank5_controls', 'joint_negative_controls')
PROVIDER_KEYS = ('semantic_phase_sha256', 'width_digest', 'program_hashes', 'artifacts', 'expected_profile', 'expected_local', 'entering',
                 'entrance', 'inventory', 'wrappers', 'phase_edges', 'native_negative_controls')
GLOBAL_KEYS = ('provider_counts', 'global_profile', 'owners_per_call', 'hosted_residuals', 'rank_mass', 'actual_73column_sigmas',
               'cross_replica_helper_roles', 'idle_remainders', 'live', 'physical', 'deficit', 'entering_helper_roles', 'idle_remainder_profile',
               'complex_lower', 'conservative_complex_lower', 'kappa', 'kappa_decimal', 'conservative_kappa_decimal', 'mutations_rejected',
               'assembly_controls_rejected')


def digest(x): return hashlib.sha256(json.dumps(x, separators=(',', ':')).encode()).hexdigest()


def write(p, x): Path(p).write_text(json.dumps(x, indent=1) + '\n', newline='\n')


def complete_witness(witness, v):
    """Fill the input hash pins a hand-written WITNESS.json may leave out; existing pins must already agree."""
    plan = V.read(v.pkg / 'data/PLAN.json')
    w = json.loads(json.dumps(witness))
    filled = dict(schema=WITNESS_SCHEMA,
                  data=dict(plan_sha256=V.sha(v.pkg / 'data/PLAN.json'), owners_sha256=V.sha(v.pkg / 'data/OWNERS.json.gz')),
                  dispatch=[[c['stage'], c['replica'], c['provider']] for c in plan['provider_calls']],
                  call_order=plan['order'])
    for k, value in filled.items():
        assert w.setdefault(k, value) == value, 'WITNESS.%s disagrees with the package' % k
    for pid, d in w['build']['providers'].items():
        for s in d['steps']:
            for k in ('recipe', 'kernel_recipes'):
                if k in s:
                    h = V.sha(v.ref(s[k]))
                    assert s.setdefault(k + '_sha256', h) == h, '%s %s hash disagrees with the file' % (pid, s[k])
    order = ('schema', 'name', 'geometry', 'gain_baseline_kappa', 'data', 'dispatch', 'call_order', 'build')
    return {k: w[k] for k in order}


def expected_from(run, witness_sha256):
    """Copy every expected value out of a discovery run's audited outputs."""
    G = run / 'mixed-global'
    inv = V.read(G / 'audit/PREFIX-AND-INVOICE.json')
    own = V.read(G / 'audit/OWNERS-AND-PROFILE.json')
    aud = V.read(G / 'audit/ASYNC-AUDIT.json')
    asm = V.read(run / 'ASSEMBLY.json')
    ac = V.read(run / 'ASSEMBLY-CONTROLS.json')
    providers = {}
    for pid, p in sorted(inv['providers'].items()):
        local = G / 'base/providers' / pid
        providers[pid] = dict(
            semantic_phase_sha256=p['semantic_artifact_sha256']['CLIFFORD-REVIEW.json'],
            width_digest=digest(p['widths']),
            program_hashes=p['program_hashes'],
            artifacts={k: h for k, h in p['artifacts'].items() if k not in UNPINNED_ARTIFACTS},
            expected_profile=p['paid_profile'],
            expected_local={o: {k: z[k] for k in ('events', 'macros', 'real_component_primitives', 'prefix_l1', 'coefficient_work_primitive_count')}
                            for o, z in p['local'].items()},
            entering=p['entering_helpers'],
            entrance=p['entrance_rank'],
            inventory=p['width_inventory'],
            wrappers=p['local'][next(iter(p['local']))]['pre_wrappers'],
            phase_edges=V.read(local / 'CLIFFORD-REVIEW.json')['directed_edges'],
            native_negative_controls=len(V.read(local / 'INDEPENDENT-LOCAL-REPLAY.json')['negative_controls_rejected']))
    glob = dict(
        provider_counts=inv['provider_counts'],
        global_profile=own['paid_profile'], owners_per_call=own['owners_per_call'], hosted_residuals=own['hosted_residuals'],
        rank_mass=own['rank_mass'], actual_73column_sigmas=own['actual_73column_sigmas'],
        cross_replica_helper_roles=own['cross_replica_helper_roles'], idle_remainders=own['explicit_idle_remainder_children'],
        live=own['live'], physical=own['physical'], deficit=own['deficit'], entering_helper_roles=aud['entering_helper_roles'],
        idle_remainder_profile=V.read(G / 'audit/IDLE-REMAINDER-FRAMES.json')['rank_profile'],
        complex_lower=asm['complex_lower'], conservative_complex_lower=asm['conservative_complex_lower'],
        kappa=asm['kappa'], kappa_decimal=asm['kappa_decimal'], conservative_kappa_decimal=asm['conservative_kappa_decimal'],
        mutations_rejected=len(aud['mutations_rejected']),
        # discovery cannot reject spec-only controls; the strict run must reject all of them
        assembly_controls_rejected=len(ac['rejected_controls']) + len(ac['discovery_accepted_controls']))
    return dict(schema=EXPECTED_SCHEMA, witness_sha256=witness_sha256, build=V.read(run / 'EXPECTED-BUILD.json'), providers=providers, **{'global': glob})


def verifier(a, discover, witness=None):
    return V.Verifier(argparse.Namespace(package=a.package.resolve(), witness=witness or a.witness, expected=getattr(a, 'expected', None),
                                         source=a.source, discover=discover))


def generate(a):
    a.out_dir.mkdir(parents=True, exist_ok=True)
    wfile, efile = a.out_dir / 'WITNESS.json', a.out_dir / 'EXPECTED.json'
    assert not efile.exists(), efile
    witness = complete_witness(V.read(a.witness), verifier(a, True))
    write(wfile, witness)
    v = verifier(a, True, wfile)
    bad = problems(witness, None)
    if bad:
        sys.exit('WITNESS INVALID\n' + '\n'.join(bad))
    v.verify(a.work, a.jobs)
    expected = expected_from(a.work.resolve(), V.sha(wfile))
    write(efile, expected)
    print('wrote', wfile, efile, 'kappa', expected['global']['kappa_decimal'])


def problems(w, e):
    """Structural problems of WITNESS.json and (if given) EXPECTED.json; empty when both are well formed."""
    bad = []
    need = lambda where, keys, label: bad.extend('%s: missing %s' % (label, k) for k in keys if k not in where)
    need(w, ('schema', 'name', 'geometry', 'gain_baseline_kappa', 'data', 'dispatch', 'call_order', 'build'), 'WITNESS')
    if bad:
        return bad
    if w['schema'] != WITNESS_SCHEMA:
        bad.append('WITNESS.schema: expected %s' % WITNESS_SCHEMA)
    g = w['geometry']
    need(g, GEOMETRY, 'WITNESS.geometry')
    need(w['data'], ('plan_sha256', 'owners_sha256'), 'WITNESS.data')
    need(w['build'], ('status', 'sources', 'providers'), 'WITNESS.build')
    if bad:
        return bad
    calls = sorted((s, r) for s in range(g['stages']) for r in range(g['replicas']))
    if sorted((s, r) for s, r, _ in w['dispatch']) != calls:
        bad.append('WITNESS.dispatch: must name each (stage, replica) exactly once')
    if sorted(map(tuple, w['call_order'])) != calls:
        bad.append('WITNESS.call_order: must be a permutation of all (stage, replica) calls')
    if not all(0 <= h < g['helpers'] for h in g['cold_helpers']):
        bad.append('WITNESS.geometry.cold_helpers: out of range')
    used = {p for _, _, p in w['dispatch']}
    if set(w['build']['providers']) != used:
        bad.append('WITNESS.build.providers: %s, dispatch uses %s' % (sorted(w['build']['providers']), sorted(used)))
    if 'multicold' not in w['build']['sources']:
        bad.append('WITNESS.build.sources: the PR568 package must be named multicold (it carries the frozen558 and vendor pipeline)')
    for name, s in w['build']['sources'].items():
        need(s, ('dir', 'manifest_sha256', 'files'), 'WITNESS.build.sources.' + name)
    for pid, d in w['build']['providers'].items():
        need(d, ('base', 'steps'), 'WITNESS.build.providers.' + pid)
        need(d.get('base', {}), ('kind',) + (('file',) if d.get('base', {}).get('kind') == 'source_file' else ()), 'WITNESS.build.providers.%s.base' % pid)
        for i, s in enumerate(d.get('steps', [])):
            label = 'WITNESS.build.providers.%s.steps[%d]' % (pid, i)
            if s.get('type') not in V.STEP_TYPES:
                bad.append('%s: step type %r not allowlisted %s' % (label, s.get('type'), V.STEP_TYPES))
            elif s['type'] != 'frozen558_scalar_audits':
                need(s, ('recipe', 'recipe_sha256') + (('variant', 'kernel_recipes', 'kernel_recipes_sha256') if s['type'] == 'joint_prefix' else ()), label)
    if e is None:
        return bad
    need(e, ('schema', 'witness_sha256', 'build', 'providers', 'global'), 'EXPECTED')
    if bad:
        return bad
    if e['schema'] != EXPECTED_SCHEMA:
        bad.append('EXPECTED.schema: expected %s' % EXPECTED_SCHEMA)
    need(e['global'], GLOBAL_KEYS, 'EXPECTED.global')
    if set(e['providers']) != used or set(e['build']) != used:
        bad.append('EXPECTED.providers/build: must name exactly the dispatched providers %s' % sorted(used))
    for pid in used & set(e['providers']):
        need(e['providers'][pid], PROVIDER_KEYS, 'EXPECTED.providers.' + pid)
    for pid in used & set(e['build']):
        b, steps = e['build'][pid], w['build']['providers'][pid]['steps']
        need(b, ('base_content_sha256', 'steps', 'word_content_sha256'), 'EXPECTED.build.' + pid)
        if len(b.get('steps', [])) != len(steps):
            bad.append('EXPECTED.build.%s.steps: %d steps, WITNESS has %d' % (pid, len(b.get('steps', [])), len(steps)))
            continue
        for i, (s, x) in enumerate(zip(steps, b['steps'])):
            if s['type'] != 'frozen558_scalar_audits':
                need(x, STEP_EXPECTED + (JOINT_EXPECTED if s['type'] == 'joint_prefix' else ()), 'EXPECTED.build.%s.steps[%d]' % (pid, i))
    if e.get('global', {}).get('provider_counts') != dict(Counter(p for _, _, p in w['dispatch'])):
        bad.append('EXPECTED.global.provider_counts: differs from WITNESS.dispatch')
    return bad


def check(a):
    v = verifier(a, False)
    bad = problems(v.witness, v.expected)
    if not bad:
        plan = V.read(v.pkg / 'data/PLAN.json')
        if [[c['stage'], c['replica'], c['provider']] for c in plan['provider_calls']] != v.witness['dispatch'] or plan['order'] != v.witness['call_order']:
            bad.append('WITNESS.dispatch/call_order: differ from data/PLAN.json')
    if bad:
        sys.exit('INVALID\n' + '\n'.join(bad))
    v.check_pins()
    print('CHECK OK', v.witness['name'], 'witness', V.sha(v.witness_file), 'expected', V.sha(v.expected_file))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('generate', help='complete WITNESS.json and derive EXPECTED.json')
    g.add_argument('--package', type=Path, required=True)
    g.add_argument('--witness', type=Path, required=True)
    g.add_argument('--work', type=Path, required=True, help='new directory for the discovery run')
    g.add_argument('--out-dir', type=Path, required=True, help='where WITNESS.json and EXPECTED.json are written (e.g. PKG/data)')
    g.add_argument('--source', action='append', default=[], metavar='NAME=DIR')
    g.add_argument('--jobs', type=int, default=3)
    c = sub.add_parser('check', help='validate WITNESS.json and EXPECTED.json and their static pins')
    c.add_argument('--package', type=Path, required=True)
    c.add_argument('--witness', type=Path)
    c.add_argument('--expected', type=Path)
    c.add_argument('--source', action='append', default=[], metavar='NAME=DIR')
    a = ap.parse_args(argv)
    generate(a) if a.cmd == 'generate' else check(a)


if __name__ == '__main__':
    main()
