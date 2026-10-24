# A rank bound for the pure-cycle operation set

The fresh three-child construction cannot gain native rank by a scalar
mix of its two data fields, by an exchange of their completion paths, or
by a change to their scalar controller, if all complete native calls and
free maps stay in the operation set below. The bound includes changes
to the arbitrary Y baseline. It does not assume that Y is zero.

For four pairs and 112 ports, the bound is 65,408 native rank units per
cover copy. This is exactly the productive target rank, 896 times 73.
Thus this operation set cannot supply the required saving of 144 rank
units. The bound is independent of the number or size of scalar ADDs.

This is a restriction on a specified operation set. It is not a lower
bound for all native circuits. In particular, it does not permit a new
payload map to be called free without checking the test below.

## The allowed operations

Fix one port p and one orbit of the common response E on cover owners.
The orbit has ten owners. Let

    B = h [the actual nine-axis port chart, the 64 fresh unit axes].

B is one fixed orthonormal basis of the 73 payload axes. The ten owner
bases differ only by the cycle of ten columns of B. Use raw physical
data as the inputs. In particular, the logical notation Qx for a raw X
input does not supply a free Q operation in this model.

The circuit can use any finite number of fields on this orbit. It can
use arbitrary borrowed inputs and owned zero fields. The permitted
operations are:

1. Scalar linear operations between fields. Their coefficients do not
   depend on the payload address. This includes ADD, scaling, copying,
   exchanges, and CLEAR on owned fields.
2. The cover permutations and complete uniform payload translations in
   the pinned common-cycle construction. A uniform translation applies
   the same 73-bit vector on every tensor copy.
3. A complete one-field native call whose exact net map is, up to such
   a translation, a product of directional C transforms along a subset
   S of B. Its paid native rank is at least |S|. An inverse directional
   C has the same test and price as a positive C.

The result also permits any free linear operation whose matrix is
unchanged by all sign tests defined below. Thus it includes arbitrary
scalar mixing of the two banks and of owner fields within this orbit.
The free operation need not be invertible. Fields can be added as zero
inputs and removed after a CLEAR.

Each serialized child is grouped with both of its side maps. Its side
maps can contain quadratic phases. The proof uses the exact pure-C net
map of the complete child. It does not permit a new data operation
between a side map and that child. Such an operation must receive a new
analysis.

The actual common-cycle transfers are cover permutations and uniform
translations. No payload permutation remains in their complete
owner-coordinate map. The local body views cancel as specified in the
phase packet. This distinction is needed: a general payload permutation
or quadratic phase need not preserve the tests.

## Independent sign tests on legal tensor characters

Let the tensor width f be at least three. Use Fourier characters on its
f copies. For each basis axis j, independently choose its frequency
bits on the first three copies to be either

    (1,0,0) or (1,1,1).

Set the remaining bits to zero. The pure directional transform on axis
j then has eigenvalue

    z_j = i or -i.

Both choices have odd total weight. Consequently every uniform
translation has the same eigenvalue for all these choices. Equivalently,
its value depends on z_j squared, and z_j squared is always -1.

There are 2^73 independent choices. Each is an actual Fourier character
of the stated finite tensor domain. No formal extension of the input
space is required. For every j, let sigma_j exchange the two choices
at axis j and leave the other choices fixed.

Every allowed free operation has the same matrix at z and sigma_j z.
A complete native call on S multiplies one field by a nonzero scalar
of the form

    translation(z squared) * product_(j in S) z_j.

Its matrix difference under sigma_j has rank zero if j is outside S,
and rank one if j is in S. This is true for positive and inverse calls.

## The rank argument

At a fixed character, include all fields in one finite vector. Zero
allocation can be represented by an input embedding, and final output
selection by a projection. Write the full circuit matrix as a product
of the matrices of its operations. The difference of two matrix
products is the sum of terms with exactly one factor replaced by its
difference. Matrix multiplication cannot increase rank. Therefore

    rank(T(z) - T(sigma_j z))
        <= sum_over_operations rank(M(z) - M(sigma_j z)).       (1)

The same inequality holds after the input embedding and output
projection. It does not require a free factor to be invertible. Thus
owned CLEARs and arbitrary borrowed state do not invalidate it.

Suppose N independent productive inputs on this orbit must each receive
the full 73-axis transform. A fixed output exchange or a free cover
map can be included. In the chosen basis, the required input-output
block is

    T_required(z) = (product_(j=1)^73 z_j) * A,

where A is an invertible matrix that is independent of all sign choices.
The change from the standard full frame to B contributes only a uniform
translation. The pinned phase calculation checks that statement.
For every j the difference of this required block has rank N.

Let n_j be the number of one-field native calls whose set S contains j,
with multiplicity. Equation (1) gives N <= n_j. Sum over all 73 tests:

    total paid native rank >= sum_j n_j >= 73 N.                (2)

A batch over ten cover owners contains ten one-field calls in this
sum. It is not one call. The proof does not omit the cover multiplicity.

## Binding to the fresh-cycle construction

The pinned port chart gives B before the left factor h. The cycle L_p
permutes ten columns of B and fixes the other 63. Hence the orbit
h, h L_p, ..., h L_p^9 has one common B.

At stage s the three complete native products are

    C_(rho_s v0),
    C_(rho_s root9) C_q^-1,
    C_(rho_s root9) C_q^-1 C_(rho_s v0)^-1.

Their ranks are 1, 8, and 7. At every owner in the orbit, the checker
expresses each complete Z4 phase polynomial in B coordinates. Its
quadratic part vanishes. Its odd linear coefficients select exactly
1, 8, or 7 basis axes. Its even coefficients are the exact uniform
translation. This checks the phase, not only the polar span.

The same check applies to every old DATA idle recipe on this port and
to the full output frame. It also checks the two terminal line
directions. The checks cover all 112 ports and all ten owner positions.
The already pinned local native packet supplies the complete child
side-map identity. The common-cycle phase and exit packets supply the
exact conversion from local body views to owner coordinates.

For m pairs, each orbit has N = 20m productive fields. The cover action
has no shorter orbit, because h L_p^k = h implies L_p^k = I. Summing
over ports and all cover orbits gives

    rank per cover copy >= 2m * 112 * 73.

These are independent arbitrary inputs for every productive owner. No
relation between the data in distinct cover classes is imposed. The
rank conclusion is not asserted on a smaller, repeated-data input set.

For m=4 this is 65,408. The current complete construction has 64,512
rank units before its 896-unit terminal and attains this bound. A new
scalar controller or a two-field completion exchange within the stated
operation set cannot reduce that total. The proof does not depend on
the old endpoint formula or on the old scalar order.

## Scope and next useful change

The proof allows a changed Y baseline and arbitrary scalar coupling.
It rules out an attempt to save a terminal line by moving the same
coordinate-C factors to another field in this operation set.

A useful escape must fail at least one stated premise. Examples include
a new payload map that is not invariant under a sign test, a native
frame outside this common coordinate basis, a transfer between ports
with incompatible bases, or an operation inside a child side-map
boundary. Each such change needs its own phase, input, and cost proof.
None is certified by this note. Nonlinear finite-grid operations are
also outside the model.

The argument is exact. It does not by itself prove a lower bound for
all approximate algorithms. For the actual raw target, A consists of
translations and signed exchanges, so A is unitary. In this case the
bound is stable under an output error smaller than one in operator norm
on both members of every sign-test pair. The required difference has
all N singular values equal to two, so the perturbed difference still
has rank N. For a general invertible A, replace one by its smallest
singular value. A full finite-precision supplier must establish the
applicable error statement separately.

Run the finite binding checker with one process:

    python3 -I -B check_pure_cycle_rank.py

The checker does not run the complete supplier or replace the pending
independent native review. No PR, commit, push, or publication is part
of this work. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
