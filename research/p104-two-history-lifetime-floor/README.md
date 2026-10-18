# P104 two-history price under reported lifetime floors

**Scoped audit of pending PR2920. No construction, no new floor, no κ change.**

[PR2920](https://github.com/CrocSwap/integer-mult-bounds/pull/2920) (Nick Petalas,
head `b9ea9def949f9d71d59e21294d0e6cfbe0692a73`) prices the restricted two-history
P104 route. Its unique cheapest profile is 0 cheap `(1,7,1)` and 208 unit-step
helpers, with selected moment ≈ 0.998896 and relaxed root in
(0.002104152801941, 0.002104152801942). Its price search enforces PR2909's
endpoint curve and `C+U <= 482`, but no lifetime floor above the merged 208.

Sagar Thakrar's mixer handoff
([discussion 2245, comment 18960667](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18960667),
fork commit `743640530229e1821ae11dc104798871272d6f00`, branch
`loop9d24/i14-s32-p104-rank1-mixer`) reports written floors
in the same X-only monotone helper model on the frozen P104 paths:

- at least 216 lifetimes in grammar G′, which allows singular in-frame copies,
  clears and rescalings and lifetimes born or ended at any frame;
- at least 219 lifetimes in grammar G, whose only in-frame operation is the
  invertible shear `w_i += c*w_j`;
- at least 234 lifetimes for words that write only at the final target frame.

Each floor excludes PR2920's 208-lifetime optimum. The **216 floor applies to
PR2920's model**: the fork README states that G′ contains #2353's in-frame
copies and clears, and that its proof uses neither dirty restoration nor cut
order. Both count new helper lifetimes, as PR2920's `C+U` does. This package adds the
constraint `C+U >= L` to PR2920's relaxation and re-optimizes it exactly.

## Result

| Floor L | Source | Cheapest (cheap, unit) | Selected moment | Relaxed root bracket |
|---:|---|---|---:|---|
| 208 | merged #2353/#2383 (control) | (0, 208) | 0.9988962439 | (0.002104152801, 0.002104152802) |
| 216 | reported, singular mixing | (8, 208) | 0.9989395970 | (0.002083218565, 0.002083218566) |
| 219 | reported, invertible mixing | (12, 207) | 0.9989524538 | (0.002077091201, 0.002077091202) |
| 234 | reported, final-frame words | (28, 206) | 0.9990303403 | (0.002040723010, 0.002040723011) |
| 387 | unproved relay-v2 estimate | (194, 193) | 0.9998152606 | (0.001734617821, 0.001734617822) |

The **first rejecting floor is 423 lifetimes**. At L = 422 the cheapest profile
still passes. At L = 423 every feasible two-type profile has moment above one;
the cheapest is (232, 191), with moment ≈ 1.0000035.

Consequences for PR2920:

1. Its statement that (0, 208) is the unique cheapest profile holds only without
   a lifetime floor. Under any reported floor, (0, 208) is infeasible.
2. Its decision is unchanged. The restricted route still passes the optimistic
   screen under every reported floor. Under the applicable 216 floor the optimum
   is (8, 208) and the root falls by about 1.0%; it falls by about 1.3% at
   L = 219 and 3.0% at L = 234.
3. A future lifetime floor rejects this two-type relaxation only at 423 or more.
   This is above the reported floors and the 387 relay estimate. The handoff
   also quotes a first decision threshold of 333 and fixed-template allowances
   of 431 / 478 / 482; those numbers are not recomputed here. It is specific to the two-type
   route, because it includes PR2909's endpoint curve.

The optimizer form follows from two facts. Both helper prices are positive,
so no profile uses more cheap helpers than necessary. Also `q_c < q_u` for every
`a > 0`, because `q_u - q_c = 7*73^(a-1)*(1 - 7^(-a))`. Thus extra lifetimes for
a floor are cheap helpers. Removing a unit helper trades for its endpoint
marginal (at least 12) in cheap helpers, which pays only when the floor already
forces those cheap helpers. The checker does not rely on this argument: it
certifies the optimum over every feasible minimal-cheap pair.

## Method and independence

The model, template (`m = 73`, `W = 832/9`, centre 56, total paid mass 6712,
ideal idle at rank 51), original channel profile and endpoint types are PR2920's.
The certified interval engine is the existing
`research/complex-local-word-ceiling/ceiling.py` (`relax`), as in PR2920.
The endpoint curve is recomputed from the six endpoint types. When PR2920's
commit is present, the checker requires that the curve equals PR2920's
`RESULT.json` curve in both orientations.

The moment is affine in (C, U): counts enter linearly, and idle mass is the fixed
template mass minus the local mass. Three `relax` enclosures give exact-interval
coefficients. For each floor, the checker certifies that the optimizer's upper
bound is below the lower bound of every other feasible pair. Each optimizer is
also re-evaluated directly with `relax` and must agree with the affine enclosure.
Root brackets use a certified grid of `1e-12`. The threshold uses a certified
bisection: every floor decision is either a passing optimizer or a rejection of
all pairs.

This is new coverage, not a second evaluation of PR2920's root. PR2920's checker
and its formalization in PR2922 contain no lifetime-floor constraint.

## Reproduce

Python 3.10 or later, standard library only. To bind the endpoint curve to PR2920,
fetch its commit once:

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git pull/2920/head
python3 -B research/p104-two-history-lifetime-floor/verify.py
python3 -B research/p104-two-history-lifetime-floor/test_verify.py
```

The first command emits `PASS_P104_TWO_HISTORY_LIFETIME_FLOOR ...
first_rejecting_floor=423 pr2920_curve_checked=True no_new_kappa` in about 7
seconds. Without the PR2920 commit it still passes, with
`pr2920_curve_checked=False`. The test runs the positive case and 6 controls:
without a floor the optimum returns to (0, 208); a changed endpoint capacity
with the same total demand fails the PR2920 curve binding inside `compute()`; a wrong affine
coefficient fails the direct `relax` re-evaluation; 422 passes and 423 rejects;
an altered receipt fails; and a changed pinned `ceiling.py` fails before use.
The test requires the PR2920 commit.

## Limits

- The 216 / 219 / 234 floors are imported as reported. They are author-checked,
  on a fork branch, and not merged or re-proved here. If they fail, only the 208
  control row stands. The 387 estimate is unproved.
- The applicable floor is 216 (G′). The fork README itself notes that not every
  difference between G′ and #2353's model was audited; this package inherits that
  caveat. The 219 floor is proved only for shear-only mixing, which is narrower
  than PR2920's equal-frame rational operations, so the 219 row is conditional.
  The 234 floor applies only to final-frame words; whether PR2920's two named
  histories write only at the final frame was not checked.
- Everything else is PR2920's relaxation: two named histories, separate endpoints,
  favorable fractional idle at rank 51 and the fixed template. Joint acquisition,
  chronology, restoration, native execution, hosting, precision and the complete
  consumer bill remain open and are additional.

## Open next questions

- **Does a lifetime floor of 423 or more hold in the X-only monotone model?**
  Such a floor would reject the two-type route. First step: test whether the
  "private-half" count sketched in the mixer handoff (250 / 234) or a sub-7-frame
  gathering charge can exceed 423. Blocker: the handoff expects that top-level
  arguments alone cannot exceed 416, so a lower-level charge is likely needed.
- **Do other histories, for example `(1,1,5,1,1)`, lower the price under the same
  floors?** PR2920 notes that it has the same endpoint-adjacent dimensions and
  cheaper transport. First step: add its internal cut capacities to this
  optimization. Blocker: the per-cut capacity rows for that history are not yet stated.

## Credit

Nick Petalas (PR2920 / PR2909 / PR2896) for the relaxation, endpoint curve and
price model; Sagar Thakrar for the reported floors and the mixer handoff;
Hiroki Kumazaki (#2353 / #2889) for the 208 floor and span rows; Philippe Van
Velzen for relay-v2 and the window bill; Arham Tahir (#2675 / #2682), ywz65
(#2614) and Douglas Colkitt (`ceiling.py`); and the retained P104 geometry and
native lineage credited in those packages. This audit: **Sudarsh Chaturvedi**,
with substantial **Anthropic Claude** assistance in selection, computation,
controls and writing. No human review is claimed. Apache-2.0.
