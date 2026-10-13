# Independent frame review of mixed-center fusion

Source: PR46 head `71b6c960c89295e952522dd44111df9cfc51ae90`, especially `scripts/structured_bulk/complex.py`, `notes/structured-bulk-complex.tex`, `notes/copied-centers-complex.tex`, `notes/copied-centers-lemma.tex`, and the retained transparent word in `notes/complex-circuit-construction.tex`.

## Scalar fresh-difference statement

Work over Gaussian integers at a common denominator tag: write source values as `x_S = z_S / 2^p`, with `z_S` Gaussian integers. Old dirty states may be arbitrary Gaussian dyadics, after alignment to a common tag. Let `T = sum z_S`, `G_i = sum_{S contains i} z_S`, and let `D` be the first 19 points of the 28-point source.

The new-minus-old retained-center increments are

```
delta B_i = 2 G_i                  (i outside D)
delta D_i = T - G_i                (i in D)
delta N   = sum delta B_i - 2 sum delta D_i
          = 2(3 - 19) T = -32 T.
```

Thus dividing `delta B_i` by two and `delta N` by minus 32 is exact on common-tag integer numerators. Old dirty `B_i` or old `N` need not satisfy these divisibility predicates. A raw old scatter can require denominator 64, as the existing notes state.

For target triple `S`, define `center2_S = sum_{i in S} G_i - T`. Add the complete disjoint sum and subtract the complete intersection-two sum *before* dividing by two. Each source triple `U` then has numerator coefficient

```
(|S intersect U| - 1)
+ [|S intersect U| = 0]
- [|S intersect U| = 2]
= 2 [S = U].
```

The fused output is exactly `z_S`, hence remains at the input common denominator tag. This is a scalar shear identity for the fresh contribution; it holds with arbitrary old dirty auxiliaries because the transparent word computes an old/new difference.

## Why dirty differences are sound

The retained old-value/new-value word gives target increment

```
- J L z - R w + R(w + G x) + J L(z + V x)
= (J L V + R G) x = x.
```

The final inverse mixer and source-copy cancellation restore old scalar scratch. Fusion of `R(w+Gx)-Rw` and the matching side differences can therefore serve as an independent exact interpreter. It is not valid to assume divisibility separately for either old scatter.

## Physical frame boundary

The actual network is not an unframed scalar circuit. A retained center starts at frame `D_U`; its read copy is transported to the common frame `D0` (forward) or `D1` (reverse-complement). The old original is transported to its cleanup frame. Side injections have target-dependent phase frames. An edge applies `C_{Q2} C_{Q1}^{-1}`; every common-frame scalar gate is physically conjugated by that frame.

The copied-center lemma guarantees read copies agree with the old schedule at the unchanged common frame. This supports using the fresh-difference identity as a scalar reference *after consistent frame transport*. It does not establish that all scalar fusion terms become adjacent physical pointwise gates, or that their necessary streams can be read at lower cost.

At the complete physical invocation boundary, every original role—including dirty auxiliaries—receives the selected-axis tensor `C_F`. Scalar restoration corresponds to that prescribed physical endpoint map, not identity on raw physical scratch bytes. Tests of the physical wrapper must compare dirty outputs against `C_F` of their input.

## Defensible integration claim

An integer-only fresh-difference compiler/reference can eliminate artificial scatter denominators in the scalar audit, check division predicates exactly, reject divisibility applied to raw dirty states, and serve as an independent oracle for the current mixed-center producer. A common tag handles dyadic data already produced by other phase children. The scalar identity is general and coefficientwise; finite tests can verify its actual DAG implementation and negative cases.

No reduction of the general intermediate precision bound, fixed-tape charge, row stock or exponent kappa follows without a new physical scheduling/frame proof. The existing semantic precision proof expressly keeps all streams on the fixed fine grid without compression or re-encoding. Its magnitude guard also remains needed.
