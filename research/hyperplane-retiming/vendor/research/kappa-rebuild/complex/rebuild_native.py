#!/usr/bin/env python3
"""Fresh reconstruction of H112, its dirty logger and helper boundary factors.

Apache-2.0. Substantial OpenAI assistance. This is newly generated evidence;
it does not recreate or assert the identity of files lost in an earlier session.
The immutable predecessor is the attributed function-composition clean-J word.
Logical sparse replay extends the independently pinned verify_buffers grammar.
Physical lowering uses the attributed exact Clifford compiler and independently
decodes each new recipe, comparing tableau AND the exact zero-state phase.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import platform
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P_PATH = ROOT/'research/kappa-function-composition/complex/prune_native.py'
BASE = P_PATH.parent/'pruned-native'
P_SHA = 'f2b37c183a10922eabc8e0436b426a08866430e96bd0adc7e178951c7fbb5257'
RECEIPT_SHA = 'b62c6c123f43a697802a336ee7178942040c0249c64ebc19cd6aad7ba2728ae7'
CE_SHA = '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'
TAGS = ('THREE-base', 'THREE-extra', 'FOUR-base', 'FOUR-extra')
SELECTED = (0, 7, 20, 27, 36, 46, 57, 111)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def save(path, value):
    path = Path(path)
    data = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data+b'\n')
    return digest(path)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def authenticated():
    need(digest(P_PATH) == P_SHA, 'Pinned clean-J reconstruction utility')
    need(digest(BASE/'RESULT.json') == RECEIPT_SHA, 'Pinned clean-J receipt')
    p = load(P_PATH, 'fresh_h112_prune')
    need(digest(p.CHECKER) == p.CHECKER_SHA, 'Pinned independent native interpreter')
    need(digest(p.CLIFFORD) == CE_SHA, 'Pinned phase compiler')
    v = load(p.CHECKER, 'fresh_h112_independent')
    inherited = v.authenticate()
    ce = load(p.CLIFFORD, 'fresh_h112_clifford')
    receipt = read(BASE/'RESULT.json')
    for tag in TAGS:
        for filename, expected in receipt['providers'][tag]['artifacts'].items():
            need(digest(BASE/filename) == expected, 'Pinned predecessor artifact '+filename)
    return p, v, ce, receipt, inherited


def geometry(packet):
    """Return exact sparse R, L and the freshly checked 112 by 112 H."""
    packet = read(packet) if isinstance(packet, (str, Path)) else packet
    R = [{int(k): Q(x) for k, x in row.items()} for row in packet['R_rows']]
    ordinary = tuple(i for i in range(112) if i not in SELECTED)
    need(len(R) == 8, 'Eight query rows')
    dot = lambda a, b: sum((x*b.get(j, Q(0)) for j, x in a.items()), Q(0))
    need(all(dot(a, b) == 56*int(i == j) for i, a in enumerate(R) for j, b in enumerate(R)), 'R R^t = 56 I')
    need(all(sum((r.get(a, 0)*r.get(b, 0) for r in R), Q(0)) == 4*int(a == b)
             for a in SELECTED for b in SELECTED), 'Selected Gram matrix 4 I')
    L = [{p: q for p in ordinary if (q := sum((r.get(a, 0)*r.get(p, 0) for r in R), Q(0))/4)}
         for a in SELECTED]
    need(all(len(row) == 52 and set(map(abs, row.values())) == {Q(1, 2)} for row in L), '416 half-integral L entries')
    need(all(dot(a, b) == 13*int(i == j) for i, a in enumerate(L) for j, b in enumerate(L)), 'L L^t = 13 I')
    J = []
    H = []
    for i in range(112):
        row = {j: q for j in range(112)
               if (q := Q(i == j)-sum((r.get(i, 0)*r.get(j, 0) for r in R), Q(0))/4)}
        J.append(row)
        changed = dict(row)
        if i in SELECTED:
            k = SELECTED.index(i)
            for j, x in {i: Q(1), **L[k]}.items():
                changed[j] = changed.get(j, Q(0))+12*x
                if not changed[j]:
                    del changed[j]
        H.append(changed)
    need(all(sum((x*H[k].get(j, 0) for k, x in H[i].items()), Q(0)) == int(i == j)
             for i in range(112) for j in range(112)), 'Exact H squared equals identity')
    need(any(H[i].get(j, 0) != H[j].get(i, 0) for i in range(112) for j in range(112)), 'H is not symmetric')
    return dict(selected=SELECTED, ordinary=ordinary, R=R, L=L, J=J, H=H)


def kernel_h(packet):
    return geometry(packet)['H']


def scalar(op, frame):
    return ['scalar', op, frame]


def make_h_word(canonical, base_word, geo):
    """Forward suffix and separate backward prefix; H is NOT self-transpose."""
    out = deepcopy(base_word)
    for backward in (False, True):
        correction = [['phase', 'fresh_H112_completion']]
        common = 0 if backward else 1
        source_offset = 112 if backward else 0
        target_offset = 0 if backward else 112
        for k, a in enumerate(geo['selected']):
            target_frame = canonical['start'][a] if backward else canonical['final'][112+a]
            correction += [scalar(['clear', ['C', 0]], common),
                           scalar(['copy', ['C', 0], ['L', source_offset+a]], common)]
            correction += [scalar(['add', ['C', 0], ['L', source_offset+p], q.numerator, q.denominator], common)
                           for p, q in sorted(geo['L'][k].items())]
            correction += [['center', 0, common, target_frame, 1],
                           scalar(['add', ['L', target_offset+a], ['C', 0], -12 if backward else 12, 1], target_frame),
                           scalar(['clear', ['C', 0]], target_frame)]
        name = 'backward' if backward else 'forward'
        out[name] = correction+out[name] if backward else out[name]+correction
    return out


def make_logger_word(canonical, base_word, geo):
    """Eight arbitrary cache fields; the caller owns their dirty baselines."""
    suffix = [['phase', 'fresh_forward_dirty_query_logger']]
    for k, a in enumerate(geo['selected']):
        suffix += [['cache_child', k, 0, 1, 9], scalar(['add', ['P', k], ['L', a], 1, 1], 1)]
        suffix += [scalar(['add', ['P', k], ['L', p], q.numerator, q.denominator], 1)
                   for p, q in sorted(geo['L'][k].items())]
    return base_word['forward']+suffix


def primitive_allowance(op):
    if op[0] in ('clear', 'copy'):
        return 2
    q = Q(op[3], op[4]) if op[0] == 'add' else Q(op[2], op[3])
    n, d = abs(q.numerator), q.denominator
    need(n and not d & (d-1), 'Nonzero dyadic scalar')
    if op[0] == 'scale':
        need(not n & (n-1), 'Dyadic unit SCALE')
        return 2*(abs(n.bit_length()-d.bit_length())+int(q < 0))
    need(op[0] == 'add', 'Known scalar macro')
    return 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)


def replay_extended(v, program, canonical, geo, backward=False, endpoint='H', cache_count=0,
                    expected_profile=None, allow_mismatch=False):
    """Literal exact all-column native replay, including arbitrary C at entry.

    Transports change canonical coordinate tags and retain logical row values;
    separate phase receipts implement the exact physical coordinate change.
    Warp words remain free noncommuting symbols, including dual orientation.
    """
    need(endpoint in ('H', 'J', 'logger'), 'Known endpoint')
    n = len(canonical['start'])
    need(n == 632, '632 persistent predecessor roles')
    rows = {('L', i): v.identity(('L', i)) for i in range(n)}
    current = {('L', i): f for i, f in enumerate(canonical['start'])}
    centers = {e[1] for e in program if e[0] == 'center'}
    centers |= {r[1] for e in program if e[0] == 'scalar'
                for r in (e[1][1:3] if e[1][0] in ('add', 'copy') else e[1][1:2])
                if r[0] == 'C'}
    need(centers <= {0}, 'Only one owned completion field')
    for i in centers:
        rows['C', i] = v.identity(('C', i)); current['C', i] = None
    for i in range(cache_count):
        rows['P', i] = v.identity(('P', i)); current['P', i] = 0
    spaces = [v.span(vectors) for vectors in canonical['frames']]
    dimensions = [len(s).bit_length()-1 for s in spaces]
    profile = Counter(); counts = Counter(); scalar_cost = 0
    max_l1 = Q(1); max_coefficient = Q(1); max_numerator = 1; max_denominator = 1
    witness = {'event': -1, 'role': ['L', 0]}
    for i, e in enumerate(program):
        kind = e[0]; counts[kind] += 1; touched = None
        if kind in ('climb', 'center', 'cache_child'):
            if kind == 'climb':
                _, part, j, old, new, rank = e; role = ('L', j)
                need(spaces[old] < spaces[new], 'Strict ascending borrowed climb')
            else:
                _, j, old, new, rank = e
                role = ('C' if kind == 'center' else 'P', j)
                need(spaces[old] < spaces[new] or spaces[new] < spaces[old], 'Nested transport')
            need(current[role] == old and rank == abs(dimensions[new]-dimensions[old]), 'Transport frame and exact rank')
            current[role] = new; profile[rank] += 1
        elif kind == 'warp':
            _, r, op, old, new = e; role = tuple(r)
            need(current[role] == old, 'Warp source frame')
            rows[role] = v.warp(rows[role], op, backward); current[role] = new; touched = role
        elif kind == 'scalar':
            op, frame = e[1:]; role = tuple(op[1]); touched = role
            scalar_cost += primitive_allowance(op)
            if op[0] == 'clear':
                need(role[0] == 'C', 'No clearing arbitrary persistent inputs')
                rows[role] = {}; current[role] = frame
            else:
                need(current[role] == frame, 'Scalar target frame at event '+str(i))
                if op[0] in ('add', 'copy'):
                    source = tuple(op[2]); need(current[source] == frame, 'Scalar source frame at event '+str(i))
                    if op[0] == 'copy':
                        need(role[0] == 'C', 'Copy targets owned field')
                        rows[role] = dict(rows[source])
                    else:
                        need(role != source, 'Reversible ADD distinct registers')
                        v.add(rows[role], rows[source], Q(op[3], op[4]))
                else:
                    q = Q(op[2], op[3]); rows[role] = {k: q*x for k, x in rows[role].items()}
        else:
            need(kind in ('phase', 'adapter', 'residual_adapter'), 'Unsupported event '+kind)
        if touched is not None:
            values = [abs(x) for x in rows[touched].values()]
            norm = sum(values, Q(0))
            if norm > max_l1:
                max_l1 = norm; witness = {'event': i, 'role': list(touched)}
            if values:
                max_coefficient = max(max_coefficient, max(values))
                max_numerator = max(max_numerator, max(x.numerator for x in values))
                max_denominator = max(max_denominator, max(x.denominator for x in values))
    need([current['L', i] for i in range(n)] == canonical['final'], 'Exact final native frames')
    need(all(current['P', i] == 1 for i in range(cache_count)), 'Logger cache terminal frame')
    if expected_profile is not None:
        need(dict(profile) == {int(k): x for k, x in expected_profile.items()}, 'Complete profile binding')
    mismatch = []
    matrix = geo['H'] if endpoint == 'H' else geo['J']
    for role, actual in rows.items():
        wanted = {} if role[0] == 'C' else v.identity(role)
        if role[0] == 'L':
            port = role[1] if backward else role[1]-112
            if 0 <= port < 112:
                offset, sign = (112, -1) if backward else (0, 1)
                for j, q in matrix[port].items():
                    v.add(wanted, v.identity(('L', offset+j)), sign*q)
        elif role[0] == 'P':
            need(endpoint == 'logger' and not backward, 'Only forward logger cache contract')
            k = role[1]
            for j, q in {geo['selected'][k]: Q(1), **geo['L'][k]}.items():
                v.add(wanted, v.identity(('L', j)), q)
        if actual != wanted:
            differences = {k: actual.get(k, Q(0))-wanted.get(k, Q(0)) for k in actual.keys() | wanted.keys()}
            differences = {k: x for k, x in differences.items() if x}
            first = min(differences)
            mismatch.append({'role': list(role), 'unequal_coefficients': len(differences),
                             'first_input': list(first[0]), 'first_word': list(first[1]),
                             'first_coefficient': str(differences[first])})
    if not allow_mismatch:
        need(not mismatch, 'Endpoint mismatch: '+repr(mismatch[:3]))
    return dict(direction='backward' if backward else 'forward', endpoint=endpoint,
                independent_persistent_input_fields=n+cache_count,
                independently_initialized_owned_C_fields=len(centers), owned_C_fields_zero_at_exit=all(not rows['C', i] for i in centers),
                all_408_helpers_exactly_restored_in_logical_coordinates=all(rows['L', i] == v.identity(('L', i)) for i in range(224, 632)),
                all_scalar_frames_checked=True, all_new_coefficients_dyadic=True,
                event_counts=dict(counts), paid_profile=dict(sorted(profile.items())),
                paid_rank_mass=sum(k*x for k, x in profile.items()), real_scalar_allowance=scalar_cost,
                prefix=dict(max_formal_row_l1=str(max_l1), max_abs_coefficient=str(max_coefficient),
                            max_abs_numerator=max_numerator, max_denominator=max_denominator, l1_witness=witness,
                            scope='Exact logical ideal prefixes; no rounded recursive error bound.'),
                exact_endpoint=not mismatch, mismatch_examples=mismatch[:3])


def lower_exact(p, ce, op):
    recipe, _ = ce.lower_child(op)
    left = p.monomial(ce, recipe['left'], op.n)
    if recipe['rank']:
        right = p.monomial(ce, recipe['right'], op.n)
        decoded = right.then(ce.fourier(op.n, range(recipe['rank']))).then(left)
    else:
        decoded = left
    need(decoded.tab == op.tab and decoded.zero_state() == op.zero_state(), 'Independent recipe decode including absolute phase')
    return recipe


def normal_form(p, ce, op, rank):
    recipe = lower_exact(p, ce, op)
    need(recipe['rank'] == rank, 'Physical rank equals promised helper width')
    left = p.monomial(ce, recipe['left'], 9)
    right = p.monomial(ce, recipe['right'], 9)
    pre = right.adjoint(); post = left.adjoint()
    pre_recipe = lower_exact(p, ce, pre); post_recipe = lower_exact(p, ce, post)
    need(pre_recipe['rank'] == post_recipe['rank'] == 0, 'Free boundary wrappers')
    wrapped = pre.then(op).then(post); target = ce.fourier(9, range(rank))
    need(wrapped.tab == target.tab and wrapped.zero_state() == target.zero_state(), 'Helper boundary is exact standard Fourier including phase')
    return dict(rank=rank, factorization=recipe, outer_pre_monomial=pre_recipe['left'],
                outer_post_monomial=post_recipe['left'], exact_tableau_and_global_phase=True)


def helper_normal_forms(p, ce, canonical, cache=None):
    """Certify every helper, with explicit inherited and fresh outer wrappers.

    Bare residual is F_end F_start^-1. The retained residual_adapter convention
    already maps it to C_width in forward, and conjugate(C_width) in backward.
    New outer normalizers below act at the WHOLE invocation boundaries. They
    require no change to internal frames, helper reads, or scalar event order.
    """
    cache = {} if cache is None else cache
    rows = []; widths = Counter()
    for role in range(224, 632):
        start, end = canonical['start'][role], canonical['final'][role]
        A, B = canonical['frames'][start], canonical['frames'][end]
        rank = len(B)-len(A)
        need(0 < rank <= 9, 'Positive productive helper width')
        key = (tuple(A), tuple(B))
        if key not in cache:
            physical = ce.canonical_frame(9, A).adjoint().then(ce.canonical_frame(9, B))
            inherited = lower_exact(p, ce, physical)
            need(inherited['rank'] == rank, 'Native helper residual rank')
            lm = p.monomial(ce, inherited['left'], 9)
            rm = p.monomial(ce, inherited['right'], 9)
            directions = {}
            for backward in (False, True):
                name = 'backward' if backward else 'forward'
                op = p.conjugate(ce, physical) if backward else physical
                l = p.conjugate(ce, lm) if backward else lm
                r = p.conjugate(ce, rm) if backward else rm
                native = r.adjoint().then(op).then(l.adjoint())
                target = ce.fourier(9, range(rank))
                if backward:
                    target = p.conjugate(ce, target)
                need(native.tab == target.tab and native.zero_state() == target.zero_state(), 'Inherited oriented native helper boundary')
                directions[name] = dict(bare_residual_normal_form=normal_form(p, ce, op, rank),
                                        inherited_native_target='conjugate(C_width)' if backward else 'C_width',
                                        existing_native_boundary_normal_form=normal_form(p, ce, native, rank))
            cache[key] = dict(start_basis=A, end_basis=B, inherited_forward_factorization=inherited, directions=directions)
        rows.append(dict(role=role, start_frame=start, end_frame=end, width=rank, certificate=cache[key]))
        widths[rank] += 1
    expected = {5: 28, 6: 18, 7: 56, 8: 93, 9: 213} if widths[7] == 56 else {5: 28, 6: 18, 7: 57, 8: 92, 9: 213}
    need(dict(widths) == expected, 'Exact all-helper productive width profile')
    return dict(status='PASS_ALL_408_HELPERS_BOTH_ORIENTATIONS_WITH_ABSOLUTE_PHASE',
                count=len(rows), widths=dict(sorted(widths.items())), total_width=sum(k*x for k, x in widths.items()),
                recipes=rows, unique_frame_pairs=len({(r['start_frame'], r['end_frame']) for r in rows}),
                scope='Native ideal helper block and free boundary adapters only; productive outer ownership and full recursive bill are separate obligations.')


def h_child_recipes(p, ce, canonical, words):
    result = {}
    for direction, program in words.items():
        rows = []
        for i, e in enumerate(program):
            if e[0] != 'center':
                continue
            _, role, old, new, rank = e
            # These corrections occur OUTSIDE the inherited data adapters.
            # The physical endpoint references are the original port gates,
            # not the monomial-equivalent canonical representatives. Using a
            # bare canonical_frame here would leave an uncharged/missing phase
            # adapter on the scalar contact despite a correct logical replay.
            k = len(rows); port_index = SELECTED[k]; q = canonical['ports'][port_index]
            if direction == 'forward':
                source = ce.fourier(9)
                target = ce.cgate(9, q).adjoint().then(ce.fourier(9))
            else:
                source = ce.ident(9)
                target = p.conjugate(ce, ce.cgate(9, q))
            op = source.adjoint().then(target)
            recipe = lower_exact(p, ce, op)
            need(recipe['rank'] == rank == 1, 'Completion child rank one')
            direct = ce.cgate(9, q).adjoint()
            need(op.tab == direct.tab and op.zero_state() == direct.zero_state(), 'External completion is exact inverse port gate')
            rows.append(dict(event=i, selected_port=port_index, port_vector=q,
                             source_frame=old, target_frame=new, recipe=recipe,
                             physical_reference='original external endpoint gauge; inherited adapters already outside the contact',
                             exact_inverse_port_gate_including_phase=True))
        need(len(rows) == 8, 'Exactly eight completion children')
        result[direction] = rows
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=HERE/'fresh-certificates')
    ap.add_argument('--stage', choices=('helpers', 'H', 'logger', 'all'), default='all')
    ap.add_argument('--tags', nargs='+', choices=TAGS, default=list(TAGS))
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    p, v, ce, receipt, inherited = authenticated()
    geo = geometry(v.PACKET)
    run = dict(schema='fresh-native-H112-reconstruction/1', reconstructed_after_loss=True,
               source_sha256=digest(Path(__file__)), predecessor_receipt_sha256=RECEIPT_SHA,
               predecessor_generator_sha256=P_SHA, independent_interpreter_sha256=p.CHECKER_SHA,
               clifford_compiler_sha256=CE_SHA, packet_sha256=digest(v.PACKET),
               geometry=dict(selected=list(SELECTED), ordinary_count=104, L_nonzeros=416, H_squared_identity=True,
                             H_not_symmetric=True, divisions_by_odd_numbers=0),
               environment=dict(python=sys.version, platform=platform.platform()),
               no_new_kappa_claimed=True, providers={})
    phase_cache = {}
    for tag in args.tags:
        started = time.monotonic()
        c = read(BASE/(tag+'-CANONICAL.json.gz')); word = read(BASE/(tag+'-NATIVE-WORD.json.gz'))
        row = dict(predecessor_artifacts=receipt['providers'][tag]['artifacts'])
        if args.stage in ('helpers', 'all'):
            helpers = helper_normal_forms(p, ce, c, phase_cache)
            path = args.out/(tag+'-HELPER-BOUNDARIES.json.gz')
            row['helper_boundaries'] = dict(artifact=path.name, sha256=save(path, helpers), widths=helpers['widths'],
                                            total_width=helpers['total_width'], count=408)
            print('PASS helpers', tag, helpers['widths'], flush=True)
        if args.stage in ('H', 'all'):
            hw = make_h_word(c, word, geo); expected_profile = Counter({int(k): x for k, x in c['local_profile'].items()}); expected_profile[1] += 8
            checks = {d: replay_extended(v, hw[d], c, geo, d == 'backward', expected_profile=expected_profile) for d in ('forward', 'backward')}
            phases = h_child_recipes(p, ce, c, hw)
            baseline_scalar = receipt['providers'][tag]['checks']['forward']['independent_literal_replay']['conservative_real_scalar_primitive_allowance']
            need(all(check['real_scalar_allowance']-baseline_scalar == 4336 for check in checks.values()), 'Exact 4336 scalar increment')
            broken = deepcopy(hw['forward'])
            omitted = next(i for i, e in enumerate(broken) if e[0] == 'scalar' and e[1][:2] == ['add', ['L', 112+SELECTED[0]]] and e[1][2] == ['C', 0])
            broken.pop(omitted)
            negative = replay_extended(v, broken, c, geo, allow_mismatch=True)
            need(not negative['exact_endpoint'], 'Missing completion negative control rejected')
            path = args.out/(tag+'-H112-NATIVE.json.gz')
            row['H112'] = dict(artifact=path.name, sha256=save(path, hw), checks=checks, new_child_recipes=phases,
                               increment=dict(profile={'1': 8}, real_scalar_allowance=4336, owned_C_fields=1, persistent_fields=0),
                               omitted_completion_negative_control=negative['mismatch_examples'])
            print('PASS H112', tag, '8 H1 + 4336; both directions', flush=True)
        if args.stage in ('logger', 'all'):
            lw = make_logger_word(c, word, geo)
            profile = Counter({int(k): x for k, x in c['local_profile'].items()}); profile[9] += 8
            check = replay_extended(v, lw, c, geo, endpoint='logger', cache_count=8, expected_profile=profile)
            baseline_scalar = receipt['providers'][tag]['checks']['forward']['independent_literal_replay']['conservative_real_scalar_primitive_allowance']
            need(check['real_scalar_allowance']-baseline_scalar == 4224, 'Exact 4224 scalar logger increment')
            op = ce.canonical_frame(9, c['frames'][0]).adjoint().then(ce.canonical_frame(9, c['frames'][1]))
            recipe = lower_exact(p, ce, op); need(recipe['rank'] == 9, 'Logger paid rank nine')
            path = args.out/(tag+'-FORWARD-LOGGER.json.gz')
            row['logger'] = dict(artifact=path.name, sha256=save(path, lw), check=check, cache_child_recipe=recipe,
                                 increment=dict(profile={'9': 8}, real_scalar_allowance=4224, owned_C_fields=0, arbitrary_cache_fields=8),
                                 cache_restored=False, productive_cache_credit_claimed=False)
            print('PASS logger', tag, '8 H9 + 4224', flush=True)
        row['seconds'] = time.monotonic()-started
        run['providers'][tag] = row
        save(args.out/('RESULT-'+args.stage+'.json'), run)
    run['status'] = 'PASS_FRESH_RECONSTRUCTION_REQUESTED_STAGES'
    save(args.out/('RESULT-'+args.stage+'.json'), run)


if __name__ == '__main__':
    main()
