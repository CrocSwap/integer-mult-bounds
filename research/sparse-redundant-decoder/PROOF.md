# Equality and the all-active gap for a sparse P112 ninth normal

This is a written structural argument with exhaustive finite binary lemmas. It
is not a proof-assistant verification of integer multiplication. Transposes and
products are ordinary, also over C.

Mihir Srivastava's incorporated PR845 already proves the cost-64 lower bound
for arbitrary real single lifts with fixed coordinate readers. The additions
here are the *complete equality classification* and *sharp all-nine-active
cost65* for the specified three-coordinate-sum normal. No priority for the
64 floor is claimed. For a fixed real normal, replacing a nonreal row shift by
a real value outside its finitely many zero locations preserves that row's
support; complex coverage alone is not advertised as a new mechanism.

## 1. Fixed geometry and exact family

Start with E8 roots `±e_a ±e_b` and the half-integral roots
`(±1/2,...,±1/2)` with an even number of negative signs. Take one representative
per opposite pair. Rotate each coordinate pair by the orthogonal Hadamard
matrix, then multiply every root by sqrt(2). Denote the resulting vectors by r.
The eight lines of the frame `e_0±e_1,...,e_6±e_7` become `2e_j`; delete them.
The remaining set P has 112 vectors of norm squared four, each with four
entries in `{±1}` and four zeros. Its true-root Gram matrix is `G_ij=r_i·r_j/2`.
The binary pairing is

    B_ij = (r_i·r_j/2 + 1) mod 2.

Fix nine column functions on P:

    T_ij = r_ij (0 <= j < 8),     T_i8 = r_i0+r_i1+r_i2.

This is one specified frame, with a dependency supported on four columns. We
vary the *row coefficients*, not the normal frame. Every exact complex D with
`D T^t = 2G` has, for arbitrary independently chosen `t_i ∈ C`, the form

    D_ij = r_ij-t_i (j=0,1,2),
    D_ij = r_ij     (j=3,...,7),
    D_i8 = t_i.

Indeed the roots span R^8; testing the identity against every column root forces
the represented vector to equal r_i. The only dependency of the nine fixed
normals is `e_0+e_1+e_2-(e_0+e_1+e_2)=0`. This proves the claimed form directly,
and is the fixed-frame instance of joaqcoo's PR1224 Corollary C.

For column k, let `X_k={i:D_ik != 0}`, `Y_k={i:T_ik != 0}`. Charge its *separate
term* copy cost `c_k=rank_F2 B[X_k,Y_k]`, the PR446/717/968 model. The theorem
covers all-pairs exactness, not masked identities or shared-copy billing.

## 2. Deficiency spaces correctly account for the column side

Let C_k be the space of length-112 binary functions spanned by the columns
`B[:,Y_k]`. Let K_k consist of functions in C_k that vanish on X_k. Then

    c_k = dim C_k - dim K_k.

This is rank-nullity for restriction of the column code to X_k. It remains true
when `dim C_k < 9`; row-label span alone is not substituted for pairing rank.
The finite check establishes:

- the full binary code has dimension nine;
- `dim C_k=8` for k=0,...,7 and `dim C_8=9`;
- each rigid term k=3,...,7 costs eight;
- every live row has a nonzero restriction to every Y_k. Consequently `c_k=0`
  if and only if X_k is empty.

Write δ_j=dim K_j for j=0,1,2 and δ_*=dim K_8. Total cost is

    cst = 40 + (24-δ_0-δ_1-δ_2) + (9-δ_*)
        = 73 - (δ_0+δ_1+δ_2+δ_*).

## 3. Compatibility and complete finite lemmas

Use four local column labels 0,1,2,* and values
`v_i=(r_i0,r_i1,r_i2,0)`. If a deficiency function f in K_a is 1 at i, then
`D_ia=0`, hence `t_i=v_ia`. Thus for f in K_a and g in K_b,

    f_i=g_i=1  implies  v_ia=v_ib.                 (compatibility)

This is necessary for arbitrary complex t_i. Generic complex values do not
escape it: they simply zero fewer coefficients.

For a subspace U of C_a define H_b(U) as the functions in C_b compatible with
every f in U. It is a linear space: on each position in the union of supports
of U where v_ia differs from v_ib, its functions must vanish. Actual deficiency
spaces obey `K_b ⊆ H_b(U)` whenever `U ⊆ K_a`.

Two finite lemmas suffice; no search over complex coefficients is used.

**L1.** For each a=0,1,2 and every binary plane U in C_a, the two *other
coordinate* H spaces have dimension zero and H_*(U) has dimension one.

There are `[8 choose 2]_2=(255*254)/6=10,795` planes in each C_a. All 32,385
are checked. The encoding `0<x<y<x xor y` enumerates every plane exactly once.

**L2.** For each a=0,1,2 and each nonzero f in C_a, `dim H_*(span(f)) <= 2`.
Of its 255 nonzero functions, 254 give dimension two and one gives dimension
one. All 765 cases are checked.

The primary implementation uses length-112 function bitsets and enumerates all
possible compatible functions. The separate checker independently reconstructs
P as the signed affine planes in F2^3: four-element supports whose coordinate
indices XOR to zero. It changes to nine-coordinate code functions and computes
H by rank-nullity of linear equations. It imports no primary or predecessor
implementation. Both replay the complete L1 and L2 inventories.

## 4. Sharp minimum and equality classification

If some coordinate deficiency δ_a is at least two, choose a plane in K_a.
By L1 the other coordinate deficiencies vanish and δ_* <= 1. Since δ_a <= 8,

    δ_0+δ_1+δ_2+δ_* <= 9.

If all coordinate deficiencies are at most one and at least one is nonzero,
L2 gives δ_* <= 2, so their sum is at most five. If they all vanish, δ_* <= 9
immediately gives the desired bound. Therefore **cst >= 64**.

Equality can occur only in two cases:

1. All coordinate deficiencies vanish and δ_*=9. The ninth term costs zero,
   hence its support is empty and every t_i=0.
2. One coordinate deficiency is eight and δ_*=1, with the other two zero.
   That coordinate term costs zero, hence every t_i=r_ia for one a=0,1,2.

The replay checks all four shift assignments and every identity entry. Each
has eight active terms and cost 64. Thus these four global assignments are
**exactly all minimum-cost decoders in the fixed family**, even allowing
arbitrary complex per-row shifts.

## 5. Sharp all-nine-active minimum

If all nine terms are active then every c_k is positive. In the first case of
section 4 this improves δ_a <= 8 to δ_a <= 7, so the total deficiency is at most
eight. In the all-zero-coordinate-deficiency case it improves δ_* <= 9 to
δ_* <= 8. The intermediate case still has total deficiency at most five.
Thus every all-nine-active decoder has **cst >= 65**.

For attainment let t_i=0 except at row 40 in the specified sorted geometry,
where t_40=2. Since the original coordinate entries are 0 or ±1, this removes
none of the first three original row supports; their costs stay eight. All
five rigid terms cost eight. The ninth term has one row of nonzero pairing,
so costs one. The nine term costs are `(8,8,8,8,8,8,8,8,1)`. Every term is active
and all 12,544 identity entries hold. Row 40 uses the original assignment seed
to choose a witness, not to claim novelty.

## 6. Price, scope and remaining obligations

The algebraic ratio is at least `64/112=4/7`, exactly the coordinate decoder's
ratio. Keeping all nine terms raises it to `65/112`. Therefore this single
sparse-dependency extension cannot save copied information even before paying
any helper, source access, frame, restoration, hosting or recursive-child
expenses. All such additional nonnegative expenses were optimistically set to
zero for this *copy-budget screen*. No complete recurrence, realized supplier,
changed paid rank histogram, runtime gain or new kappa is claimed. The exact
moment depends on more than this scalar copy sum; no general moment barrier is
inferred.

The equality classification and active-term gap have not been extended here
to other ninth normals or coefficients. PR845 already supplies its broader
real fixed-reader cost64 floor. Other punctures, more terms, masked identities,
interacting delivery and shared-copy billing are outside this result. This is
not a proof about all nine-term decoders. The selected
PR1094 conditional construction and its all-size/compiler, common-label,
mutable-source, hosting, precision/tape and analytic hypotheses are unchanged.
