# A binary tree of query suppliers

The author-checked complete conditional saving is `kappa = 0.00314933`.
The source comparison is PR6167 at `0.003128645`. The local P104 word does
not change. The new caller changes the complete target and paid profiles.
The selected frontier does not change.

The five retained assumptions are native all-column implementation, owned
erasure, the uniform compiler, precision and tape cost, and analytic
recovery. This proof does not discharge those assumptions. It does not
claim an unconditional integer multiplication theorem or a global optimum.

## 1. Retained interface

Use the complete arbitrary-input P104 interface from
[PR6167](https://github.com/CrocSwap/integer-mult-bounds/pull/6167), with its
all-forward binding from
[PR5544](https://github.com/CrocSwap/integer-mult-bounds/pull/5544).
For each of 104 ports, put `q = Q^-1`. A full call supplies

```text
D [[1, 0], [q, 1]],
```

where D acts on eight fresh axes and commutes with Q. The full call has
562 independent helper inputs and outputs. Its local profiles are

```text
helpers = {1:14, 2:8, 3:4, 4:107, 5:14, 6:2, 7:9, 8:19, 9:385}
paid    = {1:2216, 2:456, 3:496, 4:98, 5:165, 6:8, 7:9, 8:1}
```

The paid rank mass is 5952. The helper rank mass is 4232. The main rank
progress is 1664, so the full call has 56 remaining paid ranks.
All 29 owned labels, 32 lifetimes and peak occupancy 13 remain charged.
No helper input is initialized to zero.

A swap gives the upper query `D U(q)`, where `U(q) = [[1,q],[0,1]]`.
Conjugation by `diag(Q^2,1)` changes q to its inverse. A sign change and
swap give the other orientation. The identity `Q^2 = Q^-2 = X_q` has
absolute phase +1. These wrappers use ordinary signed exchanges and
translations. They do not transpose a COPY or CLEAR instruction.

The thin query of Cinna Davis costs one rank-one Gaussian per port. It
copies the source to an initialized owned field, applies Q or Q^-1, adds
the result, and clears the field. The field receives no productive credit.

## 2. A four-field query extension

Use four arbitrary independent fields `(x,y,a,b)`. Let D_A and D_B be
commuting products on disjoint fresh axes. Suppose two child suppliers
provide `D_A U(q)` and `D_B [[1,0],[-q^-1,1]]` on the first two fields.
Their other independent outputs remain outside this four-field block.

Define ordinary integer maps R, S and L by

```text
R(x,y,a,b) = (x+b, a, x, y)
S(x,y,a,b) = (x+a, y, a, b)
L(x,y,a,b) = (x, b, x-a, b-y).
```

Each map has an integer inverse. The emitted implementation uses only
ADD, SCALE by -1, and SWAP. Let C(q) be the one-query shear

```text
a <- a + q*(b-y).
```

Compute C with `b <- b-y`, one paid query from b to a, and `b <- b+y`.
Let I be the paid idle map

```text
I = diag(1, 1, D_A D_B, D_A D_B).
```

The complete chronological word is

```text
R, C(q), S^-1, I, child B, child A, S, L.
```

Its exact matrix is

```text
D_A D_B * (U(q) direct-sum q direct-sum q^-1).
```

The output on x,y is another query supplier. The outputs on a,b are two
independent Gaussian jobs. They are not owned scratch. The two idle calls
remain in the bill.

To check the identity, work in the Laurent ring `Q[q,q^-1,D_A,D_B]`.
In the S coordinates, both child queries use the first two fields. Their
D factors commute with both queries. I applies the product of those same
D factors to the other two fields. Thus their combined D factor is the
scalar matrix `D_A D_B I_4`. Direct multiplication of the remaining
four-field matrices gives `U(q) direct-sum q direct-sum q^-1`.
[module_check.py](module_check.py) performs this multiplication with exact
rational Laurent coefficients. It does not import the caller generator.
Removing I fails this identity.

This statement also holds after replacing q by q^-1. All scalar signs stay
outside tensor substitution. No finite-order relation for q is used in
the Laurent proof. The native relation for Q^2 is used only to implement
ordinary orientation wrappers.

## 3. Tree composition and independent inputs

A leaf is one full native supplier. A binary node applies the four-field
extension to its two children and adds two new independent input fields.
If a node contains f native leaves, it supplies one query with diagonal
product D on its original two fields. It also supplies two new Gaussian
outputs of rank `1+8f`. Its one thin query costs H1 per port. Its paired
whole idle costs two H(8f) calls per port.

Induction proves this interface. The children have disjoint native stage
sets and disjoint helper inventories. The parent acts only on their shared
query pair and its new pair. It does not change a child's other outputs.
Every new pair is an original arbitrary input pair. All boundary maps are
invertible, so no input dimension is lost.

At the root, combine three query suppliers on one pair:

```text
D_C U(q), D_B [[1,0],[-q^-1,1]], D_A U(q),
then (x,y) <- (-y,x).
```

The root outputs are `D_A D_B D_C * diag(q^-1,q)`.
No new idle is needed at this root. The other outputs of each child remain
independent. The whole word is sequential. Full calls and thin queries can
reuse the source's owned storage without overlapping their lifetimes.

Choose root subtree sizes 4, 7 and 8. Use these fixed trees:

```text
T2 = (leaf, leaf)
T3 = (leaf, T2)
T4 = (T2, T2)
T7 = (T3, T4)
T8 = (T4, T4)
root = (T4, T7, T8).
```

There are 19 native leaves and 16 binary nodes. There are 34 independent
main fields per port. The nonroot node-size counts are
`{2:9, 3:1, 4:4, 7:1, 8:1}`.

[CONTROLLER.json](CONTROLLER.json) contains all 353 instructions. The
literal replay starts with 34 independent variables. It checks every one
of the 1156 matrix entries over the Laurent ring with Q and 19 distinct
stage multipliers. It checks each native stage exactly once. This replay
does not replace the stages by equal variables or use sampled values of Q.

## 4. Native maps and whole jobs

Keep all source words and source bytes unchanged. The source interpreter
checks all 799 public and owned coordinates. Its separate dense transpose
checks all 638401 coefficients in reverse chronology. Its native compiler
and separate Gaussian interpreter check every paid map, helper boundary,
main adapter and absolute phase.

Use stage numbers 1 through 19 and ambient dimension 161. The old nine axes
contain the common central port. Each stage has eight fresh axes. The
retained orthogonal route fixes the central port and moves at most 17 axes.
The adapted physical checker verifies all four source contacts at all 104
ports and 19 stages, for 7904 contacts. The checked diagonal and cross terms
are D_s and D_s Q^-1. This is an arbitrary-input operator interface.
It does not assume that a caller input already has a particular Gaussian
value. Fresh axes are spectators in earlier calls.

For a node with stage set J, the paired idle is the whole product of the
D_s for `s in J`. Its axes are independent and orthonormal. Its rank is
`8*|J|`; it is not priced as separate rank-eight calls. A main target is
`Q^(+1 or -1)` times this product, of rank `1+8*|J|`. A negative central
power differs from the positive Gaussian by its charged ordinary
translation. The physical checker checks all main and idle phases.

## 5. Complete invoice

The fixed local profiles are used 19 times. The following table gives all
additional main targets and whole idle calls.

| Node size | Number of nodes | Main rank | Main fields | Idle rank | Paid idle calls |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 9 | 17 | 1872 | 16 | 1872 |
| 3 | 1 | 25 | 208 | 24 | 208 |
| 4 | 4 | 33 | 832 | 32 | 832 |
| 7 | 1 | 57 | 208 | 56 | 208 |
| 8 | 1 | 65 | 208 | 64 | 208 |
| 19, root | 1 | 153 | 208 | none | 0 |

Add 1664 paid H1 calls for the 16 thin queries. The complete invoice has
14214 productive fields and 70523 paid calls. Its target rank mass is
202088; its paid rank mass is 201280. The surplus is 808. The emitted
instruction count and a separate fixed-tree count must agree exactly.

The source path has 18 full calls and 15 thin queries. Its complete raw
crossing is between 0.00312865201590 and 0.00312865201591. The present gain
comes from a changed caller and a changed complete bill. It is not a
refinement of that source crossing. More native calls and more total calls
do not imply a practical speedup.

## 6. Conditional price and ordinary work

Two retained rational interval engines check the new complete moments.
The raw crossing is strictly between 0.00314934401301 and
0.00314934401302. The claimed saving is 0.00314933 and the tested saving
is 0.003149335.
The complete compiler must use the new target distribution. In particular,
the source cutoff 16/floor 17 completion ratio is above one and is rejected.

The new parameters are power 1024, cutoff 12, floor 13, offset 1/7,
reserve 1e-12 and tail decay 31/32. Both higher-moment and completion ratios
are below that decay, and `(31/32)^128 < 1/16`. The normalized paid bound,
including splitting and rounding, is strictly below one.

The complement factor is 63/64. The logarithm power is 1100, with maximum
target rank 153. The checker gives `N = 2^70855400000000` and rejects the preceding
integer grid point. It evaluates `153^(1024*tested)` by squaring an
outward interval for `153^(512*tested)`. Each exponential stays inside
the retained interval engine's proved domain. It checks all 54 strict outer predicates and all
four functional predicates. The unchanged admitted BIT saving 0.0034 is
larger than the tested complex saving.

The complete ordinary-work count is 194902768, below the allowance 10^9. It includes 19 native source
allowances, all 353 caller instructions, every thin COPY/query/ADD/CLEAR,
every wrapper, route and target normalizer. The source scalar coefficients
have their retained growth bound. The new scalar coefficients are ±1. A
conservative whole-word growth bound is `2^(10^9 + R*f)`, where R is the
complete paid rank mass and f is the tensor width. This is a finite bound,
not a measured norm.

The uniform word and the rounded integer multiplier are not materialized.
The package gives their finite parameters under the retained framework.
Author replay is not independent scientific acceptance or a proof-kernel
verification. No optimality over callers, trees or native words is claimed.
