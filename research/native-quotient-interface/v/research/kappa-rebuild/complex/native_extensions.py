#!/usr/bin/env python3
"""Native embedded query logger and common-frame H conjugation contacts.

Apache-2.0. Substantial OpenAI assistance. These are fresh constructions with
explicit arbitrary-input endpoints. An embedded cache output is not claimed
as an independent clean helper output until a whole caller erases its defect.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import argparse
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rebuild_native as N
import power_two_balance as B

B_SHA = '76929bb3887911ccf100c4593574b8a1c82ee64e96f939a8aca196869438b424'


def common_frame_h(geo, offset, frame):
    """H = diag(I,-I) S_L S_-K S_L, with all shear ADDs having coefficient ±1.

    Balancing only the eight selected coordinates avoids scaling104 ordinary
    coordinates. No private field and no recursive transport are introduced.
    Precondition: ALL112 physical fields share the stated actual frame gauge.
    """
    A = geo['selected']
    out = [['phase', 'fresh_common_frame_H']]
    def scale(n, d):
        out.extend(N.scalar(['scale', ['L', offset+a], n, d], frame) for a in A)
    def left():
        for k, a in enumerate(A):
            for u, value in sorted(geo['L'][k].items()):
                coefficient = 2*value
                N.need(abs(coefficient) == 1, 'Balanced unit L coefficients')
                out.append(N.scalar(['add', ['L', offset+a], ['L', offset+u], int(coefficient), 1], frame))
    scale(2, 1); left(); scale(1, 4)
    for k, a in enumerate(A):
        for u, value in sorted(geo['L'][k].items()):
            coefficient = -2*value
            out.append(N.scalar(['add', ['L', offset+u], ['L', offset+a], int(coefficient), 1], frame))
    scale(4, 1); left(); scale(-1, 2)
    N.need(B.scalar_sum(out) == 10096, 'Exact common-frame H scalar allowance')
    return out


def embedded_cache_roles(canonical):
    roles = [i for i in range(224, 632) if canonical['start'][i] == 0 and canonical['final'][i] == 1]
    N.need(len(roles) == 213, '213 genuinely cold, full-ended native helper roles')
    return roles[:8]


def embedded_logger_suffix(canonical, geo, roles=None):
    roles = embedded_cache_roles(canonical) if roles is None else list(roles)
    N.need(len(roles) == len(set(roles)) == 8, 'Eight distinct embedded caches')
    N.need(all(224 <= i < 632 and canonical['start'][i] == 0 and canonical['final'][i] == 1 for i in roles),
           'Embedded logger only uses cold full-ended physical helper references')
    out = [['phase', 'fresh_embedded_dirty_logger']]
    for k, a in enumerate(geo['selected']):
        r = roles[k]
        out += [N.scalar(['scale', ['L', r], 2, 1], 1),
                N.scalar(['add', ['L', r], ['L', a], 2, 1], 1)]
        out += [N.scalar(['add', ['L', r], ['L', u], int(2*q), 1], 1)
                for u, q in sorted(geo['L'][k].items())]
        out.append(N.scalar(['scale', ['L', r], 1, 2], 1))
    N.need(B.scalar_sum(out) == 3440, 'Embedded logger exact scalar bill')
    return out


def make_embedded_logger(canonical, base_word, geo):
    word = B.make_balanced_h(canonical, base_word, geo)['forward']
    return word+embedded_logger_suffix(canonical, geo)


def make_wrapped_h(canonical, base_word, geo):
    words = B.make_balanced_h(canonical, base_word, geo)
    return {direction: common_frame_h(geo, 112, 0)+word+common_frame_h(geo, 0, 1)
            for direction, word in words.items()}


def literal_replay(v, c, program, backward=False):
    """Second literal evaluator for new endpoints; all632 inputs arbitrary.

    This checker has no endpoint-specific shortcut. It applies every scalar
    and free-warp event and checks each contact's frame before comparing rows.
    """
    rows = {('L', i): v.identity(('L', i)) for i in range(632)}
    rows['C', 0] = v.identity(('C', 0))
    current = {('L', i): f for i, f in enumerate(c['start'])}; current['C', 0] = None
    spaces = [v.span(frame) for frame in c['frames']]
    profile = Counter(); cost = 0; max_l1 = Q(1); witness = None; max_denominator = 1
    for j, event in enumerate(program):
        kind = event[0]; touched = None
        if kind == 'scalar':
            g, frame = event[1:]; target = tuple(g[1]); touched = target
            cost += N.primitive_allowance(g)
            if g[0] == 'clear':
                N.need(target == ('C', 0), 'Only owned C0 can be cleared')
                rows[target] = {}; current[target] = frame
            else:
                N.need(current[target] == frame, 'Exact scalar target frame')
                if g[0] in ('add', 'copy'):
                    source = tuple(g[2]); N.need(current[source] == frame, 'Exact scalar source frame')
                    if g[0] == 'copy':
                        N.need(target == ('C', 0), 'Only owned field overwritten by copy')
                        rows[target] = dict(rows[source])
                    else:
                        N.need(target != source, 'Distinct reversible ADD arguments')
                        v.add(rows[target], rows[source], Q(g[3], g[4]))
                else:
                    N.need(g[0] == 'scale', 'Known scalar action')
                    q = Q(g[2], g[3]); rows[target] = {i: q*x for i, x in rows[target].items()}
        elif kind == 'warp':
            _, r, op, old, new = event; target = tuple(r); touched = target
            N.need(current[target] == old, 'Warp input frame')
            rows[target] = v.warp(rows[target], op, backward); current[target] = new
        elif kind in ('climb', 'center'):
            if kind == 'climb':
                _, part, i, old, new, rank = event; target = ('L', i)
                N.need(spaces[old] < spaces[new], 'Ascending borrowed climb')
            else:
                _, i, old, new, rank = event; target = ('C', i)
                N.need(spaces[old] < spaces[new] or spaces[new] < spaces[old], 'Nested center transport')
            N.need(current[target] == old and rank == abs(len(c['frames'][new])-len(c['frames'][old])), 'Paid rank and source frame')
            current[target] = new; profile[rank] += 1
        else:
            N.need(kind in ('phase', 'adapter', 'residual_adapter'), 'Known inert native marker')
        if touched is not None:
            norm = sum(map(abs, rows[touched].values()), Q(0))
            if norm > max_l1:
                max_l1 = norm; witness = dict(event=j, role=list(touched))
            max_denominator = max(max_denominator, max((x.denominator for x in rows[touched].values()), default=1))
    N.need([current['L', i] for i in range(632)] == c['final'], 'Final native frames')
    N.need(not rows['C', 0], 'Owned C0 cleared at return')
    return rows, dict(independent_persistent_columns=632, independent_owned_entry_columns=1,
                      scalar_frames_checked=True, arbitrary_owned_C0_cleared=True,
                      paid_profile=dict(sorted(profile.items())), paid_rank_mass=sum(k*x for k, x in profile.items()),
                      real_scalar_allowance=cost, max_formal_prefix_l1=str(max_l1), max_denominator=max_denominator,
                      l1_witness=witness)


def check_rows(v, rows, geo, kind, backward=False, cache_roles=()):
    mismatch = []
    for r in range(632):
        actual = rows['L', r]
        if kind == 'wrapped' and r < 224:
            port = r % 112; wanted = {}
            for j, q in geo['H'][port].items():
                v.add(wanted, v.identity(('L', (112 if r >= 112 else 0)+j)), q)
                if backward and r < 112:
                    v.add(wanted, v.identity(('L', 112+j)), -q)
                if not backward and r >= 112:
                    v.add(wanted, v.identity(('L', j)), q)
        else:
            wanted = v.identity(('L', r))
            if 112 <= r < 224:
                for j, q in geo['H'][r-112].items():
                    v.add(wanted, v.identity(('L', j)), q)
            if r in cache_roles:
                k = list(cache_roles).index(r)
                for j, q in {geo['selected'][k]: Q(1), **geo['L'][k]}.items():
                    v.add(wanted, v.identity(('L', j)), q)
        if actual != wanted:
            mismatch.append(r)
    N.need(not mismatch, 'Fresh exact endpoint mismatch '+repr(mismatch[:5]))


def check_scalar_h(v, geo):
    """Independent112-column execution without native body or Clifford data."""
    rows = {i: {i: Q(1)} for i in range(112)}
    program = common_frame_h(geo, 0, 0)
    for event in program:
        if event[0] != 'scalar':
            continue
        g = event[1]; target = g[1][1]
        if g[0] == 'scale':
            q = Q(g[2], g[3]); rows[target] = {i: q*x for i, x in rows[target].items()}
        else:
            v.add(rows[target], rows[g[2][1]], Q(g[3], g[4]))
    N.need(all(rows[i] == geo['H'][i] for i in range(112)), 'Three balanced shears exactly equal H')
    return dict(all_columns=112, real_scalar_allowance=B.scalar_sum(program),
                additions=sum(e[0] == 'scalar' and e[1][0] == 'add' for e in program),
                unit_add_coefficients=True, owned_fields=0, new_recursive_children=0,
                required_physical_precondition='All112 fields occupy one actual common frame reference.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=HERE/'extension-certificates')
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    N.need(N.digest(HERE/'rebuild_native.py') == B.N_SHA and N.digest(HERE/'power_two_balance.py') == B_SHA,
           'Authenticated fresh prerequisite sources')
    p, v, ce, receipt, inherited = N.authenticated(); geo = N.geometry(v.PACKET)
    result = dict(schema='fresh-native-helper-log-and-common-frame-conjugation/1',
                  source_sha256=N.digest(Path(__file__)), reconstruction_source_sha256=B.N_SHA,
                  balance_source_sha256=B_SHA, scalar_H=check_scalar_h(v, geo), providers={}, no_new_kappa_claimed=True)
    for tag in N.TAGS:
        c = N.read(N.BASE/(tag+'-CANONICAL.json.gz')); word = N.read(N.BASE/(tag+'-NATIVE-WORD.json.gz'))
        base_scalar = B.scalar_sum(word['forward'])
        roles = embedded_cache_roles(c); embedded = make_embedded_logger(c, word, geo)
        rows, embedded_check = literal_replay(v, c, embedded)
        check_rows(v, rows, geo, 'embedded', cache_roles=roles)
        N.need(embedded_check['real_scalar_allowance'] == base_scalar+3504+3440, 'Embedded complete scalar invoice')
        wrapped = make_wrapped_h(c, word, geo); wrapped_checks = {}
        for direction, program in wrapped.items():
            back = direction == 'backward'
            rows, checked = literal_replay(v, c, program, back)
            check_rows(v, rows, geo, 'wrapped', back)
            N.need(checked['real_scalar_allowance'] == base_scalar+3504+2*10096, 'Wrapped H complete scalar invoice')
            wrapped_checks[direction] = checked
        ep = args.out/(tag+'-EMBEDDED-LOGGER.json.gz'); wp = args.out/(tag+'-SCALAR-WRAPPED-H.json.gz')
        result['providers'][tag] = dict(
            embedded_logger=dict(artifact=ep.name, sha256=N.save(ep, embedded), check=embedded_check,
                                 cache_roles=roles, exactly_400_other_helpers_restored=True,
                                 cache_output='d_k + X_A[k] + L[k] X_U', extra_children=0,
                                 extra_persistent_fields=0, extra_owned_fields=0, extra_scalar_allowance=3440,
                                 independent_clean_output_credit_for_eight_caches=False),
            scalar_wrapped_H=dict(artifact=wp.name, sha256=N.save(wp, wrapped), checks=wrapped_checks,
                                  endpoint='diag(H,H) times the corresponding identity shear in local logical coordinates',
                                  new_recursive_children_beyond_H=0, extra_scalar_allowance=20192,
                                  all_408_helpers_restored=True,
                                  outer_intercall_frame_identification_certified=False))
        N.save(args.out/'RESULT.json', result)
        print('PASS extensions', tag, 'embedded0 extra children; wrapped H20192 extra scalars', flush=True)
    result['status'] = 'PASS_LOCAL_NATIVE_ENDPOINTS_WITH_EXPLICIT_OUTER_FRAME_OBLIGATION'
    N.save(args.out/'RESULT.json', result)


if __name__ == '__main__':
    main()
