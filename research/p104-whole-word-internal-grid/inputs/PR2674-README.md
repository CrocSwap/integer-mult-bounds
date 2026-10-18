# Physical component precision for the corrected P104 dual

For the unchanged **5,398-event** canonical physical word in
[ywz65's PR2586](https://github.com/CrocSwap/integer-mult-bounds/pull/2586),
head `7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`, a sufficient caller format is

```text
fractional bits: f + max(10 lambda, 9 lambda + 2)
component magnitude: < H * 2^(ceil((9 lambda + 1)/2) + 6).
```

Here `lambda` is any positive integer payload tensor depth. Every real and
imaginary component of every public physical input lies in `2^-f Z` and has
magnitude at most `H`. The bounds cover **every allocated field at every
instruction boundary**, including the private collectors and all 416 added
endpoint conversions. At one layer, eleven extra fractional bits and eleven
magnitude guard bits suffice. These are conservative bounds, not optimal formats.

There is also an explicit **interior precision witness**. On integer input
`Y2 = delta_0`, all other physical inputs zero, the literal word reaches

```text
after event 2143, D18 at address 0 = (-1+i)/128.
```

All final fields of this execution need at most six fractional bits; the
interior needs seven. More generally, a product-delta integer input at depth
`lambda` requires **`ceil(9 lambda/2)+2`** fractional bits at that cut, while
its complete final state requires exactly **`ceil(9 lambda/2)+1`**. An
endpoint-only format misses a bit at every positive depth. This is a new
transient of the pinned physical word. The separating final value
`X0[0]=(-1+i)/64` and its input are credited to PR2551/2586.

## Contract and limits

Each instruction is exact and atomic. A transport from `A` to `B` means
`Delta_B Delta_A^-1`, with `Delta_W = conjugate(Gamma_W)` for the canonical
nine-coordinate chart in the pinned
[`native_verify.py`](../p104-native-channel/vendor/native_verify.py).
At tensor depth `lambda`, **each chart** is tensor-powered; scalar ADD
coefficients remain the word's original rationals. This is the usual payload
lift of the word, not the tensor power of its whole scalar matrix.

The statement concerns physical array components. It is separate from
[Nick Petalas's PR2549](https://github.com/CrocSwap/integer-mult-bounds/pull/2549),
which bounds completed-child defects in logical Hilbert norm for the older
4,982-event clean dual. Its `P=127/2` is reproduced here with credit, not claimed
as new. PR2586 supplies the physical operator/native binding; that pending
claim is not independently admitted by this package.

If exact instruction outputs are rounded to the stated grid, rounding is a
no-op at these boundaries. **No child-internal precision or approximate-child
error estimate follows.** Internal Fourier arithmetic, arbitrary rounded
defects, strict erasure after approximate execution, intrinsic endpoint
adapters, physical ownership/routing, idle/residual work and all-size supplier
admission remain open. This does not supply a favorable moment, new supplier
or new kappa. The other 102 forward rows still have the predecessor's Gram/2
contract; this is not an all-target identity correction.

## Proof of the all-depth bounds

Write `I_s` for input `s`'s initial frame and `F_r(c)` for field `r`'s frame
after cut `c`. Exact common-chart execution gives

```
V_r(c) = sum_s c_rs(c) [Delta_F_r(c) Delta_I_s^-1]^(tensor lambda) V_s(0).
```

This follows by induction: transport changes only the outer chart; an ADD
combines rows in a common chart; signs negate a row; a fresh owned zero has
the zero row. Each ideal private erase is checked to have a zero row. All
358 initial rows are independent; no arbitrary helper is assumed clean.

The pinned canonical chart is a product of Gaussian monomials and exactly
`dim W` gates of the form `((1+i)I+(1-i)X)/2` (or their conjugates/inverses).
Gaussian monomials use only permutations and powers of `i`. Thus the entries
of `Delta_W` and `Delta_W^-1` lie in `2^(-dim W) Z[i]`. This holds also for
ZERO and FULL. All factors are unitary. These facts follow from the literal
gate formulas; no floating-point estimate or Clifford compiler is used here.

For nonzero dyadic scalar `c_rs`, define `v2(c_rs)` including powers of two
in its numerator. Its term above has entries on the grid with extra bits

```
(dim F_r + dim I_s) lambda - v2(c_rs).
```

The signed rational interpreter checks all changed fields and entries:
**5,748 field boundaries, 103,145 nonzero term visits**. Unchanged fields
retain their last bound; the eight erased fields are zero. For each possible
slope, the largest intercept is exactly:

| Slope `dim F_r + dim I_s` | Maximum `-v2(c_rs)` |
| --- | --- |
| 0 | 1 |
| 1 through 9 | 2 |
| 10 | 0 |

The maximum of these affine bounds for every integer `lambda>=1` is
`max(10 lambda,9 lambda+2)`. `RESULT.json` records a source/cut/coefficient
witness for each slope, independently reconstructed by reverse functionals.
This is a bound on the termwise certificate; cancellation may improve the
actual format. In particular, the slope-ten self term is bounded by a product
of two charts even when that product simplifies.

For magnitude, the largest signed-row absolute sum at any cut is `P=127/2`,
attained at cut 3535 in `X12`. The separate reverse pass corroborates that
row and all 358 public outputs. Every relative chart tensor is a unitary
`D`-by-`D` matrix, `D=512^lambda`; Cauchy--Schwarz bounds each row absolute
sum by `sqrt(D)`. Each input complex entry has modulus at most `sqrt(2) H`.
Consequently every component has magnitude at most

```
(127/2) * 2^((9 lambda+1)/2) H
  < 2^(ceil((9 lambda+1)/2)+6) H.
```

This dimension-dependent conversion is why a logical Hilbert-norm guard alone
is not a fixed physical component format.

### The all-depth interior witness

A separate reverse functional gives coefficient `-1/4` from `Y2` to `D18`
after event 2143, whose target frame is FULL. The initial `Y2` chart is ZERO.
At the all-zero address the integer product-delta input therefore gives

```
-1/4 * ((1-i)/32)^lambda = -(1-i)^lambda / 2^(5 lambda+2).
```

Since `(1-i)^2=-2i`, its nonzero real/imaginary numerators have common
two-adic valuation `floor(lambda/2)`. Its exact required fractional-bit count
is `5 lambda+2-floor(lambda/2)=ceil(9 lambda/2)+2`.

At the end, the same input reaches only the X fields and Y2. Every final X
chart is FULL and its scalar coefficient has denominator at most two; X0 has
coefficient exactly `-1/2`. Thus their exact maximum fractional-bit count is
`ceil(9 lambda/2)+1`. Y2 ends at a dimension-eight chart: monomial conjugation
of eight distinct coordinate C gates has nonzero entries equal to Gaussian
units divided by 16. Its tensor lift needs only `4 lambda` fractional bits.
All these finite endpoint premises are checked by the reverse interpreter.
This proves the one-bit separation at every positive depth. It does not show
that the complete word's optimal global format is attained by this input.

## Evidence and reproduction

The verifier authenticates the exact retained word and predecessor text plus
the live main chart-definition bytes **before reading their semantics**. It
executes no predecessor code. The forward Fraction interpreter and reverse
functionals are separately written, sharing only event parsing and rational
arithmetic. `physical.py` executes all 5,398 events directly on 512-component
Gaussian-integer arrays for the stated physical input. It constructs chart
permutations using complete inverse tables and span enumeration, not the
predecessor's elimination/interpreter. This is one complete physical input
column, not every native recipe or every input column.

The literal fixture checks all 5,748 field boundaries, eight exact private
erasures and the final separating value. It attains seven fractional bits at
the interior and six at the endpoint. It does not attain the conservative
eleven-bit upper bound or prove a sharp magnitude norm.

The reconstructed invoice is unchanged:

```
1632 H1 + 74 H2 + 86 H3 + 104 H4 + 48 H5 + 42 H6 + 76 H7 + 8 H8
rank mass 3542; 3104 ADDs, 208 signs, 8 zero/erase pairs.
```

Standard-library Python 3.12; from the repository root:

```sh
python3.12 scripts/research_package.py --package research/p104-physical-dual-grid
python3.12 -I -O -B research/p104-physical-dual-grid/verify.py
python3.12 -I -B research/p104-physical-dual-grid/test_verify.py
```

Default verification is read-only and compares the complete typed receipt.
`--out NEW.json` writes only to an unoccupied path. Controls reject a missing
decreasing endpoint conversion, wrong rank, non-dyadic coefficient, omitted
private compensation and an endpoint-only six-bit format. Tests also check
canonical-chart unitarity/inversion, a Git-free relocated replay and real
source/receipt corruption. No network is needed for replay.

Validated with CPython 3.12.14 on macOS arm64. The final overlap refresh covered
840 open PRs and 1,305 Discussion records with complete pagination and no
warnings (2026-10-15 16:52--16:55 UTC). James Reed's independent
[18-word logical audit](https://github.com/CrocSwap/integer-mult-bounds/discussions/2644)
corroborates the unchanged word's logical/frame/invoice checks and explicitly
excludes physical precision. The newer
[PR2662 endpoint fusion](https://github.com/CrocSwap/integer-mult-bounds/pull/2662)
and Discussions2646/2647 intrinsic bridges have different instruction/boundary
contracts; this package makes no precision claim for those successors. The
audited PR2586 head and canonical main were unchanged at the final checks.

## Open next questions

- Can the sufficient grid be tightened by evaluating the actual relative
  charts and same-source cancellations? First resolve the slope-ten self
  terms and the slope-nine quarter terms; the current termwise certificate
  deliberately leaves that cancellation unused. This would reduce a caller's
  storage allowance, but no implementation currently requires the optimum.
- Can completed native children meet this exact boundary contract, or can
  their actual rounding defects be propagated with a valid disposal rule?
  First bind the chosen child precision and private return operation to this
  exact word. Native internals and strict rounded erasure are the blockers;
  the exact-grid proof does not remove them.

## Provenance and credit

Base: canonical main `b4560d9e7216f72b73c5aa940ac099c05e33ccf9`, priority
revision 5. [Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2649).
The independent-verification task draw is retained, with the scope change
from ledger/moment checking to the physical caller-grid obligation recorded
in `TASK.json`. `DEPENDENCY.json` records exact PR2586 Git blobs and SHA256s;
`WORD.json` and `PREDECESSOR.md` are byte-identical retained inputs. Main
provenance and chart-definition pins are in `SOURCES.json`.

The construction and its local bill belong to **ywz65 / PR2586 / PR2497**.
The boundary distinction and final witness belong to **PR2551**; the
complementary-frame idea to **Nick Petalas / PR2550**. Credit Nick Petalas's
**PR2549**, Adam Gall's **PR2096** and the **PR2603 QQ16 component-grid**
precedent for the distinct precision methods. Retain Ross Richardson,
commdata2338, Hiroki Kumazaki, Philippe Van Velzen, Chafik Boukhalfa / PR1991,
Rohan Arun / PR1972, Adam Gall / PR1940, Josie Elliston / PR1071,
Ali Romman / PR1125 / PR1862, icekylinx / PR531, and the original compiler,
interpreter, geometry and correction lineage credited in `PREDECESSOR.md`.

New proof, independent replay and transient witness prepared for **Arham
Tahir**, with substantial **OpenAI Codex** assistance. Apache-2.0. No separate
human, proof-assistant, native-compiler cold replay or maintainer review is
claimed.
