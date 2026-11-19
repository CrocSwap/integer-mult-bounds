# Complete invoice identity and a valid interval

This is a source binding and an exact real inequality. It does not add a
Lean theorem or prove a multiplication algorithm.

## Sources and statement

The formal source is
[PR #7783](https://github.com/CrocSwap/integer-mult-bounds/pull/7783),
commit `47ef383d7de8b77bd198b104c84efb06191a89c2`.
The native source and caller receipt are
[PR #7761](https://github.com/CrocSwap/integer-mult-bounds/pull/7761),
commit `d5219594c9b0e80c002a75e79b85766256496b07`.
The preceding graph audit is
[PR #7785](https://github.com/CrocSwap/integer-mult-bounds/pull/7785).
Its full operator check is not repeated here.

Let `g` be the submitted native graph. Let `T` and `P` be the complete
target and paid histograms in the submitted application receipt.
For every real exponent `s`, the formal caller has the same two sums:

```text
totalCredit(caller7761, s) = sum_r T[r] r^s
totalPaid(caller7761, s, specInvoice) = sum_r P[r] r^s.
```

This statement uses the actual definitions in
[BankPrem](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/47ef383d7de8b77bd198b104c84efb06191a89c2/research/p104-banked-banner/lean/Nov15/BankPrem.lean),
[BankHelpA](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/47ef383d7de8b77bd198b104c84efb06191a89c2/research/p104-banked-banner/lean/Nov15/BankHelpA.lean),
and
[Bridge7761S2](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/47ef383d7de8b77bd198b104c84efb06191a89c2/research/p104-banked-banner/lean/Nov15/Bridge7761S2.lean).
The Lean object is parameterized by its output identity proof `hO`.
The invoice data do not depend on the choice of that proof. This audit
does not construct a Lean proof term for `hO` or for the identity above.

## Native and caller binding

The retained data-only builder applies the submitted edit journal to the
submitted graph. Its canonical digest must be
`c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84`.
The builder runs in a normal Python child process in both audit modes.
This use does not verify the edit journal's physical pulses.

For each of the 1,099 charts, the checker enumerates its binary span.
It compares that span with the actual packed `BASK` basis and the literal
`chBasis` list. It decodes `FAK`, `FBK`, `BSK` and `BTK`, then compares
every field and bank endpoint with `g`. Bank indices use the submitted
schedule order. Thus the rank calculation uses the formal chart data,
not a separate list of reported ranks.

The formal main set is the set of bits in `MB`. All 1,262 bits must equal
the literal `mainL0` list and the source interface's main owners:
`live`, `live + 112`, `hosted.X2`, and `hosted.Y2`. There are exactly
400 mains. Each climbs by eight. The other 862 fields are helpers.
Every helper has a positive climb. The packed mask is bound by identity,
not only by its cardinality.

For each bank, the checker computes the SPEC lattice distance directly:

```text
rank(U,V) = dim(U) + dim(V) - 2 dim(U intersection V).
```

All 5,746 bank endpoint pairs are nested and have positive distance.
All productive endpoint pairs are nested. The helper credit is the
positive dimension gain summed over the complement of the main set.
The mains receive no helper credit.

| Rank | Native helper count | Native paid count |
|---|---:|---:|
| 1 | 16 | 3,852 |
| 2 | 7 | 805 |
| 3 | 6 | 492 |
| 4 | 200 | 225 |
| 5 | 10 | 297 |
| 6 | 0 | 72 |
| 7 | 6 | 2 |
| 8 | 28 | 1 |
| 9 | 589 | 0 |

The actual `caller7761` definition has 2,048 copies of this graph.
Its `T` and `P` fields are the literal `TB` and `PB` lists from
[BankBannerCert](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/47ef383d7de8b77bd198b104c84efb06191a89c2/research/p104-banked-banner/lean/Nov15/BankBannerCert.lean).
Those two nine-entry tables equal `fixed_root_targets` and
`fixed_caller_paid` in the source
[application receipt](https://github.com/Clear1nsight/integer-mult-bounds/blob/d5219594c9b0e80c002a75e79b85766256496b07/research/p104-mixed-batch-boundary/evidence/application.json).

The checker then adds 2,048 native histograms to the caller tables. Both
complete histograms must equal the receipt, rank by rank. Equality of the
histograms proves equality of the power sums for all real `s`. Every
base is positive, so this identity has no zero-power exception.
It does not prove that the source caller receipt follows from a legal
caller execution. That separate obligation needs a full caller replay.

## Exact non-vacuity

Set `F(k) = sum_r T[r] r^(1-k) - sum_r P[r] r^(1-k)`.
The exact integer certificate gives

```text
F(0) = 169984
B = sum_r T[r] r ceil(log2 r) = 169886720.
```

No logarithm is evaluated. For an integer `r >= 1`, the checker computes
`b_r = bit_length(r-1)` and checks the defining binary bounds.

For `x >= 0`, we have `2^(-x) >= 1-x`. If `x >= 1`, the right side is
nonpositive. If `0 <= x <= 1`, convexity of `2^x` gives `2^x <= 1+x`.
Taking reciprocals gives `2^(-x) >= 1/(1+x) >= 1-x`.
For `k >= 0` and `r <= 2^b_r`, it follows that

```text
r^(1-k) = r r^(-k) >= r 2^(-b_r k) >= r(1-b_r k).
r^(1-k) <= r.
F(k) >= F(0) - B k = 169984 - 169886720 k.
```

Use the lower bound on target terms and the upper bound on paid terms.
At `k = 1/1000`, the resulting lower bound is exactly `2432/25 > 0`.
It is no smaller for `0 <= k <= 1/1000`. Thus the formal invoice's
`Valid` inequality holds on that whole interval. Its intersection with
the source theorem's strict domain is `0 < k <= 1/1000`.

`Valid` means paid is at most credit. It does not assert equality at a
root. This interval is sufficient to prove non-vacuity; it is not a
maximal validity interval or a new estimate of the source crossing.
No floating-point power, logarithm or root is used.

## Checks and remaining obligations

Seven controls change the caller root count, caller charge, call count,
main credit, bank count, helper credit or main identity. Each must fail
at the stated semantic comparison after source authentication. The
checker uses explicit exceptions and also runs with Python optimization.

The proof above supplies the real-variable step. Python checks its
finite hypotheses and exact integer margin. No Lean build, axiom audit,
full proof-closure review, physical realization, caller chronology,
ordinary BIT, outer assembly, stock or compiler replay runs here.
The source-aware graph builder and receipt remain consumed evidence.
There is no independent human or proof-kernel acceptance claim.
The selected multiplication exponent is unchanged. All five framework
assumptions remain.

## Open next questions

1. Add the histogram identity and positive interval as Lean theorems
   against this exact caller. The first step is to express these finite
   histograms in the existing `cdat` definitions. This package has no
   Lean build environment or proof term.
2. Bind the caller tables to a legal full caller execution. Start with
   the source receipt's finite ownership and chronology checks. Matching
   two submitted data tables does not discharge that obligation.
