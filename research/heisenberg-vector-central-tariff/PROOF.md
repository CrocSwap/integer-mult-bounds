# Exact central-target tariff with vector labels

This contribution was produced by Nick Petalas. Apache-2.0.

## Model and statement

All vectors and matrices in this note are binary. For positive integers m,n,
let H(m,n) consist of triples (u,v,Z) in F2^m × F2^n × M_(m,n)(F2), with

    (u,v,Z)(p,q,W) = (u+p,v+q,Z+W+u q^T).

Write x(u)=(u,0,0), y(v)=(0,v,0), and z(Z)=(0,0,Z). A paid call is

    D_N(g) = I_r + ([g]+[1])N,

in M_r(F2[H(m,n)]), where N is any nonzero rank-one binary r×r matrix and
g is any x(u) with u≠0 or any y(v) with v≠0. Every such vector label costs
one paid call. In particular, its coordinate decomposition is not separately
charged. Arbitrary invertible binary scalar mixing is free. All r input
roles may be dirty and no clean initialization, erasure or free address map
is available. Equality means equality in the full formal group algebra.

Choose nonzero matrices Z_1,...,Z_P and r≥P. The target has [z(Z_t)] on
role t for 1≤t≤P and [1] on every other diagonal entry; off-diagonal entries
are zero. Put K=Σ_t rank(Z_t).

**Theorem.** The exact minimum number of paid calls is 2(K+P), for every
finite r≥P. Zero target matrices may be omitted. The identity target costs
zero. Arbitrary restored dirty spectator roles do not lower this minimum.

The changed alphabet is essential. Cinna Davis's PR2258 proves a coordinate
edge tariff in this same group family. Its calls only allow x(e_i),y(e_j),
and its outputs are distinct edge coordinates. Here both the allowed labels
and the central targets change: an entire arbitrary vector is one label,
and a target may have any matrix rank. The new result is the matching
tariff for that explicitly enlarged alphabet. It does not contradict the
coordinate-edge theorem or price vector-label production in a bit supplier.

## Upper bound by a closed vector walk

For nonzero Z of rank k, take a rank factorization

    Z = Σ_(i=1)^k u_i v_i^T,

where both lists are linearly independent. Let u_0=0 and V=Σ_i v_i. Use

    x(u_1)y(v_1)x(u_1+u_2)y(v_2)...x(u_(k-1)+u_k)y(v_k)x(u_k)y(V).

There are k+1 x-labels and k+1 y-labels. Every label is nonzero by
independence, including V. Immediately before the i-th y(v_i), the running
u coordinate is u_i; after the last x(u_k), it is zero. The group law
therefore gives final coordinates u=v=0 and central coordinate
Σ_i u_i v_i^T=Z. This proves the full group identity, not just an identity
in a representation.

Apply this word to coordinate projector E_tt for each target t. The product
acts by [z(Z_t)] on that role and identically on every other role. All calls
are counted and every dirty spectator is restored. Total length is 2(K+P).
For Z=I_2, the word is x(e_1)y(e_1)x(e_1+e_2)y(e_2)x(e_2)y(e_1+e_2),
of length six, versus eight for two separate rank-one commutators.

## Lower bound

First normalize free scalar maps by pushing them through the paid calls.
Conjugation preserves rank one. Augmentation sends every paid call and
the target to I_r, so the final scalar map is I_r. It suffices to bound a
pure paid word. Each factor is invertible, even for nilpotent N: g is an
involution, so ([g]+[1])²=0 and D_N(g)²=I_r.

Use the natural representation and its contragredient:

    rho(u,v,Z) = [ I_m  u  Z  ]       rho_dual(g) = rho(g)^(-T).
                 [  0   1  v^T]
                 [  0   0  I_n]

These are group homomorphisms. In rho, x(u) has only the off-diagonal block
u at position (1,2), and y(v) only v^T at (2,3). The central target is Z
at (1,3). In rho_dual, x(u) has only u^T at (2,1), y(v) only v at (3,2),
and z(Z) only Z^T at (3,1). Signs disappear in characteristic two.
Apply each representation entrywise to the full register matrix.

For each x-labelled occurrence s, write N_s=a_s b_s^T and let u_s be its
label vector. Define

    A = [u_s ⊗ a_s]_s,       B = [b_s^T]_s.

The target has zero (1,2) block. In the natural representation this block
is exactly Σ_s u_s⊗N_s=AB. No product of two strictly upper blocks can
contribute to (1,2). Thus AB=0 and

    rank(A)+rank(B) ≤ n_x,

where n_x is the number of x-labelled calls. Its central block C is the
ordered sum of x-then-y products. Consequently im(C)⊆im(A). After a
permutation of tensor coordinates, the target C is the block diagonal
matrix with blocks Z_t and zero spectator blocks. Hence rank(C)=K and
rank(A)≥K.

In the dual representation, the central block C_dual is a sum of y-then-x
products. Its row space is contained in the span of all rows
u_s^T⊗b_s^T. For each nonzero target Z_t, the row space of C_dual contains
a nonzero row q^T⊗e_t^T. Choose a nonzero coordinate of q and contract the
address tensor coordinate there. This yields e_t^T. Applying the same
contraction to any u_s^T⊗b_s^T yields either zero or b_s^T. Thus every
active e_t^T belongs to row(B). The P active coordinate vectors are
independent, so rank(B)≥P. Therefore n_x≥K+P.

For completeness, the y-labelled argument uses

    A_y=[a_s]_s,       B_y=[v_s^T⊗b_s^T]_s.

The natural (2,3) block gives A_y B_y=0. Its central block has row space
inside row(B_y), giving rank(B_y)≥K. The dual central block has column
space inside the span of v_s⊗a_s. Contracting a nonzero address coordinate
in each active target column gives e_t in im(A_y), so rank(A_y)≥P. It
follows that n_y≥K+P. Every paid call is of exactly one label type, whence

    length = n_x+n_y ≥ 2(K+P).

Together with the explicit full-formal word, this proves the theorem for
all finite dimensions and every finite number of dirty spectators. No
finite search supplies this universal quantifier.

## Evidence and scope

The standalone verifier enumerates bounded central matrices, independently
computes their ranks by minors, constructs full group endpoints, and obtains
their exact one-role word distances by complete Cayley BFS. It also excludes
every normalized word of length at most five for the new rank-two target
with a restored second dirty role, using exact full-formal balls of radii
three and two. Arbitrary rank-one binary couplings, including nilpotents,
are present in that finite exclusion. Literal four-role formal matrices
check heterogeneous targets and dirty spectator restoration.

The theorem counts only this abstract alphabet. Producing arbitrary vector
labels, native implementations, scalar mixing costs, physical read/write
access, caller scheduling, hosting, precision, tapes, compiler closure,
recursive moments and outer recovery remain unproved. It establishes no
new κ and leaves all five selected framework assumptions intact.

Credit Cinna Davis / 1337isnot1337, PR2258, for the H(m,n) coordinate-edge
model and natural/contragredient rank-nullity strategy. That package credits
the eumemic / woklerx normalized register model and preceding UT3/UT4
shared-middle tariffs. Rank factorization, unitriangular representations,
rank-nullity and closed-walk accumulation are classical. No broad
literature-priority claim or independent human/kernel review is made.
