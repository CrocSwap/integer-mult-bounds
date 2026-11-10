# Compute sparse Gaussian inverse halos from the original band

**Scoped constructive result, with a written all-size proof and exact finite
corroboration. No new κ.**

This package replaces an unpriced global polynomial-row oracle with an
explicit local numerical consumer. It evaluates the normalized inverse
polynomial from the original rational reference band, shrinking the saved
dependency interval after each step. The full local tensor program includes
sparse axis exposure, absolute-coordinate coefficient pages, actual rounding,
immutable fixed-source lines, physical head returns and cleanup.

The contribution is the source-bound sequential interface and complete bill.
The Neumann/Horner identities, the direct row-gap locality degree, and generic
rounded core/halo composition were already available. The comparison below
is part of the novelty boundary, not a claim of general literature priority.

## Technical result

For real cyclic band matrices `H_i=I-E_i` with row gap `delta_i>0`, bandwidth
`W_i`, and a shared q grid, choose dyadic `a_i` with `a_i delta_i>=1`. The
program uses `J_i` fixed-source updates and a saved halo of
`b_i=(J_i-1)W_i`. It returns the target rectangle with error at most

    sum_i [(2W_i+1)R+2] * 2^-q/delta_i
      + R sum_i (1-delta_i)^J_i/(a_i delta_i).

Every actual intermediate remains on the same grid and within the original
component-l1 radius `R`. Each source line is preserved through its complete
update sequence. The program never forms the dense polynomial coefficient
rows, and it never assumes translation invariance of the reference entries.

The numerical tensor uses eight reusable local tape roles and one protected
concatenated reference archive. Each local page takes at most two **complete
archive scans per rectangle/axis**, and is reused across all spectator lines.
Sorting touches only the sparse saved rectangle. A live-body/blank-suffix
invariant prevents repeated erasure of old large buffers from introducing an
unfunded `L/A` factor on a later short face.

For copied volume `C`, key width `K`, arithmetic/control width `w`, and
archive coefficient count `G`, the complete generic bit bill is

    T_reference + O(w^2 [h_axes G + C sum_i(J_i(2W_i+1)+K+1)]).

The full archive term is explicit. In the exact balanced growing-group regime
of the pinned #4100 route, a rectangle's many long sides absorb the repeated
archive scans. The original source producer has separately charged
`d*2^O(ell)*poly(p)=2^o(p)` setup. The resulting numerical consumer costs
`O(V d g A p^6/L)`, inside the route's older conservative halo allowance.
This substitution does not admit that archived outer proof or change the
selected conditional frontier.

The complete definitions, no-alias domain, fixed-role implementation,
coefficient producer, scalar arithmetic and production substitution are in
[PROOF.md](PROOF.md). Exact base and source hashes are in
[SOURCES.json](SOURCES.json).

## What was already proved

| Source | Existing result | Present distinction |
|---|---|---|
| #1430 and #6490 | Stable fixed-source Horner evaluation and its oracle precision allocation | Original reference entries, local shrinking domains and sequential producer/consumer cost |
| #5159 and #5216 | Complete rounded whole-period service on one rational Gaussian Reference | Sparse local tensor, variable certified gaps, fixed tape roles and production-group substitution |
| #5260 and #5284 | Host-array direct solves and variable-gap cyclic-band precision | Different iterative mechanism; includes the sparse physical page/layout interface |
| #3851 | Physical normalized principal-window compression core | Complements that core; does not reprove its Schur/q-convolution mechanism or use its different gap as this caller's gap |
| #6880 | Direct row-gap polynomial, `J=16p^4`, inward-rounded polynomial rows and nonlinear core/halo composition | Eliminates the polynomial-row oracle using the original band and prices its production/access |
| #4870 | First-face source-copy enumeration | Receives one completed saved rectangle; dense-source copy generation and final unique return remain outside this consumer |

#5325's tensor error join, #4415's outer suffix accounting, and #4205/#4253's
finite-core circuit theorem are not claimed as new work. A future integration
must check their source/reference versions and actual grids before composing
them with this consumer.

## Exact evidence and reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -I -B research/shrinking-reference-halo/verify.py
```

Expected marker: `PASS_SHRINKING_REFERENCE_HALO`, with 32 finite lines,
40 Gaussian rows, 1,600 original source entries, 17 rejection controls,
and `no_new_kappa: true`.

The registered replay runs the author verifier and two separately developed
mathematical checks, each in normal and optimized Python:

```sh
python3 -B scripts/research_package.py --package research/shrinking-reference-halo
```

[RESULT.json](RESULT.json) is generated by the verifier and required by normal
read-only replay. It records:

- Thirty-two signed, nonstationary cyclic-band lines and ninety-six returned
  target coordinates, with exact dense-polynomial and full rounded-period
  comparators.
- Complete two- and three-axis synthetic tensor executions, followed by a
  long/short/long rectangle history with all tape constructors disabled.
- The actual retained `Reference(32,8,2,1,8,32)`, including every one of its
  1,600 entries, all eight identity holes, and genuine across-period entries.
- Three actual-reference lines and a two-axis, 756-record saved rectangle
  returning twelve target records, with the complete product, rounding,
  archive-scan, radix, head-action and retained-space counts.
- Seventeen explicit rejection/code-mutation controls. Separate executed
  comparisons detect dropping the actual periodic branch and the unfavorable
  high-water-clearing tariff, even though the latter leaves numerical answers
  unchanged.

The matrix-power oracle forms successive exact powers and their sum; it does
not import the numerical recurrence's implementation. The global rounded
comparator additionally checks bit-for-bit locality.

The separately developed [independent_inverse.py](independent_inverse.py)
solves four rows of the **original rational inverse** by exact elimination,
checks their exact matrix residuals, and uses those rows to evaluate the
two-axis inverse independently of the polynomial recurrence. The physical
consumer's four outputs have maximum error below `5.252e-9`, within the
proved `8.213e-8` allowance. A second nested target returns identical bits,
reuses the same eight roles with tape creation disabled, and preserves the
archive. A wrong-target control produces error greater than `0.109`.

[independent_residual.py](independent_residual.py) runs all forty physical
singleton outputs and bounds their inverse error directly from the original
matrix residual and its exact row gap. The certified error is below
`7.667e-9`, while a cyclically misreturned output has error greater than
`0.543`. Neither check imports the author verifier or its expected output.
Their expected markers are `PASS_LEAD_EXACT_TENSOR_INVERSE` and
`PASS_LEAD_ORIGINAL_REFERENCE_RESIDUAL`.

These checks were developed by a separate AI reviewer within this contribution,
using different mathematical mechanisms. All acceptance comparisons use
exact rational arithmetic; displayed decimal summaries are diagnostic. The
all-size claims rest on the written proof. No external human or formal-kernel
acceptance is asserted.

## Scope and limitations

The source-bound forty-row example is a legal finite Reference fixture, not
an execution of the asymptotic outer production parameters. Its all-input
same-reference numerical error is funded below `2^-20` per axis, while the
source's ideal-Gaussian perturbation and global gap proof remain inherited.
The generic theorem explicitly requires zero outside the stated cyclic band;
checking stored row mass alone does not prove support.

Binary tape movement is executed. Scalar integer macros are exact in the
reference and are priced by a written ordinary schoolbook arithmetic
implementation. Source cache serialization and its conservative polynomial
setup bound are proved, not claimed as a measured fast Python producer.
Retained blank backing is included in space; Python allocator zeroization
and byte-exact host heap accounting are not claimed.

The saved rectangle must come from original values before any core mutation.
This package consumes that saved copy and returns its target; it does not
implement the full dense-source first-face gather or final dense unique-key
merge. It supplies no new native supplier, core admission, complete broad
Gaussian map, all-depth compiler, CRT join or exact integer multiplier. All
five selected framework assumptions remain. **No new κ.**

## Provenance and credit

Scientific base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The selected conditional frontier at that base is
`781451/250000000 = 0.003125804`; it is unchanged.

The compatible, concurrently published #6880 proof was read at
`e212af981b49c299de515f8c23dfb0e5b73e2e95`. This package is self-contained for
its local theorem and has no executable dependency on that unmerged commit.
The exact retained Gaussian implementation and source proof are pinned at
the canonical base in SOURCES.json; no predecessor file is changed.

Prepared for **@CubeJerry**, with substantial OpenAI Codex assistance in
mathematics, source analysis, implementation, verification and prose. Credit
Cinna Davis (#4100), Jose Manuel / jmbarrancoml (#3851, #4205/#4253),
JoyboyBrian (#5159/#5216), Hanson Sun / bbMisk (#1430), Ali Romman
(#5260/#5284), @codyw912 (#4870), Nick Petalas (#4217/#5986), and the inherited work of
Vlado Vojdanovski, Jeremy Kothe, Mason Hale and Chafik Boukhalfa. Classical
Neumann iteration, Horner evaluation, diagonal dominance, stable radix
distribution and ordinary binary arithmetic retain their original credit.
The source's Harvey–van der Hoeven, OpenAI manuscript and Douglas Colkitt
lineage and Apache-2.0 notices are retained in the declared sources.

## Open next questions

The former first-face transaction join question is resolved within the
explicit source/plan hypotheses by [the integrated reference
transaction](../first-face-reference-join/README.md). Its source-bound
streamed codec preserves the common grid and original values, canonicalizes
only target returns, and proves the complete group bill. Actual-reference
wrap/hole execution and independent unequal-halo full-grid checks are
retained there. This does not admit the accelerated core or outer caller.

1. **Use the same rounded reference at the actual finite core and outer
   recovery.** The local result does not permit substituting a similarly named
   Gaussian matrix. First pin the core's exact reference/normalizers and its
   all-input error, then insert (5) in its existing recovery ledger. Source
   compatibility and complete outer admission remain open.

The quantified questions, overlap coverage and stopping rule are also retained
in [TASK.json](TASK.json). No further optimization is reserved by this package.
