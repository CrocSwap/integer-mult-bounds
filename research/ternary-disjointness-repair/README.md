# Ternary disjointness needs a full-rank additive identity repair

For every odd h >= 3 and every field F of characteristic three, disjointness
on the nonempty proper subsets of [h] satisfies

```text
rank_F(I-A_h) = 2^h-2.
```

Exactly 2^h-2 additive scalar rank-one terms are necessary and sufficient
to repair A_h to the identity. This is a **scoped algebraic proof**, with an
explicit inverse and bounded exact corroboration. It gives a maximal-rank
obstruction to cheap additive repair in this ternary counterpart of the
Boolean-lattice endpoint. It does not assume a ternary physical supplier.

[PROOF.md](PROOF.md) derives a polynomial inverse of the full tensor matrix
and proves that its two-endpoint block is nonsingular. Deleting those
endpoints leaves an invertible repair. The resulting explicit inverse is
checked literally in the finite replay. Even h is outside the theorem;
h=2 is a counterexample to dropping the oddness hypothesis.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ternary-disjointness-repair
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/ternary-disjointness-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ternary-disjointness-repair --check-source-history
```

The manifest runs the verifier normally and with optimization enabled. Each
run computes the ranks at h=3,5,7,9; verifies the full polynomial inverse,
endpoint block and corrected interior inverse at h=3,5,7; independently
enumerates all 729 candidate kernel vectors at h=3; and checks six rejecting
controls plus the h=2 counterexample. It prints a generated report bound to
the hashes of all six package files, followed by
`PASS_TERNARY_DISJOINTNESS_REPAIR`. No receipt is handwritten or required
as a committed input. The all-h and all-field conclusions come from the
written proof, not the finite enumeration.

## Scope, provenance and credit

Scientific base: `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority revision 7.
The selected frontier remains unchanged. The `formal-interface-lemma` card
is changed to an original characteristic-three side theorem; this is not
a formalization or a replay of another contribution.

Ali Romman's [#4962](https://github.com/CrocSwap/integer-mult-bounds/pull/4962)
provides the binary rank theorem, tensor representation and endpoint-deletion
approach. Its exact scientific head is
`378275c8e1228d7cdad4888d808a8b8c6395b32e`. Its retained proof and README
are pinned as provenance, not executed. mikey1201's
[#172](https://github.com/CrocSwap/integer-mult-bounds/pull/172) supplies
the earlier binary disjointness endpoint, with the icekylinx/#144 compiler
and bookkeeping lineage credited there. No predecessor implementation or
cost ledger is imported. The new theorem and verifier are produced by Nick Petalas.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.

Before claiming, live PRs, recent account contributions, handoffs, active
Discussions, question-specific local reservations, and all-main README and
merged-PR term searches were checked. The supplementary cache covered 331
open PRs and 4,356 Discussion records; local note coverage was sparse.
These checks do not cover arbitrary diffs or unpublished work. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144847)
aimed for a first original rank statement; the odd-dimensional theorem is
that first result, and the even-dimensional question is left open under the
instruction to ship the first improvement.

Physical coefficient preparation, paid reads/copies, dirty restoration,
native frames, compiler/stock/precision/tape costs, actual caller integration
and complete multiplication bounds remain unproved. No binary invoice is
transferred to characteristic three. No selected cold replay, Lean, Docker
or predecessor scientific verifier is run.

## Verification design

The checker has no recursion, external commands or input files beyond its
six source hashes. Every matrix dimension is capped at 512. The largest
elimination is 510 by 510, the largest dense inverse check is 128 by 128,
and the separate kernel census has exactly 3^6 vectors. Functions stay
below 60 lines. Explicit checks remain active under `-O`.

Power of Ten rule 3 deviation: CPython allocates integers and lists during
arithmetic. Scope is this terminating, fixed-size verifier; fixed dimension
guards bound live storage by O(512^2) scalar slots and retained case results
are limited to four rows. Normal/optimized replay verifies those guarded cases. A future
larger replay must revise the explicit capacities and memory analysis.
Warning-strict execution supplies the available interpreter diagnostics;
there is no project-wide static analyzer requirement for this standalone
standard-library proof check.

## Open next questions

- What is rank_F3(I-A_h) for even h >= 4? This would complete the ternary
  classification. Start with the full tensor eigenspaces and the two-endpoint
  restriction when T^4=I; the odd-dimensional inverse no longer applies.
  Blocker: that singular full-matrix deletion calculation is not done here.
- Can a nonadditive physical repair avoid this rank-one obstruction?
  Start by stating an all-input ternary identity and its complete paid bill.
  Blocker: no such physical caller or accounting contract is supplied.
