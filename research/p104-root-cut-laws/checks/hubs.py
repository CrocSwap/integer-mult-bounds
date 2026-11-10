"""Theorem H and H' (THEOREM.md section 4) on the two all-pivot roots and on two words with an interior stage at t = -1.
Exact rational arithmetic, standard library only. Prints 'ok   ' lines and the marker PASS_HUBS."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sys
from fractions import Fraction as Fr
from common import req, ok, fail, finish, rank_q
from rootmodel import load_root, merged_word, rand_D, Root

ONE = lambda L: [Fr(1)] * L


def degenerate_Ds(L):
    yield 'D=1', ONE(L)
    yield 'D=-1', [Fr(-1)] * L
    yield 'D alternating +-1', [Fr(1 if k % 2 == 0 else -1) for k in range(L)]
    yield 'D_k = 2, 1/2 alternating', [Fr(2) if k % 2 == 0 else Fr(1, 2) for k in range(L)]
    for s in (1, 2, 3):
        yield 'random D seed %d' % s, rand_D(L, s)


def analyse(W, name, expect):
    """Verify the hypotheses on W, then Theorem H and H'. expect = dict of exact values recorded in THEOREM.md."""
    L, rho = W.L, W.rho
    # --- hypotheses: contract, H-R on LOCAL units, hub rank law (rank Z(D) = rho) at degenerate and random D
    cont = all(W.contract(D) for _, D in list(degenerate_Ds(L))[:2] + list(degenerate_Ds(L))[4:6])
    req(cont, '%s: M(D) = -diag(prod D^eps) exactly at D = 1, -1 and two random D' % name)
    req(W.hr(), '%s: H-R, every LOCAL unit lies inside its label mask' % name)
    ranks = {tag: rank_q(W.Z(D)) for tag, D in degenerate_Ds(L)}
    req(set(ranks.values()) == {rho}, '%s: rank Z(D) = N - n = %d at all %d tested D (1, -1, alternating, 2 and 1/2, random)' % (name, rho, len(ranks)))
    # --- labels, pivots
    rj, pivots = [], []
    for k, lab in enumerate(W.labels):
        us = lab['units']
        Zu = W.Z(ONE(L), units=us)                      # D-free: no Delta between the LOCAL units of one label
        rj.append(rank_q(Zu))
        if len(us) == rho and rj[-1] == rho:
            pivots.append(k)
    req(rj == expect['rj'], '%s: rank of the label blocks Z_UU, by label = %s' % (name, rj))
    req(pivots == expect['pivots'], '%s: pivot labels (rho LOCAL units, Z_UU invertible): %d of %d' % (name, len(pivots), L))
    f, l = pivots[0], pivots[-1]
    masks = [lab['mask'] for lab in W.labels]
    I_piv = set(range(W.n))
    for k in pivots:
        I_piv &= masks[k]
    I_hull = set(range(W.n))
    for k in range(f, l + 1):
        I_hull &= masks[k]
    req(sorted(I_piv) == expect['I_piv'], '%s: coordinates in every pivot mask of [%d, %d] = %s (Theorem H needs at least %d)' % (name, f, l, sorted(I_piv), rho))
    req(len(I_piv) >= rho, '%s: Theorem H holds, |pivot intersection| = %d >= rho' % (name, len(I_piv)))
    req(sorted(I_hull) == expect['I_hull'], '%s: coordinates in every mask of the hull [%d, %d] = %s' % (name, f, l, sorted(I_hull)))
    # --- proof ingredients on the hull ends f, l
    Uf, Ul = W.labels[f]['units'], W.labels[l]['units']
    Zfl1 = W.Zpoly_at(ONE(L), Uf, Ul)
    req(rank_q(Zfl1) == rho, '%s: Z_fl(1) is invertible (Schur step at the pivot l)' % name)
    zero_at = []
    for k in pivots:
        if k < l:
            E = ONE(L); E[k] = Fr(0)
            zero_at.append(all(v == 0 for row in W.Zpoly_at(E, Uf, Ul) for v in row))
    req(all(zero_at), '%s: Z_fl vanishes at E_k = 0 for each of the %d pivots k in [f, l): divisibility by E_k' % (name, len(zero_at)))
    # Schur identity at a pivot: Z_ab = Z_am Z_mm^-1 Z_mb, checked at a random D on all units
    D = rand_D(L, 11)
    Zall = W.Z(D)
    m = pivots[len(pivots) // 2]
    Um = W.labels[m]['units']
    Zmm = [[Zall[a][b] for b in Um] for a in Um]
    det = Zmm[0][0] * Zmm[1][1] - Zmm[0][1] * Zmm[1][0]
    inv = [[Zmm[1][1] / det, -Zmm[0][1] / det], [-Zmm[1][0] / det, Zmm[0][0] / det]]
    good = True
    for a in range(W.N):
        for b in range(W.N):
            S = sum(Zall[a][Um[i]] * inv[i][j] * Zall[Um[j]][b] for i in range(2) for j in range(2))
            if S != Zall[a][b]:
                good = False
    req(good, '%s: Schur complement of the pivot block %d vanishes on all %d x %d entries of Z(D) (random D)' % (name, m, W.N, W.N))
    # --- Theorem H' at every label of the hull, and the inequality behind it
    allok, ineq = True, True
    table = []
    for j in range(f + 1, l):
        Hj = masks[j] & I_piv
        if len(Hj) < rj[j]:
            allok = False
        E = ONE(L); E[j] = Fr(0)
        r0 = rank_q(W.Zpoly_at(E, Uf, Ul))
        if r0 > rho - rj[j]:
            ineq = False
        table.append((j, rj[j], len(Hj)))
    req(allok, "%s: Theorem H' at every interior label j of [%d, %d]: |M_j meets pivot intersection| >= rank Z_UU(j)" % (name, f, l))
    req(ineq, "%s: rank Z_fl(E_j = 0) <= rho - rank Z_UU(j) at every interior label (the step that proves H')" % name)
    tight = [t for t in table if t[1] < rho]
    return dict(f=f, l=l, I_piv=sorted(I_piv), I_hull=sorted(I_hull), interior=[(j, r, h) for j, r, h in tight], incidence=sum(len(m) for m in masks))


def main():
    base = load_root('root_t0_dsum.json')
    allpiv = list(range(18))
    exp_h = dict(rj=[2] * 18, pivots=allpiv, I_piv=[0, 1], I_hull=[0, 1])
    exp_0 = dict(rj=[2] * 18, pivots=allpiv, I_piv=[0, 20], I_hull=[0, 20])
    res_h = analyse(load_root('root_h.json'), 'root_h (t = -1/2, hosted)', exp_h)
    res_0 = analyse(base, 'root_t0 (t = 0, two chains)', exp_0)
    req(res_h['incidence'] == 216 and res_0['incidence'] == 216, 'all-pivot roots: total mask incidence 216 on both')
    # two chains with an interior Whitehead stage on chain A at label J, and on chain B at the last label
    merged = {}
    for J in (4, 7):
        W = merged_word(base, J)
        rj = [2] * 18
        rj[J] = 1
        rj[17] = 1
        piv = [k for k in range(18) if rj[k] == 2]
        exp = dict(rj=rj, pivots=piv, I_piv=[0, 20], I_hull=[0])
        res = analyse(W, 'merged J=%d (t = -1 at labels %d and 17)' % (J, J), exp)
        merged[J] = (W, res)
        req(res['interior'] == [(J, 1, 1)], 'merged J=%d: the only interior label with rank 1 is %d, and it holds exactly %d hub (needs >= 1)' % (J, J, 1))
        req(res['incidence'] == {4: 208, 7: 205}[J], 'merged J=%d: total mask incidence %d, below 216' % (J, res['incidence']))
        masks = [lab['mask'] for lab in W.labels]
        req(0 in masks[J] and 20 not in masks[J], 'merged J=%d: hub 20 lies in every pivot mask and is absent from the interior mask M_%d, hub 0 present' % (J, J))
    # --- the earlier, stronger form ("every mask of the hull") fails exactly there
    for J in (4, 7):
        res = merged[J][1]
        req(len(res['I_piv']) >= 2 and len(res['I_hull']) < 2, 'merged J=%d: the stronger form fails: %d coordinates in all pivot masks but only %d in all masks of the hull' % (J, len(res['I_piv']), len(res['I_hull'])))
    # --- failing controls
    W = merged_word(base, 4)
    masks = [lab['mask'] for lab in W.labels]
    bad = merged_word(base, 4)
    bad.labels[4]['mask'] = set(bad.labels[4]['mask']) - {0}      # drop hub 0 too: both hubs absent at the t = -1 label
    req(not bad.contract(rand_D(18, 5)), 'control: deleting hub 0 from M_4 as well breaks the contract (the word is no longer exact)')
    bad2 = merged_word(base, 4)
    bad2.labels[9]['mask'] = set(bad2.labels[9]['mask']) - {20}
    req(not bad2.contract(rand_D(18, 5)), 'control: deleting hub 20 from a pivot mask breaks the contract')
    # a word with a unit outside its mask must be flagged by the H-R check
    bad3 = merged_word(base, 4)
    bad3.labels[0]['mask'] = set(bad3.labels[0]['mask']) - {0}
    req(not bad3.hr(), 'control: the H-R check flags a LOCAL unit outside its mask')
    # the hub-rank hypothesis must be able to fail: a Z with one sign flipped has the wrong rank
    D = rand_D(18, 3)
    Z = W.Z(D)
    jj = next(j for j in range(1, W.N) if Z[0][j] != 0)
    Z[0][jj] = -Z[0][jj]
    req(rank_q(Z) > 2, 'control: a Z with one nonzero off-diagonal entry sign-flipped has rank above rho')
    finish('PASS_HUBS')


if __name__ == '__main__':
    main()
