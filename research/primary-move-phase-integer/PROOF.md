# The #6030 primary does not store a joint phase

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No new κ. Assumption ID: `native_all_columns`. This is one implication, not that assumption and not the other four.

## 1. Proposition

Let the selected word be `research/p104-helper470-twin-rung-removal/WORD.json.gz` at canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The selected verifier loads `local.py` from the PR5827 archive `inputs/pr5827-source.tar` and sets its `ROOT` to the depth-7 source root. That root's `research/p104-native-channel/vendor/clifford_exact.py` and `native_verify.py` are byte-identical to the copies pinned in this package.

`local.native` is the primary recipe recorder. For a chart change from frame `a` to frame `b` it stores

```text
recipe, _ = lower_child(chart(a).adjoint().then(chart(b)))
```

and later hashes those records together with the main adapters. Each record has keys `rank`, `left` and `right`. Each monomial has a field `phase` in `{0,1,2,3}` and no multiplicity.

**Proposition.** This recorder builds no joint recipe. Its registered proof sentence says "frame induction at every positive tensor width", but that sentence is a string in the returned summary. After the sentence is removed, the function contains no tensor factor, no multiplicity and no phase scaling by `f`.

On the first rank-1 `MOVE`, zero-based event 9896, `["MOVE", 236, 3, 7, false]`, the stored integer is `p = 1`. Write `U` for the width-1 operator and `U_0` for the same circuit with phase gates removed. Then `U = i U_0`, and for every pair of computational-basis inputs

```text
(U|x>) ⊗ (U|y>) = i^{2} (U_0|x>) ⊗ (U_0|y>)
```

while the same tensor with one extra factor of `i^1` disagrees. So copying the stored integer as a joint phase is false for this operator at width 2, and replacing it by `p f` is true for this operator at width 2.

## 2. Why the two readings differ

A gate `('phase', p)` multiplies every amplitude by `i^p`. The recorder's own `native_verify.state` implements that gate, and `lower_child` puts the nonzero residue on the right monomial of this MOVE. Therefore `U = i^p U_0`.

For a scalar `c` and a linear map `A`, `(c A) ⊗ (c A) = c^2 (A ⊗ A)`. Take `c = i^p` and `A = U_0`. At `p = 1` the exponent `2p = 2` is not congruent to `p = 1` modulo 4, since `i^2 = -1` and `i^1 = i`.

The exhaustive check evaluates both sides on all `512 × 512` basis pairs. It is a check of this operator, not a new proof that every scalar factors out of a tensor power.

## 3. What this does not say

The payload hash `e22642923d5437c49e2d1dc79dd6b795503499d6f33615a1df3568f0b96164c1` is read from `RESULT.json`. It is not recomputed, and the other 2,921 chart records are not lowered here. The source inspection does cover them: they are stored by the same assignment, which has no `f`.

Per-column execution of the width-1 circuit, including its phase gate on each column, is the tensor power and is consistent with `i^{p f}`. The merged phase law in `research/move-chart-phase-power` already states that identity for every MOVE on this word. This note binds the primary recorder, which that law did not read.

`owned_erasure`, `compiler`, `precision_tape` and `analytic_recovery` are untouched. No outer row or selected κ changes.
