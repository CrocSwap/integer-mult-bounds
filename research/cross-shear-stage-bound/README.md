# A uniform stage-count proof for the archived borrowing model

**Research consolidation; no new kappa.** In the model below, swapping two
blocks of dimension `P*v` needs at least `2P + 1` cross-block calls when each
call has rank at most `v`. The existing borrowing chain attains this count.
This note supplies a short proof for every positive `P` and `v`, over every
field. It does not claim a new controller or a lower bound for multiplication.

## The evidence discrepancy being resolved

The archived campaign's [report M, section 1](evidence/M-RESULT.md) concludes
that fewer than `2P + 1` stages are impossible in its model. Its supporting
discussion gives a small-pattern rank argument for at most four calls and
reports finite searches for `P <= 3`. Its general count of at least `P` upper
and `P` lower calls gives only `2P`; the extra call needs a separate argument.
The proof below provides that argument. **The stage-count conclusion survives
this audit.** No counterexample to it, failed search, or new saving is reported.

The original report and its notice are retained byte for byte. Their other
claims, historical timings, recommendations, and local paths are not audited
or adopted here. The campaign index already labels this material as historical
and distinguishes analysis from completed experiments. We preserve that scope.

Assignment seed **97** selected research consolidation. Campaign idea 97 links
to report M, which led to this specific obligation. [CLAIM.json](CLAIM.json)
records the alternatives, overlap checks, and local claim. No pinned sprint
issue existed. Base commit:
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.

## Exact model

Let `F` be any field, let `d = P*v`, and write the data as `(X,Y)` with
`X,Y in F^d`. A **shear** adds a linear function of one block to the other.
The counted calls are

```text
L(E) = [ I  0 ]       U(H) = [ I  H ]
       [ E  I ]              [ 0  I ],
```

where `rank(E) <= v` or `rank(H) <= v`. Rank means the number of independent
columns. A **bridge** is any `diag(S,T)` with `S,T` invertible `d` by `d`
matrices. Arbitrarily many bridges may occur anywhere, including at both ends.
Bridges can mix ports within a block. They are not limited to pairwise adds.

The starting map is the identity. The required endpoint, **before the
designated terminal exchange**, is block antidiagonal:

```text
[ 0  C ]
[ D  0 ],       C and D invertible.
```

The usual controller has `C = -I`, `D = I`; the final signed exchange then
restores the data. The exchange is not an allowed bridge inside this model.
If the only endpoint requirement were identity, doing nothing would suffice.

"Uncounted" bridges are a relaxation for this call-count lower bound. They
still require scalar work and legal frames in an implemented controller.
Auxiliary registers are not extra state in this model. To apply the result to
a supplier, each complete invocation must satisfy its normalized data-shear
contract; its helpers, restoration, frames, and physical costs remain separate
obligations. Calls that change both blocks at once are outside this model.

## Uniform lower bound

Write the matrix of a prefix as

```text
M = [ A  B ]
    [ C  D ]
```

and define `Phi(M) = rank(A) + rank(D)`. Initially `Phi = 2d`. At the required
endpoint `Phi = 0`.

1. Left multiplication by a bridge replaces `A,D` by `S*A,T*D`. Both ranks
   stay unchanged because `S,T` are invertible.
2. A lower call replaces `D` by `D + E*B` and leaves `A` unchanged. The rank
   inequality `rank(R + Q) >= rank(R) - rank(Q)` and
   `rank(E*B) <= rank(E)` show that its decrease in `Phi` is at most `v`.
   An upper call replaces `A` by `A + H*C`, with the same conclusion.
3. Before the **first** counted call, all preceding bridges have left the
   prefix block diagonal, so `B = C = 0`. The first call changes neither `A`
   nor `D`. Its decrease in `Phi` is exactly zero.

Zero counted calls cannot reach a block-antidiagonal invertible endpoint.
With `k >= 1` calls, summing the decreases gives

```text
2d <= (k - 1)*v,       hence k >= 1 + ceil(2d/v) = 2P + 1.
```

Intermediate increases in `Phi` do not affect this inequality. No reduction
modulo a prime, finite search, alternating-pattern assumption, or common port
basis is used. In particular, arbitrary invertible within-block bridges cannot
remove the first call's zero progress.

The proof also gives the useful weighted statement: if the actual ranks of
the calls are `r_1,...,r_k`, then `sum(r_i for i >= 2) >= 2d`. We do not claim
that this bound is always attainable for a prescribed unequal rank list.

## Why the existing count is sharp

This is the existing Sussman borrowing chain, not a new construction. Index
the bank pairs by `j = 0,...,P-1`, each of width `v`. Start with `Y_0 += X_0`.
For each `j` in increasing order:

1. Make the counted call `X_j -= Y_j`.
2. If there is a next pair, bridge with
   `X_j += X_(j+1)` and `Y_(j+1) -= Y_j`.
3. Make the counted call `Y_j += X_j`.
4. If there is a next pair, bridge with
   `X_j -= X_(j+1)` and `Y_(j+1) += Y_j`.

Finally, for `j = P-2,...,0` in decreasing order, bridge with
`X_(j+1) += X_j` and `Y_j -= Y_(j+1)`.

Here is an all-size scalar check. Let the original data be `(x_j,y_j)`, and
put `t_-1 = 0`, `t_j = y_j - t_(j-1)`. On entry to iteration `j`, the active
pair is `(x_j, x_j + t_j)`. Its exit values are
`X_j = -t_j` and `Y_j = x_j + x_(j+1)`, except that the last pair exits with
`Y_(P-1) = x_(P-1)`. The bridges prepare the next entry pair with
`t_(j+1) = y_(j+1) - t_j`. Descending cleanup then gives `X_j = -y_j` and
`Y_j = x_j` for every `j`. These identities hold over the integers and hence
over any field. Tensoring with `I_v` gives rank-`v` counted calls.

There are exactly `2P + 1` counted calls and `6(P - 1)` elementary bridge
adds, followed by the terminal signed exchange. This establishes sharpness
of the call count only. It says nothing about optimal idle transitions,
helper stock, copied information, moment costs, or an optimal kappa.

## Reproduce the finite evidence

From the repository root, with Python 3.9 or newer:

```sh
python3 -I -B research/cross-shear-stage-bound/verify.py
```

Expected final line:

```text
PASS_CROSS_SHEAR_STAGE_BOUND 28 rational witnesses; 20160 F2 prefixes; 362880 cross-call and 725760 bridge transitions
```

The command uses only the standard library, performs no network requests,
writes no files, and compares every result with [RESULT.json](RESULT.json).
All rejection checks remain active under `-O`. `--write-result NEW_PATH`
instead saves freshly computed evidence and refuses to overwrite a file.
Recorded interpreter, clean-tree, and corruption checks are in
[VALIDATION.json](VALIDATION.json). The path-filtered workflow runs normal and
optimized checks on Linux with Python 3.11 and 3.14; its presence alone is not
evidence that hosted CI has passed.

The checks cover:

- Seven pinned input files, including the preserved historical report and
  the controller source. Only its inspected `recipe` function is evaluated;
  no supplier imports or replay jobs run.
- Equality of the independent, grouped-coordinate word with the pinned
  recipe for every `P` from 1 through 16. This exercises the scalar recipe
  beyond the physical driver's supported sizes; it does not certify those
  physical layouts.
- Exact rational replay for `P = 1,...,16` at `v = 1`, and `P = 1,...,6` at
  each of `v = 2,3`. Each witness attains every available potential decrease
  and restores the data after the signed exchange.
- Every invertible four-by-four binary prefix: 20,160 matrices. For each,
  all 18 nonzero rank-one cross-block calls satisfy the rank inequality and
  all 36 invertible block-diagonal bridges preserve the potential. All 648
  first-call cases have zero progress. This uses a separate bit-packed rank
  implementation, not rational elimination or any repository rank engine.
- Omission and sign reversal of every counted call and every elementary
  bridge in the words with `P = 1,...,6`. These controls check the actual
  wrong signed-swap endpoint, rather than merely rejecting a changed operation
  count. Every omitted counted call also leaves a nonzero diagonal block, so
  it fails even the more permissive antidiagonal endpoint condition.
- Hypothesis controls: a rank-two three-call swap defeats an incorrectly
  applied rank-one five-call bound; a cross-block exchange and a singular
  diagonal map can lower the potential if admitted as bridges; identity is
  not the required endpoint. A matrix with different rational and binary
  ranks checks the distinction between the two arithmetic implementations.

This is a complete census of the stated finite domain, not a search for a
new construction. There is no solver or time-based stopping rule. The proof
above, rather than extrapolation from these tests, establishes the uniform
claim. No proof-assistant or independent human verification is claimed.

## Sources, overlap, and scope

[SOURCE-PINS.json](SOURCE-PINS.json) records exact source hashes. The original
report is from Rohan Arun's [PR368 at fa8ab946](https://github.com/rohanarun/integer-mult-bounds/blob/fa8ab946df57ebadae1a470b637c2a590a0a5317/research/campaign-100-results/reports/M-RESULT.md).
The main-branch campaign index is the later PR477 integration. The executable
recipe is the unchanged `global_k.py` preserved by #543 from the
#510/#463/#443/#436/#386 controller lineage. Its original notice retains
the contributor credit.

Jacob Sussman's bridge construction and the #234/#363/#373/#375 lineage
already provide the borrowing mechanism. [PR397](https://github.com/CrocSwap/integer-mult-bounds/pull/397)
at `cb6455fa1e9af68be47c33948d3d1a6f0717a5e4` separately formalizes the
indexed scalar identity. That Lean package is cited, not imported or rebuilt;
we make no priority claim for the identity or its arbitrary-size validity.
The added result here is the explicit rank-potential lower-bound proof and
its reconciliation with the archived stage exclusion.

The checked nearby PRs concern different obligations: #695 records Linux
execution provenance; #704 binds review-ledger metadata; #705 bounds complex
rank-homogeneous paths; #720 treats an abelian three-register bit model.
None is a dependency of this proof. #288 and #446 also remain distinct
model-specific obstruction packages.

The selected conditional result remains
`51110230636731/31250000000000000`. No selected certificate, upstream source,
or construction is changed. All inherited compiler, physical realization,
hosting, restoration, precision/tape, and analytic obligations remain.

Prepared by **Johnny Franks (0xjohnnydev)** with substantial **OpenAI Codex**
assistance in analysis, implementation, and writing. New work is Apache-2.0.
See the preserved [historical notice](evidence/NOTICE.md) and the pinned
controller notice for predecessor attribution and AI disclosures.
