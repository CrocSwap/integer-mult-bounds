# The semilocal two-role theorem

Let `K` be a field in the centre of an associative unital algebra `R`.
The paid alphabet is `I+u y^T`, with `u in R^2` and `y in K^2`, and free maps
are common `GL_2(K)` maps. Cost and delta have the meanings of
[#4276](../right-vector-two-factor-criterion/PROOF.md). In particular,

`delta_R(M) = min_{T in GL_2(K)} dim_K (MT-I)K^2`.

Assume `R` is semilocal: its Jacobson radical `J` has quotient
`R/J = product_i M_{d_i}(D_i)`, for finitely many division rings `D_i`.
This includes every finite-dimensional `K`-algebra. The quotient contains
the same central field `K`. The zero algebra is excluded.

## The new statement

For every `M in GL_2(R)`:

1. Three paid factors suffice, with the fixed right vectors `e1,e2,e1`.
   No free map is needed for this upper bound.
2. `cost_R(M)<=2` holds exactly when `cost_{R/J}(Mbar)<=2`.
3. `cost_R(M)=max(delta_R(M),cost_{R/J}(Mbar))<=3`.

This settles the semilocal matrix-block question in #4601. That predecessor
proves the formula for products of local algebras. ToikY's #4334 proves the
field-product case and supplies its three-factor construction. The new step
here allows arbitrary matrix blocks in the semisimple quotient and does not
require `R` itself to split as a product of local algebras. The one/two-factor
criteria and delta lower bound are inputs from #4276/#4243/#4099.

The unit-completion argument below is the classical stable-range-one
argument, included to specify sides and coefficient types. Stable range and
ordinary ring-matrix elimination are not claimed as new. For historical
context see Ara, Pedersen and Perera, [*An infinite analogue of rings with
stable rank one*, introduction](https://arxiv.org/abs/math/9910131v2).
The contribution is its application to this restricted-right-vector cost
question and its exact radical consequence.

## 1. Units and one-sided inverses

An element of `R` is a unit exactly when its image modulo `J` is a unit.
Indeed, lift an inverse to `y`, so `xy=1+j` and `yx=1+k` for `j,k in J`.
The elements `1+j` and `1+k` are units by the Jacobson-radical property.
Thus `y(1+j)^(-1)` is a right inverse of `x`, and `(1+k)^(-1)y` is a left
inverse. A left and a right inverse agree. The converse follows by projection.

Every right-invertible element in `R` is a unit. Project a right inverse to
each finite matrix ring over a division ring, where a right inverse is an
inverse by finite-dimensional linear algebra, and use the preceding paragraph.

## 2. Complete a unimodular block row to a unit

Suppose `aR+bR=R`. We prove that some `f in R` makes `a-bf` a unit.
Work first in one quotient block `M_d(D)`, acting on the right vector space
`V=D^d`. Since `aR+bR=R`, `im(a)+im(b)=V`.

Choose a complement `U` of `ker(a)` in the domain. Then `a` maps `U`
isomorphically onto `im(a)`, and
`dim ker(a)=dim V/im(a)`. The map induced by `b` onto `V/im(a)` is onto.
Choose a right-linear map `f` on `ker(a)` so that `b f`, followed by the
quotient map, is an isomorphism `ker(a) -> V/im(a)`. Extend `f` by zero on
`U`. On `U`, `a-bf=a` has image `im(a)` and is injective. On `ker(a)`, its
image projects isomorphically onto the quotient. Therefore `a-bf` is bijective.

Make these choices independently in every quotient block. Lift the resulting
element `fbar` to `R`. The lifted `a-bf` has unit residue, so it is a unit by
section 1. In particular, no idempotent lifting or splitting of `R` is assumed.
The coefficient `f` is algebra-valued. Restricting it to `K` is unjustified.

## 3. Three factors with base-field right vectors

Write `M=[[a,b],[c,d]]`. Its first block row is right unimodular, because
the first column of `M^(-1)` gives `ax+by=1`. Choose `f` as above and put

```text
e = a-bf,
g = (c-df)e^(-1),
h = d-gb.

F1 = [[1,0],[g,1]]   = I + (0,g)^T e1^T,
F2 = [[1,b],[0,h]]   = I + (b,h-1)^T e2^T,
F3 = [[e,0],[f,1]]   = I + (e-1,f)^T e1^T.
```

Multiplication in the indicated algebraic order gives

```text
F1 F2 F3 = [[e+bf,b],[ge+(gb+h)f,gb+h]]
          = [[a,b],[c,d]] = M.
```

All three right vectors are in `K^2`; the algebra coefficients occur only on
the left. `F1` and `F3` are invertible, since `e` is a unit. Therefore
`F2=F1^(-1) M F3^(-1)` is invertible, which also proves that `h` is a unit.
Every prefix in either product or execution order is invertible. A column
execution applies `F3`, then `F2`, then `F1`. There is no scratch register and
the identity holds on arbitrary input data.

## 4. The two-factor threshold and radical formula

By #4276, `cost_R(M)<=2` exactly when some `G,H in GL_2(K)` give `N=GMH`
with `N12 in N11 R`. For an invertible `N`, its first row is right unimodular.
Writing `N12=N11 z` shows that `N11` is right-invertible, hence a unit by
section 1. Conversely, a unit `N11` gives the required ideal membership.
Thus the threshold is equivalent to

`there are G,H in GL_2(K) for which (GMH)11 is a unit`.

Equivalently, some common nonzero base-field row `phi` and column `t` have
`phi M t` a unit. Every nonzero row and column extends to an invertible
base-field matrix. The word "common" is essential across quotient blocks.

Units lift and descend through `J`, and the same `G,H` work on both sides.
This proves item 2. Projection also gives
`cost_R(M)>=cost_{R/J}(Mbar)`. The column bound gives
`cost_R(M)>=delta_R(M)`.

If the residue cost is 3, the three-factor upper bound proves item 3.
Otherwise item 2 gives `cost_R(M)<=2`. If `delta_R(M)<=1`, #4276's one-factor
theorem gives `cost_R(M)=delta_R(M)`; projection makes the residue cost no
larger. If `delta_R(M)=2`, both sides of item 3 equal 2. These exhaust the
possibilities, since `delta_R(M)<=2`.

## 5. A matrix-block family attaining three

Take `R0=M_2(F_2)` and the established #4265/#4276 sharp target

```text
a=E11, b=E01, c=E10, d=E00,
```

where indices are 0,1. The flattened 4x4 matrix exchanges coordinates 0 and 3.
All nine common base-field row/column pivots are singular. For example,
`a-bf` is singular for both scalar choices `f=0,I`, whereas `f=E10` gives
`a-bf=I`. This is a fixture distinguishing the matrix-block
completion from a scalar-only pivot choice. Its sharp residue cost is
predecessor credit, not a new counterexample.

Now take the new lifting family `R=M_2(F_2[e]/e^2)`. For every
`X in M_4(F_2)`, let `M_X=M_0+eX`, viewed as a 2x2 matrix over `R`.
Its residue `M_0` is invertible. Explicitly

`M_X^(-1)=M_0^(-1)-e M_0^(-1)X M_0^(-1)`.

All `2^16=65,536` targets are distinct and invertible. Items 1 and 2 prove
that every one costs exactly 3. The verifier enumerates each lift, checks
every common pivot, constructs its actual three-factor word using the lifted
pivot inverse, and checks its action on all eight binary basis coordinates.
It also constructs words for all 20,160 elements of `GL_4(F_2)` in the
matrix-block residue ring. These are finite corroborations of the written
theorem; they do not establish an unbounded theorem by enumeration.

## Limits

The target must be invertible, the role count is two, and `R` is semilocal.
This does not settle the singular-target question of #4276/#4601. The
construction is a formal alphabet with unpriced algebra-valued left vectors
and common free base-field maps. Preparation, conversion, routing, control,
precision, restoration and stock costs for a native implementation are unknown.
No supplier admission, new kappa or complete multiplication theorem follows.
Independent human and formal proof-kernel review are unclaimed.
