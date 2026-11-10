# Three-carrier merges with a rank-two tail cost at least 22

A single full-support merge of three fixed PR6030 carriers, with paid tail
rank two and source-normal retention, has total paid rank at least **22**.
Separate delivery costs **21**. This settles the rank-two-tail case of
Matarener's [PR6315](https://github.com/CrocSwap/integer-mult-bounds/pull/6315)
question under the explicit retention hypothesis required by CubeJerry's
[PR6323](https://github.com/CrocSwap/integer-mult-bounds/pull/6323).

Claim type: **scoped proof with a finite certificate**. No new kappa is claimed.
Paid rank is the sum of frame-dimension drops. This result does not order
concave recursive moments, and 22 is not claimed attainable.

## New step and evidence

The [proof](PROOF.md) grants receivers all individual carrier values available
anywhere in their path unions, plus the one merged tail value. For each triple,
take the quotient by its three source normals. Two path unions of dimension
at most seven can cover at most 28 quotient points. But receivers demanding
exactly one of two carrier coordinates occupy at least 39 quotient points.
Thus at least two pre-merge paths pay seven, while the third pays at least six.
The rank-two tail raises the total to at least 22.

[verify.py](verify.py) enumerates all 56 triples and all three pairs in each.
The 168 quotient counts have histogram `{39: 72, 46: 72, 47: 24}`. It also
enumerates all 651 four-dimensional subspaces of F2^6 and their 423801 ordered
pairs, confirming the cover capacity 28. Explicit coset fixtures, strict
threshold checks, invalid-input rejection and 10648 integer-cost tuples test
the new certificate. No predecessor executable is imported or replayed.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-triple-merge-tail2/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-triple-merge-tail2
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-triple-merge-tail2 --check-source-history
```

On another machine, replace the interpreter path with its CPython 3.12 path.
Expected markers are `PASS_P104_TRIPLE_MERGE_TAIL2`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
The registered normal and optimized commands each have a 120-second limit.
Optional `--output /absolute/new/external/receipt.json` writes a generated
receipt binding every local package file and live input hash. It refuses an
existing destination or one inside the checkout. Default replay writes no files.
Exact source pins are in [SOURCES.json](SOURCES.json).

## Limits

The fixed code, its independent contents, decoder zero supports and walk
bound are cited premises from PR6315. Source normals must lie in the merge
dual. A common frame alone is insufficient, as PR6323 explains. Pure paths
and one full-support merged scalar are the receiver model. No extra mixtures,
feedback or arbitrary public-dirt cancellation are granted.

Longer tails, merge trees, codes with nine or more carriers, physical purity,
dirty restoration, chronological delivery, native realization and the complete
signed supplier bill remain open. None of the five selected framework
assumptions is discharged. No selected cold replay, predecessor audit, Lean
build, independent human review or formal proof-kernel acceptance is claimed.

## Open next questions

The structured questions are in [TASK.json](TASK.json). First price a tail of
rank three using its new path dimension limits and quotient covers. A different
route would construct a pure arbitrary-input relay that relaxes source-normal
retention, with every dirty restoration cost charged. Neither direction has a
physical construction or complete invoice here.

## Implementation scope

The verifier uses bounded finite domains, explicit exceptions that remain active
under optimization, and functions below 60 lines. Python allocates managed
objects during enumeration, a deviation from fixed steady-state allocation.
Input reads and decompression are capped at 16 MiB each; geometric sets contain
at most 512 binary vectors, 104 ports, 168 records and 651 subspace masks.
The 423801 pairs are streamed. The integer check has 22^3 bounded iterations.
These bounds replace unavailable static allocation control in CPython. Revisit
the bound if any dimension or input cap changes. Warning-strict execution and
source compilation provide the interpreted-language diagnostics.

## Credit

This result was produced by Nick Petalas. Credit Matarener for PR6315's open
question and carrier model, CubeJerry for PR6323's corrected premise,
DreamingOfClouds for PR6030, and the fragmentation, owned-boundary and
carrier-uniqueness contributors credited in those packages. Predecessor claims
are cited premises, not new results here. Apache-2.0.
