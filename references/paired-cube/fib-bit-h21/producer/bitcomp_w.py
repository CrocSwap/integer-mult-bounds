#!/usr/bin/env python3
"""Weighted automatic compile for round-seven-style bit side programs: a companion to bitcomp.py.

bitcomp.py's automatic choices lose about 2.8% of first-order a_b against round seven's shipped schedule on round
seven's own DAG (links 2.1 points, late copies 0.35, lifted set 0.3). This file replaces the three choices and keeps
every other step of bitcomp's pipeline (slots, op placement, B-defer, V leaves, PR #117's one-child list).
phi(t) = t ln(m/t) is the first-order weight of a child of width t; ext = phi(m - h).

1. links (weighted_links): one pass in decreasing schedule order, as bitcomp.greedy_links (when donor x is decided
   every later reach is final, so a link is checked valid with reach followed through links). Each donor takes the
   free valid use with the best score own(u) + phi(h - d_x) - phi(d_u - d_x): the slot the use would otherwise need,
   started at about its frame d_u (phi(m - h + d_u) if that slot can be deferred, i.e. the use reaches no retained
   root, else ext + phi(d_u)), plus the donor's sink step, minus the link step. The pass records every valid
   (donor, use, score) edge, taken uses included; a maximum-weight matching (SciPy LAPJVsp, one dummy per donor)
   then reassigns the uses, and a second pass keeps each matched link while it is still valid (on round seven's DAG
   all of them: 38874 links, the maximum matching of evaluate.py). Two rounds.
2. late copies (beneficial_late): a node with >= 2 free uses gets a late list (uses ordered by frame dimension,
   every intersection frame nonzero and nondegenerate) only when its first-order slot cost is lower than with early
   copies, with no deferral credit for the higher starts.
3. lifted set (lifted_set): bitcomp.auto_lifted's rule, plus plain frames span(n) for every addition with span
   dim <= 8 (closed under slot predecessors). Round seven's plain set is 92% of its span-dim-2 and -3 additions;
   the threshold 8 is the best of 0..16 on round seven's DAG and on lane C's best DAG (5..8 within 0.01%).

bdefer below is bitcomp.bdefer with one change: G-nondegeneracy of a frame ker(K) is tested on whichever side is
smaller (ker K with gram_rank, or the dual Gram (9-h) K K^T + (K1)(K1)^T on K's rows; the two are equivalent because
G is nondegenerate on Q^h for h != 9). It is about 10x faster, and the forced shipped schedule reproduces bitcomp's
a_b exactly (python bitcomp_w.py <witness> --choice SSS).
"""
import os, math, os, sys, time
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bitcomp as bc
from linalg_p import Span, span_of, kernel, gram_rank, P


def log(*a):
    print('[%7.1fs]' % (time.time() - T0), *a, flush=True)


T0 = time.time()
STRICT_LINKS = os.environ.get('STRICT_LINKS', '0') == '1'


# ------------------------------------------------------------------------------------ nondegeneracy
def nondeg(K):
    """G = I - J/9 nondegenerate on the frame ker(K) (K a Span of covectors); same answer as
    gram_rank(kernel(K)) == len(kernel(K)). For r = len(K) < h - r it tests the r x r dual Gram matrix
    K G^{-1} K^T, proportional to (9 - h) K K^T + (K 1)(K 1)^T."""
    h, r = K.h, len(K)
    if 2 * r >= h or h == 9:
        B = kernel(K)
        return gram_rank(B) == len(B)
    rows = K.vectors()
    s = [sum(x) % P for x in rows]
    c = 9 - h
    M = [[(c * sum(a * b for a, b in zip(rows[i], rows[j])) + s[i] * s[j]) % P for j in range(r)] for i in range(r)]
    return len(span_of(r, M)) == r


# ------------------------------------------------------------------------------------ B-defer (bitcomp's, faster)
def bdefer(pr, sl, fr, log=print):
    """bitcomp.bdefer with the nondegeneracy test above; returns the same dict."""
    h, v, R = pr.h, pr.v, sl['R']
    chains, hold = sl['chains'], sl['hold']
    L = bc.place_ops(pr, sl)
    touch = lambda o: (o[1], o[2])
    prev = {}
    pred = defaultdict(list)
    last = {}
    for i, o in enumerate(L):
        for s in touch(o):
            if s in prev:
                pred[i].append(prev[s])
            prev[s] = i
            last[s] = i
    ret_slots = [s for s in range(R) if chains[s][-2][0] == 'ret']
    assert len(ret_slots) == h
    phase1, st = set(), [last[s] for s in ret_slots]
    while st:
        i = st.pop()
        if i not in phase1:
            phase1.add(i)
            st.extend(pred[i])
    touched = set()
    for i in phase1:
        touched.update(touch(L[i]))
    cov = [0] * R
    tid = pr.tid
    for s in range(R):
        k = chains[s][-2]
        if k[0] == 'out':
            cov[s] = 1 << tid[k[2]]
        elif k[0] == 'ret':
            cov[s] = sum(1 << t for t, T in enumerate(pr.trip) if k[1] in T)
    for o in reversed(L):
        if o[0] == 'add':
            cov[o[2]] |= cov[o[1]]
        else:
            cov[o[1]] |= cov[o[2]]
    leaf_slots = defaultdict(list)
    for s in range(R):
        if pr.args[hold[s][0]] is None:
            leaf_slots[hold[s][0]].append(s)
    vK, vdim = {}, {}
    nfall = 0
    for n, ss in leaf_slots.items():
        ss.sort(key=lambda s: (pr.gpos.get(hold[s][1], 10 ** 9) if len(hold[s]) > 1 else 10 ** 9, s))
        acc = Span(h)
        for s in reversed(ss):
            acc = acc.copy().add_span(fr.K(chains[s][2]))
            if nondeg(acc):
                vK[s], vdim[s] = acc, h - len(acc)
            else:
                vK[s], vdim[s] = fr.K(('n', n)), 1
                nfall += 1
    log('V leaves: %d use slots, %d fall back to <t_S>' % (len(vdim), nfall))

    def startK(s):
        return vK[s] if s in vK else fr.K(chains[s][1])

    def startdim(s):
        return vdim[s] if s in vdim else fr.dim(chains[s][1])
    cand = {}
    nd_deg = 0
    targets_of = {}
    for s in range(R):
        if s in touched or not cov[s]:
            continue
        K = startK(s).copy()
        ts = []
        m = cov[s]
        while m:
            b = m & -m
            t = b.bit_length() - 1
            ts.append(t)
            if len(K) < h:
                K.insert(pr.wout[pr.trip[t]])
            m ^= b
        if len(K) == h:
            continue
        if not nondeg(K):
            nd_deg += 1
            continue
        cand[s] = K
        targets_of[s] = ts
    chainT = defaultdict(dict)
    placed = {}

    def sup_of(KA, KB):
        return all(KB.contains(r) for r in KA.vectors())
    for s in sorted(cand, key=lambda s: (len(cand[s]), s)):
        K = cand[s]
        changed = True
        while changed and len(K) < h:
            changed = False
            d = h - len(K)
            for t in targets_of[s]:
                ch = chainT[t]
                if not ch:
                    continue
                lower = max((e for e in ch if e < d), default=None)
                upper = min((e for e in ch if e >= d), default=None)
                for e, need in ((lower, 'X>=B'), (upper, 'X<=B')):
                    if e is None:
                        continue
                    KB = ch[e]
                    ok = sup_of(K, KB) if need == 'X>=B' else sup_of(KB, K)
                    if not ok:
                        K = K.copy().add_span(KB)
                        changed = True
                        break
                if changed or len(K) == h:
                    break
        if len(K) == h:
            continue
        if not nondeg(K):
            continue
        placed[s] = K
        for t in targets_of[s]:
            chainT[t][h - len(K)] = K
    undef = 0
    changed = True
    while changed:
        changed = False
        for n, ss in leaf_slots.items():
            early_max = max((vdim[s] for s in ss if s not in placed), default=0)
            for s in ss:
                if s in placed and vdim[s] < early_max:
                    del placed[s]
                    undef += 1
                    changed = True
    if undef:
        log('un-deferred %d leaf slots to keep X_S chains nested' % undef)
    f = [0] * R
    for s, K in placed.items():
        f[s] = h - len(K)
    dset = [s for s in range(R) if f[s]]
    log('phase one: %d ops of %d; untouched slots %d; deferred %d (degenerate intersections %d)' % (
        len(phase1), len(L), R - len(touched), len(dset), nd_deg))
    lev = defaultdict(set)
    for s in dset:
        m = cov[s]
        while m:
            b = m & -m
            lev[b.bit_length() - 1].add(f[s])
            m ^= b
    ylev = {t: sorted(lev[t]) for t in range(v)}
    xdata = []
    for n, ss in leaf_slots.items():
        early = sorted(startdim(s) for s in ss if not f[s])
        late_ = sorted(startdim(s) for s in ss if f[s])
        ds = [1] + early + late_ + [h]
        ds = [d for i, d in enumerate(ds) if i == 0 or d != ds[i - 1]]
        xdata.append([b - a for a, b in zip(ds, ds[1:])])
    chain_dims = []
    for s in range(R):
        ds = [f[s], startdim(s)] + [fr.dim(k) for k in chains[s][2:]]
        chain_dims.append(ds)
    return dict(f=f, ylev=ylev, xdata=xdata, chain_dims=chain_dims, deferred=len(dset), phase1=len(phase1),
                cov=cov, vdim=vdim, placedK=placed)


# ------------------------------------------------------------------------------------ first-order weights
def phi_of(m):
    """first-order weight of a child of width t: t ln(m/t) (0 for t <= 0)."""
    return lambda t: t * math.log(m / t) if t > 0 else 0.0


# ------------------------------------------------------------------------------------ links
def root_masks(pr):
    """star[c]: triples containing c; good[T]: triples S with |S cap T| = 1; sup[n]: support bitmask of node n."""
    h, v = pr.h, pr.v
    star = [0] * h
    for i, S in enumerate(pr.trip):
        for a in S:
            star[a] |= 1 << i
    good = {}
    for T in pr.trip:
        a, b, c = (star[x] for x in T)
        good[T] = (a ^ b ^ c) & ~((a & b) | (a & c) | (b & c))
    sup = {}
    for n in pr.order:
        sup[n] = (1 << pr.tid[pr.leafT[n]]) if pr.args[n] is None else sup[pr.args[n][0]] | sup[pr.args[n][1]]
    return star, good, sup


def link_score(pr):
    """first-order saving of the link x -> u = (y, k) at the moment x is decided (later frames final):
    own(u) + phi(h - d_x) - phi(d_u - d_x), d_x the donor's frame with the link, d_u the use's frame.
    own(u) = cost of the slot the use would need without the link, started at about d_u: deferrable (the use does
    not reach a retained root) phi(m - h + d_u), else phi(m - h) + phi(d_u)."""
    h = pr.h
    m = h * h
    phi = phi_of(m)

    def score(du, dx1, ret_u):
        own = (phi(m - h) + phi(du)) if ret_u else phi(m - h + du)
        return own + phi(h - dx1) - phi(du - dx1)
    return score


_SPANS = {}


def strict_ok(pr, x, t):
    """check_lifted's link criterion: span(x) <= span(t)."""
    key = (id(pr), t)
    if key not in _SPANS:
        _SPANS[key] = span_of(pr.h, [pr.tvec[s] for s in pr.bas[t]])
    St = _SPANS[key]
    return all(St.contains(pr.tvec[s]) for s in pr.bas[x])


def link_pass(pr, prefer=None, record=False, log=print):
    """one pass in decreasing schedule order. When donor x is reached every later node's reach (and frame) is final,
    so a link x -> (y, k) is valid exactly when every triple of x is G-orthogonal to every root reachable from the
    use through gates and links (bitmask test, as in bitcomp.auto_links, with reach through links). x takes the
    free valid use with the best link_score; with prefer (x -> use, e.g. a matching) x takes its preferred use when
    still free and valid, and a preferred use stays reserved until its donor has been decided.
    record: also return every valid (donor, use, score) edge seen, free or already taken."""
    h, v = pr.h, pr.v
    star, good, sup = root_masks(pr)
    full = (1 << v) - 1
    score = link_score(pr)
    K, allowed, hasret = {}, {}, {}
    taken = set()
    links = {}
    edges = []
    held = {u: x for x, u in prefer.items()} if prefer else {}

    def uK(u):
        return K[u[1]] if u[0] == 'gate' else bc.use_K(pr, K, u)

    def uallowed(u):
        return allowed[u[1]] if u[0] == 'gate' else good[u[1][1]] if u[0] == 'out' else star[u[1]]

    def uret(u):
        return hasret[u[1]] if u[0] == 'gate' else u[0] == 'ret'
    for x in reversed(pr.order):
        K0 = Span(h)
        al = full
        hr = False
        for u in pr.users[x]:
            K0.add_span(uK(u))
            al &= uallowed(u)
            hr = hr or uret(u)
        if pr.args[x] is not None:
            best = None
            pref = prefer.get(x) if prefer else None
            for y in pr.args[x]:
                for k, u in enumerate(pr.users[y]):
                    if u[0] == 'gate' and (u[1] == x or not pr.key(x) < pr.key(u[1])):
                        continue
                    if sup[x] & ~uallowed(u):
                        continue
                    if STRICT_LINKS and u[0] == 'gate' and not strict_ok(pr, x, u[1]):
                        continue
                    free = (y, k) not in taken
                    if not free and not record:
                        continue
                    hd = held.get((y, k))
                    Ku = uK(u)
                    K1 = K0.copy().add_span(Ku)
                    sc = score(h - len(Ku), h - len(K1), uret(u))
                    if record:
                        edges.append((x, y, k, sc))
                    if not free or (hd is not None and hd != x):
                        continue
                    key = (pref == (y, k), sc)
                    if best is None or key > best[0]:
                        best = (key, y, k, K1, u)
            if pref is not None:
                held.pop(pref, None)
            if best is not None:
                _, y, k, K1, u = best
                links[x] = (y, k)
                taken.add((y, k))
                K0 = K1
                al &= uallowed(u)
                hr = hr or uret(u)
        K[x] = K0
        allowed[x] = al
        hasret[x] = hr
    return links, edges


def max_weight_matching(edges, log=print):
    """maximum-weight matching of donors to uses over the recorded edges (scores > 0), with a private dummy column
    per donor so that a donor may stay unmatched (SciPy's LAPJVsp)."""
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import min_weight_full_bipartite_matching
    best = {}
    for x, y, k, w in edges:                      # one weight per (donor, use): the latest record wins
        if w > 0:
            best[(x, (y, k))] = w
    donors = sorted({x for x, _ in best})
    did = {x: i for i, x in enumerate(donors)}
    uses = sorted({u for _, u in best})
    uid = {u: i for i, u in enumerate(uses)}
    nd, nu = len(donors), len(uses)
    rows = [did[x] for x, _ in best] + list(range(nd))
    cols = [uid[u] for _, u in best] + [nu + i for i in range(nd)]
    ws = list(best.values()) + [1e-9] * nd
    G = csr_matrix((np.array(ws, dtype=float), (np.array(rows), np.array(cols))), shape=(nd, nu + nd))
    r, c = min_weight_full_bipartite_matching(G, maximize=True)
    match = {donors[i]: uses[j] for i, j in zip(r, c) if j < nu}
    log('matching: %d donors, %d uses, %d edges -> %d matched' % (nd, nu, len(best), len(match)))
    return match


def weighted_links(pr, rounds=2, log=print):
    """greedy weighted pass, then `rounds` times: maximum-weight matching over every valid edge seen in the last
    pass, and a validation pass that keeps each matched link while it is still valid with reach through links."""
    links, edges = link_pass(pr, record=True, log=log)
    log('weighted pass: %d links' % len(links))
    for it in range(rounds):
        match = max_weight_matching(edges, log)
        links, edges = link_pass(pr, prefer=match, record=it < rounds - 1, log=log)
        kept = sum(1 for x, u in match.items() if links.get(x) == u)
        log('validated: %d links (%d of %d matched links kept)' % (len(links), kept, len(match)))
    return links


def check_links(pr, links, Kn):
    """every link x -> (y, k) valid with reach through links: span(x) inside the frame of the use."""
    bad = 0
    for x, (y, k) in links.items():
        Ku = bc.use_K(pr, Kn, pr.users[y][k])
        if any(any(sum(a * b for a, b in zip(r, pr.tvec[t])) % P for t in pr.bas[x]) for r in Ku.vectors()):
            bad += 1
    return bad


# ------------------------------------------------------------------------------------ late copies
def beneficial_late(pr, links, fr, margin=0.0):
    """a late list (free uses ordered by frame dimension, every intersection frame nonzero and nondegenerate) for a
    node only when its first-order slot cost is lower than with early copies:
      early: pivot d_n -> M(first free use); each other use a copy  ext + phi(d_n) + phi(M_u - d_n)
      late:  pivot d_n -> C_1 -> ... -> C_{k-1} -> M(l_k); copy i  ext + phi(C_i) + phi(M(l_i) - C_i)
    (no deferral credit: crediting the higher starts of late copies with deferral selects too many lists)."""
    h = pr.h
    m = h * h
    phi = phi_of(m)
    ext = phi(m - h)
    linked = {r: x for x, r in links.items()}
    late = {}
    for n in pr.order:
        if pr.args[n] is None:
            continue
        ks = [k for k in range(len(pr.users[n])) if (n, k) not in linked]
        if len(ks) < 2:
            continue
        d = fr.dim(('n', n))
        M = {k: fr.dim(fr.ukey(n, k)) for k in ks}
        early = phi(M[ks[0]] - d) + sum(ext + phi(d) + phi(M[k] - d) for k in ks[1:])
        lt = sorted(ks, key=lambda k: (M[k], k))
        C = []
        for i in range(len(lt) - 1):
            K = fr.K(('c', n, tuple(lt[i:])))
            if len(K) == h or not nondeg(K):
                break
            C.append(h - len(K))
        if len(C) < len(lt) - 1:
            continue
        chain = [d] + C + [M[lt[-1]]]
        cost = sum(phi(b - a) for a, b in zip(chain, chain[1:]))
        cost += sum(ext + phi(C[i]) + phi(M[lt[i]] - C[i]) for i in range(len(lt) - 1))
        if cost < early - margin:
            late[n] = ([], lt)
    return late


# ------------------------------------------------------------------------------------ lifted set
def lifted_set(pr, Kn, links, plain_dn=8):
    """bitcomp.auto_lifted's rule (lift every addition whose U_n is nondegenerate; the plain set, frame span(n), is
    closed under slot predecessors), and also plain every addition of span dim <= plain_dn whose span and whose
    slot predecessors' spans are all nondegenerate (so the threshold never adds a degenerate plain frame).
    Returns (lifted, number plain, number of degenerate plain frames)."""
    preds = defaultdict(list)
    for n in pr.order:
        if pr.args[n]:
            for x in pr.args[n]:
                preds[n].append(x)
    for x, (y, k) in links.items():
        u = pr.users[y][k]
        if u[0] == 'gate':
            preds[u[1]].append(x)
    spanok = {}
    for n in pr.order:                            # slot predecessors come earlier in the schedule order
        if pr.args[n] is not None and pr.dn[n] <= plain_dn:
            B = [pr.tvec[t] for t in pr.bas[n]]
            spanok[n] = gram_rank(B) == len(B) and all(spanok.get(x, False) for x in preds[n] if pr.args[x])
    plain = set()
    for n in pr.order:
        if pr.args[n] is None:
            continue
        if spanok.get(n) or not nondeg(Kn[n]):
            plain.add(n)
    st = list(plain)
    while st:
        t = st.pop()
        for x in preds[t]:
            if pr.args[x] is not None and x not in plain:
                plain.add(x)
                st.append(x)
    bad = sum(1 for n in plain if gram_rank([pr.tvec[t] for t in pr.bas[n]]) < len(pr.bas[n]))
    return {n for n in pr.order if pr.args[n] is not None and n not in plain}, len(plain), bad


# ------------------------------------------------------------------------------------ pipeline
def first_order(profile):
    """(a, E) of a profile dict: a = (N - L) / sum_t n_t t ln(m/t)."""
    m = profile['m']
    E = sum(n * int(t) * math.log(m / int(t)) for t, n in profile['child_multiplicities'].items())
    return (profile['N'] - profile['L']) / E, E


def compile_program(pr, links=None, late=None, lifted=None, rounds=2, plain_dn=8, margin=0.0, log=print):
    """full pipeline -> one-child list and statistics (same result dict as bitcomp.compile_program). Any of links,
    late, lifted may be given (e.g. round seven's shipped choices); the others are chosen automatically."""
    if links is None:
        links = weighted_links(pr, rounds=rounds, log=log)
    Kn = bc.node_frames(pr, links)
    if lifted is None:
        lifted, nplain, nbad = lifted_set(pr, Kn, links, plain_dn=plain_dn)
        log('lifted %d additions, plain %d (degenerate plain frames %d)' % (len(lifted), nplain, nbad))
    fr = bc.Frames(pr, Kn, lifted)
    if late is None:
        late = beneficial_late(pr, links, fr, margin=margin)
        log('late decisions: %d nodes' % len(late))
    return compile_forced(pr, links, late, lifted, log=log, Kn=Kn, fr=fr)


def compile_forced(pr, links, late, lifted, log=print, Kn=None, fr=None):
    """bitcomp.compile_program for given links, late decisions and lifted set, with the faster bdefer."""
    if Kn is None:
        Kn = bc.node_frames(pr, links)
    if fr is None:
        fr = bc.Frames(pr, Kn, lifted)
    sl = bc.compile_slots(pr, links, late)
    log('R = %d (%.4f v)' % (sl['R'], sl['R'] / pr.v))
    bd = bdefer(pr, sl, fr, log)
    oc = bc.one_child(pr, sl['R'], bd)
    log('one-child list: %d children, rank %d vs s %d, decreasing chains %d' % (
        sum(oc['z'].values()), oc['rank'], oc['s'], oc['decreasing_chains']))
    degenerate_plain = sum(1 for n in pr.act if pr.args[n] is not None and n not in lifted
                           and gram_rank([pr.tvec[t] for t in pr.bas[n]]) < len(pr.bas[n]))
    return dict(R=sl['R'], links=len(links), late=len(late), lifted=len(lifted), deferred=bd['deferred'],
                profile=dict(h=pr.h, m=oc['m'], W=oc['W'], N=oc['N'], L=oc['L'], total_rank=oc['s'],
                             child_multiplicities={str(t): n for t, n in oc['z'].items()}),
                ok=oc['rank'] == oc['s'] and not oc['decreasing_chains'], invalid_links=check_links(pr, links, Kn),
                degenerate_plain=degenerate_plain, chosen=dict(links=links, late=late, lifted=lifted))


def shared_a(pr, profile):
    """evaluate_ab --shared: a_b with sunflower-shared exteriors (the same transform as evaluate_ab.py)."""
    h, m, v = pr.h, profile['m'], pr.v
    g = (h - 1) // 2
    if not (h % 2 and v % g == 0):
        return None
    ng = v // g
    a, E = first_order(profile)
    Es = E
    for t, n in profile['child_multiplicities'].items():
        t = int(t)
        if t >= m - h:
            roles, r = n // (2 * v), m - t
            Es -= n * t * math.log(m / t)
            if m - g * r > 0:
                Es += roles * 2 * ng * (m - g * r) * math.log(m / (m - g * r))
    return (profile['N'] - profile['L']) / Es


def main():
    import argparse, gzip, json
    ap = argparse.ArgumentParser(description='weighted automatic compile (or forced shipped choices on a witness)')
    ap.add_argument('path', help="round-seven witness (.json.gz) or the kit's DAG dump (run_producer.py)")
    ap.add_argument('--choice', default='AAA', help='links/late/lifted: S shipped (witness only), A automatic, '
                    'N no late copies; e.g. SSS reproduces the shipped schedule')
    ap.add_argument('--rounds', type=int, default=2, help='matching rounds after the weighted pass')
    ap.add_argument('--plain-dn', type=int, default=8, help='also keep plain every addition of span dim <= this')
    ap.add_argument('--margin', type=float, default=0.0, help='late list only when it saves more than this')
    ap.add_argument('--out', help='write the profile JSON here')
    ap.add_argument('-q', action='store_true')
    a = ap.parse_args()
    t0 = time.time()
    lg = (lambda *x: None) if a.q else log
    if a.path.endswith('.gz'):
        pr, links_s, late_s = bc.load_witness(a.path)
        lifted_s = {int(k) for k in json.load(gzip.open(a.path, 'rt'))['j']}
    else:
        pr, links_s, late_s, lifted_s = bc.load_dump(a.path), None, None, None
    c = a.choice.upper()
    if 'S' in c and links_s is None:
        sys.exit('shipped choices need a witness')
    links = links_s if c[0] == 'S' else None
    late = late_s if c[1] == 'S' else {} if c[1] == 'N' else None
    lifted = lifted_s if c[2] == 'S' else None
    res = compile_program(pr, links=links, late=late, lifted=lifted, rounds=a.rounds, plain_dn=a.plain_dn,
                          margin=a.margin, log=lg)
    p = res['profile']
    ab, E = first_order(p)
    if a.out:
        json.dump(p, open(a.out, 'w'))
    print(json.dumps(dict(choice=c, ok=res['ok'], h=pr.h, a_b=ab, a_b_shared=shared_a(pr, p), R=res['R'],
                          R_per_v=round(res['R'] / pr.v, 4), links=res['links'], invalid_links=res['invalid_links'],
                          degenerate_plain=res['degenerate_plain'],
                          late=res['late'], lifted=res['lifted'], deferred=res['deferred'],
                          children=sum(p['child_multiplicities'].values()), seconds=round(time.time() - t0, 1))),
          flush=True)


if __name__ == '__main__':
    main()


# ------------------------------------------------------------------------------------ plain link users
def fix_plain_links(pr, links, lifted, log=print):
    """a link x -> (y, k) continues y's slot from x's frame to the frame of y's k-th user t. Valid nesting needs
    span(x) <= M_t: automatic when t is lifted (U_t contains span(x) by link admissibility), but a plain t
    (M_t = span(t)) must contain span(x). For each violation lift t and its slot-successor closure (the lifted set is
    closed under slot successors) when all their U frames are nondegenerate, otherwise drop the link; recompute
    the node frames and repeat until stable. Returns (links, lifted, Kn, stats)."""
    links, lifted = dict(links), set(lifted)
    spans = {}

    def span(n):
        if n not in spans:
            spans[n] = span_of(pr.h, [pr.tvec[s] for s in pr.bas[n]])
        return spans[n]
    nl = nd = rounds = 0
    while True:
        rounds += 1
        Kn = bc.node_frames(pr, links)
        sc, pc = defaultdict(set), defaultdict(set)
        for n in pr.order:
            if pr.args[n]:
                for a in pr.args[n]:
                    sc[a].add(n); pc[n].add(a)
        for x, (y, k) in links.items():
            u = pr.users[y][k]
            if u[0] == 'gate':
                sc[x].add(u[1]); pc[u[1]].add(x)
        # lifted frames must stay nondegenerate under the current links; the plain set stays predecessor-closed
        bad = [n for n in lifted if not nondeg(Kn[n])]
        st = list(bad)
        while st:
            n = st.pop()
            if n in lifted:
                lifted.discard(n)
                st.extend(pc[n])
        changed = bool(bad)
        for x, (y, k) in sorted(links.items()):
            u = pr.users[y][k]
            if u[0] != 'gate':
                continue
            t = u[1]
            inside = all(span(t).contains(pr.tvec[s]) for s in pr.bas[x])
            if inside:
                continue
            if STRICT_LINKS:                 # check_lifted's criterion: span(x) <= span(t) on every link
                del links[x]
                nd += 1
                changed = True
                continue
            if t in lifted:
                continue
            need, st = set(), [t]
            while st:
                n = st.pop()
                if n in need or n in lifted:
                    continue
                need.add(n)
                st.extend(sc[n])
            if all(pr.args[n] is not None and nondeg(Kn[n]) for n in need):
                lifted |= need
                nl += len(need)
            else:
                del links[x]
                nd += 1
            changed = True
        if not changed:
            break
    log('plain link users: lifted %d nodes, dropped %d links (%d rounds)' % (nl, nd, rounds))
    return links, lifted, Kn, dict(lifted_extra=nl, dropped=nd, rounds=rounds)
