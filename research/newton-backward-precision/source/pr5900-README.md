# Sharp full-precision depth for Gaussian Newton residuals

For the degree-R consecutive-interval Gaussian Newton residual, every
Walsh prefix through depth **n-R-1** needs full creation precision
Q=p+2n-R-1 under the max-descendant demand contract. The cutoff is sharp
for every interpolation offset. At depth n-R a prefix lies entirely in
the zero residual band and needs no creation precision.

The resulting residual-gather ADD precision mass is at least

```text
2^n (n-R-1) (p+2n-R-1).
```

This is a **scoped written proof with finite corroboration**. It extends
Ali Romman's [PR #5825](https://github.com/CrocSwap/integer-mult-bounds/pull/5825)
degree-zero obstruction to arbitrary positive degree. The new argument
uses the first surviving Gaussian digit and a finite-difference identity.
The exact full-precision prefix count at every depth is also given in
[PROOF.md](PROOF.md), including negative Newton offsets and arbitrary
axis order. Classical binomial identities are not claimed as new.

For n >= 4 and 1 <= R <= floor(n/2)-1, the residual alone costs at least
(n/2) 2^n (p+n). At p=Theta(n) this is Omega(2^n n^2), even granting a
free bulk. This removes the predecessor's uniform-bulk-precision premise
in that low-degree range. It is an ADD precision statement about the
named graph, not a physical bit-time or arbitrary-circuit lower bound.

## Evidence

The self-contained [verifier](verify.py) imports no predecessor code and
runs no predecessor fixture. Its complete fixed domains are:

- Positive-degree Gaussian coefficients for 2 <= n <= 24, every
  1 <= R < n, every 0 <= a <= n-R and every 0 <= j <= n. There are
  49,726 coefficients, including 14,950 negative offsets, 2,576 zero-band
  witnesses and 29,900 consecutive unit-containing windows.
- All binary prefixes for 2 <= n <= 10, every positive R and permitted a,
  and p in {0,1,3}. There are 630 trees and 551,700 literal prefixes.
  Each tree checks the sharp cutoff; 336 also meet the low-degree corollary.
- 16,448 signed-argument binomial parity cases and 4,128 exact
  finite-difference windows. Eight separately lowered forced-prefix
  precision profiles must be rejected.

For n=8, R=3, a=2 and p=3, the exact gather mass is 21,540, while the
new forced-level lower bound is 15,360. The theorem claims sharpness of
the cutoff, not equality in that total mass bound.

Each direct run prints `PASS_NEWTON_RESIDUAL_PREFIX_FLOOR` and a generated
receipt binding the six package files by SHA256. The written proof supplies
the universal argument; finite enumeration is corroboration. No receipt
is handwritten or committed. No generated files are written by the verifier.

## Reproduce

From the repository root, with CPython 3.12 and no third-party packages:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -X dev -I -B research/newton-residual-prefix-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -X dev -I -O -B research/newton-residual-prefix-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/newton-residual-prefix-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/newton-residual-prefix-floor --check-source-history
```

The last command checks a committed package. The two registered commands
repeat the complete domain in normal and optimized modes with warnings
as errors and development diagnostics. They each have a 120-second timeout.
The interpreter path is the local reproduction path; another clean CPython
3.12 installation can replace it. Git-free direct replay needs only these
six files. Historical catalogue and selected-record pins require full Git
history for metadata validation, not for the mathematical verifier.

## Limits

The contract fixes the residual definition, its normalization, literal
Walsh-prefix graph and max-descendant creation demands. It permits exact
coefficient-valuation pruning. A changed graph, representation, integral
dependency treatment or demand contract is outside the theorem. The
near-full-degree heterogeneous bulk remains unresolved. No physical caller,
native implementation, storage/restoration protocol, complete bit-time tariff,
new kappa or complete multiplication theorem is supplied. The selected
frontier and its five assumptions are unchanged. Independent human and
formal proof-kernel review are unclaimed.

The original `p104-side-correction` card is explicitly changed to this
component obstruction in [TASK.json](TASK.json). [SOURCES.json](SOURCES.json)
pins the original card and selected record as provenance and gives exact
cited predecessor heads. External citations are context, not replay inputs.
No unmerged source object is required by the scientific verifier.

## Open next questions

1. Can a changed residual graph exploit integral Walsh dependencies to beat
   max-descendant creation demands? This is a possible escape from the
   obstruction. Start with an explicit arbitrary-input graph and exact
   quotient/precision map. A replacement graph and complete invoice are missing.
2. Does a heterogeneous high-degree Newton bulk retain an obstruction when
   n-R is sublinear? The residual bound then loses its n-scale factor.
   Start with backward precision demands on a named falling-factor graph,
   including coefficient valuations. No such bulk lower bound is proved here.

These questions and their blockers are recorded in TASK.json. No follow-up
is reserved by this contribution.

## Implementation constraints

The verifier uses explicit runtime checks, so optimization disables none
of its mathematical obligations. All loops have fixed census bounds;
there is no recursion, dynamic import, evaluation or concurrent work.
Every function has fewer than 60 physical lines. The largest tree has
2,048 integer entries. Only one tree and its eight sequential rejection
mutants are processed at a time. Gaussian valuations reject coefficient
norms exceeding a 1,024-bit resource bound. No physical address or machine
allocation guarantee is claimed for Python objects.

Rule 3 deviation, verify.py: CPython necessarily allocates integer and
container objects during exact arithmetic. Fixed census sizes, a bounded
tree and coefficient height bound constrain the live mathematical data;
normal and optimized checks exercise the whole domain. Runtime-internal
allocation is not measured. A future native implementation would need its
own capacity and allocation accounting. Rules about C preprocessing and
raw pointer dereferencing have no direct Python mechanism here; the code
uses ordinary direct calls and shallow immutable integer-pair values.
Warning-strict development-mode execution is the available diagnostic gate.

## Credit

This contribution was produced by Nick Petalas. Credit Ali Romman #5825
for the explicit residual graph, precision contract and degree-zero theorem;
David Ganz / Dugongue #5815 for the valuation-pruned residual construction
and #5813 for its Gaussian spectral predecessor; and their retained native,
precision, ownership and compiler contributors. The new contribution is
the positive-degree prefix cutoff, sharpness proof and residual-only
low-degree obstruction. New work is Apache-2.0.
