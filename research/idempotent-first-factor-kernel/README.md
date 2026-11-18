# All-rank middle-factor classification

No new kappa. For every idempotent A over F2, this package gives a bijection
and exact count for all matrices B such that
`(I+xA)(I+xB)(I+x(I+A+B)) = I+xI`.
The data are the A-invariant kernel of B, an injective map on one fixed
complement, and an arbitrary map on the other complement.

The [proof](PROOF.md) covers every rank and dimension. It gives each rank
count and the numbers for which B, the forced third factor C, both, or
neither are idempotent. In dimension four, the totals for first-factor
ranks zero through four are `802,296,188,184,316`. The counts with neither
remaining factor idempotent are `0,0,114,168,315`.

The named rank-one count 296 and its three families are already proved in
[PR #7223](https://github.com/CrocSwap/integer-mult-bounds/pull/7223).
This package credits that result and repeats it only as a source comparison.
The new all-rank parameterization includes higher-rank cases that the
rank-one exclusion does not permit. No factor is admitted as a paid call.

## Evidence and reproduction

Use CPython 3.12 with the standard library, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/idempotent-first-factor-kernel
python3 -I -O -W error -B research/idempotent-first-factor-kernel/verify.py
```

Expected direct marker: `PASS_IDEMPOTENT_FIRST_FACTOR_KERNEL raw_matrix_cases=395316`.
The registered hook runs normal and optimized checks. Failures raise exceptions.
The verifier reads only [RESULT.json](RESULT.json). It compares two different
enumerations: subspaces with maps, and every matrix bit pattern with direct
polynomial multiplication. All 14 canonical first-factor cases through
dimension four and the named source matrix are covered. It checks exact
kernels, unique parameter tuples, each count stratum, rank histograms, both
idempotence criteria, the source fingerprint, and changed-hypothesis controls.

The finite checks corroborate the written all-dimension proof. They are not
independent human or proof-kernel review. See [VALIDATION.md](VALIDATION.md).

## Scope and overlap

Base: canonical main `e54523517d0f03e58352e647c403a5af3e525a57`.
The selected value remains `363005817/100000000000`; all five framework
assumptions remain. The revision-8 catalogue still has historical context;
the contextual picker detects this difference and the selected binding
check passes. It is not a full selected replay.

Card `joint-query-controller` changes scope to one algebraic classification.
The boundary is the exact ordered polynomial identity on arbitrary vectors.
All physical realization, preparation, ownership, restoration and complete
recursive prices are unknown. Stop at the classification; no supplier
expansion follows from these matrix counts.

The [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19709190)
records the change. The 2026-11-18 refresh searched 1,003 open PRs and 7,645
Discussion records with complete pagination. Phrase search found PR #7223,
which reference-only intake missed because its body does not name its
predecessor. Its proof and open questions were read before the claim.
The complete closed cache contains 6,175 records; a fresh updated-order
check found no closed update after that cache. No all-rank kernel result
was found. Sparse local notes, unpublished work and semantic search limits
prevent a novelty guarantee.

Before submission, Discussion refresh completed but the full open-PR refresh
timed out and retained its earlier cache. A separate updated-order page of
100 open PRs covers every update since that cache. Its four changed records
are this chat's prior result, two banked-circuit improvements and a Lean
proof link; none classifies these middle factors. The pinned PR #7223 head
was also read back and is unchanged.

## Open next questions

Which classified higher-rank factors have an admitted implementation in
an actual paired-star caller? Pin one caller and one rank-two witness.
Check its arbitrary-input action and all preparation, storage, restoration
and paid costs. The missing native implementation and consumer contract
block any saving claim. This question is not reserved.

## Credit

[CREDITS.md](CREDITS.md) pins the proofs by unpaidmoon and retains their
source lineage. Standard linear algebra supplies the subspace and complement
counts. No source code is copied. Prepared by Ali Romman with substantial
OpenAI Codex assistance. Apache-2.0.
