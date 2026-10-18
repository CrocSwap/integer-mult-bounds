# Sharp minimum cost across all canonical-span decompositions

For any rank57 fitting matrix on the pinned PR2757 mask, assume both factor
families lie in that matrix's column and row spaces. If there are m=57+s
nonzero rational rank-one terms, then

    C >=334+2s.

The saved57-term construction attains334. Thus allowing arbitrary extra terms
within both spans cannot lower the invoice. The statement excludes exterior
factor directions, higher-rank fitting matrices, changed covers and changed
physical contracts. It is a finite decoder-cost result, not supplier admission.

## Common definitions and inherited normal form

Normalize the common diagonal to1. The existing normal-form proof gives
K=[I,A;B,BA] and factors U=[P;BP], V=[Q;A^T Q], with PQ^T=I57. The57 latent
coordinates consist of eighteen three-coordinate paired components H_i and
the three-coordinate component J. Invertible paired maps make each nonzero
paired component touch both physical triads, so its full port space is H_i.
The residual coefficients remain general linear functionals of component8.

Call a term pure when either latent factor is supported entirely in J, and
let p_J count these terms. This is the same definition in both inequalities
below. Each pure term costs3; each nonpure term costs at least4. Let L4,L5
count nonpure terms of actual tariff4 and5, and write D=2L4+L5. Since the
residual diagonal is nonzero, some nonpure term costs at least7. Consequently

    C >=6m-3p_J-D+1.                                      (1)

The extra1 is charged to a term outside both low-price classes. The pure
terms, the actual-price classes and this residual term are unchanged when
the identity is subsequently restricted.

## Full and restricted acyclic budgets

The existing complete40-space closure checks all272 ordered low-rank span
rectangles. Their maximal component supports are disjoint. A rank4 rectangle
has size1 by1; rank5 rectangles have size1 byk or k by1, k<=3. Each actual
term's supports are subsets of these maximal supports. Replacing a maximal
support by a nonempty subset only increases the probability that all source
components precede all reader components in a random order. The geometric
rank may be below the actual price because the closure omits the residual
line; this also only increases the discount available from the probability.

For a random order of all19 components, select each low-price term when its
source support entirely precedes its reader support. Selected terms sum to
a strictly block triangular N. Therefore I57-N remains invertible, so at
most m-57 terms were selected. The exact census probabilities give

    D <=4(m-57).                                          (2)

Now remove the p_J pure terms and restrict to the54 ordinary coordinates.
The remaining m-p_J terms sum to I54, and every one has nonzero projections
on both sides. Delete J from each low-price support rectangle. The supports
are still nonempty and disjoint, and selection probabilities cannot decrease.
Repeating the same argument for a random order of these18 components yields

    D <=4(m-p_J-54).                                      (3)

This second argument requires no minimality of the remaining factorization:
the only rank assertion is that I54-N is invertible and a sum of its remaining
rank-one terms. The first argument has the identical property for I57.

## Combine without discarding the pure-term count

Substituting(2) and(3) separately into(1) gives

    C >=2m-3p_J+229,
    C >=2m+ p_J+217.

One quarter of the first lower bound plus three quarters of the second
cancels p_J, proving

    C >=2m+220 =334+2s.

In particular m=58 costs at least336. The apparent333 possibility came from
retaining p_J in only the restricted inequality while discarding it in the
full inequality; it is not an unresolved construction after the two bounds
are combined.

## Exact replay and review scope

`check_canonical_sharp.py` authenticates the candidate, selected archive and
payload, reconstructs the40 spaces using explicit vector sets and
annihilators, and checks both selection probabilities on all272 rectangles.
It also verifies the exact affine combination, rejects missing closure
members and duplicate JSON keys, and prints a receipt without changing files.
The old checker uses an independent echelon representation. The proof was
separately audited by another AI agent; no human review or formal proof
assistant verification is claimed.

    python -I -O -B check_canonical_sharp.py --repo PATH_TO_REPOSITORY

Receipt: `CANONICAL-SHARP-RESULT.json`. Its low-rectangle table SHA256 is
`12858a508b318f62a568fe5205d16a399fc4e3e7fdc9cb7e8ea413f0a444832e`.
