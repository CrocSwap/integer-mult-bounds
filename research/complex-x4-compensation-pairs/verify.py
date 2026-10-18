#!/usr/bin/env python3
"""Reproduce the X4 finite compensation circuit and all exact prices (no kappa)."""
import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import experiment as E
import independent as I

CANONICAL = '1c0e9da767d4418f70016af599e4a447a3f7777acabe930318459c0fbbd260aa'
PROGRAMS = {'forward': '076a2d428f97abb30473df05110998efbe5ac809885bae4ceb1b8bd81329a1e6',
            'backward': '7915679ee305927463d19725360cc15132dd21ede18897d09a935dca1df0d55d'}
PROFILE = {1: 2548, 2: 338, 3: 430, 4: 194, 5: 56, 8: 8}


def inputs(root=E.HERE):
    manifest = E.read(root/'SOURCES.json')
    for name, expected in manifest['input_semantic_sha256'].items():
        E.require(E.digest(E.read(root/'inputs'/name)) == expected, 'source digest '+name)
    canonical = E.read(root/'inputs/CANONICAL-WORD.json.gz')
    programs = E.read(root/'inputs/LOCAL-PROGRAMS.json.gz')
    checks = E.read(root/'inputs/LOCAL-CHECKS.json')
    E.require(E.digest(canonical) == CANONICAL, 'selected canonical source pin')
    E.require((canonical['v'], canonical['R'], canonical['h']) == (112, 504, 9), 'geometry')
    E.require({int(k): v for k, v in canonical['local_profile'].items()} == PROFILE, 'paid profile')
    for name, expected in PROGRAMS.items():
        E.require(E.digest(programs[name]) == expected == checks[name]['sha256'], 'selected program '+name)
    return canonical, programs, checks


def build(root=E.HERE, rerun_search=True):
    c, programs, checks = inputs(root)
    C = E.compensation(c)
    E.require(E.row_gates(C) == sorted(c['compensation'], key=lambda g: g[1:3]), 'derived full compensation')
    recipe = E.read(root/'RECIPE.json')
    E.require(recipe['seed'] == 39, 'assignment seed')
    if rerun_search:
        pairs, search = E.search(C, seed=39)
        E.require(recipe == dict(seed=39, pairs=pairs, search=search), 'search/recipe reproduction')
    replacement = E.factored(C, recipe['pairs'])
    # Only targets and ordinary bottom-start / FULL-ended helpers are touched.
    for gate in replacement:
        for r in gate[1:3]:
            E.require(c['start'][r] == 0, 'nonzero start frame')
            if r >= 224:
                E.require(c['final'][r] == 1, 'cold/entering helper touch')
        E.require(gate[-1] == 0, 'nonzero replacement frame')
    changed = {name: E.splice(events, c, replacement, name == 'backward')
               for name, events in programs.items()}
    for name in programs:
        E.require([e for e in programs[name] if e[0] != 'scalar'] ==
                  [e for e in changed[name] if e[0] != 'scalar'], 'non-scalar event drift')
    return c, programs, checks, C, recipe, replacement, changed


def run(root=E.HERE, out=None):
    c, programs, checks, C, recipe, replacement, changed = build(root)
    n, v = 2*c['v']+c['R'], c['v']
    block_check = I.check_compensation(replacement, C, v, n)
    rows = {}
    for name in ('forward', 'backward'):
        back = name == 'backward'
        before = E.replay_emitted(programs[name], n, v, back)
        after = E.replay_emitted(changed[name], n, v, back)
        E.require(before['real_component_primitives'] == checks[name]['real_component_primitive_bound'], 'baseline price')
        E.require(before['scalar_macros'] == checks[name]['scalar_macros'], 'baseline macro count')
        E.require(before['paid_profile'] == after['paid_profile'] == PROFILE, 'child profile')
        E.require(after['prefix_bits'] == before['prefix_bits'] and after['prefix_bits'] < 192, 'inherited local guard')
        actual_gain = before['real_component_primitives']-after['real_component_primitives']
        E.require(actual_gain == sum(p[3] for p in recipe['pairs']) > 0, 'complete price gain')
        old_logical = I.check(E.logical_program(c, c['compensation']), n, dual=back, v=v)
        new_logical = I.check(E.logical_program(c, replacement), n, dual=back, v=v)
        E.require(old_logical['endpoint_sha256'] == new_logical['endpoint_sha256'], 'independent endpoint')
        rows[name] = dict(baseline=before, candidate=after, saved_real_primitives=actual_gain,
                          independent_baseline=old_logical, independent_candidate=new_logical)
    result = dict(status='PASS_X4_COMPENSATION_PAIRS', base_commit='f567884aeb8851b6e794af1184119a3bfbe1e631',
                  selected_kappa_unchanged='1661634653669567/1000000000000000000', seed=39,
                  pairs=len(recipe['pairs']), search=recipe['search'],
                  compensation_adds_before=len(c['compensation']), compensation_adds_after=len(replacement),
                  compensation_boundary=block_check, orientations=rows,
                  scope='Finite scalar circuit; exact all-column and primitive-prefix replays. No global invoice, supplier compilation or new kappa.')
    if out is not None:
        out = Path(out)
        E.require(not out.exists(), 'output directory must be new')
        out.mkdir(parents=True)
        (out/'CANDIDATE-PROGRAMS.json.gz').write_bytes(gzip.compress(
            json.dumps(changed, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
        (out/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, help='optional fresh directory for the literal candidate programs')
    ap.add_argument('--record', action='store_true', help='write the reproducible RESULT.json after all checks')
    args = ap.parse_args()
    result = run(out=args.out)
    normalized = json.loads(json.dumps(result))
    if args.record:
        (E.HERE/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    else:
        E.require(normalized == E.read(E.HERE/'RESULT.json'), 'saved result mismatch')
    print('PASS_X4_COMPENSATION_PAIRS pairs=%d compensation=%d->%d saved_real=33800 columns=728+9 orientations=2 no_new_kappa' %
          (result['pairs'], result['compensation_adds_before'], result['compensation_adds_after']))


if __name__ == '__main__':
    main()
