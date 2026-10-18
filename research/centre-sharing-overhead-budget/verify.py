#!/usr/bin/env python3
"""Exact overhead budgets for k-call centre sharing on the actual selected #1094 profiles.

Planning result for the centre-path-sharing card; no construction and no kappa claim.
Exact moment enclosures come from selected-suppliers-de-diagnostic (Navinor) and the
bootstrap/outer formulas from frontier1042-invoice-audit-seed81 (Wronskode), both loaded
unchanged as Git blobs at BASE. Standard library and git only.

Model: sharing one centre path across k calls removes (1 - 1/k) of the 1,152 rank-8 centre
children and changes the coverage identity to 72W + (64/k)N; every other child of the actual
selected histogram is kept. The moment is linear in child counts, so each budget below is a
sharp integer: the stated count passes the exact moment test and one more child fails.

Prepared for rtyu193-rgb with Claude Code (Claude Opus 5.5). Apache-2.0.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import types
from fractions import Fraction as Q

if not __debug__:
    raise SystemExit("checks use assert; run without -O")
sys.set_int_max_str_digits(1000000)

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
BASE = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
CODE = {"de": ("research/selected-suppliers-de-diagnostic/verify.py", "f9a9d5e5103b6ccbadb3f50fea34e25ccfce7ff1"),
        "seed81": ("research/frontier1042-invoice-audit-seed81/verify.py", "8ee1d7a01473e1b5674710165566e4e9761f7c65")}
CERT = "research/community-frontier1094-audit/ASSEMBLY.json"
CERT_SHA = "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045"
M, W, N = 73, 14336, 144
GRID = Q(1, 10 ** 24)
ETA = BETA = Q(1, 10 ** 24)
B_CERTIFIED_K2 = Q(3, 1000)          # a certified complex acceptance point for 2-call sharing
OVERHEAD_RANKS = (1, 2, 3, 4, 5, 8, 16, 32, 48, 51, 72)


def git_blob(b):
    return hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()


def load_module(key):
    path, blob = CODE[key]
    src = subprocess.run(["git", "-C", str(ROOT), "show", BASE + ":" + path], capture_output=True, check=True).stdout
    assert git_blob(src) == blob, "audited code blob differs: " + path
    mod = types.ModuleType("pinned_" + key)
    mod.__file__ = str(ROOT / path)
    exec(compile(src, str(ROOT / path), "exec"), mod.__dict__)
    return mod


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    de, s81 = load_module("de"), load_module("seed81")
    raw = (ROOT / CERT).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CERT_SHA, "selected certificate bytes"
    asm = json.loads(raw)
    bit_raw = (ROOT / asm["bit_supplier"]["path"]).read_bytes()
    assert git_blob(bit_raw) == asm["bit_supplier"]["git_blob_sha1"], "PR589 blob"
    expected = json.loads(bit_raw)
    with tarfile.open(ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz") as tar:
        inv_raw = tar.extractfile("candidate/strict/global/audit/PREFIX-AND-INVOICE.json").read()
    assert hashlib.sha256(inv_raw).hexdigest() == asm["input_sha256"]["fresh_invoice"], "invoice pin"
    invoice = json.loads(inv_raw)

    H = {int(r): int(n) for r, n in asm["complex_profile"].items()}
    b_sel, c_sel, k_sel = Q(asm["complex_lower"]), Q(asm["bit_lower"]), Q(asm["kappa"])
    complex_bill = lambda h: de.Bill(h, M, W)
    accepts = lambda bill, a: bill.residual(a)[1] < 0
    rejects = lambda bill, a: bill.residual(a)[0] > 0

    def kappa(b, c):
        a, _ = s81.bootstrap(b, c, ETA, BETA)
        k = s81.kappa_from(a, ETA)
        slacks, _ = s81.assembly_slacks(a, b, k, ETA, BETA)
        assert all(v > 0 for v in slacks.values()), "outer slack"
        return k

    def add(h, r, x):
        out = dict(h)
        out[r] = out.get(r, 0) + x
        assert out[r] >= 0
        return {q: n for q, n in out.items() if n}

    def sharp(fits, guess):
        """Largest integer x >= 0 with fits(x), starting from a linear estimate."""
        x = max(0, int(guess))
        while not fits(x):
            x -= 1
            assert x >= 0, "no admissible count"
        while fits(x + 1):
            x += 1
        return x

    def unit(bill_factory, r, a):
        lo, hi = bill_factory({r: 1}).residual(a)
        return lo + 1, hi + 1

    out = {}
    # Controls: certified endpoints and the recorded kappa reproduce.
    sel = complex_bill(H)
    assert accepts(sel, b_sel) and rejects(sel, b_sel + GRID), "selected complex endpoint"
    bit_bill, bit_info = de.bit_ledger(asm, expected)
    assert accepts(bit_bill, c_sel) and rejects(bit_bill, c_sel + GRID), "selected bit endpoint"
    assert kappa(b_sel, c_sel) == k_sel, "selected kappa"
    out["controls"] = ["complex endpoint accepted, next grid rejected", "bit endpoint accepted, next grid rejected",
                       "selected kappa recomputed", "undoing the sharing (+4 rank-8 per call) is exactly break-even"]

    # 1. k-call sharing on the actual histogram.
    rows = []
    for k in (2, 4, 8, 16, 144):
        h = {**H, 8: H[8] // k}
        bill = complex_bill(h)
        mass = sum(r * n for r, n in h.items())
        assert mass == 72 * W + 64 * N // k and accepts(bill, c_sel)
        budget = {}
        for r in (1, 8):
            lo, hi = bill.residual(c_sel)
            ulo, uhi = unit(complex_bill, r, c_sel)
            x = sharp(lambda x: accepts(complex_bill(add(h, r, x)), c_sel), -hi / uhi)
            budget[r] = dict(total=x, per_call=str(Q(x, N)), mass_per_call=float(Q(x * r, N)))
        rows.append(dict(k=k, rank8_children=h[8], centre_charge_per_call=str(Q(64, k)),
                         residual_at_bit_endpoint=float(bill.residual(c_sel)[1]), complex_above_bit=True,
                         overhead_budget_full_gain=budget))
    out["k_sharing"] = rows

    # 2. Two-call sharing: sharp per-rank overhead budgets (full bit-limited gain / any gain).
    h2 = {**H, 8: H[8] // 2}
    b2 = complex_bill(h2)
    assert accepts(b2, B_CERTIFIED_K2)
    k_bit = kappa(B_CERTIFIED_K2, c_sel)
    table = []
    for r in OVERHEAD_RANKS:
        _, hi_c = b2.residual(c_sel)
        _, hi_s = b2.residual(b_sel + GRID)
        full = sharp(lambda x: accepts(complex_bill(add(h2, r, x)), c_sel), -hi_c / unit(complex_bill, r, c_sel)[1])
        anyg = sharp(lambda x: accepts(complex_bill(add(h2, r, x)), b_sel + GRID),
                     -hi_s / unit(complex_bill, r, b_sel + GRID)[1])
        table.append(dict(rank=r, full_gain_total=full, full_gain_mass_per_call=round(full * r / N, 4),
                          any_gain_total=anyg, any_gain_mass_per_call=round(anyg * r / N, 4)))
    r8 = next(t for t in table if t["rank"] == 8)
    assert r8["any_gain_total"] == 4 * N - 1, "re-adding all 576 shared rank-8 children must be exactly break-even"
    out["two_call"] = dict(bit_limited_kappa=str(k_bit), bit_limited_kappa_decimal=str(float(k_bit)),
                           gain_percent=float((k_bit / k_sel - 1) * 100), budgets=table)

    # 3. Minimum net complex-side saving that hands the binding role to the bit side.
    need = []
    for r in (1, 8, 48):
        lo, hi = sel.residual(c_sel)
        ulo, _ = unit(complex_bill, r, c_sel)
        # smallest removal x with acceptance at the bit endpoint
        x = max(1, int(hi / ulo))
        while not accepts(complex_bill(add(H, r, -x)), c_sel):
            x += 1
        while x > 1 and accepts(complex_bill(add(H, r, -(x - 1))), c_sel):
            x -= 1
        need.append(dict(rank=r, children_removed=x, mass_per_call=round(x * r / N, 4)))
    out["complex_saving_to_reach_bit_cap"] = need

    # 4. The card's 10% headline target: complex ample, so the bit endpoint must rise.
    target = k_sel * Q(11, 10)
    lo_i, hi_i = int(c_sel / GRID), int(Q(1, 100) / GRID)
    while hi_i - lo_i > 1:
        mid = (lo_i + hi_i) // 2
        if kappa(B_CERTIFIED_K2, mid * GRID) >= target:
            hi_i = mid
        else:
            lo_i = mid
    c_star = hi_i * GRID
    assert kappa(B_CERTIFIED_K2, c_star) >= target > kappa(B_CERTIFIED_K2, c_star - GRID)
    bit_hist = dict(bit_bill.hist)

    def bit_factory(h):
        return de.Bill(h, bit_info["m"], bit_info["W"],
                       surcharge_coeff=Q(32 * bit_info["m"] * sum(h.values()), 10 ** 16 * bit_info["W"]))
    assert bit_factory(bit_hist).residual(c_sel) == bit_bill.residual(c_sel), "bit surcharge reconstruction"
    bit_need = []
    for r in (1, max(bit_hist)):
        _, hi = bit_factory(bit_hist).residual(c_star)
        ulo, _ = unit(lambda h: de.Bill(h, bit_info["m"], bit_info["W"]), r, c_star)
        x = max(1, int(hi / ulo))
        while not accepts(bit_factory(add(bit_hist, r, -x)), c_star):
            x += 1
        while x > 1 and accepts(bit_factory(add(bit_hist, r, -(x - 1))), c_star):
            x -= 1
        bit_need.append(dict(rank=r, children_removed=x, mass=x * r, mass_per_replica=round(x * r / bit_info["T"], 3)))
    out["ten_percent_target"] = dict(kappa_target=str(target), bit_endpoint_needed=str(c_star),
                                     bit_endpoint_ratio=float(c_star / c_sel), bit_deficit=bit_info["deficit"],
                                     bit_saving_needed=bit_need,
                                     note="surcharge recomputed from the reduced child count")

    # 5. Scalar overhead under the binding finite guard (local primitive bound < 2^48).
    prov = max(invoice["providers"].values(), key=lambda p: p["local_primitive_bound"])
    assert prov["local_primitive_bound"] == invoice["local_primitive_bound"]
    per_macro = 16 * invoice["compiler"]
    headroom = 2 ** 48 - 1 - invoice["local_primitive_bound"]
    out["scalar_overhead"] = dict(local_primitive_bound=invoice["local_primitive_bound"], guard="< 2^48",
                                  adapter_growth_per_extra_macro=per_macro,
                                  extra_macros_per_call_upper_bound=headroom // per_macro,
                                  note="each extra macro or child adds 16 adapters at the compiler constant; "
                                       "primitive counts of the new macros reduce this further")

    out["status"] = "PASS_CENTRE_SHARING_OVERHEAD_BUDGET"
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    target_path = PKG / "RESULT.json"
    if args.write:
        target_path.write_text(text, encoding="utf-8", newline="\n")
        print("WROTE", target_path.relative_to(ROOT).as_posix())
    else:
        assert target_path.read_text(encoding="utf-8") == text, "RESULT.json differs from regenerated result"
    print(f"{out['status']} k2_full_gain_budget_rank8={r8['full_gain_total']} bit_limited_kappa={float(k_bit):.15f} "
          f"bit_endpoint_for_10pct={float(c_star):.10f} no_new_kappa")


if __name__ == "__main__":
    main()
