#!/usr/bin/env python3
"""Derive PR540's hand-supplied pending ranges from PR442's bit schedule and geometry.

PR540 (`PhysicalSourceConnection.pendingTag`, head acc19170) states that idle
child 1 owns pending axes [15,22) and child 2 owns [1,29) in the selected
invocation (stage 2, replica 0, pair 0). Lean checks only that these ranges
contain the hosted target masks. This script derives the ranges from the source
schedule instead, with standard-library code that imports nothing from PR442,
PR434 or PR540.

  1. Bind the hosted template to PR442's EXPECTED.json on main, and bind the
     geometry to the template.
  2. Read the exterior 7-block layout from every port route. Check every chart
     [q/2 | A_q] as an exact orthogonal matrix, so axis 0 is span(q) and axes
     1..7 are q-perp.
  3. Level model (PR386 geometry: rho_(s,q) sends (P_q,E_s) to (I_8,E_(s-1))):
     L_-1 = span(q) = {0} and L_l = Q^8 + E_1..E_l = [0, 8+7l) in chart axes.
     Every idle event's rank must equal dim L_b - dim L_a.
  4. The pending set of a child a->b is L_b minus L_a. Recompute the windows
     from the schedule, then map each hosted route (child, off, w) of the
     selected call to axes pending[off:off+w].
  5. Require PR540's ranges to equal the derived pending sets, not merely
     contain the targets. Six mutations must be rejected.

Douglas Colkitt, with Claude (Anthropic) assistance. Apache-2.0.
"""
import gzip, hashlib, json, sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {  # compressed sha256; byte-identical to PR540 research/lean-multi-host-source/inputs/
    'hosted-template.json.gz': '6e18a9ce240229c34556ba43fd6ec28f83200dfcf85e5584d4a670aeb605aeb0',
    'geometry.json.gz': 'c2bdd236e44fb868e4d2260b1fd7820aa7a565119532781904ebff90b9e852d7',
}
# Literal constants of PR540 PhysicalSourceConnection.pendingTag (blob 9a78d48f at head acc19170)
LEAN_PENDING = {1: range(15, 22), 2: range(1, 29)}
SELECTED = dict(stage=2, replica=0, pair=0, orientation='forward')
H, M, BLOCK = 8, 64, 7


class Reject(Exception):
    pass


def require(ok, why):
    if not ok:
        raise Reject(why)


def load():
    raw = {}
    for name, pin in PINS.items():
        b = (HERE / 'inputs' / name).read_bytes()
        require(hashlib.sha256(b).hexdigest() == pin, f'pin {name}')
        raw[name] = gzip.decompress(b)
    expected = json.loads((ROOT / 'research/idle-axis-hosting/EXPECTED.json').read_text())
    require(hashlib.sha256(raw['hosted-template.json.gz']).hexdigest() == expected['bit_template_sha256'],
            'template is not PR442 bit_template_sha256')
    t = json.loads(raw['hosted-template.json.gz'])
    require(hashlib.sha256(raw['geometry.json.gz']).hexdigest() == t['geometry_sha256'], 'geometry not bound by template')
    return t, json.loads(raw['geometry.json.gz'])


def exterior_blocks(geo):
    """Exterior block l from the stage-l route axes of every port (stage 0: local block only)."""
    require((geo['h'], geo['m'], geo['stages']) == (H, M, 9), 'h, m, stages')
    blocks = {}
    for port in geo['ports']:
        for r in port['routes']:
            s, ax = r['stage'], r['axes']
            require(ax[:H] == list(range(H)), 'route must contain the local block')
            ext = ax[H:]
            if s == 0:
                require(ext == [] and r.get('identity'), 'stage-0 route is the identity')
                continue
            require(len(ext) == BLOCK, 'exterior block width')
            require(blocks.setdefault(s, ext) == ext, 'ports disagree on exterior block')
    require(sorted(blocks) == list(range(1, 9)), 'exterior blocks 1..8')
    require(sorted(a for b in blocks.values() for a in b) == list(range(H, M)), 'blocks partition axes 8..63')
    require(all(blocks[s] == list(range(H + BLOCK * (s - 1), H + BLOCK * s)) for s in blocks), 'block order')
    return blocks


def check_charts(geo):
    """[q/2 | A_q] is exactly orthogonal: axis 0 <-> span(q), axes 1..7 <-> q-perp (form I_8/2 rescaled)."""
    require(len(geo['ports']) == 120, '120 ports')
    for port in geo['ports']:
        q = [Q(x) for x in port['q']]
        A = [[Q(x) for x in row] for row in port['complement_columns']]
        require(len(A) == H and all(len(row) == BLOCK for row in A), 'A_q shape')
        cols = [[x / 2 for x in q]] + [[A[i][j] for i in range(H)] for j in range(BLOCK)]
        for i in range(H):
            for j in range(H):
                require(sum(a * b for a, b in zip(cols[i], cols[j])) == (1 if i == j else 0),
                        f'port {port["port"]} chart not orthogonal')
    return True


def level(l, blocks):
    """Chart axes of data level l. L_-1 = span(q) = axis 0; L_l = local block + E_1..E_l."""
    if l == -1:
        return {0}
    return set(range(H)) | {a for s in range(1, l + 1) for a in blocks[s]}


def pending_sets(t, blocks, level_fn=level):
    idle = [e for e in t['schedule'] if e['kind'] == 'idle']
    require([e['idx'] for e in idle] == list(range(len(idle))), 'idle indices')
    out = {}
    for e in idle:
        lo, hi = level_fn(e['source_level'], blocks), level_fn(e['target_level'], blocks)
        require(lo <= hi, 'levels nested')
        require(len(hi) - len(lo) == e['rank'], f'idle {e["idx"]} rank {e["rank"]} != dim difference')
        out[e['idx']] = dict(pair=e['pair'], levels=(e['source_level'], e['target_level']), axes=sorted(hi - lo))
    return out


def windows(schedule):
    """Stages of local invocations strictly between the pair's last local/bridge touch and its idle child."""
    last, done, out = {}, [], {}
    for pos, e in enumerate(schedule):
        if e['kind'] == 'local_cover_sweep':
            done.append((pos, e['stage'], e['pair'])); last[e['pair']] = pos
        elif e['kind'] == 'bridge':
            last[e['dst']] = last[e['src']] = pos
        elif e['kind'] == 'idle':
            lo = last.get(e['pair'], -1)
            out[e['idx']] = {s for p_, s, pr in done if lo < p_ < pos and pr != e['pair']}
    return out


def derive(t, geo, lean=LEAN_PENDING, level_fn=level, routes=None, win_fn=windows):
    blocks = exterior_blocks(geo)
    check_charts(geo)
    pend = pending_sets(t, blocks, level_fn)
    win = win_fn(t['schedule'])
    calls = [c for c in t['calls'] if all(c[k] == v for k, v in SELECTED.items())]
    require(len(calls) == 1, 'selected call unique')
    owners = calls[0]['owners']
    require(len(owners) == 987, '987 roles')
    routes = routes if routes is not None else [o[1] for o in owners[240:]]
    used = {}
    for r in routes:
        if r[0] != 'hosted':
            continue
        _, child, off, w = r
        require(SELECTED['stage'] in win[child], f'stage 2 outside window of child {child}')
        require(pend[child]['pair'] != SELECTED['pair'], 'host pair is active')
        require(0 <= off and off + w <= len(pend[child]['axes']), f'route {r} exceeds pending rank')
        axes = pend[child]['axes'][off:off + w]
        lean_axes = list(range(lean[child].start + off, lean[child].start + off + w))
        require(axes == lean_axes, f'route {r}: derived {axes} != Lean {lean_axes}')
        used.setdefault(child, set()).update(axes)
    require(sorted(used) == sorted(lean), 'hosted children differ from Lean tags')
    for child, rng in lean.items():
        require(list(rng) == pend[child]['axes'], f'Lean range of child {child} != derived pending set')
        require(used[child] <= set(rng), 'target outside pending range')
    return dict(
        exterior_blocks={str(s): [b[0], b[-1] + 1] for s, b in sorted(blocks.items())},
        hosted_children={str(c): dict(pair=pend[c]['pair'], levels=list(pend[c]['levels']),
                                      window_stages=sorted(win[c]),
                                      derived_pending_axes=[pend[c]['axes'][0], pend[c]['axes'][-1] + 1],
                                      lean_range=[lean[c].start, lean[c].stop],
                                      hosted_axes_used=len(used[c]),
                                      pending_rank=len(pend[c]['axes'])) for c in sorted(lean)},
        idle_ranks_checked=len(pend),
        hosted_routes=sum(1 for r in routes if r[0] == 'hosted'),
        ports_checked=len(geo['ports']))


def controls(t, geo):
    owners = next(c for c in t['calls'] if all(c[k] == v for k, v in SELECTED.items()))['owners']
    base = [o[1] for o in owners[240:]]
    def shifted_off(rs):
        out = [list(r) for r in rs]
        i = next(i for i, r in enumerate(out) if r[0] == 'hosted' and r[1] == 1)
        out[i][2] += 1
        return out
    def no_stage2(s):
        w = windows(s); w[1] = w[1] - {2}; return w
    cases = {
        'child1_previous_level_block': dict(lean={1: range(8, 15), 2: range(1, 29)}),
        'child2_includes_q_axis': dict(lean={1: range(15, 22), 2: range(0, 28)}),
        'children_swapped': dict(lean={1: range(1, 29), 2: range(15, 22)}),
        'level_minus_one_empty': dict(level_fn=lambda l, b: set() if l == -1 else level(l, b)),
        'route_offset_past_rank': dict(routes=shifted_off(base)),
        'stage2_outside_window': dict(win_fn=no_stage2),
    }
    out = {}
    for name, kw in cases.items():
        try:
            derive(t, geo, **kw)
            out[name] = 'ACCEPTED'
        except Reject as e:
            out[name] = 'rejected: ' + str(e)
    require(all(v.startswith('rejected') for v in out.values()), f'control accepted: {out}')
    return out


def main():
    t, geo = load()
    result = dict(status='PASS_PR540_PENDING_RANGES_DERIVED_FROM_PR442_SCHEDULE',
                  selected_call=SELECTED, **derive(t, geo), controls=controls(t, geo),
                  scope='Python derivation from the source schedule and geometry. Not kernel checked. The level model '
                        'L_-1=span(q), L_l=Q^8+E_1..E_l is PR386 geometry, checked here against every idle rank and '
                        'route; the ascending order of pending axes within a child is the shared offset convention.')
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if len(sys.argv) > 1 and sys.argv[1] == '--write':
        (HERE / 'RESULT.json').write_text(text)
    else:
        require((HERE / 'RESULT.json').read_text() == text, 'RESULT.json differs')
    print(result['status'])


if __name__ == '__main__':
    try:
        main()
    except Reject as e:
        print('FAIL:', e); sys.exit(1)
