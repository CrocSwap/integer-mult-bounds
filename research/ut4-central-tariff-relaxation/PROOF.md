# UT4 central tariffs with arbitrary restored dirty workspace

This is a written uniform lower bound and an exactly solved necessary
coefficient relaxation. Full multi-target word optimality remains open.
Finite programs corroborate the algebra and fixtures; no kernel theorem,
physical supplier, paid rank profile or multiplication exponent is claimed.

## Model, hypotheses and complete abstract bill

All coefficients and ranks are over **F2**. Let `G=UT4(F2)`, the group of
upper unitriangular four-by-four binary matrices. Write

```
a=I+E12, b=I+E23, c=I+E34, z=I+E14.
```

These are involutions; `z` is central. Work in the **full formal group algebra**
`R=F2[G]`. For every finite pair of integers `r>=w>=1`, a legal paid factor is

```
D_N(g)=I_r+([g]+1)N,    g in {a,b,c},
N=x y^T,    x,y nonzero binary r-vectors.
```

The scalar coupling may be idempotent or nilpotent. Every factor is an
involution because `([g]+1)^2=0`; no condition on `N^2` is used.
The target is `T=I_r+([z]+1)P`, `P=diag(I_w,0_(r-w))`. All roles have arbitrary
input; every one of the `r-w` extra roles is restored as an operator. A common
scalar conjugate of `P` gives the same result.

Scalar `GL_r(F2)` maps are optimistically free. Move them to one end by
conjugating each rank-one coupling. Augmentation `[g]->1` sends every paid
factor and the target to identity, so the remaining scalar map is identity.
There are no other free address maps, initialized workspace, COPY, ERASE,
higher-rank paid factors or uncharged inverses. Every occurrence, including
restoration, is counted. Uniform positive prices are `alpha,beta,gamma` for
`a,b,c` respectively; role-dependent and physical implementation prices are
outside this tariff statement.

This changes the rational abelian three-register model to one explicitly
specified nonabelian binary group. It does not reduce rational frames modulo
two or establish a rational-frame identity. The group is fixed; no all-size
supplier/compiler claim follows from its formal identities.

## Uniform separate-generator theorem

Every legal word equal to `T`, of any length and with any finite dirty workspace,
satisfies

```
n_a >= 2w,    n_c >= 2w,    n_b >= 3w+[w=1].
```

Therefore its complete abstract tariff is at least

```
2w alpha + (3w+[w=1]) beta + 2w gamma.
```

For unit prices this is `7w+[w=1]`. One direct eight-call word per target
gives the upper bill `8w`; the lower and upper bills coincide only at `w=1`
in the results proved here. In particular one target costs **exactly eight**,
or `2alpha+4beta+2gamma`, for every `r>=1`. For `w>=2`, the lower tariff is
not claimed attainable by a full formal word.

## Outer letters: two representations are necessary

Use the natural representation of `G`. Reorder the evaluated register matrix
into four address blocks of size `r`. A paid factor becomes `I+E_edge tensor N`.
The first-order blocks are the separate sums of the scalar couplings. The
two length-two blocks are the ordered `AB` and `BC` coefficients, and the
top-right block is

```
H_abc = sum_(i<j<k, labels a,b,c) N_i N_j N_k.
```

The target implies that all first- and second-order blocks are zero and
`H_abc=P`. Collect each label's column vectors in `X_g` and row vectors
in `Y_g`. Thus `X_g Y_g=sum_g N_j=0`. The column space of `H_abc` lies in
`im X_a`, and its row space lies in `row Y_c`. Hence
`rank X_a>=w` and `rank Y_c>=w`.

Now use the contragredient representation `g -> (g^-1)^T`. This is a
homomorphism: `(gh)^-T=g^-T h^-T`. The three generators become the respective
lower-triangular adjacent units, and `z` becomes `I+E41`. Its length-three
coefficient is

```
H_cba = sum_(i<j<k, labels c,b,a) N_i N_j N_k = P.
```

This gives `rank X_c>=w` and `rank Y_a>=w`. Since `X_g Y_g=0`, the image of
`Y_g` lies in the kernel of `X_g`, so rank-nullity gives
`rank X_g+rank Y_g<=n_g`. For `g=a,c`, both ranks are at least `w`, proving
`n_a,n_c>=2w`. The argument uses rank one and exact restoration, not scalar
idempotence or a bound on workspace.

## Middle letter: the quotient ker(X)/im(Y)

Number the `b` factors in product order. Put `B_j=x_j y_j^T`. Let `P_j` be
the sum of preceding `a` couplings and `Q_j` the sum of following `c` couplings.
Define four matrices of the indicated shapes:

```
X=[x_j]        r by n_b,      Y=[y_j^T]        n_b by r,
U=[P_j x_j]    r by n_b,      V=[y_j^T Q_j]    n_b by r.
```

Direct ordered expansion, without commuting any scalar matrices, yields

```
XY=0,    UY=0,    XV=0,    UV=P.
```

The first identity is the first-order `B` coefficient. The next two are the
`AB` and `BC` coefficients. The last is the `ABC` coefficient. Consequently
`im V` and `im Y` lie in `ker X`, and `U` annihilates `im Y`. The map `UV`
therefore factors through `ker X/im Y`, whose dimension is

```
n_b-rank X-rank Y.
```

Since `rank(UV)=w`, we have `n_b>=w+rank X+rank Y`.
The next fixed-group lemma forces both latter ranks to be at least `w`.

## Fixed degree-three quotient and the missing middle spans

Let

```
Q=F2<a,b,c>/(a^2,b^2,c^2, ac-ca, all monomials of degree >=4).
```

Here letters denote augmentation generators, so group generators map to
`1+a,1+b,1+c`. The basis is exactly

```
1,a,b,c,ab,ac,ba,bc,cb,aba,abc,acb,bab,bac,bcb,cba,cbc.
```

Multiplication concatenates, sorts adjacent `ca` into `ac`, kills adjacent
squares, and kills degree at least four. In degrees at most three these rules
are complete (the possible overlaps `caa` and `cca` reduce to zero in either
order). This also defines a finite algebra with an explicitly checked table.
For coordinates `(A,B,C,D,E,F)` of a group matrix at positions
`12,23,34,13,24,14`, use its unique normal form

```
a^A b^B c^C d^(D+AB) e^(E+BC) z^(F+AE),
d=abab, e=bcbc, z=abcbabcb.
```

In this line the letters denote group generators. Substitute their `1+letter`
images into the displayed word. `quotient.py` verifies **all4,096 products**
of these64 images against literal four-by-four group multiplication, and
all4,913 basis triples for associativity. This finite, fixed-group computation
is the exact homomorphism lemma used here; it is not an enumeration of `r`,
`w` or word lengths, nor a proof-kernel formalization. It gives

```
image(z)=1+abc+acb+bac+cba.
```

Consequently a word with the central target has coefficient `P` on each of
these four basis monomials. Its `bac` coefficient sums scalar products from
both chronological label patterns `bac` and `bca` (`ca=ac`). Every summand
starts with a middle coupling; its column space lies in `im X_b`.
The `acb` coefficient similarly sums `acb` and `cab`; every summand ends
with a middle coupling, and its row space lies in `row Y_b`. Thus

```
rank X_b>=w,    rank Y_b>=w.
```

Combining with the previous quotient proves `n_b>=3w`. At `w=1`, equality
`n_b=3` forces both ranks to be one. Over F2 every nonzero column of `X`
and every nonzero row of `Y` is then identical within its family. All three
middle couplings are the same nonzero matrix; their sum cannot be zero.
Therefore `n_b>=4` at `w=1`, proving `3w+[w=1]` uniformly. Nilpotence of
individual scalar couplings makes no difference.

## Exact optimum of the strengthened middle-factor relaxation

The relaxation retains `XY=UY=XV=0`, `UV=P`, nonzero columns/rows and
`rank X,rank Y>=w`; it does not require a chronological word or every `Q`
coefficient equation. At `w=1`, take length four, `X=Y^T=(1,1,1,1)`,
`U=(1,0,0,1)`, `V=(1,0,1,0)^T` and pad with zero role coordinates.

For every `w>=2`, write `w` as a sum of twos and threes. For a dimension-two
block take six columns

```
e1,e1,e2,e2,e1+e2,e1+e2.
```

For a dimension-three block take all seven nonzero binary columns followed
by two copies of `e1`. Both blocks have full row rank and `XX^T=0`:
among the seven original columns of the three-dimensional block each row
has four ones and each row pair
has two common ones; the two extra identical columns cancel. Direct sums
give a full-rank `w by3w` matrix with no zero column. Set `Y=X^T`.
Then `im Y` lies in `ker X`, and `ker X/im Y` has dimension exactly `w`.
Choose `w` quotient representatives as columns of `V`. Choose the dual
functionals on that quotient, extend them from `ker X` to the ambient
`F2^(3w)` by completing a basis, and use them as rows of `U`.
This proves `UY=XV=0` and `UV=I_w`. Padding yields `P=diag(I_w,0)` for
every `r>=w`. Each individual `x_j y_j^T` is nonzero rank one.
`relaxation.py` constructs the quotient representatives and extensions using
exact binary elimination, with no imports from the primary verifier.

Thus the strengthened necessary factor relaxation attains `3w+[w=1]` for
every `w`. It does not supply paid `a,c` paths realizing `U,V`, or cancel
all remaining formal coefficients. No full-word bound is claimed sharp
for `w>=2`.

The field restriction matters. Over F3, `n=3,w=r=1`, `X=Y^T=(1,1,1)`,
`U=(1,-1,0)`, `V=(1,0,-1)^T` satisfy the same four equations with `UV=1`.
This is only a counterexample to extending the **factor parity lemma** across
fields, not an admitted UT4(F2) word.

## Full formal upper witness and precise failure controls

In `G`, `(abcb)^2=z`. On a coordinate projector, a paid factor acts as `[g]`
on that role and identity on all others. Apply this eight-factor word to each
target coordinate and concatenate: counts are `2w,4w,2w`; all other roles are
untouched and arbitrary dirty. There is no additional preparation or undo in
this abstract construction. It proves the stated upper bill for every `r,w`.

A legal twelve-call two-role word is included as a **specific failed trial**:

```
[(a,1,1),(b,1,1),(c,1,3),(a,3,1),(b,1,1),(c,1,2)] repeated twice,
```

where each tuple gives `(label,x,y)` in binary vector encoding. Its natural
endpoint has zero first/second blocks and `H_abc=I2`, but `H_cba=E11` has rank
one. Its full formal product has37 nonzero group coefficients and fails the
two-target endpoint. This disproves acceptance from the natural relaxation
alone. The new14-call lower bound excludes every twelve-call two-target word
in the stated alphabet, without using that finite trial as an impossibility proof.

The proof images are not faithful on the group algebra, even together.
The nonzero four-term `f=(1+[z])(1+[a])` maps to zero in all three images: its degree in `Q` is at least four, and `E14 E12=0`
and `E41 E21=0`. An off-diagonal `f` perturbation of a target is invisible
to all three images and to clean-extra inputs, but changes all64 dirty-extra basis columns
in the faithful regular representation. This is a nonfaithfulness diagnostic,
not asserted to be a legal paid-letter word. Lower bounds use representations
only as necessary conditions; witness acceptance checks the full formal algebra.

## Credit, evidence boundary and remaining work

Credit steph4n-gh/PR1573 for the UT3 arbitrary-register zero-sum proof;
Arham Tahir/PR1589 for the expanded nilpotent alphabet; Hanson Sun (@bbMisk)/
PR1607 for coefficient-span tariffs, and the retained register-model lineage.
No predecessor executable or unproved conclusion is imported. The new step is
the class-three middle quotient, the mixed middle-span constraints and their
precisely scoped attained relaxation.

The finite certificate checks definitions, complete witnesses, coefficient
formulas and rejection controls. The written rank argument and the fixed finite homomorphism lemma prove
the uniform result. Formalization, sharp full multi-target tariffs, physical/compiler/hosting,
precision/tape and analytic transfer remain open; no selected frontier changes.

Prepared for @ToikY with substantial OpenAI Codex assistance. Apache-2.0.
