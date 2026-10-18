#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Josie Elliston, prepared with substantial assistance from Anthropic Claude (Claude Code).
"""Independent owner-map audit of the open seven-slot k8 T8/T16 kappa claims.

Standard library only. Nothing from the audited packages is imported or run.
Their owner maps, plans and specs are read as git blobs at pinned ids
(SOURCES.json). The source-event stream, the idle-child geometry and the
helper widths come from three pinned inputs:

  * main's vendored ROUND20 parent template (30 source events per replica);
  * main's PR558 DATA-PHASES.json (pending axes of each idle child);
  * the seven-slot word c2b29430..., copied from #1049.

For every claim, the rules of research/complex-double-replica-owners/PROOF.md
are re-implemented from that text:

  R1  calls: T*9 complete invocations; the order is the stated interleave and
      every replica sees its 30 source events in order.
  R2  each invocation hosts helpers 0..R-1 exactly once, at the word's width.
  R3  physical family identity owner*896 + (2*pair+side)*112 + port, inside
      the live data namespace, and not the invocation's own active pair.
  R4  at most one helper per physical family per invocation.
  R5  the invocation is strictly inside the owner's actual window, from the
      last touch of the pair (local sweep or bridge end) to the idle sweep.
  R6  slices lie inside the child's rank and are disjoint per (owner, child,
      port); occupied cells form a prefix.
  R7  the idle remainders and the whole profile are recounted and compared
      with SPEC/PLAN/RESULT; rank mass is 73*live - 320*T.

Two further checks are not in the audited checkers:

  X1  the windows are rebuilt from the event stream and compared with the
      committed PLAN windows (and the T8 builder against the T8 PLAN);
  X2  pending axes of distinct idle children of one physical family are
      disjoint, so a family's hosts on different children never share a cell.

Chart/route construction, the local word's own admission, invoices, prices
and every inherited interface are out of scope.
"""
import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
V, H, M, L, PAIRS = 112, 9, 73, 9, 4
FAMILIES_PER_REPLICA = 2 * PAIRS * V  # 896

TEMPLATE = 'research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor535/inputs/ROUND20-PARENT-TEMPLATE.json.gz'
PHASES = 'research/community-k492-audit/pr622/replay/baseline558/complex-global/base/work/complex-nine-native/DATA-PHASES.json'
WORD = HERE / 'inputs/k8-seven-slot-word.json.gz'


class Reject(Exception):
    pass


def need(ok, rule, msg):
    if not ok:
        raise Reject(f'{rule}: {msg}')


def load(raw, name):
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)


def blob(git, oid):
    return subprocess.run(['git', '-C', str(git), 'cat-file', 'blob', oid], check=True, capture_output=True).stdout


def sha(data):
    return hashlib.sha256(data).hexdigest()


def span(vectors):
    pivots = {}
    for x in vectors:
        while x:
            top = x.bit_length() - 1
            if top not in pivots:
                pivots[top] = x
                break
            x ^= pivots[top]
    return len(pivots)


# ---------------------------------------------------------------- geometry

def word_widths(word):
    """Residual width of each helper: span(final) - span(start)."""
    R = word['report']['R']
    full = [1 << i for i in range(H)]
    out = []
    for q in range(2 * V, 2 * V + R):
        end = span(word['helper_final'].get(str(q), full))
        start = span(word['start_extra'].get(str(q), []))
        need(0 < end - start <= H, 'word', f'helper register {q} width {end - start}')
        out.append(end - start)
    return out


def geometry(template, phases):
    """Per-stage source-event blocks, stage pairs and idle-child ranks/places."""
    events = template['execution_schedule']
    need([e['kind'] for e in events[30:]] == ['bank_padding_cover_sweep', 'translate_every_live_family'],
         'geometry', 'global tail')
    blocks, stage = defaultdict(list), None
    for index, e in enumerate(events[:30]):
        if e['kind'] == 'local_cover_sweep':
            need(e['stage'] == (stage + 1 if stage is not None else 0), 'geometry', 'stage order')
            stage = e['stage']
        need(stage is not None, 'geometry', 'event before first sweep')
        blocks[stage].append((index, e))
    need(sorted(blocks) == list(range(L)), 'geometry', 'nine stages')
    stage_pair = {e['stage']: e['pair'] for e in template['recipe'] if e['kind'] == 'local'}
    need(sorted(stage_pair) == list(range(L)), 'geometry', 'recipe stages')
    place = {}
    for e in events[:30]:
        if e['kind'] == 'idle_cover_sweep':
            need(len(e['child_indices']) == 2, 'geometry', 'two sides per idle sweep')
            for side, child in enumerate(e['child_indices']):
                need(child not in place, 'geometry', 'child swept twice')
                place[child] = (e['pair'], side)
    # Ranks and axes from DATA-PHASES, uniform over ports.
    axes = defaultdict(dict)
    for recipe in phases['recipes']:
        for child, item in enumerate(recipe['idle_children']) if isinstance(recipe['idle_children'], list) \
                else ((int(k), v) for k, v in recipe['idle_children'].items()):
            axes[child][recipe['port']] = [int(x) for x in item['orthogonal_axes']]
    need(set(axes) == set(place), 'geometry', 'phase children equal swept children')
    rank = {}
    for child, per_port in axes.items():
        need(sorted(per_port) == list(range(V)), 'geometry', 'phase ports')
        sizes = {len(a) for a in per_port.values()}
        need(len(sizes) == 1, 'geometry', f'child {child} rank varies by port')
        rank[child] = sizes.pop()
    # X2: distinct children on one (pair, side) have disjoint pending axes.
    by_family = defaultdict(list)
    for child, where in place.items():
        if rank[child]:
            by_family[where].append(child)
    x2 = 0
    for where, children in by_family.items():
        for port in range(V):
            seen = set()
            for child in children:
                a = axes[child][port]
                need(len(set(a)) == len(a) and not seen & set(a), 'X2', f'children {children} share axes at port {port}')
                seen |= set(a)
                x2 += 1
    positive = {c: r for c, r in rank.items() if r}
    return dict(blocks=blocks, stage_pair=stage_pair, place=place, rank=positive, x2_child_ports=x2)


def windows(geo, order):
    """Actual windows {(replica, child): (lo, hi)} and call positions."""
    pos, callpos, last, span_ = 0, {}, {}, {}
    seen = defaultdict(list)
    for stage, replica in order:
        for index, e in geo['blocks'][stage]:
            seen[replica].append(index)
            kind = e['kind']
            if kind == 'local_cover_sweep':
                callpos[stage, replica] = pos
                last[replica, geo['stage_pair'][stage]] = pos
            elif kind == 'bridge':
                last[replica, e['src']] = last[replica, e['dst']] = pos
            elif kind == 'idle_cover_sweep':
                for child in e['child_indices']:
                    if child in geo['rank']:
                        span_[replica, child] = (last.get((replica, e['pair']), -1), pos)
            pos += 1
    need(all(s == list(range(30)) for s in seen.values()), 'R1', 'per-replica source-event projection')
    return span_, callpos


# ---------------------------------------------------------------- one claim

def audit(geo, widths, local_profile, roles, plan, expected_idle, T):
    R = len(widths)
    live = T * FAMILIES_PER_REPLICA
    rank, place, stage_pair = geo['rank'], geo['place'], geo['stage_pair']
    need(len(roles) == L * T * R, 'R1', 'role count')
    at = {}
    for z in roles:
        key = (z['stage'], z['replica'])
        need(at.setdefault(z['time'], key) == key, 'R1', 'time names two invocations')
    need(sorted(at) == list(range(L * T)), 'R1', 'contiguous times')
    order = [at[t] for t in range(L * T)]
    need(set(order) == {(s, r) for s in range(L) for r in range(T)}, 'R1', 'stage/replica inventory')
    need([tuple(x) for x in plan['order']] == order, 'R1', 'role order differs from PLAN order')
    if T == 16:
        need(all(order[2 * i + 1] == (order[2 * i][0], order[2 * i][1] + 8) and order[2 * i][1] < 8
                 for i in range(len(order) // 2)), 'R1', 'two-group interleave')
    span_, callpos = windows(geo, order)
    need(len(span_) == T * len(rank), 'R5', 'window inventory')
    # X1: committed PLAN windows equal the rebuilt ones.
    rebuilt = {f'{r},{c}': [rank[c], [t for t, key in enumerate(order) if lo < callpos[key] < hi]]
               for (r, c), (lo, hi) in span_.items()}
    need(rebuilt == plan['windows'], 'X1', 'committed PLAN windows differ from the event stream')

    hosted = defaultdict(set)
    families = defaultdict(set)
    cells = defaultdict(set)
    for z in roles:
        call = (z['stage'], z['replica'])
        helper, owner, child, port = z['helper'], z['owner_replica'], z['child'], z['port']
        offset, width, family = z['offset'], z['width'], z['family']
        need(0 <= helper < R and helper not in hosted[call], 'R2', f'helper {helper} repeated or invalid in {call}')
        hosted[call].add(helper)
        need(width == widths[helper], 'R2', f'helper {helper} width {width} != {widths[helper]}')
        need(0 <= owner < T and 0 <= port < V and child in rank, 'R3', 'role coordinates')
        pair, side = place[child]
        need(family == owner * FAMILIES_PER_REPLICA + (2 * pair + side) * V + port
             and z['copy'] == owner * V + port, 'R3', 'physical family identity')
        need(0 <= family < live, 'R3', 'family outside live data namespace')
        need((owner, pair) != (call[1], stage_pair[call[0]]), 'R3', 'helper hosted on the active data pair')
        need(family not in families[call], 'R4', f'family {family} hosts two helpers in {call}')
        families[call].add(family)
        lo, hi = span_[owner, child]
        need(lo < callpos[call] < hi, 'R5', f'{call} outside window of replica {owner} child {child}')
        new = set(range(offset, offset + width))
        need(offset >= 0 and offset + width <= rank[child], 'R6', 'slice exceeds child rank')
        need(not cells[owner, child, port] & new, 'R6', 'overlapping slices')
        cells[owner, child, port] |= new
    need(all(hosted[call] == set(range(R)) for call in order), 'R2', 'incomplete helper inventory')
    idle = Counter()
    for (owner, child) in span_:
        for port in range(V):
            used = cells[owner, child, port]
            need(used == set(range(len(used))), 'R6', 'gap in occupied prefix')
            if rank[child] > len(used):
                idle[rank[child] - len(used)] += 1
    need(idle == expected_idle, 'R7', f'idle profile {dict(sorted(idle.items()))} != claimed')
    profile = Counter({r: L * T * n for r, n in local_profile.items()})
    profile.update(idle)
    mass = sum(r * n for r, n in profile.items())
    need(M * live - mass == 320 * T, 'R7', 'rank deficit')
    need(max(profile) ** 2 * 2 < M * M, 'R7', 'halving guard')
    return dict(idle=dict(sorted(idle.items())), profile=dict(sorted(profile.items())), rank_mass=mass,
                deficit=M * live - mass, calls=len(order), roles=len(roles), windows=len(span_),
                cross_replica_roles=sum(z['owner_replica'] != z['replica'] for z in roles))


def as_profile(d):
    return Counter({int(k): v for k, v in d.items()})


# ---------------------------------------------------------------- controls

def controls(geo, widths, local_profile, roles, plan, expected_idle, T):
    """Each mutant must be rejected by the rule it targets."""
    rank, place = geo['rank'], geo['place']
    span_, callpos = windows(geo, [tuple(x) for x in plan['order']])
    order = [tuple(x) for x in plan['order']]
    first = roles[0]
    out = []

    def expect(name, rule, mutant, idle=expected_idle):
        try:
            audit(geo, widths, local_profile, mutant, plan, idle, T)
        except Reject as e:
            need(str(e).startswith(rule + ':'), 'control', f'{name} rejected by {e} instead of {rule}')
            out.append(dict(name=name, rejected_by=rule))
            return
        raise Reject(f'control: accepted {name}')

    def swap(i, z):
        return roles[:i] + [z] + roles[i + 1:]

    expect('drop_role', 'R1', roles[1:])
    expect('narrow_width', 'R2', swap(0, dict(first, width=first['width'] - 1)))
    j = next(i for i, z in enumerate(roles) if z['time'] == first['time'] and z['helper'] != first['helper'])
    expect('duplicate_helper', 'R2', swap(j, dict(roles[j], helper=first['helper'])))
    expect('private_family', 'R3', swap(0, dict(first, family=T * FAMILIES_PER_REPLICA)))
    # A role whose family/copy are consistent but sits on the active pair.
    for i, z in enumerate(roles):
        s, r = z['stage'], z['replica']
        p = geo['stage_pair'][s]
        child = next(c for c, (pp, sd) in place.items() if pp == p and c in rank and (r, c) in span_)
        fam = r * FAMILIES_PER_REPLICA + (2 * p + place[child][1]) * V + z['port']
        expect('active_pair', 'R3', swap(i, dict(z, owner_replica=r, child=child, family=fam, copy=r * V + z['port'])))
        break
    # Two helpers of one invocation on the same family (second gets a fresh slice range).
    calls = defaultdict(list)
    for i, z in enumerate(roles):
        calls[z['time']].append(i)
    a, b = calls[first['time']][0], calls[first['time']][1]
    za, zb = roles[a], roles[b]
    expect('family_collision', 'R4', swap(b, dict(zb, owner_replica=za['owner_replica'], child=za['child'],
                                                  port=za['port'], family=za['family'], copy=za['copy'],
                                                  offset=za['offset'] + za['width'])))
    # Move a whole role to an invocation after its owner's idle sweep, keeping the helper index unique
    # by swapping times with the same helper there.
    for i, z in enumerate(roles):
        lo, hi = span_[z['owner_replica'], z['child']]
        later = next((key for key in order if callpos[key] > hi), None)
        if later is None:
            continue
        t2 = order.index(later)
        k = next(k for k in calls[t2] if roles[k]['helper'] == z['helper'])
        mutant = list(roles)
        mutant[i] = dict(z, stage=later[0], replica=later[1], time=t2)
        mutant[k] = dict(roles[k], stage=z['stage'], replica=z['replica'], time=z['time'])
        expect('past_idle_sweep', 'R5', mutant)
        break
    # Two slices of one bin overlapping in cells (different invocations, so R4 is silent).
    by_bin = defaultdict(list)
    for i, z in enumerate(roles):
        by_bin[z['owner_replica'], z['child'], z['port']].append(i)
    i, k = next(v for v in by_bin.values() if len(v) >= 2)[:2]
    expect('overlap', 'R6', swap(k, dict(roles[k], offset=roles[i]['offset'])))
    # Shift the last slice of some bin up by one inside capacity: a gap appears.
    for v in by_bin.values():
        top = max(v, key=lambda x: roles[x]['offset'])
        z = roles[top]
        if z['offset'] + z['width'] < rank[z['child']]:
            expect('prefix_gap', 'R6', swap(top, dict(z, offset=z['offset'] + 1)))
            break
    tampered = Counter(expected_idle)
    one = min(tampered)
    tampered[one] -= 1
    tampered[one + 1] += 1
    expect('claimed_idle_tampered', 'R7', roles, idle=+tampered)
    stale = dict(plan, windows=dict(plan['windows']))
    key = next(iter(stale['windows']))
    stale['windows'][key] = [stale['windows'][key][0], stale['windows'][key][1][:-1]]
    try:
        audit(geo, widths, local_profile, roles, stale, expected_idle, T)
    except Reject as e:
        need(str(e).startswith('X1:'), 'control', 'stale window rejected elsewhere')
        out.append(dict(name='plan_window_truncated', rejected_by='X1'))
    else:
        raise Reject('control: accepted plan_window_truncated')
    return out


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repo', type=Path, default=HERE.parent.parent, help='repository holding the pinned blobs')
    ap.add_argument('--fetch', action='store_true', help='fetch refs/pull/N/head for every claim first')
    ap.add_argument('--only', type=int, action='append', help='audit only these PR numbers')
    ap.add_argument('--write', action='store_true', help='rewrite RESULT.json instead of comparing with it')
    args = ap.parse_args()
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    repo = args.repo.resolve()

    pins = sources['inputs']
    tbytes, pbytes, wbytes = (repo / TEMPLATE).read_bytes(), (repo / PHASES).read_bytes(), WORD.read_bytes()
    need(sha(tbytes) == pins['template_sha256'], 'input', 'parent template hash')
    need(sha(pbytes) == pins['data_phases_sha256'], 'input', 'DATA-PHASES hash')
    need(sha(gzip.decompress(wbytes)) == pins['word_content_sha256'], 'input', 'seven-slot word content hash')
    template, phases, word = load(tbytes, TEMPLATE), load(pbytes, PHASES), load(wbytes, '.gz')
    geo = geometry(template, phases)
    widths = word_widths(word)
    local_profile = as_profile(word['report']['local_profile'])
    need(Counter(widths) == as_profile(word['report']['width_inventory']), 'word', 'width inventory')

    if args.fetch:
        for c in sources['claims']:
            subprocess.run(['git', '-C', str(repo), 'fetch', '-q', 'https://github.com/CrocSwap/integer-mult-bounds.git',
                            f'refs/pull/{c["pr"]}/head'], check=True)

    rows, receipt_controls, t8_done = [], {}, None
    for c in sources['claims']:
        if args.only and c['pr'] not in args.only:
            continue
        get = {name: load(blob(repo, oid), name) for name, oid in c['blobs'].items()}
        spec, plan = get['data/SPEC.json'], get['data/PLAN.json']
        if 'RESULT.json' in get:
            result = get['RESULT.json']
        else:  # #1082 ships CANDIDATE.json (kappa) and PROFILE.json instead of RESULT.json
            result = dict(kappa_decimal=get['CANDIDATE.json']['kappa'], profile=get['PROFILE.json'])
        need(spec['providers']['gauge44']['expected_profile'] == {str(k): v for k, v in sorted(local_profile.items())},
             'spec', f'#{c["pr"]} local profile differs from the word')
        need(Counter(widths) == as_profile(spec['providers']['gauge44']['inventory']), 'spec', 'width inventory')
        if t8_done is None and 'data/T8/OWNERS.json.gz' in get:
            # The shared T8 owner map (#1018) under the same rules, T = 8.
            t8 = audit(geo, widths, local_profile, get['data/T8/OWNERS.json.gz'], get['data/T8/PLAN.json'],
                       as_profile(get['data/SPEC-T8.json']['expected']['idle_remainder_profile']), 8)
            need(t8['profile'] == {int(k): v for k, v in get['data/T8/PLAN.json']['profile'].items()}, 'R7', 'T8 PLAN profile')
            t8_done = dict(owners_blob=c['blobs']['data/T8/OWNERS.json.gz'], **t8)
        roles = get['data/OWNERS.json.gz']
        r = audit(geo, widths, local_profile, roles, plan,
                  as_profile(spec['expected']['idle_remainder_profile']), 16)
        claimed = result.get('complex_profile', result.get('profile'))  # rohanarun packages use 'profile'
        need(r['profile'] == {int(k): v for k, v in claimed.items()}, 'R7', 'RESULT profile')
        need(r['profile'] == {int(k): v for k, v in plan['profile'].items()}, 'R7', 'PLAN profile')
        if 'idle_remainder_profile' in result:
            need(r['idle'] == {int(k): v for k, v in result['idle_remainder_profile'].items()}, 'R7', 'RESULT idle')
        need(r['cross_replica_roles'] == spec['expected'].get('cross_replica_helper_roles', r['cross_replica_roles']),
             'R7', 'cross-replica role count')
        if c['pr'] == sources['controls_on']:
            receipt_controls = controls(geo, widths, local_profile, roles, plan,
                                        as_profile(spec['expected']['idle_remainder_profile']), 16)
        rows.append(dict(pr=c['pr'], head=c['head'], kappa=result['kappa_decimal'], **r))
        print(f"PASS #{c['pr']} kappa={result['kappa_decimal']} idle={r['idle']}", flush=True)

    receipt = dict(
        status='PASS_INDEPENDENT_T16_OWNER_AUDIT',
        geometry=dict(source_events_per_replica=30, positive_children=len(geo['rank']),
                      child_ranks={str(c): geo['rank'][c] for c in sorted(geo['rank'])},
                      x2_disjoint_child_port_checks=geo['x2_child_ports']),
        word=dict(R=len(widths), width_inventory={str(k): v for k, v in sorted(Counter(widths).items())},
                  local_profile={str(k): v for k, v in sorted(local_profile.items())}),
        t8=t8_done, claims=rows, controls=receipt_controls)
    text = json.dumps(receipt, indent=1, default=lambda o: {str(k): v for k, v in o.items()}) + '\n'
    text = json.dumps(json.loads(text), indent=1) + '\n'
    target = HERE / 'RESULT.json'
    if args.write:
        target.write_text(text)
    elif not args.only:
        need(target.read_text() == text, 'receipt', 'RESULT.json differs from this run')
    print(f"PASS_INDEPENDENT_T16_OWNER_AUDIT claims={len(rows)} roles={sum(r['roles'] for r in rows)} "
          f"t8_roles={t8_done['roles'] if t8_done else 0} controls={len(receipt_controls)}")


if __name__ == '__main__':
    try:
        main()
    except Reject as e:
        sys.exit(f'FAIL {e}')
