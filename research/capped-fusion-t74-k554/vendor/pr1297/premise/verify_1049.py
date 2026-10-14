#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared by Sagar Thakrar with substantial Anthropic Claude assistance.
"""Independent audit of the mutable-leaver all-K cells of PR1005, and of the same cells in PR1018's word.

Standard library only. No code from the audited packages is imported; their words are read as data
(see SOURCES.json for how each pinned input was produced). The checks follow the documented
scalar/frame semantics of the gauge44 local words:

E  Endpoint. Each data column is replayed forward through precondition + A + cut + B + tail +
   cleanup and must give x_t -> x_t + y_t-coordinate, i.e. x -> x, y_t -> y_t + x_t. Each helper
   column is replayed through the inverse of the post-precondition program; the result must be
   the unit vector plus a target-only residue. That is exactly the condition under which a
   pre-main compensation y -= a*h exists. The residue must vanish for entering helpers.
F  Frames. Monotone climbs over A, the centre paths, B, the early-cleanup tail and the terminal
   ends. The FULL cleanup may touch only registers that end at FULL. The paid histogram must equal
   the word's recorded local profile.
L  Leaver cells. Each coded cell's 21 scaled gates are located literally (contiguous, in order)
   in A + cut + B by unification. Each name binds to one register, the y-names bind to the cell's
   six targets (TRI read indices; the coded index is t8 + 8), and the x-names bind to non-targets.
   For every mutated leaver: it is not a centre, entering helper or low-ended helper. It is never
   touched again in A/cut/B or the tail after its cell, and it is written later in the FULL
   cleanup. Its value at the end of B differs from its input, so the restoration is real work.
D  Profile deltas. The raw-stage paid profiles of the no-triangle, k5 and k8 words are recomputed
   with F and differenced.
Every check raises AuditError directly (no assert), so it also runs under python -O.
"""
import argparse, copy, gzip, hashlib, json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
IN = HERE / 'inputs'
PINS = {  # sha256 of the decompressed JSON (of the file itself for .json)
    'k8-cell-word.json.gz': '58e14a02f2c1d4dcfeb363ebd5fa2e713064b5c724d90f6721419a8cfa67729b',
    'k8-final-word.json.gz': 'db2c7cfb3f8eee2b76c2e0154fc530520fb4d90cd9511a002cab527b16033b83',
    'k8-seven-slot-word.json.gz': 'c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8',
    'notri-cold44-word.json.gz': '3e99ba778ab8a97853f50912776247802b529439937176363f6c42786163b1f9',
    'raw-notri.json.gz': '5a55ea28628e3d76ed31393505f4605d7a8d5b002716a44115fea60cdc3477e3',
    'raw-k5.json.gz': 'c9114254533c7e272504016764c93370e18734469587a86fb07652b85f8ae209',
    'raw-k8.json.gz': '85c0e64718a9ceafe094e7152ea27ec9d7f804e514b5efaab085a94b7ef1841f',
    'CODED-CELLS-k8.json': '7347f814850a838bd617bc7a55c307cec2b72becde2f12ea3e2e1af344b43563',
    'TRI-LEAVER-k8.json': 'b22e6ecf76104de66844bd617c4ca80f5546ba0966a50e5e9aa0ffea4976cb30',
}


class AuditError(Exception):
    pass


def need(ok, msg):
    if not ok:
        raise AuditError(msg)


def read_pinned(name):
    data = (IN / name).read_bytes()
    raw = gzip.decompress(data) if name.endswith('.gz') else data
    need(hashlib.sha256(raw).hexdigest() == PINS[name], 'input pin mismatch: ' + name)
    return json.loads(raw)


# ------------------------------------------------------------------ scalar semantics

def regs(g):
    return (g[1], g[2]) if g[0] == 'add' else (g[1],)


def coef(g):
    return Q(g[3], g[4]) if g[0] == 'add' else Q(g[2], g[3])


def forward(gates, col):
    for g in gates:
        if g[0] == 'add':
            x = col.get(g[2])
            if x:
                y = col.get(g[1], 0) + coef(g) * x
                if y:
                    col[g[1]] = y
                else:
                    col.pop(g[1], None)
        elif g[0] == 'scale':
            if g[1] in col:
                col[g[1]] *= coef(g)
        else:
            raise AuditError('unknown gate ' + str(g[0]))
    return col


def inverse(gates, col):
    for g in reversed(gates):
        if g[0] == 'add':
            x = col.get(g[2])
            if x:
                y = col.get(g[1], 0) - coef(g) * x
                if y:
                    col[g[1]] = y
                else:
                    col.pop(g[1], None)
        elif g[1] in col:
            col[g[1]] /= coef(g)
    return col


def parts(w):
    early = w.get('early_cleanup', [])
    ids = [i for i, _ in early]
    need(len(ids) == len(set(ids)), 'duplicate early-cleanup index')
    tail = [list(w['cleanup'][i][:-1]) + [U] for i, U in early]
    cleanup = [g for i, g in enumerate(w['cleanup']) if i not in set(ids)]
    return w['precondition'], w['A'] + w['cut'] + w['B'], tail, cleanup


def endpoint(w):
    v, R = w['report']['v'], w['report']['R']
    n = 2 * v + R
    pre, main, tail, cleanup = parts(w)
    for g in pre + main + tail + cleanup:
        need(all(0 <= r < n for r in regs(g)), 'register out of range')
        need(g[0] != 'add' or g[1] != g[2], 'self add')
        q = coef(g)
        need(q != 0 and q.denominator & (q.denominator - 1) == 0, 'non-dyadic or zero scalar')
    need(all(v <= r < 2 * v for g in pre for r in regs(g)), 'precondition touches a non-target')
    full, post = pre + main + tail + cleanup, main + tail + cleanup
    entering = {int(k) for k in w.get('start_extra', {})}
    bad, residue = [], 0
    for c in range(2 * v):
        want = {c: Q(1)}
        if c < v:
            want[v + c] = Q(1)
        if forward(full, {c: Q(1)}) != want:
            bad.append(('data', c))
    for k in range(2 * v, n):
        out = inverse(post, {k: Q(1)})
        rest = {r: x for r, x in out.items() if r != k}
        if out.get(k) != 1 or any(not v <= r < 2 * v for r in rest):
            bad.append(('helper', k))
        elif rest and k in entering:
            bad.append(('entering-response', k))
        residue += len(rest)
    need(not bad, 'endpoint failures %s' % bad[:6])
    return dict(columns=n, data_columns=2 * v, helper_columns=R, target_residue_entries=residue)


# ------------------------------------------------------------------ frames

def span(vectors):
    piv = {}
    for x in vectors:
        need(type(x) is int and x >= 0, 'bad frame vector')
        while x:
            b = x.bit_length() - 1
            if b in piv:
                x ^= piv[b]
            else:
                piv[b] = x
                break
    for b in sorted(piv):
        for u in piv:
            if u > b and piv[u] >> b & 1:
                piv[u] ^= piv[b]
    return frozenset(piv.values())


def frames(w):
    v, h, R = w['report']['v'], w['report']['h'], w['report']['R']
    n = 2 * v + R
    FULL = span([1 << i for i in range(h)])
    hyper = lambda p: span([x for x in range(1, 1 << h) if bin(x & p).count('1') % 2 == 0])
    cur = [span([p]) for p in w['ports']] + [span([])] * (v + R)
    for q, U in w.get('start_extra', {}).items():
        need(2 * v <= int(q) < n, 'entrance on a non-helper')
        cur[int(q)] = span(U)
    start = list(cur)
    end = [FULL] * v + [hyper(p) for p in w['ports']] + [FULL] * R
    for q, U in w.get('helper_final', {}).items():
        end[int(q)] = span(U)
    paid = Counter()

    def climb(r, U, where):
        U = U if isinstance(U, frozenset) else span(U)
        need(span(list(cur[r]) + list(U)) == U, 'non-monotone climb in %s, register %d' % (where, r))
        if len(U) > len(cur[r]):
            paid[len(U) - len(cur[r])] += 1
        cur[r] = U

    pre, main, tail, cleanup = parts(w)
    for g in w['A']:
        for r in regs(g):
            climb(r, g[-1], 'A')
    need(not w.get('target_levels'), 'nonzero target levels are outside this audit')
    need(all(cur[v + t] == span([]) for t in range(v)), 'targets not at level zero before B')
    for q, U in zip(w['centers'], w['center_frames']):
        need(cur[q] == span(U), 'centre carrier frame')
        paid[len(span(U))] += 1
    for g in w['B']:
        for r in regs(g):
            climb(r, g[-1], 'B')
    for g in tail:
        for r in regs(g):
            climb(r, g[-1], 'tail')
    for r in range(n):
        climb(r, end[r], 'end')
    need(all(end[r] == FULL for g in cleanup for r in regs(g)), 'FULL cleanup touches a low end')
    paid = {k: paid[k] for k in sorted(paid)}
    need(paid == {int(k): x for k, x in w['report']['local_profile'].items()}, 'paid profile differs from the recorded profile')
    return paid


# ------------------------------------------------------------------ leaver cells

def cell_targets(cells, tri):
    out = {}
    for tr in tri['triangles']:
        if tr.get('coded'):
            c = cells[tr['cell']]
            t8 = {r[0] for r in tr['reads']}
            need({b[1] - 8 for b in c['bindings'].values() if b[0] == 'target'} == t8, 'TRI/coded index mismatch ' + c['cell'])
            out[c['cell']] = t8
    need(len(out) == len(cells), 'a coded cell lacks a TRI entry')
    return out


def locate(w, cells, targets):
    v = w['report']['v']
    main = w['A'] + w['cut'] + w['B']
    found = []
    for cell in cells:
        pat = [(t, s, Q(q)) for t, s, q in cell['scaled']]
        T = {v + t for t in targets[cell['cell']]}
        hits = []
        for i in range(len(main) - len(pat) + 1):
            bind, ok = {}, True
            for k, (tn, sn, q) in enumerate(pat):
                g = main[i + k]
                if g[0] != 'add' or Q(g[3], g[4]) != q:
                    ok = False
                    break
                for name, reg in ((tn, g[1]), (sn, g[2])):
                    if bind.setdefault(name, reg) != reg or (name[0] == 'y') != (reg in T):
                        ok = False
                if not ok:
                    break
            if ok and len(set(bind.values())) == len(bind):
                hits.append((i, bind))
        need(len(hits) == 1, 'cell %s located %d times' % (cell['cell'], len(hits)))
        i, bind = hits[0]
        need({bind[x] for x in bind if x[0] == 'y'} == T, 'cell %s target set' % cell['cell'])
        found.append(dict(cell=cell['cell'], start=i, stop=i + len(pat), bind=bind,
                          leavers=sorted({bind[t] for t, s, q in pat if t[0] == 'x'})))
    ivals = sorted((c['start'], c['stop']) for c in found)
    need(all(a[1] <= b[0] for a, b in zip(ivals, ivals[1:])), 'overlapping cells')
    return found


def premise(w, found):
    v, R = w['report']['v'], w['report']['R']
    pre, main, tail, cleanup = parts(w)
    special = set(w['centers']) | {int(k) for k in w.get('start_extra', {})} | {int(k) for k in w.get('helper_final', {})}
    tail_regs = {r for g in tail for r in regs(g)}
    rows = []
    for c in found:
        for r in c['leavers']:
            need(r not in special, 'leaver %d is a centre, entering or low-ended register' % r)
            later = [j for j in range(c['stop'], len(main)) if r in regs(main[j])]
            need(not later, 'leaver %d touched in main after its cell (index %d)' % (r, later[0] if later else -1))
            need(r not in tail_regs, 'leaver %d touched in the early-cleanup tail' % r)
            writes = [j for j, g in enumerate(cleanup) if g[1] == r]
            need(writes, 'leaver %d is never written in the FULL cleanup' % r)
            rows.append(dict(cell=c['cell'], register=r, kind='data' if r < v else 'helper',
                             first_full_cleanup_write=writes[0], full_cleanup_writes=len(writes)))
    # value after precondition + main, as a linear form in the inputs
    want = {row['register'] for row in rows}
    form = {r: {r: Q(1)} for r in range(2 * v + R)}
    for g in pre + main:
        if g[0] == 'add':
            dst, q = form[g[1]], coef(g)
            for k, x in form[g[2]].items():
                y = dst.get(k, 0) + q * x
                if y:
                    dst[k] = y
                else:
                    dst.pop(k, None)
        else:
            form[g[1]] = {k: x * coef(g) for k, x in form[g[1]].items()}
    need(all(form[r] != {r: Q(1)} for r in want), 'a leaver holds its input value at the end of B')
    return rows


def audit_word(w, cells, targets):
    found = locate(w, cells, targets)
    rows = premise(w, found)
    return found, dict(R=w['report']['R'], paid_profile=frames(w), endpoint=endpoint(w),
                       cells=[dict(cell=c['cell'], main_index=c['start'], leavers=c['leavers']) for c in found],
                       leavers=rows)


# ------------------------------------------------------------------ negative controls

def controls(w, found, cells, targets):
    by = {c['cell']: c for c in cells}
    nA, nC = len(w['A']), len(w['cut'])
    c0 = found[0]
    pat = by[c0['cell']]['scaled']
    r0 = c0['leavers'][0]

    def at(i):
        return ('A', i) if i < nA else (('cut', i - nA) if i < nA + nC else ('B', i - nA - nC))

    def outcome(name, m, expect):
        for check, fn in (('endpoint', lambda: endpoint(m)), ('frames', lambda: frames(m)),
                          ('premise', lambda: premise(m, found))):
            try:
                fn()
            except AuditError as e:
                need(check == expect, 'control %s rejected by %s, expected %s: %s' % (name, check, expect, e))
                return name, '%s: %s' % (check, str(e)[:70])
        raise SystemExit('CONTROL ACCEPTED: ' + name)

    out = []
    h = w['report']['h']
    FULLF = [1 << j for j in range(h)]
    kx = next(k for k, (t, s, q) in enumerate(pat) if t[0] == 'x')
    m = copy.deepcopy(w); sec, i = at(c0['start'] + kx); del m[sec][i]
    out.append(outcome('N1_drop_leaver_write', m, 'endpoint'))
    early = {i for i, _ in w.get('early_cleanup', [])}
    k = next(i for i, g in enumerate(w['cleanup']) if i not in early and g[1] == r0)
    m = copy.deepcopy(w); del m['cleanup'][k]
    m['early_cleanup'] = [[i - (i > k), U] for i, U in w.get('early_cleanup', [])]
    out.append(outcome('N2_drop_full_cleanup_restore', m, 'endpoint'))
    # A semantically neutral pair at FULL: only the premise check can see it.
    pre, main, tail, cleanup = parts(w)
    busy = {r for g in tail for r in regs(g)} | set(w['centers']) | {int(q) for q in w.get('helper_final', {})}
    v, R = w['report']['v'], w['report']['R']
    hh = max(r for r in range(2 * v, 2 * v + R) if r not in busy)
    m = copy.deepcopy(w); m['B'] += [['add', hh, r0, 1, 2, FULLF], ['add', hh, r0, -1, 2, FULLF]]
    out.append(outcome('N3_neutral_touch_of_leaver_after_cell', m, 'premise'))
    m = copy.deepcopy(w); sec, i = at(c0['start']); m[sec][i][3] *= 3
    out.append(outcome('N4_wrong_cell_coefficient', m, 'endpoint'))
    xn = pat[kx][0]
    kr = next(k for k, (t, s, q) in enumerate(pat) if k > kx and s == xn)
    m = copy.deepcopy(w); a, b = at(c0['start'] + kx), at(c0['start'] + kr)
    need(a[0] == b[0], 'control N5 spans sections')
    m[a[0]][a[1]], m[b[0]][b[1]] = m[b[0]][b[1]], m[a[0]][a[1]]
    out.append(outcome('N5_leaver_write_after_its_read', m, 'endpoint'))
    y = next(b for nm, b in c0['bind'].items() if nm[0] == 'y')
    e = min(int(q) for q in w['start_extra'])
    m = copy.deepcopy(w); m['B'].insert(0, ['add', y, e, 1, 1, FULLF])
    out.append(outcome('N6_entering_dirt_into_cell_target', m, 'endpoint'))
    m = copy.deepcopy(w); sec, i = at(c0['start'] + kx); m[sec][i][-1] = []
    out.append(outcome('N7_leaver_gate_below_current_frame', m, 'frames'))
    return dict(out)


# ------------------------------------------------------------------ driver

def delta(a, b):
    return {r: a.get(r, 0) - b.get(r, 0) for r in sorted(set(a) | set(b)) if a.get(r, 0) != b.get(r, 0)}


def scale(u, s):
    return {r: s * x for r, x in u.items()}


def run():
    cells = read_pinned('CODED-CELLS-k8.json')
    targets = cell_targets(cells, read_pinned('TRI-LEAVER-k8.json'))
    words = {name: read_pinned(f) for name, f in [('cell', 'k8-cell-word.json.gz'), ('final', 'k8-final-word.json.gz'),
                                                   ('seven_slot', 'k8-seven-slot-word.json.gz')]}
    res = dict(status=None, audited={}, controls={})
    keep = {}
    for name, w in words.items():
        found, res['audited'][name] = audit_word(w, cells, targets)
        res['audited'][name]['content_sha256'] = PINS[{'cell': 'k8-cell-word.json.gz', 'final': 'k8-final-word.json.gz', 'seven_slot': 'k8-seven-slot-word.json.gz'}[name]]
        keep[name] = found
        print('PASS', name, res['audited'][name]['paid_profile'], flush=True)
    for name in ('final', 'seven_slot'):
        res['controls'][name] = controls(words[name], keep[name], cells, targets)
        print('PASS controls', name, len(res['controls'][name]), flush=True)
    # Face events: data-register leavers receive one B-section write in both the base and the cell word.
    base = read_pinned('notri-cold44-word.json.gz')
    v = base['report']['v']
    data_leavers = sorted(r for c in keep['cell'] for r in c['leavers'] if r < v)
    def bwrites(w):
        return {x: [[g[2], str(coef(g))] for g in w['B'] if g[0] == 'add' and g[1] == x] for x in data_leavers}
    wb, wc = bwrites(base), bwrites(words['cell'])
    need(all(len(wb[x]) == 1 and len(wc[x]) == 1 for x in data_leavers), 'a data leaver lacks exactly one B write')
    awrites = lambda w: [[g[1], g[2], str(coef(g))] for g in w['A'] if g[0] == 'add' and g[1] in data_leavers]
    need(awrites(base) == awrites(words['cell']), 'A-section writes to data leavers changed')
    res['face_events'] = dict(data_leavers=data_leavers, base_B_write=wb, cell_B_write=wc,
                              repaired=[x for x in data_leavers if wb[x] != wc[x]])
    # Profile deltas.
    raw = {k: read_pinned(f) for k, f in [('notri', 'raw-notri.json.gz'), ('k5', 'raw-k5.json.gz'), ('k8', 'raw-k8.json.gz')]}
    P = {k: frames(w) for k, w in raw.items()}
    d5, d3 = delta(P['k5'], P['notri']), delta(P['k8'], P['k5'])
    unit = {r: x // 5 for r, x in d5.items()}
    need(scale(unit, 5) == d5 and scale(unit, 3) == d3, 'raw per-cell deltas are not additive')
    need(raw['notri']['report']['R'] - raw['k5']['report']['R'] == 15 and raw['k5']['report']['R'] - raw['k8']['report']['R'] == 9, 'helper counts')
    claimed = {1: -30, 2: 6, 3: 6}
    slot = delta(res['audited']['seven_slot']['paid_profile'], res['audited']['final']['paid_profile'])
    need(slot == scale({3: 2, 4: -4, 5: 2}, 7), 'seven-slot delta is not 7 x {3:+2,4:-4,5:+2}')
    res['profile_deltas'] = dict(raw_profiles={k: P[k] for k in P}, k5_minus_notri=d5, k8_minus_k5=d3,
                                 per_cell_raw=unit, helpers_removed_per_cell=3,
                                 pr_description_per_cell=claimed, matches_pr_description=unit == claimed,
                                 rank_mass_per_cell_raw=sum(r * x for r, x in unit.items()),
                                 seven_slot_minus_final=slot)
    res['status'] = 'PASS_INDEPENDENT_MUTABLE_LEAVER_AUDIT'
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true', help='write RESULT.json instead of comparing with it')
    a = ap.parse_args()
    try:
        res = run()
    except AuditError as e:
        print('FAIL', e)
        sys.exit(1)
    text = json.dumps(res, indent=1, sort_keys=True) + '\n'
    if a.write:
        (HERE / 'RESULT.json').write_text(text)
    else:
        need((HERE / 'RESULT.json').read_text() == text, 'result differs from committed RESULT.json')
    d = res['profile_deltas']
    print('%s cells=8 leavers=%d columns=%d controls=%d per_cell_raw=%s claimed_match=%s' % (
        res['status'], len(res['audited']['final']['leavers']), res['audited']['final']['endpoint']['columns'],
        sum(map(len, res['controls'].values())), d['per_cell_raw'], d['matches_pr_description']))
