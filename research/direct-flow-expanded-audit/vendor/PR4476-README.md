# Independent check of #4436 §3 on raw p7: widths, routing slots and growth

**Claim type:** an independent finite check plus an exact counting identity. **No new κ.** It covers §3
("Nested divisible widths and complete count bounds") of zxv's
[#4436](https://github.com/CrocSwap/integer-mult-bounds/pull/4436), which my #4456 left uncovered. It uses
the same independent flow implementation as #4456.

## What is checked, for every rank 121 ≤ n ≤ 2000

Let `W = Σ_k W_k = 7688` and `P = Σ_r P_r = 55998` be the unit's target and paid multiplicities, and
`h = G(n)`.

1. **The width factor.** `S_n` (total source weight) is at most `C = W(W+P+1)^{h+1}`. The worst ratio
   is `S_n/C = 1.6·10⁻⁵`, so the bound is very loose.
2. **An exact slot identity.**

       sources + exits + 2·matched = U·(W + P).

   Each unit's `W` target slots are either matched or sourced, and its `P` paid positions are either
   matched or exits. So #4436's routing count (sources, exits, unit target slots and unit paid positions)
   equals `2(W+P)U − 2·matched` **exactly**. That is at most `2(W+P)U`, with equality only when nothing
   is matched.
3. **Growth.** `log B_N = Σ log S_n` grows like `N log N`. The ratio `log B_N/(N log N)` is 1.094, 1.756,
   1.965 and 2.033 at `N` = 500, 1,000, 1,500 and 2,000. A local run gives 2.066 at `N = 3,000`, so the
   ratio is levelling off near 2.

## Not covered

- §3's telescoping `B_N·N − P_N = Δ·Qcol_N`, which needs the fully expanded program. The per-flow
  identity is in #4456.
- The record and description bounds.
- Native premises.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/direct-flow-width-check --check-only
python3.12 -B scripts/research_package.py --package research/direct-flow-width-check
```

The verifier prints `PASS_DIRECT_FLOW_WIDTH_CHECK`, using only the standard library.

## Open next questions

1. **Tighten the constructive width (#4436 open question 3).**
   - *Why it matters:* the observed `S_n` sits about 10⁵ times below `C`.
   - *First step:* replace `C` by the exact `S_n` recurrence from the flow, and bound it by
     `(W+P)·(units at the top layer)`.

## Credit

- The construction and the bounds are zxv's (#4436).
- The lockstep construction is Jacob Alan Sussman's Theorem 1G.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
