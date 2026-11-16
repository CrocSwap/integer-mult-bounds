# Odd-denominator shear length of the helper-462 landing permutation

**Scoped proof. No new κ.** The selected record stays `781451/250000000`.

Every swap-free word for the landing permutation below, with shear
coefficients in the rationals of odd denominator and scale coefficients in
the odd-denominator units, has **at least 18 shears**. Eighteen is achieved.
The unreduced concatenation of the seven-shear cleanup with any such landing
factor has at least 25 shear letters. This package does **not** claim that 25
is the minimum shear count of a two-scale zero-swap word.

## Scope

Original card: `supplier-boundary-audit`, priority revision 8, base
`17469fff78c22941280f04d39dc5a1faee09c840`. Scope status: **refined**.

Discussion #1166 comment
[19507690](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19507690)
asks whether the pinned helper-462 matcher has a zero-swap word with at least
two scales and fewer than 25 shears. Its first step is to factor the landing
permutation in fewer than 18 shears and prepend the inverse of the seven-shear
cleanup. This package answers that factorization for odd-denominator
coefficients. The 25-shear word itself remains the witness of open PR #7012
and is not recorded again here.

The one-scale 53-shear word is merged PR #6954. The seven-scale 27-shear
swap-free route is merged PR #6947. The one-scale 29-shear schedule is a
different lane. None of those is the question answered here.
`current-priorities.md` on this base still quotes an older selected value
from PR #5599. The verifier reads `certificates/selected-result.json`.

## Result

The proof is [PROOF.md](PROOF.md). The finite checks are in `verify.py`.

The cleanup of the 25-shear route is seven shears of coefficient `±1` and
five scales. It sends the pinned matcher `S` to the permutation matrix `P`
with

```text
σ = (4, 3, 5, 6, 7, 0, 1, 2) = (0 4 7 2 5)(1 3 6).
```

Four of those scales are halves, so the cleanup is outside the coefficient
class below. `det(P) = 1`.

Over `F2`, every CNOT circuit for `P` has at least 18 gates: at least six
links, six middles and six cuts, and those classes are disjoint. The explicit
reverse of the six content exchanges is an 18-gate circuit, and along it the
classes split `6/6/6`. The same positions over `Z`, with a scale by `-1` on
each exchange, are 18 shears and six scales by `-1`, and they multiply to `P`.

A shear or scale whose lowest-terms denominator is odd reduces modulo 2 to a
CNOT or to the identity. Even shears and allowed scales disappear. A word in
that class therefore needs at least as many shears as the CNOT length. The
odd-denominator shear length of `P` is exactly 18.

Concatenating the seven cleanup shears with an 18-shear landing factor,
without cancelling a letter at the junction, gives 25 shear letters. There is
no odd-denominator landing factor with fewer than 18 shears.

## Open next questions

These are the structured questions in [TASK.json](TASK.json).

1. **Dyadic shear coefficients.** A coefficient with `2` in its denominator
   does not reduce to a CNOT or to the identity. The smallest useful follow-up
   is one explicit word for `P` of shear length less than 18 that uses such a
   coefficient, or a 2-adic obstruction. An incomplete search is not a proof
   that 18 remains minimal. Nothing in this package blocks that attempt; the
   obstruction is simply not proved here.

2. **Cancellation at the junction.** The cleanup uses scales by `1/2`, so the
   odd-denominator theorem does not apply to the concatenated word. The
   smallest useful follow-up is one commutation or Steinberg rewrite that
   deletes a shear from the 25-letter concatenation and still multiplies to
   `S`, or a proof that no shear cancels.

3. **Another route.** A zero-swap word for `S` with at least two scales need
   not pass through this matrix `P`. The smallest useful follow-up is a
   checked word with fewer than 25 shears, or an invariant that forces every
   such word through a factor of CNOT length 18 after a seven-shear prefix.
   No such invariant is proved here.

## Reproduce

From the repository root:

```sh
python3 scripts/research_package.py --package research/helper462-landing-shear-floor --check-only
python3.12 scripts/research_package.py --package research/helper462-landing-shear-floor
```

The verifier is Python 3.12 with the standard library only. It checks the
pinned matcher and `det(S) = -16`, the cleanup, the explicit 18-shear word,
deletion of each CNOT, replacement of an odd shear by its double, the 16-row
river-parity table, the `6/6/6` split, and the same one-step predicates on
every CNOT in `GL(3, F2)`. The `GL(3, F2)` census is a control on those
predicates. The proof for `n = 8` is the written argument, not the census.

Selected-frontier replay, Lean and Docker were not run.

## Credit

The matcher and its published elimination come from the helper-462 record in
`research/bit-completed-backend-api`. The landing matrix, the seven-shear
cleanup and the six content exchanges come from the open 25-shear route, PR
#7012. The link/middle/cut split is the standard shape of a CNOT-length
argument for a permutation; the counting used here is written out in
`PROOF.md` and is not imported as a black box.

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0.
