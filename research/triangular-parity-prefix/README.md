# One parity-split prefix is at most 3/2

**Claim type:** an infinity-norm bound for one triangular circuit prefix.
**No new κ.** The selected record is `60403/20000000`. The full shifted-interior
stage, the row gap, and the dyadic `p^100` normalizer stay hypotheses.

## Question

`research/one-factor-of-t` counts one factor of `T` on the coefficient-error
path and leaves the Gaussian stages conditional on an infinity-norm
contraction. Its first step is to bound one shifted-interior circuit's
prefix factors in the infinity norm.

`GAUSSIAN.md` cites the triangular compiler in `SHALLOW-TOEPLITZ.md`. That
compiler's parity split is one prefix of the circuit. The question for this
package is the infinity norm of that one split, before and after a
one-coefficient rounding.

## Lemma

Let `n = 2m ≥ 2` and let `T` be lower triangular Toeplitz with constant term
`1` and off-diagonal coefficient `l1` norm at most `η ≤ 1/2`. Write the
symbol as `e(z^2) + z o(z^2)`, and let `a` and `b` be the coefficient `l1`
norms of `e − 1` and of `o`. Then `a + b ≤ η`. In exact arithmetic, every
factor of this one parity split has infinity norm at most `1 + η ≤ 3/2`:

- the even child `E` satisfies `‖E − I‖_∞ ≤ a ≤ η`;
- the quotient `k = o/e` satisfies `‖k‖_1 ≤ b/(1 − a) ≤ η`, so each shear
  block has infinity norm at most `1 + η`;
- the Schur child `s = e − z o^2/e` satisfies `‖S − I‖_∞ ≤ η`.

The pure odd symbol `(1, 1/2, 0, 0)` meets `3/2` on the completed map and
on the right-shear prefix. Replacing `1/2` by `1` makes that tail `l1`
equal to `1` and raises the same prefix from `3/2` to `2`.

## Proof

The coefficient `l1` norm is submultiplicative, and discarding positive
powers does not increase it. Since the constant term of `e` is `1` and
`‖e − 1‖_1 = a < 1`, the Neumann series gives `‖e^{−1}‖_1 ≤ 1/(1 − a)`.
The even coefficients are a subset of the original tail, so `a ≤ η` and
`‖E‖_∞ ≤ 1 + η`.

The quotient bound is `‖k‖_1 ≤ b/(1 − a)`. With `b ≤ η − a` and `η ≤ 1`,

```text
b/(1 − a) ≤ (η − a)/(1 − a) ≤ η,
```

because `(η − a)/(1 − a) = 1 − (1 − η)/(1 − a) ≤ η`. Each shear is a block
matrix `[I, U; 0, I]` or `[I, 0; U, I]` with `‖U‖_∞ ≤ η`, so its infinity
norm is at most `1 + η`.

For the Schur child, `‖z o^2 e^{−1}‖_1 ≤ b^2/(1 − a)`. Then

```text
b^2/(1 − a) ≤ b,
```

because `b ≤ η − a ≤ 1 − a`. Hence `‖S − I‖_∞ ≤ a + b ≤ η`.

At `η = 1/2` these caps are `3/2`. The symbol `(1, 1/2, 0, 0)` has
`a = 0` and `b = 1/2`, and both the matrix and the right shear have
infinity norm `3/2`. The factorization

```text
[ E, ZO ; O, E ] = [ I, 0 ; T(k), I ] diag(E, S) [ I, T(zk) ; 0, I ]
```

holds on the even/odd reordering. Moving the single odd coefficient from
`1/2` to `1` preserves the shape of that shear and changes its infinity
norm from `3/2` to `2`. The tail hypothesis `η ≤ 1/2` has then failed, so
the cap does not survive an arbitrary one-coefficient rounding.

`SHALLOW-TOEPLITZ.md` states the looser descendant cap `η/(1 − η)`. At
`η = 1/2` that number is `1`, while the parity-split factors above are
already at most `1/2` away from `I` in the cases the shared budget controls.

## Not covered

- A second nested split, or the `O(log^2 N)` depth of the triangular compiler.
- The generator-shear compiler and the full Toeplitz recursion.
- Whether `p^100` absorbs the resulting prefix.
- The row gap after truncation, alias removal and rounding.
- Internal rounding smaller than the one-coefficient step above, except
  through the same tail budget: a perturbation of total `l1` at most `ε`
  replaces `η` by `η + ε` and keeps the cap `3/2` when `η + ε ≤ 1/2`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/triangular-parity-prefix --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-prefix
```

Base `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
Upstream fetches at 2026-10-22T16:21:18Z, 2026-10-22T16:31:19Z, and
2026-10-22T16:33:00Z were that commit. The pinned input blobs were unchanged.
The selection is κ = `60403/20000000`.

Overlap snapshot: open PRs fetched 2026-10-22T16:30:04Z (464 records) and
discussions fetched 2026-10-22T16:31:05Z (3622 records). Terms
`triangular-parity-prefix`, `right-shear prefix`, and `parity-split prefix`
reported 2 matches, this README and this TASK. A second search of the same
cache, offline, for `shifted-interior circuit` returned this README,
`research/one-factor-of-t`, and that package's TASK. That note leaves the
prefix bound open. No matches is not a novelty certificate.

## Open next questions

1. **Do nested parity splits keep every proper prefix inside the product of
   the one-level caps?** One split is at most `3/2`. The first step is one
   `n = 8` symbol with tail `l1` at most `1/2`: record the largest
   proper-prefix infinity norm. Do not treat `p^100` as already spent.

## Credit

- The one-factor ledger, and this question, are `research/one-factor-of-t`'s.
- The `2^{-4p}` exponent table is #4371's.
- The triangular parity split is #4100's `SHALLOW-TOEPLITZ.md`.
- The shifted-interior citation of that compiler is #4100's `GAUSSIAN.md`.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
