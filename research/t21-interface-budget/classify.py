# SPDX-License-Identifier: Apache-2.0
"""Phase/role classification of every paid frame climb in the U8 complex word.

Independent recount written for this package. It follows the native frame
semantics used by audit_local.py and research/u8-independent-xcheck/xcheck.py
(monotone nested F2^h frames, a paid child of rank r for every climb of r,
centre-path descents at the cut, and the fixed endpoint frames), but uses
reduced F2 row-echelon bases instead of either predecessor's representation,
and it records *which register role and which program phase* pays each climb.

The scalar map, compensation and cone obligations are NOT rechecked here; they
are checked by the selected replay and by the two cited independent checkers.
This script only partitions the already-admitted paid profile.

Usage: classify.py U8-FULL-WORD.json.gz OUT.json
"""
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict

U8_CONTENT_SHA256 = '090fd574747fbf9628e70cb9beb792732914cfa52e1df147579fe4dbccc68c5a'  # matches research/u8-independent-xcheck
U8_PROFILE = {1: 2548, 2: 338, 3: 446, 4: 162, 5: 72, 8: 8}
U8_WIDTHS = {4: 80, 5: 32, 7: 54, 8: 122, 9: 216}


def require(ok, msg):
    if not ok:
        raise SystemExit('FAIL ' + msg)


class Frame:
    """Subspace of F2^h as a reduced echelon basis keyed by leading bit."""
    __slots__ = ('rows',)

    def __init__(self, gens=()):
        self.rows = {}
        for g in gens:
            self.add(g)

    def reduce(self, x):
        while x:
            top = x.bit_length() - 1
            if top not in self.rows:
                return x
            x ^= self.rows[top]
        return 0

    def add(self, x):
        x = self.reduce(x)
        if x:
            self.rows[x.bit_length() - 1] = x
        return bool(x)

    def contains(self, other):
        return all(self.reduce(x) == 0 for x in other.rows.values())

    @property
    def rank(self):
        return len(self.rows)

    def __eq__(self, other):
        return self.rank == other.rank and self.contains(other)


def annihilator(p, h):
    """{x : <x,p> = 0}, a hyperplane of F2^h for p != 0."""
    require(p != 0, 'zero port')
    low = (p & -p)
    gens = [1 << i for i in range(h) if not (1 << i) & low]
    gens = [x ^ (low if (x & p).bit_count() % 2 else 0) for x in gens]
    F = Frame(gens)
    require(F.rank == h - 1 and all((x & p).bit_count() % 2 == 0 for x in F.rows.values()), 'annihilator')
    return F


def classify(word):
    h, v, R = word['report']['h'], word['report']['v'], word['report']['R']
    N = 2 * v + R
    entering = {int(q) for q in word['start_extra']}
    lowends = {int(q) for q in word['helper_final']}

    def role(q):
        if q < v:
            return 'source'
        if q < 2 * v:
            return 'target'
        if q in entering and q in lowends:
            return 'helper_entering_lowend'
        if q in entering:
            return 'helper_entering_full'
        if q in lowends:
            return 'helper_cold_lowend'
        return 'helper_cold_full'

    regs = lambda g: g[1:3] if g[0] == 'add' else g[1:2]
    cur = [Frame([p]) for p in word['ports']] + [Frame() for _ in range(v + R)]
    for q, U in word['start_extra'].items():
        cur[int(q)] = Frame(U)
    start_rank = [f.rank for f in cur]
    paid = defaultdict(Counter)   # (phase, role) -> Counter(rank)

    def climb(q, U, phase):
        require(U.contains(cur[q]), f'non-monotone frame at register {q} in {phase}')
        d = U.rank - cur[q].rank
        if d > 0:
            paid[(phase, role(q))][d] += 1
        cur[q] = U

    for g in word['A']:
        for q in regs(g):
            climb(q, Frame(g[-1]), 'A')
    require(not word['target_levels'], 'this classifier assumes empty target levels (U8)')
    for q, U in zip(word['centers'], word['center_frames']):
        U = Frame(U)
        require(cur[q] == U, 'centre frame at cut')
        if any(g[2] == q for g in word['cut']):
            paid[('cut_centre_path', 'centre')][U.rank] += 1
    for g in word['B']:
        for q in regs(g):
            climb(q, Frame(g[-1]), 'B')
    early = {i: U for i, U in word['early_cleanup']}
    for i, U in word['early_cleanup']:
        g = word['cleanup'][i]
        for q in regs(g):
            climb(q, Frame(U), 'early_cleanup_tail')
    full = Frame([1 << i for i in range(h)])
    end = [full] * v + [annihilator(p, h) for p in word['ports']] + [full] * R
    for q, U in word['helper_final'].items():
        end[int(q)] = Frame(U)
    for q in range(N):
        climb(q, end[q], 'final_endpoint')
    for i, g in enumerate(word['cleanup']):
        if i not in early:
            require(all(end[q] == full for q in regs(g)), 'FULL cleanup touches a low end')
    widths = Counter(end[q].rank - start_rank[q] for q in range(2 * v, N))
    return paid, widths, start_rank, [e.rank for e in end], role, N


def load_word(path):
    raw = gzip.open(path).read()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == U8_CONTENT_SHA256, 'not the pinned U8 word content')
    return json.loads(raw), digest


def report(word, digest):
    paid, widths, s, e, role, N = classify(word)
    total = Counter()
    for c in paid.values():
        total.update(c)
    require(dict(total) == U8_PROFILE, f'profile {dict(total)} differs from the claimed U8 profile')
    require(dict(widths) == U8_WIDTHS, 'helper widths differ from claim')
    # Telescoping identity: every register's paid climbs sum to end-start.
    by_role_mass = Counter()
    for (phase, r), c in paid.items():
        by_role_mass[r] += sum(k * n for k, n in c.items())
    endpoint_mass = Counter()
    for q in range(N):
        endpoint_mass[role(q)] += e[q] - s[q]
    for r, m in endpoint_mass.items():
        require(by_role_mass[r] == m, f'telescoping fails for {r}')
    require(by_role_mass['centre'] == 64 and sum(by_role_mass.values()) == 5634, 'local mass')
    rows = []
    for (phase, r), c in sorted(paid.items()):
        rows.append(dict(phase=phase, role=r, profile={k: c[k] for k in sorted(c)},
                         mass=sum(k * n for k, n in c.items()), children=sum(c.values())))
    roles = Counter(role(q) for q in range(N))
    out = dict(status='PASS_U8_CLIMB_CLASSIFICATION', word_content_sha256=digest,
               profile={k: total[k] for k in sorted(total)}, helper_widths=dict(sorted(widths.items())),
               register_counts=dict(sorted(roles.items())), mass_by_role=dict(sorted(by_role_mass.items())),
               rows=rows,
               telescoping='Each register pays exactly rank(end frame) - rank(start frame); the centre path pays 8 per centre.',
               scope='Partition of the admitted paid profile only; scalar map, compensation and cones are checked elsewhere.')
    return out


def main():
    out = report(*load_word(sys.argv[1]))
    rows = out['rows']
    with open(sys.argv[2], 'w') as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(out['status'])
    for x in rows:
        print(f"{x['phase']:20s} {x['role']:24s} mass {x['mass']:5d} children {x['children']:5d} {x['profile']}")


if __name__ == '__main__':
    main()
