# Independent review of the last rank9 contraction

The contraction is exact for all 64 preferred paths and both providers.
It replaces one rank7 completion and one rank2 terminal child by one
rank9 child on each path. It removes 64 children. It does not reduce
the native rank mass, which remains 5,600.

## Independent method

The checker imports no producer code. `CHECKS.json` pins the emitted
recipes, native words, permutation suffix, triple terminal, D25 views,
controller, and final scalar gauge.

The phase interpreter uses the convention

```text
i^s X_x Z_z.
```

A positive line gate is

```text
C_q = ((1+i)I+(1-i)X_q)/2.
```

If z dot q is one, its Pauli action changes x to x+q and s to s-1.
If z dot q is zero, it fixes the Pauli operator. The inverse has the
opposite phase change. Binary linear maps act by M on x and M^-T
on z. Diagonal phases are checked from their exact quadratic form.
These rules give a separate implementation of signed Pauli conjugation.

The checker also applies each full circuit to the basis vector at
address zero. It keeps Gaussian integer numerators and an exact power
of two denominator. This check fixes the constant complex phase that
a Pauli tableau cannot see.

All circuit factors are unitary. Equal conjugation on all Pauli
generators implies that two such circuits differ by one scalar.
Equality on a nonzero state fixes that scalar. Thus the two checks
prove operator equality on every input, not only on the tested basis
vector.

## Canonical completion and the exact terminal product

Let M_p be the source endpoint adapter and T_p=M_p C_qp. The retained
Y field is at T_p after its last scalar transfer. Its omitted native
completion and target endpoint adapter have exact operator

```text
R_r = F9 C_qr^-1 C_qp^-1 M_p^-1.
```

The checker derives this operator from the actual serialized rank7
recipe and both endpoint adapters. It verifies the complete signed
Pauli map and global phase.

The seven recorded complement vectors, together with q_r and q_p,
form an orthonormal basis of the nine-dimensional root. For every
one of its 512 characters, the checker verifies

```text
weight(chi)-sum_v (chi dot v) = 2 (Delta dot chi) mod 4.
```

Hence

```text
R_r = X_Delta (product_j C_uj) M_p^-1.
```

Let rho be the literal stage-two route, e its exit translation, A
the inverse-triple owner map, and delta the complete triple Fourier
translation. The preceding raw terminal contributes X_qr. The exact
ordered terminal path is

```text
-X_delta C_a C_b^-1 P_A X_qr X_e P_rho R_r,
a=q_p,                   b=A q_r.
```

Since P_A X_qr=X_b P_A and C_b^-1 X_b=C_b, this becomes

```text
-X_tau C_a C_b (product_j C_(A rho uj)) P_(A rho) M_p^-1,
tau=delta+A(e+rho Delta).
```

The nine displayed directions are orthonormal on every actual path.
Their full product therefore has Fourier rank nine. The checker also
finds rank nine directly from the X components of the images of the
25 Z generators.

Each emitted right wrapper includes M_p^-1 and A rho. Each left
wrapper includes the exact translation tau. The complete serialized
wrappers, the positive H9 child, and the scalar minus sign are compared
with the ordered old circuit. Wrong-sign and wrong-translation controls
are rejected on every path.

There is a matching local rank obstruction. For a Clifford operator,
write its binary Pauli matrix as [[A,B],[C,D]], so B contains the X
parts of the images of Z generators. Composition gives

```text
B_(12) = A_1 B_2+B_1 D_2,
rank(B_(12)) <= rank(B_1)+rank(B_2).
```

A monomial Clifford has B=0. A rank-k native child, with monomial
wrappers, has rank(B)=k. Consequently any such circuit on this one
field has total native rank at least rank(B_target)=9. The old 7+2
word and the new rank9 word both attain this local bound.

Here the input basis is the physical computational-address basis of
the deferred Y field at its canonical T_p cut. The target operator
ends in the raw output-p chart after the full terminal. Its right
side includes M_p^-1, and its left side includes the final translation.
The rank computation uses that complete ordered operator. It does
not remove the current frame by an unpriced Fourier change of basis.

This obstruction allows arbitrary monomial Clifford wrappers between
children. It does not cover cross-field scalar mixing, a changed
target operator, productive centre sharing, or a general supplier.

Before tensorization, cancel the common scalar minus sign in the two
equal operators. The remaining single-column equality tensorizes at
every width. Restore one scalar minus sign on the full field. This
keeps the scalar sign separate from column phases in the wrappers.

## Why the operation can be deferred

The retained permutation64 word is the literal suffix of the complete
native word. The checker locates each last scalar transfer and its
actual rank7 target completion. It checks every later event for a
read or write of that target. There is none.

The pinned controller ends with the final forward call and then one
X-only code. The checker verifies that every operand of the actual
full scalar gauge is in the X bank. Thus deferring the 64 Y completions
does not change any later local scalar input.

The retained signed bank exchange is a physical array permutation
with signs. It remains valid on arbitrary incomplete-frame arrays.
On these 64 fields its Q-squared map is omitted, since that map has
already been included in the exact contraction above.

The output-to-source port map is a permutation. Each actual A rho
is invertible and orthogonal, so its right action on the regular
O(25,2) cover is a permutation as well. The combined source assignment
is therefore bijective. No second copy or zero input is required.
This proves the field assignment. It does not price its packed
field-and-address permutation.

## Exact invoice and its limit

The complete profile changes from

```text
{1:576,2:208,5:144,7:336,8:192}
```

to

```text
{1:576,2:144,5:144,7:272,8:192,9:64}.
```

The latter has 1,392 children and rank mass 5,600. The 64 new child
recipes have 128 monomial wrappers. Their 64 complex negative signs
cost 128 real scalar primitives; these signs replace the same signs
in the previous terminal. The signed bank exchange remains. No owned
or private field is added.

For 0<sigma<1, strict subadditivity gives

```text
64 (9^sigma-7^sigma-2^sigma) < 0.
```

Thus the contraction reduces the native child moment at fixed field
volume. This is not a positive-exponent supplier. In the inherited
224-field, D25 normalization, all child ranks are below 25 and

```text
(1/224) sum_r count(r) (r/25) = 5600/(224*25) = 1.
```

For every b>0 with sigma=1-b, each term (r/25)^(1-b) is strictly
larger than r/25. The normalized native moment remains above one.
The contraction cannot by itself cross the native admissibility
threshold.

The proof preserves the scalar response. It does not supply the
complete finite precision bound, full-cover correction, packed map
price, or revised recursive row-hosting certificate. Those obligations
remain as stated in the producer packet.

## Reproduction and credit

Run `python3 -I -B check_rank9.py` and
`python3 -O -I -B check_rank9.py`. Both must end with
`PASS_INDEPENDENT_RANK9_COMPLETION` and produce identical receipt bytes.

Per provider, the review checks 64 complete and 128 local operator
equalities, 9,600 signed Pauli columns, all 32,768 local Fourier phase
values, and the exact Gaussian state images. The receipt gives the
state coefficient and chronology counts.

The bridge-access lane supplied the contraction and literal wrappers.
The history lane supplied the permutation64 word. The controller
lane supplied the current five-cut program. Earlier independent
reviews supply the complete triple-terminal and scalar-gauge context.
This review supplies separate phase, chronology, and invoice checks.
AI assistance was used. No PR, publication, rank saving, or kappa
improvement is claimed.
