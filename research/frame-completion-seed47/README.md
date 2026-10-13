# Minimum-rank frame sandwiches in the historical parity decoder

**Structural geometry research note; no new kappa or legal supplier.**
This package gives an exact, constructive test for a nondegenerate subspace
between a source span and the orthogonal complement of a target span. Applied
to all 2,271 active nodes of the pinned `ParitySide(10)` DAG, it separates
**692 completable degenerate source spans** from **two impossible sandwiches**.
Every completable degenerate span needs exactly one additional dimension.

This refines the diagnosis in [parity-side.md](../../docs/research/parity-side.md):
source-span degeneracy alone is not an impossibility certificate. It does not
revive the rejected circuit. Its two common-span obstructions remain, and
pointwise completions do not establish compatible transfers between nodes.

## Reproduce

From the repository root with Python 3.11 or later, standard library only:

```sh
python3 -B research/frame-completion-seed47/check.py
```

The checker reads the committed certificate, checks the pinned generator
sources, regenerates the fixed DAG, and independently verifies all recorded
spans, minimal ranks and explicit witnesses. It also exhausts the tiny-space
domain below and runs negative controls. A mismatch exits nonzero, including
under optimized Python. See [VALIDATION.md](VALIDATION.md) for the exact tested
environment and completed checks. Regenerate the certificate without changing
the checked copy:

```sh
python3 -B research/frame-completion-seed47/discover.py > /tmp/frame-completion.json
python3 -B research/frame-completion-seed47/check.py --certificate /tmp/frame-completion.json
```

`discover.py` uses Gaussian elimination and dual radical partners. `check.py`
uses explicit XOR-closed vector sets and tests nondegeneracy directly. The
implementations share the pinned scalar DAG generator, but no frame-algebra
implementation. This is algorithmic cross-checking with AI assistance, not
independent human peer review or a formal proof of integer multiplication.

## Exact local criterion and proof

Let `V = F2^h` have its standard nondegenerate dot product. For subspaces
`A` and `B`, first require `A perpendicular B`. Write `R = A intersect A-perp`,
`a = dim A`, and `r = dim R`. Then

> A nondegenerate `U` satisfying `A subset U subset B-perp` exists exactly when
> `A intersect B = {0}`. Its minimum dimension is `a + r`.

The zero space is nondegenerate. The statement includes empty spans and every
ambient dimension; disjointness without the orthogonality premise is not enough.

**Necessity.** Any vector in `A intersect B` belongs to both `U` and `U-perp`.
Nondegeneracy forces that vector to be zero.

**Construction.** The map from `B-perp` to `R*` given by pairing is onto:
the kernel of its dual is `R intersect (B-perp)-perp = R intersect B = {0}`.
Choose a basis `r_i` of `R` and vectors `z_j` in `B-perp` with
`r_i dot z_j = delta_ij`. Set `U = A + span(z_j)`. Pairing with the `r_i`
shows the `z_j` are independent modulo `A`, so `dim U = a+r`.
If `x = a_0 + sum(c_j z_j)` is orthogonal to `U`, pairing with `R` forces
all `c_j=0`. Pairing `a_0` with `A` then gives `a_0 in R`; pairing it with
the `z_j` gives `a_0=0`. Hence `U` is nondegenerate and attains the bound.

**Minimality.** For any nondegenerate `U` containing `A`, the pairing map
`U -> R*` is onto and annihilates `A`. It induces a surjection `U/A -> R*`,
so `dim U - a >= r`. The constrained construction attains this familiar
radical rank floor; no extra ambient-dimension assumption is missing.

This is a standard bilinear-form extension argument, supplied here as a
reviewable proof and executable local oracle. Mathematical priority is not
claimed. The existing [format limits note](../format-limits-corrected/README.md)
already gives the sandwich restriction in C.1 and the unconstrained radical
rank floor in C.4. The addition here is the constrained construction together
with its complete fixed-DAG certificate.

## Complete finite domain and result

Seed **47**, drawn from OS randomness, chooses `h=8+2*(47 mod 2)=10` from
the historical small domains 8 and 10. The domain is every active node of
the deterministic pinned `ParitySide(10)`, including its 120 source nodes.
`A` spans all ancestor source labels; `B` spans all descendant target labels.
The producer reads source supports and traverses from each output. The
checker independently propagates sources forward and targets backward.
Every node is checked for `A perpendicular B`; no sample is extrapolated.
The stopping rule is exhaustion of this fixed node set and all orthogonal
subspace pairs of `F2^h` for `h=0,1,2,3,4`.

| Quantity | Exact result |
|---|---:|
| Active nodes / binary nodes / output copies | 2,271 / 2,151 / 120 |
| Nondegenerate source spans (already minimum completions) | 1,577 |
| Degenerate source spans | 694 |
| Completable degenerate spans | 692 |
| Impossible sandwiches | 2 |
| Pointwise feasible nodes, including sources | 2,269 |
| Sum of additional dimensions over feasible nodes | 692 |

All 692 feasible degenerate spans have radical dimension one. The full
`(dim A, dim rad A, minimum dim U)` histogram and a basis for every witness
are in [CERTIFICATE.json](CERTIFICATE.json). These counts are node counts;
they are not helper counts, operations or a recursive cost invoice.

The impossible nodes are 124 and 1691, with respective explicit common
vectors 480 and 15 (bit-mask coordinates). For example, node 124 has
`A=span(800,832,384)` and `B=span(608,896)`; both contain 480. No larger
nondegenerate frame satisfying this sandwich can fix that node.

As a positive witness, node 135 has `A=span(672,704,768)`, `B=span(224)` and
minimum dimension four. The producer supplies `U=span(160,192,256,512)`.
Its source span has dimension three and radical dimension one.

## What the cost and residual checks permit

Optimistically setting every scalar gate, source access, copy, helper,
restoration and recursive child cost to zero still cannot make the two
impossible sandwiches legal. Thus completing frames alone cannot realize the
unchanged historical DAG under this interface. The experiment stops here;
no large supplier implementation or new assembly calculation is justified.
For the other nodes, `a+r` is a geometric minimum only. The sum 692 is not a
paid operation saving or a complete cost lower bound for a different circuit.

Every active node has odd source and target labels. Consequently a separating
`U` and its complement are both nonalternating. **Their incident residuals
need not be nonalternating, and independently chosen frames need not nest.**
[PR #920](https://github.com/CrocSwap/integer-mult-bounds/pull/920) supplies the
essential negative control: at `h=6`, sources 7 and 25 and targets 11 and 19
have a minimum dimension-three separator `span(25,26,4)`, but its residual
at source 7 is `{0,3,29,30}`, a nonzero alternating plane. Our checker accepts
the separator and explicitly rejects that residual as an orthonormal transfer.
It does not relabel it as a legal primitive.

The result does not close other DAGs, alternative labels, paid non-nested
transport, copied carriers or phase-aware interfaces. A future supplier must
still establish simultaneous frame choices, all transfer residuals, source
access, helper lifecycle and inverse cleanup, complete recursive pricing,
hosting, precision/tape and analytic obligations. Nothing here removes any
assumption from the selected conditional multiplication result.

## Sources and attribution

Exact base: `007664306fff84fbb1c9a1b4053b69f439764034`. Current main at this
base selects the reviewed T21/PR #890 result,
`kappa=1661957774647029/10^18`, whose source head is
`4b3bd8cbe8e3e81c44161017c9b72c905a8040a8`. The selected manifest, actual
T21/U8 proof and maintainer review were followed; no frontier file is changed.
[SOURCES.json](SOURCES.json) pins the predecessor documents and concurrent PRs;
the certificate pins every imported repository module used by the generator.

Credit Douglas Colkitt's historical parity-side work for the signed kernel,
source/target obstruction and scoped failed repair; eumemic's PR #114 for
earlier completed-core and nested-frame work; DreamingOfClouds' format limits
for the sandwich and radical floor; and ArnavSwiggy's PR #920 for the local
rectangle census and residual counterexample. PR #920's stronger incident
residual test is not replaced by this weaker local oracle. This package adds
arbitrary-span pointwise minima and all-node h=10 evidence, rather than
claiming frame completion itself as a new mechanism.

Prepared for GitHub contributor **ToikY**, with substantial **OpenAI Codex**
assistance in mathematics, code, independent implementation, review and writing.
New files follow the repository's Apache-2.0 license. No predecessor code is
vendored or modified, and `upstream/` is unchanged.
