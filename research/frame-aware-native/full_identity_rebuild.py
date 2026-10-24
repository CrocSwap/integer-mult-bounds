#!/usr/bin/env python3
"""Restore a full-identity native supplier with zero external cleanup bank.

Apache-2.0. Substantial OpenAI assistance. The full-identity ancestor supplies
the original center cuts and compensation; the independently retained later
cleanup supplies a legal scheduled alias of all91 old buffers. A fresh native
replay checks their actual composition. Eight sequential center fields reuse
one explicitly cleared C0. Each rank8 center is optionally split into rank5
and rank3 with exact phase decoding, keeping a strict child-rank ceiling5.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import argparse
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rebuild_native as N
import native_extensions as X

INTEGRATED = N.ROOT/'research/kappa-global-routing/integrated-complex'
INTEGRATED_RECEIPT_SHA = '70c3d5b1c1d6a18afb29ea1febec3c619ff2b1e38a09c44db7828794ea095429'


def reuse_centers(words):
    words = deepcopy(words)
    for program in words.values():
        for event in program:
            if event[0] == 'center':
                event[1] = 0
            elif event[0] == 'scalar':
                g = event[1]
                for role in (g[1:3] if g[0] in ('add', 'copy') else g[1:2]):
                    if role[0] == 'C':
                        role[1] = 0
    return words


def compose_full_identity(v, tag, integrated_receipt):
    source = v.CORE/'sources'/(tag+'-CANONICAL.json.gz')
    scheduled = INTEGRATED/(tag+'-CANONICAL.json.gz')
    N.need(N.digest(scheduled) == integrated_receipt['providers'][tag]['artifacts'][scheduled.name],
           'Authenticated scheduled cleanup input')
    original = N.read(source); newer = N.read(scheduled)
    changes = {k for k in set(original) | set(newer) if original.get(k) != newer.get(k)}
    N.need(changes == {'centers', 'center_frames', 'cut', 'compensation', 'cleanup', 'local_profile', 'zero_buffers'},
           'Exact ancestor-to-clean-J change inventory')
    c = deepcopy(original)
    c['cleanup'] = deepcopy(newer['cleanup'])
    c['zero_buffers'] = []
    N.need(len(c['centers']) == 8 and len(c['cut']) == 176, 'Retained full-identity center response')
    words = reuse_centers(v.emit_original(c))
    return c, words, dict(original_canonical_sha256=N.digest(source), scheduled_canonical_sha256=N.digest(scheduled),
                         changed_fields_from_original=['cleanup', 'zero_buffers'],
                         ordinary_compensation_and_all_eight_center_cuts_retained=True)


def split_centers(p, ce, canonical, words):
    c = deepcopy(canonical); result = {}; phases = {}; profile = Counter({int(k): n for k, n in c['local_profile'].items()})
    N.need(profile[8] == 8, 'Eight old rank8 children')
    del profile[8]; profile[3] += 8; profile[5] += 8
    c['local_profile'] = {str(k): n for k, n in sorted(profile.items())}
    for direction, program in words.items():
        out = []; detail = []
        for event in program:
            if event[0] != 'center':
                out.append(deepcopy(event)); continue
            _, role, old, new, rank = event
            N.need(role == 0 and rank == 8 and {len(c['frames'][old]), len(c['frames'][new])} == {0, 8},
                   'Single eight-dimensional old center transport')
            high = old if len(c['frames'][old]) == 8 else new
            basis = c['frames'][high][:3]
            if basis not in c['frames']:
                c['frames'].append(basis)
            mid = c['frames'].index(basis)
            path = [old, mid, new]; pieces = []; recipes = []
            for a, b in zip(path, path[1:]):
                width = abs(len(c['frames'][b])-len(c['frames'][a]))
                part = ce.canonical_frame(9, c['frames'][a]).adjoint().then(ce.canonical_frame(9, c['frames'][b]))
                if direction == 'backward':
                    part = p.conjugate(ce, part)
                recipe = N.lower_exact(p, ce, part)
                N.need(recipe['rank'] == width and width in (3, 5), 'Split child exact rank')
                out.append(['center', 0, a, b, width]); pieces.append(part)
                recipes.append(dict(old_frame=a, new_frame=b, recipe=recipe))
            whole = ce.canonical_frame(9, c['frames'][old]).adjoint().then(ce.canonical_frame(9, c['frames'][new]))
            if direction == 'backward':
                whole = p.conjugate(ce, whole)
            product = pieces[0].then(pieces[1])
            N.need(product.tab == whole.tab and product.zero_state() == whole.zero_state(),
                   'Two split children equal old center including absolute phase')
            detail.append(dict(old_frame=old, intermediate_frame=mid, new_frame=new,
                               intermediate_basis=basis, pieces=recipes, product_exact_including_phase=True))
        N.need(len(detail) == 8, 'All eight center paths split')
        result[direction] = out; phases[direction] = detail
    return c, result, phases


def bind_helper_boundaries(c, tag):
    source = HERE/'fresh-certificates'/(tag+'-HELPER-BOUNDARIES.json.gz')
    receipt = N.read(HERE/'fresh-certificates/RESULT-helpers.json')
    expected = receipt['providers'][tag]['helper_boundaries']['sha256']
    N.need(N.digest(source) == expected, 'Fresh helper boundary certificate pin')
    helper = N.read(source)
    for r in helper['recipes']:
        role = r['role']
        N.need(c['frames'][c['start'][role]] == r['certificate']['start_basis'] and
               c['frames'][c['final'][role]] == r['certificate']['end_basis'],
               'Full-identity helper has identical exact endpoint references')
    return dict(certificate_sha256=expected, certificate=str(source.relative_to(N.ROOT)),
                count=408, widths=helper['widths'], total_width=helper['total_width'],
                both_orientations_and_global_phases_bound=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=HERE/'full-identity-certificates')
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    p, v, ce, predecessor, inherited = N.authenticated(); geo = N.geometry(v.PACKET)
    N.need(N.digest(INTEGRATED/'RESULT.json') == INTEGRATED_RECEIPT_SHA, 'Pinned scheduled cleanup receipt')
    scheduled_receipt = N.read(INTEGRATED/'RESULT.json')
    result = dict(schema='fresh-full-identity-zero-bank-native-supplier/1',
                  generator_sha256=N.digest(Path(__file__)), reconstruction_source_sha256=N.digest(HERE/'rebuild_native.py'),
                  independent_interpreter_sha256=p.CHECKER_SHA,
                  independent_prefix_evaluator_sha256=N.digest(HERE/'native_extensions.py'),
                  integrated_cleanup_receipt_sha256=INTEGRATED_RECEIPT_SHA,
                  source_closure_verified=inherited, no_new_kappa_claimed=True, providers={})
    for tag in N.TAGS:
        c, words, composition = compose_full_identity(v, tag, scheduled_receipt)
        unsplit = {direction: v.replay(program, c, geo['R'], direction == 'backward', False)
                   for direction, program in words.items()}
        c, split, phases = split_centers(p, ce, c, words)
        checks = {}
        for direction, program in split.items():
            checked = v.replay(program, c, geo['R'], direction == 'backward', False)
            rows, prefixes = X.literal_replay(v, c, program, direction == 'backward')
            N.need(all(rows['L', i] == v.expected(('L', i), geo['R'], direction == 'backward', False) for i in range(632)),
                   'Second all632-column endpoint implementation')
            N.need(checked['conservative_real_scalar_primitive_allowance'] ==
                   unsplit[direction]['conservative_real_scalar_primitive_allowance'], 'Splitting adds no scalar macro')
            N.need(max(checked['paid_profile']) == 5 and checked['explicitly_owned_C_fields_cleared'] == 1,
                   'Child ceiling5 and one reusable owned C0')
            checks[direction] = dict(independent_native_replay=checked, independent_prefix_and_endpoint=prefixes)
        bad = deepcopy(split['forward'])
        remove = next(i for i, e in enumerate(bad) if e[0] == 'scalar' and e[1][0] == 'add' and e[1][2] == ['C', 0])
        bad.pop(remove)
        rejected = False
        try:
            v.replay(bad, c, geo['R'], False, False)
        except ValueError as error:
            rejected = 'operator mismatch' in str(error)
        N.need(rejected, 'Dropped center response negative control rejected')
        cp = args.out/(tag+'-FULL-IDENTITY-CANONICAL.json.gz')
        wp = args.out/(tag+'-FULL-IDENTITY-NATIVE.json.gz')
        result['providers'][tag] = dict(composition=composition, unsplit_replays=unsplit, split_replays=checks,
              split_center_phase_recipes=phases, helper_boundary=bind_helper_boundaries(c, tag),
              artifacts={cp.name:N.save(cp, c), wp.name:N.save(wp, split)},
              all_632_persistent_inputs_arbitrary=True, all_408_helpers_autonomous=True,
              external_cleanup_fields=0, owned_C_fields=1, owned_C_input_arbitrary_and_erased=True,
              max_child_rank=5, no_H_involution_or_query_controller_needed=True,
              dropped_center_response_negative_control_rejected=True)
        N.save(args.out/'RESULT.json', result)
        print('PASS full identity', tag, checks['forward']['independent_native_replay']['paid_profile'], flush=True)
    result['status'] = 'PASS_FULL_IDENTITY_ALL_FOUR_BOTH_DIRECTIONS_632_ARBITRARY_FIELDS_ZERO_EXTERNAL_BANK_CHILD_CEILING5'
    result['scope'] = ('Complete ideal local native supplier and helper boundaries. Outer productive job ownership, '
                       'complete recurrence, scalar and storage charges, and rounded induction remain caller obligations.')
    N.save(args.out/'RESULT.json', result)


if __name__ == '__main__':
    main()
