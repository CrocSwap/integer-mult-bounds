# A cyclic product gap does not replace pointwise contraction

**Adversarial mathematical audit / scoped negative result; no new κ.**
The retained weighted cyclic inverse assumes every coefficient is contractive.
This package audits the proposed relaxation that only the complete cycle
product needs a fixed gap from one. That relaxation preserves algebraic
invertibility, but cannot preserve a precision or magnitude budget depending
only on that gap, the input bound and cycle length. Retiming the same rounded
scan does not fix the problem.

The precise object is `inverse_scan` and its `validate` caller in
[`source_scan.py`](../cubic-cyclic-inverse/source_scan.py), together with
PR628's retained [weighted-scan proof](../grouped-dirty-cyclic/vendor/PR628-WEIGHTED-PROOF.md).
The raw helper checks its computed closure denominator; the complete caller
also checks stable roots and exact unit phases. **The complete caller rejects
our expansive-coefficient family. This is not a defect in its accepted
contract or a counterexample to the selected construction.**

The new evidence consists of an all-length, all-cut rounding obstruction,
an explicit sufficient certificate for a relaxed scan, and source-bound
checks against a separate rational matrix solver. The inverse formula and
affine closure are standard algebra; no literature-priority claim is made.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/cyclic-product-gap-audit
```

Expected verifier line:

```text
PASS_CYCLIC_PRODUCT_GAP_AUDIT family=16800 dense=240 caller=24 controls=9 no_new_kappa
```

Then nine focused tests and `PASS_REGISTERED_RESEARCH_PACKAGE` pass. A direct
replay also works: `python3 -I -O -B research/cyclic-product-gap-audit/verify.py`.
The default verifier reads and compares [RESULT.json](RESULT.json); only its
explicit `--write` option regenerates that package-local receipt.

## Statement and all-cut counterexample

For a cyclic array of length L, let

`(Wy)_i = a_i y_(i-1)` and `C = product_i a_i`.

Coefficients are fixed exact complex values throughout both passes. Reversing
the physical cycle gives the identical argument in the other direction.
Because `W^L = C I`, for `C != 1` the exact inverse is

`(I-W)^-1 = (I + W + ... + W^(L-1))/(1-C)`.

Different powers below L reach different input columns. Thus its infinity
operator norm is exactly

`max_i [sum_(j=0..L-1) |a_i ... a_(i-j+1)|] / |1-C|`,

where the empty product is one. A closure gap controls the denominator,
while the partial products in the numerator still require bounds. At L=2,
`a=(M,1/(4M))` has `C=1/4`, but its inverse norm is `4(M+1)/3` for M>=2.

There is also a stronger, algorithm-specific precision obstruction. Fix any
integers `k>=1`, `L>=2`, `w>=0`; put `M=2^k`, `u=2^-w`, and

```text
a = (M, 1, ..., 1, 1/(4M))
x = (0, 0, ..., 0, 1).
```

The exact solution is `(4M/3, ..., 4M/3, 4/3)` and the closure gap is always
`3/4`. In the second pass, the coordinate with coefficient M is computed
as `round_w(M * previous)` with zero input. Both the rounded seed and every
previous value belong to `u Z`; M is an integer, so this final coordinate
belongs to the coarser lattice `M u Z`. This holds at **every cyclic cut**,
including when that coordinate is the first or last operation. The nearest
distance from `4M/3` to this lattice is `M u/3`: `4*2^w` has residue one or
two modulo three. Therefore every such two-scan execution satisfies

`|computed_large - exact_large| >= 2^(k-w)/3`.

For error at most `2^-p`, the necessary integer fractional width is
`w >= p+k-1`. No guard depending only on `p`, L, B=1 and the fixed closure
gap can work for all k. Stored magnitudes also grow at least as `4M/3`.
This is a proof about this rounded recurrence and its stated coefficient
class, not an impossibility theorem for other solvers or multiplication.

The seed-73 illustration uses `k=9`, `w=11`, L=2. The unchanged raw helper
returns `2731/4` instead of `2048/3` at the large coordinate: error `1/12`.
Illegally replacing the pointwise margin by `beta=3/4` in the old
`6(B+1)u/beta^3` estimate would give `1/72`. Its denominator test passes.
Representing these coefficients through `inverse_factor` with `rho=4`
requires phases `(2048,1/512)`; `validate` rejects them as nonunit. This
explicitly distinguishes a failed relaxation from a current acceptance bug.

## A sufficient relaxed-scan certificate

This certificate permits expansive individual coefficients. It pays for
both rounded first-pass quantities, the closure division, every second-pass
prefix and numerical height. It is conservative, not an optimal guard.

Write the coefficients and input in the chosen traversal order, j=0..L-1.
Assume `|x_j|<=B`, `A_j>=|a_j|`, and `0<delta<=|1-C|`. Every completed
multiply-add, product multiplication and division is rounded with complex
absolute error at most u. Set

```text
Q_-1 = 0,  Q_j = 1 + A_j Q_(j-1)
P_-1 = 1,  P_j = A_j P_(j-1)
q = Q_(L-1),  d = delta - u q > 0
S = B q / delta
E = u q (1 + S) / d + u.
```

Inductively, the exact zero-seed first pass has `|z_j|<=B Q_j`; errors in
its rounded z and its rounded running product are each at most `u Q_j`.
Consequently the rounded denominator has modulus at least d. The exact
periodic seed `s=z_(L-1)/(1-C)` has modulus at most S. If hats denote the
rounded numerator and denominator, then before the division's rounding,

`|zhat/dhat - s| <= (u q + |s| u q)/d`.

After rounding, its error is at most E. A second induction proves, at every
coordinate,

`|computed_j - exact_j| <= P_j E + u Q_j`.

This is uniform over all lengths and fixed exact complex coefficient tables
satisfying those hypotheses. No contraction of individual coefficients was
used. An uncertified denominator is an unresolved/rejected certificate, not
evidence that the actual scan necessarily fails.

For a stored-state magnitude certificate, take the maximum H0 of

```text
1, B,
(B+u) Q_j,
P_j + u Q_j,
1 + P_(L-1) + u q,
S + E,
(B+u) Q_j + P_j (S+E).
```

These bound initialization, first-pass z and product, the subtracted
denominator, the seed, and second-pass values. They also bound each completed
operation before its final rounding. A sufficient signed integer reserve is
`2 + ceil(log2(1+H0))`; the fractional width w and coefficient descriptions
are additional storage. Internal scalar multiplication/division scratch must
be charged separately.

`certificate` computes exact rational envelopes using
`A_j=|Re a_j|+|Im a_j|`, `B=max_j(|Re x_j|+|Im x_j|)`, and
`delta=max(|Re(1-C)|,|Im(1-C)|)`. These are respectively upper, upper and
lower bounds for the complex modulus. The executable thus needs no floating
point square root or logarithm. Its acceptance tests compare squared exact
errors and magnitudes with these rational bounds.

## Cost and remaining interfaces

The unchanged two-scan primitive performs 3L complex multiplications, 2L
complex additions, one subtraction, one complex division, and `3L+1`
roundings. It reads each input twice, queries each fixed coefficient twice,
and writes each output once. Sequential rewind/return costs O(L) movement;
coefficient preparation and access remain paid. No required arithmetic,
source access, restoration, frame change or recursive child is removed here.
An in-memory observer checks the unchanged helper's input reads, writes,
coefficient queries, rounding count, and completed values before/after each
rounding. It includes the closure denominator; arithmetic inside an ideal
complex division is outside the completed-operation height statement.

The diagnostic certificate is **offline exact rational arithmetic**. Exact C,
P and Q descriptions can grow with L and coefficient description length;
this is not the original bounded-width running-product implementation.
Supplying or computing valid envelopes, reading their descriptions, and
executing at their integer/fractional widths must be added to any proposed
physical interface. This audit neither derives a faster bit-time recurrence
nor adopts a noncontractive factor in a supplier.

The proof assumes one fixed coefficient table, exact coefficient access and
the stated completed-operation rounding model. Approximate coefficient
preparation, aliasing/mutation, fixed-tape routing, arbitrary dirty storage,
common-label realization, physical hosting, all-size compilation and analytic
transfer retain their own obligations. The selected κ and all supplier
sources remain unchanged.

## Evidence, sources and overlap

Base: `410026dc5513b87db92ae98571d1d5984c69a983`; assignment seed **73**,
adversarial-audit track. [TASK.json](TASK.json) records three candidate tasks,
the local claim, selection, bounded domain, stopping rule and open questions.
No pinned sprint coordination issue existed in the entry snapshot, so the
claim was recorded locally as the donor instructed.

[SOURCES.json](SOURCES.json) pins all consumed inputs by base Git blob and
SHA256. Selected-record/catalogue pins are historical provenance rather than
moving acceptance dependencies. The source-bound baseline at entry passed;
its accepted conditional saving was `0.001672660197076918`, with the complex
supplier binding. [VALIDATION.json](VALIDATION.json) records actual checks and
the final overlap refresh.

The finite receipt checks:

- All **16,800** family executions: k=1..16, w=2..16, L=2..8, every cyclic
  cut and both physical directions by reflection. The lattice lower bound
  holds even when the general sufficient certificate declines admission.
- **240** complex rational systems of lengths 1..6, compared with a separate
  real `2L x 2L` Gaussian-elimination oracle. Inputs use a fixed declared
  coefficient alphabet and seed-73 generation; this is not exhaustive complex
  coverage. Singular nominees are deterministically changed to have a zero
  final coefficient, and the solved tables remain nonsingular.
- **24** unchanged full-caller executions at lengths 1,2,3, both directions
  and four unit-phase patterns, with nonzero dirty targets, exact source
  restoration and independent dense accuracy checks.
- Nine semantic/domain controls: missing prefix amplification, an invalid
  gap-only precision bound, a gap-only integer bound, rounded-product loss
  of the denominator, actual zero-denominator failure, retained-caller
  rejection, singularity, shape and precision type. Focused tests additionally
  reject missing/corrupted source bytes, corrupted/ill-typed receipts, and an
  extra uncharged source read that leaves the mathematical output unchanged.

The observer checks **311,880** rounding events across the family and dense
screens, with all stored/completed scalar heights checked in admitted cases.
Of the 16,800 family calls, 9,932 receive a sufficient certificate and 6,868
are explicitly left uncertified; all still obey the lattice obstruction.

The independently represented dense solve supplies an accuracy check; the
second rounded replay only corroborates implementation of the same algorithm.
All code and proofs were produced in this session with AI assistance. There
is no claim of independent human review or proof-assistant verification.
Finite replay does not prove the all-length theorem; the written arguments
above are its proof, subject to their explicit hypotheses.

The fresh entry overlap search covered 823 open PRs, 158 discussion records
and 326 local records with complete reported remote pagination. Its nearest
match was Charles Bethin's [PR764](https://github.com/CrocSwap/integer-mult-bounds/pull/764),
head `983d66f0f2e48ee500ec7eee2da9244c001c5064`, which sharpens the rounding
bound **under pointwise contraction**. This audit changes that hypothesis and
proves why even changing the scan cut cannot recover a product-gap-only guard.
No PR764 code is imported and no contraction-only optimum is reproved.
Overlap coverage excludes arbitrary code diffs; absence of a match does not
prove novelty.

## Open next questions

1. Identify an actual source-bound expansive cyclic factor and certify all
   required cuts before relaxing an admission contract. This could establish
   whether the general bound is useful, but coefficient preparation,
   description growth and physical execution remain blockers. The next step
   is an exact coefficient-envelope/closure-gap calculation, not a κ claim.
2. Price diagonal balancing of the explicit family, including input/output
   scaling, both grids, numerical height and exact restoration. Balancing
   might relocate the expense into scaling; a legal common-label and storage
   contract plus a complete invoice is required before calling it a saving.

## Attribution and license

Prepared for Charan (@theon199), with substantial OpenAI Codex assistance in
selection, mathematics, implementation, testing and writing. No subagents
were used. New files are under the repository's Apache-2.0 license.

Credit Chafik Boukhalfa (@chafreaky), whose PR628
`0768f97d06c623b8211e651543c66135796b62bf` supplies the stable weighted scan
and whose incorporated PR905 supplies the consumed coarse-source wrapper;
Ali Romman (@aliromman), PR621
`520774462b19b29af41554b74def31f9d01e997e`, for the kernel/circle lineage;
and Charles Bethin for the sharper contraction-only PR764 boundary. The
predecessor [NOTICE](../cubic-cyclic-inverse/NOTICE.md) retains the standard
filtering, factorization and other source attributions. No predecessor file
or selected-frontier record is edited.
