# Exact Fourier repairs and the 0.1 outer parameter domain

This is a local investigation at source commit
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`. It supplies two exact operator
identities, a charged recurrence criterion, and an enlarged **arithmetic**
parameter region. It does not supply a new finite supplier or a multiplication
theorem. In particular, it does not remove the selected bit supplier merely
by renaming its address maps as complex operations.

The concrete native-adapter attempt is in [ADAPTER-FUSION.md](ADAPTER-FUSION.md).
The subsequent shared-Walsh-frame attempt is audited in
[CONVOLUTION-FRAMES.md](CONVOLUTION-FRAMES.md): alternative symmetric frames
exist at some cuts, but a specific helper has incompatible carried/read
eigenspaces under the stated fixed-content replacement scheme.

## 1. A genuine Fourier implementation of an address shear

For binary vectors `x,y` of length `f`, write `W_f[x,z]=(-1)^(x dot z)`.
Let `D_xy` multiply the entry at `(x,y)` by `(-1)^(x dot y)`. If `P_xy`
moves `(x,y)` to `(x xor y,y)`, then

    P_xy = 2^-f W_x D_xy W_x.                         (1)

Indeed the matrix coefficient from `(z,y)` to `(x,y)` is
`2^-f sum_t (-1)^(t dot (x+y+z))`, which is one precisely when
`x=z+y`, and otherwise zero. This proof is valid on arbitrary arrays,
with arbitrary spectator fields and arbitrary initial payloads.

Use the Gaussian-dyadic scaled Walsh operator

    J_f = ((1+i)/2)^f W_f = S_f C_f S_f,
    J_f^2 = i^f I,     S_f(x)=i^wt(x).

The native `C_f` and its conversion to `J_f` are the literal operators in
`upstream/build/sections/05-layers.tex`, equations phase-basic-identities.
Equation (1) becomes

    P_xy = (-i)^f J_x D_xy J_x.                       (2)

Thus this repair costs **two complete native children of width f**, plus
diagonal phases. All scalar factors and inverse normalizations are explicit.
There is no irrational arithmetic, truncation, free indexed access, or free
general binary permutation in this identity.

The identity extends to a rectangular block shear `x -> x+B y` by replacing
`D_xy` with `(-1)^(x dot B y)`. The target x can contain t whole slots,
giving two native children of width `t*f`.

### Fusion is allowed, but must follow the actual operator word

Consecutive shears with the same target x and unchanged controls combine:

    (J_x D_1 J_x^-1)(J_x D_2 J_x^-1)
       = J_x (D_1 D_2) J_x^-1.

An arbitrary run of these operations costs two children, not two per row
addition. This also groups all source additions to one target into one
bilinear diagonal phase. If a control changes or an intervening scalar gate
needs a different physical frame, this cancellation requires a new proof.
The verifier includes a changing-target counterexample to unconditional
commutation. Full adjacent Clifford recipes should be composed before
charging their Fourier implementation.

There is a further useful fusion for a complete interchange. On the joint
2f-bit address field let `H_2f=2^-f W_2f`, a real dyadic involution. Then

    SWAP_xy = (H_2f D_xy)^3.                          (3)

At f=1, multiplying the four-by-four matrices proves the identity. Tensoring
over corresponding bit pairs proves it for all f, without assuming that
the input payload array is a tensor product. Also
`H_2f=(-i)^f S_2f C_2f S_2f`. Consequently (3) costs three native children
of width 2f. This is cheaper in an exponent moment than six width-f children:
at saving `a=1/9` its price is multiplied by `2^(-1/9)`.

### Precision and the domain restriction

If each payload is represented by B-bit integer or Gaussian-dyadic scalar
components and `B >= f`, these exact operations use `O(B+f)=O(B)` bits per
component. A Walsh sum adds at most f integer bits; the displayed dyadic
denominators add at most O(f) fractional bits. Bilinear phase evaluation
costs O(f) per record for a fixed-size block matrix, hence O(V) under this
domain. For a fixed finite supplier whose children have a uniform width
contraction ratio strictly below one, the sums of widths along a recursion
path are O(root width). This observation can support a guard
induction once the actual child and scalar schedule is supplied.

For one-bit payloads and arbitrary growing address width, this argument
would expand volume by O(f). It therefore does **not** prove the existing
ordinary-interchange contract on all bit payloads. Nor does an already
proved layer on K-spaced selected axes automatically supply whole contiguous
chunks (K=1): the selected-bit layout domain must also be established.

## 2. The recurrence must include the repair

Let a complete supplier on m selected slots have W productive streams and
native child inventory `h_r`. With all volumes, guards and restorations
properly accounted for, its pure native moment at saving a is

    M_native(a) = (1/W) sum_r h_r (r/m)^(1-a).

The source `notes/general-clifford-frames.tex` explicitly lowers a rank-r
edge to `P_L C_r P_R`, with affine binary address maps and quadratic phases
in `P_L,P_R`. Fourier rank zero means monomial; it does not imply linear
time on a fixed number of tapes. Section 05 uses the separate bit supplier
to implement these maps.

For a self-contained complex supplier using (2), let `g_t` be the number
of **fused, fully scheduled** rectangular shears targeting t slots. Include
every entrance, exit, child adapter, routing and restoration operation. The
additional moment is

    M_adapters(a) = (2/W) sum_t g_t (t/m)^(1-a).        (4)

For each use of (3), add `3/W * (2t/m)^(1-a)` instead. These are genuine
recursive calls and must be proper children. A sufficient scalar recurrence
condition is

    M_native(a) + M_adapters(a) < 1,                  (5)

plus the native physical/compiler, complete-volume, scalar, row, guard,
uniform shape and exact endpoint contracts. In the normalized recurrence,
the nonrecursive cost must be O(1) or otherwise strictly lower order than
the desired width exponent. This is a possible repair route: it replaces
the separate bit premise by an explicit augmented native invoice.

Applying (2) to an existing complex supplier that itself calls the bit
supplier is circular unless (5), its proper recursion and its complete
shape contract are proved. In particular, the unaugmented native moment
cannot be reused unchanged.

If a self-contained augmented supplier is actually completed on all whole
binary chunk shapes needed by the caller, with cost `O(V e^(1-s))` and
guarded payload width `B=Omega(e)`, equation (3) gives ordinary chunk
interchange on that same restricted domain in `O(V e^(1-s))`. There is
then no separate numerical bit endpoint: one can choose both `a<s` and
`b<s` with `a<b` and satisfy the outer ordering. For example, a completed
supplier with `s>9/80` would support the two hypothetical saving inputs
in section 3, subject to all of that caller's domain and analytic contracts.
This conditional reduction identifies a concrete way the bit cap could be
removed. It is not a reduction from the currently bit-dependent layer.

For scale, the advertised optimistic d=3 paired-plane screen used
`m=73`, `W/N=896/9` and moment `0.995605075916` with the centre retained
(`0.984346481996` without). If every added fused shear targets one slot,
the allowable number per local invocation is less than approximately
`9.91457` with the centre, or `35.31299` without. These are sensitivities
using the published rounded moments, not new exact admissions. They do
not lower-bound the unknown best fused adapter program. The separate
copy-accounting audit already raises those d=3 moments above one before
these adapter costs are added.

## 3. An explicit arithmetic extension admitting kappa=0.1

The selected outer engine is byte-identical to
`research/adaptive-kernel-demotion/vendor/engines/outer.py`, SHA-256
`c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c`.
It checks 47 strict inequalities, including `b<1/32`. The prior
`docs/research/assembly-domain-audit.md` correctly distinguishes that
enforced domain from an impossibility result and from the retained
Gaussian restriction `r<1/4`.

Here is a sufficient **displayed arithmetic region** beyond 1/32. Put

    1/9 < a < 1/3,       a < b < 1,
    0 < beta < 1-a/b,
    0 < eta < min(1/8, (9a-1)/(28a), (1-3a)/(2(1+a))).

Retain all equations from the selected balanced engine:

    q=a(1-2eta), c=q+eta/4, epsilon=(1-eta)/(1+q),
    G=epsilon*q, r=G+eta/2, delta=eta/8,
    tau=1-a, sigma=1-b,
    lambda=1-a+a*eta, lambdaPrime=1-q.

Assume positive literal-scalar and row-product bridge slacks. Then **all
46 displayed constraints other than `b<1/32` are strictly positive at
kappa=1/10**. The verification below is an arithmetic lemma, not the
missing analytic domain extension.

To see the target bound, multiplying `G>1/10` by its positive denominator
gives

    9a-1-28a*eta+20a*eta^2 > 0,

which follows from the second eta bound. Moreover `0<q<a<1/3` and
`epsilon>21/32`, giving `epsilon>a`, `epsilon>1/2`, and all elementary
width, fallback, cell and dimension comparisons. Since
`G<a/(1+a)`, the third eta bound gives `r<1/4`. Also `c<a+1/32<1`.

The layer internal exponent is tau because `b>a`. Its leaf exponent is
`1-(1-beta)b`, strictly below tau. Hence all internal, leaf, lambda and
lambdaPrime gaps are positive. The reservation gap is `c-q=eta/4`.
The exact identities

    1-epsilon=G+eta,
    1-epsilon-r=eta/2,
    1-epsilon*(1+c)=eta*(1-epsilon/4)

give the remaining geometry, guard and phase inequalities. The seven
outer margins are respectively

    G+eta, a, G, a, G+3eta/8, G+7eta/8, epsilon.

Their minimum is G. This also proves positivity of every margin minus
1/10. The artificial-boundary gap is `8-epsilon+3eta/8>7`.

An explicit rational example is

    a=14/125, b=9/80, beta=1/1000, eta=1/100000,
    q=349993/3125000, epsilon=4166625/4633324,
    G=11666316669/115833100000,
    r=23333791669/231666200000,
    G-1/10=83006669/115833100000 > 0.

Here G is approximately 0.100716605780. These a and b are hypothetical
supplier inputs, not established exponents. The unchanged strict engine
rejects the example solely at `b<1/32`; the diagnostic explicitly checks
that rejection before inspecting the other 46 inequalities.

This closes the *displayed parameter-arithmetic* gap. The supplier,
stopping, router, uniform setup, finite row stock, guard, precision,
prime/Gaussian and coefficient-enclosure lemmas must still be checked in
this larger parameter domain. In particular, a moment engine restricted
to arguments below 1/4 must use justified range reduction: at b near .112
even `b*log(73)` already exceeds that range. No production guard or
selected certificate is changed here.

## Reproduction and open next questions

Run `python3 -I -B research/kappa01-outer-repair/verify.py`. It authenticates
the exact source blobs, verifies the Walsh/shear and fused interchange
identities over rational coefficients, checks fusion and a noncommuting
control, and compares the independent outer fractions with an observed
execution of the unchanged source body. Its `RESULT.json` marks assumed
bridge and missing supplier/analytic premises explicitly.

The remaining productive tasks are a source-bound adapter word minimized
by exact fusion, a strict augmented moment with all native children
included, and a complete dependency audit of the expanded outer region.
Without those, this package establishes no kappa improvement.

Prepared with OpenAI assistance. Predecessor phase identities and native
frame contracts are retained and attributed to the source repository;
the outer equations credit Zhihao Chen, RaD/hipotures, icekylinx and eumemic
in their original source. New investigation is Apache-2.0. No independent
human review is claimed.
