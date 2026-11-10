# Independent compiler/scalar review

Prepared for @CubeJerry by a separate OpenAI Codex research worker. This is
an AI mathematical/source review, not human review or formal verification.
The author package is `research/compiled-root-clifford-precision`, based on
canonical `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## Independently checked source boundary

I read the actual `FINITE-PRECOMPILATION.md` sections 3–6, chronological
`p7-TENSOR.md` sections 1–3, the lockstep `executor.py` planning and execution
methods, and CrocSwap/integer-mult-bounds#6878's full occurrence construction
at `41febf890fbbb852c6059d4c0cc8c593ae9dfa5c`. These are the exact source paths
and commits recorded in the package manifests. I did not use the compiler's
assumed precision/tape conclusion to establish the new precision implication.

An independent literal read of CrocSwap/integer-mult-bounds#6030's current
WORD, SHA256 `7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f`,
found 18,404 ADD, 861 SCALE and 23 COPY instructions. Every scalar denominator
is a power of two at most 16; absolute numerators are at most 16; every COPY
coefficient is 1. The current RESULT, SHA256
`84fcbe2a0b64307b5703c363408042bdd91555b0419509aa50daa43b3b1924ad`,
sets chronological power 1024 and symbolic N to `2^65807000000000`.
Raw targets include rank 1: separation is applied only after strictification.

Integer batch clearing creates distinct field copies. Its rational leaf-cost
formulas do not introduce payload divisions. Chronological products preserve
the exterior scalar coefficients; only the operators and their absolute
phases receive their actual column multiplicities. Completion, splitting,
complements and exits add positive jobs and restored whole-field adapters.
The separate BIT rational-cover grammar is not used by this conclusion.

The permitted exchange `x+=y; y-=x; x+=y; y=-y` has intermediate states
`(a+b,b)`, `(a+b,-a)`, `(b,-a)`, `(b,a)`. Its temporary coefficient mass is
at most 2, its denominator debt is zero, and its completed endpoint resets
to a permutation. One factor 2 is valid only with the stated prohibition on
interrupted/nested swaps and consuming unfinished fields.

## Contribution paths and compiler depth

For a raw prefix `y_i=sum_j b_ij V_ij x_j`, the published current caller's
bound `sum_j |b_ij|<=8500`, `b_ij in (1/16)Z` gives mass at most `8500 M`
and debt at most `delta+4` when every actual entrance expansion has mass
at most M and debt delta. This triangle-inequality composition includes all
roles and correlated centers. Nested source slots retain their actual
entrance expansions; only original root inputs begin with mass 1.

Completed independent positive endpoints reset to their entrance expansion,
not to zero root debt. Parallel unit count and past completed units therefore
do not multiply the active contribution-depth bound. This uses the all-column
endpoint theorem, rather than an integral local chart alone.

The actual compiler completes complements before its flow, suspends each
class while its child/exit group finishes, and never advances that parent to
its next paid round early. At rank n, there are at most
`L=1+floor(log2 n)` classes per path. A chronological v-fold product contributes
at most v unfinished raw contexts per class; simultaneous copies are distinct
roles, not extra serial depth. This yields the stated max-over-complement/exit
recurrence for K, distinct from the owned-bank inventory recurrence.

I independently checked the strengthened bound against actual source ranks.
For `rho=(m-1)/m`, source complements satisfy `n-s<rho*n` because `s>n/m`.
Deepest exits satisfy

    e/n <= (r_max/m)*(r_max/k_min)^G <= rho,

using `m*k_min^G<=n` and integer `r_max<k_min<=m`. The source has only deepest
exits in this separated regime. Fractional descent is credited to
CrocSwap/integer-mult-bounds#4586; its numerical-context use is new here.
Bernoulli gives `rho^m<1/2`. A chain with mL+1 positive nodes would have mL
descents and terminal rank `<2^-L*n<1`, impossible. Thus **including its root**
the chain has at most mL nodes. Each contributes at most vL contexts, proving

    K(n) <= v*m*(1+floor(log2 n))^2.

This argument explicitly resolves the root-node/off-by-one issue. Zero-rank
complements and elementary bases contribute no raw contexts.

## Explicit current format

With `m=145^1024`, `H=65807000000000`, independently computed
`K_star=1024*m*(H+1)^2` has 7,455 bits and 2,244 decimal digits. Its decimal
SHA256 is `e507a371505ade190c0908fbe51c13b17653077642dfae07f8c17f3bf8cad383`.
I did not construct N. Since `32*K_star<2^8299<2^H`, for
`ell=floor(log_N d)`, `t=K_star*ell` one has `32t<d`, including ell=0.
For ell>=1 this follows from `ell<=N^(ell-1)<=d/N`.

Integrality now gives `d>=32t+1`, so `floor(d/2)>=16t` and
`floor((d+1)/2)>=16t+1`. These inequalities prove, with the small d=1 case
included, that the detailed required grid `p+ceil(d/2)+4t` is at most p+d
and the required magnitude exponent `h+ceil((d+1)/2)+14t+1` is at most h+d+2.
After raising the grid, the signed width must be recomputed: the stated
`F=p+d`, `W=p+h+2d+3`, temporary `W+6`, is sufficient. W is **per component**;
a complex record contains two W-bit components plus actual framing.

## Scope and evidence

The fixed-root Clifford invariant must retain ancestor remainder axes.
Only complete external ROW fibers may be selected; active-coordinate
projection is excluded. A partially written field needs component bounds,
not an incorrect assertion that its masked whole vector is Clifford. C pair
numerators are formed completely before exact division by two. Under those
types, the scalar/depth argument composes with the independently reviewed
Gaussian-dyadic root denominator. This review does not admit arbitrary
implementations with the same completed endpoint.

My literal-source census and symbolic swap computation ran independently
under ordinary and optimized Python; their exact receipts agreed. The method
did not import the author's verifier. I then read the author's complete
proof, source checker and bounded compiler/algebra controls. Those finite
tests corroborate source scheduling and discriminators; the inequalities
above supply the universal review argument.

Earlier CrocSwap/integer-mult-bounds#2287, CrocSwap/integer-mult-bounds#2390
and the finite-template closure already establish O(p) format existence.
This result supplies an explicit current-source implication and sharper
context accounting, not that first existence result. Unspecified current
preprocessing/normalization joins, actual native internal precision, ownership
and erasure implementation, full tape tariffs and outer recovery stay open.
The proof-state expansion is not a proposed runtime computation.

One source-binding issue identified in review was authenticating bytes and
then reopening the executor/RESULT/WORD for consumption. The author corrected
this: immutable cached authenticated bytes now feed every such parse/compile.
I read the correction, including the protected-path re-read discriminator and
unconditional restoration of the temporary file-access guard. No source or
numerical assumption was weakened. Final scientific authentication follows.

## Numerical 05-layers wrapper addendum

I independently read `upstream/build/sections/05-layers.tex`, blob
`5ce8b3c83c455f221bb84858a97230b0285644aa`, before reviewing the added
specialization. Its first-q0 individual C preprocessing, complete suffix rows,
completed padded-zero return and final `b^D S_D C^D S_D` macro match the
stated scope. For q processed bits, entrance bounds
`p'=p+ceil(q/2)`, `h'=h+ceil((q+1)/2)` absorb into the global p+D grid and
h+D+2 magnitude bound. Across sequential pieces all remaining R bits must
stay one reference factor; completed pieces add Clifford factors, not scalar
debt. The source's closed unit disk is admitted using h=1.

The final exactness has a source-specific parity reason: a=i*b, so every
literal tensor C^D entry is a fourth-root phase times b^D. After the source's
floor(D/2)-bit shift, even D needs no further denominator. For odd D the
real/imaginary integer numerators have equal parity, and the complete
optional-b numerators `(A+B,B-A)` divide by two exactly on p+D. This is not
true of arbitrary values merely lying on the smaller C-grid. The six-bit
temporary margin covers those full numerators; termwise rounding is excluded.

I read the added 65-dimension entry/phase, preprocessing and off-image parity
controls. They match this numerical claim and are expressly finite evidence.
The specialization does not assert that the current front/back-reservation
dispatcher supplies every selected-axis preprocessing job. Physical movement,
owned lifetime, current reservation and complete tariffs remain separate;
final Q_p truncation is a paid, intentionally lossy output operation.

## Reviewed scientific snapshot

At 2026-11-08 23:55 UTC I authenticated the following final scientific
bytes and the author's registered normal/optimized receipt. This is a source
review disposition plus byte authentication, not a second author replay.

| File | SHA256 |
| --- | --- |
| PROOF.md | `42606a73acf3313f39e6055bf2409974c528c12a3092d13ca09f206bbbd010a1` |
| verify.py | `4b228f8e9a19a82f3b5e07f88507d68529f283b8cdb5b98020230746c83afec1` |
| RESULT.json | `4fc6f2174e4776cf33fb7b9013ae2d70dd675f802fdf76d49ab00a40d7049995` |
| SOURCES.json | `8824122668eac5ea86577fb48f1c83251c45eb3d6771361bed7a6818c3eab445` |
| DEPENDENCIES.json | `c2c2caa08f9a9d75bbf4d9c62c45c42c2d1e1075b9c162888b19a1c0a6846799` |
| VERIFY.json | `e9cb34b4b47e74df1cf2b6b1b7eef4c2bed9e0e06248eee8fe45af976e5c31e1` |
| RECEIPT.json | `f83abaafa13b332c627788682d4c2c49a951843593b3e69353f85f4c4e287be8` |

No remaining mathematical or source-binding blocker was identified within
the declared ideal/compiler scope and exact numerical 05-layers specialization.
No current physical admission, unspecified reservation/normalization join or
multiplication exponent follows. Any later scope expansion needs its own review.
