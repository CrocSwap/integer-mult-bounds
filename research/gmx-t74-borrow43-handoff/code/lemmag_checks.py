# SPDX-License-Identifier: Apache-2.0
"""Lemma G label / adapter checks, vendored VERBATIM from research/selected1094-extended-labels-seed65/verify.py (PR1964, thakrarsagar / Sagar Thakrar
with Anthropic Claude assistance): `label_check` (the independent, HPE-aware Lemma G H1 check in the extended labels (tag, frame), strict and permissive
readings), `adapter_rule` (the hardening rule: every data adapter and wrapper sits in its own phase at its frame, and no scalar or climb touches a source
before its entry adapter or a target after its exit adapter), and the three physically wrong adapter mutants X (exit straddle), Y (entry straddle) and
Z (exit adapters moved before a phase-B add) that the frame-only local replay accepts and these checks must reject.
Lemma G (extended labels) is due to DreamingOfClouds (PR509 / PR516); the checker it extends is research/e8-lemma-g-lean/code/check_extended_labels.py.
Only this header and the constants below are added; the function bodies are byte-for-byte those of PR1964."""
from collections import Counter
from fractions import Fraction as Q

FULL = 1                       # frame-table row of FULL (row 0 is the zero frame)
T = ('T',)                     # the word's family tag
FREE = 'free'                  # label of a cleared private register under the permissive reading
PHASE_ORDER = ['zero_frame_precondition', 'entry_adapters', 'A', 'centers', 'B', 'cleanup_tail', 'final',
               'exit_adapters', 'full_frame_cleanup', 'done']


def need(ok, message):
    if not ok:
        raise ValueError(message)


def operands(op):
    return [tuple(op[1]), tuple(op[2])] if op[0] in ('add', 'copy') else [tuple(op[1])]


def label_check(c, events, reading):
    """Independent, HPE-aware Lemma G H1 check in the extended labels (tag, frame) of PROOF.md.

    Every climb, centre step, data adapter and wrapper is read as Lean's `relabel r A B` and must find its register at
    label A.  Scalar events, two readings:
      'strict'     clear C at f sets (T, f); add/scale/copy need every operand at (T, f) (G0, stronger than Lean's
                   Admissible, which asks only lt = ls for add and lr = F for copy);
      'permissive' clear leaves a private label unconstrained until its next touch, the frame annotation is ignored,
                   and only Lean's Admissible is asked (add: lt = ls; copy: none, it sets lc := lr; scale: none).
    Acceptance under 'strict' implies acceptance under 'permissive'; a rejection under 'permissive' means no reading of
    the private clears makes the stream WellLabelled.  The adapter/wrapper bridge and end labels are checked as well.
    Returns (violations, statistics)."""
    v, R = c['v'], c['R']; n = 2 * v + R; start, final = c['start'], c['final']
    hpe = {r for r in range(2 * v, n) if final[r] != FULL}
    entering = {r for r in range(2 * v, n) if start[r] != 0}
    wrapped = hpe | entering
    lab = {('L', r): (('pre', r) if r < v else ('prew', r) if r in wrapped else T, start[r]) for r in range(n)}
    first_private = {}
    viol = []; st = Counter(); src = Counter(); by_phase = Counter(); phases = []
    entry, exit_, pre, post = Counter(), Counter(), Counter(), Counter()
    phase = None; zalloc, zfree, wcount = set(), set(), Counter()

    def bad(idx, why):
        viol.append([idx, phase, why])

    for idx, e in enumerate(events):
        kind = e[0]; st['events'] += 1
        if kind == 'phase':
            phase = e[1]; phases.append(phase); continue
        if kind == 'zero_buffer':   # BORROW extension: private FULL zero buffer Z_r of a restored cold input (full_frame_cleanup)
            _, way, r = e; z = ('Z', r); st['zero_buffer_' + str(way)] += 1
            if phase != 'full_frame_cleanup': bad(idx, f'zero buffer {way} {r} outside full_frame_cleanup')
            if way == 'alloc':
                if z in lab: bad(idx, f'zero buffer {r} allocated twice')
                if r not in hpe: bad(idx, f'zero buffer for {r} which is not a cold-ended register')
                lab[z] = (T, FULL); zalloc.add(r)
            elif way == 'free':
                if lab.get(z) != (T, FULL): bad(idx, f'zero buffer {r} freed at {lab.get(z)} not (T,{FULL})')
                lab.pop(z, None); zfree.add(r)
            else:
                bad(idx, 'unknown zero_buffer way ' + str(way))
            continue
        if kind == 'warp':          # BORROW extension: rank-0 K_G reference change, relabel (T,a)->(T,b) of register r
            _, x, op, a, b = e; x = tuple(x); st['warp'] += 1
            if x[0] != 'L' or v <= x[1] < 2 * v: bad(idx, f'warp of target or non-L register {x}')
            if lab.get(x) != (T, a): bad(idx, f'warp of {x} from {lab.get(x)} not (T,{a})')
            lab[x] = (T, b); wcount[x[1]] += 1
            continue
        if kind == 'scalar':
            op, f = e[1], e[2]; regs = operands(op); st['scalar_' + op[0]] += 1; by_phase[phase] += 1
            for x in regs:
                if x[0] == 'Z' and x not in lab: bad(idx, f'zero buffer {x} used before allocation')
                if x[0] == 'C' and x not in first_private:
                    # Lean leaves a private register's initial label free; record whether its dirty initial content
                    # can be read (a hygiene fact, not a label violation).
                    first_private[x] = op[0] if (op[0] == 'clear' or (op[0] == 'copy' and x == regs[0])) else 'read'
                    lab.setdefault(x, FREE)
            if op[0] in ('add', 'scale') and regs[0][0] == 'L' and regs[0][1] < v:
                src[phase] += 1
            want = (T, f)
            if op[0] == 'clear':
                lab[regs[0]] = want if reading == 'strict' else FREE
            elif op[0] == 'copy':
                t, s = regs
                if reading == 'strict':
                    if lab.get(s) != want: bad(idx, f'copy source {s} at {lab.get(s)} not {want}')
                    lab[t] = want
                else:
                    lab[t] = lab.get(s)
            elif op[0] == 'add':
                t, s = regs
                if reading == 'strict':
                    for x in (t, s):
                        if lab.get(x) == FREE and x[0] == 'C': lab[x] = want
                    off = [(x, lab.get(x)) for x in (t, s) if lab.get(x) != want]
                    if off: bad(idx, f'add operands {off} not at {want}')
                else:
                    if lab.get(t) == FREE: lab[t] = lab.get(s)
                    if lab.get(s) == FREE: lab[s] = lab.get(t)
                    if lab.get(t) != lab.get(s): bad(idx, f'add {t} at {lab.get(t)} but {s} at {lab.get(s)}')
            elif op[0] == 'scale':
                if reading == 'strict':
                    x = regs[0]
                    if lab.get(x) == FREE and x[0] == 'C': lab[x] = want
                    if lab.get(x) != want: bad(idx, f'scale operand {x} at {lab.get(x)} not {want}')
            else:
                bad(idx, 'unknown scalar ' + str(op[0]))
            continue
        if kind == 'climb':
            _, part, r, a, b, rank = e; x = ('L', r); st['climb'] += 1
            if lab[x] != (T, a): bad(idx, f'climb of {r} from {lab[x]} not (T,{a})')
            lab[x] = (T, b)
        elif kind == 'center':
            _, k, a, b, rank = e; x = ('C', k); st['centre_step'] += 1
            if lab.get(x) == FREE: lab[x] = (T, a)
            if lab.get(x) != (T, a): bad(idx, f'centre step of {x} from {lab.get(x)} not (T,{a})')
            lab[x] = (T, b)
        elif kind == 'adapter':
            _, way, r, f = e; x = ('L', r)
            if way == 'old_to_new':
                entry[r] += 1; st['entry_adapter'] += 1
                if r < v:
                    if f != start[r] or lab[x] != (('pre', r), f): bad(idx, f'source entry adapter of {r} at {lab[x]}, frame {f}')
                    lab[x] = (T, f)
                else:
                    if r in wrapped or f != 0 or lab[x] != (T, 0): bad(idx, f'identity entry adapter of {r} at {lab[x]}, frame {f}')
            elif way == 'new_to_old':
                exit_[r] += 1; st['exit_adapter'] += 1
                if v <= r < 2 * v:
                    if f != final[r] or lab[x] != (T, f): bad(idx, f'target exit adapter of {r} at {lab[x]}, frame {f}')
                    lab[x] = (('post', r), f)
                else:
                    if r in hpe or f != FULL or lab[x] != (T, FULL): bad(idx, f'identity exit adapter of {r} at {lab[x]}, frame {f}')
            else:
                bad(idx, 'unknown adapter ' + str(way))
        elif kind == 'residual_adapter':
            _, side, r, f, *U = e; x = ('L', r)
            if r not in wrapped or f != start[r] or U != ([final[r]] if r in hpe else []):
                bad(idx, f'wrapper key of {r}: frame {f}, terminal {U}')
            if side == 'pre':
                pre[r] += 1; st['pre_wrapper'] += 1
                if lab[x] != (('prew', r), start[r]): bad(idx, f'pre wrapper of {r} at {lab[x]}')
                lab[x] = (T, start[r])
            elif side == 'post':
                post[r] += 1; st['post_wrapper'] += 1
                if lab[x] != (T, final[r]): bad(idx, f'post wrapper of {r} at {lab[x]}')
                lab[x] = (('done', r), final[r])
            else:
                bad(idx, 'unknown wrapper side ' + str(side))
        else:
            bad(idx, 'unknown event ' + str(kind))
    phase = 'end'
    if phases != PHASE_ORDER: bad(len(events), 'phase order ' + str(phases))
    for r in range(n):
        want_end = ((T, FULL) if r < v else (('post', r), final[r]) if r < 2 * v
                    else (('done', r), final[r]) if r in wrapped else (T, FULL))
        if lab[('L', r)] != want_end: bad(len(events), f'register {r} ends at {lab[("L", r)]} not {want_end}')
        want_entry = 0 if r in wrapped else 1
        want_exit = 0 if r in hpe else 1
        want_wrap = 1 if r in wrapped else 0
        if (entry[r], exit_[r], pre[r], post[r]) != (want_entry, want_exit, want_wrap, want_wrap):
            bad(len(events), f'bridge of {r}: entry {entry[r]} exit {exit_[r]} pre {pre[r]} post {post[r]}')
    if zalloc != zfree or any(('Z', r) in lab for r in zalloc): bad(len(events), 'zero buffers not all freed')
    stats = dict(warps=st['warp'], zero_buffers=len(zalloc), private_first_touch_reads=sum(first == 'read' for first in first_private.values()),events=st['events'], phases=len(phases), scalar_events=sum(by_phase.values()),
                 scalar_by_kind={k[7:]: z for k, z in sorted(st.items()) if k.startswith('scalar_')},
                 scalar_by_phase=dict(sorted(by_phase.items())), climbs=st['climb'], centre_steps=st['centre_step'],
                 entry_adapters=st['entry_adapter'], exit_adapters=st['exit_adapter'], pre_wrappers=st['pre_wrapper'],
                 post_wrappers=st['post_wrapper'], private_registers=len(first_private),
                 source_writes=sum(src.values()), source_writes_by_phase=dict(sorted(src.items())))
    return viol, stats


def straddle(events, adapter_event, frame, reg):
    """[C0 += L; L -= C0] adapter [L += C0; C0 -= L; clear C0], all at the adapter's frame."""
    i = events.index(adapter_event)
    need(events.count(adapter_event) == 1, 'adapter event not unique')
    C0, L = ['C', 0], ['L', reg]
    before = [['scalar', ['add', C0, L, 1, 1], frame], ['scalar', ['add', L, C0, -1, 1], frame]]
    after = [['scalar', ['add', L, C0, 1, 1], frame], ['scalar', ['add', C0, L, -1, 1], frame], ['scalar', ['clear', C0], frame]]
    return events[:i] + before + [events[i]] + after + events[i + 1:], i


def adapter_rule(c, events):
    """The hardening README (b) recommends next to the frame-only replay (a sketch, not proved sufficient for H1): every
    data adapter and wrapper sits in its own phase at cur[r] == its frame, and per-register adapter state is tracked as
    the replay tracks wrappers: no scalar or climb touches a source before its entry adapter or a target after its exit
    adapter.  Returns the indices of offending events."""
    v = c['v']; cur = list(c['start']); phase = None; entered, exited = set(), set(); bad = []
    for idx, e in enumerate(events):
        kind = e[0]; regs = []
        if kind == 'phase':
            phase = e[1]; continue
        if kind == 'scalar':
            regs = [x[1] for x in operands(e[1]) if x[0] == 'L']
        elif kind == 'climb':
            regs = [e[2]]
        elif kind == 'warp':
            regs = [e[1][1]]
        elif kind == 'adapter':
            _, way, r, f = e
            if phase != ('entry_adapters' if way == 'old_to_new' else 'exit_adapters') or cur[r] != f:
                bad.append(idx)
            (entered if way == 'old_to_new' else exited).add(r)
        elif kind == 'residual_adapter':
            _, side, r, f, *U = e
            if (phase, cur[r]) != (('entry_adapters', c['start'][r]) if side == 'pre' else ('full_frame_cleanup', c['final'][r])):
                bad.append(idx)
        if any((r < v and r not in entered) or (v <= r < 2 * v and r in exited) for r in regs):
            bad.append(idx)
        if kind == 'climb':
            cur[e[2]] = e[4]
        if kind == 'warp':   # BORROW extension: the warp must find the register at its from frame
            if cur[e[1][1]] != e[3]: bad.append(idx)
            cur[e[1][1]] = e[4]
    return bad


def exit_block_move(c, events):
    """Mutant Z: the exit adapters of registers 0 .. t (t = v, the target of port 0), in order, moved to just before the
    last scalar event on L_t ahead of its exit adapter.  Returns (mutant, insertion index, first and last moved index)."""
    t = c['v']
    xs = [x for x, e in enumerate(events) if e[0] == 'adapter' and e[1] == 'new_to_old' and e[2] <= t]
    need([events[x][2] for x in xs] == list(range(t + 1)) and xs == list(range(xs[0], xs[-1] + 1)),
         'the exit adapters of registers 0..t are not one ordered block')
    g = max(x for x in range(xs[0]) if events[x][0] == 'scalar' and ('L', t) in operands(events[x][1]))
    return events[:g] + events[xs[0]:xs[-1] + 1] + events[g:xs[0]] + events[xs[-1] + 1:], g, xs[0], xs[-1]


def touches(e, reg):
    if e[0] == 'scalar':
        return reg in operands(e[1])
    if e[0] in ('climb', 'adapter', 'residual_adapter'):
        return reg == ('L', e[2])
    if e[0] == 'center':
        return reg == ('C', e[1])
    return False
