# Replaying the evidence

The seven commands registered in VERIFY.json use Python 3.12 and its standard library. The algebraic checker, prefix-state counter, and literal matrix enumeration are differently constructed checks from the same assisted author. The finite runs corroborate the written proofs.

| Check | What is actually counted |
| --- | --- |
| Algebra and raw prefixes | 248 pencil specializations, 28 binary predecessor comparisons, 42 independent triples and 668 exact-mask size cases. A second method retains each actual prefix and its current column span in 36 small cases. Repeated rows and mixed dependencies are included. |
| Dimension and size signs | 232 field-order/pencil-size windows, compared with direct rational arithmetic at 18,560 dimensions. The scaled boundary integers are floors obtained by integer division. Further examples bound the dimension and family-size crossovers through field order 4096. |
| Recounting the crossings | Eleven raw-prefix calculations give the actual passing-tuple count and orbit denominator at the main boundaries. These include dimensions 60 and 61 over the four-element field and both the dependent and independent triples at dimension 61. They avoid enumerating the enormous groups at those dimensions. |
| Full affine flats | 32 finite comparisons of a separate binomial formula with the lattice sum. Seventeen field orders have exact thresholds for the sufficient last-coordinate condition. |
| Independent triples | A conditional sampling bound covers the infinite tail. The 17 remaining field/dimension pairs have exact ratios from both the lattice formula and a direct count of noncollinear points in coordinate boxes. [Certificates](TRIPLE-CERTIFICATES.json) |
| Smallest possible field order | Five ternary quartet cases below the analytic dimension cutoff are recounted with raw prefixes, including an independent four-row case. [Exact values](TERNARY-FOUR.json) |
| Literal conjugation | The first twelve experiments make 66,042 complete-header visits. They include every invertible two-dimensional matrix at field orders 2, 3, 4, 5, 7, 8 and 9, plus selected normalized families in dimensions three and four. A separate experiment evaluates four affine directions on all 181,440 matrices of `GL_3(F_4)`. |
| All subsets in dimension three | One census at each field order 2, 3 and 4 covers all 16, 512 and 65,536 subfamilies of the complete affine plane respectively. Every observed count agrees with the rank-three master formula, including rank-deficient subfamilies. The empty-subset count checks the total number of headers. |
| Rejection controls | 21 actual private-copy faults are each rejected with the specified reason in normal and optimized Python. Four unmodified controls pass. The faults include dropping rank subtraction, altering a field-size factor, changing the forbidden prefix value, imposing the full-order minor, changing the determinant stratum, weakening the ternary count and editing a pinned precursor. |

A complete-header visit refers to one matrix in one stated family experiment. Several experiments use the same group. In the affine-plane sweep at field order four, the 65,519 nonsingleton subsets all lie above the product in dimension three. The 16 singletons give equality by definition. These finite counts alone say nothing about the signs in larger dimensions. The four-element pencil of three directions changes sign at dimension 61.

## Literal and prefix methods

The literal enumerator traverses all square coordinate arrays in lexicographic order, discards singular matrices by elimination, constructs the actual conjugate of each complement with two matrix products, and tests its proper leading determinants. It records the mask of named passing guards. It also checks that every nonzero determinant stratum gives the same per-mask counts. The byte trace hashes concatenate each accepted header in row-major field-element encoding, its determinant byte, and a fixed-width little-endian mask. Extension fields use polynomial bases: over the binary field the moduli are `X^2+X+1` and `X^3+X+1`; over the ternary field the quadratic modulus is `X^2+1`.

The prefix program instead loops over raw coordinate and column choices with exact field arithmetic. Its state carries the current prefix and the span of columns in the quotient by the all-ones line. It never uses the Möbius coefficients or pencil bases. The all-subsets check uses a third counting arrangement: it retains all directions in one rank-three master and sums literal masks over supersets. In the formula path it counts supports of coefficient vectors in the ambient space and its projective planes, leaving coordinates outside the chosen subset unconstrained.

## Reproduction from package files

```sh
python3.12 -I -W error -B verify.py
python3.12 -I -O -W error -B verify.py
python3.12 -I -W error -B literal_check.py
python3.12 -I -O -W error -B literal_check.py
python3.12 -I -W error -B literal_check.py --extended
python3.12 -I -W error -B plane_check.py
python3.12 -I -W error -B audit_mutations.py
```

The compact hashes and histograms are retained in [literal fixtures](LITERAL-GL.json), [the four-element pencil](GL4-ORDER3.json) and [the full planes](AFFINE-PLANES.json). The formula checks and exact integer brackets are in [the primary result](RESULT.json), [the sign windows](SIGN-WINDOWS.json), [the scaling examples](ASYMPTOTICS.json) and [the full-flat examples](FULL-FLATS.json). Runtime uses no predecessor code or network input.

## Optional larger censuses

Run `python3.12 -I -W error -B extra_censuses.py` from the package directory. The full five-direction pencil passes on exactly 99,200 of the 1,488,000 headers in `GL_3(F_5)`, giving `1/15 > (441/775)^5`. This literally checks the opposite sign to the dimension-two case.

Over the ternary field, the program traverses 1,516,320 invertible four-dimensional headers modulo the 16 free left diagonal scalings. These classes account for all 24,261,120 headers. The initial image vector has four nonzero entries. All 64 named subsets of six directions agree with the rank formula. The three quartet counts from SMALL-FIELDS.md at dimension four are 1,166,400, 1,660,608 and 1,499,712. [Larger census fixtures](EXTRA-CENSUSES.json)
