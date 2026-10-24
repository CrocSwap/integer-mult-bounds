#!/usr/bin/env python3
"""Independent audit of the BIT row-stock formulas of #4359 and their #4470 atom change.

Standard library only. Exit status 0 means every check passed; the summary is printed
as JSON. See README.md for the statements and proofs.
"""
import itertools
import json
import math
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A_OLD = Q(384599, 10 ** 10)
CASES = {
    "pr4359": dict(C0=Q(69, 25000), C1=Q(11, 4000), delta=Q(3, 1000), admitted=Q(27, 10000),
                   prime=Q(25_600_000), log2N=6552928412, beta=Q(99997, 100000),
                   a_expected=Q(27418653797, 10 ** 13)),
    "pr4470": dict(C0=Q(3459, 10 ** 6), C1=Q(69, 20000), delta=Q(1, 250), admitted=Q(34, 10000),
                   prime=Q(2 ** 26), log2N=25986965159937, beta=1 - 3 * Q(1, 1_400_000_000),
                   a_expected=Q(8590884599, 2500000000000)),
}
BINDINGS = {
    "research/kappa-rebuild/transfer-audit/OUTER-TRANSFER-AUDIT.md": [
        "q0(h,p) <= C*(log2 h + h^0.003*(log2 p)^3 + 1)",
        "[1024*C*(log2 p)^3]^(1/(1-0.003))",
        "R(h) <= 3h/128 + q0(h,p) + O(1) <= h/16",
        "`O(h^0.003*(log p)^(2*0.003+1))`",
        "has width at most `C*h*(log p)^2`",
    ],
    "research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md": [
        r"W(w)=B|\operatorname{GL}_N(\mathbb F_q)|q^{N^2(w-1)}",
        "A safe reserve is `W(w)^D * S_old`",
        r"a_{\rm BIT}=(1-\delta)C_1+\delta a_{\rm old}",
        r"q>\frac{256N^5}{d}=25,600,000N^5.",
    ],
    "research/kappa-rebuild/bit/delayed_cover_bridge.py": [
        "before={(0,mapped),(1,mapped)}",
        "after={(role,act(gauge,address)) for role in (0,1)}",
    ],
    "research/capped-phase-fusion/SUPPLIER-SUPPORT-AUDIT.md": [
        "G=4 ceil(log2 p)+6",
        "With K=128G",
        "Three disjoint 3kG-bit reservoirs",
        "Q_rows=W_complex^D_complex W_bit^D_bit",
    ],
    "notes/three-stage-cover-bit.tex": [
        r"$a_{\rm old}=384599/10^{10}$",
        r"old width-$O(w)$ interchanges",
        r"$W(w)=W_0q^{m^2(w-1)}$",
    ],
    "research/query-thinned-controllers/verify.py": [
        "Q('.004')",
        "params['beta']*(1-atom)",
        "atom < 1-ordinary",
    ],
    "research/joint-helper-lattice/verify.py": [
        "atom==Q('.004')",
    ],
}


def need(cond, msg):
    if not cond:
        raise AssertionError(msg)


def bind_sources():
    found = {}
    for path, needles in BINDINGS.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        for s in needles:
            need(s in text, f"source statement missing in {path}: {s}")
        found[path] = len(needles)
    return found


# ---------------------------------------------------------------- conversion
def ordinary_saving(C1, delta):
    return (1 - delta) * C1 + delta * A_OLD


def conversion():
    out = {}
    for name, c in CASES.items():
        d, C0, C1 = c["delta"], c["C0"], c["C1"]
        a = ordinary_saving(C1, d)
        gap = C0 - C1
        need(a == c["a_expected"], f"{name}: exact ordinary saving")
        need(d > a, f"{name}: linear adapter term e^(1-delta) is paid")
        need(d < 1 - a, f"{name}: stock e^delta log e is lower order")
        need((1 - d) * (1 - C1) + d * (1 - A_OLD) == 1 - a, f"{name}: middle exponent identity")
        need(a > c["admitted"], f"{name}: admitted saving below ordinary")
        need(c["prime"] >= 256 / gap, f"{name}: prime coefficient >= 256/(C0-C1)")
        need(64 / c["prime"] <= gap / 4, f"{name}: fallback surcharge 64N^5/q <= gap/4")
        need((1 + gap / 4) / (1 + gap / 2) < 1, f"{name}: complete fallback moment < 1")
        # N^gap >= 2^gap = exp(gap ln 2) >= 1 + gap ln 2 > 1 + gap/2  (ln 2 > 1/2)
        need(math.log(2) > 0.5, "ln 2 > 1/2")
        out[name] = {"a_BIT": str(a), "a_BIT_decimal": f"{float(a):.13f}",
                     "adapter_margin": str(d - a), "stock_margin": str(1 - d - a)}
    old_at_new = ordinary_saving(CASES["pr4470"]["C1"], Q(3, 1000))
    need(not Q(3, 1000) > old_at_new, "#4470: the old atom 0.003 cannot pay the adapter")
    return out


# ---------------------------------------------------------------- stock algebra
def gl_order(n, p):
    out = 1
    for i in range(n):
        out *= p ** n - p ** i
    return out


def det(a, m):
    n = len(a)
    if n == 1:
        return a[0][0] % m
    if n == 2:
        return (a[0][0] * a[1][1] - a[0][1] * a[1][0]) % m
    return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
            - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
            + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])) % m


def stock_algebra():
    gl = {}
    for n, p, w in ((1, 3, 3), (2, 3, 2), (2, 2, 3), (1, 5, 2)):
        m = p ** w
        cnt = sum(det([list(e[i * n:(i + 1) * n]) for i in range(n)], p) != 0
                  for e in itertools.product(range(m), repeat=n * n))
        need(cnt == gl_order(n, p) * p ** (n * n * (w - 1)), f"|GL_{n}(Z/{p}^{w})| lift formula")
        gl[f"n{n}_p{p}_w{w}"] = cnt
    for N, q, w, B, S in ((2, 3, 2, 5, 7), (3, 5, 2, 11, 4), (2, 7, 3, 2, 9)):
        Wf = B * gl_order(N, q) * q ** (N * N * (w - 1))
        for D in (1, 2, 3, 4):
            R = Wf ** D * S
            for _ in range(D):
                R, r = divmod(R, Wf)
                need(r == 0, "reserve splits exactly at every level")
            need(R == S, "the last level keeps S_old")
    for N in range(2, 13):
        for n in range(1, 20001):
            d, x = 0, n
            while x >= N:
                x, d = x // N, d + 1
            need(N ** d <= n < N ** (d + 1), "D(n) = floor(log_N n)")
    need(all(6 * (2 * m) * (2 * m - 1) + 3 * (2 * m) + 6 * (2 * m - 1) < 32 * m * m
             for m in range(1, 20001)), "fallback child count < 32 m^2")
    return {"gl_lift_counts": gl, "split_cases": 12, "depth_scan": "N=2..12, n<=2e4"}


# ---------------------------------------------------------------- borrowed digits
def log2_k(Le, delta, log2N):
    """log2 of D (N^2 w + 2), the main part of the borrowed base-q digit count, at e = 2^Le."""
    logw = delta * Le
    D = math.floor((Le - logw) / log2N)
    if D < 1:
        return None
    return math.log2(D) + 2 * log2N + logw


def borrowed_digits():
    out = {}
    for name, c in CASES.items():
        d, L = float(c["delta"]), float(c["log2N"])
        good = lambda Le: (lambda k: k is not None and k + 1 < Le)(log2_k(Le, d, L))
        lo, hi = L, 4 * L
        while not good(hi):
            hi *= 2
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if good(mid) else (mid, hi)
        need(all(good(hi * (1 + t / 100) ** 3) for t in range(1, 2001)), f"{name}: 2k<e after threshold")
        need(abs(hi - 2 * L / (1 - d)) < 64, f"{name}: threshold ~ 2 log2 N/(1-delta)")
        out[name] = {"threshold_log2_e": round(hi, 3), "two_log2N_over_1_minus_delta": round(2 * L / (1 - d), 3)}
    return out


# ---------------------------------------------------------------- outer reserve
def outer_reserve():
    out = {}
    # BIT call width from the support router: 2hK(1+9G), K=128G, G=4ceil(L)+6
    worst = max(2 * 128 * (4 * L + 6) * (1 + 9 * (4 * L + 6)) / L ** 2 for L in range(1, 100001))
    need(worst <= 232960, "BIT-call width <= 232960 h L^2")
    out["bit_call_width_C"] = 232960
    # e^d log2 e <= Cw^d (log2 Cw + 3) h^d L^(1+2d) for 1 <= h <= p, e = Cw h L^2
    for logCw in (0, 10, 1000, 10 ** 6):
        for d in (0.003, 0.004):
            for L in (2, 64, 4096, 10 ** 6, 10 ** 12):
                for frac in (0, 0.25, 0.5, 1):
                    logh = frac * L
                    loge = logCw + logh + 2 * math.log2(L)
                    lhs = d * loge + math.log2(loge)
                    rhs = d * logCw + math.log2(logCw + 3) + d * logh + (1 + 2 * d) * math.log2(L)
                    need(lhs <= rhs + 1e-9, "BIT-call stock bound")
    for d in (Q(3, 1000), Q(1, 250)):
        need(2 + 2 * d <= 3, "nesting log h and complex stock keep the L power <= 3")
    # threshold H = [1024 C L^3]^(1/(1-d)) already gives C(log2 h + h^d L^3 + 2) <= h/64
    for d in (0.003, 0.004):
        for logC in (0, 20, 1000, 1.4e10, 5.3e13):
            for L in (8, 64, 1024, 2 ** 20, 2 ** 40):
                logH = (10 + logC + 3 * math.log2(L)) / (1 - d)
                for s in (0, 1, 10, 100, 1e4, 1e8):
                    lh = logH + s
                    t2 = logC + d * lh + 3 * math.log2(L)          # log2 of C h^d L^3
                    t1 = logC + math.log2(lh + 2)                  # log2 of C (log2 h + 2)
                    need(t2 <= lh - 10 + 1e-6, "C h^d L^3 <= h/1024 above H")
                    need(max(t1, t2) + 1 <= lh - 6, "q0 + O(1) <= h/64 above H")
    need(Q(3, 128) + Q(1, 64) <= Q(1, 16), "R(h) <= h/16")
    need(Q(1, 64) - Q(1, 1024) / Q(693, 1000) - Q(1, 250) / 1024 > 0, "h/64 - q0 increasing above H")
    out["threshold_multiple_needed"] = 1
    out["phase_sum_factor_x=0.997"] = 1 / (1 - 16 ** -0.997)
    return out


# ---------------------------------------------------------------- cover
def mat_mul(a, b, m):
    n = len(a)
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(n)) % m for j in range(n)) for i in range(n))


def adjugate(a):
    n = len(a)
    if n == 2:
        return ((a[1][1], -a[0][1]), (-a[1][0], a[0][0]))
    cof = [[0] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            r = [x for x in range(3) if x != i]
            c = [x for x in range(3) if x != j]
            cof[i][j] = (-1) ** (i + j) * (a[r[0]][c[0]] * a[r[1]][c[1]] - a[r[0]][c[1]] * a[r[1]][c[0]])
    return tuple(tuple(cof[j][i] for j in range(3)) for i in range(3))


def inv(a, m):
    di = pow(det(a, m), -1, m)
    return tuple(tuple(x * di % m for x in row) for row in adjugate(a))


def cover_audit():
    cases = {
        (2, 3, 2): ([((1, 0), (0, 0)), ((1, 0), (1, 0))], [((1, 1), (1, 0)), ((0, 1), (1, -1))]),
        (3, 2, 2): ([((1, 0, 0), (0, 1, 0), (0, 0, 0)), ((1, 0, 0), (1, 0, 0), (0, 0, 1))],
                    [((1, 1, 0), (0, 1, 0), (0, 1, 1)), ((0, 1, 0), (0, 0, 1), (1, 0, 0))]),
    }
    out = {}
    for (N, p, w), (children, matchers) in cases.items():
        m, hm = p ** w, p ** (w - 1)
        cov = []
        for e in itertools.product(range(m), repeat=N * N):
            g = tuple(tuple(e[i * N:(i + 1) * N]) for i in range(N))
            if det(g, p):
                cov.append(g)
        need(len(cov) == gl_order(N, p) * p ** (N * N * (w - 1)), "cover size")
        covset = set(cov)
        for Qc, S in zip(children, matchers):
            S = tuple(tuple(x % m for x in r) for r in S)
            need(mat_mul(Qc, Qc, m) == tuple(tuple(x % m for x in r) for r in Qc), "child projector")
            P = mat_mul(mat_mul(S, Qc, m), inv(S, m), m)
            images, ctrl = set(), False
            for g in cov:
                h = mat_mul(g, S, m)
                images.add(h)
                gi = inv(g, m)
                lhs = mat_mul(mat_mul(g, P, m), gi, m)
                need(lhs == mat_mul(mat_mul(h, Qc, m), inv(h, m), m), "projector matching")
                ctrl |= mat_mul(mat_mul(g, Qc, m), gi, m) != lhs
                g0 = tuple(tuple(x % p for x in r) for r in g)
                G1 = tuple(tuple((x - y) // p for x, y in zip(r, s)) for r, s in zip(g, g0))
                raw = [[sum(g0[i][k] * S[k][j] for k in range(N)) for j in range(N)] for i in range(N)]
                carry = [[x // p for x in r] for r in raw]
                pred = tuple(tuple((sum(G1[i][k] * S[k][j] for k in range(N)) + carry[i][j]) % hm
                                   for j in range(N)) for i in range(N))
                need(tuple(tuple(x // p for x in r) for r in h) == pred, "affine high-row carry")
            need(images == covset, "right routing is a bijection of the cover")
            need(ctrl, "omitting the matcher changes the projector")
        out[f"N{N}_p{p}_w{w}"] = len(cov)
    return out


def tautology_check():
    # The original 6561-address gauge check compares two identical constructions.
    act = lambda x: ((2 * x[0]) % 9, (4 * x[1]) % 9) + tuple(x[2:])
    for address in itertools.product(range(9), repeat=4):
        mapped = act(address)
        before = {(0, mapped), (1, mapped)}
        after = {(role, act(address)) for role in (0, 1)}
        need(before == after, "identical by construction")
    return "the delayed_cover_bridge.py scalar-gauge check cannot fail; it is not evidence"


def main():
    start = time.monotonic()
    result = {"schema": "bit-row-stock-atom-audit/1", "sources": bind_sources(),
              "conversion": conversion(), "stock_algebra": stock_algebra(),
              "borrowed_digits": borrowed_digits(), "outer_reserve": outer_reserve(),
              "cover": cover_audit(), "tautology": tautology_check()}
    result["status"] = "PASS_BIT_ROW_STOCK_AUDIT_NO_NEW_KAPPA"
    result["seconds"] = round(time.monotonic() - start, 1)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
