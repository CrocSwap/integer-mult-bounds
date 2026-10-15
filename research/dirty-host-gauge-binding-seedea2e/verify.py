#!/usr/bin/env python3
"""Credit-binding checks for hosted dirty residuals in the scalar common-frame transport model.

Model: PR 1664 (https://github.com/CrocSwap/integer-mult-bounds/pull/1664)
PROOF.md sections 4-5, "scalar common-frame transport": registers hold formal
coefficient rows over Q; a transport of one register frame A -> B is charged
|nu(A)-nu(B)|; add/scale/copy at one common frame are free. The cut lemma is

    D_j >= dim(W_j^0 + span Q_j) - dim W_j^0                      (C-down)

with the symmetric high-side statement, and M >= sum_j (D_j + U_j).  The
conditional dirty-host corollary is M >= H_end + q*rank_K(S)                 (H)

for restored hosts and clean scatter Y' = Y + S X at height 0.

This script implements (C-down) and the crossing feasibility condition exactly,
and audits the *credit binding* of the idle-axis hosted-residual mechanism
(research/idle-axis-hosting/PROOF.md): which entry/exit gauges *suffice* to make
a hosting move operator-identical (sufficient legality hypotheses of the
inherited interface; not claimed necessary -- see the cancellation control
below), and how much mass a hosted pending factor may claim
credit for.  All checks are exact rational arithmetic; entry rows are
identity-basis rows (arbitrary dirty content), so row equality covers every
dirty input by linearity.

Aaron Wang, with help from opencode.  Apache-2.0.
"""

from fractions import Fraction
import sys

# ---------------------------------------------------------------- exact linear algebra


def rank(rows):
    m = [[Fraction(x) for x in r] for r in rows]
    if not m:
        return 0
    n = len(m[0])
    row = 0
    for col in range(n):
        piv = None
        for i in range(row, len(m)):
            if m[i][col] != 0:
                piv = i
                break
        if piv is None:
            continue
        m[row], m[piv] = m[piv], m[row]
        inv = Fraction(1) / m[row][col]
        m[row] = [x * inv for x in m[row]]
        for i in range(len(m)):
            if i != row and m[i][col] != 0:
                f = m[i][col]
                m[i] = [a - f * b for a, b in zip(m[i], m[row])]
        row += 1
        if row == len(m):
            break
    return row


def mod_rank(base, extra):
    return rank(base + extra) - rank(base)


def contained(base, rows):
    """True iff every row of `rows` lies in span(base)."""
    return mod_rank(base, rows) == 0


def vec(n, *ones):
    v = [0] * n
    for i in ones:
        v[i] = 1
    return v


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
            for i in range(len(a))]


def eye(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def shear(n, dst, src):
    m = eye(n)
    m[dst][src] = 1
    return m


# ---------------------------------------------------------------- region + cut engine


class Region:
    """A finite charged region.

    entry: list of (name, height, row) at the region entry (row = content as a
           coefficient row over the formal inputs; arbitrary dirty inputs are
           covered by taking entry rows as a basis).
    moves: list of (name, from_height, to_height, row_at_move): one-register
           transports; paid mass |delta| each; the row is what actually crosses.
    exits: list of (name, height, row) demanded at the region exit.
    """

    def __init__(self, entry, moves, exits):
        self.entry = entry
        self.moves = moves
        self.exits = exits

    def paid_mass(self):
        return sum(abs(t - f) for _, f, t, _ in self.moves)

    def crossings(self, j):
        """(D_j, U_j, rows_down, rows_up) at cut j."""
        d = u = 0
        down, up = [], []
        for _, f, t, r in self.moves:
            if f >= j > t:
                d += 1
                down.append(r)
            elif t >= j > f:
                u += 1
                up.append(r)
        return d, u, down, up

    def cut_report(self):
        """For every cut j: (need_low, D_j, rows_down, need_high, U_j, rows_up,
        W_low, W_high)."""
        heights = {h for _, h, _ in self.entry} | {t for _, _, t, _ in self.moves} \
            | {h for _, h, _ in self.exits} | {f for _, f, _, _ in self.moves}
        lo, hi = min(heights), max(heights)
        out = {}
        for j in range(lo, hi + 2):
            w_low = [r for _, h, r in self.entry if h < j]
            w_high = [r for _, h, r in self.entry if h >= j]
            q_low = [r for _, h, r in self.exits if h < j]
            q_high = [r for _, h, r in self.exits if h >= j]
            d, u, down, up = self.crossings(j)
            out[j] = (mod_rank(w_low, q_low), d, down,
                      mod_rank(w_high, q_high), u, up, w_low, w_high)
        return out

    def obstructions(self):
        """Violations of (C-down)/(C-up) and of crossing feasibility."""
        bad = []
        for j, (nl, d, down, nh, u, up, w_low, w_high) in sorted(self.cut_report().items()):
            if d < nl:
                bad.append(f"cut {j}: D_j={d} < demanded quotient rank {nl}")
            if u < nh:
                bad.append(f"cut {j}: U_j={u} < demanded quotient rank {nh}")
            q_low = [r for _, h, r in self.exits if h < j]
            q_high = [r for _, h, r in self.exits if h >= j]
            if not contained(w_low + down, q_low):
                bad.append(f"cut {j}: low-side exits not in span(W_j^0 + crossed rows)")
            if not contained(w_high + up, q_high):
                bad.append(f"cut {j}: high-side exits not in span(W_j^0 + crossed rows)")
        return bad


def report(name, ok, detail):
    print(("PASS" if ok else "FAIL"), name, "-", detail)
    if not ok:
        raise SystemExit(f"CHECK FAILED: {name}: {detail}")


# ---------------------------------------------------------------- checks


def check_smallest_falsifier():
    """Smallest double-duty borrow: one host row asked to carry both the centre
    direction and its own restoration. m=t=w=1, q=1, r=1, host 1->0.
    Inputs x (centre total), d (host dirt), y (target old value).
    """
    n = 3  # x, d, y
    x, d, y = vec(3, 0), vec(3, 1), vec(3, 2)
    entry = [("x", 1, x), ("d", 1, d), ("y", 0, y)]
    # hosted schedule: d += x at height 1 (free add), one descent 1->0
    crossed = [1, 1, 0]  # the row d+x crosses
    exits = [("y", 0, [1, 0, 1]), ("d", 0, [0, 1, 0])]  # y'=y+x; host restored
    hosted = Region(entry, [("d", 1, 0, crossed)], exits)
    bad = hosted.obstructions()
    report("double-duty-borrow-refuted", bool(bad),
           f"m=t=w=1: one crossing carries d+x and cannot also produce both "
           f"y'=y+x and the restored d; {bad}")

    # Absorbed endpoint, separate target demand survives: the host exits at d+x
    # (its prescribed advance), but the construction's data endpoint still
    # demands y'=y+x.  Refuted the same way: d+x alone cannot give y+x.
    exits_abs = [("y", 0, [1, 0, 1]), ("d", 0, [1, 1, 0])]
    hosted_abs = Region(entry, [("d", 1, 0, crossed)], exits_abs)
    bad = hosted_abs.obstructions()
    report("absorbed-endpoint-with-target-refuted", bool(bad),
           f"even when the host endpoint absorbs the direction, the separate "
           f"target row y'=y+x still owes its own crossing: {bad}")

    # Full absorption: no separate target demand at all (the family's advance IS
    # the delivery).  Feasible with M=1, and (H) no longer applies because the
    # clean-scatter and restoration obligations are absent from the contract.
    exits_free = [("d", 0, [1, 1, 0])]
    hosted_free = Region(entry, [("d", 1, 0, crossed)], exits_free)
    bad = hosted_free.obstructions()
    report("full-absorption-is-the-only-free-route", not bad,
           "with the host endpoint absorbing the direction and no separate target "
           "demand, M=1 passes (C-down); this drops the (H) scatter/restoration "
           "obligations and is exactly the endpoint-contract change that must be "
           "charged (see README)")


def check_operator_gauges():
    """The factor-move gauges as exact composed linear maps on d=3 coordinates.
    The hosted version applies I_mu' (the advance off the hosted block) followed
    by the moved factor; the gauges make that equal the original advance I_mu.
    Controls: escape, overlap order dependence, out-of-window touch.
    The gauges are sufficient legality hypotheses only: each control shows one
    hypothesis cannot simply be deleted, not that any of them is necessary for
    operator equality (see check_cancellation_control).
    """
    d = 3
    moved = shear(d, 0, 2)        # hosted pending factor on S'={0}
    ip = shear(d, 1, 2)           # I_mu' : the advance on S \ S', S={0,1}
    imu = matmul(moved, ip)       # the original advance, factored on S' then S\S'
    # Convention: total = later o earlier.  Original: moved at I1, then I_mu'
    # at I_mu.  Hosted: both applied at I_mu in the factor order that equals I_mu.
    total_orig = matmul(ip, moved)
    total_hosted = imu
    report("gauge-move-identity", total_orig == total_hosted,
           "the moved factor at I1 followed by I_mu' reproduces the advance exactly")
    # escape: the moved factor is not the advance's factor on S' (block outside S)
    escape = shear(d, 2, 1)
    report("gauge-escape-refuted", matmul(ip, escape) != imu,
           "a moved factor whose block escapes the pending set does not compose "
           "to the advance: the endpoint differs")
    # overlap: two moved factors on overlapping blocks do not commute
    m1, m2 = shear(d, 0, 1), shear(d, 1, 0)
    report("gauge-overlap-order-refuted", matmul(m1, m2) != matmul(m2, m1),
           "the exhibited overlapping hosted blocks are order-dependent; "
           "disjointness (count each pending factor once) is the inherited "
           "interface's sufficient premise for an order-free composition")
    # out-of-window touch: an intervening touch T between the residual write at
    # I1 and the advance at I_mu; hosting moves the factor past T
    T = shear(d, 2, 0)
    total_orig_w = matmul(ip, matmul(T, moved))
    total_hosted_w = matmul(imu, T)
    report("gauge-window-refuted", total_orig_w != total_hosted_w,
           "a single intervening touch that does not commute with the moved "
           "factor breaks the composition: the no-touch window is a sufficient "
           "premise, not a necessary one (see the cancellation control)")


def commute(a, b):
    return matmul(a, b) == matmul(b, a)


def check_cancellation_control():
    """Regression control: the sufficient-only hypotheses must NOT reject a
    genuine equality (reviewer's counterexample, PR 1837 comment 6173237648).

    Over Q take R = I + E01, T = I + E12, T^{-1} = I - E12.  Both T and T^{-1}
    fail to commute with R, so the sufficient window premise ("no intervening
    touch of the host", or "every intervening touch commutes with the moved
    factor") is not met in this instance; yet moving R across the consecutive
    touches T, T^{-1} preserves the complete operator:

        T^{-1} T R = R T^{-1} T = R.

    This is a genuine equality (the touches cancel as a composite), checked
    below with this package's composed-linear-map machinery (exact integer
    arithmetic on these entries).  The corrected condition is sufficient only,
    so it must accept this instance rather than reject it: premise failure is
    not an operator change, and cancellation-based routes stay open.
    """
    d = 3
    r = shear(d, 0, 1)                    # R = I + E01
    t = shear(d, 1, 2)                    # T = I + E12
    tinv = eye(d)
    tinv[1][2] = -1                       # T^{-1} = I - E12
    premise_met = commute(r, t) and commute(r, tinv)
    lhs = matmul(matmul(tinv, t), r)      # T^{-1} T R
    rhs = matmul(r, matmul(tinv, t))      # R T^{-1} T
    report("cancellation-touches-noncommuting", not premise_met,
           "T = I + E12 and T^{-1} = I - E12 each fail to commute with "
           "R = I + E01, so the sufficient window premise is not met here")
    report("cancellation-equality-not-rejected", (not premise_met) and lhs == rhs == r,
           "T^{-1} T R = R T^{-1} T = R = [[1,1,0],[0,1,0],[0,0,1]] exactly, so the "
           "sufficient-only condition must NOT reject this instance: absence of "
           "individually noncommuting touches is sufficient, not necessary, and "
           "cancellation-based routes remain open")


def check_engine_canonical():
    """The PR1664 section 5.2 arithmetic: two carriers, two restored hosts,
    q=r=2, host rows 2->0.  Baseline M = 8 = H_end(4) + q*r(4); a schedule
    claiming the same obligations in M=6 is refuted.
    """
    n = 6  # x1, x2, d1, d2, y1, y2
    entry = [("x1", 2, vec(6, 0)), ("x2", 2, vec(6, 1)),
             ("d1", 2, vec(6, 2)), ("d2", 2, vec(6, 3)),
             ("y1", 0, vec(6, 4)), ("y2", 0, vec(6, 5))]
    exits = [("y1", 0, [1, 0, 0, 0, 1, 0]), ("y2", 0, [0, 1, 0, 0, 0, 1]),
             ("d1", 0, vec(6, 2)), ("d2", 0, vec(6, 3))]
    base = Region(entry, [("x1", 2, 0, vec(6, 0)), ("x2", 2, 0, vec(6, 1)),
                          ("d1", 2, 0, vec(6, 2)), ("d2", 2, 0, vec(6, 3))], exits)
    bad = base.obstructions()
    report("canonical-bound-baseline", not bad and base.paid_mass() == 8,
           f"M=8 = H_end(4)+q*r(4) passes; obstructions: {bad}")
    mutant = Region(entry, [("x1", 2, 0, vec(6, 0)), ("x2", 2, 0, vec(6, 1)),
                            ("d1", 2, 0, vec(6, 2))], exits)
    bad = mutant.obstructions()
    report("canonical-bound-mutant-refuted", bool(bad),
           f"M<=6 mutant refuted: {bad}")


def check_prepositioned_dirt():
    """Pre-positioned dirt: the host's row was already copied below the cut at
    entry, so its descent earns no credit and the x direction stays unpaid.
    """
    n = 3  # x, d, y
    entry = [("x", 1, vec(3, 0)), ("d", 1, vec(3, 1)),
             ("d_copy", 0, vec(3, 1)),  # pre-positioned copy of d below the cut
             ("y", 0, vec(3, 2))]
    exits = [("y", 0, [1, 0, 1]), ("d", 0, [0, 1, 0])]  # y'=y+x, host restored
    region = Region(entry, [("d", 1, 0, vec(3, 1))], exits)
    cr = region.cut_report()
    need1 = cr[1][0]
    bad = region.obstructions()
    report("prepositioned-dirt-no-credit", need1 == 1 and bool(bad),
           f"cut 1 demand quotient rank is {need1} (the restoration direction is "
           f"already in W_1^0 and earns no credit) and the unpaid x direction is "
           f"refuted: {bad}")


def check_restored_host_exhaustive():
    """All tiny restored-host regions: m,t in {1,2}, w in {1,2},
    (a,b) in {(1,0),(2,0),(2,1)}, every binary t x m scatter S (26 cases).

    Verified per case:
      (i)  the baseline schedule (carriers a->0, hosts a->b) passes (C-down);
      (ii) the exact per-cut demand identity
           sum_j need_j = q*rank(S) + w*|a-b|  (q = a),
           i.e. with restored hosts the scatter term q*rank(S) survives every
           hosting claim and the creditable mass never exceeds the host
           displacement w*|a-b|.
    """
    cases = 0
    for m in (1, 2):
        for t in (1, 2):
            for w in (1, 2):
                for a, b in ((1, 0), (2, 0), (2, 1)):
                    for bits in range(1 << (t * m)):
                        S = [[(bits >> (i * m + j)) & 1 for j in range(m)]
                             for i in range(t)]
                        r = rank(S)
                        n = m + w + t  # carriers, hosts, target old values
                        entry = []
                        for i in range(m):
                            entry.append((f"x{i}", a, vec(n, i)))
                        for k in range(w):
                            entry.append((f"d{k}", a, vec(n, m + k)))
                        for i in range(t):
                            entry.append((f"y{i}", 0, vec(n, m + w + i)))
                        exits = []
                        for i in range(t):
                            row = [0] * n
                            for j in range(m):
                                row[j] = S[i][j]
                            row[m + w + i] = 1
                            exits.append((f"y{i}", 0, row))
                        for k in range(w):
                            exits.append((f"d{k}", b, vec(n, m + k)))
                        moves = [(f"d{k}", a, b, vec(n, m + k)) for k in range(w)] + \
                                [(f"x{i}", a, 0, vec(n, i)) for i in range(m)]
                        region = Region(entry, moves, exits)
                        bad = region.obstructions()
                        if bad:
                            report(f"restored-host-case-{cases}", False,
                                   f"m={m} t={t} w={w} (a,b)=({a},{b}) S={S}: {bad}")
                        cr = region.cut_report()
                        demand = sum(nl for (nl, _d, _dn, _nh, _u, _up, _wl, _wh)
                                     in cr.values())
                        rhs = a * r + w * abs(a - b)
                        if demand != rhs:
                            report(f"demand-identity-{cases}", False,
                                   f"per-cut demand {demand} != H_end + q*r = {rhs} "
                                   f"(m={m} t={t} w={w} ({a},{b}) S={S})")
                        cases += 1
    report("restored-host-exhaustive", cases == 156,
           f"{cases} complete tiny regions (all binary S, m,t<=2, w<=2) satisfy "
           f"(C-down) and the exact per-cut demand identity "
           f"sum_j need_j = H_end + q*rank(S): the scatter term cannot be hosted "
           f"away while hosts are restored, and credit <= host displacement")


def main():
    print("PASS_DIRTY_HOST_GAUGE_BINDING_BEGIN")
    print("--- smallest falsifying instance first ---")
    check_smallest_falsifier()
    print("--- operator gauges ---")
    check_operator_gauges()
    check_cancellation_control()
    print("--- credit accounting ---")
    check_engine_canonical()
    check_prepositioned_dirt()
    check_restored_host_exhaustive()
    print("PASS_DIRTY_HOST_GAUGE_BINDING")


if __name__ == "__main__":
    main()
