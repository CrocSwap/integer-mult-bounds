#!/usr/bin/env python3
"""Dependency-respecting diagonal batching of rank-1 climbs in the selected gauge44 provider.

A rank-1 climb on register L r reads and writes only L r. It may therefore be moved past any event
that touches no L r, inside its own phase. This script moves rank-1 climbs (only those; every other
event keeps its relative order), groups them into disjoint batches of 16 on distinct destinations
by an earliest-deadline greedy, emits the reordered programs, and replays their frame semantics.

usage: batch.py LOCAL-PROGRAMS.json.gz CANONICAL-WORD.json.gz
Prepared for Josie Elliston with Claude (Anthropic) assistance. Apache-2.0.
"""
from __future__ import annotations

import collections
import gzip
import json
import sys

BATCH = 16


def touched(event):
    """Registers ('L', r) or ('C', k) that an event reads or writes."""
    tag = event[0]
    if tag == 'climb':
        return {('L', event[2])}
    if tag in ('adapter', 'residual_adapter'):
        return {('L', event[2])}
    if tag == 'center':
        return {('C', event[1])}
    if tag == 'scalar':
        e = event[1]
        regs = {tuple(e[1])}
        if e[0] in ('copy', 'add'):
            regs.add(tuple(e[2]))
        return regs
    return set()


def is_r1(event):
    return event[0] == 'climb' and event[5] == 1


def split_phases(events):
    """[(phase_event_or_None, [events...])] in order."""
    out = [(None, [])]
    for e in events:
        if e[0] == 'phase':
            out.append((e, []))
        else:
            out[-1][1].append(e)
    return out


def batch_phase(body):
    """Return (new_body, batches) for one phase body."""
    skel = [e for e in body if not is_r1(e)]
    s = len(skel)
    # original skeleton gap of each rank-1 climb and its legal window [lo, hi]
    climbs = []  # (orig_order, gap, event)
    gap = 0
    for e in body:
        if is_r1(e):
            climbs.append((len(climbs), gap, e))
        else:
            gap += 1
    touch_pos = collections.defaultdict(list)
    for i, e in enumerate(skel):
        for reg in touched(e):
            touch_pos[reg].append(i)
    import bisect
    win = {}
    for k, g, e in climbs:
        pos = touch_pos[('L', e[2])]
        j = bisect.bisect_left(pos, g)  # skeleton events at index < g lie before the climb
        lo = pos[j - 1] + 1 if j > 0 else 0
        hi = pos[j] if j < len(pos) else s
        win[k] = (lo, hi)
    # same-register climbs sharing a window must keep their order: exclude them from batching
    by_win = collections.Counter((e[2], win[k]) for k, g, e in climbs)
    movable = [k for k, g, e in climbs if by_win[(e[2], win[k])] == 1]
    ev = {k: e for k, g, e in climbs}
    orig_gap = {k: g for k, g, e in climbs}
    # earliest-deadline greedy sweep over gaps
    start_at = collections.defaultdict(list)
    for k in movable:
        start_at[win[k][0]].append(k)
    avail = set()
    batches = collections.defaultdict(list)  # gap -> list of batches
    batched = set()
    for g in range(s + 1):
        avail.update(start_at[g])
        while any(win[k][1] == g for k in avail) and len(avail) >= BATCH:
            pick = sorted(avail, key=lambda k: (win[k][1], k))[:BATCH]
            batches[g].append(pick)
            batched.update(pick)
            avail.difference_update(pick)
        avail = {k for k in avail if win[k][1] > g}
    # emit: at each gap, batches first, then unbatched climbs that originally sat there
    stay = collections.defaultdict(list)
    for k, g, e in climbs:
        if k not in batched:
            stay[g].append(k)
    out = []
    for g in range(s + 1):
        for b in batches[g]:
            out.extend(ev[k] for k in b)
        out.extend(ev[k] for k in stay[g])
        if g < s:
            out.append(skel[g])
    flat = [b for g in sorted(batches) for b in batches[g]]
    for b in flat:
        assert len({ev[k][2] for k in b}) == BATCH
    return out, [[ev[k] for k in b] for b in flat], len(climbs), len(movable)


def replay_frames(events, word):
    """Frame-semantics replay (the subset of hpe_audit_local's checks that reordering can affect)."""
    frames = word['frames']

    def contains(a, b):
        for x in a:
            for y in b:
                if x >> (y.bit_length() - 1) & 1:
                    x ^= y
            if x:
                return False
        return True

    cur = list(word['start'])
    phase = None
    private = {}
    for e in events:
        tag = e[0]
        if tag == 'phase':
            phase = e[1]
            assert not private
        elif tag == 'climb':
            _, part, r, a, b, rank = e
            assert not private and phase == part and cur[r] == a
            assert contains(frames[a], frames[b]) and rank == len(frames[b]) - len(frames[a]) > 0
            cur[r] = b
        elif tag == 'scalar':
            _, op, f = e
            target = tuple(op[1])
            source = tuple(op[2]) if op[0] in ('copy', 'add') else None
            if target[0] == 'C' and op[0] == 'clear':
                private.pop(target, None)
                continue
            for reg in (target, source):
                if reg is None:
                    continue
                if reg[0] == 'L':
                    assert cur[reg[1]] == f, ('common frame', reg, cur[reg[1]], f)
                else:
                    if reg == target and reg not in private:
                        private[reg] = f
                    assert private[reg] == f
        elif tag == 'center':
            assert phase == 'centers'
            private[('C', e[1])] = e[3]
    assert cur == word['final'], 'terminal frames'


def rank_one_runs_1779(events):
    """PR1779's contiguous-run batch rule, re-implemented: phases skipped, any other event breaks a run."""
    runs, current = [], []
    for e in events:
        if e[0] == 'phase':
            continue
        if is_r1(e):
            current.append(e)
        else:
            if current:
                runs.append(current)
            current = []
    if current:
        runs.append(current)
    n = 0
    for run in runs:
        for g in range(len(run) // BATCH):
            block = run[g * BATCH:(g + 1) * BATCH]
            if len({e[2] for e in block}) == BATCH:
                n += 1
    return n


def main(prog_path, word_path, out_path=None):
    programs = json.load(gzip.open(prog_path))
    reordered = {}
    word = json.load(gzip.open(word_path))
    result = {}
    for orient, events in programs.items():
        replay_frames(events, word)  # positive control: original program
        new_events, per_phase = [], []
        nb = 0
        for ph, body in split_phases(events):
            if ph is not None:
                new_events.append(ph)
            nb_body, batches, n1, nmov = batch_phase(body)
            new_events.extend(nb_body)
            if n1:
                per_phase.append((ph[1] if ph else None, n1, nmov, len(batches)))
            nb += len(batches)
        assert collections.Counter(json.dumps(e) for e in new_events) == collections.Counter(json.dumps(e) for e in events)
        assert [e for e in new_events if not is_r1(e)] == [e for e in events if not is_r1(e)]
        replay_frames(new_events, word)
        reordered[orient] = new_events
        result[orient] = dict(batches=nb, per_phase=per_phase,
                              pr1779_rule_original=rank_one_runs_1779(events),
                              pr1779_rule_reordered=rank_one_runs_1779(new_events))
    if out_path:
        with gzip.open(out_path, 'wt') as fh:
            json.dump(reordered, fh, separators=(',', ':'))
    print(json.dumps(result, indent=1))
    return result


if __name__ == '__main__':
    main(*sys.argv[1:4])
