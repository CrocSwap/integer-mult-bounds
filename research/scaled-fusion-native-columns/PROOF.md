# Exact columns for the two changed native transports

This audit freezes PR6529 at 44b0d0e8961201ac1656490b4384a7752e1cd9c5.
It covers only transports 243 to 127 and 240 to 127, for fields 368 and 336.
The concurrently claimed 569-gate output correction is outside this scope.

## Source boundary

The live word and specification are exact retained bytes. The checker confirms
the two old MOVE pairs in the embedded PR6453 source and one new direct MOVE
for each field in PR6529. The frame table is unchanged. It walks all nine
nested source archives and compares the actual compiler bytes with the retained
compiler file. This is a runtime equality check, not a provenance-only claim.

A normal Python child invokes the original `canonical_frame` and `lower_child`
functions for these two maps. Assertions stay enabled even when the parent
checker runs with `-O`. The exact produced recipes and circuits must match
`RECIPES.json`. No other source construction, price or caller replay is run.

## Separate coordinate calculations

The first consumer executes the serialized monomial and C gates on each of
512 coordinate inputs. It uses integer real/imaginary pairs and an explicit
power-of-two denominator. A C gate sends each coefficient to its original
address and its translated address. Permutations, quadratic phases, shifts
and global phases are applied literally. No Pauli tableau decides equality.

The second consumer never imports the compiler or native checker. It extends
each frame basis by explicit finite spans, forms the chart permutation and
its inverse by address tables, then evaluates its quadratic phase. For a rank-r
frame, the central Fourier coefficient at mask m is

```
(1+i)^(r-|m|) (1-i)^|m| / 2^r.
```

The chart phases before and after this coefficient are included. The inverse
uses conjugate coefficients. Direct convolution gives each column of
`C_new C_old^*`, with exact cancellation in the integer numerators. The full-rank
frame uses the source's literal nine-axis Fourier convention. The denominator
is reduced only when every coefficient has a common factor two.

All 512 columns of each compiled recipe equal this closed calculation. This
compares all 524,288 complex coordinate positions, including zeros and absolute
phase. Each column has 32 nonzero positions, as the rank-five recipe predicts.
The conjugate transpose of each independent matrix is then compared with all
512 columns of the literal inverse circuit. Thus 1,048,576 forward and inverse
positions are checked in total. Hashes include zeros and exact denominators;
entrywise equality is checked before hashing.

Every primitive is unitary: a monomial is a unit-modulus diagonal followed by a
permutation, and the two-point C block has eigenvalues 1 and i. Hence the
literal reversed conjugate circuit is the inverse. Equality on the coordinate
basis proves equality on arbitrary complex data at this finite width. The
matrix equality also implies equality of every positive tensor power. Applying
that implication to an actual all-size compiler still requires its stated
block/tensor placement contract; this audit does not prove that compiler.

## Relation to the fusion and limits

For any three exact frame operators, the chronological old path telescopes:

```
(C_G C_F^*) (C_F C_E^*) = C_G C_E^*.
```

This identity includes the absolute phases. A scalar sign commutes with these
linear maps. Thus moving the sign to the held frame is valid for this exact
native interface. It is not automatic for a nonlinear rounded grid kernel;
phase/sign covariance or a literal revised caller proof is needed there.

The source's rank-four plus rank-one to rank-five paid change remains credited
to PR6529. This audit does not price the changed scalar correction, reconstruct
the whole native word, rerun all caller contacts, or admit its conditional kappa.
The existing source Pauli-plus-phase proof was already logically complete.
These are separate AI implementation checks of its two changed maps, not a
claim of a new generic theorem, a source flaw, human review or proof-kernel
acceptance. All five framework assumptions remain.

## Rejecting controls

For each map, changing the absolute phase, reducing the child rank, using the
inverse direction, or inserting an input Z phase changes a checked column.
The Z fault preserves column zero exactly but changes column eight. It is a
specific control for the added full-column coverage. Source and table receipts
also remain hash-bound; the portable replay rejects a changed retained input.
