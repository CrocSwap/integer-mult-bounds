# The E7 weight-12 kernel words are the two receipt orbits

**Coverage check of a published classification receipt. No new κ.** The
selected conditional exponent stays `781451/250000000`. An independent
half-split of the pinned 27-dimensional E7 kernel returns the same 1638
weight-12 words as the union of the two reflection orbits recorded in
`research/e7-bitsliced-exhaustion/source/RESULT.json`.

## Result

The kernel basis is the one constructed by the pinned PR #5238 geometry:
135 frames and 27 free coordinates on which the basis is the identity. The
census splits that ordered basis after 13 generators and after 16. Each half
is listed by doubling. A pair `(high, low)` contributes `high XOR low`,
scored by integer popcount. Both splits, and `low_weight_words` at batch
sizes 16 and 8, return one set: zero plus 1638 words of weight 12. No nonzero
word in the `2^27` span is lighter.

The 63 reflection permutations are the frozen `reflections` function in
`research/e7-bitsliced-exhaustion/source/verify.py`. Each is a permutation of
the 63 roots and preserves the frame set, because that function rejects a
failure. Starting from the two receipt representatives:

| Orbit | Size | SHA256 of the sorted masks |
|---|---:|---|
| diagonal | 630 | `d08f659fab919baab7b2c87c0b7e55edb5a3e23e05a313522f0b17e684d8ee39` |
| product | 1008 | `a9bb36def7396f184d343e38f410d705a50be3188b40725235f866ad0753309b` |

Those are the `orbit_sha256` fields of `source/RESULT.json`. The orbits are
disjoint, every element has weight 12, and their union is the census. The
hash is `SHA256` of `json.dumps(sorted(masks))` with the standard separators,
the same encoding as the predecessor.

Deleting one census word makes the predecessor partition check fail. Feeding
it an overlapping second orbit fails. Deleting one diagonal-orbit word changes
its hash. Clearing one bit of the diagonal representative produces a weight-11
seed whose orbit hash differs and which does not stay inside the weight-12 set.

## Scope

Task card `replay-runtime`, priority revision 8, base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Scope status is **refined**.

The card asks for a new measured speedup that keeps coverage. PR #5729
published the bit-lane speedup and was archived without an independent
scientific replay. `research/e7-bitslice-coverage-check` compared the iterator
with this census and left the reflection orbits unreplayed. This package is
that orbit comparison. It does not time the engine, recompute quadratic ranks
or single-omission kernels, rerun the 120 ambient root slices, or install the
iterator into another consumer.

Ordered eligible list for session r93, rebuilt on 2026-11-03 against
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The overlap snapshot at
2026-11-03T13:22:29Z had 572 open PR bodies and 6625 discussion records.
Structured handoffs are dropped when the post is completed, a merged result
answers the question, or the canonical artifact is an open pull request. That
removes the 19 October index, the H25 requests, the 2 November PR6353 review
chain (#6355, #6357, #6359, #6360, #6361), and the later #6376, #6378 and
#6396 artifacts. The 28 October null-artifact handoffs that were later
answered are dropped with them, including the absolute-phase word, the
residual two-cycle incidence, the Schur-bandwidth carve and the RootPlan
descriptor bound. Prose handoffs already marked DONE or RELEASED, and the
PR6551 kappa handoff whose artifact is an open pull request, are dropped.
No structured claim was unexpired. Work already delivered by this account,
including the named upstream pull requests and fork `cursor/*` branches, is
dropped. The revision-8 "Next bounded decisions" table then supplies six
rows. A row stays while that table still states the decision. Catalogue
cards not named by those rows follow in file order.

1. Complex helpers (`p104-side-correction`, `coverage-law-change`).
2. BIT (`bit-helper-contract`).
3. New decoders and interfaces.
4. Supplier audit (`supplier-boundary-audit`).
5. All-size audit (`uniform-transfer-audit`).
6. **This package.** Verification tooling (`replay-runtime`): the orbit-hash
   partition left open by the #5729 coverage check.
7. `bit-new-register-model`.
8. `r437-carrier-integration`.
9. `complex-rank-shape-decoder`.
10. `complex-new-helper-inventory`.

Rows 1 through 5 stay because the priority text still states those
decisions. `research/e7-bitslice-coverage-check` answered the word-set half
of row 6 and named this orbit comparison as its first open question. The six
rows already name `p104-side-correction`, `coverage-law-change`,
`bit-helper-contract`, `supplier-boundary-audit`, `uniform-transfer-audit`
and `replay-runtime`. Items 7 through 10 are the next catalogue cards in file
order after those six names.

## Reproduce

Python 3.12 and the standard library, from the repository root. The two
half-splits scan `2^27` words each.

```sh
python3 -B scripts/research_package.py --package research/e7-orbit-hash-partition --check-only
python3 -I -B research/e7-orbit-hash-partition/verify.py
python3 -I -O -B research/e7-orbit-hash-partition/verify.py
python3 -B scripts/research_package.py --package research/e7-orbit-hash-partition
```

The direct verifier prints

```text
PASS_E7_ORBIT_HASH_PARTITION supports=1638 diagonal=630 product=1008 reflections=63 quadratic_ranks_replayed=false no_new_kappa=true
```

Not run: the #5729 timing harness, quadratic ranks, single-omission kernels,
the 120 ambient root slices, another decoder code, Lean, Docker, and
`make frontier6030-verify`.

## Open next questions

1. Do the two receipt representatives still have quadratic ranks 6 and 2,
   with every single omission of rank 11? The orbit hashes identify the sets
   and do not rerun that half of the classification. First evaluate `form_a`
   and `form_b` in `source/verify.py` and compare `supported_rank` and
   `quadratic_matrix` with the receipt.
2. Does the same set equality hold for one other deletion or decoder code?
   The bit-lane proof leaves that consumer unbound. First name its generators,
   width and weight bound, then compare one half-split with `low_weight_words`
   on that basis alone.

## Credit

The geometry and minimum-support statement are Nick Petalas's PR #5238,
retained in `research/e7-bitsliced-exhaustion/source/vendor/PR5238.py`. The
equality classification, reflection code and receipt are Ali Romman's
PR #5669, frozen in `research/e7-bitsliced-exhaustion/source/verify.py` and
`source/RESULT.json`. The bit-lane engine is Ali Romman's PR #5729. The
word-set comparison that left this orbit question open is
`research/e7-bitslice-coverage-check`. This package does not modify those
files.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
