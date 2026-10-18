# The full selected reader excludes a unitary paired-cycle intertwiner

This is a scoped obstruction at one named local cut, conditional on the exact
native frame identities retained in the selected replay. It is not an
obstruction to every order-four action or to a different supplier contract.

## 1. Object, ordering and boundary

Use the `gauge44` provider in the pinned selected replay archive. Its 704 live
fields are the 112 source fields, 112 target fields and 480 arbitrary dirty
helpers, in that order. The eight output fields, in order, are

```
(92, 57, 81, 224, 11, 240, 9, 256).
```

The input cut is immediately before `phase: entry_adapters`, **after** all
7,400 zero-frame precondition/compensation scalar gates. The output cut is
immediately before `phase: centers`. These are half-open event indices
`[7401,12550)` in the exact forward emitted program. No centre COPY, descent,
ERASE, B block or final cleanup belongs to this reader. The omitted prefix is
invertible: every gate is an addition between distinct fields or a nonzero
scale. Therefore every tuple of 704 input payloads at the named cut is
attainable from an arbitrary dirty invocation input. No helper is assumed zero.

Erase the unitary frame annotations, retaining the 3,451 scalar gates of this
segment. Replaying them on all 704 formal basis inputs and selecting the eight
output rows defines `A` in `Q^(8 x 704)`. An independent reverse covector
pullback gives exactly the same matrix. The committed `RESULT.json` contains
all entries, not just its diagonal norms.

## 2. Scalar prefix invariant for every input field

Let `H` be the common payload Hilbert space. In the retained native realization,
each frame `f` has an exact unitary operator `T_f` on `H`; a climb `f -> g`
implements exactly `T_g T_f^-1`. This is the exact-phase Clifford contract
retained in `CLIFFORD-REVIEW.json`, not a phase-free tableau assertion. The
frames are built from normalized Fourier, invertible address permutations and
unit-modulus phases, all unitary. Entry adapters, including the inverse right
residual wrappers for entering or hyperplane-ended helpers, are unitary too.

Write `E_j` for the physical entry adapter on field `j`, and `s_j` for its
starting frame. For the arbitrary physical input payload `z_j`, define

```
u_j = T_(s_j)^-1 E_j z_j.
```

Thus `U_in = diag_j(T_(s_j)^-1 E_j)` is unitary on the full direct sum `H^704`.
The definition applies separately to **all** 704 fields, including all 480
helpers and all 240 residual-adapter entries. It makes no assertion that
constants, Fourier characters or any one-dimensional subspace are invariant.

The induction invariant after any prefix of A is

```
physical field r = T_(current[r]) sum_j a_(r,j) u_j,
```

where `a_(r,*)` is the corresponding row of the scalar prefix matrix.
Immediately after entry it holds with the identity matrix. For a climb,
left multiplication by `T_new T_old^-1` changes only the displayed frame. For
a scalar addition, source and target have the *same current frame*, so
linearity updates their coefficient rows exactly as the scalar replay does.
For a scale, the coefficient multiplies the entire row. These are all events.
The verifier checks the current frame of both operands of every addition,
each climb's old frame, nestedness and rank, all 704 entry wrappers, and the
eight exact output frames `(415,...,422)`.

Consequently the actual native reader has the factorization

```
A_native = T_out (A tensor I_H) U_in,
T_out = diag(T_415,...,T_422).
```

This uses the retained exact transition identities. The new check authenticates
their bytes and global-phase review, checks the scalar/frame prefix, and
independently verifies bijectivity and phase ranges of all 6,088 serialized
monomials. It does not independently rerun every Clifford equality or claim
that checking monomial unitarity alone proves those equalities. The factorization
is valid at every payload size for which the retained exact unitary frame
realization applies; no all-size supplier or analytic-transfer obligation is
newly discharged here.

## 3. Native Gram obstruction, including physical permutations

Set `G = A A^T`. The exact diagonal is

```
(150, 130, 146, 134, 122, 126, 142, 146).
```

By the factorization, the `i,i` block of
`A_native A_native*` is `G_ii I_H`. This conclusion uses all 704 inputs: the
unitary input factor cancels, and unitary conjugation of a scalar identity
block leaves that block unchanged.

Suppose an arbitrary unitary input action `P` on `H^704` and an output action
`Q_native` satisfy `A_native P = Q_native A_native`. Allow `Q_native` to be any
unitary block-permutation: its `i,sigma(i)` block is an arbitrary unitary
payload map `V_i`, and all other blocks in row `i` are zero. Gram invariance
then forces

```
G_ii I_H = V_i (G_(sigma(i),sigma(i)) I_H) V_i*;
hence G_ii = G_(sigma(i),sigma(i)).
```

When `sigma` has two cycles of length four, this is impossible: no value of the
diagonal occurs four times (the maximum multiplicity is two). The verifier
also enumerates all `8!/(4^2 2!) = 1260` such permutations and retains a failing
row for each. This covers arbitrary unitary input mixing, not merely signed
permutations or permutations of helpers.

There are two different output actions worth distinguishing. A physical row
permutation is `Q tensor I_H`. A permutation of typed scalar outputs is
`T_out (Q tensor I_H) T_out^-1`; its nonzero blocks include transitions between
output frames. Both lie in the excluded block-permutation class. We do not
silently identify them. Adding signs or unitary payload rotations to either
does not repair the unequal scalar diagonal blocks.

This rules out a direct embedding of the paired-cycle contract into the full
selected dirty reader at this cut with unitary input action. It neither proves
that the abstract PR1391/1410 echo is wrong nor asserts that PR2464 supplied
this missing embedding: PR2464 explicitly says no named host child exposes it.
The location of the unitary condition matters: the preceding 7,400 scalar gates
are invertible but need not be unitary. Conjugating an action that is unitary
before that prefix can give a nonunitary action at our cut. Such an earlier-cut
unitary action is outside this result unless its conjugate is also unitary here.

## 4. Controls that delimit the conclusion

The source-data restriction `R = A[:,0:112]` satisfies `R R^T = 56 I_8`.
For the fixed paired cycle `Q x = (x_3,x_0,x_1,x_2,x_7,x_4,x_5,x_6)`, every
transformed column of `R` is another signed column. The signed action
`P_data` constructed in the receipt is a permutation of all 112 columns,
has fourth power identity and satisfies `R P_data = Q R`. Deleting its negative
signs breaks the identity. Thus data-only inspection passes even though the
full interface fails. The helper-only row norms are
`(94,74,90,78,66,70,86,90)`. No clean-helper assumption is licensed.

A smaller witness for the fixed `Q` is input field 224. Its column is
`h=(0,2,2,0,0,0,0,0)`, while `Qh=(0,0,2,2,0,0,0,0)` is absent, even up to
sign, among all 704 columns. This excludes a signed permutation directly;
the Gram argument is the stronger statement for every unitary input action.

There is an explicit **nonunitary escape**, so no general intertwiner
impossibility is claimed. Define

```
J = [R^T/56; 0]     (704 x 8),
P_t = I_704 + J (Q^t-I_8) A,       t in Z/4Z.
```

Then `AJ=I`, so `A P_t = Q^t A`. Expanding the product and using `AJ=I`
gives `P_s P_t = P_(s+t)`, hence `P_4=I`. Since A is surjective and Q has
exact order four, `P_1` also has exact order four. The verifier checks the
right inverse and all 16 low-rank group-law products exactly. But for `e_224`,

```
||P_1 e_224||^2 = 1 + ||J(Q-I)h||^2
                = 1 + ||(Q-I)h||^2/56 = 8/7.
```

The first term and the correction have disjoint input supports. Thus P is not
unitary. This formula does not provide an executable native word, favorable
invoice, source restoration, precision bound or legal hosting schedule. Those
are the next questions if a paid nonorthogonal replacement is pursued.

Output rescaling or nonunitary mixing, changed cuts, different copied totals,
or new host contracts are also outside the obstruction. No charge, selected
histogram, ceiling or kappa is changed by this result.
