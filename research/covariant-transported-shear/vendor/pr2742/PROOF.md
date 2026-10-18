# A covariant native action on the selected dirty reader

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
We construct a local native operator and its restoration word. We retain the
selected centre children and exponent.

## Statement and changed interface

Let A be the selected 8-by-704 scalar reader at the post-precondition,
pre-entry-adapter cut. We use forward events [7401,12550) of the pinned
gauge44 word. The input order is 112 X fields, 112 Y fields and 480 arbitrary
dirty helpers. The output centres are (92,57,81,224,11,240,9,256).
We inherit PR2491's framed-reader refinement

    R = T_out (A tensor I) U_in,

where T_out has the eight centre frames 415 through 422. For a data input j,
the actual entry adapter E_j satisfies E_j C_port(j)=T_start(j), so
U_j=T_start(j)^-1 E_j=C_port(j)^-1. We recheck this equality with exact phases
on all 112 data fields. Helpers in the support of A have frame zero and an
identity entry adapter. We check their 115 literal identity entries and the
absence of residual input wrappers; frame labels alone would not suffice.
Other input wrappers may be nontrivial; our action leaves
those fields untouched.

Fix lambda>=1 and the payload space H=(C^512) tensor-powered lambda times.
Let Q have row permutation (3,0,1,2,7,4,5,6). We construct an order-four binary
orthogonal sigma and put M=M_sigma tensor-powered lambda times. Our query
action is

    G = T_out (Q tensor M) T_out^-1.

This changes the predecessor's fixed Q tensor I action. A caller must consume
G or charge its inverse; it cannot observe the old intermediate outputs by
silently retagging them.

**Local theorem.** Under the pinned framed-reader interpretation, the literal
input action P in circuit.py satisfies

    R P = G R,       P^4=I,       G^4=I.

We implement P, its inverse and G using scalar field operations and native
monomials, with zero positive-rank Fourier children. We accept arbitrary,
correlated values in all 704 fields. We change the X bank and eight designated
helper outputs; we preserve the other 584 outputs at every literal prefix.
We restore all inputs through the inverse or four consecutive applications.
Intervening writes require a separate complete-word identity.

We use a nonunitary P: on helper 224 with payload basis state 0, we obtain
output squared norm 6 from input norm 1. We therefore use the nonunitary
escape outside PR2491's unitary obstruction. We preserve the
reader kernel as a subspace but do not fix it pointwise. We make no global
displacement-rank-six claim.

## Scalar and binary covariance

Write A=(A_X,0,A_H). PR2491 already supplies the signed data permutation
S_X with A_X S_X=Q A_X and S_X^4=I. We reconstruct it from the authenticated
reader: its 112 columns are distinct up to sign, with 80 positive and 32
negative transitions. Its unsigned cycles have lengths 1^4,2^10,4^22.
We do not claim this scalar permutation as new.

For the source port vectors u_j, solve sigma u_j=u_pi(j), where pi is the
signed permutation's underlying field permutation. With bit0 as coordinate0
and column vectors, we obtain

    rows    = [433,309,174,143,313,398,64,158,307],
    columns = [283,428,174,188,403,279,64,173,307].

The port vectors span F_2^9, so this solution is unique for these images.
We check sigma^T sigma=I, sigma^4=I and sigma^2!=I. We also check all vectors
in each centre hyperplane. The centre cycle is

    415 -> 416 -> 417 -> 418 -> 415,
    419 -> 420 -> 421 -> 422 -> 419.

Equivalently, sigma C_(q_i)=C_i for the row-i/source-q_i convention.
The payload operator M_sigma sends |x> to |sigma x>; it has order four.

For the selected C_q convention, conjugating the translation in direction q
by M_sigma gives the translation in direction sigma q, including its scalar
phase. Hence M_sigma C_q M_sigma^-1=C_(sigma q). For data edge j->i,

    U_i^-1 M_sigma U_j = M_sigma.

We check these 112 equalities against the actual source adapters, rather than
substituting a different Walsh-H convention.

## A section entirely inside the zero-frame helpers

All 115 nonzero helper columns of A_H have actual start frame zero. We leave
the other 365 helpers alone, including the 192 with nonzero start frames.
Choose helper pivots

    J=(224,225,226,227,240,241,256,257).

Let B=A_H[:,J], and let C contain the other helper columns. Exact elimination
gives det(B)=-32 and half-integral B^-1. In the split (h_J,h_N), define

    K_H(h_J,h_N)=(B h_J+C h_N,h_N),
    P_H=K_H^-1 diag(Q tensor M,I) K_H.

Thus

    h_J' = B^-1[(Q tensor M)(B h_J+C h_N)-C h_N],
    h_N' = h_N.

This is a reversible chart on dirty inputs; it requires no zero entry or
clearing. Its inverse replaces Q,M by Q^-1,M^-1. Since Q and M act on
different factors and both have fourth power I,

    A_H P_H=(Q tensor M)A_H,       P_H^4=I.

Only the eight pivots appear as destinations in the helper word. We retain
the nonpivot input contributions during both chart directions. Omitting a
helper from both directions preserves the inverse and fourth-power tests
but breaks the true reader identity; our controls exercise that failure.

Define the full scalar/payload action by

    P=diag(S_X tensor M, I_Y, P_H).

Then A P=(Q tensor M)A and P^4=I. This algebra holds over Z[i,1/2] for any
module carrying an order-four linear operator M. Our verifier replays every
column over Q[z]/(z^4-1), so it covers arbitrary dirty inputs and any such
specialization, including M_sigma tensor-powered lambda times.

## Native identity and phases

The completed X action commutes with its input wrappers by the data
covariance above. The helper action reads and writes only zero-frame helper
operands. On the remaining input fields P is identity. Consequently

    U_in P=P U_in,
    R P=T_out A P U_in
       =T_out(Q tensor M) A U_in
       =G R.

We therefore execute the literal scalar/payload word itself; we do not
normalize all X fields to frame zero and restore them afterward. Data swaps
are literal operations on physical arrays, and we check their completed
native boundary. We do not require each intermediate data mixture to carry
an old monotone frame label.

For each centre edge we compile

    T_Ci M_sigma T_C(q_i)^-1.

All eight blocks have rank zero. Their affine offsets and global phases are

| i | source q_i | offset | phase exponent modulo4 |
| --- | ---: | ---: | ---: |
|0|3|172|0|
|1|0|427|2|
|2|1|282|0|
|3|2|303|2|
|4|7|172|0|
|5|4|467|2|
|6|5|282|0|
|7|6|343|2|

RESULT.json retains the complete binary matrices and linear signs. All
quadratic rows vanish, but omitting the offsets or signs changes the
operator. Ali Romman's retained compiler supplies the monomial records;
the separate native interpreter compares 18 signed Pauli images and one
exact 512-entry basis-state image for each block. Pauli equality determines
a Clifford operator up to a scalar, and the nonzero state image fixes that
scalar. This establishes the full operator on the 512-dimensional space.

The wrong sigma^-1 orientation has rank two on all eight centre blocks.
A missing global phase passes the Pauli comparison and fails the state
comparison. We also verify the whole query action's fourth power, including
field labels and affine phases.

For lambda layers, tensor each exact block. In particular, apply its scalar
phase once per layer; a phase exponent2 becomes2*lambda modulo4. Tensoring
the exact one-layer identities proves the stated algebra for every lambda.
This is an algebraic extension, not a uniform physical-stream cost theorem.

## Literal invoice and precision

The helper basis factorization uses 28 scalar operations. It implements the
same B, with no changed reader coefficients. The nonpivot loads require
450 signed-unit ADDs. We add six swaps for Q, eight payload monomials and
the literal inverse chart. A swap uses three unit ADDs and one negation.

The X permutation uses 76 swaps and 32 sign changes, then one M_sigma per
data field. All data and helper fields already exist and may be dirty.

| One P or P^-1 | Scalar operations | Payload monomials | Positive-rank children |
| --- | ---: | ---: | ---: |
| X action |336|112|0|
| Helper action |980|8|0|
| Total |1316|120|0|

We use 1186 unit ADDs, five doublings, five halvings and 120
negations. At the retained two-real-component tariff, we charge 9748 real
scalar primitives per orientation. Each source read belongs to its emitted
ADD or monomial application. We do not price address movement as zero.

We implement G with six field swaps and its eight recorded monomial blocks:
24 scalar operations, 8 monomial applications and zero positive-rank children.
We charge the same count for its inverse. A caller pays these additional
costs when it applies or removes the query phase.

We use no algebraic scratch field or CLEAR. A machine implementation must
still supply buffers, address traversal and physical placement. We use
rank zero to classify native monomials and retain their address/phase work.

For one orientation from independent symbolic inputs, formal row L1 bounds
are 374 forward and 370 inverse. We also check both orientations starting at
each of the four phases. We obtain a maximum of 374 and coefficient
denominators at most 2. Since M is a unit-modulus permutation, the same L1 bound
controls physical amplitudes despite possible collisions between formal z
powers. For inputs on a fixed dyadic grid, one extra fractional bit and nine
integer guard bits suffice for these exact local words. The bound concerns
P-only phase changes; it does not bound an arbitrary intervening caller or
the complete recursive approximation error.

## Caller obligations and unchanged centre bill

After t applications the reader is G^t R. A caller must track that phase
and restore the source through the actual inverse or a justified complete
word. P^4 alone does not restore a source after arbitrary intervening writes.
Our helper pivots mix values, so the unsigned-permutation transported-ERASE
shortcut in PR2595 does not apply. Emit its full shear or charge the required
P^-t / ordinary erase / P^t sequence.

PR2500's typed echo permits order-four P,G with R_iP=GR_i and canonical child

    C_i(D,W)=(D+R_i W,PW).

Its canonical endpoint after the complete echo is D+=sum_i R_i X, with
source/work restored. That endpoint does not contain G, so a changed query
action can fit the algebra if both child orientations, phase corrections
and input/output placements change together. Our theorem supplies one
actual reader R. It does not supply a pair of host readers or a cheaper
implementation of the complete child.

An explicit expensive child can run the reader's invertible prefix N on W,
add its centre outputs to separate D fields, undo N, then apply P. Charge
both N and N^-1, the eight output ADDs, P and all movement. This is a
constructive existence argument, without a favorable supplier invoice.

The selected centre interval [12550,12759) still contains eight rank-eight
descents, eight copies, 176 ADDs and sixteen clears. We retain rank mass 64.
Returning a reader to canonical phase supplies its original centre values;
that alone removes none of these children or proves the surrounding word's
other outputs. We claim zero additional positive-rank children for the
standalone action, and zero deleted centre children.

Before another construction round, identify one requested target increment,
replace its complete native gather/centre/scatter word, and list the deleted
and added children. Include source restoration, output-phase operations,
hosting, physical movement and precision. The finite result here leaves
that consumer/admission problem open and preserves the selected exponent.
