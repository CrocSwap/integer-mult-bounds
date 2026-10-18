# PR1866's one-unit block overhead passes only by idle credit

**Scoped audit of a pending screen. No new κ, construction or supplier. The selected record is unchanged.**

[PR #1866](https://github.com/CrocSwap/integer-mult-bounds/pull/1866) (head
`7d22d1d51eb6c0bc040f8181b6c5f83e051fb234`, package `research/complex-mixed-rank6-block-seedc8d6`)
proposes a heterogeneous bilinear block `(3,1,1,1) → 6`. One rank-3 child and three rank-1 children of the
selected word become one rank-6 child. The package prices `k = 0..432` such blocks per call, each with
`e ∈ {0,1,2}` assumed rank-one-equivalent overhead units. Its stated thresholds against the 5% target are:
first pass at **135** blocks for `e = 0`, at **284** for `e = 1`, and no pass for `e = 2`.

The thresholds are arithmetically correct for the invoice PR1866 actually computes. However, that invoice
adds the `e·k` overhead units to the *local profile* passed to the retained ceiling engine. The
[ceiling model](../complex-local-word-ceiling/ceiling.py) fixes paid mass per call at `72w + 64 = 7232`
(the coverage identity). So each overhead unit is subtracted from the idle remainder and replaces `1/51`
of an ideal rank-51 idle child. The merged [rank-one block budget](../complex-rank-one-block-budget/README.md)
(PR1605) and the [block target screen](../complex-block-target-screen/README.md) price additional copies,
gathering and restoration **on top** of the unchanged idle bill. They state that this work cannot be
deducted from the old idle remainder without a new coverage identity. PR1605's replay includes this exact
"subtract extra work from idle mass" invoice as a false-pass control.

## Result (exact, two code-disjoint engines)

Same model and target as PR1866: width 73, 896 live families per nine-stage replica, centre charge 64,
idle rank cap 51, and selected profile `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`. The target is
`a* = 35491136290869/20000000000000000`, which is 21/20 × the selected ceiling's upper bracket. A row passes
when the relaxation moment at `a*` is certified strictly below 1.

| Overhead per block `e` | PR1866 invoice (overhead credited against idle) | Additional overhead (no idle credit) |
|---:|---|---|
| 0 | first pass k = 135 (298 passing k) | first pass k = 135 (298 passing k) |
| 1 | first pass k = 284 (149 passing k) | **no k in 0..432 passes** |
| 2 | no pass | no pass |

- **Per-block saving.** One block saves `3 + 3^q − 6^q` rank-one calls, with `q = 1 − a`. This is zero at
  `a = 0` and increasing in `a`. At `a*` it is certified in `(0.013204, 0.013205)`. So with no idle credit,
  one extra rank-one call per block makes every block strictly costlier than the children it replaces,
  for every `0 ≤ a ≤ a*`. This is the `(3,1,1,1) → 6` instance of PR1605's per-block tariff obstruction.
- **Why the credited invoice passes.** A credited overhead unit costs only `c(1) − c(51)/51 ≈ 0.006953`
  rank-one calls, about half the block saving. That gap is the entire source of the `e = 1` pass at k = 284.
- **Total overhead budget.** With all 432 blocks, the uncredited budget is at most **3 extra rank-one
  calls per call in total**, not per block. At the first passing count, k = 135, it is **0**.

PR1866's zero-overhead threshold (135) and its `e = 2` rejection are independently reproduced. Its `e = 1`
threshold holds only under the credited invoice. If overhead is real additional work, as PR1605's
convention requires, the 5% gate allows a fractional tariff below 0.0133 rank-one calls per block, or
3 rank-one calls in total. The README's phrase "284 with one" should therefore carry that qualification.

## Method and controls

`verify.py` evaluates every decision with two arithmetic engines. Every decision must be strict, and the
two engines must agree on all of them:

- **Engine A.** The pinned `ceiling.py` `child_cost` enclosures (atanh/Taylor, `Fraction`, outward rounding).
- **Engine B.** A code-disjoint `decimal` engine. It uses libmpdec's correctly rounded `ln`/`exp` at
  80 digits, widened by 4 ulps, with `ROUND_FLOOR`/`ROUND_CEILING` for every other operation.

The engines agree on the selected ceiling bracket `[…088, …089]·10⁻¹⁵`, all 2,598 scan decisions
(433 × 3 tariffs × 2 conventions) and both overhead-budget counts. Each passing set is checked to be an
upper interval in k. The script also runs these controls:

- the idle rank 52 violates the halving guard;
- a profile that overspends the coverage identity is rejected;
- the two conventions coincide at `e = 0`;
- k = 134, `e = 0` is rejected;
- k = 284, `e = 1` passes when credited and is rejected as additional work.

## Scope and limits

- This audits one pricing convention in one pending package's moment screen. It does not examine
  PR1866's tensor-rank proof, its dirty-target contract or its phase-A placement scan.
- The `e` tariff remains a parameter, as in PR1866. Nothing here establishes the block's actual copy,
  frame, restoration or hosting bill.
- If a construction proves a new coverage identity under which its overhead legitimately displaces idle
  mass, the credited column becomes the relevant one. That proof would be its own obligation.
- All other limits of the retained ceiling model apply: fixed width, template, centre and outer recipe,
  and fractional idle packing.
- Engine B trusts libmpdec's documented correct rounding of `ln` and `exp`. The 4-ulp widening and the
  agreement with engine A are the safeguards.

## Reproduce

From the repository root, standard library only (about one second):

```sh
python3 -I -B research/pr1866-overhead-idle-credit-audit/verify.py          # PASS_PR1866_OVERHEAD_IDLE_CREDIT_AUDIT
python3 scripts/research_package.py --package research/pr1866-overhead-idle-credit-audit --check-only
python3.12 scripts/research_package.py --package research/pr1866-overhead-idle-credit-audit
```

`verify.py --write` regenerates `RESULT.json`. Run locally with Python 3.14.8. The registered Python 3.12
replay was not run locally.

## Open next questions

- **Does any heterogeneous block clear the 5% gate with real overhead?** For a mass-preserving merge of
  children `r_1..r_j` into one rank-`Σr_i` child, the saving in rank-one units is `Σ r_i^q − (Σ r_i)^q`.
  It is far below one call for small blocks. A first step is to tabulate that saving and the uncredited
  budget for every small merge type the selected profile can supply. The blocker is that each type still
  needs an exact identity and a measured overhead bill.
- **Should the ceiling engine refuse credited overhead?** `ceiling.relax` cannot tell payload children
  from overhead children. A separate `extra` argument priced outside the coverage identity would make the
  PR1605 convention the default. The blocker is that `ceiling.py` is a pinned input of several packages,
  so this would need a successor helper, not an edit.

## Credit

The audited block, tensor-rank proof and screen are by Cinna / commdata2338 (PR #1866). The ceiling model
is Douglas Colkitt's (PR1240), built on PR1012's coverage identity. The uncredited overhead convention and
its false-pass control are Arham Tahir's (PR1605). The block target screen is Jose Manuel's (@jmbarrancoml), building on Ali Romman's PR1429.
Prepared by ianlibanio with substantial Claude (Anthropic) assistance; no independent human review.
Apache-2.0.
