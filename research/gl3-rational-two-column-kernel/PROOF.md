# The exact two-column kernel over characteristic zero

This is a scoped proof using the finite exact certificate in `verify.py`.
It concerns the address permutation algebra alone. No complete complex
unit or multiplication theorem is asserted.

## Statement

Let G=GL_3(F2), let V=Q^{F2^3}, and let P_g e_x=e_{gx}.
For f>=1 define the algebra homomorphism

    rho_f : Q[G] -> End_Q(V^{tensor f}),
    rho_f([g]) = P_g^{tensor f}.

Write C_j for the sum of all elements of order j in Q[G], and put

    E = 6[1] - 2 C_2 + 2 C_4 - C_7.

Then

    E^2 = 56 E,
    ker rho_2 = Q[G] E,
    dim_Q ker rho_2 = 18,
    dim_Q image rho_2 = 150.

The same statements hold after extending scalars to C. The map rho_f is
injective for every f>=3. Thus width three is the smallest single positive
width that certifies every formal identity in this characteristic-zero
address algebra. A two-register restored shear realizes a nonidentity
formal map that is identity at both widths one and two.

## The finite certificate

The verifier constructs G in two ways. First it lists all three nonzero
binary columns and keeps the invertible matrices. Second it closes the six
elementary binary row additions, with a bound of 168 visited elements.
Both constructions give the same 168 address permutations. The multiplication
table is literal permutation composition, so no presentation or external
group data are assumed.

Their order populations are

    order 1: 1, order 2: 21, order 3: 56, order 4: 42, order 7: 48.

The verifier forms all coefficients of E^2 by integer convolution and checks
E^2=56E in all 168 coordinates. It checks centrality against all 168 group
elements. Centrality also follows because element order is conjugacy invariant.
It then sums all 168 permutation actions on all 64 point pairs and checks
that every one of the 4,096 entries of rho_2(E) is zero. These are finite
integer identities, with no numerical tolerance.

Let A_g be the 64 by 64 matrix P_g^{tensor 2}, viewed as a column of 4,096
integers. The Gram matrix of these 168 columns has entries

    H[g,h] = <A_g,A_h> = #{x in F2^3 : gx=hx}^2.

The equality holds because a common nonzero entry of two permutation matrices
is a point pair whose two coordinates have the same images under g and h.
The verifier constructs H from this formula. Gaussian elimination modulo
65537 selects 150 row indices and 150 column indices. A second determinant
calculation on that original integer minor gives a nonzero residue. Trial
division through 256 proves the modulus prime. The generated receipt records
the complete indices and determinant residue, so the minor is reproducible.
Consequently rank_Q H>=150, hence rank_Q rho_2>=150. No inference of a
rational upper rank from a modular upper rank is used.

## Why this is the entire kernel

Set e=E/56. The checked product identity says that e is an idempotent.
Left multiplication L_e on Q[G] is therefore an idempotent linear map.
Every diagonal entry of L_e is the identity coefficient of e, namely 6/56.
Its trace is

    168 * 6/56 = 18.

An idempotent over Q has eigenvalues zero and one, so its rank equals its
trace. Since e is central, its image is the two-sided ideal Q[G]e=Q[G]E.
The checked rho_2(E)=0 puts this 18-dimensional ideal inside ker rho_2.
It follows that rank_Q rho_2<=168-18=150. The minor proves the opposite
inequality. Thus the image rank is 150 and this ideal is exactly the kernel.
Ranks of rational matrices are unchanged by extension to C, which proves
the complex version as well.

## Why the third column suffices

The tuple (1,2,4) is the ordered standard basis of F2^3. Its images under
G are all distinct. For a=sum_g a_g[g], the coefficient at (g1,g2,g4) of

    rho_3(a) e_(1,2,4)

is exactly a_g. Hence rho_3 is injective. For any f>3, append zero columns
to this tuple. All address maps fix zero, so the same regular orbit and
coefficient recovery apply. This is the standard regular-orbit argument
already used in the binary-stream predecessor. The new content here is the
characteristic-zero kernel below it.

## A restored two-register witness

Write E=sum_g c_g[g]. There are 112 nonzero c_g. Start with arbitrary
independent registers (x,y). For each such g, in lexicographic permutation
order, execute

    y <- P_g^{tensor f} y
    x <- x + c_g y
    y <- (P_g^{-1})^{tensor f} y.

Every term restores the source y exactly. The final map is

    (x,y) -> (x + rho_f(E)y, y).

It is invertible, with inverse obtained by changing every c_g to -c_g.
It uses no clean scratch, erasure or assumption that either input is zero.
These address maps and rational scalar additions are free in the stated
address-only part of the complex engine game. No physical movement or
precision price follows from that algebraic convention.

At width two the map is identity by rho_2(E)=0. At width one the same
identity follows by restricting the width-two calculation to pairs (x,0).
The verifier also executes the chronological word on the complete dirty
input bases, 16 columns at width one and 128 at width two, and checks source
restoration after each term. At width three, take x=0 and y=e_(1,2,4).
The 112 nonzero coefficients of E occur on distinct output basis vectors,
so the word is not identity. The verifier executes that witness too.

## Limits

The arithmetic identities and nonzero minor are exhaustive finite evidence.
The linear-algebra deductions above are written proofs, with independent
human and formal proof-kernel review unclaimed. This package does not classify
the characteristic-two kernel, arbitrary address dimension, affine maps,
phase letters, paid C-calls or native precision and tape costs. In particular,
width three certifies only identities whose coefficients lie in Q[G] or C[G].
It is not an all-width test for the full complex engine.
