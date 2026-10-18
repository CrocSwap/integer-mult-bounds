#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Small exact controls for review.md; NOT a selected-word verifier.

Original audit code: Andrey Mas with GPT-6 Pro through ChatGPT.
Only Python's standard library is used. No repository module is imported.
All acceptance checks use explicit exceptions and survive python -O.
The coefficient interpreter implements the NAMED RELAXATION in review.md,
not the production event language or an asserted dirty-host admission.
"""
from fractions import Fraction as Q
import json


class CheckError(Exception):
    pass


def need(condition, message):
    if not condition:
        raise CheckError(message)


def qr(rows):
    """Exact rational row rank, including empty and dependent row lists."""
    a = [list(map(Q, r)) for r in rows]
    if not a:
        return 0
    n = len(a[0])
    need(all(len(r) == n for r in a), 'ragged rational matrix')
    rank = 0
    for c in range(n):
        p = next((i for i in range(rank, len(a)) if a[i][c]), None)
        if p is None:
            continue
        a[rank], a[p] = a[p], a[rank]
        s = a[rank][c]
        a[rank] = [v / s for v in a[rank]]
        for i in range(rank + 1, len(a)):
            s = a[i][c]
            if s:
                a[i] = [x - s*y for x, y in zip(a[i], a[rank])]
        rank += 1
        if rank == len(a):
            break
    return rank


def basis(vectors):
    b = {}
    for v in vectors:
        need(isinstance(v, int) and v >= 0, 'invalid binary vector')
        for p in sorted(b, reverse=True):
            if (v >> p) & 1:
                v ^= b[p]
        if v:
            p = v.bit_length() - 1
            for j in list(b):
                if (b[j] >> p) & 1:
                    b[j] ^= v
            b[p] = v
    return tuple(b[p] for p in sorted(b, reverse=True))


def span(b):
    s = {0}
    for v in b:
        s |= {x ^ v for x in tuple(s)}
    return s


def intersect(a, b):
    return basis(sorted(span(a) & span(b)))


def contained(a, b):
    return len(basis(a+b)) == len(b)


def distance(a, b):
    return len(a) + len(b) - 2*len(intersect(a, b))


def coordinate_frame(h):
    return basis(1 << i for i in range(h))


def unit(n, j):
    return tuple(Q(int(i == j)) for i in range(n))


def plus(a, b, q=1):
    return tuple(x+Q(q)*y for x, y in zip(a, b))


class Replay:
    """One-register transitions, common-frame scalar operations, paid rank metric.

    Inputs are coefficient rows, so correlated/pre-positioned information can
    be represented deliberately. The clean-boundary corollary imposes the
    extra joint-rank hypothesis; the generic cut bound does not assume it.
    """
    def __init__(self, initial, h=8):
        need(bool(initial), 'empty fixture')
        self.h = h
        self.n = len(next(iter(initial.values()))[1])
        self.frames = {k: basis(v[0]) for k, v in initial.items()}
        self.rows = {k: tuple(map(Q, v[1])) for k, v in initial.items()}
        need(all(len(r) == self.n for r in self.rows.values()), 'wrong row width')
        need(all(len(f) <= h for f in self.frames.values()), 'height out of range')
        self.private = set()
        self.initial = {k: (self.frames[k], self.rows[k]) for k in self.rows}
        self.initial_low = {j: [r for k, r in self.rows.items() if len(self.frames[k]) < j]
                            for j in range(1, h+1)}
        self.initial_high = {j: [r for k, r in self.rows.items() if len(self.frames[k]) >= j]
                             for j in range(1, h+1)}
        self.low_seen = {j: set(rs) for j, rs in self.initial_low.items()}
        self.high_seen = {j: set(rs) for j, rs in self.initial_high.items()}
        self.down = {j: 0 for j in range(1, h+1)}
        self.up = {j: 0 for j in range(1, h+1)}
        self.mass = 0
        self.events = 0

    def capture(self):
        self.events += 1
        for j in range(1, self.h+1):
            for k, row in self.rows.items():
                (self.low_seen if len(self.frames[k]) < j else self.high_seen)[j].add(row)
            dl = qr(list(self.low_seen[j])) - qr(self.initial_low[j])
            dh = qr(list(self.high_seen[j])) - qr(self.initial_high[j])
            need(dl <= self.down[j], 'downward history-rank bound violated')
            need(dh <= self.up[j], 'upward history-rank bound violated')

    def allocate(self, k, f):
        need(k not in self.rows, 'duplicate private allocation')
        self.frames[k] = basis(f)
        need(len(self.frames[k]) <= self.h, 'height out of range')
        self.rows[k] = (Q(0),)*self.n
        self.private.add(k)
        self.capture()

    def scalar(self, op, dst, src=None, q=1):
        need(dst in self.rows, 'unknown destination')
        if op == 'clear':
            need(dst in self.private, 'clear of an ordinary dirty role')
            self.rows[dst] = (Q(0),)*self.n
        elif op in ('copy', 'add'):
            need(src in self.rows and src != dst, 'invalid scalar source')
            need(self.frames[dst] == self.frames[src], 'not at one common frame')
            self.rows[dst] = self.rows[src] if op == 'copy' else plus(self.rows[dst], self.rows[src], q)
        else:
            raise CheckError('unsupported scalar operation')
        self.capture()

    def move(self, k, f, charge=None):
        need(k in self.rows, 'unknown moved register')
        a, b = self.frames[k], basis(f)
        need(len(b) <= self.h, 'height out of range')
        cost = distance(a, b)
        need(charge is None or charge == cost, 'incorrect paid rank')
        for j in range(1, self.h+1):
            self.down[j] += int(len(a) >= j > len(b))
            self.up[j] += int(len(a) < j <= len(b))
        self.mass += cost
        self.frames[k] = b
        self.capture()

    def finish(self, expected):
        need(set(expected) == set(self.initial), 'incomplete endpoint specification')
        for k, (f, row) in expected.items():
            need(self.frames[k] == basis(f), 'wrong final frame: '+k)
            need(self.rows[k] == tuple(map(Q, row)), 'wrong arbitrary-dirt endpoint: '+k)
        need(all(not any(self.rows[k]) for k in self.private), 'private work not erased')
        self.capture()
        need(self.mass >= sum(self.down.values()) + sum(self.up.values()), 'mass/crossing mismatch')
        return {'mass': self.mass, 'events': self.events,
                'cut_profiles': [{'j': j, 'down': self.down[j], 'up': self.up[j],
                                  'new_low_history_rank': qr(list(self.low_seen[j]))-qr(self.initial_low[j]),
                                  'new_high_history_rank': qr(list(self.high_seen[j]))-qr(self.initial_high[j])}
                                 for j in range(1, self.h+1)]}


def reject(name, fn, controls):
    try:
        fn()
    except CheckError:
        controls.append(name)
    else:
        raise CheckError('negative control accepted: '+name)


def tree_controls():
    # All binary subspaces of F2^3, generated here, not repository geometry.
    all_spaces = {()}
    for v in range(1, 8):
        all_spaces |= {basis(s+(v,)) for s in tuple(all_spaces)}
    need(len(all_spaces) == 16, 'wrong number of tiny subspaces')
    full = coordinate_frame(3)
    edge_count = 0
    for m in all_spaces:
        for n in all_spaces:
            need(distance(m, n) >= abs(len(m)-len(n)), 'height is not 1-Lipschitz')
            if not contained(n, m):
                continue
            # Choose B complementary to M in F, then H_e = N + B.
            extension, b = m, ()
            for v in full:
                if len(basis(extension+(v,))) > len(extension):
                    b += (v,)
                    extension = basis(extension+(v,))
            he = basis(n+b)
            need(intersect(m, he) == n, 'ambient edge constraint is wrong')
            need(3-len(he) == len(m)-len(n), 'wrong ambient codimension')
            edge_count += 1
    forks = 0
    for u in all_spaces:
        for v in all_spaces:
            cost = (3-len(u))+(3-len(v))
            rhs = 3-len(intersect(u, v))
            need(cost >= rhs, 'rooted two-leaf tree inequality')
            forks += 1
    # Three hyperplanes meet trivially: a tight tree of total cost 3.
    leaves = [basis((1, 2)), basis((1, 4)), basis((2, 4))]
    meet = full
    for leaf in leaves:
        meet = intersect(meet, leaf)
    need(sum(3-len(v) for v in leaves) == 3-len(meet) == 3, 'tight tree fixture')
    need(qr([[1, 1], [1, -1]]) == 2, 'rational-rank control')
    need(len(basis([3, 3])) == 1, 'binary-rank control')
    return {'ambient_dimension': 3, 'subspaces': 16, 'ambient_edge_checks': edge_count,
            'two_leaf_trees': forks, 'tight_three_leaf_cost': 3,
            'rational_rank_2_binary_rank_1_control': True}


def run():
    top, bot = coordinate_frame(8), ()
    x, d, y = [unit(3, j) for j in range(3)]
    initial = {'X': (top, x), 'H': (top, d), 'Y': (bot, y)}
    expected = {'X': (top, x), 'H': (bot, d), 'Y': (bot, plus(y, x))}
    out, controls = {}, []

    # Author's three-transition algebra, only rational logical rows replayed.
    r = Replay(initial)
    r.scalar('add', 'H', 'X'); r.move('H', bot); r.scalar('add', 'Y', 'H')
    r.move('H', top); r.scalar('add', 'H', 'X', -1)
    r.move('H', bot); r.scalar('add', 'Y', 'H', -1)
    out['three_move_repair'] = r.finish(expected)
    need(r.mass == 24, 'wrong three-move cost')

    # Independent two-move save/reload fixture. Not the unpublished script.
    r = Replay(initial); r.allocate('P', top)
    r.scalar('copy', 'P', 'H'); r.scalar('copy', 'H', 'X')
    r.move('H', bot); r.scalar('add', 'Y', 'H')
    r.move('P', bot); r.scalar('copy', 'H', 'P'); r.scalar('clear', 'P')
    out['two_move_save_reload'] = r.finish(expected)
    need(r.mass == 16, 'wrong two-move cost')

    # Mixing two independent centres, with or without a round-trip cycle.
    for cycle in (False, True):
        a, b, yy, zz = [unit(4, j) for j in range(4)]
        r = Replay({'A': (top, a), 'B': (top, b), 'Y': (bot, yy), 'Z': (bot, zz)})
        for name in ('P', 'Q'):
            r.allocate(name, top); r.scalar('copy', name, 'A')
        r.scalar('add', 'P', 'B'); r.scalar('add', 'Q', 'B', -1)
        r.move('P', bot); r.move('Q', bot)
        for dst, q in (('Y', Q(1, 2)), ('Z', Q(-1, 2))):
            r.scalar('add', dst, 'P', Q(1, 2)); r.scalar('add', dst, 'Q', q)
        if cycle:
            r.move('P', top); r.move('P', bot)
        for name in ('P', 'Q'):
            r.scalar('clear', name)
        out['mixed_centres_cycle' if cycle else 'mixed_centres'] = r.finish(
            {'A': (top, a), 'B': (top, b), 'Y': (bot, plus(yy, a)), 'Z': (bot, plus(zz, b))})
        need(r.mass == (32 if cycle else 16), 'wrong mixed-centre cost')

    # Ascending independent host: it contributes to the opposite direction.
    r = Replay({'X': (top, x), 'H': (bot, d), 'Y': (bot, y)})
    r.allocate('P', top); r.scalar('copy', 'P', 'X'); r.move('P', bot)
    r.scalar('add', 'Y', 'P'); r.scalar('clear', 'P'); r.move('H', top)
    out['ascending_host'] = r.finish({'X': (top, x), 'H': (top, d), 'Y': (bot, plus(y, x))})
    need(r.mass == 16, 'wrong ascending-host cost')

    # Scope illustration ONLY: a dirt backup already below the cut.
    # This violates the clean independent entry/no-free-prepositioning clause.
    side_initial = dict(initial, Backup=(bot, d))
    r = Replay(side_initial)
    r.scalar('add', 'H', 'X'); r.move('H', bot)
    r.scalar('add', 'Y', 'H'); r.scalar('add', 'Y', 'Backup', -1)
    r.scalar('copy', 'H', 'Backup')
    out['outside_clean_boundary_prepositioned_dirt'] = r.finish(dict(expected, Backup=(bot, d)))
    need(r.mass == 8, 'wrong prepositioned-information example')
    actual = qr(r.initial_low[1]+[x, d])-qr(r.initial_low[1])
    need(actual == 1, 'wrong quotient rank with prepositioned dirt')
    reject('raw_scatter_plus_host_rank_without_joint_entry_independence',
           lambda: need(actual == 2, 'host direction was already initially low'), controls)

    # Exact, meaningful rejection controls, no assert statements.
    r = Replay(initial)
    r.scalar('add', 'H', 'X'); r.move('H', bot); r.scalar('add', 'Y', 'H')
    reject('one_pass_dirty_borrow_endpoint', lambda: r.finish(expected), controls)
    r = Replay(initial)
    reject('cross_frame_copy', lambda: r.scalar('copy', 'Y', 'X'), controls)
    reject('cross_frame_add', lambda: r.scalar('add', 'Y', 'X'), controls)
    reject('unpaid_rank8_transition', lambda: r.move('H', bot, charge=0), controls)
    reject('undercharged_rank8_transition', lambda: r.move('H', bot, charge=7), controls)
    reject('clear_unrestored_ordinary_dirt', lambda: r.scalar('clear', 'H'), controls)
    r.allocate('P', top); r.scalar('copy', 'P', 'X')
    reject('nonzero_private_endpoint', lambda: r.finish(initial), controls)
    reject('incomplete_endpoint_contract', lambda: r.finish({'X': (top, x)}), controls)
    # Unequal frame subspaces can have identical heights: equality of heights
    # is not common-frame legality, nor is height displacement Fourier cost.
    p, q = basis((1,)), basis((2,))
    need(distance(p, q) == 2 and abs(len(p)-len(q)) == 0, 'equal-height distance control')
    r = Replay({'A': (p, unit(2, 0)), 'B': (q, unit(2, 1))}, h=2)
    reject('same_height_but_different_frame', lambda: r.scalar('add', 'A', 'B'), controls)
    reject('equal_height_nonnested_move_priced_zero', lambda: r.move('A', q, charge=0), controls)

    return {'status': 'PASS_SMALL_EXACT_AUDIT_CONTROLS',
            'scope': 'Toy logical row and binary subspace checks only; no selected word, production audit, physical Clifford, owner, wrapper, or global invoice replay.',
            'tree_controls': tree_controls(), 'fixtures': out,
            'negative_controls_rejected': controls, 'negative_control_count': len(controls)}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
