# Adopted constructions and exact scope

This note joins the reviewed local results. It does not alter their frozen
proofs. CLAIM-INDEX.json points to each original proof and independent
review. Every field below can have an arbitrary input value.

## 1. The actual row reader

The fixed 112-port response has E=I+UV, with 16 centre coordinates. Its
selected ports, in order, are

```text
0,27,36,111,20,7,57,46,1,3,6,8,17,18,24,23.
```

The actual signed pivot Gram matrix is V_P V_P^T=diag(2I8,I8).
Thus V_P is a unit over Z[1/2]. Put L=V_P^-1 V=[I,B] in P,R order.
The code C has selected rows L and ordinary rows I:

```text
C = [[I,B],[0,I]],       C^-1 = [[I,-B],[0,I]].
```

The off-diagonal correction squares to zero. The literal scalar code and
its inverse each cost 1760 real primitives and use existing fields only.
For the actual response, LE=Hc L with Hc=diag(-5I8,-7I8). This equality
does not require division by five or seven in any word below.

For row formation, start with X=Qx,Y=y. Precode Y by C at I. Remove the
250 selected-target events from the old native word; these contain 128 H1
calls. The retained core never reads a removed selected Y field. Complete
the entire core, advance the sixteen selected Y fields from I to FULL,
and then execute the literal late query. The endpoint is

```text
X'   = F9 x,
Y'_R = F9 q_R (y+Ex)_R,
Y'_P = F9 [C(y+Ex)]_P = F9 (Ly+Hc Lx).
```

The arbitrary Ly baseline remains. The direct-FULL refinement uses the
exact F9 kernel with identity side maps for the sixteen H9 children.
It changes the side-map count, not the scalar bill or native profile.

The line-entry variant starts with Y_P=Q_P z for independent z. It omits
the precode and uses sixteen H8 children to reach FULL. Its selected
output is F9(z+Hc Lx), with the same ordinary output. If z=Ly, the same
reader is retained. This is not an implementation of a different past
reader L_s E_t. That routed query has a separate word and cost.

## 2. Clean exchange and its exact dual

After the retained core and selected FULL advance, apply C to X. For each
selected pair, execute Y+=X, X-=Y, Y+=X. This maps (a,b) to (-b,a).
For I-entry let b=y_P; for Q-entry let b=z. The complete endpoint is

```text
X'_P = -F9 b,               X'_R = F9 x_R,
Y'_P =  F9 Lx,              Y'_R = F9 q_R (y+Ex)_R.
```

The old baseline moves into X_P. No field is erased. The code and three
ADDs give an algebraic inverse on all 224 data fields. A formula for that
inverse alone would not price a native inverse service.

For the Q-entry content, put J=-B^T. The actual symmetric response has
E_PP=0 and E_R=[J,I+JB]. In P,R bank order, write an input as (a,u,z,v).
Then the clean content map and its inverse transpose are

```text
M(a,u,z,v)     = (-z,u,a+Bu,v+u+J(a+Bu)),
M^-T(a,u,z,v)  = (-z,u+Ja-v,a+Bv,v).
```

The selected-conjugate word has content

```text
S M^-T S(a,u,z,v) = (z+Bv,u+Jz-v,-a,v).
```

Here S exchanges X_P and Y_P. This uses J=-B^T for the actual source.
A routed substitution needs its own adjoint relation.

If a physical word is W=Aout M Ain^-1 and Ain,Aout are unitary, then
W^-*=Aout M^-T Ain^-1. In chronological order, replace each real ADD by
its negative transpose and each SCALE by its reciprocal. Keep each
unitary native or monomial operator, including its phase, in the same
chronological position. This gives the physical inverse-adjoint. It does
not reverse chronology. For the selected conjugate, both selected input
types are Q and both output types are FULL. Rename every selected field
in each instruction; adjacent S factors cancel. No runtime swap is used.
This fact does not permit a free bank permutation in an arbitrary caller.

## 3. Row involutions and native words

Over a ring in which two is a unit, let V_P be invertible. Keep U_R and set

```text
U'_P = V_P^-1(-2I-V_R U_R),       A = I+U'V.
```

Then VU'=-2I and A^2=I. The ordinary rows of E are unchanged. Over a
field of characteristic different from two, rank(A-I)=16 and det(A)=1.
The actual source also has rank(A-E)=16 and trace(A)=80. The first rank
identity is the general statement; the second is source-specific.
The frozen COMPLETION-LIMITS.md and independent review retain this
clarification.

The independent signed-block construction uses eight blocks of size six
and eight of size eight. In each block d_p=1 and
A_k=I+((k-2)e_p-d)d^T. Its contraction is -2. The actual physical pair
metric is checked when the transpose is formed; H is not assumed to be
an orthogonal matrix of unit scale.

The 3276-scalar common-frame A and A^T words use no new field or odd
division. The native words use explicit changed transfer coefficients,
complete their retained cores, and execute the selected FULL queries.
For M=A or A^T, their exact content maps are

```text
forward:   (x,y) -> (x,y+Mx),
backward:  (x,y) -> (x-M^T y,y).
```

The physical input is X=Qx,Y=y. The output types are FULL on X and Y_P,
and F9 q_R on Y_R. The complete emitted lists, both providers, both M,
and both directions are checked on all 640 inputs. The physical boundary
conversions remain part of any composition; A^2=I alone does not close a
reciprocal caller.

The independent model review also proves that sixteen changed rows are
necessary for a dyadic-unit row replacement of this fixed E. Its large
component has left-nullity eight modulo five and its small component has
left-nullity eight modulo seven. If fewer than eight rows change in one
component, a nonzero old left-null vector can vanish on all changed rows
and still annihilate the new matrix. A dyadic unit must stay invertible
modulo those odd primes. The actual A attains eight changed rows in each
component. This is a common-scalar row-replacement bound, not a native or
computation lower bound.

## 4. Complete D25 fixed-reader pair

Let A_t be the actual current response with its owner routes, and L_s the
retained past reader. At the completed FULL cut, apply A_t to X, add L_s X
to selected Y, and apply A_t again to X. Since the routed A_t is itself
an involution, the endpoint is (x,y)->(x,y+L_s A_t x). The old target
baseline is retained and X is restored. No reader commutes through A_t.

The literal query costs 8440 scalars and 672 monomial maps: two
3276-scalar/224-map A applications, one 1760-scalar/224-map complement
reader, and sixteen same-port copies at cost 128. It uses no child or
extra field. Omitting the second A or substituting the current reader
fails for each checked pair.

Put G_R=diag(I_P,q_R). Let F_l act on the first 9+8l axes. Set
(D_st)_P=L_s A_t and (D_st)_R=(A_t)_R. For (s,t)=(0,1),(0,2),(1,2),
both providers have complete typed services

```text
forward:
(F_(t-1)x,F_(t-1)G_R w) -> (F_t x,F_t G_R(w+D_st x)),

dual:
(F_(t-1)x,F_(t-1)G_R w) -> (F_t(x-D_st* w),F_t G_R w).
```

The input level is t-1, including pair (0,2). The star includes transpose
and inverse owner route. The replay keeps the complete native prefix,
all DATA entry/exit views, the full cover barrier, and the late query.
It checks 896 DATA phase equations and the ordered D25 owner paths.
There are 3824 selected field/path terms per pair. Both inverse products
of the complete dual with the forward adjoint are identity on all 640
fields. This is a complete local backward service with stated boundary
types; it does not supply a recursive host or a closed outer caller.

## 5. Route32 raw response and scalar codes

Split the old signed blocks by the least valid shared-root label. The
actual classes have 64,32,16 ports, with labels 30,45,75. The split gives
eight large four-mode blocks, eight large two-mode blocks, and sixteen
small four-mode blocks. With the actual pair code H, use

```text
E32 = H^-1 direct_sum(I-dd^T) H.
```

The response has rank(E32-I)=32, zero physical diagonal, and determinant
3^24. Its inverse is rational with no odd denominator except three. It
is not a dyadic inverse. The old selected-eight principal block is zero;
the reviewed raw packet instead has empty selection.

One pivot code sends d to k e_p and has pivot row d^T. It conjugates each
I-dd^T to I-k e_p e_p^T. The complete code costs 1870 scalars in each
direction, including H. A second code uses S=I-ss^T/2 on each four-mode
block, where s=d-2d_p e_p. Since s^T s=4 and s^T d=2, S is an involution
and S d=2d_p e_p. Its complete price is 2486 in each direction. Both use
existing fields and dyadic units only. Their common diagonal response is
-3 on 24 pivots, -1 on eight pivots, and +1 on 80 complements.

All scalar transfers preserve the route class. Thus the codes commute
with diag(A_r) when each class has one exact spatial operator. The actual
unshifted D11 advances have identical ordered circuits within each class.
This does not move Q through C or admit a field-dependent view. The
literal entry C Q^2 includes 112 maps before the scalar code. The formal
q C q code diagonalizes Q E32 q, not E32 alone, and is not a raw decoder.

The rank32 minimum is restricted to the same H, route-homogeneous
partitions within each large vertex, small monochromatic cliques, and no
cross-sector mixing. Each large vertex needs two blocks. The small sector
needs sixteen cliques because its largest monochromatic clique has four
ports. The total is at least 32, and this construction attains it.

The raw native forward/backward words have content (x,y+E32 x) and
(x-E32^T y,y), with input (Qx,y) and output types (F9,F9 q). Their 297
new spatial kernels are checked on every 512-column input basis. Exact
ordered-record equality retains 752 accepted kernels. The whole-W lift
and reflection decoder are not part of the adopted result.

## 6. Direct clean comparator

A separate direct word applies F9 q_p to all X and selected Y, F9 to
ordinary Y, adds each ordinary X to its Y partner, and applies q_p to
ordinary Y. It then applies C to FULL X and the same selected rotations.
This gives

```text
Fsimple(a,u,z,v) = (-z,u,a+Bu,v+u).
```

The selected-conjugate inverse-adjoint gives

```text
Bcustom(a,u,z,v) = (z,u-B^T z-v,-a,v).
```

Both have input (Q(a,u),Q_P z,v) and output types (F9,F9,F9 q_R).
All 209 distinct kernels are checked on all 512 spatial columns, with
exact Gaussian-integer coefficients and global phase. These are complete
one-alphabet operator identities. Their full tensor powers give the same
field transitions at every width; no one-bit polynomial is substituted
for a tensor-power line operator.

Each complete word costs 2912 scalars, with 320 children and mass 1984.
This is a different profile and interface from the old 8600-scalar clean
word and from the separate 4632-scalar phase-coded caller word. It is a
local comparator, not a better complete recursive supplier.
