# Independent review of fixed-witness tensor sharpness

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is separate mathematical reasoning and exact implementation, not human
peer review or proof-kernel acceptance.

## Conclusion and exact pins

The refined four-axis certificate attains the stronger squared tensor-witness
floor **24** while retaining the finite obligations for the bounded-error,
sum-preserving, globally phase-covariant exact-square map. The result concerns
the specified witness `lambda e0^T`. It does not assert a worst-case tensor
discrepancy bound or a new multiplication exponent.

The checked `CERTIFICATE.json` has SHA256
`44a950a62abec947b4c094c2c1f290bec2f8d7f41d3a108ab4c58b5bdfc46b56`.
The independently expanded table has SHA256
`4b69d88e3049b4abca063d79e9145d2519bdbc506a09858dec4c210059b4dc43`.
The period rows remain `(0x21,0x906,0x6fde,0x103,0xa8ec,0x29e)`. Thus the
previous lattice-to-global-map proof and its precise scope apply; this
refinement changes the correction table rather than the period lattice or lifting formulas.

## Forced cycle and completion

Write `B=SW/4`, with W the sixteen-dimensional Walsh matrix, S the parity
diagonal and `K=SJ`. Prescribe `e0 -> e3 -> e15 -> e12 -> e0` under T and
put `c(e_j)=4e_next-SW e_j`. Direct dense integer computation gives one
coordinate equal to 3 and fifteen of absolute value 1 in each correction:
its energy is 24. Both weighted sums against the real and imaginary parts of
`D_jj=(-i)^wt(j)` vanish.

The correction identity is `c(next)=-B c(current)`. It follows algebraically
from `B^2=K` and `e_nextnext=K e_current`, and B applied to every correction
is integral. The positive quotient labels are 64, 849, 3920 and 3136; their
negatives have labels 201, 960, 4049 and 3289. All eight differ and lie outside
the 64-class zero-correction fiber `L/Gamma`. K shifts the cycle by two because
all four support indices have even weight. Hence there is no local quotient,
oddness, K-covariance or exact-fiber collision.

I ran the existing independently written dense-Walsh checker with its largest
binary L-coordinate representatives. It checks all 4,096 classes, square
transitions, oddness, K-covariance, both weighted sums, integrality, quotient
bijectivity and the unchanged error bound. Maximum correction energy remains
64 and maximum absolute coordinate remains 5. Its altered-correction negative
control still fails the square obligation as intended.

I reconstructed all 4,096 corrections again with descending-column quotient
lifts, without importing the author's kernel. The complete table digest
agrees with the first independent replay. Every class in `L/Gamma` still has
zero correction, preserving exactness on integral ideal images. These full
checks, together with the unchanged global lifting proof, establish the map's
properties; local feasibility of the forced cycle alone would not do so.

## Direct complex tensor check

Separately written integer-pair code implements `F=-D R_C D`, with `R=ST`,
then applies F to every row and column of the complete 16-by-16 witness.
Since `D_33=-1` and `S_33=1`, the forced first transition gives `F(e0)=e3`.
At four axes, `lambda_j=i^wt(j)` and `alpha=-4`. The computation confirms:

- Row-after-column has row 0 equal to `D*1` and all other rows zero.
- Column-after-row has only entry `(0,3)=-4`.
- Their difference has row 0 equal to `D*1+4e3`, with all other rows zero.

All 256 complex entries match. Coordinate 3 of the difference is 3 and its
other fifteen nonzero entries are Gaussian units, so its squared Frobenius
norm is `3^2+15=24`. This attains the stronger fixed-witness lower bound.
No covariance under the nonunit scalar -4 is assumed: exactness on integral
ideal images supplies the necessary value on `-4e0`.

## Reproduction and limitation

From the repository root:

```sh
python3 -I -B research/four-axis-exact-square-grid/independent_sharpness.py
```

Expected status: `PASS_INDEPENDENT_SHARP_TENSOR_COMPOSITION`, with 4,096
finite classes, 256 tensor entries and `tensor_defect_squared: 24`.
Normal and optimized Python runs passed. This is fixed-witness sharpness
inside the same bounded-error exact-square family. It does not assert row/
column commutation, a worst-case tensor discrepancy of 24, or a physical caller.
