# Coupling two individually rigid resonant Jordan blocks

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical proof. The finite verifier corroborates the
argument; independent human and formal proof-kernel review are unclaimed.

## Statement

Let F_q be any finite field. Choose nonzero lambda_1, lambda_2 with
lambda_i^2=1, and put

    P = diag(J_2(lambda_1), J_2(lambda_2)),
    J_2(lambda) = [[lambda,1],[0,lambda]].

Use precisely the ordinary wrapper of Nicholas Stone's #5556, on arbitrary
H,D in F_q^4, with chronological operations

    D -= H; F_P; D += H; F_Q; D = -D; D += H,
    F_T(H,D) = (T D, T^-1 H).

Require Q invertible. Optimality means least rank of the difference between
this wrapper and the interchange (H,D) -> (D,H), with this P fixed.

**Theorem.** In characteristic two the unique optimum is Q=P. In odd
characteristic there are exactly q^2 optimal Q, all with determinant one.
Exactly q^2-1 have rank(Q-P)=1. In coordinates 0,1,2,3, the complete list is

    Q = P + U D S V,                    S^2=0,
    U = [e_0 e_2],   V = [e_1^T; e_3^T],
    D = diag(2 lambda_1, 2 lambda_2).

Here S is an arbitrary two-by-two matrix over F_q. The parameterization is
injective in odd characteristic. The minimum wrapper error rank is two in
odd characteristic and zero in characteristic two. Thus odd-characteristic
optimal wrappers agree with interchange on exactly q^6 of the q^8 input pairs.

Each individual J_2(lambda_i) has a unique optimum by #5556. Their direct
sum has q^2 optima in odd characteristic. Multiplying individual counts
would give one and misses all q^2-1 new coupled maps.

## Credited starting point

Nicholas Stone's [#5556](https://github.com/CrocSwap/integer-mult-bounds/pull/5556),
`research/jordan-second-callee-count/PROOF.md`, gives the fixed-wrapper
error reduction. Write A=P^2-I and R=Q-P. For invertible P and Q, the
wrapper error rank is

    rank M,   M = [[A,R],[R,0]].                         (1)

The minimum is rank A, attained by R=0. The error identity and optimum are
used as inherited statements, not re-audited here. They originate in Jerry
Chen / CubeJerry's #2950 and Nick Petalas's #5228. The latter gives a general
equality characterization for arbitrary P. The argument below specializes
(1) directly to the new coupled pair and counts its complete solution set.
It does not claim the general characterization as new.

Nick Petalas's #6406 counts regular J_3(lambda), where P^2-I is invertible.
Our P has singular P^2-I. The block-coupling question appears in #5556's
Open next questions. No predecessor executable is used.

## The support forced by equality

In odd characteristic, each block of P has square
I+2 lambda_i N, where N=[[0,1],[0,0]]. Therefore

    A=U D V,    rank A=2,    V U=0,
    im A=span(e_0,e_2),    ker A=span(e_0,e_2).

If rank M=rank A, its top block row [A R] cannot have rank greater than A.
Thus im R is contained in im A. The first block column [A; R] likewise
forces ker A contained in ker R. These two containments say exactly that

    R=U T V                                                  (2)

for a unique two-by-two T. In particular the only possible nonzero entries
of R are at (0,1),(0,3),(2,1),(2,3). No candidate is discarded on a clean-input
assumption. These are consequences of equality for the entire error map.

Substitute (2) into M and delete its identically zero rows and columns.
Permuting the remaining rows and columns yields

    [[D,T],[T,0]].

Since D is invertible, block elimination gives

    rank M = 2 + rank(T D^-1 T).

Put T=D S. Then T D^-1 T=D S^2, so equality is equivalent to S^2=0.
Since U has independent columns, V has independent rows and D is invertible,
different S yield different R and hence different Q.

## The invertibility filter accepts every parameter

Order the coordinates as (0,2,1,3). In this order P+U D S V is

    [[Lambda, I_2+D S], [0,Lambda]],
    Lambda=diag(lambda_1,lambda_2).

It is invertible for every S, with determinant
(lambda_1 lambda_2)^2=1. Invertibility is proved before counting; no singular
second maps are counted as optima. This remains true when the two signs differ.

## Count and perturbation ranks

The square-zero two-by-two matrices over any field are exactly

    S=[[a,b],[c,-a]],    a^2+bc=0.                           (3)

This elementary parameterization, including characteristic two, is recorded
in #5556. For c=0, the equation forces a=0 and permits any b, giving q choices.
For each of the q-1 nonzero c, any a determines the unique b=-a^2/c,
again giving q choices. Thus (3) gives q+(q-1)q=q^2 parameters.
One is zero; every other one has rank one because im S is contained in ker S.
The injective left/right maps in U D S V preserve that rank. This proves
the count and the stated rank distribution.

For a concrete coupled optimum take S=E_01. Then R has the single nonzero
entry R_03=2 lambda_1. Both diagonal two-by-two blocks of Q remain unchanged,
yet Q differs from the independent-block optimum P.

Finally, a rank-two linear error map on the eight-dimensional input space
has a six-dimensional kernel, hence q^6 agreeing inputs.

## Characteristic two

The equation lambda_i^2=1 over a field of characteristic two implies
lambda_i=1. Each J_2(1) squares to I, so A=0. Equation (1) then has rank
2 rank R. Its minimum zero is attained exactly when R=0. Consequently Q=P
is the unique optimum. The odd-characteristic count cannot be transferred
to this case because D is zero.

## Scope and open next questions

This settles one coupled finite-field equality/counting problem. The first
verified pair ended the investigation. No larger block family, selected
assumption, physical implementation or cost advantage is proved. Native
coefficients, movement, restoration, precision, stock, compiler and outer
costs remain unpriced. No new kappa, selected frontier, exact interchange in
odd characteristic, or complete multiplication theorem is claimed.

Further questions and their first steps are in TASK.json. Classical block
elimination, rank-nullity and finite-field counting are not claimed as new.
