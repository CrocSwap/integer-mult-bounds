# Independent review of the spectral downset precision selector

**Disposition: accepted as a scoped conditional theorem.** No mathematical
correction to the frozen candidate is required. This review covers the
sharper selector in `norm/wave2-sharp-b`, not a replacement of the Full
compiler's allocation or its component admission rules. The earlier cut and
relative-interval review is a named dependency. The publication status can
now record separate model-assisted review; human or proof-kernel acceptance
is not asserted.

## 1. Reviewed objects and exact scope

The reviewed candidate has these SHA-256 identities:

| Object | SHA-256 |
| --- | --- |
| `PROOF-DRAFT.md` | `0501a6a9a5f467fff4c998606965babc8157e74d98cf33b93f71fb10674d57bb` |
| `precision.py` | `9c3e99219f741c5b08c0628c30784cf72c60b4421beae3373fa976aeffcd8e20` |
| First-wave cut/interval `PROOF.md` | `e942012e66adc2d696cde3fedd6ae9c73df98e77a71b16e5004f5a74ccdfaa07` |
| #8093 parent `PROOF.md` | `26e4e214f0a5785c1d1414561465bb49a3248f9e6f59f6b514eb95a887bdfe2f` |

The canonical source base is
`e54523517d0f03e58352e647c403a5af3e525a57`. The #8093 publication head is
`13561dbdf4971a7ae0901d2f43df8de3981e94a5`; its #7849 source head is
`3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd`. The decisive credited downset
theorem is Nick Petalas #4852 at
`8acf04b4c42fe75894a87a3b2d37ddb68e96a798`, retained SHA-256
`1e59ae73eb142ec3d4579ce98244295b733896afca0fec3693906fc6def26d3f`.
The source manifests retain the earlier compiler and allocation credits,
including Jose Manuel, Vlado Vojdanovski, Chafik Boukhalfa, Ali Romman and
Brian/JoyboyBrian. In particular, #4977's allocation substitution is not
claimed again here.

For `d>=1`, `ell_i>=1`, `2<=r_i<=t_i=2^ell_i`, `p>=1`, and `L=sum ell_i`,
the accepted selector is

```
E = ceil(257L/2) + 1354d
A = 20L + 303d
J = 20000(d+1)(max ell_i+2)^6
C = 4J(d+1)^2+d+1
P = 4p+A+2E+bit_length(C).
```

Under the parent phase, source rank, exact represented-input native H,
Fourier and recovery interfaces, `Grid(P)` and the unchanged `P+8` producer
target give raw coordinate error strictly below `2^(-4p)` on the complete
padded input half disk. This is an all-size statement under those premises.
It does not certify a new multiplication recurrence, remove any selected
assumption, reprice helper/native work, or change kappa.

## 2. The spectral hypotheses apply to this source matrix

The parent establishes, for each external `P>=1`, that the actual stored
identity-padded root T satisfies `||T||_2<2` and that every original leading
section has inverse norm at most `4r<=4t`. Strict accretivity survives both
the rational root-column error and the identity padding. Restriction to a
leading coordinate subspace preserves the same positive Hermitian lower
bound. Thus `Lambda=2`, `Q=4t`, and `chi=Lambda*Q=8t` are legitimate
spectral estimates for the actual rational matrix used by the Full factory.

The component guards are stronger statements and remain distinct:
`lambda_c=max(1,norm_upper(T))` and `Q_c=8tr`. A rational orthogonal rotation
with entries `3/5,4/5` has spectral norm one but component row/column envelope
`7/5`; the independent control rejects their conflation. The source
`compile_padded_root` still computes the original component bounds. No
spectral number is substituted into that call.

The #4852 argument is valid for every complex matrix with the stated leading
inverses and every binary contiguous-interval tree. It does not require
Toeplitz structure. Its finished/untouched partition gives the ordered
identities

```
P = E_B U_B^-1 U,
P^-1 = U^-1 U_B E_B^-1.
```

For a finished interval `[a,b)`, the forward block row is a rectangular
original Schur row, with bound `Lambda+Lambda^2 Q`. Its inverse block column
is a restriction of `T_b^-1`, with bound Q. For an untouched interval, the
forward tail is a restriction of `T_b^-1 T[:b,b:]`; the inverse top block is
`-T_a^-1 T[:a,[a:b]]`. Their whole row/column norms are at most
`sqrt(1+chi^2)`. Summing squared forward row bounds, and applying
Cauchy-Schwarz to inverse block columns, yields the common
`2 sqrt(t) chi^2` envelope. This handles the source's non-Toeplitz padded
roots directly. The separate displacement-rank premise remains necessary
for compiling their children.

Consequently

```
B_new = 2^7 t^3 >= 2 sqrt(t) (8t)^2.
```

The original allocation has
`B_old=256t^3(lambda_c Q_c)^12 >=256t^3>B_new`. At the same external P,
the original eta therefore gives
`(3t-2) B_new^2 eta <= (3t-2) B_old^2 eta <=1/4`.
The original endpoint error theorem at target `P+8` continues to apply.
There is no need to derive the endpoint error by reallocating with B_new.

This distinction is essential: at a fixed P, the word, child targets and
coefficients are unchanged; selecting a different external P regenerates
them through the same source rules. The frozen candidate explicitly makes
that distinction and does not claim identical coefficient bytes across
different selectors.

## 3. The smaller child cap follows from actual argument forwarding

At a full split, each ideal upper or lower coupling is a restriction of an
original leading solve, respectively of `T_b^-1 T[:b,J]` or
`T[J,:b] T_b^-1`. The source reference shears thus obey
`||K||,||L||<=chi`, without multiplying a local Schur matrix bound by a
separate Schur inverse bound.

For a child X of side m, let `E=X-ZXZ^T`. Since the shift Z has norm at most
one, `||E||<=2chi`. For every complex row or column, its component l1 norm
is at most `sqrt(2m)` times its Euclidean norm. Therefore the actual value
returned by `generator.prepare` satisfies

```
be <= sqrt(2m)||E|| <= 2sqrt(2m)chi <=4t chi=32t^2.
```

The literal source bridge is decisive. `Full.shear` assigns
`items, displacement, be, heights = prepare(...)` and calls

```
generator_allocation(m, len(items), be, 1,
                     self.bound["child_target_bits"], 0).
```

It does not pass the old full-level displacement envelope in place of be.
The separate source-syntax oracle verifies that assignment and call, the
exact component-envelope expression, the child formulas, and the unchanged
parent target. The complete source files are also authenticated by SHA-256
and Git blob identities. This syntactic audit supplements the mathematical
source review; it is not a general data-flow verifier.

Using the retained rank bound `rank<=2ell+8<=5t` gives

```
alpha = 2 rank m be <=320t^4,
KG = 2m+16m be <=514t^3.
```

The first-wave review supplies the actual four-way child fragment estimate
at arbitrary matching subsets:

```
H_gen = max(3200m^3,2+2KG) (10+4alpha+2KG).
```

Its source factory is overprecise for the new analysis; its allocated phase,
triangle and multiplier precisions remain sufficient. For `t>=1`,

```
3200t^3-(2+1028t^3) =2172t^3-2 >=0,
2318t^4-(10+1280t^4+1028t^3)
  =10(t^4-1)+1028t^3(t-1) >=0.
```

Hence `H_gen<=3200*2318*t^7=7,417,600t^7<2^23t^7`.
The dyadic rank comparison follows by induction from equality at ell=1;
doubling `5*2^ell` grows at least as fast as adding two to `2ell+8`.

An ideal leaf pivot has modulus between `1/Q` and
`U=Lambda+Lambda^2 Q=2+16t<=18t`. The same stored pivot differs by at most
eta, and the original margin gives
`eta<=1/(2Q_c)<=1/(2Q)`. Its modulus and reciprocal are bounded by `U+1`
and `2Q`. Both are below `H=2^23t^7`. These are inverses of the same stored
pivots; no independently rounded inverse is introduced.

## 4. All lowering and norm conversions are retained

Apply the accepted first-wave source-cut theorem with
`L0=max(1,Lambda,Q)=4t`, and its relative-interval theorem with B_new and H.
The resulting exponents are:

| Boundary | Accepted cap |
| --- | --- |
| Full source prefixes/suffixes and their inverses | `K=2 L0 B_new H <=2^33 t^11` |
| Any Full source interval and its inverse, including one gate | `G=2 B_new^2 H^2 <=2^61 t^20` |
| Routed root prefix and inverse prefix | `4 K 64^40 (2G) <=2^337 t^31` |
| Complete one-axis prefix and inverse prefix | `(2t)^2 (2^337 t^31)^2 =2^676 t^64` |
| One joined axis-diagonal scalar | `64^40 (2G) <=2^302 t^20` |

The parent pivoted sixteen-H expansion has one pivot factor bounded in both
directions by `2G`; every ordinary factor and inverse is at most 64. Its
literal expanded word has 38 ordinary factors, and retaining 40 is safe.
Joining adjacent diagonals does not create an additional factor outside this
partial-product bound. Matchings are direct sums, so no pair-count factor
appears. Completed Beneš switch rows are permutations; one partial switch
and its inverse cost at most four.

Each axis has two root passes and two exterior diagonals with forward and
inverse bounds `2t`. Distinct axes tensor and commute. The width-class and
pack schedule therefore selects one prefix for each axis, not a product of
multiple prefix allowances for the same axis. Retaining `2^d` for a partial
H pack at each interval end yields spectral interval cap

```
2^(1354d+128L).
```

There are `2^L` physical coordinates, including padding. The induced
infinity norm is at most `sqrt(2^L)` times the spectral norm. Thus the common
external prefix and interval allowance is `R=M=2^E` with the stated
`E=ceil(257L/2)+1354d`. This conversion must be retained even when the
logical transform has fewer true coordinates.

## 5. The coefficient cache and rounding bootstrap close

Let `b_i=2^302 t_i^20`, `F=product b_i=2^(302d+20L)`, and `v=2^-P`.
An individually rounded factor differs by at most v and has modulus at most
`2b_i`. Telescoping the exact products bounds table-entry error by
`d 2^(d-1) F v`. A rounded right-associated product adds at most d-1
nonzero multiplication errors, each propagated by a product of preceding
rounded factors. Their total is at most `(d-1)2^(d-1)Fv`. The candidate's
`2d 2^d Fv` coefficient-error cap is therefore conservative.

The source odometer keeps precisely this bounded expression. At every
record, suffix k is a right-associated rounded product of the current
factors k through d-1. A carry resets indices below j and increments index
j, then recomputes suffixes j through 1. Higher suffixes retain unchanged
arguments. The source multiplication-by-one shortcut makes the bottom
suffix multiplication exact. Thus no error is charged once per earlier
record. Zero factors need no special division or ratio update.

The independent expression-tree oracle executes the pinned
`product_diagonal` body with symbolic factors and checks every current
mixed-radix coordinate against a freshly constructed expression. A mutated
subject that skips suffix refresh fails at exactly the two later records of
the 2-by-2 control. A separate numerical oracle uses exact rational complex
targets and the pinned Grid arithmetic, including its actual tie convention.
Both coefficient error and the final multiplication by represented data are
checked on heterogeneous sides and zero-factor cases.

The final data multiplication adds at most v. Since
`2d+1<=(d+1)^2`, the local defect is bounded by

```
epsilon(1+||z||_infinity),
epsilon=(d+1)^2 2^(-P+A), A=20L+303d.
```

A native H has zero error under the inherited exact represented-input
contract. Counting it as a separate step allows a preceding diagonal's
roundoff to propagate through the appropriate interval. The unchanged
source matching bound is

```
D(x)=32x^4+256x^3+584x^2+288x+1.
```

The exact coefficient list, from constant to degree six, of
`20000(x+2)^6-4D(x)(12x+11)` is

```
1279956, 3827280, 4760480, 3160704, 1186304, 238464, 20000.
```

All are positive. It follows for all allowed d and x that
`2+4dD(x)(12x+11)<=20000(d+1)(x+2)^6=J`. This is a universal polynomial
comparison, not a fit to sampled side widths.

The parent root-column and exact endpoint synthesis estimates are unchanged.
Their tensor bias is absorbed by
`beta=(d+1)2^(-P+E)`, since `E>=d-1+L/2`. To see the nonlinear bootstrap
without circularity, suppose earlier computed states have norm at most
`1+2R`. Variation of constants and the interval bound give numerical error
at most `JM epsilon(2+2R)`. If `JM epsilon<=1/4`, adding the ideal stored
prefix's input bound `R/2` gives at most `R+1/2`, which lies strictly inside
the proposed state allowance. This closes induction from the half-disk input.

Put `m=bit_length(C)`. The selected P yields

```
JM epsilon = [J(d+1)^2/2^m] 2^(-4p-E)
           < (1/4) 2^(-4p-E),
raw error <= C 2^(-P+A+2E)
          = [C/2^m] 2^(-4p) <2^(-4p).
```

Both strict inequalities follow from `4J(d+1)^2<C<2^m`.
Changing the selector by one bit loses this particular strict certificate
because `2C>=2^m`; that control does not claim the actual algorithm then
fails. Opposite signs follow by input/output conjugation of the same
forward program. Conjugation is an isometry; no oddness of the source's
rounding tie rule is needed.

## 6. Selector comparison for every dimension

Expanding `A+2E` gives

```
P_new=4p+277L+3011d+(L mod 2)+bit_length(C).
```

The #8093 selector has linear part `4p+1361L+4746d+(L mod 2)`, with the
same C. The exact saving is `1084L+1735d` bits.

For the original source selector, put `q=J(d+1)` and
`m_q=bit_length(q)`. Since `d+1<=q`,

```
C=(d+1)(4q+1)<=5q^2<2^(2m_q+3).
```

Therefore the original source P exceeds P_new by at least

```
32491L+193597d+2m_q+61-(L mod 2)>0.
```

This proves dominance for arbitrary d and widths without enumerating
dimensions. At `p=72`, widths `(4,5)`, the values are 8,842, 22,068 and
688,620 for new, #8093, and original source selectors respectively. These
are sufficient bit-count comparisons. No measured time, storage or optimal
precision claim follows from them.

The local numerical theorem accepts every positive axis count. The outer
multiplier wrapper can retain additional geometric restrictions on its own
arguments. Public-grid recovery also retains true-volume, scale, no-wrap,
CRT-character and native supplier premises. Under those interfaces the
parent `144/B_radix^2<1/2` conclusion remains available for
`B_radix>=32`.

## 7. Independent evidence and reproduction

`independent.py` imports neither author checker, compiler factory nor an
earlier reviewer oracle. It authenticates 24 retained-origin records, the
two dependency proofs and the frozen candidate; the two subjects executed
are the proposed precision API and AST-extracted pinned Grid/odometer bodies.
It uses integer exponents, exact Fractions and symbolic expression trees.

The normal and optimized runs produce byte-identical evidence:

* 113 selector cases, including width `10^80` without instantiating a
  `2^width` array, mixed large widths, and d=129;
* seven invalid input cases, including Boolean precision/widths;
* 254 symbolic cache records and 762 numerical complex rational records on
  grids of 2, 5 and 11 bits;
* 507 zero-factor numerical records and a broken-carry rejection control;
* exact source argument forwarding, complete exponent recomputation and a
  positive-coefficient stage-count certificate;
* component/spectral and whole-inverse/leading-inverse negative controls,
  plus a non-Toeplitz, identity-padded strictly accretive rational fixture.

The author separately retained bounded actual-source root probes, including
`r=3<t=4`, in the candidate evidence. Those probes were authenticated but
are not counted as independent reruns here. The universal conclusion rests
on the source bridge and written derivation above, together with the named
predecessor theorems.

From the session workspace root:

```sh
python3 -I -W error -B dyadic/selector-review/independent.py --candidate norm/wave2-sharp-b --cuts norm/package --parent /workspace/scratch/5b0914ccc34e/publish-precision/research/direct-circulant-production-precision --output dyadic/selector-review/EVIDENCE.json
python3 -I -O -W error -B dyadic/selector-review/independent.py --candidate norm/wave2-sharp-b --cuts norm/package --parent /workspace/scratch/5b0914ccc34e/publish-precision/research/direct-circulant-production-precision --output dyadic/selector-review/EVIDENCE-OPTIMIZED.json
```

The command paths are relocatable through the four explicit CLI arguments.
The receipt contains exact source identities and no machine-dependent
timestamps. Source review, finite arithmetic checks, conditional all-size
proof and a complete multiplication theorem remain distinct evidence types.

Prepared independently for Jerry Chen / @CubeJerry with substantial OpenAI
assistance. No author package was modified during this review.
