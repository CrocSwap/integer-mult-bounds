# Independent review of partner retirement

The ordered local theorem is accepted. It cancels all 112 arbitrary
borrowed inputs from the retired Y bank. The Y bank contains an
invertible code of the original data. The X coefficient of the borrowed
inputs is also invertible. These statements hold without commuting a
line operator through a graph entry.

The reviewed producer freeze is
`ee4c11882ab042f3101b8ccc21e33cfae0348e48af77dcd1667757b94c403af6`
in `controller-followthrough-20261017/partner-retirement-20261018`.
Its proof has SHA256
`904950ea0121db197b8ce2142707e67981888a2499349ba1fb3ff069720b049d`.
The signed native response has decompressed SHA256
`0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee`.

This review proves the local algebra and checks its principal-unit
hypotheses. It does not certify the native prefix, inter-stage access,
helper leases, a global controller, or a terminal decoder. Those require
the separate literal implementation and cost packets.

## Independent ordered derivation

Let S and T be disjoint port sets. Put U = complement(S),
V = complement(T), and R = complement(S union T). The proof works for
any sizes of S and T. The actual packet has |S| = |T| = 8.

Let Q_p be an invertible operator on port p, and let q_p be its inverse.
Let J_t have arbitrary linear operator entries. Products retain their
order. Before the prefix, the physical input is (Qh,d).

After the prefix, define hat_h_S = Q_S h_S and hat_h_U = h_U. The X
input to the raw word is Q hat_h. The selected Y input on T is
Q_T z_T, where z_S = d_S and z_U = h_U+d_U. On V, the Y input is

    J_t[V,V] (z_V - hat_h_V).

The initial T exchange therefore gives the raw word normalized X
content w_T = z_T and w_V = hat_h_V. For V, the raw Y output is

    q_V (J_t[V,V](z_V-hat_h_V) + (J_t w)_V)
      = q_V (J_t z)_V.

For T it is h_T + q_T(J_t w)_T. The final T exchange gives

    Y_T = z_T,                 Y_V = q_V(J_t z)_V,
    X_V = hat_h_V,             X_T = h_T + q_T(J_t w)_T.

No inverse of J_t is used. The cancellations occur with the same
ordered graph entries. This proves the local identities even if the
graph entries are unrelated noncommuting operators. To implement the
ordinary precode reversibly, J_t[V,V] must be a unit.

## Weaker backward hypotheses and joint invertibility

The preceding stage need only provide

    h_S = p_S + q_S b,       d_S = Q_S a,
    h_U = p_U - v,          d_U = v,
    p_U = H_s^-1 (u - D_s Q_S a),

where H_s is a unit and p_S is any data-only linear function. In
particular, the formula for p_S from A_s is not needed. Substitution
gives z_S = Q_S a and z_U = p_U. All borrowed terms cancel from z.
No relation between J_s and J_t is needed for this cancellation.

Let K_s have identity rows on S and rows [D_s,H_s] on U. Let R_t have
identity rows on T and rows of J_t on V. In block order these are
triangular, with ordinary diagonal blocks H_s and J_t[V,V]. Therefore
the original-data to physical-Y map is the unit

    E = diag(I_T,q_V) R_t K_s^-1 diag(Q_S,I_U).             (1)

This statement needs both ordinary blocks to be units. It does not
need J_s, J_t, their selected principal blocks, or A_s to be units.

Write D = diag(I_S,-I_U) and

    N = P_T q_T J_t[T,V] P_V.

The borrowed coefficient in X is G_b = (I+N)D. Since V is the complement
of T, N has source columns only in V and target rows only in T.
Thus N^2 = 0 without a commutation assumption. Its exact inverse is

    G_b^-1 = D (I-N).

This gives X_S = b, X_R = -v_R, and

    X_T = -v_T + q_T(J_t[T,S]b - J_t[T,R]v_R).

There is a further consequence. Write the complete local map as

    X = C x + G_b y,       Y = E x.

Since E and G_b are units, this joint map is a unit for every C:

    x = E^-1 Y,
    y = G_b^-1 (X - C E^-1 Y).

Hence the local retirement operation does not require its X data
coefficient to be invertible. This does not remove a separate global
controller requirement for that coefficient, if a controller imposes
one. It does identify which hypotheses this retirement theorem uses.

The optional correction uses w_T = Y_T and w_V = X_V, all in FULL.
Subtract q_T(J_t w)_T from X_T. The result is hat_h on every port.
Its borrowed coefficient is D. This correction acts on the full state;
it is not just a change to the borrowed coefficient. A direct version
needs eight inverse-line queries, plus their scalar, access, restore,
and storage obligations.

## Actual response and complete column checks

The independent checker uses exact fractions and operator words in
execution order. It reduces adjacent powers of the same Q only. Route
tokens retain their stage, source, and target. It imports no producer
code. It checks all 224 independent local input columns and then builds
the preceding backward data coefficient from the original 112 inputs.
It checks all 224 original data and borrowed columns again.

Every borrowed coefficient in Y is zero. The exact X source matrix,
its ordered inverse, and the optional eight-query correction pass. An
arbitrary new selected data coefficient leaves Y unchanged. Omitting
the selected positive Q, omitting the ordinary gauge, or moving q
through a graph entry fails. The generic local map has no coefficient
of any h_S input in Y, which proves independence from every p_S.

Both complete ordinary blocks have size 104 and determinant 2^60.
Their inverses are dyadic, and both inverse orders pass. The row codes
K_s and R_t also have determinant 2^60. The checker verifies G^2 = I,
GJ = JG, and G(S) = T directly from the pinned scalar response, after
extending G by the identity on its separate 64-port block.

The 40-port large-component gauge from the S8 packet is not the whole
104-port ordinary gauge. Its determinant is 1/16. The separate 64-port
negative-Hadamard block supplies determinant 2^64 and must also be
implemented and priced. The native emitter has been asked to bind
the complete 104-port gauge and its inverse.

The principal-unit calculation is in one current chart. To apply it
to routed operator blocks, the implementation must transport a block
and its inverse consistently. It must also identify the preceding and
current same-port Q views before using (1). Independent formal route
tokens in the algebra do not establish those physical identifications.

## Terminal endpoint guard

The retired physical Y is (1), not a FULL copy of x. A direct decoder
can first apply Q_V to its 104 hole fields. In the common FULL view,
R_t^-1 followed by K_s gives diag(Q_S,I_U)x.

To obtain FULL x from there needs q_S on eight fields. This is the
104 + 8 = 112 native-line count. It does not reach the required qx
hole endpoint.

For that endpoint, the remaining operator is q_S^2 on S and q_U on U.
For the actual intrinsic rank-one C frames, q_S^2 is monomial. Thus
this direct route has 104 normalization lines, 104 demotion lines, and
eight even-line monomial maps: 208 native lines in total. Its scalar
codes, routes, monomial maps, precision, and hosting still need a full
invoice. The count is not a lower bound on all possible decoders and
is not itself a global terminal construction.

The 16-line prefix count likewise covers only eight positive Q lines
on S and eight on T. Its sixteen ADDs and the complete ordinary gauge
must be included. The initial Y_S -= X_S is a raw physical array ADD;
the two fields do not have the same logical frame. Literal access and
frame bookkeeping must use that physical interpretation. At each fixed
local address z it is the update Y_p[z] -= X_p[z]. Q remains in the
operator coefficient. Defining the changed native X input as q times
the changed physical array does not execute an inverse Q for free.
This is the same explicit boundary model described in
`native-escape-20261017/RAW-SELECTED-BACKWARD.md`. The new literal emitter
must still bind its own addresses and retain the complete coefficient.

Run the independent check with one process:

    python3 -I -B -O check_review.py

Expected result:

    PASS_INDEPENDENT_PARTNER_RETIREMENT

No frozen producer file was changed. No PR, commit, push, or publication
was made. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
This review and its checker were produced with AI assistance.
