# Exact full Stein rank for three selected physical source factors

**All 40,320 orders have rank eight. No new kappa.**

For three distinct fine-prime axes, take the same deterministic extremal
two-point source sections used by
[CrocSwap/integer-mult-bounds#7599](https://github.com/CrocSwap/integer-mult-bounds/pull/7599).
Their unrounded, alias-deleted tensor and its exact inverse have full
ordinary lower-shift Stein displacement rank in every simultaneous
vertex order. The result retains the literal source phase/chirp
coefficients.

This improves the predecessor's general exact rank floor from six to
eight in this fixed dimension. It does **not** extend the predecessor's
quantitative two-axis rounding theorem. No numerical margin, periodic
alias tolerance or `Cp`-bit robustness is proved.

## Why the source restriction matters

The parameter-box obstruction is stronger than the known `U=1`
boundary example. For any repeated factor `B=[[1,u],[v,1]]), the order
`(0,1,2,4,6,5,3,7)` of `B tensor B tensor B` gives two pairs of
identical displacement columns. Its rank is at most six even for
strictly positive decays `0<u<1`, `0<v<1`.

The rational example `u=2047/2048`, `w=1/4096`, `v=3/8192` lies inside the
earlier asymmetric box, strictly away from `U=1`, and has rank six.
Thus removing that boundary face cannot justify an all-order
full-rank extension. Actual distinct-prime source triples avoid these
and all other zeros by a separate source arithmetic argument.

## Proof

[PROOF.md](PROOF.md) gives the complete quantified statements.

1. The exact source pair is `[[1,U_l],[V_l,1]]), with
   `U_l=exp(-a(2delta_l+1)/s_l)` and
   `V_l=exp(-a(2s_l-1)/s_l)`.
2. Every eight-by-eight displacement determinant is a nonzero polynomial
   in its six directed factor variables. A single integer evaluation
   certifies this for the complete set of 40,320 orders.
3. The fine-prime guards make each source exponent map injective through
   degree eight. Distinct-prime CRT separation prevents cross-axis
   cancellation. Gelfond-Schneider then gives exact nonvanishing.
4. A Schur-complement identity transfers full rank to the inverse with
   order reversal explicitly included.

The exact minimum in the ordinary lower/upper Toeplitz product
representation is therefore eight terms in every order. A format that
stores their two length-eight generator vectors separately uses at least
128 scalar slots. No general circuit, algorithm, runtime or memory lower
bound follows.

## Reproduce

Python 3.12 or later, standard library only, from the repository root:

```sh
python3 -I -W error -B research/three-axis-extremal-source-rank/verify.py
python3 -I -W error -B research/three-axis-extremal-source-rank/review/check_integer.py
python3 -B scripts/research_package.py --package research/three-axis-extremal-source-rank
```

Both direct scripts are read-only. The primary script authenticates four
retained source inputs, evaluates all 40,320 determinants over a proved
prime field, checks the strict-box symbolic column identities, and
verifies three exact prime/source fixtures with meaningful controls.
The separate arithmetic audit constructs the tensor by Kronecker products
and uses fraction-free integer determinants over the same entire domain.
Their ordered residue digests agree:

```
03f10c1a02430d1f476cc71967b2b51b3f061c697488a19de49f925bc5f74aa0
```

[RESULT.json](RESULT.json) and
[review/INTEGER-RESULT.json](review/INTEGER-RESULT.json) retain the
outputs. The integer witness determinants have absolute values from
159,381,760,000 through 2,566,943,397,076,755,904. These are algebraic
test-point values, not source determinant margins.

The exhaustive finite order certificate proves polynomial nonidentity;
the written source argument supplies the unbounded parameter
quantifiers. The prime fixtures corroborate only the declared local
source guards, not a complete producer or outer multiplication caller.
Two independently implemented arithmetic algorithms in one AI worker
are not independent human or formal-kernel acceptance.

## Scope and cost

The canonical base is
`e54523517d0f03e58352e647c403a5af3e525a57`, selected conditional
`kappa=0.00363005817`. [DEPENDENCIES.json](DEPENDENCIES.json) pins
the scientific inputs; [SOURCES.json](SOURCES.json) records repository
provenance; [OVERLAP.md](OVERLAP.md) records bounded overlap checking.

The selected source factors are unrounded and have their aliases deleted.
The inverse is that of the selected tensor. The selector pays for
modular inverses and returned indices; it does not construct coefficients,
generators, an inverse page or a complete caller. All five foundational
assumptions remain: native_all_columns, owned_erasure, compiler,
precision_tape and analytic_recovery.

## Open next questions

- **Actual-source quantitative margin.** Bound the displacement
  determinants along distinct-prime source curves near the strict
  equal-factor singularities. Start with the displayed order and
  include actual prime spacing; exact transcendence alone supplies
  no useful rounding budget.
- **Periodic and rounded source tables.** Once a margin is available,
  charge tensor entry error, inverse conditioning, aliases and the
  actual coefficient producer. The four-call two-axis adapter in
  [#7600](https://github.com/CrocSwap/integer-mult-bounds/pull/7600)
  does not automatically provide these three-axis bounds.
- **Growing dimension.** Determine whether full generic displacement
  rank persists for all orders at four or more axes, or identify the
  first structural counterexample. An eight-vertex enumeration is
  not a theorem for increasing dimension.

## Credit

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
The new work is the full three-axis polynomial certificate, its
source specialization at degree eight and the strict-interior
equal-factor obstruction.

Credit #7598 for the selected-phase exponent separation method and
#7599 for the extremal selector and quantitative two-axis theorem.
Chafik Boukhalfa / #1786, Vlado Vojdanovski / #1673, IdeaOuter's work
credited in #1758, Jeremy Kothe and the retained bilateral/framework
lineage retain their contributions. The classical transcendence input
is A. Gelfond, *Sur le septième problème de Hilbert* (1934),
pp. 623–634, theorem on printed p. 628
([original record and text](https://www.mathnet.ru/eng/im4924));
Schneider's independent theorem is also credited.
No classical determinant, CRT or transcendence theorem is claimed as new.
Source notices and Apache-2.0 terms are retained.
