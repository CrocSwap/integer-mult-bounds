# Fixed-word endpoint and e264 refit

## Global raw bound

Let `D(t)=T(t)-P(t)` be the difference of productive and paid moments for
the exact homogeneous 36-call binary word, where each rank occurrence counts. The
[global lemma](GLOBAL-PROOF.md) normalizes at rank 8 and uses nonnegative
upper tails to prove `D(t)/8^t` strictly increasing for every `t≥0`.
For `t≤0`, the rank-one deficit and the total positive count prove
`D(t)≤-30678`. At `t=0` and `t=1`, `D` is respectively `-85998` and
`1506`. Thus there is one crossing and no re-entry for all real `t`.
Two directed integer-root enclosures put its corresponding price strictly
inside

```
0.003890115286594461129996942 < c* <
0.003890115286594461129996943.
```

The next `10^-18` reporting point is therefore above the raw crossing.
This conclusion fixes the exact paid and productive occurrences; it is
not an upper bound for a changed word or a different multiplier.
`global_crossing.py` rebuilds the literal source inventory, checks the
signed coefficients, tail sums, endpoint signs and a corrupted-tail
rejection. It reproduces [GLOBAL-CROSSING.json](GLOBAL-CROSSING.json).

## A funded seven-stage arithmetic profile

The source at e264 uses the rate rule

```
covered_i = c - 11/(8 H_i)
limit_i = min(eta, (249*covered_i + b_(i-1))/250), b_0=0
```

and chooses the first six rates on its own `10^-21` grid. The final rate
is `κ+5g`. For the named candidate use

```
c = 287039844436133239/2^66
g = 10^-21                   kappa = 0.003890115286594461
H_i = 2*10^12*16^i          i=0,...,6
H_M = 36000                  eta = 39/10000
```

The exact source `profile_row` verifies every strict stage inequality and
the 54 strict and four functional signed gates. The seventh limit exceeds
`κ+5g` by

```
27007124810227343 / 1759218604441600000000000000000000000.
```

The binary directed relative surplus is exactly
`191135881425181897/61353847083031545306054570474927705731` in the
source's certified enclosure. The recomputed transport has 24 nonempty
grade cells; the original full 18,906/104,904 target/paid label census is
unchanged. The later signed numerical construction uses two copies of its
48-call word; its unchanged two-scale positive source has 105,216/564,144
labels and 54 cells. The source tariff checks row and column sums,
minimum positive cell share, the physical `11/(8H)` and `39/(256H)`
debits, and both budget factors. Two different directed raw readers give
positive binary margin. [Tariff receipt](ENDPOINT-TARIFF.json)

The previous source price `4484997569314581/2^60` is already below the
new κ; the source price guard rejects the candidate with that old value.
The package also checks the different `0.003890115286594460` control
using the old price and seven stages, in a separate reconstructed source
and interpreter. No previous certificate is overwritten.

## How much dyadic precision is needed?

For these fixed seven heights and `g=10^-21`, the largest raw-funded
64-bit dyadic has numerator `71759961109033309`. Even omitting all
intermediate rounding, its seventh ordinary upper is below `κ+4g` by
approximately `2.4301e-20`. Every dyadic with fewer denominator bits is
also on this mesh, so none can satisfy the fixed-height ordinary gate.
The largest funded 65-bit dyadic has numerator `143519922218066619`; its
six rounded intermediate rates leave approximately `1.7975e-21` above
`κ+5g` at stage seven. The selected 66-bit trial leaves approximately
`1.5352e-20`. These are exact rational checks in
[denominator_design.py](denominator_design.py), conditional on the fixed
raw inventory, heights and rate rule. The 65-bit result is only raw and
ordinary arithmetic; it is not a complete installed positive/physical
witness.

## Extending the 66-root precision and fixed setup

The binary `t=1-c` has denominator `2^66`. The actual source loop has
67 passes, 66 root levels and at most 67 accumulator products, instead
of the published 60/61 bound. The original grid has spacing
`2^(-64(H+1))`; its source recurrence bounds a step by
`4*sqrt(512*N) < 2^7*sqrt(N)`. Conservatively charging both endpoints and
`V/t`, with `V=N^6` and `t>1/2`, bounds their count error by

```
16*(2^7*sqrt(N))^67*N^6 / 2^(64(H+1))
    = 2^(409 - 49*H/2) < 1/4  for H >= 1024.
```

This extends the written rounding induction; the executable check counts
132 actual paired integer-square-root calls at four feasible arguments and
compares the resulting intervals with an independent rational log/exp
reader. The source's former numerical statement `binary surplus >1e-18`
is replaced by the directed margin above; the test separately verifies
the source's positive-cell and `δ=2^-128` conditions. No production-sized
calendar is opened by this test.

The maximum binary H, cut and public exponent need 65 bits; `92H` needs
72 bits. The actual numerical rank `2^36000` needs 36,001 bits. The
stopping denominator `10^21` has 70 bits and 29 one-bits, so the original
69-square/29-multiply bound applies. For the numerical cap at H=36000,
the fixed signed fractions have common scale `3D²`, not the `19D²` used
by the older H=19000 instance. These values are all far below the source's
`2^38`-bit item allowance. [Exact controls](ENDPOINT-SETUP.json) · [Uniform source ranges](UNIFORM-RANGES.md)

The additional dyadic levels can at most double the source's stated
endpoint arithmetic allowance. With a conservative extra factor for the
candidate installation, the cited fixed indexed-action envelope is below
`2^70`. The source's `2^400` sequential access/arithmetic allowance and
`2^32` parsing factor then give `2^502 < 2^513`. Even doubling the
source's table-preparation bound to `2^151*N^2*(H+1)^6` stays below
`N^3` for H≥1024. This is an adaptation of the source's written cost
accounting, not an independently measured production runtime or a proof
of all its compiler and storage premises.

## Physical interpretation and limits

The overlay installs a named profile before source imports and rebuilds
both grade couplings from the changed c. It exercises actual stage
selection at all seven cut boundaries and the source's first numerical
external placement at H=36000 (period 1620, first tickets 0, 324, 648;
first swap 1↔324). Its finite positive receiver is constructed at the
stated rank and stopping denominator; the M/M+1 dispatch test mocks the
payload. These observations do not allocate a production-dimensional
binary field or execute the physical multiplier at the sufficient entrance.

The [role-transfer argument](ROLE-TRANSFER.md) binds the changed-c
admissible jobs to the same stage-store branches and page arities, using
the source's stated global data census. That binding remains a written
argument under the inherited premises; a later parameterized kernel lemma
is not a formal proof of this particular source-to-role mapping.

The earlier #8048 uses a different `3d33cb0` retimed source with its own
prices and heights; this refit is pinned at e264 even though #8042 later
added related stage-store formal work at dfd25d5. A standalone [Lean
4.8/4.34.1 certificate](lean/Endpoint.lean) checks the seven exact
rational stage bookings, six rounding rules, the signed
booking inequality and corruption controls. Its raw upper is an external
hypothesis; neither the source/coupling nor the all-size multiplier is
Lean-verified by this certificate. The global upper and the
finite lower remain conditional on their respective fixed-source models;
the five inherited all-size obligations and independent human review
remain open.
