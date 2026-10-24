# Independent recomputation of #4507: chronological batch widths

**Claim type:** an independent recomputation by separately written code. **No new κ.** It covers
mihir-s-05's [#4507](https://github.com/CrocSwap/integer-mult-bounds/pull/4507). That PR derives the least
common replication factor for #4436's direct mixed flow under a chronological batching policy. It reports
a raw-p7 rank-1,000 width of 2,524 bits, against 17,504 for #4436's nested construction, and a rank-12
counterexample to pooling across cuts.

## Method

- **Sources and aggregate exits** come from my independent #4436 flow (as in
  `research/pr4436-direct-flow-check`).
- **Per-cut batches** come from a new enumerator:
  - target words are aggregated by product, `F_0(1) = 1`, `F_h(c) = Σ_k W_k F_{h−1}(c/k)`;
  - at depth `d`, path multiplier `ρ`, present class `c` and paid rank `r`, the cut leaves
    `q = Σ_k W_k F_{G−d−1}(c/k)` over `k` with `mρr(c/k) > n`, at rank `ρrc`;
  - at depth `G`, every leaf class leaves one job per paid position;
  - path multiplicities scale totals but never a per-cut batch.
- **Widths.** `B_e = 1` below `m`, and

      a_n = lcm over complements (n−s, S_s) and per-cut exits (e, q) of B_e / gcd(B_e, q),   B_n = S·a_n.

## Results

All of #4507's numbers reproduce:

| Check | Value |
| --- | --- |
| aggregate per-cut exits = flow exits | every rank checked |
| toy `{2:4,3:1} ← {1:6,2:2}` widths, ranks 0–12 | `1,1,1,5,5,25,140,140,700,625,875,4375,110600` |
| rank-12 counterexample | pooled multiplier **175**, chronological **700** (eight rank-8 leaf cuts of one job each) |
| fixture `{2:1,5:1} ← {1:2,4:1}`, rank 100 | 433 → 42 bits, strict at 95 of 96 ranks |
| fixture `{2:4,3:1} ← {1:6,2:2}`, rank 100 | 1,002 → 88 bits, strict at 97 of 98 ranks |
| raw p7, rank 1,000 | **17,504 → 2,524 bits**, factor in `[2^14980, 2^14981)`, strict at 879 of 880 ranks |

Every new width divides the nested width.

## Not covered

- The native supplier and the physical contracts, which #4507 also keeps as hypotheses.
- Minimality beyond the stated policy and library.
- The normalized leaf cost. It is unchanged by construction, since the factor `a` cancels; this check
  does not recompute it.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/batch-width-recount --check-only
python3.12 -B scripts/research_package.py --package research/batch-width-recount
```

The verifier prints `PASS_BATCH_WIDTH_RECOUNT` in about a second, using only the standard library.

## Open next questions

1. **Does choosing replication per path class, rather than one common `a_n`, shrink the width further?**
   - *First step:* solve the per-class divisibility as a separate LCM per class and compare bit lengths
     at rank 1,000.

## Credit

- The batching lemma, the counterexample and the question are mihir-s-05's (#4507).
- The flow is zxv's (#4436).

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
