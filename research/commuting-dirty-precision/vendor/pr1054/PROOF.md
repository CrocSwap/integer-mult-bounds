# Cubic precision for the constant-coefficient dirty stride word

## Result and fixed interface

This result applies to PR985 at
`9df42a99dd8497b6e7d46cd2507bb89071372640`. The unchanged source is in
`vendor/pr985/`. The new `dirty_stride.py` changes the precision admission,
adds its effective-depth formula, and caches two validation reads. It retains every rounded
operation, recursive child, block swap, coefficient computation, and head
return. In particular, it does not add an early exit or a clean data array.

The two validation loops now read each datum once, check that cached value,
and discard it. PR985's Python expression read the same entry twice while
charging one access. The simultaneous phase lane found that mismatch with
an independent array observer. The derived source corrects it without a
new data operation or a changed validation result. An observer separate
from the meter checks every literal indexed read and write in the new
leaf and kernel executions. The original source remains unchanged.

Let `u=2^-W`, `0<beta<=1/2`, and `|b|<=1-beta`. The root coefficient is
one immutable rational complex number. The source and target are distinct
length-`L` arrays on the complex grid of spacing `u`. They can contain
arbitrary data in every bit. The leaf adds an approximation to
`m (I-b Z_L^w)^-1 x`, with the same output shifts as PR985. It restores
the source exactly. The increment can depend on the initial target.

Put

    g = ceil(log2(1/beta)),
    D_eff = g + ceil(log2(W+1)).

If `K` is the structural Euclidean depth, the sufficient admission is now

    48 (min(K,D_eff)+1) u <= beta^3.                 (1)

The condition `W>=4g+16` implies (1) at every length and stride. The
unscaled leaf error remains `64 (X+1) u / beta^5` for source norm at most
`X`. For a multiplier with modulus at most `R>=1`, it is at most

    [64 R (X+1)/beta^5 + 3] u.                     (2)

For the inherited certified prime-power kernels, the complete balanced
dirty word has sufficient fractional precision

    W <= max(p,w_input) + m + 18r^3,

where every initial array has norm at most `2^m`. A sufficient signed
integer reserve per component is at most `m+15r^3`. The bound applies to
both signs of the word. Exact source and scratch restoration, two data
tapes, the logarithmic borrowed-array count, and the full PR985 movement
bill remain. No new multiplication exponent follows.

## 1. Extinction for the coefficients that PR985 computes

At a normalized non-base level, `0<d<=n/2`. Each new closure edge joins
at least two edges of that level. By induction, each edge at level `k`
represents at least `2^k` original edges. The actual number `e` of original
edges is the return time in PR985's modular formula. It lies in `[1,M]`,
where `M=L/gcd(L,w)` is the original cycle length. This counts actual
return times, not just residues modulo `M`. If `2^k>M`, that level cannot
occur. Reversal changes orientation but does not change these counts.

PR985 computes each coefficient afresh as `power(b,e,W)`. It does not
multiply a stored array of child coefficients. Its binary powering
truncates both components toward zero after each product. Truncation
cannot increase complex modulus. Induction over the multiplication tree
therefore gives

    |power(b,e,W)| <= |b|^e.

For `e>=2`, the returned number is on the grid of spacing `u`; the final
operation includes truncation. At level `k>=D_eff`,

    beta e >= 2^-g 2^k >= W+1,
    |b|^e <= (1-beta)^e <= exp(-beta e)
            <= exp(-(W+1)) < 2^-W.

The last inequality is strict, also when `W=0`. Since `g>=1`, these
levels have `e>=2`. Each component of the returned grid number thus has
absolute value below one grid unit and must be zero. This proof uses
complex modulus and the actual truncation rule. It does not assume a
positive real coefficient, a dyadic root descriptor, or monotonicity of
individual rounded powers. Every descendant meets the same bound. The
terminal cycle exponent is also at most `M` and meets the lower bound.

## 2. The full dirty zero subtree

Consider a subtree in which the two prepared coefficients at every level,
including every diagonal coefficient, are zero. A causal map with zero
coefficient is the identity on both arrays. Its physical implementation
still makes all the prescribed swaps, but only permutes values temporarily.
An expansion is a causal inverse, a zero injection, and a causal map.
It is the identity, including when its target contains arbitrary data.

At a non-base node, the closure calls are consequently adjacent inverse
maps after the identity expansions are removed. The first call adds its
result to the source prefix; the inverse sees the exact state that the
first call left. Both calls restore their tail input. The pair cancels
exactly. The baseline addition is the only remaining operation. At a
diagonal node, division by one and grid rounding leave the source value
unchanged. Thus, with the internal multiplier one, the whole subtree is
exactly `y += sign*x`. Both signs satisfy the identity. This is an
induction on the actual dirty word, not a use of PR977's clean-scratch
identity and not an assumption of target-independent rounding elsewhere.

The identity also has an internal magnitude bound. Let the incoming source
and target norms be at most `S` and `T`. Each recursive source is an
unchanged tail of its caller's source. Its target is a disjoint prefix of
that source. No recursive source includes an already changed connector.
Each temporary connector therefore contains at most the sum of two
source values, with norm at most `2S`. The outer target has norm at most
`T+S`. The inverse sign has the same bound. All other data movement is
swaps. The peak in the entire zero subtree is at most

    max(T+S, 2S),

independently of its structural depth. Endpoint equality alone would not
have proved this internal bound.

For the accuracy proof only, replace each subtree at depth `D_eff` by
its exact addition. This preserves the complete rounded output. There
are now at most `min(K,D_eff)` active non-base levels. PR985's power
error, shared-suffix, coefficient mismatch, and weighted source estimates
apply to those levels without any change. The new terminal has zero
error, which satisfies the former terminal allowance `u`. Beyond the
cutoff, the actual source causal maps are identities; their weighted
source bound does not accumulate more error. The preceding magnitude
lemma also controls all data in the untruncated zero tail. This proves
(1), (2), and the use of PR985's internal forward-leaf bound below.

No runtime subtree is removed. The structural depth, recursive call
count, two-tape movement, metadata stack, and coefficient preparation
still have their original costs.

## 3. A length-independent sufficient threshold

For fixed `g`, `(D_eff+1)2^-W` decreases as integer `W` increases: the
ceiling logarithm increases by at most one at a step, while the power of
two doubles. It is enough to check `W0=4g+16`. For `g>=1`,

    4g+17 <= 2^(g+5),
    D_eff(W0)+1 <= 2g+6 <= 8*2^(g-1),
    48(D_eff(W0)+1) <= 192*2^g <= 2^(g+16).

As `beta>=2^-g`, this proves `48(D_eff+1)2^-W<=beta^3`. The first two
elementary inequalities hold at `g=1` and persist after incrementing
`g`: each right side doubles and each left side grows by at most four.

The executable admission uses (1), which can be weaker than this simple
threshold. For example, `beta=1/2`, `W=12`, `L=5741`, `w=2378` has
`K=10` and `D_eff=5`. The original admission fails and (1) holds. The
checker executes the full rounded word on this case, checks its residual
and exact inverse, and charges every data movement. A residual check is
numerical evidence for this one input; the preceding proof covers all
lengths.

## 4. Transfer to the actual target-dependent kernel leaves

Let `U=tau Z_L^w`, with one immutable unit scalar `tau` shared by all
factors. Let `Q(z)=r^-1 product_j(z-rho_j)`, of degree `n=r-1`.
The outer leaf has coefficient `tau/rho_j` and multiplier `-1/rho_j`.
The inner leaf has coefficient `rho_j conjugate(tau)`, stride `-w`,
multiplier `conjugate(tau)`, and output shift `-w`. Both ideal maps are
`(U-rho_j I)^-1`. Exactly one factor also has scale `r`. These are the
maps in PR985's unchanged dispatcher, and all use the same `U`.

Let `||Q||_1<=M_Q` and `||Q(U)^-1||<=H_Q`. PR862's complementary-factor
argument gives a norm bound for every subset of the scaled factors:

    G = max(1, r 2^n M_Q H_Q).                    (3)

Indeed `product max(1,|rho_j|)<=||rQ||_1<=r M_Q` by the elementary
Mahler-measure inequality. A complementary polynomial has coefficient
norm at most `2^n r M_Q`. Multiplication by `Q(U)^-1/r` bounds the
unscaled subset inverse, and the one factor `r` is then paid. The same
unit isometry must occur in all factors; this is not a bound for
arbitrary unrelated operators.

Use PR905's free-algebra prefix lemma for the balanced four-call word.
With `h=ceil(log2 n)`, every ideal prefix and inverse prefix has
coefficient row sum at most `C=2*3^h`, and each monomial uses a strictly
decreasing subset of factor occurrences. Its proof includes both signs
of every child word. It depends on the ideal shear word, not on the
implementation of a rounded leaf. PR985's ideal dispatcher is exactly
that word. Equation (3) therefore gives

    B = C G

for every ideal prefix and inverse prefix, and `B^2` for every interval
propagator. The retained PR905 proof gives the universal induction. The
new contribution here is the transfer to the PR985 leaf contract and its
physical word, not a new prefix lemma.

For a positive PR985 leaf, (2) implies error at most

    a u (||source||+1),  a=68(r+1) beta^-5.         (4)

For a negative leaf, write its input target as `y` and its output as
`z`. Exact inversion of the positive word gives

    y = z + A x + delta(x,z),
    z = y - A x - delta(x,z).

The source is unchanged. The positive bound (4) holds for every target
`z`, without a target magnitude hypothesis. Thus the negative leaf has
the same error bound with the same source norm. No bound on the unknown
preimage target is used for this accuracy step. Its magnitude is paid
separately in Section 5.

Let all initial arrays have norm at most `D0`. The exact leaf count is
`N=3qn-2q^2<=2n^2`, with `q=2^floor(log2 n)`. Let `T` be the largest
actual joint norm at complete leaf boundaries. Every computed prefix is
finite because all closure denominators have modulus at least `beta`.
Insert the actual nonlinear errors into the ideal word by variation of
constants. For either sign, the prefix bounds and (4) give

    T <= B D0 + t(T+1),  t=N B^2 a u.

If `t<=1/2`, then `T<=2 B D0+1`, and the final execution error is at most

    2 N B^2 a u (B D0+1).                         (5)

This argument uses neither linearity nor target independence of a rounded
call. Each closure and each whole-word inverse is still the exact inverse
grid word. Distinct ancestor operands and the original scratch-depth
condition remain required by the implementation.

## 5. Integer guards, including inverse preimages

At a leaf boundary put `D*=2 B D0+1`. PR985's forward-leaf bound is

    512 (r+1)(D*+1)/beta^7.

Section 2 justifies the same bound in the full zero tails. To apply it
inside an inverse leaf, first bound that leaf's positive preimage. Its
source has norm at most `D*`, and its ideal operator has norm at most
`r/beta`. Since `a u<=1` follows from `t<=1/2`, the preimage target has
norm at most

    D_pre <= (2+r/beta)D*+1.

The inverse traverses the positive word at this preimage in reverse.
Use `D_pre+1<=(r+2)(D*+1)/beta` in the forward bound. A bound for every
data value, in either sign of every leaf, is consequently

    V = 1024 (r+1)(r+2)(B D0+1)/beta^8.            (6)

Two extra bits above `ceil(log2 V)` suffice for a signed component
reserve. This extra preimage factor is necessary in this proof; the
incoming negative target was not assumed to obey the forward preimage
bound. Block transport only moves these values and adds no new magnitude.

## 6. Explicit prime-power budgets

Retain the PR621/628/862 analytic and supplied factor-preparation
hypotheses. Let `r>=3` be a prime power, `n=r-1`, `ell=ceil(log2 r)`,
`h=ceil(log2 n)`, `phi=EulerPhi(r)`, and `D0<=2^m`, `m>=0`. Define

    d0 = 1+2ell+r n phi,
    a0 = 2d0+r+2,
    g  = d0+ell+2r+2,             beta=2^-g,
    e  = max(d0+1,a0+1,p+2a0+m+4),
    b_factor = max(n ell,e+r+3).

The original inverse has norm at most `2^a0`. The supplied dyadic-root
polynomial `Q` has coefficient error at most `2^-e`, norm at most `2^r`,
and stable factor margin `beta`. The common-isometry Neumann argument
gives `||Q(U)^-1||<=2^(a0+1)`. On a source of norm at most `2^m`, the
original-versus-prepared inverse error is at most `2^(-p-3)`. These are
inherited hypotheses and algorithms; this package does not implement
an all-size root factorizer.

Equations (3)--(6) are paid by the integer exponents

    J = a0+2r+ell+1+2h,
    A = 5g+ceil(log2(68(r+1))),
    W = max(w_input,4g+16,p+3+ceil(log2 N)+A+m+3J),
    I = J+m+8g+2ell+16.

Here `B<=2^J`, `a<=2^A`, and `B D0+1<=2^(J+m+1)`. Thus (5) is at
most `2^(-p-1)`, with `t<=1/2`. Admission follows from Section 3. The
bound (6), plus a sign reserve, is below `2^I`. No incoming grid is
coarsened. Preparation plus execution error is below `2^-p`.

For completeness, use `phi,ell,h<=r`,
`ceil(log2 N)<=1+2h`, and `ceil(log2(68(r+1)))<=ell+8`. The fractional
overhead is at most

    11r^3-11r^2+58r+42 <= 18r^3.

The difference is `(r-3)(7r^2+32r+38)+72`. The term `4g+16` is smaller
than this same majorant. Likewise

    I-m <= 10r^3-10r^2+52r+45 <= 15r^3,

with difference `(r-3)(5r^2+25r+23)+24`. The inherited factor width obeys
`b_factor<=p+m+7r^3`. These polynomial identities prove the all-size
bounds; the finite budget rows check their implementation.

At `r=64`, `p=128`, `m=20`, and `w_input=0`, the fractional budget is
`1,420,902` bits. PR985's full-word bound with the same margin and initial
norm needs `517,236,859` bits before any larger structural-depth admission.
Both words have `4,000` leaf calls and six borrowed arrays. These are
sufficient bounds, not optimal widths or measured execution times.

## 7. Complete cost and scope

Every leaf still uses two data arrays, a constant number of clean complex
arithmetic registers, and `O(log^2 L)` integer metadata bits. PR985 proves
at most `1280L` scalar products and divisions and `4096L` record moves
per leaf, including the complete structural recursion and returns. The
kernel retains `h` arbitrary dirty arrays and routes all of them over
two physical tapes. Its unchanged bound is

    8192 (N+1)(h+2)L

data-record moves. The effective depth is only for error analysis. It
must not replace structural depth in these resource counts.

Let `A_word=W+I` and let `B_desc` include the actual immutable root,
margin, multiplier, and unit-gauge descriptor lengths. Let `M(s)` pay
for rounded multiplication and division of words of width `s`. The bill
remains

    preparation + O(N L M(A_word+B_desc))
                + O(N(h+2)L(A_word+B_desc)) + O(NL).

The last term pays the inherited integer-control bound. Reading a stride
descriptor longer than `O(log L)` is additional input work. The supplied
preparation bill is `soft-O(r^3(p+m+r^3))` under the retained algorithms.
An arbitrarily long exact gauge description remains an extra charge.
There is no new coefficient array, tape, or borrowed data allocation.

This is a written accuracy proof with exact-rational supporting checks.
It is not a Lean proof, a fast arithmetic compiler, a measured runtime
gain, a variable-site-phase construction, a complete transform, or a
multiplication reduction. The selected certificate and `upstream/` do
not change. Source credit and substantial AI assistance are in `NOTICE.md`.
