# Independent audit of PR1212, Lemmas 5 and 6

**Verdict: the two lemmas are valid under the stated hypotheses. No substantive flaw was found.** The pinned written argument is already a universal argument, not an inference from rational examples. This contribution expands its compressed algebra, supplies explicit integral certificates, and independently reconstructs the finite geometry needed for gluing. It is not a repair of a demonstrated false claim.

**Exact target:** `57099cb5684f38877f31d149d598801671a633db`, `research/complex-rank8-decoder-rigidity/PROOF.md`, Sections 5–6, in [PR1212][pr]. The contributor handoff is [Discussion 1448][claim]. The supplied main integration base is `410026dc5513b87db92ae98571d1d5984c69a983`; it is not being substituted for the audited predecessor head.

**Scope:** a conditional lemma audit. The predecessor's zero-exclusion conclusion is an explicit premise, not reproved or independently replayed here. No new κ, supplier, decoder-cost floor, all-size multiplication theorem, or P111/P104/P110 extension is asserted. No full selected-supplier cold replay or merge is claimed. The dimensions below describe only the class-column-scaling equations, not a new multiplication construction.

**Credit and assistance:** Brett Halligan / `burntout76` and **Ninefold** for PR1212; **DreamingOfClouds** for the PR717 model; **themilkman216** for PR968. Prepared with substantial **GPT-6 Pro assistance through ChatGPT**. The derivations and verifier are an AI-assisted independent reimplementation in this session, not an independent human review. Codex handled source coordination, repository packaging and the separate local replay recorded in README.md. No independent human review is claimed.

## 1. Results and evidence at a glance

The contribution has four parts:

1. An exact local classification, with both a nine-identity polynomial-ideal certificate and explicit unimodular matrices. The original six-variable exponent matrix has Smith diagonal **(1,1,2,0,0,0)**. Its nonzero solution set has exactly the common-sign branches, not an unnoticed family of complex phases.
2. A sign-normalization proof which identifies the negative branch as a genuine rank-one class matrix. The factor **4** and the order of factors in the formula for `B` are checked using ordinary inverse transpose.
3. A separate geometric proof and reconstruction for the P112/P120 pivots: affine planes in `F₂³`, complete classes, all needed witnesses, and the same-block comparison bridge.
4. An integral gluing certificate. For all actual overlap constraints, explicit integer matrices satisfy

   `M P = 0,    Q P = I,    I - P Q = W M`.

   This proves the gluing relation lattice is saturated and the solution is a global potential, with no extraction of roots and no hidden finite torsion. It is stronger evidence than a rational-rank computation.

The delivered program was replayed locally with Python **3.12.14** on macOS arm64. The ordinary run passed **28 named checks**; a historical optimized execution plus saved-certificate comparison passed **29**. Changing the saved Smith diagonal entry from 2 to 1 was rejected with exit status 1. The fresh certificate was byte-identical to the Pro research-session artifact. The default ordinary and optimized commands reconstruct all witnesses in memory and run 28 checks; exporting and comparing a saved certificate is optional. README.md records the local commands, counts, hashes and limits. These executions check the exact identities and finite inputs; the universal implications remain written mathematics below.

| Independently checked quantity | P112 | P120 |
|---|---:|---:|
| Complete live classes | 26 | 28 |
| Four-point support blocks | 14 | 14 |
| Triples / pairs covered by the design | 56 / 28 | 56 / 28 |
| Class/group/column-pair witness obligations | 312 | 336 |
| Witness counts per obligation | 96 have 6; 216 have 8 | all 336 have 8 |
| Unordered distinct-block class overlaps | 288 | 336 |
| Ordered two-term equations on these overlaps | 4608 | 5376 |
| Class-coordinate variables | 104 | 112 |
| Free parameters after fixing `g₀=1` | 33 | 35 |
| Rank of saturated gluing relation lattice | 71 | 77 |
| Ordered pair-class transfers checked, including identities | 876 | 1008 |

These are complete finite censuses for the explicit pivots used here. The universal field-valued assertions follow from the proofs and integer identities below, not from those counts alone.

## 2. Precise hypotheses and dependency boundary

Let `k` be a characteristic-zero field. All transposes are ordinary transposes; the pairing is bilinear, not Hermitian. Work with the fixed integer E8 root-line geometry and a live orthogonal pivot frame `F` of size eight.

The following input is used:

- The pivot reduction gives vectors `a_i,b_i` supported on the four-element set `T_i`, with diagonal pairing `a_i·b_i=16` and zero pairing for distinct orthogonal lines. In particular, a complete orthogonal four-line class satisfies `A_C B_Cᵀ=16I₄`.
- Every relevant support entry of `a_i` and `b_i` is nonzero. **This is the assumed predecessor zero-exclusion premise.** It is not inferred by the present program from the finite geometry.
- The supports form the stated `S(3,4,8)` design. Each support carries two four-line classes whose sign matrices are Hadamard, and the overlap orthogonality rule is the one obtained by expanding in the pivot frame.
- The chosen live sets/pivots have only complete or wholly absent classes; each support block retains at least one complete live class.
- The appropriate two-term cross-block equations hold. The required finite witnesses are both derived from the preceding geometry and independently enumerated below.

For reference, the factorization `K=(1/4)K[:,F]K[F,:]` is standard block linear algebra: `K[F,F]=4I₈` forces rank at least eight, and a rank-at-most-eight matrix with that pivot has zero Schur complement. Neither positivity nor symmetry of `K` is required. This explains the interface to the lemmas; it is not a replay of the preceding theorem package.

### What the nonzero premise does

It permits division by row-normalizing entries and all six normalized variables. It also supplies a nonzero witness vector in the two-coordinate pairing. For that particular kernel argument, having at least one nonzero coordinate of the witness would suffice, but we retain the stronger stated premise throughout the audit.

Complete classes cannot be replaced silently by incomplete ones: the invertibility of the square `A_C` used below comes from the complete-class identity. Nor can an arbitrary live pivot silently replace the special P112 pivot: completeness is a real hypothesis.

## 3. Lemma 5: from witnesses to the exact local equations

### 3.1 The forced minor is valid over a general field

Take two rows `i,i'` in one sign-product group for columns `c,c'`. A live row `j` in another block meeting this block exactly in `{c,c'}` is orthogonal to both, so

`a_ic b_jc + a_ic' b_jc' = 0`,

`a_i'c b_jc + a_i'c' b_jc' = 0`.

The nonzero vector `(b_jc,b_jc')` defines a nonzero linear functional on `k²`; its kernel has dimension one. Therefore the two `a`-vectors are linearly dependent and

`a_ic a_i'c' - a_ic' a_i'c = 0`.                                      (3.1)

This reasoning does not use a positive definite inner product. In particular, over `C`, an isotropic witness causes no exception: the functional is still nonzero and its kernel still has dimension one.

Let `ε_if` be the sign entry, and set `u_if=a_if ε_if`. For a group, write

`ε_ic ε_ic' = ε_i'c ε_i'c' = s ∈ {±1}`.

The left side of (3.1) becomes

`s ε_ic ε_i'c (u_ic u_i'c' - u_ic' u_i'c)`.

The prefactor is nonzero, so the same minor of `u` vanishes. There is no additional minus sign in this conversion.

### 3.2 Simultaneous row labels exist

Fix any column as `a`; name the others `b,c,d`. The column-pair groups are the three distinct perfect matchings of four rows. Choose row 1 arbitrarily. Label its partner in the `ab` matching row 2, its partner in the `ac` matching row 3, and its partner in the `ad` matching row 4. Distinctness of the matchings makes these three partners distinct.

The matchings are now

- `12|34` for `ab` and `cd`;
- `13|24` for `ac` and `bd`;
- `14|23` for `ad` and `bc`.

This is a local relabeling used in the proof. It does not require compatible Hadamard orderings in different blocks: after proving the class formula, the coordinates are returned to their original pivot labels.

Set `δ_i=u_ia`, divide row `i` by `δ_i`, and thus normalize its first entry to 1. The six first-column group equations give

```
          a   b   c   d
row 1     1   x   y   z
row 2     1   x   Y   Z
row 3     1   X   y   Z
row 4     1   X   Y   z
```

All six variables are nonzero. The other six group minors are precisely

```
yZ = Yz,    yz = YZ,
xZ = Xz,    xz = XZ,
xY = Xy,    xy = XY.                                                (3.2)
```

The verifier obtains these expressions directly by Laurent-polynomial multiplication of the indicated minors. It checks their signs and also checks that the other six minors vanish identically in the displayed parametrization.

## 4. Universal two-branch classification and exact certificates

### 4.1 A direct derivation

Introduce nonzero ratios

`p=X/x,    q=Y/y,    r=Z/z`.

Then (3.2) is equivalent to

```
r=q,    qr=1,
r=p,    pr=1,
q=p,    pq=1.                                                       (4.1)
```

The first and third equations give `p=q=r=t`. The second gives `t²=1`. Conversely, `p=q=r=t` and `t²=1` satisfy all six equations. In a characteristic-zero field,

`(t-1)(t+1)=0`

implies `t=1` or `t=-1`. These are distinct elements and exhaust the possibilities over every such field, whether or not the field is algebraically closed. Thus the exact branches are

`(X,Y,Z)=(x,y,z)` and `(X,Y,Z)=(-x,-y,-z)`.

No positivity assumption, ordering of the field, or assertion that “complex squares have real roots” is being made. The only polynomial whose roots matter is `t²-1`.

### 4.2 A polynomial-ideal certificate

This certificate also proves there is no extra component concealed by the compressed elimination. In `k[p,q,r]`, define

```
f1 = r-q,       f2 = qr-1,
f3 = r-p,       f4 = pr-1,
f5 = q-p,       f6 = pq-1,

g1 = p-r,       g2 = q-r,       g3 = r²-1.
```

The following **literal polynomial identities** prove equality of the two generated ideals:

```
g1 = -f3
g2 = -f1
g3 = f2 + r f1

f1 = -g2
f2 = g3 + r g2
f3 = -g1
f4 = g3 + r g1
f5 = g2 - g1
f6 = g3 + q g1 + r g2.                                              (4.2)
```

All nine identities were checked by exact polynomial expansion in the delivered program. This is not evaluation at finitely many values of `p,q,r`.

After adjoining the free nonzero variables `x,y,z`, the nonzero solution algebra is

`k[x±¹,y±¹,z±¹,t]/(t²-1)`.

Here `t` is automatically a unit. Since 2 is invertible, the ideals `(t-1)` and `(t+1)` are comaximal, and the algebra is the product of two Laurent-polynomial algebras. This gives an exact scheme-level description in this characteristic: two reduced torus components, not just a statement about sampled field points.

### 4.3 An actual unimodular exponent-lattice certificate

For `(p,q,r)`, encode (4.1) as six monomial equations equal to 1, in the order

`r/q, qr, r/p, pr, q/p, pq`.

Their row-exponent matrix is

```
M_local =
[ 0 -1  1 ]
[ 0  1  1 ]
[-1  0  1 ]
[ 1  0  1 ]
[-1  1  0 ]
[ 1  1  0 ].
```

Use these explicit matrices:

```
U =
[ 0  0  1  0  0  0 ]
[ 1  0  0  0  0  0 ]
[ 1  1  0  0  0  0 ]
[-1 -1  1  1  0  0 ]
[ 1  0 -1  0  1  0 ]
[ 0 -1  1  0  0  1 ]

V =
[-1  0  1 ]
[ 0 -1  1 ]
[ 0  0  1 ].
```

Direct integer computation gives `det U=det V=1` and

```
U M_local V =
[1 0 0]
[0 1 0]
[0 0 2]
[0 0 0]
[0 0 0]
[0 0 0].                                                          (4.3)
```

Before the column change, the three surviving equations are `r/p=1`, `r/q=1`, `r²=1`. The change of variables is the invertible monomial substitution

`p=w/u,    q=w/v,    r=w`.

Thus (4.3) says exactly `u=1, v=1, w²=1`. Integral row operations are reversible products and inverses of equations; they are not taking a square root or saturating the relation lattice over `Q`.

For completeness, the original six-variable exponent matrix, in variable order `(x,y,z,X,Y,Z)`, is

```
E =
[ 0  1 -1  0 -1  1 ]
[ 0 -1 -1  0  1  1 ]
[ 1  0 -1 -1  0  1 ]
[-1  0 -1  1  0  1 ]
[ 1 -1  0 -1  1  0 ]
[-1 -1  0  1  1  0 ].
```

An explicit full column change is

```
W_local =
[ 0  0  0  1  0  0 ]
[ 0  0  0  0  1  0 ]
[ 0  0  0  0  0  1 ]
[-1  0  1  1  0  0 ]
[ 0 -1  1  0  1  0 ]
[ 0  0  1  0  0  1 ].
```

The program verifies

`det W_local=-1`,

`U E W_local = diag(1,1,2,0,0,0)`.                                  (4.4)

The quotient exponent group is therefore `Z³ ⊕ Z/2`. The torsion of order two is real information: replacing the integer lattice by its rational saturation would incorrectly erase the negative branch. The rank condition, not such a saturation, is what eliminates that branch in Lemma 5.

## 5. Signs, branch exclusion, and the formula for B

### 5.1 Sign-equivalence is a consequence of labeled groups

Use

```
H0 =
[1  1  1  1]
[1  1 -1 -1]
[1 -1  1 -1]
[1 -1 -1  1].
```

Suppose a `±1` sign matrix `H` has the labeled group partitions fixed in Section 3. Define

`r_i=H_ia`,       `s_f=H_1f H_1a`,

and normalize by

`N_if = H_if H_ia H_1f H_1a`.

The first row and first column of `N` are all 1. For every other column `f`, `N_if=1` exactly when row `i` is in row 1's group for the pair `{a,f}`. Those groups specify the other three columns uniquely, so `N=H0`. Consequently

`H=diag(r_i) H0 diag(s_f)`.

This uses the labeled, unordered partitions into two groups. It does not require preserving which group was originally named “positive”: multiplying a column by -1 exchanges the names of the groups without changing the partition. Multiplying a row by -1 changes neither product in that row.

As a separate finite-alphabet check, the program enumerates all 65,536 sign matrices. There are 768 Hadamard matrices of order four and 128 matrices with these fixed labeled group structures. Every one of the latter satisfies the displayed normalization identity. This supports the finite sign fact; the proof above is the reason it holds.

### 5.2 The negative branch is rank one, not another invertible family

On the positive branch, the normalized `u` rows coincide, so with `γ=(1,x,y,z)` we have immediately

`A_C = diag(δ) H diag(γ)`.

On the negative branch, the normalized `u` matrix is `H0 diag(γ)`. Therefore

`A_C = diag(δ) (H0 ∘ H) diag(γ)`.

But `H0 ∘ H` has entry `r_i s_f`, an outer product of two nonzero sign vectors. Thus it has rank exactly one, and the invertible diagonal factors preserve that rank.

Since `A_C B_Cᵀ=16I₄`, taking determinants gives

`det(A_C) det(B_C) = 16⁴ ≠ 0`.

In particular `A_C` has rank four. The rank-one branch is impossible.

There is also a short universal determinant certificate. Before fixing the common sign, strip off the invertible row/column factors from `A_C` to obtain

```
C(t) =
[1  1   1   1 ]
[1  1  -t  -t ]
[1 -t   1  -t ]
[1 -t  -t   1 ].
```

Exact polynomial expansion gives

`det C(t) = -2(1+t)³ ≡ -8(1+t) mod (t²-1)`.

In particular its determinants at the two branches are -16 and 0; at `t=-1` the matrix is literally the all-ones matrix. The verifier checks the full polynomial identity, not merely those two evaluations. Inverting this determinant in the quotient algebra removes precisely the negative component.

### 5.3 Ordinary inverse transpose and the normalization factor

Let `D=diag(δ)` and `Γ=diag(γ)`. Once the positive branch is established,

`A=D H Γ`,

`A⁻¹=Γ⁻¹ H⁻¹ D⁻¹`,

`A⁻ᵀ=D⁻¹ H⁻ᵀ Γ⁻¹`.

Because `H Hᵀ=4I`, one has `H⁻ᵀ=H/4`, not `Hᵀ/4`. Hence

`B=16 A⁻ᵀ = 4 D⁻¹ H Γ⁻¹`.                                         (5.1)

The entries are therefore exactly

`a_if=δ_i ε_if γ_f`,

`b_if=4 δ_i⁻¹ ε_if γ_f⁻¹`.

The direct bilinear check is

`(A Bᵀ)_ij = 4 δ_i δ_j⁻¹ Σ_f H_if H_jf = 16 δ_ij`.

The delivered code verifies this as a Laurent-polynomial identity in eight independent nonzero scaling variables, using a deliberately nonsymmetric Hadamard sign matrix. It also rejects the wrong replacement of `H` by `Hᵀ` and omission of the factor 4. Choosing a nonsymmetric matrix is important: the symmetric Sylvester matrix alone would not detect that transpose mistake.

**Conclusion for Lemma 5:** the stated formula follows. There is no missing complex branch, determinant exception, square-root choice, or hidden positivity hypothesis.

## 6. Independent finite geometry, separated from global algebra

### 6.1 Exact root construction and the two pivots

Use the standard E8 root set

`{±e_i ± e_j : i<j} ∪ {(s_0,...,s_7)/2 : s_i∈{±1}, an even number are -1}`.

The program constructs all 240 roots as **doubled integer vectors**, then chooses one representative for each sign pair by making the first nonzero coordinate positive and sorts the 120 representatives lexicographically. Its root IDs consequently need not coincide with the predecessor's IDs. Every certificate includes the actual doubled vectors, so the correspondence is unambiguous.

For the full unit use

`F0={e0±e1, e2±e3, e4±e5, e6±e7}`,

in that pair order, with `+` before `-`. For P112 remove `F0` and use the live pivot

`F1={e0±e2, e1±e3, e4±e6, e5±e7}`.

The coordinate permutation swapping 1 with 2 and 5 with 6 maps `F0` to `F1`, preserves the E8 root set, and is an involution. The latter pivot is also exactly the union of the even classes in the first `F0` support block and its complement, as in the pinned construction recipe. The program checks that equality by reconstructing those classes, rather than by importing a predecessor index list.

For doubled vectors `v_i`, Gram entries are `v_i·v_j/4`. Every division is checked to be exact; the diagonal is 2 and off-diagonal entries are 0 or ±1. The program checks the pivot identities and the integer reconstruction

`2 v_i = Σ_f ε_if v_f`

for every nonpivot line. Thus the orthogonality formula follows directly:

`2 G_ij = Σ_{f∈T_i∩T_j} ε_if ε_jf`.                                 (6.1)

### 6.2 Why the blocks are affine planes

Label the eight ordered pivot points by 0,...,7, or equivalently by `(u,s)∈F₂²×F₂`, with each pair `{2a,2a+1}` corresponding to fixed `u` and varying `s`.

Relative to `F0`, integer roots outside the pivot use one coordinate from each of two different original coordinate pairs. Their support is the union of the corresponding two vertical pivot pairs. This gives six supports, each with eight root lines.

A half-integral root is nonorthogonal to exactly one pivot in each original pair. The number of pairs where its signs disagree is even. Thus its support is the graph `s=h(u)` of a Boolean function on four points with even truth-table parity. Such a function on `F₂²` is affine: in its unique multilinear expression, the parity of its four values is precisely the coefficient of `u₁u₂`. This gives the other eight supports, also with eight lines each.

The six unions of two vertical pairs are the vertical affine planes, and the eight graphs of affine functions are the other affine planes. Thus the support system is exactly all 14 affine planes in `F₂³`. The coordinate permutation above gives the same identification relative to `F1`.

Explicitly, in the ordered pivot labels the blocks are

```
0123  0145  0167  0246  0257  0347  0356
1247  1256  1346  1357  2345  2367  4567.
```

Equivalently they are `{k : a·k=b}`, for nonzero `a∈F₂³` and `b∈F₂`.

Now the needed design properties have direct proofs:

- Three distinct points have two distinct nonzero difference vectors, which are linearly independent over `F₂`. Their affine span is the unique plane containing the triple.
- A pair with difference `d≠0` lies in one plane for each nonzero normal perpendicular to `d`; there are exactly three such normals.
- Two distinct planes are either parallel and disjoint, or intersect in a one-dimensional affine subspace with two points.
- A plane's complement is the other coset of its two-dimensional direction space.

The program independently checks the resulting 56 triple incidences, 28 pair multiplicities, every block intersection, and all complements. This geometry is not being extrapolated from a small selection of blocks.

### 6.3 Classes and sign groups

On each support, all 16 sign vectors occur as roots before taking the overall-sign quotient, giving eight root lines. The parity of the number of negative signs is unchanged by reversing all four signs. Hence the lines split into two classes of four.

Two distinct sign lines of the same parity differ, modulo overall sign, in exactly two positions. Their sign inner product is zero. The four sign rows therefore form a Hadamard matrix. Distinct classes have odd sign distance and give nonzero root inner products.

For any pair of columns, their product has two positive and two negative entries, because the columns are orthogonal. A complementary pair gives the same partition, since the product of all four signs is constant within a parity class. The three partitions are distinct: if two coincided, two rows in their common group would agree up to a common sign in three columns, and parity would force the fourth as well, contradicting row orthogonality.

Relative to `F1`, the removed `F0` lines constitute the even classes on supports `0123` and `4567`. Consequently P112 has two wholly absent classes and 26 complete live ones; every block still has a complete class. P120 has all 28. Both assertions are checked directly against the independently generated vectors.

### 6.4 The witnesses are consequences of the stronger geometry inputs

For a chosen group of a class on support `S` and a pair `{k,l}⊂S`, there are two other blocks through that pair. Either other block has a complete live class. In such a class the sign product in columns `k,l` takes each value twice; choosing the opposite sign product gives live rows orthogonal to both members of the original group by (6.1).

Thus existence of Lemma 5's witnesses follows already from the design, the complete-class coverage, and the sign-product rule. Its separate finite census is useful, but it is not an additional unexplained existence assumption once those stronger inputs hold.

Similarly, for complete classes in different blocks sharing a pair, every fixed row in one class has exactly two orthogonal rows in the other. This gives Lemma 6's witnesses in both orders. The program checks all of them and includes their root IDs in the optional generated certificate.

No Weyl-group transitivity census or result for an arbitrary other puncture was needed or claimed here. The finite reconstruction covers these two explicit pivot/live-set configurations. Transport to other configurations would require the corresponding external symmetry or geometry input.

## 7. Lemma 6: overlap comparison and global potential

### 7.1 The overlap equation has the claimed orientation

Let `C,C'` be complete classes on distinct blocks with overlap `{k,l}`. Choose orthogonal rows `i∈C`, `j∈C'`, as above. Using the class formulas from Lemma 5, their two-term equation is

```
0 = 4 δ_i/δ_j [ ε_ik ε_jk (γ^C_k/γ^C'_k)
              + ε_il ε_jl (γ^C_l/γ^C'_l) ].
```

The prefactor is nonzero. Equation (6.1) says

`ε_ik ε_jk = -ε_il ε_jl ≠ 0`.

Dividing and rearranging gives first

`γ^C_k/γ^C'_k = γ^C_l/γ^C'_l`,

and equivalently

`γ^C_k/γ^C_l = γ^C'_k/γ^C'_l`.                                     (7.1)

There is no reversal of one class's ratio and no surviving minus sign. The independent normalizations of the classes only change every `γ^C` by a common factor, so (7.1) is invariant under that freedom.

### 7.2 Why the pair ratio is well-defined, including two classes in one block

For a pair `{k,l}`, make a graph whose vertices are all complete live classes containing that pair. Join classes in different blocks. Distinct blocks through the pair intersect in exactly that pair, so every such edge supplies (7.1).

Classes in different blocks are adjacent. If two classes lie in the same block, there is a class in another block through the pair, because the pair lies in three blocks and every block has a complete class. The two classes are therefore connected by a path of length two. This is essential: the proof does **not** assume a direct orthogonality equation between the two classes of one D4 block.

Accordingly define, for `k≠l`,

`ρ_kl = γ^C_k/γ^C_l`

in any complete class through the pair. The definition is independent of the class. Set explicitly

`ρ_kk=1`,       `ρ_lk=ρ_kl⁻¹`.

These diagonal and reciprocal conventions make the degenerate cases unambiguous. They are a harmless notational expansion of the pinned proof, not a new hypothesis.

### 7.3 Why local ratios become a global potential

For three distinct points `k,l,m`, choose a complete class in the block containing their triple. Within that class,

`ρ_kl ρ_lm = (γ_k/γ_l)(γ_l/γ_m) = γ_k/γ_m = ρ_km`.                  (7.2)

It is important that **a complete class** exists on that block; the incidence of an empty support block alone would not supply these ratios.

Fix base point 0. Put

`g_0=1`,       `g_k=ρ_k0` for `k≠0`.

For distinct nonzero `k,l`, (7.2) on the triple `{k,l,0}` gives

`ρ_kl = ρ_k0/ρ_l0 = g_k/g_l`.

If one point is 0, the conclusion follows from the definition and reciprocity. If `k=l`, it follows from `ρ_kk=1`. Thus it holds for every ordered pair, with no exception at the chosen base point.

For a complete class `C`, choose any `a∈T_C` and let

`c_C=γ^C_a/g_a`.

Then (7.1) and the potential formula imply

`γ^C_k/γ^C_a = g_k/g_a`, hence `γ^C_k=c_C g_k`

for all `k∈T_C`. All scalars involved are nonzero. A different anchor gives the same `c_C`. The potential is unique up to a common factor before fixing `g_0=1`.

**Conclusion for Lemma 6:** the stated gluing follows. Pairwise agreement alone would not in general suffice; the triple coverage is exactly what kills the potential holonomy here.

## 8. Integral gluing certificates, not rational samples

The multiplicative reasoning in Section 7 already proves the lemma over every permitted field. The following certificates make its integral content directly replayable.

### 8.1 The elementary triangle contraction has determinant one

Orient edges from the smaller point to the larger point. Order the 28 edges of the complete graph as the seven star edges `(0,j)`, followed by the 21 edges `(i,j)` with `1≤i<j≤7`.

Keep the star edges as basis vectors and replace each nonstar edge by

`b_ij = e_0i + e_ij - e_0j`.

The resulting 28×28 integer change-of-basis matrix has block form

```
[I_7   0   ]
[T     I_21].
```

Its determinant is 1. The last 21 rows are exactly triangle boundaries, which map to zero under the edge-to-vertex incidence map. Therefore these triangle relations leave a free rank-seven quotient, not a quotient with unobserved torsion. The program constructs the full matrix and checks its determinant and incidence identities exactly.

This is an elementary substitute for an appeal to simple connectedness. Any cycle can be contracted by the fan of triangles through the base vertex.

### 8.2 A certificate on the actual class-coordinate variables

Let there be `n` complete live classes, so there are `N=4n` nonzero variables `γ^C_k`. Let `e_Ck` denote the corresponding basis element of the free exponent group `Z^N`.

For each unordered pair of complete classes on distinct blocks with intersection `{k,l}`, choose the fixed orientations `C<C'` and `k<l`, and include the relation row

`m = e_Ck - e_Cl - e_C'k + e_C'l`.

Collect these rows in `M_glue`. They are precisely the exponent equations furnished by (7.1). Repeated row-pair witnesses give the same relation; none is replaced by a numerical estimate.

Construct the parameter matrix `P`, of size `N×(n+7)`, by the monomial map

`γ^C_k = c_C g_k`,       `g_0=1`.

In exponent notation each row has a 1 in the column for `c_C` and, when `k≠0`, a 1 in the column for `g_k`. Immediately `M_glue P=0`.

For each `k≠0`, choose a fixed complete class `S_k` through `{0,k}` and define the exponent row

`G_k = e_Sk,k - e_Sk,0`,       `G_0=0`.

For each class choose an anchor `a_C` and define

`C_C = e_C,a_C - G_a_C`.

The rows `C_C`, followed by `G_1,...,G_7`, form an integer matrix `Q` of size `(n+7)×N`. Substituting the parameter map gives exactly `Q P=I`. This is a literal integral retraction, not a logarithm operation on field elements.

It remains to certify every residual row of `I-PQ`. For a class through `{k,l}`, write

`R_C(k,l)=e_Ck-e_Cl`.

A pair-class graph edge yields `R_C-R_C'` as one signed row of `M_glue`. A same-block comparison uses a two-edge bridge. Thus each transfer

`R_C(k,l)-R_D(k,l)`

has an explicit integer expression in at most two overlap relations.

For a coordinate `k` of class `C`, with anchor `a`, the residual is

`R_C(k,a) - G_k + G_a`.

If `k=a`, the residual is zero. If `a=0` and `k≠0`, it is a single transfer to `S_k`. If `k=0` and `a≠0`, it is the signed pair transfer `-[R_C(a,0)-R_Sa(a,0)]`. The implementation chooses the smallest support coordinate as anchor, so this last case does not arise in its actual certificates. For arbitrary anchors it completes the argument. In the remaining case `0,a,k` are distinct; choose a complete class `D` on their triple and use the exact identity

```
R_C(k,a)-G_k+G_a
 = [R_C(k,a)-R_D(k,a)]
 + [R_D(k,0)-G_k]
 - [R_D(a,0)-G_a].                                                (8.1)
```

Each bracket is a pair transfer. Hence every residual is an integer combination of at most six elementary overlap edges before cancellations. The program constructs these coefficients as the rows of `W_glue`, and checks

`I_N - P Q = W_glue M_glue`.                                       (8.2)

For the deterministic choices in the generated certificate, the actual maximum sum of absolute coefficients in a row of `W_glue` is only **3**, for both units. The proof needs only the general bound six.

### 8.3 Why these identities prove saturation and global existence

The integer equalities

`M_glue P=0`, `Q P=I`, `(8.2)`

have two consequences.

First, for any coefficient field and any nonzero `γ` satisfying the monomial relations, compute parameters by the monomials in `Q`. Equation (8.2) says the quotient of each original coordinate and its reconstructed `c_C g_k` is a product of relation monomials, and is therefore 1. This proves existence. The equation `QP=I` proves uniqueness with `g_0=1`.

Second, consider the homomorphism of free abelian groups `v↦vP`. If `vP=0`, then

`v=v(I-PQ)=v W_glue M_glue`,

so `v` belongs to the integer row lattice of `M_glue`. Conversely, every relation row maps to zero because `M_glue P=0`. The map is surjective because `QP=I`. Consequently

`Z^N / row_Z(M_glue) ≅ Z^(n+7)`.

This proves saturation and excludes every hidden finite cyclic factor. The rank of the relation lattice is

`4n-(n+7)=3n-7`,

giving 71 for P112 and 77 for P120. This conclusion was not obtained by rounding numerical ranks or computing only a rational nullspace.

The optional generated certificate contains the actual sparse integer matrices `M,P,Q,W`, every coordinate label, the anchor choices, the base-pair representative classes, all overlap edges and orthogonal witnesses, and all root representatives. Its constructor is entirely printed in `verify.py`; no saved or external archive-only witness is essential.

## 9. Failure controls and what each one actually demonstrates

All controls below were executed. Counterexamples here concern the explicitly stated relaxed local or abstract systems; none is presented as a counterexample to the original E8 theorem.

### 9.1 Damaged local and global certificates

Changing an entry of the local unimodular matrix makes the exact Smith identity fail. Changing a coefficient of a gluing reconstruction row makes `I-PQ=WM` fail for each unit. Separately, changing the saved Smith diagonal from 2 to 1 makes an optimized verifier process reject the saved certificate and exit with code 1.

These controls test certificate checking, not the truth of the predecessor's DRUP refutations. Those refutations are outside this audit.

### 9.2 Deleting the quadratic relations loses the two-branch conclusion

The three ratio equalities alone allow `p=q=r=t` for any nonzero `t`. The exact assignment `t=2` gives the six monomial values

`1,4,1,4,1,4`.

Thus the product-equals-one relations cannot be silently discarded. This also explains why retaining the torsion-2 invariant in the integer certificate matters.

### 9.3 Dropping nonzeroness admits a nonsingular local boundary solution

Let `P` be the permutation matrix with row-to-column permutation `(0,2,3,1)`, and put `A=B=4P`:

```
P =
[1 0 0 0]
[0 0 1 0]
[0 0 0 1]
[0 1 0 0].
```

Then `ABᵀ=16I₄`, and all twelve prescribed group minors for `H0` vanish. Nevertheless `A` has zeros and cannot be a nonzero row/column scaling of a sign matrix. The program checks the identity and every group minor. This is a genuine boundary counterexample to dropping nonzeroness from the **local minor classification**, not to the full witnessed E8 system.

### 9.4 An isolated complete class is not enough

Let `J` be the 4×4 all-ones matrix and take

`A=I+J`,       `B=16(I-J/5)`.

Both are entrywise nonzero, `ABᵀ=16I`, and `det A=5`. But the minor on rows 1,2 and columns `a,b` is `2·2-1·1=3`, whereas a cross-block witness would force it to vanish. Thus zero exclusion and the complete-class identity alone do not imply Lemma 5. This independent control is different from the predecessor's Pascal-matrix example.

### 9.5 Wrong transpose, missing factor, and characteristic two

The symbolic nonsymmetric-Hadamard test rejects `Hᵀ` in place of `H` in (5.1), and rejects replacing the coefficient 4 by 1.

Over characteristic two, `16I=0`; the matrix identity no longer forces invertibility. For instance, `A=B=J` gives `ABᵀ=0=16I` modulo 2 while `A` is singular. The program checks this exact obstruction. This is why the field discussion below explicitly excludes characteristic two; it is not a claim about characteristic-zero coefficients.

### 9.6 Unglued class scalings violate an actual overlap equation

Keep the valid class formulas, but multiply just one coordinate of one class's `γ` by 2. Within that class the dual formula for `B` still preserves `ABᵀ=16I`. On a recorded orthogonal overlap witness, the cross-block two-term expression becomes exactly +4 or -4 instead of zero. The program checks an actual such witness in each unit.

This control distinguishes within-class duality from the extra gluing constraint. The positive gluing proof does not rely on this rational example.

### 9.7 Pair coverage and overlap agreement do not alone imply a potential

Here is an explicit abstract atlas on six points, deliberately **not** an E8 puncture:

```
S0={0,1,2,3},    γ0=(1,1,1,1),
S1={2,3,4,5},    γ1=(1,1,1,1),
S2={0,1,4,5},    γ2=(2,2,1,1).
```

Every pair of points belongs to a block. Each pair of blocks meets in two points, and their ratios agree on the intersection. Thus every pair ratio is well-defined. But

`ρ_02 ρ_24 ρ_40 = 1·1·(1/2) = 1/2`,

so a global potential is impossible. The triple `{0,2,4}` has no covering block.

The verifier checks the full pair coverage, all overlaps, and that loop product exactly. This shows why a proof of globality needs cycle-filling information beyond connectedness and pairwise overlap agreement. It does **not** claim that removing one triple from the E8 design necessarily breaks gluing, nor that the remaining original Steiner axioms can be held fixed while independently removing a redundant axiom. A separate deliberately damaged 13-block E8 list is rejected as failing the stated design inputs; that is a data-validation control, not a new puncture analysis.

## 10. Field hypotheses and separately identified weakenings

### 10.1 Original audit conclusion

Characteristic zero is sufficient. Every division is by a hypothesized nonzero scalar or by a nonzero integer power of 2. The bilinear kernel argument, polynomial factorization, inverse transpose, and multiplicative gluing all work over `C` without conjugation. No real-analytic or positivity step is hidden in these two lemmas.

### 10.2 A scoped algebraic weakening, not a new E8 theorem

The two lemmas' algebra in fact uses only a field of characteristic different from 2, provided the same fixed signed geometry, complete-class identities, cross-block equations, and nonzero-entry premise are supplied. The written derivations and integral/polynomial certificates show this directly. We do **not** assert a new zero-exclusion theorem, a new decoder-cost theorem, or a finite-characteristic multiplication theorem on this basis.

Over general rings, “nonzero” does not justify division, and `t²=1` need not imply a global choice of `t=±1`. For example, `(1,-1)` in the characteristic-zero ring `Q×Q` is neither global sign but squares to 1. The user specified a field, so this is not an objection to the audited claim. No unmentioned general-ring theorem is used here.

### 10.3 A scoped geometric weakening of the scalar gluing statement

For the abstract scalar gluing step, uniqueness of the block containing a triple is unnecessary; existence is sufficient. Indeed, after pair-ratio independence is established, the base-point proof needs only the 21 triples `{0,i,j}`, not all 56 triples.

More precisely, form a separate graph for each coordinate pair, with vertices the complete classes containing that pair and edges established equalities of the ratio at that pair. The same scalar proof works if each such graph is nonempty and connected, and every triple through a fixed base point lies in some class with a local potential. An aggregate overlap graph or an overlap without an established ratio equality does not suffice. These are sufficient conditions, not a claim of necessity. Transfer paths under this weakening need not retain the original two-edge bound. The integer retraction gives a more general cycle-filling viewpoint.

This weaker proposition is separated from the original audit. No new live set is tested against it, and none of the existing P111/P104/P110 extension work is repeated. For the original two units we use and independently verify the full stronger hypotheses.

## 11. Reproduction and limits

Run from this package directory with Python 3.12 and the standard library:

```sh
python3 -I -B verify.py
python3 -I -O -B verify.py
```

Expected: 28 named checks for each command, exit status 0. The registered
repository replay runs the second command. The code does not import predecessor
code, access the network, call a solver, or use random samples. Guards use
exceptions and remain active under `-O`.

Every required finite witness and integer matrix is deterministically generated
in memory by `verify.py`. The optional
`--certificate-out PATH` and `--out PATH` arguments write a fresh certificate and
execution report; the default commands write nothing. An optional
`--check-certificate PATH` adds a 29th check against a saved certificate. This
compares parsed mathematical content, so whitespace is irrelevant. The redundant
generated certificate is omitted from the package; the historical 29-check replay
and tamper rejection remain recorded above.

The canonical certificate SHA256 is
`102cb8ddda027286b010b6edfd80c2b1c201a24020dfe32b0caee0f2a827c57e`.
The unchanged research-session verifier SHA256 is
`224355b93102d22bea4bc8c818baa13cfc9149f9e2752ec1722b959b77d59c42`.

Exact upstream commit, Git blob and SHA256 pins are recorded in
`SOURCES.json` under `external_predecessors`. Those are source-attribution pins,
not runtime inputs validated by the generic metadata hook. The new verifier is
self-contained. The selected record and task catalogue are historical provenance
at the recorded main base.

The predecessor checker was separately replayed during coordination (61 P112
checks and 41 P120 checks). That execution is not part of this new checker's
coverage and does not independently prove zero exclusion. The audit retains that
premise. No PR717/PR968 theorem audit, arbitrary-frame symmetry transport,
P111/P104/P110 extension, physical realization, all-size/precision/tape/analytic
transfer, full selected cold replay, or proof-assistant formalization is claimed.

## Public references

[pr]: https://github.com/CrocSwap/integer-mult-bounds/pull/1212
[claim]: https://github.com/CrocSwap/integer-mult-bounds/discussions/1448

- [Pinned proof, audit target](https://raw.githubusercontent.com/burntout76/integer-mult-bounds/57099cb5684f38877f31d149d598801671a633db/research/complex-rank8-decoder-rigidity/PROOF.md), especially Sections 1–6 and the coefficient scope note in Section 9.
- [Pinned predecessor verifier, separately replayed](https://raw.githubusercontent.com/burntout76/integer-mult-bounds/57099cb5684f38877f31d149d598801671a633db/research/complex-rank8-decoder-rigidity/verify.py), especially the root and pivot definitions and the descriptions of its finite checks.
- [Pinned README](https://raw.githubusercontent.com/burntout76/integer-mult-bounds/57099cb5684f38877f31d149d598801671a633db/research/complex-rank8-decoder-rigidity/README.md).
- [Pinned source manifest](https://raw.githubusercontent.com/burntout76/integer-mult-bounds/57099cb5684f38877f31d149d598801671a633db/research/complex-rank8-decoder-rigidity/SOURCES.json).
- [PR717 model credit](https://github.com/CrocSwap/integer-mult-bounds/pull/717) and [PR968 credit](https://github.com/CrocSwap/integer-mult-bounds/pull/968). Their full theorems are not independently audited in this package.
