# Exact implications in the fixed P112 demand system

This is a finite, source-bound inequality result, quantified over all nonnegative
real multiplicity vectors. No predecessor executable or clique census is replayed.
The source matrix is the literal 280-row kernel in Nick Petalas's PR6425 at
`092dcbd13d1263e691ad29f34fbf286fea1fac2c`, authenticated by `SOURCE-PINS.json`.
Its 14 ordered cap rectangles, source clique witnesses and earlier completeness
claims retain their original meaning and attribution.

## Matrix and domain

For each saved pair `(H_i,d_i)`, let `a_i` be the 14-dimensional 0/1 indicator of
hit mask `H_i`. The row is `a_i x >= d_i`, with the common baseline `x >= 0`.
The source rows have distinct nonempty 14-bit masks and positive integer demands
at most 8. These conditions are checked, not inferred from a row count.

PR6425's [proof](https://github.com/petalas/integer-mult-bounds/blob/092dcbd13d1263e691ad29f34fbf286fea1fac2c/research/p112-demand-kernel/PROOF.md)
defines the hit predicate and proves equivalence of this kernel to its full
262,928-clique demand screen. That earlier theorem is a credited premise when
composing the present result with the full geometry. The present standalone
certificate establishes equivalence of the literal 280-row matrix and its new
retained subfamily; it does not independently certify the source clique census,
the witnesses' geometric validity, decoder coefficients or physical admission.

## Checkable deletion implication

For each omitted row `t`, the certificate supplies nonnegative rational weights
`lambda_j`, with every donor `j` in the **final retained family** `R`. The exact
checks are

    sum_j lambda_j a_j <= a_t       (coordinatewise),
    sum_j lambda_j d_j >= d_t.

For any nonnegative `x` satisfying the retained rows,

    a_t x >= (sum_j lambda_j a_j) x
          >= sum_j lambda_j d_j >= d_t.

Thus the retained system implies every omitted row. Conversely a solution of
all original rows satisfies their retained subfamily. This proves equivalence
for all nonnegative real vectors, including unbounded integer vectors. No LP
solver status or floating tolerance enters this acceptance argument.

## Generation and simultaneous deletion

A positive donor weight cannot use a row having a 1 outside `H_t`, because the
target coefficient there is zero and all donor coefficients/weights are
nonnegative. Restrict candidate donors to strict subsets of `H_t`. Process
targets by increasing support size, retaining a row whenever it is not certified
implied by the already retained strict subsets. Retained rows are never deleted
later. Consequently every deletion refers directly to rows in final `R`;
simultaneous deletion is justified without circular premises.

The bounded generator uses exact rational packing simplex: maximize
`sum_j d_j lambda_j`, subject to coefficient capacities at most 1 on `H_t` and
`lambda >= 0`. Zero weights plus slacks form an initial feasible basis. Bland
entering/leaving rules include nonbasic slack columns. A feasible packing reaching
`d_t` already certifies deletion; full optimality is unnecessary for that case.
Explicit bounds reject exhausted work instead of truncating coverage.

The generator is a discovery mechanism. The elementary coefficient checks above
and the explicit points below independently establish the result even if the
simplex implementation is not trusted.

## Separating points and the restricted minimum claim

For every retained row `t`, the certificate supplies a full 14-dimensional
rational vector `x^(t) >= 0` which satisfies **all 279 other original rows** and
strictly violates row `t`. This is checked literally against the original matrix,
not just against `R`, a restricted LP, or an objective value.

A packing dual optimum below `d_t` can suggest the coordinates on `H_t`.
Setting each coordinate outside `H_t` to 8 covers any source row touching an
outside bit, since every demand is at most 8. Original rows wholly inside `H_t`
are covered by retained rows and their certified implications. This explains a
construction of the points; their literal checks are the acceptance evidence.

Given the full-original checks, any subfamily `S` of the original 280 rows
equivalent to the full system must contain every `t` in `R`: otherwise `x^(t)`
would satisfy `S` but fail the full system. Since `R` is itself equivalent, it is
the unique minimum-cardinality and unique inclusion-minimal **subfamily of these
original rows**, with the baseline `x >= 0` fixed. This claim is conditional on
every retained point passing the stated full-original checks.

No minimum over arbitrary new inequalities or alternative representations is
claimed. Fractional separating points do not establish integer-only
indispensability. Changing caps, adding rectangles or trimming actual supports
changes the matrix and requires new certificates.

## Credit and limits

Credit Nick Petalas/PR6425 for the fixed matrix, pairwise kernel and explicit
combined-implication handoff; Jeremy Diviney/PR1422 for the complete-clique guard,
source geometry, caps and smaller-family question; Cinna Davis/PR1347/1323 and
the retained E8/label/decoder lineage. Exact LP certificate semantics also have
repository precedent in PR5767; no shared solver or 128-variable cap is changed.
Nonnegative implication, packing/covering duality, simplex and Bland's rule are
classical. No general mathematical priority is asserted for them.

New work uses substantial OpenAI Codex assistance. A separately implemented
certificate checker is independent code verification of a frozen certificate,
not blind rediscovery or independent human/formal proof-kernel acceptance.
No coefficient synthesis, complete COPY floor, native/physical supplier,
restoration/access/precision/stock/compiler closure, signed invoice, outer
integration, κ improvement or selected-frontier change follows.
