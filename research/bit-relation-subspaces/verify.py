#!/usr/bin/env python3
"""No further owned-helper relation subspace pays on the PR589 reverse BIT word after #5421's nine relations.

Standard library only; well under a minute.  Reads the PR589 regenerated BIT source (WORD.json.gz and the
249-records.bin event list), pinned by SHA256 in SOURCES.json.

Model (exactly the one of PR #5421, Ali Romman, generalised from single relations to relation subspaces):
  * replay the source records in reverse order over GF(2) with 661 independent entry symbols
    (111 X, 111 Y, 439 helpers); every paid job is a MOVE of rank r > 0 or a COPY entrance (rank 7);
  * a set of owned helper relations is a subspace V of entry forms whose support lies in fields with the full
    entrance frame and which has helper pivots; owning the pivots and setting V to zero makes a job free iff
    the binary row of its moved value lies in V; each dimension of V loses one rank-8 helper target;
  * per local call the raw moment changes by  sum_{removed jobs} r^t - 8^t dim V,  t = 1 - C; the p16/a7
    controller multiplies this by its eighteen full calls (thin queries and idle transforms are unchanged).
Legality (frames, helper pivots) is only relaxed below, so every bound is also a bound for legal V.

Certificate (matroid union theorem, Edmonds / Nash-Williams): let E' be the multiset of job rows, each row
repeated rank times.  If m copies of E' split into p linearly independent sets then m w(V) <= p dim V for every
subspace V, where w(V) is the paid rank mass with rows in V.  Tight subspaces (w = 8 dim) are exactly the rows to
which an extra element cannot be added by an Edmonds augmenting path.

Checks:
  1. pinned inputs; the source paid profile {1:1323,2:1342,3:79,4:44,5:102,6:11,7:19} of #5421;
  2. calibration on the source word: E' splits into 8 independent sets (max_V w - 8 dim = 0), and the tight
     subspaces are exactly nine one-dimensional ones, each = one COPY (H7) + one MOVE (H1): #5421's relations;
  3. modulo those nine relations V0: E' still splits into 8 sets and no row is tight (w(V) < 8 dim V), and
     2E' splits into 15 independent sets, so w(V) <= 7.5 dim V for every V of every dimension;
  4. since r^t <= r for r >= 1, the moment change is <= (7.5 - 8^t) dim V < 0 for every C < log(8/7.5)/log 8;
  5. live controls: on the source word 2E' does not split into 15 sets, and an injected rank-1 job on a #5421
     COPY row makes E' not 8-splittable;
  6. the stored RESULT.json equals the rebuild.
Usage: python3 -I -B verify.py [--write]
"""
import argparse, collections, gzip, hashlib, json, struct, sys
from decimal import Decimal as D, getcontext
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SRC = ROOT / 'research' / 'kappa-rebuild' / 'bit' / 'sources' / 'pr589-regenerated'
SIZE, PORTS = 661, 111
SOURCE_PAID = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
C_5421 = D('0.0034720700448926')          # raw moment root of #5421's new controller
getcontext().prec = 50


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def pinned_inputs():
    rows = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']
    for row in rows:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row['sha256'], 'input drift: ' + row['path'])


def load():
    word = json.loads(gzip.decompress((SRC / 'WORD.json.gz').read_bytes()))
    records = list(struct.iter_unpack('<6i', (SRC / 'records' / '249-records.bin').read_bytes()))
    return word, records


def paid_jobs(word, records):
    """Reverse replay over GF(2); every paid job with the binary row of its moved value."""
    rows = [1 << i for i in range(SIZE)] + [0]
    jobs = []
    for idx, (op, x, y, a, b, _) in enumerate(reversed(records)):
        if op == 0:
            if b:
                jobs.append((idx, 'MOVE', b, rows[x]))
        elif op == 1:
            if a & 1:
                rows[x] ^= rows[y]
        elif op == 3:
            require(y == SIZE and rows[SIZE] == 0, 'source COPY entrance into the empty centre')
            jobs.append((idx, 'COPY', 7, rows[x]))
            rows[SIZE] = rows[x]
        elif op == 2:
            require(y == SIZE and rows[x] == rows[SIZE], 'source COPY exit')
            rows[SIZE] = 0
        else:
            require(False, 'unknown source record')
    want = [(1 << i) ^ ((1 << (i - PORTS)) if PORTS <= i < 2 * PORTS else 0) for i in range(SIZE)] + [0]
    require(rows == want, 'source reverse identity (X,Y) -> (X,Y+X), helpers fixed')
    require(dict(collections.Counter(j[2] for j in jobs)) == SOURCE_PAID, 'source paid profile of #5421')
    full = sum(1 << i for i in range(SIZE) if word['final'][i] == 1)
    helpers = sum(1 << i for i in range(2 * PORTS, SIZE))
    legal = [j for j in jobs if j[3] and j[3] & ~full == 0 and j[3] & helpers]
    return jobs, legal


def echelon(rows):
    b = {}
    for r in rows:
        while r:
            h = r.bit_length() - 1
            if h in b:
                r ^= b[h]
            else:
                b[h] = r
                break
    return b


def reduce(b, r):
    while r:
        h = r.bit_length() - 1
        v = b.get(h)
        if v is None:
            return r
        r ^= v
    return 0


class Partition:
    """Matroid partition of a multiset of GF(2) rows into k linearly independent parts (Edmonds)."""

    def __init__(self, elems, k):
        self.elems, self.k = elems, k
        self.members = [[] for _ in range(k)]
        self.basis = [None] * k
        self.where = {}

    def _build(self, k):
        b = {}
        for idx, e in enumerate(self.members[k]):
            r, c = self.elems[e], 1 << idx
            while r:
                h = r.bit_length() - 1
                if h in b:
                    v, cv = b[h]; r ^= v; c ^= cv
                else:
                    b[h] = (r, c); break
        self.basis[k] = b

    def circuit(self, k, e):
        if self.basis[k] is None:
            self._build(k)
        b, r, c = self.basis[k], self.elems[e], 0
        while r:
            h = r.bit_length() - 1
            t = b.get(h)
            if t is None:
                return None
            r ^= t[0]; c ^= t[1]
        out, i = [], 0
        while c:
            if c & 1:
                out.append(self.members[k][i])
            c >>= 1; i += 1
        return out

    def augment(self, x):
        """Insert element x by a shortest augmenting path; return (True, None) or (False, reachable set)."""
        prev, queue, qi = {x: None}, [x], 0
        order = sorted(range(self.k), key=lambda k: len(self.members[k]))
        while qi < len(queue):
            y = queue[qi]; qi += 1
            for k in order:
                if self.where.get(y) == k:
                    continue
                circ = self.circuit(k, y)
                if circ is None:
                    moves, z = [(y, k)], y
                    while prev[z] is not None:
                        py, pk = prev[z]; moves.append((py, pk)); z = py
                    touched = set()
                    for z, kk in moves:
                        old = self.where.get(z)
                        if old is not None:
                            self.members[old].remove(z); touched.add(old)
                    for z, kk in moves:
                        self.members[kk].append(z); self.where[z] = kk; touched.add(kk)
                    for t in touched:
                        self.basis[t] = None
                    return True, None
                for z in circ:
                    if z not in prev:
                        prev[z] = (y, k); queue.append(z)
        return False, set(queue)

    def check(self):
        """Independent re-check: every part independent and the parts cover the multiset exactly once."""
        independent = all(len(echelon([self.elems[e] for e in m])) == len(m) for m in self.members)
        cover = sorted(e for m in self.members for e in m) == list(range(len(self.elems)))
        return independent and cover


def multiset(legal, V0):
    """Rows modulo V0 with their paid rank mass; returns (distinct rows, mass, jobs per row, element list)."""
    per = collections.defaultdict(list)
    for j in legal:
        q = reduce(V0, j[3])
        if q:
            per[q].append(j)
    rows = sorted(per)
    mass = {q: sum(j[2] for j in per[q]) for q in rows}
    elems = [q for q in rows for _ in range(mass[q])]
    return rows, mass, per, elems


def split(elems, k, copies=1, base_k=8):
    """Try to split `copies` copies of elems into k independent sets; returns (ok, Partition)."""
    allel = elems * copies
    if copies == 1:
        P = Partition(allel, k)
        fails = 0
        for e in sorted(range(len(allel)), key=lambda e: allel[e]):
            ok, _ = P.augment(e)
            fails += not ok
        return fails == 0 and P.check(), P
    ok8, P8 = split(elems, base_k)
    if not ok8:
        return False, P8
    groups, n = P8.members, len(elems)
    parts = [[c * n + e for e in g] for c in range(copies) for g in groups]
    parts.sort(key=len)
    loose = [e for g in parts[:base_k * copies - k] for e in g]
    P = Partition(allel, k)
    for kk, g in enumerate(parts[base_k * copies - k:]):
        P.members[kk] = list(g)
        for e in g:
            P.where[e] = kk
    fails = 0
    for e in loose:
        ok, _ = P.augment(e)
        fails += not ok
    return fails == 0 and P.check(), P


def tight_flats(rows, per, P):
    """Rows lying in a subspace with w = 8 dim: an extra copy cannot be inserted. Returns the minimal flats."""
    flats = {}
    base_members = [list(m) for m in P.members]
    base_where = dict(P.where)
    for q in rows:
        P.elems.append(q); x = len(P.elems) - 1
        ok, reach = P.augment(x)
        if not ok:
            span = echelon([P.elems[e] for e in reach])
            inside = [r for r in rows if reduce(span, r) == 0]
            key = tuple(sorted(span))
            flats[key] = dict(dim=len(span), mass=sum(j[2] for r in inside for j in per[r]),
                              jobs=sorted([j[1], j[2], j[0]] for r in inside for j in per[r]))
        P.elems.pop()
        P.members = [list(m) for m in base_members]; P.basis = [None] * P.k
        P.where = dict(base_where)
    return sorted(flats.values(), key=lambda f: f['jobs'])


def build():
    pinned_inputs()
    word, records = load()
    jobs, legal = paid_jobs(word, records)
    out = dict(paid_jobs=len(jobs), legal_jobs=len(legal), legal_profile=dict(sorted(collections.Counter(j[2] for j in legal).items())),
               already_zero=sum(1 for j in jobs if not j[3]))
    # 2. calibration on the source word
    rows, mass, per, elems = multiset(legal, {})
    ok, P = split(elems, 8)
    require(ok, 'source E\' splits into 8 independent sets')
    flats = tight_flats(rows, per, P)
    require(len(flats) == 9 and all(f['dim'] == 1 and f['mass'] == 8 and [j[:2] for j in f['jobs']] == [['COPY', 7], ['MOVE', 1]]
                                    for f in flats), 'tight subspaces on the source word are exactly the nine #5421 relations')
    out['source'] = dict(distinct_rows=len(rows), elements=len(elems), max_gain_mass=0,
                         tight=[f['jobs'] for f in flats])
    # 3. modulo the nine relations
    V0 = echelon([j[3] for j in legal if j[1] == 'COPY'])
    require(len(V0) == 9, 'nine independent #5421 relation forms')
    rows, mass, per, elems = multiset(legal, V0)
    ok, P = split(elems, 8)
    require(ok, 'E\' modulo V0 splits into 8 independent sets')
    flats = tight_flats(rows, per, P)
    require(flats == [], 'no tight subspace modulo V0')
    ok15, _ = split(elems, 15, copies=2)
    require(ok15, '2E\' modulo V0 splits into 15 independent sets')
    out['quotient'] = dict(distinct_rows=len(rows), elements=len(elems), removed_by_V0=sum(1 for j in legal if reduce(V0, j[3]) == 0),
                           max_single_row_mass=max(mass.values()), tight=0,
                           certificate='2 w(V) <= 15 dim V for every relation subspace V (mod V0)')
    # 4. moment
    t = 1 - C_5421
    eight_t = (t * D(8).ln()).exp()
    threshold = (D(8) / D('7.5')).ln() / D(8).ln()
    require(D('7.5') < eight_t and C_5421 < threshold, 'density 7.5 is below 8^t')
    out['moment'] = dict(C=str(C_5421), eight_to_t=str(eight_t.quantize(D('1e-12'))),
                         loss_per_dimension_at_least=str((eight_t - D('7.5')).quantize(D('1e-12'))),
                         valid_for_C_below=str(threshold.quantize(D('1e-12'))))
    # 5. live controls
    rows_s, mass_s, per_s, elems_s = multiset(legal, {})
    ok_s, _ = split(elems_s, 15, copies=2)
    require(not ok_s, 'control: source word 2E\' must not split into 15 sets (tight #5421 relations)')
    copy_row = next(j[3] for j in legal if j[1] == 'COPY')
    bad = list(elems_s) + [copy_row]
    ok_b, _ = split(bad, 8)
    require(not ok_b, 'control: an extra rank-1 job on a #5421 COPY row must break the 8-split')
    out['controls'] = dict(source_2E_into_15='rejected', injected_rank1_on_copy_row='rejected')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    result = build()
    path = HERE / 'RESULT.json'
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if args.write:
        path.write_bytes(text.encode('utf-8'))
    require(path.exists() and json.loads(path.read_text(encoding='utf-8')) == json.loads(text), 'stored RESULT.json equals the rebuild')
    print('PASS_BIT_RELATION_SUBSPACES_NO_FURTHER_GAIN_AFTER_5421')


if __name__ == '__main__':
    main()
