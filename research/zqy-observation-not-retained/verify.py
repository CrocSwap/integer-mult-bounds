#!/usr/bin/env python3
"""The coupled-exit observation b = Z Q Y is not present in any retained version (negative result, no new kappa).

Mark (Matarener), with substantial Claude Code (Claude) assistance. Apache-2.0.

#5415 (zxv) shows that the PR5402 coupled provider can return its eight modes with
8 H1 + 456 ADD + 240 maps if the current-version observation b = Z Q Y is supplied,
and that buying it (120 H1 per backward FULL) fails the moment screen. Its open
question 1, #5419 experiment 1 and #5425 open question 1 ask whether b can be taken
from observations that already exist. This script answers that question in the
formal free-word grammar used by the #5377 / #5397 row engines, at two levels:

 N  native level: replay the PR5402 provider backward word and the #4610 word in both
    orientations with exact rows over (input role, warp word); paid climbs change only
    the frame. Q Y_k is the row of the input y_k = L_{112+k} standing in the full
    (9-dimensional) frame. Every full-frame version at every time may be kept in owned
    storage, so the available set is the span V of all of them. Certify
    dim(V ∩ span{y_k}) = 0, also for y_k with any warp word, and that the x-free part
    of V is exactly the helper content.
 C  caller level: replay the selected p16 caller of #5415 (162 events, 18 backward
    FULLs) with the #5415 event semantics (Q and D_s commute, Q_POWER and SIGNED_SWAP
    free). No version word begins with a Z letter, so b = Z_s Q Y is available iff
    Q Y lies in the span of all versions after free left factors Q^{+-2}, W_t
    (products of length <= LEFT_DEPTH). Certify 0 of 18 at the return and 0 of 18 with
    the whole caller history (a delayed exit).

Arithmetic is modulo the prime 2^61-1. All coefficients are dyadic, so an identity over
the rationals reduces to one modulo p; non-membership modulo p therefore implies
non-membership over the rationals. Controls show that both tests can say yes.

Part 2 (response reuse, the "global occurrence ledger" of #5423): no paid job can be
replaced by an earlier response.
 R1 native: for every paid climb/centre (frame A -> B, row r), r is not in the span of the
    versions that stood in B before it (EARLY), nor of the other B versions that exist before
    the next event touching the field (LATE; own result tagged). Injected-copy controls.
 R2 caller: no thin QUERY response, IDLE bank output or LOCAL Y output lies in the span of
    the earlier versions after free left factors Q^{+-2}, W_t, Z_t. Repeated-query control.

Usage: python3 -I -W error -B verify.py [--write] [--left-depth 2]
Exit 0 and marker PASS_ZQY_OBSERVATION_NOT_RETAINED iff every check passes and RESULT.json matches.
"""
import gzip
import hashlib
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
P = (1 << 61) - 1
INPUTS = {
    'provider': ('research/native-rank8-helper-provider/WORD.json.gz',
                 '7dc356001ed597ad6fc9fd3e0bc6ff7e3ec3a580a579a956827aa17fccfdd2dc'),
    'word4610': ('research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz',
                 '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'),
    'caller': ('research/coupled-query-transport/inputs/SUCCESSOR-CONTROLLER.json',
               '60cc512b39cdb9ea2c2ac6c6634c8d3f9627d96ace08ffa659a9d9472444122b'),
}


def need(ok, why):
    if not ok:
        raise AssertionError(why)


def read_input(name):
    rel, sha = INPUTS[name]
    with open(os.path.join(ROOT, *rel.split('/')), 'rb') as fh:
        raw = fh.read()
    need(hashlib.sha256(raw).hexdigest() == sha, 'input bytes changed: ' + rel)
    return json.loads(gzip.decompress(raw) if rel.endswith('.gz') else raw)


# ---------------------------------------------------------------- exact span modulo p
class Span:
    """Sparse reduced echelon basis modulo P."""

    def __init__(self):
        self.piv = {}

    def reduce(self, v):
        v = dict(v)
        while True:
            hit = next((c for c in v if c in self.piv), None)
            if hit is None:
                return v
            f = v[hit]
            for c, x in self.piv[hit].items():
                nv = (v.get(c, 0) - f * x) % P
                if nv:
                    v[c] = nv
                else:
                    v.pop(c, None)

    def add(self, v):
        v = self.reduce(v)
        if not v:
            return False
        c = min(v)
        inv = pow(v[c], P - 2, P)
        v = {k: x * inv % P for k, x in v.items()}
        for b in self.piv.values():
            if c in b:
                f = b[c]
                for k, x in v.items():
                    nv = (b.get(k, 0) - f * x) % P
                    if nv:
                        b[k] = nv
                    else:
                        b.pop(k, None)
        self.piv[c] = v
        return True

    def copy(self):
        s = Span()
        s.piv = {c: dict(b) for c, b in self.piv.items()}
        return s


def modrow(row, index):
    out = {}
    for key, q in row.items():
        c = index.setdefault(key, len(index))
        need(q.denominator & (q.denominator - 1) == 0, 'dyadic coefficient')
        out[c] = q.numerator % P * pow(q.denominator % P, P - 2, P) % P
    return out


# ---------------------------------------------------------------- native level
def span_set(basis):
    out = {0}
    for v in basis:
        out |= {x ^ v for x in tuple(out)}
    need(len(out) == 1 << len(basis), 'independent frame basis')
    return out


def native_replay(canon, program, backward):
    """Exact rows (convention of research/kappa-owned-relation-20261023/native.py).
    Returns the list of distinct full-frame versions, final rows and final frames."""
    spaces = [span_set(b) for b in canon['frames']]
    full = {i for i, s in enumerate(spaces) if len(s) == 512}
    need(len(full) == 1, 'one full frame')
    rows = {('L', i): {(('L', i), ()): Fr(1)} for i in range(632)}
    frames = {('L', i): canon['start'][i] for i in range(632)}

    def get(r):
        if r not in rows:
            rows[r] = {(r, ()): Fr(1)}
            frames[r] = None
        return rows[r]

    seen, versions = set(), []
    for e in program:
        k, touched = e[0], None
        if k == 'scalar':
            g, frame = e[1], e[2]
            dst = tuple(g[1]); get(dst); touched = dst
            if g[0] == 'clear':
                rows[dst] = {}; frames[dst] = frame
            elif g[0] == 'copy':
                src = tuple(g[2]); need(frames[src] == frame, 'copy frame')
                rows[dst] = dict(get(src)); frames[dst] = frame
            elif g[0] == 'add':
                src = tuple(g[2]); need(frames[src] == frame == frames[dst], 'same-frame ADD')
                q = Fr(g[3], g[4]); r = rows[dst]
                for key, v in get(src).items():
                    nv = r.get(key, 0) + q * v
                    if nv:
                        r[key] = nv
                    else:
                        r.pop(key, None)
            elif g[0] == 'scale':
                q = Fr(g[2], g[3]); rows[dst] = {a: q * v for a, v in rows[dst].items()}
            else:
                raise AssertionError('unknown scalar ' + repr(g[0]))
        elif k == 'warp':
            _, role, op, old, new = e
            dst = tuple(role); get(dst); touched = dst
            need(frames[dst] == old, 'warp input frame')
            sym = (1 if op > 0 else -1) * (abs(op) + (10 ** 6 if backward else 0))
            rows[dst] = {(r, w[1:] if w and w[0] == -sym else (sym,) + w): q for (r, w), q in rows[dst].items()}
            frames[dst] = new
        elif k == 'climb':
            dst = ('L', e[2]); need(frames[dst] == e[3], 'climb input frame')
            frames[dst] = e[4]; touched = dst
        elif k == 'center':
            dst = ('C', e[1]); get(dst); frames[dst] = e[3]; touched = dst
        elif k == 'zero_retag':
            dst = ('L', e[1]); need(frames[dst] == e[2] and not rows[dst], 'zero retag on a zero row')
            frames[dst] = e[3]; touched = dst
        else:
            need(k in ('phase', 'adapter'), 'unknown event ' + repr(k))
        if touched is not None and frames[touched] in full and rows[touched]:
            key = frozenset(rows[touched].items())
            if key not in seen:
                seen.add(key); versions.append(dict(rows[touched]))
    return versions, rows, frames, full


def role_class(key):
    r = key[0]
    if r[0] == 'L' and r[1] < 112:
        return 'x'
    if r[0] == 'L' and r[1] < 224:
        return 'y'
    return 'h'


def native_level(name, canon, program, backward):
    versions, rows, frames, full = native_replay(canon, program, backward)
    index = {(('L', 112 + k), ()): k for k in range(112)}
    V = Span()
    mods = []
    for v in versions:
        m = modrow(v, index); mods.append(m); V.add(m)
    # every final full-frame row is in V (the test sees the endpoints)
    need(all(not V.reduce(modrow(rows[r], index)) for r in rows if frames[r] in full and rows[r]), name + ': endpoints in V')
    # main test: pure y with the empty warp word
    R = Span()
    indep = sum(R.add(V.reduce({k: 1})) for k in range(112))
    inter = 112 - indep
    # control: one injected pure-y version is detected
    W = V.copy(); W.add({5: 1})
    R2 = Span()
    control = 112 - sum(R2.add(W.reduce({k: 1})) for k in range(112))
    need(control == 1, name + ': injected pure-y control')
    inv = {c: key for key, c in index.items()}
    cls = {c: role_class(key) for c, key in inv.items()}
    # x-free part and pure-y-any-word part via projections
    px, pxh = Span(), Span()
    for m in mods:
        px.add({c: v for c, v in m.items() if cls[c] == 'x'})
        pxh.add({c: v for c, v in m.items() if cls[c] != 'y'})
    out = {'full_frame_versions': len(versions), 'rank_V': len(V.piv), 'coordinates': len(index),
           'dim_V_cap_pure_y': inter, 'dim_V_cap_y_any_warp_word': len(V.piv) - len(pxh.piv),
           'dim_x_free_part': len(V.piv) - len(px.piv),
           'versions_with_y_content': sum(any(cls[c] == 'y' for c in m) for m in mods),
           'control_injected_pure_y_detected': control}
    need(inter == 0 and out['dim_V_cap_y_any_warp_word'] == 0, name + ': pure y is available')
    return out


# ---------------------------------------------------------------- caller level
def normal(word):
    """#5415 word_normal: Q and D_* commute; adjacent inverse letters cancel."""
    out, run = [], {}

    def flush():
        for lab in sorted(run):
            e = run[lab]
            out.extend([(lab, 1 if e > 0 else -1)] * abs(e))
        run.clear()
    for lab, e in word:
        if lab == 'Q' or lab.startswith('D'):
            run[lab] = run.get(lab, 0) + e
            if run[lab] == 0:
                run.pop(lab)
        else:
            flush()
            if out and out[-1] == (lab, -e):
                out.pop()
            else:
                out.append((lab, e))
    flush()
    return tuple(out)


def left(row, *ops):
    out = {}
    for (s, w), v in row.items():
        k = (s, normal(tuple(ops) + w)); out[k] = out.get(k, 0) + v
    return {k: v for k, v in out.items() if v}


def plus(a, b, c=1):
    out = dict(a)
    for k, v in b.items():
        t = out.get(k, 0) + c * v
        if t:
            out[k] = t
        else:
            out.pop(k, None)
    return out


def caller_level(ctl, depth):
    ev = ctl['physical_events']
    nf = 2 * ctl['pairs']
    rows = [{(('in', j), ()): Fr(1)} for j in range(nf)]
    versions = [dict(r) for r in rows]
    stages = sorted({e[1] for e in ev if e[0] == 'LOCAL'})
    one = [(), (('Q', 1), ('Q', 1)), (('Q', -1), ('Q', -1))] + [(('W%d' % t, 1),) for t in stages]
    frees = {()}
    for _ in range(depth):
        frees = {normal(a + b) for a in frees for b in one}
    frees = sorted(frees)
    index, V, done, targets, per_call = {}, Span(), 0, [], []

    def absorb():
        nonlocal done
        for v in versions[done:]:
            need(not any(w and w[0][0].startswith('Z') for (_, w) in v), 'a version word begins with Z')
            for f in frees:
                V.add(modrow(left(v, *f) if f else v, index))
        done = len(versions)

    for i, e in enumerate(ev):
        k = e[0]
        if k == 'LOCAL':
            s, p, bw = e[1], e[2], e[3]
            need(bw, 'backward FULL')
            x, y = 2 * p, 2 * p + 1
            D, h = ('D%d' % s, 1), {(('h', s), ()): Fr(1)}
            yold = rows[y]
            helper = plus(left(h, D), left(yold, D, ('Z%d' % s, 1)), -1)
            rows[x] = plus(plus(left(rows[x], D), left(yold, D, ('Q', 1)), -1), left(h, D, ('Q', 1), ('W%d' % s, 1)))
            rows[y] = left(yold, D)
            versions += [dict(rows[x]), dict(rows[y]), helper]
            absorb()
            target = left(rows[y], ('Q', 1))
            targets.append(target)
            ok = not V.reduce(modrow(target, index))
            ctrl = not V.reduce(modrow(rows[y], index))
            need(ctrl, 'control: current Y must be available')
            per_call.append({'event': i, 'stage': s, 'pair': p, 'b_available_at_return': ok})
        elif k == 'IDLE':
            for j in (2 * e[1], 2 * e[1] + 1):
                rows[j] = left(rows[j], *[('D%d' % st, 1) for st in reversed(e[2])])
                versions.append(dict(rows[j]))
        elif k == 'ADD':
            rows[e[1]] = plus(rows[e[1]], rows[e[2]], e[3]); versions.append(dict(rows[e[1]]))
        elif k == 'QUERY_SHEAR':
            need(not e[3], 'lower thin shear')
            resp = left(rows[2 * e[2]], ('Q', -1))
            versions.append(resp)
            rows[2 * e[2] + 1] = plus(rows[2 * e[2] + 1], resp); versions.append(dict(rows[2 * e[2] + 1]))
        elif k == 'SIGNED_SWAP':
            a, b = e[1], e[2]
            rows[a], rows[b] = rows[b], {kk: -v for kk, v in rows[a].items()}
        elif k == 'Q_POWER':
            rows[e[1]] = left(rows[e[1]], *([('Q', 1 if e[2] > 0 else -1)] * abs(e[2])))
            versions.append(dict(rows[e[1]]))
        else:
            raise AssertionError('unknown caller event ' + repr(k))
    absorb()
    late = sum(not V.reduce(modrow(t, index)) for t in targets)
    # control: a target that IS a free image of a version (Q^2 times the final Y bank) is found
    need(not V.reduce(modrow(left(rows[1], ('Q', 1), ('Q', 1)), index)), 'control: Q^2 Y is available')
    out = {'events': len(ev), 'backward_FULL_returns': len(per_call),
           'available_at_return': sum(c['b_available_at_return'] for c in per_call),
           'available_with_whole_history': late, 'free_left_factors': len(frees), 'left_depth': depth,
           'closure_rank': len(V.piv), 'versions': len(versions), 'per_call': per_call}
    need(out['backward_FULL_returns'] == 18, '18 backward FULLs')
    need(out['available_at_return'] == 0 and late == 0, 'b = Z Q Y available at some return')
    return out


# ---------------------------------------------------------------- part 2: response reuse
def native_events(canon, program, backward):
    """Per event: (index, kind, role, row after, frame before, frame after, rank, source role)."""
    rows = {('L', i): {(('L', i), ()): Fr(1)} for i in range(632)}
    frames = {('L', i): canon['start'][i] for i in range(632)}

    def get(r):
        if r not in rows:
            rows[r] = {(r, ()): Fr(1)}
            frames[r] = None
        return rows[r]
    out = []
    for idx, e in enumerate(program):
        k = e[0]
        if k == 'scalar':
            g, frame = e[1], e[2]
            dst = tuple(g[1]); get(dst); old = frames[dst]; src = None
            if g[0] == 'clear':
                rows[dst] = {}; frames[dst] = frame
            elif g[0] == 'copy':
                src = tuple(g[2]); rows[dst] = dict(get(src)); frames[dst] = frame
            elif g[0] == 'add':
                src = tuple(g[2]); q = Fr(g[3], g[4]); r = rows[dst]
                for key, v in get(src).items():
                    nv = r.get(key, 0) + q * v
                    if nv:
                        r[key] = nv
                    else:
                        r.pop(key, None)
            elif g[0] == 'scale':
                q = Fr(g[2], g[3]); rows[dst] = {a: q * v for a, v in rows[dst].items()}
            out.append((idx, 'scalar', dst, dict(rows[dst]), old, frames[dst], None, src))
        elif k == 'warp':
            _, role, op, old, new = e
            dst = tuple(role); get(dst)
            sym = (1 if op > 0 else -1) * (abs(op) + (10 ** 6 if backward else 0))
            rows[dst] = {(r, w[1:] if w and w[0] == -sym else (sym,) + w): q for (r, w), q in rows[dst].items()}
            frames[dst] = new
            out.append((idx, 'warp', dst, dict(rows[dst]), old, new, None, None))
        elif k in ('climb', 'center'):
            dst = ('L', e[2]) if k == 'climb' else ('C', e[1]); get(dst)
            old, new, rank = (e[3], e[4], e[5]) if k == 'climb' else (e[2], e[3], e[4])
            frames[dst] = new
            out.append((idx, k, dst, dict(rows[dst]), old, new, rank, None))
        elif k == 'zero_retag':
            dst = ('L', e[1]); old = frames[dst]; frames[dst] = e[3]
            out.append((idx, 'zero_retag', dst, dict(rows[dst]), old, e[3], None, None))
    return out


def reuse_census(ev, inject=None):
    """EARLY: a paid result r (frame A->B) lies in the span of every version that stood in B
    before the climb. LATE: r lies in the span of the other B versions that exist before the
    next event touching the field; the own result is stored as r + e_tag, so e_tag is in the
    span iff r is a combination of the others."""
    touches = {}
    for j, x in enumerate(ev):
        touches.setdefault(x[2], []).append(j)
        if x[7] is not None:
            touches.setdefault(x[7], []).append(j)
    index, spans, tspans, pending = {}, {}, {}, []
    early, late, paid, by_rank = [], [], 0, {}
    for j, (idx, kind, dst, row, a, b, rank, src) in enumerate(ev):
        while pending and pending[0][0] <= j:
            _, tag, fr, info = pending.pop(0)
            if not tspans[fr].reduce({tag: 1}):
                late.append(info)
        tag = None
        if kind in ('climb', 'center'):
            paid += 1
            by_rank[str(rank)] = by_rank.get(str(rank), 0) + 1
            info = {'event': idx, 'role': list(dst), 'from': a, 'to': b, 'rank': rank}
            m = modrow(row, index) if row else {}
            if not row or not spans.setdefault(b, Span()).reduce(m):
                early.append(info)
            else:
                nxt = [t for t in touches[dst] if t > j]
                tag = (1 << 40) + j
                pending.append((nxt[0] if nxt else len(ev), tag, b, info))
                pending.sort(key=lambda x: x[0])
        if inject is not None and idx == inject[0]:
            v = modrow(inject[2], index)
            spans.setdefault(inject[1], Span()).add(v)
            tspans.setdefault(inject[1], Span()).add(v)
        if row and b is not None:
            v = modrow(row, index)
            spans.setdefault(b, Span()).add(v)
            tv = dict(v)
            if tag is not None:
                tv[tag] = 1
            tspans.setdefault(b, Span()).add(tv)
    for _, tag, fr, info in pending:
        if not tspans[fr].reduce({tag: 1}):
            late.append(info)
    return {'paid_events': paid, 'paid_by_rank': by_rank, 'early_reuse': early, 'late_reuse': late}


def native_reuse(name, canon, program, backward, control):
    ev = native_events(canon, program, backward)
    out = reuse_census(ev)
    need(not out['early_reuse'] and not out['late_reuse'], name + ': a paid result is reusable')
    if control:
        j, first = next((j, x) for j, x in enumerate(ev) if x[1] == 'climb' and x[6] == 1 and x[3])
        before = reuse_census(ev, inject=(ev[j - 1][0], first[5], first[3]))
        after = reuse_census(ev, inject=(first[0], first[5], first[3]))
        need([x['event'] for x in before['early_reuse']] == [first[0]], name + ': EARLY control')
        need([x['event'] for x in after['late_reuse']] == [first[0]] and not after['early_reuse'], name + ': LATE control')
        out['controls'] = {'injected_before_climb_found_early': first[0], 'injected_after_climb_found_late_only': first[0]}
    out['early_reuse'] = len(out['early_reuse'])
    out['late_reuse'] = len(out['late_reuse'])
    return out


def caller_reuse(ev, nf):
    """Each paid caller output (QUERY response, IDLE bank output, LOCAL Y output) against the
    span of all earlier versions after free left factors Q^{+-2}, W_t, Z_t (length <= 1)."""
    rows = [{(('in', j), ()): Fr(1)} for j in range(nf)]
    versions = [dict(r) for r in rows]
    stages = sorted({e[1] for e in ev if e[0] == 'LOCAL'})
    frees = [(), (('Q', 1), ('Q', 1)), (('Q', -1), ('Q', -1))]
    frees += [(('W%d' % t, 1),) for t in stages] + [(('Z%d' % t, 1),) for t in stages]
    index, V, hits = {}, Span(), []
    tested = {'QUERY': 0, 'IDLE': 0, 'LOCAL_Y': 0}
    done = [0]

    def test(i, kind, out):
        for v in versions[done[0]:]:
            for f in frees:
                V.add(modrow(left(v, *f) if f else v, index))
        done[0] = len(versions)
        tested[kind] += 1
        if not V.reduce(modrow(out, index)):
            hits.append([i, kind])
    for i, e in enumerate(ev):
        k = e[0]
        if k == 'LOCAL':
            s, p = e[1], e[2]
            x, y = 2 * p, 2 * p + 1
            D, h = ('D%d' % s, 1), {(('h', s), ()): Fr(1)}
            yold = rows[y]
            newx = plus(plus(left(rows[x], D), left(yold, D, ('Q', 1)), -1), left(h, D, ('Q', 1), ('W%d' % s, 1)))
            newy = left(yold, D)
            test(i, 'LOCAL_Y', newy)
            rows[x], rows[y] = newx, newy
            versions += [dict(newx), dict(newy), plus(left(h, D), left(yold, D, ('Z%d' % s, 1)), -1)]
        elif k == 'IDLE':
            for j in (2 * e[1], 2 * e[1] + 1):
                out = left(rows[j], *[('D%d' % st, 1) for st in reversed(e[2])])
                test(i, 'IDLE', out)
                rows[j] = out
                versions.append(dict(out))
        elif k == 'ADD':
            rows[e[1]] = plus(rows[e[1]], rows[e[2]], e[3])
            versions.append(dict(rows[e[1]]))
        elif k == 'QUERY_SHEAR':
            resp = left(rows[2 * e[2]], ('Q', -1))
            test(i, 'QUERY', resp)
            versions.append(resp)
            rows[2 * e[2] + 1] = plus(rows[2 * e[2] + 1], resp)
            versions.append(dict(rows[2 * e[2] + 1]))
        elif k == 'SIGNED_SWAP':
            a, b = e[1], e[2]
            rows[a], rows[b] = rows[b], {kk: -v for kk, v in rows[a].items()}
        elif k == 'Q_POWER':
            rows[e[1]] = left(rows[e[1]], *([('Q', 1 if e[2] > 0 else -1)] * abs(e[2])))
            versions.append(dict(rows[e[1]]))
        else:
            raise AssertionError('unknown caller event ' + repr(k))
    return tested, hits


def caller_reuse_level(ctl):
    ev, nf = ctl['physical_events'], 2 * ctl['pairs']
    qi = next(i for i, e in enumerate(ev) if e[0] == 'QUERY_SHEAR')
    _, chits = caller_reuse(ev[:qi + 1] + [ev[qi]] + ev[qi + 1:], nf)
    need(chits == [[qi + 1, 'QUERY']], 'control: a repeated thin query is found')
    tested, hits = caller_reuse(ev, nf)
    need(tested == {'QUERY': 15, 'IDLE': 30, 'LOCAL_Y': 18}, 'paid caller output census')
    need(not hits, 'a paid caller output is reusable: %r' % hits)
    return {'paid_outputs_tested': tested, 'reusable': 0, 'control_repeated_query_found_at_event': qi + 1}


def main():
    write = '--write' in sys.argv
    depth = 1
    if '--left-depth' in sys.argv:
        depth = int(sys.argv[sys.argv.index('--left-depth') + 1])
    word = read_input('word4610')
    prov = read_input('provider')
    ctl = read_input('caller')
    need(prov['source_sha256'] == 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
         and prov['direction'] == 'backward', 'provider word is the PR5402 backward word over the #4610 canonical frames')
    result = {'schema': 'zqy-observation-not-retained/2', 'native': {}, 'caller': None,
              'arithmetic': 'exact dyadic rows, spans modulo 2^61-1 (non-membership mod p implies non-membership over Q)'}
    for name, prog, bw in (('pr5402_provider_backward', prov['word'], True),
                           ('pr4610_backward', word['programs']['backward'], True),
                           ('pr4610_forward', word['programs']['forward'], False)):
        out = native_level(name, word['canonical'], prog, bw)
        result['native'][name] = out
        print('[native %s] %s' % (name, json.dumps(out, sort_keys=True)), flush=True)
    result['caller'] = caller_level(ctl, depth)
    print('[caller] %s' % json.dumps({k: v for k, v in result['caller'].items() if k != 'per_call'}, sort_keys=True), flush=True)
    result['reuse'] = {'native': {}, 'caller': None}
    for name, prog, bw in (('pr5402_provider_backward', prov['word'], True),
                           ('pr4610_backward', word['programs']['backward'], True),
                           ('pr4610_forward', word['programs']['forward'], False)):
        out = native_reuse(name, word['canonical'], prog, bw, control=(name == 'pr5402_provider_backward'))
        result['reuse']['native'][name] = out
        print('[reuse native %s] %s' % (name, json.dumps(out, sort_keys=True)), flush=True)
    result['reuse']['caller'] = caller_reuse_level(ctl)
    print('[reuse caller] %s' % json.dumps(result['reuse']['caller'], sort_keys=True), flush=True)
    if depth != 1:
        print('left depth %d run: RESULT.json is recorded at depth 1; not compared' % depth)
        print('PASS_ZQY_OBSERVATION_NOT_RETAINED')
        return
    result['caller_depth2_evidence'] = {
        'note': 'same test with free left factors of length <= 2 (419 factors), run with --left-depth 2 (about 2 minutes); not part of the registered replay',
        'available_at_return': 0, 'available_with_whole_history': 0, 'closure_rank_at_end': 56405}
    path = os.path.join(HERE, 'RESULT.json')
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if write:
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(text)
    else:
        with open(path, encoding='utf-8', newline='') as fh:
            need(fh.read() == text, 'RESULT.json differs from the recomputed result; run with --write to refresh')
    print('PASS_ZQY_OBSERVATION_NOT_RETAINED')


if __name__ == '__main__':
    main()
