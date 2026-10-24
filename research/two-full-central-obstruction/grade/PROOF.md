# Full monomial routing does not complete the two-owner, two-FULL unit

This note audits the lower-grade argument proposed by the root agent and
gives a direct-column formulation retaining the actual transverse factors.
It is an additive mathematical note for Discussion4902, not a new PR or a
physical consumer. All helper jobs remain autonomous and unchanged. There
are exactly two main owners per port, without access to other transformed
states or scratch owners in this extension.

## A single controlled-phase check and its rejected endpoint gate

Normalize the ambient axes to one central q, eight old A axes, and eight
fresh B axes. Let a be one A axis. The literal controlled phase

    C_f: value[address] *= (-1)^(sum_columns q_column*a_column)

is a monomial Clifford. Apply it only to the Y owner between the two FULL
calls. It is one pass per port, 112 passes for the actual 112-port bank,
with zero extra Gaussian calls. Its literal inverse and inverse transpose
are itself. It requires only predetermined signs, independent of input data.
For source normalized coordinates q=bit8, a=bit0, this is the quadratic
phase with exactly the cross term q*a and no linear/global phase. The
checker relabels these as bits0/1 and retains all other fifteen axes.

Writing positive central Q and positive transverse D_A,D_B, the main word is

    M = D_B [[1,-Q],[0,1]] diag(I,C) D_A [[1,0],[Q^-1,1]].

All factors are literal words. Matrix multiplication gives

    M11 = D_B D_A - D_B Q C D_A Q^-1,
    M12 = -D_B Q C D_A,
    M21 = D_B C D_A Q^-1,
    M22 = D_B C D_A.

The exact pinned Clifford engine finds grades16,16 for the two M11 words,
17 for M12 and M21, and16 for M22. These are true17-axis signed-tableau
calculations, not width-one owner/address interchange. The off-diagonal
rank17 words pass the maximal-grade image-count gate. They nevertheless
fail the necessary lower-grade purity gate: M22 is a nonzero group unit of
grade16, and arbitrary invertible monomial-algebra outer matrices cannot
erase the whole grade16 matrix component.

The pure coordinate swap q<->a is retained as a discriminating control:
only M21 then has grade17. The controlled phase avoids that one-copy
obstruction but does not produce an endpoint. Its positive maximal-grade
gate must not be reported as a positive feasibility result.

## The stronger two-owner theorem, with arbitrary interstage words

Let G be a fixed finite group of one-column17-axis Clifford matrices,
including absolute phases. Let H be its full monomial subgroup, B=K[H],
A=K[G], with K enlarged if needed for a necessary obstruction. Gaussian
Fourier rank is invariant under monomial multiplication on either side.
Projection pi_<=16 onto group basis elements of rank at most16 is therefore
a B-bimodule map. The same holds in the central-character twisted quotient
needed at a fixed tensor width; scalar phases do not change Fourier rank.

Let each actual FULL main block have form

    T_s = diag(D_sx,D_sy) E_s,

where both D_sx,D_sy have Gaussian rank eight, and E_s is either elementary
upper or lower shear with one arbitrary central Clifford letter. The
letters may differ, need not commute, and may include signs or inverses.
Allow arbitrary L,W,R in GL_2(B). Suppose

    L T_2 W T_1 R = diag(g1,g2),

where both g1,g2 are single Clifford words of Fourier rank17, up to arbitrary
monomial boundaries. The target is pure grade17. By the bimodule property
and invertibility of L,R, pi_<=16(T_2 W T_1)=0.

Choose the input column c untouched by E_1 (column2 for a lower shear,
column1 for an upper shear). Choose the output row r untouched by E_2.
Let i be the other row. Direct multiplication in the actual factor order
gives

    M_rc = D_2r W_rc D_1c.

Every group word in W_rc is monomial. Fourier-rank subadditivity implies
every word of this entry has rank at most8+0+8=16. Thus it is its own
pi_<=16 projection and must vanish. The D factors are group units, hence
W_rc=0. The other entry in that input column then simplifies to

    M_ic = D_2i W_ic D_1c,

because its possible second-shear contribution factors through W_rc=0.
It too is supported only on grades at most16, so it vanishes and W_ic=0.
The entire c-th column of W is zero, contradicting its invertibility.

No commutation of a changed central letter with a raw transverse factor is
needed in this direct-column proof. In particular the raw D0 translation
correction cannot break it. Role-dependent D factors of rank eight are
allowed. The proof keeps every transverse operation explicitly and grants
the full monomial Clifford subgroup, including central/fresh axis mixing,
controlled phases, and arbitrary non-diagonal interstage W.

The all-width group-algebra implication is the separating-polynomial proof
in [the retained independent review](../independent/algebra-REVIEW.md): for all sufficiently large f,
distinct projective Clifford words tensor-powered f times are linearly
independent after specializing global phases. Thus accidental one-column
matrix sums do not invalidate the pure-grade argument. Width-dependent
scalar choices and free words are permitted within the same fixed finite
one-column alphabet. Arbitrary width-specific address operations outside
that alphabet remain outside the claim.

## Exact scope and stopping decision

This closes two FULL calls on exactly two main owners per port under the
declared macro endpoint, even with arbitrary full-monomial owner boundaries
and interstage words. It does not close access to transformed helper
states, additional scratch mixing, changed native operations, inter-port
mixing with unbound coordinate frames, a different target invoice, or a
non-columnwise address grammar. The separate separated-H theorem covers a
different relaxed scratch model; these scopes must not be combined silently.

The hypothetical invoice `224H17+2H` against `2P` remains positive before
finite/compiler/outer work, but this endpoint cannot be attained in the
two-owner model. The controlled-phase policy is stopped. No wider circuit
enumeration or synthesis was run and no kappa improvement is claimed.
