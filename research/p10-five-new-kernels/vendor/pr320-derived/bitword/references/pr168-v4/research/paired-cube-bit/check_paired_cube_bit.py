#!/usr/bin/env python3
"""Standalone checker for subset-port bit words with broadcast roots (paired-cube bit word with partner-pair
source mixing).  Standard library only; independent of the generator (own exact integer linear algebra, own
register simulation).  Refuses to run under python -O.

Inputs (plain JSON written by paired_cube_bit_word.py): graph_pP.json, word_pP.json, frames_pP.json,
kchron_pP.json, profile_pP.json.  Checks:
  1. exact frames: every frame record (integer annihilator rows 'a' or integer basis rows 'b') is completed to
     the other representation by exact integer elimination; A.B^T = 0 exactly and rank A + rank B = h;
  2. the mod-2 decoder: supports of all additions are disjoint; for every target the deliveries (star roots,
     side roots, partner singles, partner-pair sums) XOR to {T}; stars read are exactly the c in T and the
     side part is exactly sum_{|S cap T|=1} x_S;
  3. geometry: source frames are the lines <chi_S>; side root frames lie in every receiver's cap
     ker(3 chi_T - 1) and equal the common cap of the group; centre frames are the star spans; the frame of
     every addition contains its operands' frames; every root node's frame lies in its root frame;
  4. every role chain (start -> each op frame -> root frame -> full) is nested, including gauged starts
     (sigma inside the first op frame, gauged roles untouched in phase one); every target chain (gauge reads
     ascending, side root caps in root order, partner-pair delivery at the level-2 cap, final cap) is nested;
     the partner-pair chronology: mix frame span{chi_c,chi_d} with H0-Gram I_2, contained in the receivers'
     level-2 cap, carrier chain [<chi_c>, mix, cap, full] and passive chain [<chi_d>, mix, full] nested;
  5. G = I - J/9 nondegenerate on every frame used (exact integer determinant test);
  6. literal F2 replay with arbitrary dirty scratch: y = y0 + x, scratch and sources restored;
  7. independent ledger recount from the role chains equals the saved child histogram (PR #144 bit ledger);
  8. mutation controls (must all be REJECTED): broken partner mix, delivery outside the shared cap (full
     frame), delivery below the level (face cap without span{chi_c,chi_d}), dropped star, non-nested role chain.
Usage: python3 check_paired_cube_bit.py --dir out --p 12
"""
import argparse, json, random, sys
from collections import Counter, defaultdict
from math import gcd
from operator import mul
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('refusing to run under python -O: assertions are part of the check')


class Fail(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise Fail(msg)


# ------------------------------------------------------------------ exact integer linear algebra
def prim(v):
    g = 0
    for x in v:
        g = gcd(g, abs(x))
    if g > 1:
        v = [x // g for x in v]
    f = next((x for x in v if x), 0)
    return tuple(-x for x in v) if f < 0 else tuple(v)


def reduce_rows(rows, h):
    """Integer reduced echelon form: returns (rows, pivot columns); each pivot column is zero outside its row."""
    rows = [list(r) for r in rows]
    out, pivs = [], []
    for r in rows:
        for pr, pc in zip(out, pivs):
            if r[pc]:
                a, b = pr[pc], r[pc]
                r = [x * a - y * b for x, y in zip(r, pr)]
        r = list(prim(r))
        c = next((j for j in range(h) if r[j]), None)
        if c is None:
            continue
        for i, (pr, pc) in enumerate(zip(out, pivs)):
            if pr[c]:
                a, b = r[c], pr[c]
                out[i] = list(prim([x * a - y * b for x, y in zip(pr, r)]))
        out.append(r); pivs.append(c)
    return out, pivs


def kernel(rows, h):
    red, pivs = reduce_rows(rows, h)
    ps = set(pivs)
    basis = []
    for f in range(h):
        if f in ps:
            continue
        D = 1
        for r, c in zip(red, pivs):
            if r[f]:
                D = D * abs(r[c]) // gcd(D, abs(r[c]))
        v = [0] * h
        v[f] = D
        for r, c in zip(red, pivs):
            if r[f]:
                v[c] = -r[f] * D // r[c]
        basis.append(prim(v))
    return basis, len(red)


def rank(rows, h):
    return len(reduce_rows(rows, h)[0])


def dot(a, b):
    return sum(map(mul, a, b))


# ------------------------------------------------------------------ checker
class Checker:
    def __init__(self, d, p, mutate=None):
        self.mut = mutate
        rd = lambda name: json.loads((d / ('%s_p%d.json' % (name, p))).read_text())
        self.g, self.w, self.fr, self.k, self.prof = rd('graph'), rd('word'), rd('frames'), rd('kchron'), rd('profile')
        self.h, self.v = self.g['h'], self.g['v']
        if mutate == 'dropped_star':
            j = next(i for i, r in enumerate(self.g['roots']) if r['kind'] == 'center')
            self.g['roots'][j]['targets'] = []
        if mutate == 'broken_mix':
            self.k['entries'][0]['skip_mix'] = True
        if mutate == 'outside_cap':
            # raise the mixed carrier past the receivers' shared cap (to the full frame) and deliver there
            e = self.k['entries'][0]
            e['deliver_frame'] = self.w['full_frame']
            e['carrier_chain'][2] = e['deliver_frame']
        if mutate == 'below_level':
            # deliver at the receivers' level-1 (face) cap, which does not contain span{chi_c, chi_d}
            e = self.k['entries'][0]
            face = next(j for j, r in enumerate(self.g['roots']) if r['kind'] == 'side' and set(e['receivers']) < set(r['targets']))
            e['deliver_frame'] = self.w['root_frame'][face]
            e['carrier_chain'][2] = e['deliver_frame']
        if mutate == 'non_nested':
            # move one addition's frame down to the frame of its smallest operand's source line
            x = next(int(k) for k, f in sorted(self.w['node_frame'].items(), key=lambda kv: int(kv[0])) if int(k) >= self.v and str(int(k)) not in set(map(str, self.w['plain'])))
            self.w['node_frame'][str(x)] = self.w['source_frame'][0]

    # ---------------- frames
    def frames(self):
        h = self.h
        self.A, self.B, self.dimf = {}, {}, {}
        for key, rec in self.fr['frames'].items():
            f = int(key)
            if 'a' in rec:
                A = [tuple(r) for r in rec['a']]
                need(rank(A, h) == len(A), 'independent annihilator rows %d' % f)
                B, _ = kernel(A, h)
            else:
                B = [tuple(r) for r in rec['b']]
                need(rank(B, h) == len(B), 'independent basis rows %d' % f)
                A, _ = kernel(B, h)
            need(len(A) + len(B) == h and len(B) == rec['dim'], 'dimensions of frame %d' % f)
            need(all(dot(a, b) == 0 for a in A for b in B), 'A.B = 0 for frame %d' % f)
            self.A[f], self.B[f], self.dimf[f] = A, B, len(B)
        self.cc = {}
        return len(self.A)

    def sub(self, f1, f2):
        """frame f1 contained in frame f2 (exact)"""
        if f1 == f2:
            return True
        key = (f1, f2)
        r = self.cc.get(key)
        if r is None:
            B1, A2 = self.B[f1], self.A[f2]
            r = len(B1) <= len(self.B[f2]) and all(dot(a, b) == 0 for a in A2 for b in B1)
            self.cc[key] = r
        return r

    def in_frame(self, vec, f):
        return all(dot(a, vec) == 0 for a in self.A[f])

    def nondeg(self, f):
        h = self.h
        B, A = self.B[f], self.A[f]
        if not B or len(B) == h:
            return True
        if len(B) <= len(A):
            s = [sum(b) for b in B]
            M = [[9 * dot(B[i], B[j]) - s[i] * s[j] for j in range(len(B))] for i in range(len(B))]
            return rank(M, len(B)) == len(B)
        s = [sum(a) for a in A]
        M = [[(9 - h) * dot(A[i], A[j]) + s[i] * s[j] for j in range(len(A))] for i in range(len(A))]
        return rank(M, len(A)) == len(A)

    # ---------------- decoder
    def decoder(self):
        g, v = self.g, self.v
        args = g['args']
        lab = [frozenset(l) for l in g['labels']]
        sup = [1 << i for i in range(v)] + [0] * (len(args) - v)
        for x in range(v, len(args)):
            a, b = args[x]
            need(not sup[a] & sup[b], 'support-disjoint addition %d' % x)
            sup[x] = sup[a] | sup[b]
        self.sup = sup
        acc, stars, side = [0] * v, [set() for _ in range(v)], [0] * v
        for r in g['roots']:
            need(r.get('coefficient', 1) == 1, 'mod-2 unit coefficients')
            for t in r['targets']:
                acc[t] ^= sup[r['node']]
                if r['kind'] == 'center':
                    stars[t].add(r['coordinate'])
                else:
                    side[t] ^= sup[r['node']]
        for e in self.k['entries']:
            for t in e['receivers']:
                acc[t] ^= (1 << e['carrier']) | (1 << e['passive'])
                side[t] ^= (1 << e['carrier']) | (1 << e['passive'])
        for t in range(v):
            need(acc[t] == 1 << t, 'decoder identity at target %d' % t)
            need(stars[t] == set(lab[t]), 'stars read by target %d' % t)
            orth = sum(1 << s for s in range(v) if len(lab[s] & lab[t]) == 1)
            need(side[t] == orth, 'side part = sum over |S cap T| = 1 at target %d' % t)
        for r in g['roots']:
            if r['kind'] == 'center':
                c = r['coordinate']
                need(sup[r['node']] == sum(1 << s for s in range(v) if c in lab[s]), 'star support %d' % c)

    # ---------------- geometry and chains
    def geometry(self):
        g, w, h, v = self.g, self.w, self.h, self.v
        lab = g['labels']
        chi = [tuple(1 if j in l else 0 for j in range(h)) for l in lab]
        cov = [tuple((3 if j in l else 0) - 1 for j in range(h)) for l in lab]
        nf = {int(k): f for k, f in w['node_frame'].items()}
        rf = w['root_frame']
        full = w['full_frame']
        need(self.dimf[full] == h, 'full frame')
        for s in range(v):
            f = w['source_frame'][s]
            need(self.dimf[f] == 1 and self.in_frame(chi[s], f), 'source line <chi_S>')
        args = g['args']
        for x, f in nf.items():
            if x < v:
                need(self.in_frame(chi[x], f), 'leaf label inside its frame')
            else:
                for y in args[x]:
                    need(self.sub(nf[y], f), 'operand frame inside node frame (%d <- %d)' % (x, y))
        loss = 0
        for j, r in enumerate(g['roots']):
            f = rf[j]
            need(self.sub(nf[r['node']], f), 'root node frame inside root frame %d' % j)
            if r['kind'] == 'center':
                c = r['coordinate']
                S = [chi[s] for s in range(v) if c in lab[s]]
                need(all(self.in_frame(x, f) for x in S) and rank(S, h) == self.dimf[f], 'centre frame = star span')
                loss += self.dimf[f]
            else:
                need(all(dot(cov[t], b) == 0 for t in r['targets'] for b in self.B[f]), 'root frame inside caps')
                need(self.dimf[f] == h - rank([cov[t] for t in r['targets']], h), 'root frame = common cap')
        need(loss == self.prof['loss'], 'copied-centre loss')
        self.chi, self.cov, self.nf, self.rf = chi, cov, nf, rf

    def chains(self):
        """Role chains of the physical word and target chains; returns the recounted child histogram."""
        g, w, h, v = self.g, self.w, self.h, self.v
        nf, rf, full = self.nf, self.rf, w['full_frame']
        ops, rootroles = w['ops'], w['rootroles']
        R = 1 + max(max(a, b) for a, b, _ in ops)
        R = max(R, 1 + max(rootroles), 1 + max(w['sources'].values()))
        need(R == self.prof['R'], 'role count')
        start = {}
        for leaf, s in w['sources'].items():
            start[s] = w['source_frame'][int(leaf)]
        phase1 = set(w['phase1'])
        touched_p1 = set()
        for i in phase1:
            touched_p1.update(ops[i][:2])
        # phase one = closure of the centre roots' last ops under per-role precedence (recomputed)
        prev_op, pred = {}, []
        for i, (a, b, _) in enumerate(ops):
            pred.append((prev_op.get(a, -1), prev_op.get(b, -1)))
            prev_op[a] = prev_op[b] = i
        stack = [prev_op[s] for r, s in zip(g['roots'], rootroles) if r['kind'] == 'center' and s in prev_op]
        closure = set()
        while stack:
            i = stack.pop()
            if i not in closure:
                closure.add(i); stack.extend(j for j in pred[i] if j >= 0)
        need(closure == phase1, 'phase one is the centre closure')
        # conservative response support of every role (union incidence through the XOR word)
        co = [0] * R
        for j, (r, s) in enumerate(zip(g['roots'], rootroles)):
            for t in r['targets']:
                co[s] |= 1 << t
        for a, b, _ in reversed(ops):
            co[b] |= co[a]
        gauge_of = {}
        for z in w['gauges']:
            need(sum(1 << t for t in z['targets']) == co[z['role']], 'gauge targets = response support of its role')
            s = z['role']
            need(s not in start, 'gauged role is not a source role')
            need(s not in touched_p1, 'gauged role untouched in phase one')
            need(self.dimf[z['frame']] == z['dim'] and z['dim'] > 0, 'gauge dimension')
            need(self.nondeg(z['frame']), 'gauge frame nondegenerate')
            start[s] = z['frame']; gauge_of[s] = z
        seq = defaultdict(list)
        for i, (a, b, x) in enumerate(ops):
            f = nf[x]
            seq[a].append(f); seq[b].append(f)
        for j, s in enumerate(rootroles):
            seq[s].append(rf[j])
        H = Counter()
        for s in range(R):
            chain = [start.get(s)] + seq[s] + [full]
            prev = chain[0]
            dprev = 0 if prev is None else self.dimf[prev]
            if prev is not None and s not in gauge_of:
                H[1] += 1          # source role: injection frame <chi_S> (entrance child of width 1)
            for f in chain[1:]:
                if prev is not None:
                    need(self.sub(prev, f), 'nested role chain (role %d)' % s)
                d = self.dimf[f]
                need(d >= dprev, 'ascending role chain (role %d)' % s)
                if d > dprev:
                    H[d - dprev] += 1
                prev, dprev = f, d
        for j, r in enumerate(g['roots']):
            if r['kind'] == 'center':
                H[self.dimf[rf[j]]] += 1   # copied-centre transform
        # partner-pair chronology
        src = Counter()
        lab = [set(l) for l in g['labels']]
        for e in self.k['entries']:
            c, d = e['carrier'], e['passive']
            need(len(lab[c] & lab[d]) == 1, 'carrier and passive orthogonal (H0-Gram I_2)')
            mf, cf = e['mix_frame'], e['deliver_frame']
            need(self.dimf[mf] == 2 and self.in_frame(self.chi[c], mf) and self.in_frame(self.chi[d], mf), 'mix frame = span{chi_c, chi_d}')
            need(self.nondeg(mf), 'mix frame nondegenerate')
            need(self.sub(mf, cf), 'mix frame inside the receivers shared cap')
            need(all(dot(self.cov[t], b) == 0 for t in e['receivers'] for b in self.B[cf]), 'delivery frame inside receiver caps')
            need(e['carrier_chain'][0] == w['source_frame'][c] and e['passive_chain'][0] == w['source_frame'][d], 'chains start at source lines')
            need(e['carrier_chain'][1:] == [mf, cf, w['full_frame']] and e['passive_chain'][1:] == [mf, w['full_frame']], 'chain shape')
            for ch in (e['carrier_chain'], e['passive_chain']):
                for f1, f2 in zip(ch, ch[1:]):
                    need(self.sub(f1, f2), 'nested source-register chain')
                for f1, f2 in zip(ch, ch[1:]):
                    src[self.dimf[f2] - self.dimf[f1]] += 1
        # target chains: gauge reads (time order = reverse selection order), side caps in root order,
        # partner-pair delivery at the level-2 cap right after its root, final cap
        events = defaultdict(list)
        for z in reversed(w['gauges']):
            for t in z['targets']:
                events[t].append(z['frame'])
        deliveries = defaultdict(list)
        for e in self.k['entries']:
            deliveries[e['deliver_after_root']].append(e)
        for j, r in enumerate(g['roots']):
            if r['kind'] == 'center':
                continue
            for t in r['targets']:
                events[t].append(rf[j])
            for e in deliveries.get(j, []):
                need(sorted(e['receivers']) == sorted(r['targets']), 'delivery after the receivers own level-2 root')
                for t in e['receivers']:
                    events[t].append(e['deliver_frame'])
        Y = Counter()
        cap = {}
        for t in range(v):
            capf = None
            prev, dprev = None, 0
            for f in events[t]:
                if prev is not None:
                    need(self.sub(prev, f), 'nested target chain (target %d)' % t)
                need(all(dot(self.cov[t], b) == 0 for b in self.B[f]), 'target frame inside cap (target %d)' % t)
                if self.dimf[f] > dprev:
                    Y[self.dimf[f] - dprev] += 1
                prev, dprev = f, self.dimf[f]
            need(dprev <= h - 1, 'target chain below the cap')
            Y[h - 1 - dprev] += 1 if h - 1 - dprev else 0
        # every source register is in exactly one mixing pair
        members = Counter()
        for e in self.k['entries']:
            members[e['carrier']] += 1; members[e['passive']] += 1
        need(all(members[s] == 1 for s in range(v)), 'each source in exactly one partner pair')
        for f in set(self.nf.values()) | set(self.rf):
            need(self.nondeg(f), 'G-nondegenerate frame %d' % f)
        return H, Y, src, R

    # ---------------- replay
    def replay(self, seeds=3):
        g, w, v = self.g, self.w, self.v
        ops, rootroles = w['ops'], w['rootroles']
        R = self.prof['R']
        srcmap = {int(k): s for k, s in w['sources'].items()}
        roots = g['roots']
        for seed in range(seeds):
            rng = random.Random(1000 + seed)
            x = [rng.getrandbits(1) for _ in range(v)]
            y0 = [rng.getrandbits(1) for _ in range(v)]
            z0 = [rng.getrandbits(1) for _ in range(R)]
            X, Yv, z = x[:], y0[:], z0[:]
            # y <- y - J M z (old-value response of the dirty scratch)
            zd = z0[:]
            for a, b, _ in ops:
                zd[a] ^= zd[b]
            for j, r in enumerate(roots):
                for t in r['targets']:
                    Yv[t] ^= zd[rootroles[j]]
            for leaf, s in srcmap.items():      # z <- z + V x  (at the rank-one source lines)
                z[s] ^= X[leaf]
            for a, b, _ in ops:                  # z <- M z
                z[a] ^= z[b]
            for j, r in enumerate(roots):        # y <- y + J z
                for t in r['targets']:
                    Yv[t] ^= z[rootroles[j]]
            for e in self.k['entries']:          # partner-pair sums on the source registers
                if not e.get('skip_mix'):
                    X[e['carrier']] ^= X[e['passive']]
                for t in e['receivers']:
                    Yv[t] ^= X[e['carrier']]
            for e in self.k['entries']:          # undo at the full frame
                if not e.get('skip_mix'):
                    X[e['carrier']] ^= X[e['passive']]
            for a, b, _ in reversed(ops):        # z <- M^-1 z
                z[a] ^= z[b]
            for leaf, s in srcmap.items():       # z <- z - V x
                z[s] ^= X[leaf]
            need(all(Yv[t] == y0[t] ^ x[t] for t in range(v)), 'replay: y = y0 + x (seed %d)' % seed)
            need(z == z0 and X == x, 'replay: scratch and sources restored (seed %d)' % seed)

    def run(self):
        nfr = self.frames()
        self.decoder()
        self.geometry()
        H, Y, src, R = self.chains()
        self.replay()
        h, v = self.h, self.v
        m, W = 3 * h, 2 * v + R
        C = Counter()
        for part in (H, Y, src):
            for r, c in part.items():
                if r and c:
                    C[r] += 3 * c
        for z in self.w['gauges']:
            C[3 * z['dim']] += 1
        C[2] += 2 * v
        saved = {int(k): c for k, c in self.prof['child_histogram'].items()}
        need(dict(C) == saved, 'independent recount equals the saved child histogram')
        mass = sum(r * c for r, c in C.items())
        need(W == self.prof['W_per_vertex'] and W * m - mass == 2 * v - 3 * self.prof['loss'] == self.prof['deficit_per_vertex'],
             'W = 2v + R and deficit 2v - 3 ell')
        return dict(frames=nfr, roles=R, W=W, m=m, deficit=W * m - mass, children=sum(C.values()))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dir', type=Path, default=Path(__file__).resolve().parent / 'out')
    ap.add_argument('--p', type=int, default=12)
    ap.add_argument('--no-controls', action='store_true')
    a = ap.parse_args()
    res = Checker(a.dir, a.p).run()
    print('PASS p=%d: %s' % (a.p, res))
    if a.no_controls:
        return
    for m in ('broken_mix', 'outside_cap', 'below_level', 'dropped_star', 'non_nested'):
        try:
            Checker(a.dir, a.p, mutate=m).run()
        except Fail as e:
            print('control %-13s REJECTED: %s' % (m, e))
            continue
        raise SystemExit('FAIL: control %s was accepted' % m)
    print('PASS: all 5 mutation controls rejected')


if __name__ == '__main__':
    main()
