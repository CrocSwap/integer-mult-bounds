# Independently verify the R480 packing optimum through a=1/2

**Independent verification and interval extension; no new numerical optimum
or kappa.** Ali Romman's incorporated [PR1129](https://github.com/CrocSwap/integer-mult-bounds/pull/1129)
already proves the R480 fixed-inventory packing optimum and supplies an
attaining T37 construction. This package adds a separate standard-library
verifier, binds the same model to selected PR1094's T16 inputs, independently
checks the predecessor's fine root bracket, and proves the fractional optimum
**uniformly for every real `0<a<=1/2`** by a square-root/concavity argument.

PR1129 proves its supporting inequalities over the narrow root interval.
The related [U8 uniform audit](../u8-supporting-uniform/README.md) proves the
same signed-price support through `a=1/3`. Here all 1,163 pattern inequalities
are checked at `a=1/2`, both by directed square-root intervals and independently
by rational squaring; concavity covers the continuum. The numerical optimum,
the nine-pattern basis, and the replica divisibility obstruction are credited
predecessor results, explicitly reconciled by the checker.

The independently verified existing primitive-root bracket is

`0.001676905273619680861300 < a_root < 0.001676905273619680861301`.

Its retained balanced cap is about `kappa < 0.00167409796990539051`, less than
**0.085958%** above selected PR1094. This restates the existing fixed-inventory
limit; it is not an improvement over PR1129. The prior attaining T37 owner
construction and its outer-grid kappa are not replayed here.

Fix the selected local word, live family stock, whole-helper width inventory,
child capacities and existing disjoint-reservation contract. Chronology,
family compatibility and integrality of pattern multiplicities are relaxed;
every physical packing under this contract remains feasible in the broader
model. Changing these inputs, splitting/reusing reservations, or changing the
outer conversion is outside the statement. No optimizer is needed for replay.

## Fixed source model

Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. [SOURCES.json](SOURCES.json)
pins the selected certificate, manifest, SPEC, PLAN, owner map and replay receipt.
The selected pointer and task catalogue are historical Git provenance.

From PLAN's 288 replica/child windows and 112 ports, and its 144 per-call width
lists cross-checked against SPEC:

| Bin capacity | Number of bins | Helper width | Number of helpers |
| ---: | ---: | ---: | ---: |
| 8 | 10,752 | 4 | 8,064 |
| 16 | 7,168 | 5 | 4,608 |
| 32 | 7,168 | 7 | 4,320 |
| 48 | 7,168 | 8 | 17,568 |
| | | 9 | 34,560 |

There are 69,120 positive-width helper occurrences: 480 per call. Their total
width is 537,120; total bin capacity is 774,144, leaving idle mass 237,024.
Each occurrence reserves one disjoint block inside one child. A bin's remaining
rank is its capacity minus all reserved widths. Reusing a reservation across
occurrences, splitting helpers or transferring axes between children changes
this model and is outside the bound.
The fixed paid local profile per call is
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`. It is a reused, source-bound
supplier input, **not** a new replay of the scalar or Clifford operations.

The checker independently recounts the owner rows, their widths, call/window
membership and contiguous bin prefixes. The resulting selected idle histogram
is `{1:2276, 3:377, 7:7, 48:4866}`. Adding the 144 local profiles matches the
selected assembly and replay profile, with rank mass 1,041,408. These checks
bind the relaxation to the named finite inputs; physical correctness of the
fixed route and its capacities is inherited from the selected construction.

## The relaxation and its certificate

For each capacity C, enumerate every nonnegative integer vector
`n=(n4,n5,n7,n8,n9)` with `sum w*nw <= C`. A pattern leaves residual
`r=C-sum w*nw`. There are exactly **1,163** patterns. Assign nonnegative real
multiplicities x to them. Require the four capacity inventories and five
helper inventories above exactly. Minimize `sum x*r^p`, where `p=1-a` and
the residual-zero cost is zero. The local paid cost is fixed and added later.

The following feasible point works for the whole stated exponent interval:

| Capacity | Helpers in one bin | Residual | Multiplicity |
| ---: | --- | ---: | ---: |
| 8 | 8 | 0 | 10752 |
| 16 | 8+8 | 0 | 52896/37 |
| 16 | 7+9 | 0 | 150304/37 |
| 16 | 4+4+8 | 0 | 62016/37 |
| 32 | 7+7+9+9 | 0 | 4768/37 |
| 32 | 5+9+9+9 | 0 | 4608 |
| 32 | 4+9+9+9 | 1 | 89952/37 |
| 48 | empty | 48 | 180832/37 |
| 48 | 4+8+9+9+9+9 | 0 | 84384/37 |

Every one of the nine inventory equalities is checked over rational numbers.
Thus its idle cost is `89952/37 + (180832/37)*48^p`.

For a dual certificate assign each inventory row a price `(A+B*48^p)/37`
using the integer numerators below. Negative prices are allowed because the
inventory constraints are equalities.

| Row | A | B |
| --- | ---: | ---: |
| capacity 8 | 8 | 6 |
| capacity 16 | 16 | 12 |
| capacity 32 | 32 | 24 |
| capacity 48 | 0 | 37 |
| helper 4 | -4 | -3 |
| helper 5 | -41 | -3 |
| helper 7 | -19 | -5 |
| helper 8 | -8 | -6 |
| helper 9 | 3 | -7 |

For any pattern let alpha and beta be the sums of its corresponding row
coefficients, including division by 37. Dual feasibility asks for
`r^p >= alpha + beta*48^p`.

1. At p=1, all 1,163 inequalities are exact equalities:
   `r=alpha+48*beta`.
2. At p=1/2, **20** patterns are symbolic identities with
   `(r,alpha,beta)` equal to `(0,0,0)`, `(1,1,0)` or `(48,0,1)`.
   The remaining **1,143** inequalities are strictly positive, checked with
   outward integer-square-root intervals. The least certified gap exceeds
   0.298. A separate test checks all signs by rational squaring of quadratic
   radicals, without calling that interval engine.
3. Put `t=48^p`. For 1<=r<=48, `r^p=t^(log(r)/log(48))` is concave in t.
   Subtracting `alpha+beta*t` preserves concavity. Nonnegative values at
   `t=sqrt(48)` and `t=48` imply nonnegativity throughout that interval.
   The r=0 case is affine and obeys the same endpoint argument.

This proves every dual inequality for `1/2<=p<=1`. Multiplying by nonnegative
pattern multiplicities and summing proves the lower bound. Every pattern in
the displayed feasible point is a symbolic equality, so its cost equals the
dual bound. Consequently the relaxation's optimum is exactly

`89952/37 + (180832/37)*48^(1-a)` for `0<a<=1/2`.

The optimum cannot be attained by integer pattern counts. For `0<a<=1/2`,
every non-symbolic pattern has a strict dual gap (including by the positive
chord in the interior). Thus an optimum can use only the 20 symbolic patterns.
Their constant dual coefficient counts rank1 residuals, so the inventory
equalities force exactly `89952/37` such residuals. This is not an integer.
The corollary gives strict nonattainment, not a quantitative integrality gap
or a physically realizable near-optimum.

## Complete bill and independent exact arithmetic

Add all local children and normalize by the fixed width and live stock:

`F(a) = [144*sum local_nr*r^(1-a) + 89952/37 + (180832/37)*48^(1-a)] / [14336*73^(1-a)]`.

Every admissible packing's native moment is at least F(a). F is strictly
increasing. An independent coarse bisection brackets its root by

`0.001676905273619 < a_root < 0.001676905273620`.

Both coarse endpoints have strict signs. The checker additionally accepts
PR1129's pinned finer lower endpoint and rejects its upper endpoint, using the
same newly implemented arithmetic. Their unnormalized gaps are approximately
`-1.35014e-18` and `+1.69049e-18`; exact rational enclosures are in
[RESULT.json](RESULT.json). Failure at the upper endpoint excludes every
larger saving by monotonicity of each packing's bill.
It does not round the predecessor's receipt or import its moment engines.

The new power implementation brackets a rational exponent on a 160-bit dyadic
grid. It computes binary half-powers with outward integer square roots at
256 fractional bits, then multiplies with directed rounding. All decisions
use integers and Fractions. Refinement to 192/320 bits encloses both root
endpoints more tightly with the same signs. Sixty-four small rational-power
cases are also checked by exact integer-power comparisons. This is independent
code, not a new numerical method or a call into the existing moment engines.

As positive/negative endpoint fixtures, the same implementation accepts the
selected complex lower endpoint and rejects its next `10^-24` grid point.
No bit surcharge is applied to this native complex moment.

## Reproduce and coverage

From the repository root, Python 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/selected-t16-pattern-dual
```

Expected: `PASS_SELECTED_T16_PATTERN_DUAL`, 1,163 patterns, **11 rejected
semantic controls**, **nine test groups**, then the registered package pass.
An optimized standalone run is also supported:

```sh
python3.12 -I -O -B research/selected-t16-pattern-dual/verify.py
```

Controls include a dual forgery preserving rank mass, a missing bin, an
overfull pattern, negative multiplicity, a mass-preserving helper substitution,
an unjustified exponent range, owner undercharging, a prefix gap and a duplicate
helper. Tests additionally reject source-byte drift, omitted local work and
an unresolved numerical sign; independent Cartesian enumeration checks domain
completeness. `verify.py --write` intentionally regenerates only this package's
receipt. No predecessor artifact is modified.
Four further predecessor-claim mutations in the tests reject wrong pattern
scaling, a changed signed price and either invalid fine root endpoint.

Discovery used Python 3.12.13, SciPy 1.17.0 / HiGHS and NumPy 2.5.4 at
`a=0.0016819`, minimizing the equivalent residual excess
`r*expm1(a*log(48/r))/a` (zero for r=0). The optimizer nominated the nine
patterns; rational inventory equalities, all dual inequalities and all final
moment decisions are checked independently without SciPy. Neither optimizer
success nor its tolerances are acceptance evidence.

## Scope, overlap and credit

The primary predecessor is **Ali Romman's PR1129**, head
`a007dc2e1cc7ae7e8f7ec1343e8883fe43259f21`, retained as
[r480-owner-optimum](../r480-owner-optimum/README.md). Its certificate, proof
and notice are pinned here. The displayed primal equals its T37 nine-pattern
certificate scaled by `16/37`, which the checker verifies exactly. If s is
the predecessor's signed pattern price and r the residual, our dual coefficients
satisfy `alpha=(48*s+13*r)/925`, `beta=(r-alpha)/48`. This exact identity is
also checked row by row. These are two descriptions of the same supporting
bound, not distinct numerical discoveries. Chafik Boukhalfa's PR795 supplied
the signed prices; his concurrent PR1131 supplied an independent T37 attainment.
woklerx's U8 uniform audit's earlier `0<a<=1/3` argument is also credited.

Josie Elliston's [PR1783](https://github.com/CrocSwap/integer-mult-bounds/pull/1783),
head `691534353b8c5172f5c157e79496686d8c80f196`, gives the fixed-route rank-48
mass relaxation. woklerx's [PR1847](https://github.com/CrocSwap/integer-mult-bounds/pull/1847),
head `17ece863d91f84087a5034af900ef70e424e0296`, adds indivisible-helper patterns,
proves at least 2,448 idle mass below rank48, and prices that mass at favorable
rank44, reporting primitive cap 0.001681977435447. The older PR1129 optimum
is already tighter than both newer screens. The contribution here is an
independent selected-input check and a wider uniform proof, not another
numerical tightening of that known optimum.

Penguin/Maximus Putnam's [PR1685](https://github.com/CrocSwap/integer-mult-bounds/pull/1685)
allows arbitrary idle-rank partitions and has a different feasible domain.
Douglas Colkitt's PR1240 supplies the fixed-word ceiling context. Credit Rohan
Arun's PR1094/987 construction, Jeremy Kothe's packing chain, Hao Yan's T16
controller, and the selected review's retained supplier lineage. Integer-root
moment methods precede this implementation, including PR706 and the independent
[PR1577](https://github.com/CrocSwap/integer-mult-bounds/pull/1577) audit.

The task selector chose `independent-moment`, nonce
`14c8429d797658917dfffd38f0db810d`. [TASK.json](TASK.json) records the numeric
enclosure refinement and overlap limits; [Discussion1885](https://github.com/CrocSwap/integer-mult-bounds/discussions/1885)
records the claim. Source scalar/phase correctness, route geometry, physically
realizable ownership, native compiler, invoice/outer replay, bit H1-H5,
all-size/compiler, precision/tape and analytic obligations are **not newly
verified**. The proof is written and exactly checked in its finite arithmetic
parts, not formalized in Lean. The selected frontier remains unchanged.

Prepared by **Hanson Sun**, with substantial **OpenAI Codex assistance** in
mathematics, implementation, verification and writing. No independent human
review is claimed. New material is Apache-2.0; predecessor notices remain intact.

## Open next questions

- **What is the quantitative T16 integer-pattern gap with chronology still relaxed?** This
  would distinguish the fractional optimum from the best aggregate integer
  packing. Strict nonattainment is already proved above. Start with the nine
  inventory equations and positive reduced costs of the 1,143 non-tight
  patterns to bound how many such patterns integrality forces. A matching
  integer witness or quantitative lower-gap certificate is still needed.
- **Which T16 timing/family constraints tighten the aggregate optimum?** Add
  selected window/role eligibility constraints and seek a short exact dual
  beyond the present pooled model. This would bound the remaining actual
  packing headroom. The blocker is a tractable source-bound formulation with
  whole-family compatibility; a fractional pattern solution alone does not
  supply it.
