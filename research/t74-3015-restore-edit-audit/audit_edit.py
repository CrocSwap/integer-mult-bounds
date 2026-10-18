# SPDX-License-Identifier: Apache-2.0
"""Scope A: PR #3015's declared restore edit R1 as a literal change of PR #2979's words, with code that does not
import or run either PR.

own_diff()        the candidate word equals the parent word outside the sections 'restore', 'report' and 'cleanup'
                  (rule edit.sections); the restore section differs by exactly the declared hunk: parent[start:stop]
                  is the declared old block, candidate[start:start+len(new)] the declared new block, the lengths
                  agree, and the minimal common-prefix/suffix hunk lies inside the declared one, i.e. both words
                  agree before and after it (edit.hunk).
net_operator()    the new block equals the old block as a formal operator on the registers it touches (frames ignored,
                  exact Fractions; edit.net_operator).
own_chain()       a fresh implementation of the lineage's monotone frame chain (precondition and compensation at frame
                  0 on targets, A and B gates climb their registers to the gate frame, A and B warps need the lender at
                  U and set E at rank zero, the cut's COPY children per distinct served level, restore gates climb,
                  every live register climbs to its end frame, cleanup at FULL).  It returns the paid profile, the
                  climb list of every register (section, index, from-dimension, to-dimension) and, for the census, the
                  frame of every register before each restore gate and the next frame each register must reach after
                  it (snapshots of all registers).  Its paid profile must equal the vendored
                  check_words.frame_recount (edit.two_impl).
attribution()     the registers whose climb dimensions differ between parent and candidate, and the paid delta.
r1_class_census() every adjacent pair of restore gates t += q1*s1; t += q2*s2 at one frame F, rewritten either way
                  round as s += (q'/q) s'; t += q s; s -= (q'/q) s' with the first gate at the span of the two
                  current frames (the cheapest legal choice), the second at F and the third at EVERY subspace F3
                  with F <= F3 <= G, G = the intersection of the next frames s and s' must reach (F3 = F is always
                  legal; a larger F3 can merge a later climb).  Every candidate word (cleanup re-derived) is
                  recounted with the vendored frame recount, nothing is asserted without a recount; the record of a
                  pair/order keeps its best (lowest-mass-weighted) delta and every option.  Pricing (sign of the
                  moment change at the root) is done in audit_kappa.
Standard library only; Python 3.8-compatible syntax.
"""
import copy
import math
from collections import Counter
from fractions import Fraction

import audit_lib as AL
import check_words as CW
import words_check as WC
from audit_common import AuditFail, need

V = AL.V
H = 9
ALLOWED_DIFF = ('restore', 'report', 'cleanup')


# ------------------------------------------------------------------------------------- GF(2) linear algebra ---
def ech(vectors):
    """Reduced echelon basis (tuple, descending pivots) of the span of integer bit-vectors."""
    piv = {}
    for a in vectors:
        a = int(a)
        while a:
            b = a.bit_length() - 1
            if b in piv:
                a ^= piv[b]
            else:
                piv[b] = a
                break
    for b in sorted(piv):
        for c in list(piv):
            if c > b and (piv[c] >> b) & 1:
                piv[c] ^= piv[b]
    return tuple(piv[b] for b in sorted(piv, reverse=True))


def inside(a, b):
    """Every vector of a lies in the span of b."""
    pb = dict((x.bit_length() - 1, x) for x in ech(b))
    for a0 in a:
        x = int(a0)
        while x:
            t = x.bit_length() - 1
            if t not in pb:
                return False
            x ^= pb[t]
    return True


def regs(g):
    return (g[1], g[2]) if g[0] == 'add' else (g[1],)


# ------------------------------------------------------------------------------------------------- own diff ---
def own_diff(parent, cand, declared_edit):
    """See the module docstring.  Returns the record of the hunk."""
    keys = set(parent) | set(cand)
    diff = sorted(k for k in keys if parent.get(k) != cand.get(k))
    need(set(diff) <= set(ALLOWED_DIFF), 'edit.sections: sections differing beyond %r: %r' % (ALLOWED_DIFF, diff))
    need('restore' in diff, 'edit.hunk: the restore sections are identical')
    e = declared_edit
    need(e['section'] == 'restore', 'edit.hunk: declared section %r' % e['section'])
    a, b, old, new = e['start'], e['stop'], e['old'], e['new']
    po, cn = parent['restore'], cand['restore']
    need(0 <= a <= b <= len(po) and po[a:b] == old, 'edit.hunk: parent[%d:%d] is not the declared old block' % (a, b))
    need(cn[a:a + len(new)] == new, 'edit.hunk: candidate[%d:%d] is not the declared new block' % (a, a + len(new)))
    need(len(cn) == len(po) - len(old) + len(new), 'edit.hunk: restore length')
    # minimal hunk by common prefix / suffix: it must lie inside the declared one, which is exactly the statement
    # that the words agree outside the declared hunk (a difference before it lowers p, one after it lowers s)
    p = 0
    while p < min(len(po), len(cn)) and po[p] == cn[p]:
        p += 1
    s = 0
    while s < min(len(po), len(cn)) - p and po[len(po) - 1 - s] == cn[len(cn) - 1 - s]:
        s += 1
    need(a <= p and len(po) - s <= b, 'edit.hunk: minimal hunk [%d, %d) outside the declared [%d, %d)'
         % (p, len(po) - s, a, b))
    return dict(sections_differing=diff, declared=dict(section='restore', start=a, stop=b, old_gates=len(old),
                                                        new_gates=len(new)),
                minimal_hunk=dict(parent=[p, len(po) - s], candidate=[p, len(cn) - s]),
                restore_lengths=dict(parent=len(po), candidate=len(cn)),
                cleanup_lengths=dict(parent=len(parent['cleanup']), candidate=len(cand['cleanup'])),
                touched_registers=sorted(set(r for g in old + new for r in regs(g))))


# --------------------------------------------------------------------------------------------- net operator ---
def apply_formal(rows, g):
    if g[0] == 'add':
        t, s, q = g[1], g[2], Fraction(g[3], g[4])
        need(t != s, 'edit.net_operator: self add')
        dst = rows[t]
        for k, v in list(rows[s].items()):
            nv = dst.get(k, 0) + q * v
            if nv:
                dst[k] = nv
            else:
                dst.pop(k, None)
    elif g[0] == 'scale':
        q = Fraction(g[2], g[3])
        rows[g[1]] = dict((k, v * q) for k, v in rows[g[1]].items())
    else:
        raise AuditFail('edit.net_operator: unknown gate %r' % (g[0],))


def net_operator(old, new):
    """Both blocks as formal operators on the union of their registers (identity start); must be equal."""
    touched = sorted(set(r for g in old + new for r in regs(g)))
    states = []
    for block in (old, new):
        rows = dict((r, {r: Fraction(1)}) for r in touched)
        for g in block:
            need(all(r in rows for r in regs(g)), 'edit.net_operator: register outside the block')
            apply_formal(rows, g)
        states.append(rows)
    need(states[0] == states[1], 'edit.net_operator: the new block is not the old block as an operator')
    return dict(registers=touched,
                operator=dict((str(r), dict((str(k), str(v)) for k, v in sorted(states[0][r].items())))
                              for r in touched))


# -------------------------------------------------------------------------------------------- own frame chain ---
def own_chain(P):
    """See the module docstring.  P is the vendored parse (audit_lib.parse_word)."""
    v, full = P['v'], ech(P['full'])
    cur = dict((r, ech(P['start'][r])) for r in P['live'])
    paid, climbs = Counter(), dict((r, []) for r in P['live'])
    before_post, next_post = {}, {}

    def istarget(r):
        return v <= r < 2 * v

    def climb(r, F, sec, i):
        F = ech(F)
        need(r in cur, 'chain.live: register %d not live at %s[%d]' % (r, sec, i))
        need(inside(cur[r], F), 'chain.monotone: %s[%d] climbs %d from dim %d to a frame of dim %d not containing it'
             % (sec, i, r, len(cur[r]), len(F)))
        d = len(F) - len(cur[r])
        if d:
            paid[d] += 1
            climbs[r].append((sec, i, len(cur[r]), len(F)))
        cur[r] = F

    for i, g in enumerate(P['pre']):
        need(g[-1] == () and istarget(g[1]), 'chain.pre: item %d not a frame-0 target gate' % i)
        for r in WC.regs_of(g):
            climb(r, (), 'pre', i)
    for i, g in enumerate(P['A']):
        if g[0] == 'warp':
            reg, U, E = g[1], ech(g[3]), ech(g[4])
            need(reg in cur and not istarget(reg) and cur[reg] == U, 'chain.awarp: A warp %d lender frame != U' % i)
            cur[reg] = E
            continue
        need(g[-1] is not None, 'chain.A: unframed A gate %d' % i)
        for r in WC.regs_of(g):
            climb(r, g[-1], 'A', i)
    for t in range(v):
        need(cur[v + t] == ech(P['target_levels'].get(t, ())), 'chain.levels: target %d off its level after A' % t)
    served = dict((q, set()) for q in P['centers'])
    for q, U in zip(P['centers'], P['center_frames']):
        need(cur[q] == ech(U), 'chain.centre: centre %d frame' % q)
    for i, g in enumerate(P['cut']):
        need(g[0] == 'add' and g[-1] is None and istarget(g[1]) and g[2] in served, 'chain.cut: item %d' % i)
        served[g[2]].add(cur[g[1]])
    copy_children = []
    for q, U in zip(P['centers'], P['center_frames']):
        prev = ech(U)
        for T in sorted(served[q], key=lambda S: (-len(S), S)):
            need(inside(T, prev), 'chain.copy: served levels of centre %d not nested' % q)
            if T != prev:
                paid[len(prev) - len(T)] += 1
                copy_children.append(len(prev) - len(T))
            prev = T
    for i, it in enumerate(P['B_items']):
        if it[0] == 'warp':
            L, U, E = it[1], ech(it[3]), ech(it[4])
            need(L in cur and not istarget(L) and cur[L] == U, 'chain.bwarp: B warp %d lender frame != U' % i)
            cur[L] = E
        else:
            need(it[-1] is not None, 'chain.B: unframed B gate %d' % i)
            for r in WC.regs_of(it):
                climb(r, it[-1], 'B', i)
    post = list(P['post'])
    # next frame each register must reach after restore gate i: the frame of the next restore gate touching it,
    # else its end frame (sources and R helpers: FULL; targets: hyperplane; restored helpers: helper_final)
    nxt = dict((r, ech(P['end'][r])) for r in P['live'])
    for i in range(len(post) - 1, -1, -1):
        g = post[i]
        next_post[i] = dict(nxt)          # the next frame every register must reach after restore gate i
        for r in WC.regs_of(g):
            nxt[r] = ech(g[-1])
    for i, g in enumerate(post):
        before_post[i] = dict(cur)        # the frame of every register before restore gate i
        for r in WC.regs_of(g):
            climb(r, g[-1], 'post', i)
    for r in P['live']:
        climb(r, P['end'][r], 'end', 0)
    for i, it in enumerate(P['cleanup']):
        need(ech(it[-1]) == full, 'chain.cleanup: item %d not at FULL' % i)
        for r in ((it[1],) if it[0] == 'warp' else WC.regs_of(it)):
            need(r in P['buffers'] or cur.get(r) == full, 'chain.cleanup: item %d touches a non-FULL register %d'
                 % (i, r))
    for r in P['live']:
        need(sum(c[3] - c[2] for c in climbs[r]) == len(ech(P['end'][r])) - len(ech(P['start'][r])),
             'chain.width: charge of %d != its width' % r)
    helpers = [r for r in P['live'] if r >= 2 * v]
    return dict(paid=dict(sorted(paid.items())), climbs=climbs, before_post=before_post, next_post=next_post,
                copy_children=copy_children,
                inventory=dict(sorted(Counter(len(ech(P['end'][r])) - len(ech(P['start'][r]))
                                              for r in helpers).items())),
                mass=sum(k * c for k, c in paid.items()))


def two_impl(chain, fr):
    """edit.two_impl: the own chain and the vendored recount give the same paid profile, inventory and mass."""
    need(chain['paid'] == dict(fr['paid']) and chain['inventory'] == dict(fr['inventory']) and chain['mass'] == fr['mass'],
         'edit.two_impl: own chain %r != vendored recount %r' % (chain['paid'], fr['paid']))
    return dict(paid_equal=True, inventory_equal=True, mass=chain['mass'])


# ---------------------------------------------------------------------------------------------- attribution ---
def dims(lst):
    return [(c[2], c[3]) for c in lst]


def attribution(chain_p, chain_c, expected_delta, expected_regs):
    """The paid delta (edit.delta: exactly expected_delta, checked first), the registers whose climb dimensions
    differ (edit.attribution: exactly expected_regs) and the registers whose climb labels only move (reported)."""
    changed, moved = [], []
    for r in sorted(set(chain_p['climbs']) | set(chain_c['climbs'])):
        a, b = chain_p['climbs'].get(r, []), chain_c['climbs'].get(r, [])
        if dims(a) != dims(b):
            changed.append(r)
        elif a != b:
            moved.append(r)
    delta = AL.counter_delta(chain_c['paid'], chain_p['paid'])
    need(delta == dict(expected_delta), 'edit.delta: paid delta %r != %r' % (delta, dict(expected_delta)))
    need(changed == sorted(expected_regs), 'edit.attribution: climb dimensions changed for %r, expected %r'
         % (changed, sorted(expected_regs)))
    detail = {}
    for r in changed + moved:
        detail[str(r)] = dict(parent=[list(c) for c in chain_p['climbs'].get(r, [])],
                              candidate=[list(c) for c in chain_c['climbs'].get(r, [])])
    return dict(dimensions_changed=changed, labels_only_moved=moved, paid_delta=AL.hist(delta), climbs=detail)


# --------------------------------------------------------------------------------------------------- census ---
def dyadic(q):
    return q != 0 and q.denominator & (q.denominator - 1) == 0


def intersect(A, B):
    """Basis of span(A) ∩ span(B) over GF(2) (brute force over the 512 vectors of GF(2)^9)."""
    def member(x, S):
        return inside((x,), S)
    return ech([x for x in range(1, 1 << H) if member(x, A) and member(x, B)])


def between(F, G):
    """Every subspace F3 with span(F) <= F3 <= span(G), as echelon bases (brute force over the quotient)."""
    F, G = ech(F), ech(G)
    need(inside(F, G), 'census.between: F not inside G')
    extra = [x for x in range(1, 1 << H) if inside((x,), G) and not inside((x,), F)]
    out = set([F])
    frontier = [F]
    while frontier:
        nxt = []
        for S in frontier:
            for x in extra:
                if not inside((x,), S):
                    T = ech(S + (x,))
                    if T not in out:
                        out.add(T)
                        nxt.append(T)
        frontier = nxt
    return sorted(out, key=lambda S: (len(S), S))


def hyperplane(p):
    """E_p = {x : <x, p> = 0 mod 2}, as in the lineage's parsers."""
    return ech([x for x in range(1, 1 << H) if bin(x & p).count('1') % 2 == 0])


def v45_identity(frame):
    """The rank-7 frame of R1's first gate is E_7 ∩ E_42 ∩ E_45 (rule edit.v45)."""
    want = intersect(intersect(hyperplane(7), hyperplane(42)), hyperplane(45))
    need(ech(frame) == want and len(want) == 7, 'edit.v45: the first new frame is not E_7 ∩ E_42 ∩ E_45')
    return dict(frame=list(ech(frame)), equals_E7_E42_E45=True, dim=len(want))


def rewrite(w, i, a, b, F1, F, F3, q_a, ratio):
    """The word with restore[i:i+2] replaced by the R1-class block with carrier a absorbing b (cleanup re-derived;
    the report fields are left as they are, the recount does not read them)."""
    m = copy.deepcopy(w)
    new = [['add', a, b, ratio.numerator, ratio.denominator, list(F1)],
           ['add', w['restore'][i][1], a, q_a.numerator, q_a.denominator, list(F)],
           ['add', a, b, -ratio.numerator, ratio.denominator, list(F3)]]
    m['restore'][i:i + 2] = new
    m['cleanup'] = AL.rederive_cleanup(m)
    return m, new


def r1_class_census(w, P, chain, parent_paid):
    """See the module docstring.  Returns (records, summary)."""
    post = w['restore']
    records = []
    for i in range(len(post) - 1):
        g1, g2 = post[i], post[i + 1]
        if g1[0] != 'add' or g2[0] != 'add' or g1[1] != g2[1] or g1[-1] is None or g2[-1] is None:
            continue
        if ech(g1[-1]) != ech(g2[-1]):
            continue
        t, s1, s2 = g1[1], g1[2], g2[2]
        if s1 == s2 or t in (s1, s2):
            continue
        F = ech(g1[-1])
        for (a, b, ga, gb) in ((s1, s2, g1, g2), (s2, s1, g2, g1)):
            q_a, q_b = Fraction(ga[3], ga[4]), Fraction(gb[3], gb[4])
            ratio = q_b / q_a
            rec = dict(index=i, target=t, carrier=a, absorbed=b, order=('s1 absorbs s2' if a == s1 else 's2 absorbs s1'),
                       frame_dim=len(F))
            if not dyadic(ratio):
                rec.update(legal=False, why='non-dyadic ratio')
                records.append(rec)
                continue
            cur_a, cur_b = chain['before_post'][i][a], chain['before_post'][i][b]
            F1 = ech(cur_a + cur_b)
            nxt_a, nxt_b = chain['next_post'][i + 1][a], chain['next_post'][i + 1][b]
            G = intersect(nxt_a, nxt_b)
            rec.update(dims=dict(cur_a=len(cur_a), cur_b=len(cur_b), F1=len(F1), F=len(F), next_a=len(nxt_a),
                                 next_b=len(nxt_b), G=len(G)))
            if not inside(F1, F):
                rec.update(legal=False, why='span of the current frames not inside F')
                records.append(rec)
                continue
            if not inside(F, G):
                rec.update(legal=False, why='F not inside the intersection of the next frames')
                records.append(rec)
                continue
            options = []
            for F3 in between(F, G):
                m, new = rewrite(w, i, a, b, F1, F, F3, q_a, ratio)
                try:
                    fr = CW.frame_recount(AL.parse_word(m))
                except WC.Reject as err:
                    options.append(dict(F3=len(F3), legal=False,
                                        why='vendored recount: %s %s' % (err.check, ' '.join(str(err.msg).split())[:100])))
                    continue
                delta = AL.counter_delta(fr['paid'], parent_paid)
                options.append(dict(F3=len(F3), legal=True, delta=AL.hist(delta), mass=sum(k * v for k, v in delta.items()),
                                    new_block=new))
            legal_opts = [o for o in options if o['legal']]
            need(legal_opts and all(o['delta'] == {} for o in legal_opts if o['F3'] == len(F)),
                 'census.f3: the third gate at F must be legal with delta zero at restore[%d]' % i)
            # every legal option's delta is kept; which of them improve is decided by the exact pricing (audit_kappa);
            # 'delta' is only a display choice: the lowest proxy price (rank mass first, then the concave correction)
            best = min(legal_opts, key=lambda o: proxy(o['delta']))
            rec.update(legal=True, options=len(options), legal_options=len(legal_opts), f3_dims=[o['F3'] for o in legal_opts],
                       option_deltas=sorted(set(AL.canon(o['delta']) for o in legal_opts)),
                       delta=best['delta'], best_F3=best['F3'], new_block=best['new_block'],
                       nonzero_options=[dict(F3=o['F3'], delta=o['delta']) for o in legal_opts if o['delta']])
            records.append(rec)
    legal = [r for r in records if r['legal']]
    summary = dict(adjacent_same_target_pairs=len(set(r['index'] for r in records)), candidates=len(records),
                   legal=len(legal), illegal_reasons=dict(Counter(r['why'].split(':')[0] for r in records
                                                                   if not r['legal'])),
                   rewrites_recounted=sum(r['options'] for r in legal),
                   records_with_a_nonzero_option=sum(1 for r in legal if r['nonzero_options']),
                   option_deltas=dict(Counter(AL.canon(o['delta']) for r in legal for o in r['nonzero_options'])))
    return records, summary


def proxy(delta):
    """Display-only ordering of a per-call profile delta: rank mass first, then the first-order concave correction
    -sum d_r r ln r (the sign of the moment change of a mass-zero delta)."""
    d = AL.intkeys(delta)
    return (sum(v * r for r, v in d.items()), -sum(v * r * math.log(r) for r, v in d.items()))
