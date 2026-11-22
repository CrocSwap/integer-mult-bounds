# SPDX-License-Identifier: Apache-2.0
# Seed39 adaptation by Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
# Original PR2339/PR2226/PR2269 attribution below is retained.
# CHANGES: explicit post-wrapper lifted-target compensation; nested COPY profile.
# Original source remains immutable under anticipatory-stage-evidence/vendor/pr2339.
#!/usr/bin/env python3
"""Exact free-operator replay of an anticipatory dirty-borrowing witness (function form).

This is the replay of PR2226 "anticipatory dirty borrowing" (Cinna Davis, @1337isnot1337,
with OpenAI Codex assistance; research/anticipatory-dirty-borrowing/replay.py, Apache-2.0),
as vendored byte-identically by PR2269 (Jeremy Kothe, research/gmx-t74-borrow43/new/code/
borrow/vendor/pr2226_replay.py).  The semantics are unchanged.  The only differences are:

  * it is a function returning a dict instead of a CLI writing a file;
  * the PR2226-specific assertion ``len(pairs)==80 and sum(low)==32`` is replaced by
    caller-supplied expected counts (PR2269's T74 witnesses carry 43 pairs);
  * when ``diagnose=True`` the Y-row residuals (actual minus Y+X) are returned instead of
    raising, so that a construction script can read off the late target response of a
    nominated alias.  The verification mode (``diagnose=False``) raises exactly as PR2226.

Every low-pair condition of PR2226 is enforced verbatim:
  - initial corrections: target in Y, source active, not in Y, source entrance frame of
    dimension zero, operator words in range, dyadic coefficient;
  - low lender is exactly its restored initial input at the handoff;
  - retirement_B_event < handoff_B; handoff_paid_rank equals the frame-dimension gap;
  - deleted prefix indices / early prefix rewrites are applied only for low pairs;
  - every climb is nested (frame chronology), Y'=Y+X over the free operator algebra,
    full inverse cleanup with private zero buffers restores every non-target input, and the
    omitted-inverse-warp negative control must fail.

Adaptation prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.
Credits: PR2226 (Cinna Davis), PR2269 (Jeremy Kothe), PR2260 (Dugongue).
"""
from collections import Counter
from fractions import Fraction as Q


def span(basis):
    s = {0}
    for x in basis:
        s |= {t ^ x for t in s.copy()}
    return frozenset(s)


def incident(e):
    return e[1:3] if e[0] == 'add' else e[1:2]


def add(dst, src, c):
    for key, value in list(src.items()):
        z = dst.get(key, Q(0)) + c * value
        if z:
            dst[key] = z
        elif key in dst:
            del dst[key]


def warp(row, op):
    out = {}
    for (var, word), value in row.items():
        word = word[1:] if word and word[0] == -op else (op,) + word
        out[var, word] = value
    return out


def frame_basis(F):
    b = {}
    for x in F:
        while x:
            j = x.bit_length()
            if j not in b:
                b[j] = x
                break
            x ^= b[j]
    return [b[j] for j in sorted(b, reverse=True)]


class ReplayError(ValueError):
    pass


def replay(w, blocks, inv, *, recover_cold=True, diagnose=False, expect_pairs=None,
           expect_low=None, stop_after_B=False, trace_handoff=None, probe=None):
    pairs = inv['pairs']
    if expect_pairs is not None:
        assert len(pairs) == expect_pairs, (len(pairs), expect_pairs)
    if expect_low is not None:
        assert sum(x['low'] for x in pairs) == expect_low
    v = w['v']; n = 2 * v + w['R']; full = span([1 << i for i in range(w['h'])])
    frames = list(map(span, w['frames']))
    removed = {x['register'] for x in pairs}
    assert len(removed) == len(pairs), 'duplicate removed register'
    active = [r for r in range(n) if r not in removed]
    val = {r: {(r, ()): Q(1)} for r in active}
    cur = {r: frames[w['start'][r]] for r in active}
    anticipation = inv['initial_corrections']
    for term in anticipation:
        target = term['target']; source = term['source']; word = tuple(term['operator_word'])
        coefficient = Q(term['coefficient'])
        assert v <= target < 2 * v and source in active and not (v <= source < 2 * v)
        assert len(w['frames'][w['start'][source]]) == 0
        assert all(1 <= abs(op) <= len(pairs) for op in word)
        assert coefficient.denominator & (coefficient.denominator - 1) == 0
        add(val[target], {(source, word): Q(1)}, coefficient)
    mapping = {}; profile = Counter(); reverse = []; warps = []
    lender_check = []

    def resolve(r):
        return mapping.get(r, r)

    def climb(r, f):
        if not cur[r] <= f:
            raise ReplayError(('nonnested climb', r, len(cur[r]), len(f)))
        d = (len(f).bit_length() - 1) - (len(cur[r]).bit_length() - 1)
        if d:
            profile[d] += 1
        cur[r] = f

    def scalar(e, framed=True, record=True):
        rs = [resolve(r) for r in incident(e)]
        if any(r not in val for r in rs):
            raise ReplayError(('unallocated borrowed field', e))
        if framed:
            for r in rs:
                climb(r, frames[e[-1]])
        if e[0] == 'add':
            c = Q(e[3], e[4]); add(val[rs[0]], val[rs[1]], c)
            if record and not (v <= rs[0] < 2 * v):
                reverse.append(('add', rs[0], rs[1], c))
        else:
            c = Q(e[2], e[3]); val[rs[0]] = {k: c * x for k, x in val[rs[0]].items()}
            if record and not (v <= rs[0] < 2 * v):
                reverse.append(('scale', rs[0], c))

    original_target_levels = {r: w['start'][r] for r in range(v, 2 * v)}
    for e in w['precondition'] + w['compensation']:
        for r in incident(e):
            if v <= r < 2 * v:
                original_target_levels[r] = e[-1]
        if e[0] == 'add' and e[2] in removed:
            continue
        scalar(e, record=False)
    # Seed39 extension: paid target climbs and explicit rank-zero compensation
    # after wrappers, before A. The flag/G physical identity is checked separately.
    for target, fid in inv.get('lifted_target_frames', {}).items():
        target = int(target)
        assert v <= target < 2 * v
        climb(target, frames[fid])
        original_target_levels[target] = fid
    for term in inv.get('post_wrapper_corrections', []):
        t, s = term['target'], term['source']
        op = term['operator']
        assert v <= t < 2 * v and s in active and not v <= s < 2 * v
        assert val[s] == {(s, ()): Q(1)}
        assert cur[s] == frames[w['start'][s]]
        assert len(cur[s]) == len(cur[t])
        assert pairs[op - 1]['borrow_from'] == s
        coefficient = Q(term['coefficient'])
        assert coefficient.denominator & (coefficient.denominator - 1) == 0
        add(val[t], warp(val[s], op), coefficient)
    for e in w['A']:
        scalar(e)
    for r, f in original_target_levels.items():
        climb(r, frames[f])
    for r, f in zip(w['centers'], w['center_frames']):
        assert cur[r] == frames[f]
        # Seed39: centre COPY may serve nested target levels. Count its entire
        # descent, including the original remaining frame-zero targets.
        served = {frames[original_target_levels[e[1]]] for e in w['cut'] if e[2] == r}
        U = frames[f]
        for T in sorted(served, key=lambda F: -len(F)):
            assert T <= U, ('nonnested COPY target levels', r)
            rank = (len(U).bit_length() - len(T).bit_length())
            if rank:
                profile[rank] += 1
            U = T
    for e in w['cut']:
        scalar(e, framed=False, record=False)
    deferred = {}; skip = set()
    for b in blocks:
        ss = set(b['helpers']); part = []
        for i in range(b['first_correction'], b['first_input']):
            e = w['B'][i]
            if set(incident(e)) <= ss:
                part.append(e); skip.add(i)
        deferred[b['first_input']] = part
    starts = {}
    for i, x in enumerate(pairs):
        starts.setdefault(x.get('handoff_B', x['deadline']), []).append((i + 1, x))
    removed_early_echoes = {i for x in pairs if x['low']
                            for i in x.get('deleted_prefix_indices', x['deleted_echo_indices'])}
    early_rewrites = {}
    for x in pairs:
        if x['low']:
            for i, gates in x.get('early_prefix_rewrites', {}).items():
                assert int(i) not in early_rewrites, ('two rewrites at one index', i)
                early_rewrites[int(i)] = gates
    early_tail = {}
    for e in inv.get('early_tail_events', []):
        early_tail.setdefault(e['before_B'], []).append(e['gate'])
    for i, e in enumerate(w['B']):
        for t in early_tail.get(i, []):
            scalar(t)
        if probe is not None and i in probe:
            probe[i] = {'pristine': {r for r in active if val[r] == {(r, ()): Q(1)}},
                        'cur': {r: frame_basis(cur[r]) for r in active}}
        if i in starts:
            for op, x in starts[i]:
                old = x['borrow_from']; new = x['register']
                assert x['retirement_B_event'] < i
                if x['low']:
                    ok = val[old] == {(old, ()): Q(1)}
                    lender_check.append((op, old, ok))
                    if not ok and not diagnose:
                        raise ReplayError(('low lender is not its restored initial input', op, old))
                if trace_handoff is not None:
                    trace_handoff.append((op, old, new, i, dict(val[old]), frame_basis(cur[old])))
                E_basis = x.get('handoff_basis', x['common_basis'][:x['retirement_dimension']])
                E = span(E_basis)
                paid = abs(len(E_basis) - (len(cur[old]).bit_length() - 1))
                assert paid == x.get('handoff_paid_rank', 0), ('paid handoff', op, paid)
                if paid:
                    profile[paid] += 1
                val[old] = warp(val[old], op); reverse.append(('warp', old, op)); cur[old] = E
                mapping[new] = old
                warps.append({'operator': op, 'borrow_from': old, 'removed': new,
                              'from_basis': w['frames'][x['retirement_frame']] if 'retirement_frame' in x else None,
                              'to_basis': E_basis, 'physical_handoff_rank': paid})
                assert not x.get('handoff_echo_coefficients')
        for d in deferred.get(i, []):
            scalar(d)
        for d in early_rewrites.get(i, []):
            scalar(d)
        if i not in skip and i not in removed_early_echoes:
            scalar(e)
    for t in early_tail.get(len(w['B']), []):
        scalar(t)
    for r in range(v, 2 * v):
        climb(r, frames[w['final'][r]])
    residual = {}
    for r in range(v, 2 * v):
        expected = {(r, ()): Q(1), (r - v, ()): Q(1)}
        if val[r] != expected:
            d = dict(val[r]); add(d, expected, Q(-1)); residual[r] = d
    if residual and not diagnose:
        raise ReplayError(('output map failed in exact free operator algebra', sorted(residual)[:12]))
    if diagnose:
        return {'residual': residual, 'lender_check': lender_check, 'profile': dict(profile),
                'val': val, 'cur': cur, 'active': active, 'mapping': mapping}
    # ---- cold restoration + full inverse cleanup (verbatim PR2226 semantics) ----
    cold = [r for r in active if not (v <= r < 2 * v) and len(w['frames'][w['final'][r]]) < w['h']]
    prime = 65521; modular_cache = {}; cold_clearable = []
    for c in cold:
        V = frames[w['final'][c]]
        pool = tuple(r for r in active if not (v <= r < 2 * v) and cur[r] <= V <= frames[w['final'][r]])
        if pool not in modular_cache:
            piv = {}
            for r in pool:
                x = {k: (q.numerator * pow(q.denominator, -1, prime)) % prime for k, q in val[r].items()}
                while x:
                    j = min(x)
                    if j not in piv:
                        z = pow(x[j], -1, prime); piv[j] = {k: t * z % prime for k, t in x.items()}; break
                    z = x[j]
                    for k, t in piv[j].items():
                        y = (x.get(k, 0) - z * t) % prime
                        if y:
                            x[k] = y
                        elif k in x:
                            del x[k]
            modular_cache[pool] = piv
        x = {(c, ()): 1}; piv = modular_cache[pool]
        while x:
            j = min(x)
            if j not in piv:
                break
            z = x[j]
            for k, t in piv[j].items():
                y = (x.get(k, 0) - z * t) % prime
                if y:
                    x[k] = y
                elif k in x:
                    del x[k]
        if not x:
            dependents = [r for r in active if not (v <= r < 2 * v) and any(var == c for var, word in val[r])]
            if all(cur[r] <= V and all(not word for var, word in val[r] if var == c) for r in dependents):
                cold_clearable.append(c)
    restored = []; cold_witnesses = []

    def exact_combination(pool, goal):
        piv = {}
        for r in pool:
            x = dict(val[r]); code = {r: Q(1)}
            while x:
                j = min(x)
                if j not in piv:
                    z = x[j]; piv[j] = ({k: t / z for k, t in x.items()}, {k: t / z for k, t in code.items()}); break
                row, coeff = piv[j]; z = x[j]; add(x, row, -z); add(code, coeff, -z)
        x = dict(goal); code = {}
        while x:
            j = min(x)
            if j not in piv:
                return None
            row, coeff = piv[j]; z = x[j]; add(x, row, -z); add(code, coeff, z)
        return code

    def dyadic(q):
        return q.denominator & (q.denominator - 1) == 0

    def unit(q):
        return q and dyadic(q) and abs(q.numerator) & (abs(q.numerator) - 1) == 0

    def cleanup_add(d, s, c, V):
        climb(d, V); climb(s, V); add(val[d], val[s], c); reverse.append(('add', d, s, c))

    if recover_cold:
        for c in sorted(cold_clearable, key=lambda r: (len(frames[w['final'][r]]), r)):
            V = frames[w['final'][c]]
            pool = [r for r in active if not (v <= r < 2 * v) and r not in restored and cur[r] <= V]
            solution = exact_combination(pool, {(c, ()): Q(1)})
            if solution is None or not all(dyadic(z) for z in solution.values()):
                continue
            pivot = c if unit(solution.get(c, Q(0))) else next((r for r, z in solution.items() if unit(z)), None)
            if pivot is None:
                continue
            for r in set(solution) | {c}:
                climb(r, V)
            factor = solution[pivot]
            if factor != 1:
                val[pivot] = {k: factor * z for k, z in val[pivot].items()}; reverse.append(('scale', pivot, factor))
            for r, z in solution.items():
                if r != pivot:
                    cleanup_add(pivot, r, z, V)
            if pivot != c:
                val[c], val[pivot] = val[pivot], val[c]; reverse.append(('swap', c, pivot))
            assert val[c] == {(c, ()): Q(1)}
            for r in active:
                if v <= r < 2 * v or r == c:
                    continue
                assert all(not word for var, word in val[r] if var == c)
                z = val[r].get((c, ()), Q(0))
                if z:
                    cleanup_add(r, c, -z, V)
            assert all(not any(var == c for var, word in val[r]) for r in active if not (v <= r < 2 * v) and r != c)
            restored.append(c)
            cold_witnesses.append({'register': c, 'frame': w['final'][c],
                                   'preparation': {str(r): str(z) for r, z in solution.items()}})
    for r in active:
        if not (v <= r < 2 * v) and r not in restored:
            climb(r, full)
    work = {r: ({} if r in restored else dict(row)) for r, row in val.items()}
    negative = {r: dict(work[r]) for r in active if not (v <= r < 2 * v)}
    for e in reversed(reverse):
        if e[0] == 'add':
            _, d, s, c = e; add(work[d], work[s], -c); add(negative[d], negative[s], -c)
        elif e[0] == 'scale':
            _, d, c = e; work[d] = {k: x / c for k, x in work[d].items()}
            negative[d] = {k: x / c for k, x in negative[d].items()}
        elif e[0] == 'swap':
            _, d, s = e; work[d], work[s] = work[s], work[d]; negative[d], negative[s] = negative[s], negative[d]
        else:
            _, d, op = e; work[d] = warp(work[d], -op)
    for r in active:
        if not (v <= r < 2 * v) and work[r] != ({} if r in restored else {(r, ()): Q(1)}):
            raise ReplayError(('cleanup failed', r))
    rejected = [r for r, row in negative.items() if row != ({} if r in restored else {(r, ()): Q(1)})]
    if warps and not rejected:
        raise ReplayError('missing inverse warp negative control did not fail')
    mass = sum(r * c for r, c in profile.items())
    return {'status': 'PASS_EXACT_FREE_OPERATOR_BORROWING_REPLAY', 'original_registers': n,
            'remaining_registers': len(active), 'removed_helper_registers': len(removed),
            'independent_input_columns': len(active), 'symbolic_warps': warps, 'target_map': 'Y+=X',
            'omitted_inverse_warps_rejected_registers': len(rejected),
            'zero_FULL_cleanup_buffers': len(restored), 'exact_cold_restoration': cold_witnesses,
            'lender_check': lender_check,
            'local_profile': dict(sorted(profile.items())), 'local_mass': mass}
