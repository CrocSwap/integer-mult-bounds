# Signed rank transport and the scalar-unitary obstruction

This is a written theorem in a formal complex group algebra, accompanied by
exact finite controls. It is not proof-assistant formalization or an integer
multiplication lower bound. The forward/inverse pairing is motivated by
quasi-probability potentials in Nir Ailon's work on conditioned Fourier
computation; see NOTICE.md. The identities below are proved directly.

## 1. Model and potential

Let G be a group and let r:G -> R_{≥0} satisfy

    r(1)=0,   r(g^-1)=r(g),   r(gh) <= r(g)+r(h).

There are W independent input streams. A word acts by an invertible matrix
S over C[G], initially I. Its allowed operations are:

- Left multiplication by an arbitrary scalar matrix B in GL(W,C).
- Left multiplication of one row by a group element h. Its declared cost c
  must satisfy r(h) <= c. A free group operation has r(h)=0.

Every word and its inverse have finite support, even if G is infinite. Write

    S_ij = sum_g a_ij(g)[g],       (S^-1)_ji = sum_g b_ji(g)[g].

Define real signed coefficient weights and a potential

    p_ij(g) = Re( a_ij(g) b_ji(g^-1) ),
    Phi(S)  = sum_{i,j,g} r(g) p_ij(g).                         (1)

These are algebraic coefficient pairings, not measurement probabilities.
In particular, **b is the actual inverse**, not the conjugate transpose.

The identity coefficient in SS^-1 and S^-1S gives both normalizations

    sum_{j,g} p_ij(g) = 1 for every i,
    sum_{i,g} p_ij(g) = 1 for every j.                          (2)

For the second identity, the relevant term in (S^-1S)_jj is
b_ji(g^-1)a_ij(g); scalar coefficients commute. Coefficients need not be real
for (1) and (2) to hold.

## 2. Exact transport identity

**Scalar mixing preserves Phi, even when B is nonunitary.** Under S'=BS,
the inverse is S^-1 B^-1. For each j,g, sum over the output row i. The two
scalar factors contract as

    sum_i (B^-1)_{li} B_{ik} = delta_{lk}.

Thus the sum in (1) is unchanged. There is no condition-number assumption.

**A group operation on row i transports its weights without changing them.**
Under S'=diag(1,...,[h],...,1) S, that row has

    a'_ij(hg)=a_ij(g),
    b'_ji((hg)^-1)=b_ji(g^-1).

All other row pairings are unchanged. Consequently its exact increment is

    Delta Phi = sum_{j,g} (r(hg)-r(g)) p_ij(g).                 (3)

Subadditivity, applied also to g=h^-1(hg), gives

    -c <= r(hg)-r(g) <= c.                                    (4)

In particular a free group operation preserves Phi.

Let N_i(S)=sum_{j,g} max(0,-p_ij(g)), measured immediately **before** the
operation. Equation (2) says sum |p_ij(g)|=1+2N_i(S). Therefore

    |Delta Phi| <= c (1+2N_i(S)).                             (5)

Suppose the endpoint has the following property: for each input column j,
every group element with nonzero a_ij(g), on any output row i, has the same
rank m_j. No common frame or group element is required. Equation (2) then
gives Phi(S_final)=M, where M=sum_j m_j. Since Phi(I)=0, summing (3) gives

    M = sum_paid Delta Phi,
    M <= s + 2 sum_paid c_k N_{i_k}(S_before_k),
    sum_paid c_k N_{i_k}(S_before_k) >= (M-s)/2,                (6)

where s=sum_paid c_k. With three rank-three target columns and eight rank-one
calls, the accumulated paid-row negative mass must be **at least 1/2**.

The condition is necessary only. The supplied five-call example has Phi=9
but fails the full rank-three endpoint. Large Phi, or large negative mass,
is not evidence of a cheaper primitive.

## 3. Unitary scalar mixing cannot save

Give C[G] its formal involution

    (sum_g a(g)[g])* = sum_g conjugate(a(g))[g^-1].

Every group basis element is unitary for this involution, regardless of
whether its concrete matrix representation is unitary. If every scalar
mixing B is unitary, every prefix S is unitary in Mat_W(C[G]). Hence

    b_ji(g^-1) = conjugate(a_ij(g)),
    p_ij(g) = |a_ij(g)|^2 >= 0.

All N_i vanish and (6) reduces to **s >= M**. This permits arbitrary numbers
and placements of scalar mixing stages, arbitrary noncommuting group
operations and arbitrary scalar unitary matrices. It is not a finite-word
enumeration. For m=3, W=3, the eight-call route is closed throughout this
scalar-unitary subclass.

A nonzero scalar multiple of a unitary W-by-W mixer has the same conclusion:
normalize each such mixer. This changes the final word by a nonzero global
scalar and preserves every endpoint support condition. A matrix that is
merely invertible is not covered by this argument.

## 4. Positive diagonal gauges enlarge the excluded subclass

For scalar blocks B_1,...,B_L, suppose positive diagonal matrices
D_0,...,D_L satisfy

    B_k* D_k B_k = D_{k-1}.                                   (7)

Then U_k=D_k^{1/2} B_k D_{k-1}^{-1/2} is unitary. Every intervening group
diagonal commutes with the corresponding scalar diagonal gauge. The gauged
full word is therefore D_L^{1/2} S D_0^{-1/2}, with unitary scalar mixers and
the same group operations. Multiplication by these boundary diagonals
rescales each entry by a nonzero scalar; group support and endpoint ranks
are unchanged. Thus **s >= M** also holds under (7).

The verifier checks (7) exactly over Q(omega), omega^2+omega+1=0, with positive
rational diagonal entries. A zero, indefinite or approximate metric is not
a certificate. Failure to find metrics does not establish a construction.

## 5. A coefficient-norm budget

For a paid row i at a prefix S define

    R_i = sum_{j,g} |a_ij(g)|^2,
    L_i = sum_{j,g} |b_ji(g^-1)|^2,
    K_i = sqrt(R_i L_i).

Equations (3)-(4), the triangle inequality and Cauchy-Schwarz give

    |Delta Phi| <= c sum_{j,g}|a_ij(g)b_ji(g^-1)| <= c K_i.

It follows that M <= sum_paid c_k K_{i_k}. For eight unit-cost calls and
M=9, at least one paid prefix must have **K_i >= 9/8**. This is a local
coefficient-norm quantity; it is not the integer-multiplication exponent
kappa. The verifier checks the squared per-step inequality using rationals.

In the finite-group left regular representation, these are ordinary matrix
row and inverse-column norms. Hence K_i is at most the spectral condition
number of that prefix representation. This observation is a scoped necessary
condition, not an FFT lower bound imported from another computational model.

## 6. Specializations and limits

For the retained projective Clifford group, r is the Fourier rank
rank_F2(B) of its symplectic B block. The inverse has transposed B block;
composition has B_{gh}=A_g B_h+B_g D_h. These give symmetry and subadditivity.
Free S, X, Z, CX and CZ operations have rank zero, and paid C_v has rank one.
The usual single-frame rank-three endpoint implies the endpoint used above.

The group retains Pauli conjugation signs and quotients central scalar phase.
As in PR680/705, the intended tensor realization removes the supplied central
phases when tensor multiplicity is divisible by four. Concrete 8-by-8
matrices independently check the finite group arithmetic. Their linear
independence is **not** assumed; the theorem is in the formal group algebra.

There is also a matrix-sparsity specialization beyond Clifford frames. For
an arbitrary invertible n-by-n matrix A, let nu(A) be its maximum number of
nonzeros in any row, and set

    r(A)=log_2 max(nu(A),nu(A^-1)).

Since nu(AB)<=nu(A)nu(B), this r is symmetric and subadditive. It is zero
on every invertible monomial matrix, at most one on a two-sparse butterfly
whose inverse is also two-sparse, and exactly m on every dense n=2^m target
with dense inverse. Thus the scalar-unitary no-saving theorem applies to
formal words in arbitrary invertible matrix-frame groups with these paid
operations and targets, including non-Clifford frames. This is a direct
corollary of the proved metric hypotheses, not extrapolation from the finite
Clifford tests. It does not cover arbitrary concrete linear dependencies
between frame matrices as if they were formal group identities.

W counts independent input streams, including any dirty helpers. Columns
restored at rank zero can be assigned m_j=0. Clean ancillas that restrict the
input to a proper subspace do not satisfy the invertible independent-stream
model without a further argument. Changing the frame group or paid operation
requires checking the rank/metric hypotheses again. The nonunitary search
space remains open; this package supplies no improved primitive or kappa.
