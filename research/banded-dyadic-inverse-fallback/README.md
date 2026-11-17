# Banded exact fallback for the dyadic Gaussian reference

This contribution is produced by Nick Petalas. Claim type: scoped
constructive written proof with exact finite corroboration. Apache-2.0.

The exact inverse-completion path of Ali Romman's
[PR5677](https://github.com/CrocSwap/integer-mult-bounds/pull/5677) can use
O(N^2(w+1)) rational operations instead of O(N^3), where w is the forward
reference's half-bandwidth. It returns the identical complete rounded inverse
and retains the source's entire row/column residual and error certificate.
Dense output and O(N^2) rational storage remain charged. No new kappa or
selected-frontier change is claimed.

[PROOF.md](PROOF.md) gives the pivot/fill invariant, exact operation envelope,
coefficient-height bound and rounding/certificate connection. The theorem
allows arbitrary invertible integer bands, including zero leading pivots,
nonsymmetric signs and matrices without diagonal dominance. The executable
limits N to 256 and entry/precision heights to 4096 for a bounded reference
interface; the written proof applies to every finite N.

The source chooses w=O(sqrt((t+log p)log p)). The improvement is asymptotic
when w=o(N); if the prescribed band fills the whole cell the bound remains
cubic. No measured wall-clock or bit-complexity speedup is asserted.

The routine is an isolated proposed replacement. It changes no predecessor
code, Gaussian source, certificate, caller or selected record. The source's
reference-invertibility, conditioning and error theorem remain cited premises.
This is a partial answer to Open next question 2 of PR5677, rather than an
independent validation of that package.

## Evidence and reproduction

From the repository root with CPython 3.12 and the standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/banded-dyadic-inverse-fallback/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/banded-dyadic-inverse-fallback/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/banded-dyadic-inverse-fallback
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/banded-dyadic-inverse-fallback --check-source-history
```

Any CPython 3.12 path may replace the displayed interpreter. Direct replay
prints `PASS_BANDED_DYADIC_INVERSE_FALLBACK` in its JSON receipt. To retain a
generated source-hash receipt, add `--receipt` and a new path outside the
checkout. The verifier refuses to overwrite that path.

The finite check covers 2,427 matrices: 1,290 invertible and 1,137 singular.
There are 52,308 two-sided inverse entry checks, 508 row exchanges, three
complete rounding comparisons per invertible matrix and fifteen rejecting
controls. Separate complete tridiagonal inversions check the rational-operation
counter at dimensions 8,16,32. [VALIDATION.md](VALIDATION.md) specifies every
domain, counter convention, resource bound and engineering deviation.
The two solvers were produced by the same contributor; neither is independent
human or formal proof-kernel review.

No large Gaussian-cell exact fallback, predecessor scientific replay,
selected cold replay, native/tape implementation, physical integration,
supplier admission, Lean or Docker run is part of this claim. Dense inverse
storage, exact fraction growth and final integer rounding remain positive
costs. A full multiplication theorem is unclaimed.

## Sources and overlap

Base canonical main is `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision 8. The selected record is #7000; the catalogue's #5599 assessment is
historical. The selected source-binding orientation passed. The
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19591499)
states the delivered exact-completion scope. [SOURCES.json](SOURCES.json)
pins the source proof, implementation contract and original assignment as
provenance. Replay has no predecessor executable dependency.

Live open PRs, recent account PRs, handoffs, active discussions, merged-PR
searches and all-main README searches were checked for the exact fallback,
general pivoted-band version and structured inverse variants. The cached
search covered 800 open PRs, 7,403 Discussion records and 10,178 tracked local
notes. These are overlap leads, not a novelty guarantee over arbitrary diffs,
unpublished work or the literature. Classical band elimination is expressly
credited. The first verified improvement is packaged without expanding to
new inverse models or a physical implementation campaign.

## Open next questions

1. Can a consumer adopt this fallback and measure its actual fraction-growth
   and elapsed cost on one prescribed full Gaussian cell? Start by replacing
   only the exact-candidate call and retaining every original acceptance
   predicate. Large-cell runtime and the consumer's integration are unrun.
2. Can the reference retain a band-factor representation through a physical
   inverse application and avoid dense inverse output? Begin with the actual
   caller's required reads, reuse and residual contract. This package retains
   the dense table and provides no delivery, tape or restoration bill.

Structured questions and blockers are in [TASK.json](TASK.json).

## Credit

Ali Romman / aliromman PR5677 supplies the reference, open question, rounding
rule and error contract, retaining JoyboyBrian PR5479 and the Jose Manuel,
Vlado Vojdanovski, Cinna Davis, Ryanson Jonathan, Nick Petalas and Gaussian/q-LDU
lineage. Dugongue PR4554 and PR5566 retain their different near-identity
banded and Beatty-run periodic algorithms. Ali Romman PR5284 retains the
different variable-gap, diagonally dominant cyclic-band solve. Classical band Gaussian elimination,
row pivoting and determinant bounds are not claimed as new mathematics.
The new standalone completion, explicit application proof and finite verifier
are produced by Nick Petalas. Independent human and formal proof-kernel review
are unclaimed.
