# Independent review of the pure-cycle rank bound

The exact theorem is accepted for its stated operation set. For four
pairs and 112 ports, that set needs at least 65,408 native rank units per
cover copy. Scalar mixing, an arbitrary Y baseline, arbitrary borrowed
fields, and owned zero fields do not reduce this bound. The theorem does
not cover all native circuits or all cross-port mixing.

The producer freeze is
`15621e9a16d7390fb6073ad79d97dc7b09237263fb7d5c7be399047877590f08`.
The reviewed proof is `PURE-CYCLE-RANK.md`, SHA256
`b31fc1f1a632e323c80b8ba074116a1a2a12f28c66f1c85315f49fabe8ee58d5`,
in `history-encoding/terminal-line-fusion-20261018`. The local native
payload has decompressed SHA256
`b08cb4146f1aec241e027cd62c942f6eca4ddab3e97f000a9c0017575d36deb5`.
`REVIEW.json` records all other source pins and exact checks.

## Independent proof check

Fix a port and a ten-owner orbit. Its actual cycle permutes ten columns
of one orthonormal basis B and fixes the other 63 columns. Left
multiplication by an owner h preserves this fact. Thus the proof uses
one common Fourier coordinate system on the whole orbit. It does not
use a separate, incompatible coordinate system for each field.

Three tensor copies suffice. At each axis, the frequency bits 100 and
111 give directional-C eigenvalues i and -i. They have the same parity.
Consequently a translation applied to all tensor copies has the same
eigenvalue at both choices, even if its direction depends on the owner
or the field. Each axis choice is independent. These are actual finite
Fourier characters, not formal values of an indeterminate.

At one character, include all field and owner slots in one vector. Pad
any allocation by slots that start at zero. The input embedding and the
output projection are independent of the character. For two choices
that differ at one axis, the difference of two circuit products is a
sum with one factor difference in each summand. Rank subadditivity gives

    rank(P (M_l ... M_1 - M'_l ... M'_1) E)
        <= sum_t rank(M_t - M'_t).

This proof does not require an invertible factor. It applies to owned
CLEARs, zero allocation, and scalar COPY as well as invertible scalar
operations. Restrict the input columns to independent productive data
and project to the required productive outputs. Arbitrary borrowed
columns remain available to the circuit but cannot reduce the rank of
that required block. A correlated input cache would need its
preparation included in the circuit.

A complete native call on one field contributes rank one to an axis
test if its coordinate subset contains that axis, and zero otherwise.
The inverse-C case differs by a translation and has the same test.
The required FULL block changes by an invertible scalar multiple of A,
so its difference has rank N at each of the 73 axes. It follows that
the number of native incidences at every axis is at least N. Summing
gives total paid native rank at least 73N.

There are ten owners in each orbit: h L^k = h implies L^k = I, and the
literal L has exact order ten. For m pairs, N = 20m per port orbit.
After summing over the disjoint orbits and all 112 ports, the bound per
cover copy is 2m times 112 times 73. At m = 4 this is 65,408. This count
requires independent productive data at every owner, as the proof now
states. It is not asserted for a repeated-data restriction.

For an approximate *linear* circuit in the same operation set, the
corollary is correct if the error at both test characters is less than
the smallest singular value of A. For the stated unitary A this
threshold is one. The target difference has smallest singular value
twice that threshold. Nonlinear rounding is outside this argument.

There is also a conditional cost consequence. Suppose every native
rank r is at most 73 and its recursive term is proportional to
r^(1-b), for b >= 0. Then

    sum r^(1-b) >= 73^(-b) sum r >= N * 73^(1-b).

Thus this operation set cannot give a strict decrease from the native
cost of N full transforms under that cost model. Nonnegative scalar and
map costs cannot change this conclusion. This consequence needs the
stated rank cap and cost model. It is not a complete supplier bound.

## Independent source and phase checks

The reviewer did not import the producer's phase code or Clifford
compiler. The new checker forms binary polar matrices and exact Z4
diagonal values from the pinned vectors. Terms of degree at least three
vanish modulo four. This gives a complete phase equality test.

The complete local child recipes received an additional direct check.
For rank r, the native kernel has coefficient

    ((1+i)/2)^r * (-i)^weight(t)

at shift t in its r coordinate axes. The checker applies each literal
right monomial, this kernel, and each literal left monomial. It compares
every nonzero output coefficient with the required coordinate-C
product and its exact translation. Both sides have the same nonzero
Gaussian prefactor. All phase comparisons use integers modulo four.
Each output support has size 2^r, so this check also covers every zero
coefficient. It tests the full operation, including its global phase.

The checks passed for all 336 recipes and all 512 input columns per
recipe: 172,032 columns and 22,134,784 nonzero coefficients. This closes
the previously pending independent local native-recipe check. It does
not certify the recursive implementation of a child.

The separate phase checks passed for all 30,240 fresh factors, 22,400
actual idle factors, 1,120 FULL factors, and 1,120 terminal factors over
the ten owner positions. They also passed for all 1,008 complete owner
transfers, 2,016 literal DATA entries, 2,016 literal DATA exits, and 224
FULL cover-conjugate phases. In particular, the transfer has no payload
permutation after conversion to owner coordinates. The entry and exit
translations are included.

Two scope controls are explicit. Translation of only the second tensor
copy distinguishes 100 from 111, so it is not a permitted free map.
The odd non-coordinate native direction 111 has a nonzero polar term;
it does not pass the coordinate-subset test. This is a valid odd native
line and is a stronger control than an even direction.
The checker also rejects a literal child with an added global phase i.

The odd-direction control gives a concrete reason for the native-frame
restriction. On the eight width-three sign choices at axes 1, 2, and 3,

    C_(b1+b2+b3) has symbol -z1 z2 z3.

It is one rank-one native call but its symbol changes under all three
axis tests. The checker verifies all eight values. This restricted
character identity is not an equality to three coordinate C gates on
all inputs. It does show that a different native frame can escape the
incidence argument; the omission is material, not a proof convention.

## Claim limits

Each native call must be treated as a complete atomic operation with
both side maps. Its side maps can contain quadratic phases. The proof
does not permit a new operation inside this boundary. It also does not
permit an arbitrary payload map, an arbitrary cross-port transfer, or
a translation on just one tensor copy to be declared free.

Scalar mixing between banks and owners in one fixed-port orbit is
included. Cross-port mixing is included only if an additional proof
shows that it preserves one common set of sign tests. The present
packet gives no such general proof. The lower bound should not be
described as an obstruction to all fusion or all scalar controllers.

The lower bound is independent of the current 64,512 plus 896 native
invoice. The arithmetic equality is correct, but the bound alone is
not a complete implementation or price certificate. Global scheduling,
finite-grid precision, monomial map cost, storage, recursive hosting,
and the complete supplier and kappa calculation remain separate.

Run the independent checks with one process:

    python3 -I -B -O check_review.py

Expected result:

    PASS_INDEPENDENT_PURE_CYCLE_RANK_BINDING

The frozen producer bytes were preserved. No PR, commit, push, or
publication was made. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
This review and its checker were produced with AI assistance.
