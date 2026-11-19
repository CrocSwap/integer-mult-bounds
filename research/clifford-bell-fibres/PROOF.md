# A Gaussian-dyadic left inverse at the sharp four-qubit width

Let `R = Z[i,1/2]`, `d = 16`, and fix one Gaussian-dyadic unitary `U` in
each four-qubit Clifford coset modulo scalar powers of `i`. Let `A_f` have
columns `(vec(U)/4)^(tensor f)`. Vectorizing the tensor-power matrices in
one step instead merely permutes the coordinates.

**Theorem.** There is an explicit matrix over `R` with `B_f A_f = I` at
every integer `f >= 13`. Together with the reported complex rank failure
below width 13 in [Ali Romman's #7766](https://github.com/aliromman/integer-mult-bounds/blob/d7c2dd1868c70f0addce2c0a4d3220149452f14b/research/clifford-four-qubit-threshold/PROOF.md),
this determines the least Gaussian-dyadic width as 13. The construction
of the upper bound is independent of that spectral calculation.

## 1. Six Bell pairs and one matrix

Write `V = F_2^4 ⊕ F_2^4` and use unphased real Weyl matrices
`W_t = X^x Z^z` for `t=(x,z)`. The commutation sign is the symplectic
pairing `<t,t'> = x·z' + z·x'`, and `W_t^T = (-1)^q(t) W_t` with
`q(t)=x·z`. The 256 vectors `vec(W_t)/4` form an orthonormal basis of
the two-register space. Conjugation by a Clifford gives

```text
U W_t U* = gamma_U(t) W_(St),       S in G = Sp(V).
```

All phases here and below are units of `R`. A scalar of modulus one in
`R` is a power of `i`, by reducing a sum of two squares equal to a power
of four modulo four and dividing through by four repeatedly. The usual
Clifford action surjects onto `G`. A Hermitian Pauli lift `P` of each
nonzero `p` gives a dyadic unitary `(1+i)(I+iP)/2` inducing the
symplectic transvection at `p`, and these generate the symplectic group.
Its projective kernel consists of the Weyl matrices. Indeed, a Clifford
fixing every label has conjugation signs in `{+1,-1}` by squaring
`W_t`. These signs form a character of `V`, hence have the form
`(-1)^<p,t>`. After removing `W_p` the unitary commutes with every Weyl
matrix, which forces it to be scalar. Thus each fibre of the map to
`S` consists of 256 representatives proportional to `W_p U_S`.

On a Bell pair the action of `U ⊗ U` reads

```text
U W_t U^T = theta_U(t) W_(L_S t),       L_S t = St + b_S .
```

In fact `U bar(U)^(-1) = U U^T` is a Pauli up to phase, since entrywise
conjugation preserves the symplectic action on the real Weyls. Left
multiplication of `U` by any Pauli preserves all labels in this formula.
The affine maps compose, as follows directly by applying the two-register
action twice. Transposition also gives `q(L_S t)=q(t)`.

For an ordered six-tuple `t=(t_1,...,t_6)` put `w=sum_i t_i` over the
binary field. If its output is `t'=L_S t` componentwise, then
`w'=sum_i t'_i = Sw`, since six copies cancel the affine offset. Under
the Bell basis change on six pairs, the block of `U^(tensor 13)` between
these tuples is `beta_U(t) U`, where `beta_U(t)=product_i theta_U(t_i)`.
Every other output block for this input is zero. Left multiply this
observed block by `W_(w')` and right multiply by `W_w^(-1)`. The block
becomes

```text
sigma_S(t) U,       sigma_S(t) = beta_U(t) / gamma_U(w).
```

This phase depends only on `S`. Replacing `U` by `W_p U` multiplies each
Bell phase by `(-1)^<p,t'_i>` since `W_p^T=W_p^(-1)`, hence multiplies the product by
`(-1)^<p,w'>`. The same sign multiplies `gamma_U(w)`. A scalar lift
`zU` contributes `z^12=1` to the product and leaves conjugation unchanged.
Composition in the two matrix actions gives
`sigma_(S_1 S_2)(t) = sigma_(S_1)(L_(S_2)t) sigma_(S_2)(t)`.

All these operations are fixed `R`-linear maps on the observations.
Concretely, first multiply by `4^13` to undo the column normalization,
then unvectorize, regroup six pairs, and take the stated input and output
Bell matrix elements. This reasoning by columns therefore also applies
to an arbitrary mixture with coefficients `c_U`.

## 2. Which sums the orbit supplies

Write `Z_j, X_j` for the corresponding binary labels, and let
`L = span(Z_1,...,Z_4)`. Use the ordered seed

```text
T = (0, Z_1, Z_2, Z_3, Z_4, X_4).
```

A symplectic map stabilizing this tuple in the Bell action has `b_S=0`,
fixes `L` pointwise and fixes `X_4`. Fixing `L` pointwise forces a shear
`(x,z) -> (x,z+Bx)` with `B` symmetric. Fixing `X_4` means its fourth
row and column vanish. Preserving `q`, now with zero offset, forces
zero diagonal. Conversely the three ordinary real controlled-Z gates
on qubit pairs 12, 13 and 23 generate all eight such shears. Their lifts
fix each seed Weyl by ordinary conjugation and have `UU^T=I`.
They also fix the product of the seed Weyls, hence `gamma_U(w)=1`.
Thus the stabilizer `C` has order eight and `sigma_c(T)=1` throughout.

Identify the orbit of `T` with `G/C`. For each tuple `i` there, fix any
transporter `g_i` from the seed, and put `j_i = sigma_(g_i)(T)`. The
cocycle and its trivial value on `C` make this phase independent of the
transporter. For `S i=j` we have `sigma_S(i)=j_j/j_i`. Define the
unknown fibre matrix `M_S=sum_(U over S) c_U U`. Multiplying each
corrected observation block by `j_i/j_j` therefore exposes the sum

```text
sum_(S in g_j C g_i^(-1)) M_S .
```

An explicit transporter can always be chosen by finite enumeration.
For any subgroup `H` of power-of-two order write `e_H = sum_(h in H) h/|H|`
in the group algebra `R[G]`. The coefficient vectors of the available
coset sums are precisely the coefficient vectors of the elements
`8 g_j e_C g_i^(-1)`. Arbitrary left or right translates yield the
same set, since group elements can be replaced by coset representatives.
Consequently we can recover every `M_S` linearly over `R` once

```text
R[G] e_C R[G] = R[G].
```

## 3. A dyadic identity for the stabilizer average

Take the full abelian shear group `A = Sym_4(F_2)` fixing `L` pointwise,
including its diagonal entries. Regard a shear parameter `B` as a
symmetric matrix on a chosen basis of `L`. For any vectors `u,v` of
`L`, write `B_uv = uv^T + vu^T`. Each character of `A` is determined
by a binary quadratic form `Q` on `L` as follows:

```text
chi_Q(uu^T) = (-1)^Q(u),       chi_Q(B_uv) = (-1)^lambda(u,v),
lambda(u,v) = Q(u+v)+Q(u)+Q(v).
```

Indeed, the four diagonal coefficients and six off-diagonal
coefficients of a linear functional on symmetric matrices freely
specify the four linear and six cross coefficients of `Q`. For each
of these 1,024 characters set
`e_Q = 2^-10 sum_(B in A) chi_Q(B) B`, using group elements in this
sum. Character orthogonality gives pairwise orthogonal idempotents with
`sum_Q e_Q=1`. A basis change `g` of `L`, acting contragrediently on
the complementary dual, sends `B` to `g B g^T`, so acts on the
characters by the natural change of variables.

For any isotropic three-plane `W <= V` the conjugate `C_W` of `C`
consists of the eight products of its three pair shears. In basis-free
terms the generators for basis pairs `u,v` send
`s -> s + <s,u>v + <s,v>u`. This is the seed description above for
`W=span(Z_1,Z_2,Z_3)`, transported by a symplectic change of basis.
The stated map for each pair and all their products depend only on
`W`. Such basis changes exist by extension of an isotropic basis to
a symplectic basis. In particular, each `e_(C_W)` belongs to the
two-sided ideal generated by `e_C`.

If the alternating polar form `lambda` of `Q` is degenerate, choose a
three-plane `W <= L` isotropic for `lambda`. Its existence follows
from the rank being zero or two. In rank two, extend the two-dimensional
radical by any vector outside it. Then `C_W <= A` and `chi_Q` is one
on its three generators. Hence `e_Q e_(C_W) e_Q=e_Q`.

Now let `lambda` be nondegenerate. There exists a nonzero `r in L`
with `Q(r)=0`: on a two-dimensional `lambda`-isotropic plane `Q`
is linear, so has a nonzero zero. Set `H=r^perp` for this polar form,
take a basis `z_1=r,z_2,z_3` of `H` and extend it by `z_4` to `L`.
Then `lambda(z_4,r)=1`. Put `P=span(r,z_2)`. In the complementary
dual Lagrangian take `x_4` pairing one with `z_4` and zero with `H`
in the original symplectic form on `V`. Choose the mixed isotropic plane

```text
W = span(r,z_2,x_4).
```

Its group `C_W` consists of the eight products of `B_(r,z_2)` and the
four basis changes `T_p` for `p in P` sending `z_4 -> z_4+p` and fixing
`H` pointwise, with contragredient action on the dual. This follows
from the three pair-shear formulas. Every element normalizes `A` and
`chi_Q(B_(r,z_2))=1`.

For each nonzero `p in P`, the character moves under `T_p`. If `p=r`,
then `Q(z_4+r)=Q(z_4)+1`. If `p` is outside the span of `r`, then
`p` is outside the radical of `lambda|H`, which is the line through
`r`. Pick `y in H` with `lambda(p,y)=1`. The transformation changes
`lambda(z_4,y)`, hence changes `Q`. Thus only the two elements of
`C_W` with `p=0` stabilize the character. For each of those,
`e_Q c e_Q=e_Q`; for every other `c`, orthogonality of `e_Q` and
`c e_Q c^(-1)` gives zero. Consequently

```text
e_Q e_(C_W) e_Q = (2/8) e_Q = e_Q/4 .
```

This constructs the identity in the ideal. For each `Q` choose a plane
and a transporter `g_Q` as above. With coefficient `d_Q=1` in the
degenerate case and `d_Q=4` in the nondegenerate case,

```text
1 = sum_Q d_Q e_Q g_Q e_C g_Q^(-1) e_Q .
```

Expanding the character idempotents expresses this formula as a
dyadic linear combination of the available translates. Multiplying
by each group element on the left gives all single-fibre indicators.
There is no division by the order of the symplectic group.

## 4. Decode the Pauli fibre and pad

For each fixed projective representative `U` over `S`, return
`Tr(U* M_S)/16`. Any other representative over `S` differs by a
nonidentity Pauli on the left up to scalar, and has zero trace pairing
with `U`. The target pairing is 16, so this recovers exactly `c_U`.
It uses coefficients in `R`, even for arbitrary fixed scalar lifts.
Together the steps specify a linear left inverse on the entire
observation space. At larger widths, tensor each row with `f-13`
copies of its target's single-copy functional `(vec(U)/4)^*`. This
functional is one on the target column. All other columns are already
annihilated by the first thirteen factors. Applying any ring homomorphism
from R to a residue field preserves the identity B_f A_f = I. In
particular, the columns remain independent modulo every odd Gaussian
prime for f >= 13, including characteristics dividing the group order.

## 5. Stability on the normalized observations

The single functional which extracts one corrected coset block and traces
it against `U*/16` has Euclidean row norm `4^13/4 = 4^12`. The Bell
input and output vectors have unit norm, the Weyl corrections are unitary,
and `||U/16||_F=1/4`. Each `e_Q` has coefficient absolute sum one.
The expansion in Section 3 therefore costs at most `sum_Q d_Q/8 <= 512`
in absolute coefficients of coset sums. This bounds the norm of each row
of `B_13` by `2^33`. Tensoring with the unit-norm padding preserves that
bound for every `f>=13`. With `N=12,128,668,876,800` rows we obtain
`||B_f||_2 <= sqrt(N) 2^33 < 2^55`.

Assume the published uniform spectral enclosure of Ali Romman's
[#7772, exact source](https://github.com/aliromman/integer-mult-bounds/blob/1398fbdca3536389d8ac3c8b3aaa408f03e8f6c2/research/clifford-threshold-conditioning/PROOF.md).
For `A=A_f` and `K=A* A` it gives eigenvalues in
`[470624175/2^32, 7841980575/2^30]`. Start at `D_0=B_f` and use the
exact dyadic iteration from [#7798, Section 4](https://github.com/apoursh/integer-mult-bounds/blob/0ae10f215780296ca50142fd36fdf904b8c1b146/research/clifford-width17/PROOF.md#4-exact-dyadic-stabilization):

```text
D_(j+1) = (I-K/4) D_j + A*/4 .
```

Induction gives `D_j A=I`, and subtracting the canonical fixed point
`A^+=K^(-1) A*` multiplies its error on the left by `I-K/4`. The
enclosure gives `||I-K/4||_2 < 63/64` and `||A^+||_2 < 3.02095`
(the latter is checked by squaring against the lower endpoint).
The initial error is less than `2^56`. Since `(63/64)^64<1/2`,
at `j=8192` the operator-norm error is less than `2^-72`, giving
`||D_8192||_2 < 3.021`. This yields bounded noise amplification for
an exact Gaussian-dyadic decoder at the first possible width as well
as all larger widths. The width and splitting proof in Sections 1–4
uses no spectral bound.

The construction concerns exact algebraic recovery. It supplies no
priced physical realization, new supplier or improvement in κ. The
rank failure at width 12 is an input from #7766. An inverse at any
smaller width could be padded to width 12 by Section 4, contradicting
that rank failure. The full
Clifford alphabet and production multiplier are not enumerated here.
The earlier width-17 construction and its general stabilizer result
retain their distinct scope. [Width-17 handoff #7798](https://github.com/CrocSwap/integer-mult-bounds/pull/7798).

Clifford actions on Weyl operators, Bell coordinates, symplectic
transvections and character idempotents are classical. The projective
alphabet and complex threshold follow Ali Romman and the retained work
of alephnan and Nick Petalas. Prepared by **apoursh** with substantial
OpenAI Codex and separate agent assistance. Apache-2.0.
