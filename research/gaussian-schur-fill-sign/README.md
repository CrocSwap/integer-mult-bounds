# Exact signs and noncancellation of real Gaussian Schur fill

This contribution was produced by Nick Petalas.

For every bandwidth b>=1 and every finite linear path, truncate the real
Gaussian kernel t^((i-j)^2) to |i-j|<=b. If 0<t<=1/3, every principal
elimination pivot is invertible. The Schur entry between survivors i<j is
nonzero exactly when the chain through the eliminated indices between i
and j has no gap larger than b. Its sign is (-1)^k, where k is the number
of those eliminated indices. Diagonal Schur entries are positive. Positive
row and column scalings preserve all these conclusions.

Claim type: scoped written mathematical proof with exact finite
corroboration. [PROOF.md](PROOF.md) proves the all-size statement using an
elementary negative-root factorization and ordered minors. Classical
factorization and nonintersecting-path arguments are not claimed as new
techniques. No independent human or formal proof-kernel review is claimed.

This answers the explicit actual-real-entry gap in Ryanson Jonathan's
[PR4407](https://github.com/CrocSwap/integer-mult-bounds/pull/4407) for the
stated parameter range. That predecessor's generic support formula and
finite-field census are cited, not replayed. The new result removes the
possible-cancellation qualification for this restricted Gaussian family.
It also determines every surviving sign.

The first fixture has n=12, b=3, t=1/3 and eliminated set {4,5,6,7}.
Its entry between 1 and 10 is exactly 1/9170703360, at survivor-order
distance five. This is an actual Gaussian fixture, distinct from the
inherited equal-weight paths.

## Evidence and reproduction

Use CPython 3.12 and its standard library from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gaussian-schur-fill-sign/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/gaussian-schur-fill-sign/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-schur-fill-sign
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-schur-fill-sign --check-source-history
```

Substitute another CPython 3.12 interpreter elsewhere. Expected markers are
`PASS_GAUSSIAN_SCHUR_FILL_SIGN`, `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`.

The verifier checks 336 polynomial evaluation signs through bandwidth 12.
For t=1/3 and 1/4 and b=1,2,3 it checks every nonempty ordered minor of
the six-vertex kernel: 5,538 minors, of which 4,350 are positive and 1,188
are zero. It explicitly constructs 4,350 nonintersecting path families.
It then checks all 3,012 nonempty-survivor Schur layouts through n=8,
including empty eliminated sets, and all 44,538 surviving entries:
27,106 positive, 8,496 negative and 8,936 zero. Integer Bareiss determinants
and independently implemented rational Gauss-Jordan complements agree with
the claimed criteria. There is no finite-field or floating-point test.

The first fixture and an exact positive-gauge identity pass. Six unsupported
input fixtures are rejected; three mathematical scope controls retain the
need for truncation, eliminated-vertex parity and a restricted t range.
Checks remain active under optimized Python. Each run emits a generated
receipt containing the six package-file hashes and interpreter version,
and writes nothing. Bounded verification corroborates the universal proof;
it does not replace it.

## Scope and provenance

The parameter range is a sufficient range, with no optimality claim. A
concrete Gaussian caller has not been shown to meet it. Periodic kernels,
complex phases, finite-precision stability, condition numbers, physical
routing/hosting/stock/tape costs, supplier admission and the complete
multiplication theorem are unrun or unproved here. No new kappa or
selected-frontier change. No Lean, Docker, predecessor census or selected
full cold replay was run.

The `formal-interface-lemma` card is changed to this written real algebraic
interface theorem. The current selected-baseline metadata orientation
passes; it is not a mathematical premise. Canonical base is
`ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`, priority revision 7.
[SOURCES.json](SOURCES.json) pins predecessor and orientation documents as
historical provenance, with no live scientific input or imported code.
[TASK.json](TASK.json) records the scope change and structured questions.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19145574)
records the live overlap coverage and its limits. Main-tree README and
merged-PR searches supplement the sparse local cache; none covers unpublished
work or every historical diff.

The verifier uses dynamically allocated exact Python integers, fractions and
bounded lists, with no fixed-allocation claim. It has no recursion, solver,
subprocess or mutable shared state. Dimensions are at most 12; the principal
exhaustive sweep stops at eight. Every function is shorter than 60 physical
lines. Both registered runs treat warnings as errors.

## Open next questions

1. Does one concrete retained caller have this real kernel after positive
   gauges and satisfy t<=1/3? Pin the literal kernel and derive its parameter
   and truncation convention. Complex or nonpositive phases and the actual
   caller binding remain blockers. Do not infer admissibility from this
   support theorem.
2. What is the largest bandwidth-uniform t range preserving the strict
   ordered-minor criterion? Start with the generating polynomial's roots.
   A uniform proof or precise obstruction is needed; a finite table alone
   cannot establish it.

## Credit

Credit Ryanson Jonathan/PR4407 for the real-entry question and generic
carve formula; unpaidmoon/PR4373 for the separated carve theorem;
James Reed/PR4285/4298/4299 for earlier bandwidth fixtures; and Cinna
Davis/PR4100 for the Gaussian caller and retained predecessor lineage.
The new repository result is the restricted real-Gaussian noncancellation
and sign theorem. New work is Apache-2.0. No literature-priority claim.
