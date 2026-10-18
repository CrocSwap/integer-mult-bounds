# Dirty padding and uniform exchange adapters

This is a scoped algebraic negative result. It does not contradict PR2636,
whose scan requires fresh output. It does not bound arbitrary tape algorithms,
prove a multiplication theorem, or improve the selected kappa.

## Contract and quantifiers

Let P,Q,G,S be positive integers, with Q at least two. Write

```
A = [P] x [Q] x [G] x [Q] x [S],       [q] = {0,...,q-1},
Omega = [r(P)] x [r(Q)] x [r(G)] x [r(Q)] x [r(S)],
r(q) = 2^ceil(log2(q)),                C = Omega \ A.
```

Assume C is nonempty. E exchanges the second and fourth coordinates.
Both A and C are invariant under E. J extends a bit array on A by zeros
on C; R restricts an array on Omega to A. Thus RJ=I and EJ=JE_A.

For every finite g>=1 and k>=0, consider g genuine banks X_j in F2^A and
k padded banks B_i in F2^Omega. Every bank initially contains an arbitrary,
independent bit vector. A program is a finite, payload-independent word in
these gates:

```
X_a += X_b or B_a += B_b, for distinct banks of the same type.
B_i += J X_j    (additive padding)
X_j += R B_i    (additive restriction)
B_i <- E B_i   (one completed padded exchange)
```

The XOR gates also generate arbitrary invertible F2 bank mixing separately
within each bank type. Their coefficients are uniform over coordinates.
In particular, the same padded-bank mixing acts on A and C.
The word and its length may depend on P,Q,G,S. The model imposes no length bound.

The desired endpoint exchanges one designated genuine bank and fixes every
other bank on all its coordinates, for every initial value:

```
(X_1,X_2,...,X_g,B_1,...,B_k)
    -> (E_A X_1,X_2,...,X_g,B_1,...,B_k).
```

**Theorem.** No permitted program realizes this endpoint. More generally,
no permitted program exchanges an odd number of genuine banks and restores
all remaining banks.

The model excludes coordinate masks on the exchange, other coordinate
permutations, clean or disposable banks, erasure, nonlinear operations,
payload-dependent control, and an exchange directly on a genuine bank.
Descriptor/counter work independent of the payload does not change the proof.
An implementation using an excluded operation must declare and price it.

## Two exchange orbits

A contains a two-element orbit: take all spectator coordinates zero and
the two Q coordinates equal to 0 and 1. C also contains a two-element orbit.

* If Q is not a power of two, use Q coordinates Q and 0, with spectators
  zero. Both exchanged points lie in C and differ.
* Otherwise, some spectator cardinality P,G, or S is not a power of two.
  Set that coordinate to its cardinality and the Q coordinates to 0 and 1.
  Both exchanged points lie in C and differ.

These cases exhaust C nonempty. This step uses no finite shape census.

## Determinant invariant

Let K=F2[t]/(t^2-1). An array on one two-element orbit is the regular
K-module: its two coefficients are its two bits, and E multiplies by t.
The elements 1 and t are distinct. The regular representation is faithful,
including in characteristic two. Factoring t^2-1=(t+1)^2 does not set t=1.

Restrict the program to the chosen orbit in A. Its action is a matrix M_A
over K on g+k banks. Restrict it separately to the chosen orbit in C.
Its action is a matrix M_C over K on k banks. Every gate preserves these
coordinate orbits, so setting all other inputs to zero does not affect either system.

Every XOR and additive J/R gate has determinant 1 on the A system.
The J/R gates act as the identity on C. A padded-bank XOR has determinant
1 on both systems; a genuine-bank XOR is invisible on C. Each padded
exchange has determinant t on both. For k=0, the empty C determinant is 1
and no padded exchange is available.

Determinants multiply over the commutative ring K, without division.
If a word contains m padded exchanges, it therefore satisfies

```
det(M_A) = t^m = det(M_C).
```

Restoring every padded bank forces M_C=I and det(M_C)=1. The desired
genuine endpoint forces M_A=diag(t,1,...,1), whose determinant is t.
This contradicts 1 != t. For an odd number h of exchanged genuine banks,
the determinant is t^h=t, giving the same contradiction. The proof covers
every permitted shape, bank count, and finite word length.

The determinant is over K, not over F2 after expanding into bit matrices.
Every expanded invertible binary matrix has binary determinant 1, which
cannot detect this obstruction. Matching determinants are necessary. We claim no sufficiency for other endpoints.

## Exact failure of the natural adapter

With one genuine bank X and one padded bank B, set

```
P: B += J X
R: X += R B
S: P, R, P              (chronological order)
word: S, E_B, S
```

On A, S swaps X with the genuine part of B. On C, S is the identity.
The seven-gate word therefore has endpoint

```
X' = E_A X,     B'|A = B|A,     B'|C = E_C (B|C).
```

The useful output and genuine borrowed coordinates are correct. The padding
is generally corrupted. A single bit at one point of the chosen C orbit is
an explicit counterexample. The invariant excludes any repair within the
legal alphabet, regardless of its length or extra dirty banks.

If C is empty, S swaps the complete banks. The same word then realizes
the target on arbitrary dirty inputs. If Q=1, E_A is the identity and the empty word suffices. These excluded cases explain both hypotheses. With fresh
owned padding, R E J=E_A remains valid, under a different ownership contract.

## Consequence, cost, and prior work

The one-genuine/one-padded finite closures have an independent count of 96.
Write epsilon=t+1. Reduction modulo epsilon maps GL_2(K) onto GL_2(F2),
which has six elements. Its kernel consists of the 16 matrices I+epsilon M
for binary 2-by-2 M. The gates generate this group: conjugating each binary
elementary XOR by diag(1,t) gives its coefficient-t version. Products give
all coefficients in K.

Elementary elimination over this local ring generates
the determinant-one subgroup, and diag(1,t) supplies both unit determinants.

On fixed orbits the same matrix specializes at t=1; on a padding two-cycle
the action is its determinant. Thus these extra orbits add no independent
states, while a genuine two-cycle makes the representation faithful. This
count predicts the closure size; the literal checker explores all successors
without using that prediction to accept or prune states.

PR2457 supplies aggregate padding; PR2636 supplies its physical scans with
fresh output and owned counters. Neither claims this dirty-only replacement.
The replacement fails even when helpers, scans, source access, frame changes,
recursive exchanges, copies, restoration, and assembly are all free.
Thus a large implementation in exactly this alphabet cannot help. This is
an interface obstruction, not a physical runtime lower bound.

A continuation must retain and price fresh ownership, implement an exchange
that fixes C, or add another explicitly priced coordinate operation.
PR679's separate inverse on unused lanes illustrates a changed alphabet;
it is outside this theorem. This note does not show that an extension improves a supplier.

Prior query-boundary work establishes the group-ring determinant method,
including PR677 section 4, retained in the pinned source. The contribution
here is its paired A/C invariant for any finite number of dirty padded banks,
the aggregate-rectangle hypotheses, and the resulting ownership boundary.
The written proof has no independent human or proof-assistant review.
