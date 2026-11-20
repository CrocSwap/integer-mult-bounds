# Prove full Stein rank for every ordering of three selected source factors and expose an interior box obstruction

## Contribution and significance

The quantitative two-axis theorem in
CrocSwap/integer-mult-bounds#7599 does not extend directly to three
axes. Its parameter box contains a singular boundary example. This
package separates that box obstruction from the actual distinct-prime
source family.

For every triple of distinct fine-prime source axes satisfying the
stated guards, the extremal two-point sections give an eight-by-eight
tensor whose ordinary Stein displacement has **rank eight in all
40,320 simultaneous vertex orders**. The same holds for its exact
inverse. Physical source phase/chirp coefficients are retained. This
raises the fixed three-axis exact floor from six, supplied by
CrocSwap/integer-mult-bounds#7598's general matching argument, to full
rank eight.

A complementary exact counterexample shows that the box obstruction
also occurs away from the boundary: for repeated
`B=[[1,u],[v,1]]`, the order `(0,1,2,4,6,5,3,7)` of
`B tensor B tensor B` has two pairs of equal displacement columns.
Its rank is at most six even when `0<u<1`, `0<v<1`.
The rational example `u=2047/2048`, `w=1/4096`, `v=3/8192` is inside the
earlier box and has rank exactly six.

The new proof certifies every formal six-variable full determinant
at one integer test point, then applies degree-eight source exponent
separation, distinct-prime CRT and the classical Gelfond-Schneider
theorem. A determinant Schur identity pays for inverse order reversal.
The equal-factor counterexample is outside the actual distinct-prime
family and does not contradict the positive theorem.

## Verification

```sh
python3 -B scripts/research_package.py --package research/three-axis-extremal-source-rank
```

The primary modular checker and a separate Kronecker/Bareiss integer
checker cover all 40,320 orders and agree on the ordered residue
digest. The integer checker also verifies the inverse/reversal
identity on exact rational matrices. Source checks authenticate four
inputs and verify three prime/source fixtures by exact certificates,
literal phase formulas and degree-eight exponent guards.

Controls detect equal-factor rank loss, an invalid order, a composite
field modulus, inadequate exponent separation, repeated denominators,
missing Stein subtraction and an injected duplicate column.
The finite order computation is complete for its fixed domain;
the written proof supplies the unbounded source-parameter
quantifiers. Distinct algorithms in the same AI worker are disclosed
as such.

## Scope and remaining obligations

**No new kappa. All five foundational assumptions remain.**
This is exact source-specific nonvanishing, not a numerical margin.
It does not prove robustness to periodic aliases, rounded tables
or `Cp`-bit errors. The inverse is of the selected tensor, not
a section of a larger inverse. Growing dimensions, actual
coefficient production and complete caller integration remain open.

The result requires eight terms in the specified ordinary
lower/upper Toeplitz generator representation, or 128 scalar slots
when both length-eight generators of every term are materialized
separately. This is not a general runtime or memory lower bound.

The next quantitative task is to bound determinants along actual
distinct-prime source curves near the strict equal-factor
singularities, including prime spacing and every inverse/error bill.

## Provenance and credit

Canonical base:
`e54523517d0f03e58352e647c403a5af3e525a57`.
Predecessor heads:
`0a6315b71a47b37a4faa2a4f555c5bc4e9e87811` for #7598 and
`702c7616667c5f4e583eb73687944d148b7a1ccf` for #7599.
The package includes exact source pins, proof, results, overlap
scope and open next questions.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI
assistance. Credit the #7598/#7599 source and rank arguments,
#7600's separate coefficient adapter, Chafik Boukhalfa / #1786,
Vlado Vojdanovski / #1673, IdeaOuter's work credited in #1758,
Jeremy Kothe and the retained bilateral/framework lineage.
Gelfond and Schneider's transcendence theorem and the classical
CRT/Schur methods retain their credit. No independent human or
formal-kernel theorem acceptance is claimed. Apache-2.0.

## Independent orchestration review

The proof and inverse/reversal step were reviewed separately. A new checker
certifies all 40,320 orders at a different integer witness and prime and
rederives the literal source exponents; see REVIEW.md. This is model-assisted
review, not independent human or formal-kernel acceptance.
