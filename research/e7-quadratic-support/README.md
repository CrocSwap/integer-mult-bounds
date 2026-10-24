# Sharp support twelve for trace-zero E7 quadratics

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Result and claim type

**Scoped mathematical proof with an exact finite certificate.** Every nonzero
rational trace-zero quadratic form on the seven-dimensional orthogonal
complement of an E8 root is nonzero on at least **twelve** of its 63 root
lines. Twelve is attained.

This proves the trace-zero replacement for auxiliary statement (2) in
[JoyboyBrian's released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1502#discussioncomment-19145642).
The unrestricted statement there needs correction: products of two linear
forms can have support eleven, as already follows from the 52-line two-flat
union in DreamingOfClouds's #595 and DaysSky's
[#897](https://github.com/CrocSwap/integer-mult-bounds/pull/897).
DreamingOfClouds's open
[#3045](https://github.com/CrocSwap/integer-mult-bounds/pull/3045)
also records an E7 intersection of supports of size eleven. The eleven-line
example first reported in this contribution's progress post is therefore
credited to that existing coverage, not claimed as an original result.
The new result is the sharp trace-zero bound and its frame-code certificate.

The arbitrary-deletion quadratic extension in handoff statement (1) remains
open. This package does not prove the seven-deletion rigidity shortcut.

## Finite certificate

Use doubled E8 roots, with canonical line representatives
`2e_i +/- 2e_j`, `i < j`, and `(1,s_1,...,s_7)` with an even number of
negative coordinates. All have squared norm eight. Coordinates run from zero
through seven. Fix `a=2e_0+2e_4`, and let `R` be the 63 root lines in `a`-perp.
An orthogonal frame consists of seven mutually orthogonal lines in `R`.

The verifier constructs every frame by an increasing-clique traversal,
retaining a branch only when enough candidates remain to complete it.
It finds 135 frames. Their binary incidence matrix `H`, of shape `135 x 63`,
has rank 36 and kernel dimension 27. The verifier constructs a kernel basis
with an identity submatrix on its free coordinates, checks every basis vector
against every row, and enumerates every one of its **134,217,727 nonzero
vectors**. Their minimum Hamming weight is **12**.

The enumeration uses a Gray traversal. At step `i`, toggling basis vector
`v_((i & -i).bit_length()-1)` changes the coefficient vector to `i xor (i>>1)`.
These coefficient vectors visit every nonzero element of `F2^27` once.
The identity on the free coordinates proves that their images are distinct.
The finite minimum is recomputed on every registered replay; no saved census
or external solver is trusted.

## Proof of the rational lower bound

More generally, every nonzero rational function on `R` whose sum on every
orthogonal frame is zero has support at least twelve. Clear its denominators
and divide its integer values by their greatest common divisor. The resulting
primitive integer vector still has zero frame sums, and its reduction modulo
two is nonzero. That reduction lies in `ker(H)`, and its support is contained
in the original support. The finite certificate therefore proves the bound.

For a trace-zero quadratic `q`, every frame has zero sum: its seven roots
are an orthogonal basis of `a`-perp with squared norm eight, so
`sum(q(r): r in frame) = 8 trace(q) = 0`.
It remains to check that a nonzero quadratic cannot vanish on all of `R`.
Here is an elementary injectivity argument.

Write `J={1,2,3,5,6,7}` and `y=x_0=-x_4` on `a`-perp. If a quadratic
vanishes on every `2e_i +/- 2e_j`, with `i,j` in `J`, subtracting the two
evaluations kills each mixed coefficient within `J`, and adding them shows
that every pair of diagonal coefficients sums to zero. Three distinct indices
then force all six diagonal coefficients to vanish over the rationals.
The root `2e_0-2e_4` kills the coefficient of `y^2`. Only
`y sum(b_i x_i: i in J)` remains. The 32 half-root lines have `y=1`, with
all odd-parity six-sign rows `s`. These rows satisfy `sum(s s^T)=32 I_6`,
so vanishing on them forces every `b_i=0`. Thus the original quadratic was zero.

This proves the lower bound for the stated rational domain. To transport it
to any E8 root, the verifier checks nine orthogonal root-set automorphisms:
seven adjacent coordinate swaps, negation of coordinates zero and one, and
reflection in `(1,-1,-1,-1,1,-1,-1,-1)`. Their orbit on `a` contains all
120 root lines. Orthogonal rational transport preserves trace and support.

## A twelve-line attainer

Restrict

\[
 q_0(x)=x_0^2+x_1^2+x_2^2+x_3^2-x_4^2-x_5^2-x_6^2-x_7^2
\]

to `a`-perp. The ambient trace is zero and `q_0(a)=0`, so the restricted
trace is zero. On `R`, the six coordinate-root lines within `{1,2,3}` have
value `+8`, the six within `{5,6,7}` have value `-8`, and the other 51 lines
have value zero. Indeed, cross-part coordinate roots cancel, `2e_0-2e_4`
cancels, and every half-root has four positive and four negative square terms.
The verifier checks the twelve nonzero values and all 135 literal frame sums.

## Relation to the handoff and limits

The delivered scope repairs the proposed auxiliary support statement by adding
trace zero. If an ambient trace-zero quadratic vanishes on the pivot, its
restriction to the pivot's orthogonal complement is trace-zero: in an
orthonormal basis beginning with the pivot direction, that first diagonal
entry and the total trace are both zero. The new lemma can therefore supply
the support step in the handoff's proposed reduction, conditional on its
separate arbitrary-deletion extension statement and the remaining hypotheses.

The advance claim asked about the unrestricted statement. Semantic overlap
checking identified the earlier eleven-line coverage before any commit.
The original contribution delivered here is the trace-zero replacement.
Neither the earlier flat census nor any predecessor's rigidity result is
replayed or re-verified as this contribution.

The binary minimum is a complete finite enumeration, not a formal proof-kernel
certificate. The rational implication and injectivity argument are written
proofs. Native realization, physical supplier admission, selected cold replay,
Lean and the complete multiplication theorem are outside scope. No new kappa
or selected-frontier change is claimed.

## Reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/e7-quadratic-support/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/e7-quadratic-support/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/e7-quadratic-support
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/e7-quadratic-support --check-source-history
```

Another CPython 3.12 path can replace the local interpreter path.
Expected status is `PASS_E7_TRACE_ZERO_SUPPORT`, with 63 lines, 135 frames,
binary rank 36, dimension 27, 134217727 nonzero codewords, minimum weight 12,
a quadratic attainer with six positive and six negative values, and 92
rejecting controls. Normal and optimized modes use explicit checks, not assertions.

The verifier constructs E8 and the intrinsic E7 slice separately and checks the
root orbit. Omission controls reject every incomplete 63-line domain; basis
controls reject every one-bit-corrupted basis vector and wrong dimensions.
It uses bounded traversals, no recursion, and a constant-memory Gray census.
Python runtime allocation is unavoidable; the stored geometry has only 120
root lines, 135 frames and 27 kernel vectors. Optional
`--receipt /absolute/path/outside/the/package.json` writes a generated receipt
bound to all five package source hashes. Direct replay needs no Git or
predecessor imports and writes nothing into its source package.

## Open next questions

1. Does every live-frame zero-sum rational function on P112 minus at most
   seven lines extend to an ambient trace-zero quadratic? This is handoff
   statement (1) and is the remaining uniform bridge in that reduction.
   First prove an extension lemma retaining every deletion quantifier.
   Its existing finite fixtures do not establish that implication.
2. Which trace-zero quadratics attain support twelve? A classification could
   identify all possible sparse equality obstructions. First determine the
   rational kernels on the weight-twelve supports; no equality classification
   is claimed or required for the present minimum.

## Sources and credit

The immediate question comes from
[JoyboyBrian's released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1502#discussioncomment-19145642).
The full-family shortcut and its eight-deletion counterexamples are Josie
Elliston's [#1668](https://github.com/CrocSwap/integer-mult-bounds/pull/1668),
following [#1650](https://github.com/CrocSwap/integer-mult-bounds/pull/1650)
and [#1616](https://github.com/CrocSwap/integer-mult-bounds/pull/1616).
Andrey Mas's [#1560](https://github.com/CrocSwap/integer-mult-bounds/pull/1560)
supplies the incidence criterion. Aaron Wang's
[#1649](https://github.com/CrocSwap/integer-mult-bounds/pull/1649) separates
the subfamily question. DreamingOfClouds / #595 and #3045 and DaysSky / #897
retain credit for the earlier unrestricted eleven-line support coverage.
The retained E8 model and rigidity lineage credit Brett Halligan / #1212,
themilkman216 / #968, and DreamingOfClouds / #717.

These are motivation and provenance, not mathematical inputs to the new
self-contained certificate. `SOURCES.json` pins the originating catalogue and
predecessor notes at canonical main
`ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`.
