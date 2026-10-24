"""Bind the outer-reserve constant C of OUTER-TRANSFER-AUDIT s5 to the #4470 templates.

Explicit upper bound for C in q0(h,p) <= C*(log2 h + h^delta*(log2 p)^3 + 1), using the
actual #4470 BIT (#4440 query-thinned, kept by #4470) and complex (joint-helper-lattice)
compiled ranks, then the thresholds. Every bound has the form log2(x) <= H + ell with H
an exact integer and ell from integer bit lengths, so all rounding is upward.
"""
import json, math
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINES = []


def log(msg):
    LINES.append(msg)


def need(ok, msg):
    if not ok:
        raise AssertionError("FAIL: " + msg)
    log("PASS " + msg)


def ulog2(x):
    """Upper bound for log2 of a positive integer or Fraction (ceiling)."""
    x = Q(x)
    n, d = x.numerator, x.denominator
    return n.bit_length() - (d.bit_length() - 1)


def compute():
    # ---------------------------------------------------------------- inputs
    # research/query-thinned-controllers/RESULT.json (pinned in #4470 chain)
    SRC = ROOT / "research/query-thinned-controllers/RESULT.json"
    R = json.loads(SRC.read_text())
    H1b = R["bit_strictification"]["uniform_H1"]          # N_bit = 2^H1b
    H1c = R["complex_strictification"]["uniform_H1"]      # N_cx  = 2^H1c
    v = R["bit_strictification"]["tensor_power"]
    need(v == 1024 and R["complex_strictification"]["tensor_power"] == 1024, "tensor power 1024 both sides")
    need(H1b == 25986965159937 and H1c == 10418370291022217, "uniform ranks read from #4440 RESULT.json (BIT kept by #4470)")
    delta = Q(4, 1000)                                    # #4470 atom
    beta = Q(69999991, 70000000)                          # outer group width exponent (#4470 params)
    need(Q(R["outer"]["parameters"]["beta"]) == beta, "beta matches #4470 outer parameters")


    def invoice(name, floor):
        inv = R[name]
        T = {int(k): c for k, c in inv["targets"].items()}
        P = {int(k): c for k, c in inv["paid"].items()}
        W = sum(T.values())                  # productive fields of the raw unit
        MP = sum(k * c for k, c in P.items())  # paid rank-one mass
        need(W == inv["productive_fields"], name + " productive fields")
        return W, MP, floor


    Wb, MPb, bb = invoice("bit_invoice", R["bit_strictification"]["target_floor_base"])
    # #4470 itself (joint-helper-lattice) changes the complex word and its compiler rank
    J = json.loads((SRC.parent.parent / "joint-helper-lattice" / "RESULT.json").read_text())
    need(J["strictification"]["power"] == 1024 and J["compiler"]["H"] == 64215200000000, "#4470 complex word: v=1024, N_c = 2^64215200000000")
    Tj = {int(k): c for k, c in J["targets"].items()}; Pj = {int(k): c for k, c in J["paid"].items()}
    need(sum(Tj.values()) == J["productive_fields"] == 10928, "#4470 complex productive fields")
    Wc, MPc, bc = 10928, sum(k * c for k, c in Pj.items()), J["strictification"]["floor"]
    H1c_4440 = H1c
    H1c = J["compiler"]["H"]
    W4440, MP4440, b4440 = invoice("complex_invoice", R["complex_strictification"]["target_floor_base"])
    log(f"raw units: BIT W={Wb} paid mass={MPb} floor={bb}; complex W={Wc} paid mass={MPc} floor={bc}")


    def log2_B_over_N(W, MP, b, H1):
        """#4436 s3 nested widths: B_N <= C_N^N, C_N = Wv*(Wv+Pv+1)^(h+1), h <= H1.
        Wv = W^v targets after the v-fold product (completion keeps the count),
        Pv <= MP^v + Wv*b^v (paid count <= paid rank mass; completion adds <= b^v
        per productive endpoint; splitting preserves mass).
        Returns an integer X with log2 B_N <= N * X, i.e. log2 log2 B_N <= H1 + log2 X."""
        Wv = W ** v
        Pv = MP ** v + Wv * b ** v
        X = ulog2(Wv) + (H1 + 1) * ulog2(Wv + Pv + 1)
        return X


    Xb = log2_B_over_N(Wb, MPb, bb, H1b)
    Xc = log2_B_over_N(Wc, MPc, bc, H1c)
    log(f"log2 B_bit <= 2^H1b * {Xb}  (log2 X = {math.log2(Xb):.2f})")
    log(f"log2 B_cx  <= 2^H1c * {Xc}  (log2 X = {math.log2(Xc):.2f})")

    # ---------------------------------------------------------------- BIT part
    # cover prime: odd q > 2^26 N^5; Bertrand gives one below 2^(5 H1b + 27)
    log2q = 5 * H1b + 27
    # per level: log2 W(w) = log2 B + log2|GL_N(F_q)| + N^2 (w-1) log2 q
    #                     <= N*Xb + N^2 * w * log2q            (|GL_N(F_q)| < q^(N^2))
    # levels D <= log2 e / H1b;  w = ceil(e^delta) <= 2 e^delta.
    # stock bits <= (log2 e/H1b)*(2 N^2 log2q + N Xb) e^delta + log2 S_old + 2
    #            <= A_b e^delta log2 e + log2 S_old + 2,
    # A_b = (2 N^2 log2q + N Xb)/H1b <= N^2 * (2 log2q + Xb/N)/H1b <= N^2 * (2 log2q + 1)/H1b
    need(Xb.bit_length() < H1b, "N_bit exceeds Xb, so the role term is below N^2")
    A_b_small = ulog2(Q(2 * log2q + 1, H1b))      # log2 A_b <= 2*H1b + A_b_small
    log(f"BIT: log2 A_b <= 2*H1b + {A_b_small} = {2*H1b + A_b_small}")
    # old ordinary supplier stock: fixed old template (m=67, q_old>2^80) at atom width;
    # conservatively log2 S_old <= A_old e^delta log2 e with log2 A_old <= 64 (inherited, not re-derived)
    log2_A_old = 64
    # outer width e <= Cw h L^2 (SUPPLIER-SUPPORT-AUDIT, our #4612 stage 2)
    Cw = 232960
    # e^delta log2 e <= Cw^delta (log2 Cw + 3) h^delta L^(1+2delta)   (h <= p, L >= 1)
    lCw3 = ulog2(Q(ulog2(Cw) + 3))                    # log2(log2 Cw + 3) upper
    bit_coef_log2 = 2 * H1b + A_b_small + 1 + lCw3 + 1  # +1: Cw^delta<2 ; +1: nesting (L+1)<=2L
    log(f"BIT term <= 2^{bit_coef_log2} * h^delta L^3 (incl. nesting and Cw)")

    # ---------------------------------------------------------------- complex part
    # AUDIT s6: complex row stock proportional to ceil(log2 B_c) * log_{N_c}(d);
    # retained proportionality c_row (old lineage coefficient 20,161 per role-bit level);
    # we allow log2 c_row <= 64.  d <= Cw h L^2 so log2 d <= (log2 Cw + 3) L.
    log2_c_row = 64
    # ceil(log2 B_c)/log2 N_c <= (2^H1c * Xc + 1)/H1c
    cx_small = ulog2(Q(Xc + 1, H1c))                  # log2 kappa_c <= H1c + cx_small
    cx_coef_log2 = H1c + cx_small + log2_c_row + ulog2(ulog2(Cw) + 3) + 1  # nesting (L+1)<=2L, L^2<=L^3
    log(f"complex term <= 2^{cx_coef_log2} * L^3 <= ... * h^delta L^3")

    # ---------------------------------------------------------------- C and thresholds
    log2C = max(bit_coef_log2, log2_A_old + 10, cx_coef_log2) + 2   # +2 covers the sum of three terms and the +O(1)
    log(f"log2 C <= {log2C}  (complex share {cx_coef_log2}, BIT share {bit_coef_log2})")
    need(cx_coef_log2 > bit_coef_log2 + 10**13, "complex row stock dominates C by > 10^13 bits")
    # same computation for the #4440 complex word (query-thinned), for comparison
    X4440 = log2_B_over_N(W4440, MP4440, b4440, H1c_4440)
    cx4440 = H1c_4440 + ulog2(Q(X4440 + 1, H1c_4440)) + log2_c_row + ulog2(ulog2(Cw) + 3) + 1
    log(f"#4440 complex word for comparison: complex share 2^{cx4440}")

    # a lower bound for the complex share in the same realization: B_N = prod S_n >= 2^(N-m)
    # (every S_n >= 2), so ceil(log2 B_c)/H1c >= (2^H1c - 2^11)/H1c.
    cx_lower_log2 = H1c - (H1c.bit_length())          # log2((2^H1c - 2^11)/H1c) >= H1c - bitlen(H1c)
    log(f"in the #4436 realization the complex share is at least 2^{cx_lower_log2}")


    def threshold(log2C, L):
        """log2 H(p) for H = [1024 C L^3]^(1/(1-delta)), upper bound."""
        return (Q(log2C + 10) + 3 * Q(ulog2(L))) / (1 - delta)


    def fit_log2p(log2C):
        """least integer L (=log2 p) with log2 H(p) <= beta L, by bisection."""
        lo, hi = 1, 1 << 64
        while lo < hi:
            mid = (lo + hi) // 2
            if threshold(log2C, mid) <= beta * mid:
                hi = mid
            else:
                lo = mid + 1
        return lo


    Lfit = fit_log2p(log2C)
    Lold = fit_log2p(2 * H1b + 64)   # #4612 illustrative choice
    L4440 = fit_log2p(max(bit_coef_log2, cx4440) + 2)
    L_bit_only = fit_log2p(bit_coef_log2 + 2)
    log(f"fit for #4440 words: {L4440:.4e}; BIT share alone: {L_bit_only:.4e}")
    log(f"H(p) fits p^beta from log2 p = {Lfit} ({Lfit:.4e}); #4612 illustrative gave {Lold:.4e}")
    need(threshold(log2C, Lfit) <= beta * Lfit and threshold(log2C, Lfit - 1) > beta * (Lfit - 1), "fit point exact")

    # check the displayed H also beats pinterbanget's #4618 extra term 4096 C log2(4096 C) once C is this large
    # log2 H >= (log2C+10)/(1-delta) ; log2(4096 C log2(4096 C)) <= log2C + 12 + log2(log2C + 12)
    lhs = Q(log2C + 10) / (1 - delta)
    rhs = log2C + 12 + ulog2(log2C + 12)
    need(lhs > rhs, "for this C the displayed H already dominates the #4618 term 4096 C log2(4096 C)")

    # threshold proof at h >= H: C h^delta L^3 <= h/1024 and C(log2 h + 2) <= h/1024
    for L in (1, 2, 8, 1 << 20, Lfit, 1 << 60):
        lh = threshold(log2C, L)  # smallest log2 h considered
        t2 = log2C + delta * lh + 3 * ulog2(L)
        t1 = log2C + ulog2(math.ceil(lh) + 2)
        need(t2 <= lh - 10 and t1 <= lh - 10, f"q0 <= h/512 at h = H, L = {L}")

    out = {
        "inputs": {"H1_bit": H1b, "H1_complex": H1c, "tensor_power": v, "delta": str(delta), "beta": str(beta),
                   "bit_unit": {"W": Wb, "paid_mass": MPb, "floor": bb},
                   "complex_unit": {"W": Wc, "paid_mass": MPc, "floor": bc},
                   "Cw": Cw, "log2_q_bit_upper": log2q,
                   "assumed": {"log2_c_row": log2_c_row, "log2_A_old": log2_A_old}},
        "log2_B_bit_over_N": Xb, "log2_B_complex_over_N": Xc,
        "bit_share_log2": bit_coef_log2, "complex_share_log2": cx_coef_log2,
        "complex_share_lower_log2_same_realization": cx_lower_log2,
        "log2_C_upper": log2C,
        "fit_log2p": Lfit, "fit_log2p_4612_illustrative": Lold,
        "fit_log2p_bit_share_only": L_bit_only, "fit_log2p_4440_words": L4440,
        "H1_complex_4440": H1c_4440, "complex_share_log2_4440": cx4440,
    }
    return out
