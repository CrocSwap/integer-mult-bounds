# Tensor scope of a paired-line scalar factor

This note records a limit of a proposed terminal factor. It does not
exclude a native construction that uses more general views or a changed
interface.

Let Q be an invertible operator and let q=Q^-1. Define two elementary
field operations by

```text
U(c) = [[I,c],[0,I]],     L(c) = [[I,0],[c,I]],
J    = [[0,-I],[I,0]].
```

Direct multiplication gives

```text
U(Q) L(-q) U(Q) J = diag(Q,q).
```

The displayed order is matrix order. Its chronological order starts
with J. This identity accepts arbitrary values in both fields. It does
not need a clean field.

For one tensor position, the positive line gate has the formula

```text
Q = ((1+i)I + (1-i)T)/2,
q = ((1-i)I + (1+i)T)/2,
T = Q^2.
```

Here T is a translation. Each off-diagonal operation U(Q), L(-q), or
U(Q) can therefore be split into two scalar ADDs with translation
views at that one tensor position.

This formula does not give a fixed scalar invoice for the recursive
line gate. At tensor width f, the gate is Q_f=Q^tensor f. Its expansion
contains 2^f distinct translations, all with nonzero coefficients.
In particular,

```text
Q_f != ((1+i)I + (1-i)T^tensor f)/2
```

when f is greater than one. Applying the two-field identity at each
tensor position instead needs a number of field scans proportional
to f. That cost is not a constant scalar toll for a recursive supplier.

## A scalar support bound

Consider a word on any finite number of fields. Admit arbitrary
monomial maps within fields, nonzero scalar scales, field permutations,
and scalar ADDs from one field to another. A monomial map has exactly
one nonzero matrix entry in each row and column. Admit arbitrary input
values in every borrowed field.

After m scalar ADDs, each matrix row of the word has at most 2^m
nonzero input coefficients. To prove this, start with the identity
matrix, whose rows have support one. A monomial map, scalar scale, or
field permutation does not increase the maximum row support. One ADD
replaces a target row by the sum of two rows, so it can at most double
the maximum.

Every row of Q_f on its input field has 2^f nonzero coefficients. The
translations in its tensor expansion are distinct. Thus any word in
this class that implements Q_f, or diag(Q_f,Q_f^-1), needs at least f
scalar ADDs.

The bound permits extra arbitrary fields and arbitrary monomial views.
It rules out a fixed number of scalar ADDs with no native operation.
It does not give a lower bound on the number or ranks of native calls.

## A narrower one-call obstruction

There is also a simple exact statement when every free view is a
translation. Let R be the commutative complex group algebra of the
spatial translation group. Treat a word on two fields as a two-by-two
matrix over R.

Admit scalar elementary ADDs with translated sources, constant nonzero
scales, field translations, and field exchanges. Each such word has
determinant c T for a nonzero scalar c and a single translation T.
An elementary ADD has determinant one. The other generators have the
stated determinant form, which is closed under multiplication.

One native call Q_f or Q_f^-1 on one field multiplies the determinant
by Q_f or Q_f^-1. A complete word with exactly one such call therefore
has determinant

```text
c T Q_f       or       c T Q_f^-1.
```

Neither expression is one: Q_f and Q_f^-1 have 2^f nonzero translation
coefficients, whereas a scalar translation has one. The target
diag(Q_f,Q_f^-1) has determinant one. It cannot be realized with exactly
one line call in this translation-only class. Two direct line calls
realize the target.

This determinant argument does not admit general orthogonal address
maps or coordinate-dependent phases as free generators. Such maps can
make the operator entries noncommutative. The argument must not be
used as a lower bound for that larger construction family.

## Research consequence

The one-position paired-line factor is exact. Its proposed fixed-cost
tensor lift was invalid. The scalar support bound explains the lost
factor f. The determinant argument gives a separate, narrower limit
for one-call constructions with translation views.

These statements do not settle the actual terminal problem. A useful
escape can change a native endpoint, use a different type of view,
combine several native fields, or carry an encoded interface through a
recursive call. Each escape still needs its own complete cost and
physical proof. AI assistance was used to derive and check this note.
