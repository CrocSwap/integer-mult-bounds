# Sources and credit

Ali Romman prepared this result with substantial OpenAI Codex assistance in
research, implementation, verification and writing. Apache-2.0 applies. The
checking paths have one author and do not constitute independent human review.

The exact PR7001 native and caller, and the source replay of
[PR #7720](https://github.com/CrocSwap/integer-mult-bounds/pull/7720), are retained
unchanged from head `3e56de8c160f259612f9766e06bf6990c7b5a3ef`:
[source checker](https://github.com/aliromman/integer-mult-bounds/blob/3e56de8c160f259612f9766e06bf6990c7b5a3ef/research/bit-single-relation-bank-obstruction/verify.py),
[coordinate-set replay](https://github.com/aliromman/integer-mult-bounds/blob/3e56de8c160f259612f9766e06bf6990c7b5a3ef/research/bit-single-relation-bank-obstruction/independent.py), and
[credit](https://github.com/aliromman/integer-mult-bounds/blob/3e56de8c160f259612f9766e06bf6990c7b5a3ef/research/bit-single-relation-bank-obstruction/CREDITS.md).
Its helper-relation theorem is separate from this changed paid-path question.
[SOURCE-PINS.json](SOURCE-PINS.json) binds all 19 retained files and license
copies to exact Git blobs and SHA-256 hashes.

The original [PR #7001](https://github.com/CrocSwap/integer-mult-bounds/pull/7001)
[notice](https://github.com/CrocSwap/integer-mult-bounds/blob/d777f3a0aa2878bea0478918923dabcf86b9878b/research/paired-query-only-bit/NOTICE)
credits Jerry Chen / @CubeJerry for the paired source and QUERY-only lineage,
DreamingOfClouds for the chain-root caller, zxv and retained authors for the
native export, and Ali Romman and Cinna Davis for the root/native lineage.
All original notices and licenses remain unchanged.

ToikY's [PR #7293](https://github.com/CrocSwap/integer-mult-bounds/pull/7293)
and its [proof](https://github.com/ToikY/integer-mult-bounds/blob/b28b6bb7e0153c4c252b7e907ec0d501edfbe069/research/bit-destination-span-bound/PROOF.md)
exclude source formation from original live destination rows. That proof
explicitly leaves changed paid deliveries outside scope. The present result
retains all past rows and checks every cheaper nested donor chart, in both
orientations. The zero-rank cases are credited overlap, not the new result.

ToikY's [PR #7200](https://github.com/CrocSwap/integer-mult-bounds/pull/7200)
and [PR #7306](https://github.com/CrocSwap/integer-mult-bounds/pull/7306)
exclude cached donors for 35 adjusted deliveries on an eight-port retag.
This result concerns every original arrival. Their exact retag claims remain
separate. The joint helper-subspace result in
[PR #7722](https://github.com/CrocSwap/integer-mult-bounds/pull/7722)
changes productive promises while retaining paid paths; it is not imported
as evidence here. No P104 or half-sum CLEAR result is used or changed.

The new contribution is the complete current-word single-delivery rank floor,
all 70357 separating witnesses, a distinct geometric check and the complete
signed consequence. No priority claim is made for linear separation or causal
bank reconstruction.
