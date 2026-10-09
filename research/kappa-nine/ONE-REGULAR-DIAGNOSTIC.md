# Bounded one-regular-block diagnostic: stop this candidate family

**Outcome:** twelve exact 18-label partial constructions pass their
checks, but none permits even one of the remaining 24 Y labels to be
added individually. All 288 extension checks give zero-dimensional
allowable image and dual spaces. No new kappa or full finite geometry
is established.

This was a deliberately bounded diagnostic: 12 deterministic candidates,
24 individual extension tests each, and no adaptive expansion. It is
now complete. The negative result is about the saved candidates, not an
impossibility theorem for one regular block, uniform mode 3, or the full
dimension-15 problem. All 103 complete branch cases remain open.

## The partial construction

Fix anchor block 0 as the sole regular block. The 18 Y labels supported
there belong to the three Y_j classes for the points on its Fano line.
Each class has four private coordinates in its other two anchor blocks.
Those private coordinate sets are disjoint between the three classes.

For each outside choice 7 or 8, construct the class's three rank-two
labels as a rational orthogonal decomposition of its six-dimensional
support. In local coordinates, a representative decomposition has image
bases

    (e_singleton, e_private0),
    (e_common + t e_private1, e_private2),
    (t e_common - e_private1, e_private3),

with nonzero rational t. Use the corresponding dual vectors, dividing
the mixed vectors by 1+t^2. The three labels normalize to I_2 and
annihilate one another. The singleton/common choices follow the forced
two-color pattern in the regular block.

Different classes meet only in that regular block. Their required edge
products vanish because the colors are opposite. This supplies a valid
18-label subsystem with exactly checked anchor support constraints.

The fixed batch varies rational mixing parameters, private-coordinate
orders, and small invertible rational transformations of each private
four-space. Every resulting factor matrix is saved in the artifact.
These choices are a restricted construction family; twelve trials do
not exhaust its continuous parameters or the general problem.

## Exact extension test

A remaining Y label has six allowed coordinates. Against the fixed
partial construction, each column of its A factor must lie in

    U = intersection of ker(B_S restricted to its support),

over adjacent fixed labels S. Each row of its B factor must lie in the
corresponding left annihilator of the adjacent A_S factors; call that
space V. Both spaces are computed over Q.

More generally, choose bases U_0 and V_0. A rank-two normalization
B_T A_T=I_2 is individually possible exactly when the pairing matrix
V_0 U_0 has rank at least two. This only concerns attachment to the fixed
labels; it does not certify compatibility among multiple new labels.

For every one of the 288 tested attachments, both annihilator constraint
matrices have full column rank six. Thus U=V={0}. The failure occurs
before any coupling between the 24 missing labels needs to be considered.

## Verification

The independent replay reads the saved rational factors and checks every
partial normalization, required zero product and anchor support. It
reconstructs each extension constraint matrix, checks the displayed
kernel bases, and verifies completeness by rank plus nullity. Three
focused tests pass.

An auxiliary known 42-label coordinate construction, with all blocks
unrestricted, supplies positive extension controls: its missing labels
are correctly accepted. This is a checker control, not a solution to
the one-regular-block problem. A forged pairing rank is rejected.

## Decision

Park this local construction family. It produces valid partial objects
but offers no demonstrated path to extension, and the agreed bounded
test produced no reason to expand it. Preserve the checker and the exact
partial factors as reusable diagnostics for a substantively different
idea. Do not automatically launch a larger parameter sweep or another
long nonlinear solve from these results.

The six- and seven-exception regimes remain mathematically open. The
broader 2^-9 target also remains open and still needs a substantially
better complete finite-network certificate and downstream accounting.

## Reproduction

    python3 research/kappa-nine/one_regular_diagnostic.py --output /tmp/one-regular-diagnostic.json
    python3 -m unittest discover -s research/kappa-nine -p test_one_regular.py -v

The implementation uses only the Python standard library. The fixed
batch took about three seconds here. No commit, push, merge, change to
the selected exponent, or modification of earlier receipts was made.
