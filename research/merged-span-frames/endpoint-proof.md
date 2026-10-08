# Multiplicative proof of the merged auxiliary endpoint edges

The merged-edge construction and exact profile formulas are from eumemic’s
PR96, pinned at 606d16d6dfc714d2a467190dc91b2f8dcab38d9c. The argument below
states its endpoint change directly in the inherited partial-swap operator
contract. It does not interpret a negative projector as a partial swap.

## Common-frame invariant and arbitrary dirty inputs

At each scalar gate, all incident role streams have a common invertible
address operator G. An edge from frame F to frame G applies GF⁻¹. Because
G commutes with pointwise gates, the physical array on a role is its assigned
address operator applied to its logical array. An auxiliary role is restored
by the scalar circuit for every logical initial array. If its source and
sink operators are S,T, its physical endpoint action is therefore TS⁻¹.
No source preprocessing is executed: the logical input is interpreted as
S⁻¹f for the actual arbitrary physical array f.

For one selected auxiliary, replace both endpoints by

    S′=S D_E,   T′=T D_E.

Then T′(S′)⁻¹=TS⁻¹. All gate frames, pointwise XORs, source-copy incidences,
scatter incidences, copied-center reads and other roles remain unchanged.
The original arbitrary-dirty scalar replay therefore still applies. This is
a change to endpoint interpretation and the explicitly paid first/last
edges; it is not free preparation of a dirty role.

## The two stages

Let H=I_h⊗B be the local ambient projector in the full m-dimensional
address space, and let E=I−H. Let A denote a local envelope projector,
embedded as A⊗B. Every such projector is orthogonal to E. Partial swaps obey
D_P²=I and D_P D_Q=D_(P+Q) for orthogonal projectors P,Q.

Stage 1 has auxiliary endpoints (S,T)=(I,D_I), local gate frame D_(A⊗B), and
last pre-exterior frame D_H. Its new endpoints are

    (D_E, D_I D_E) = (D_E,D_H).

Stage 2 has endpoints (S,T)=(D_E,D_H), local gate frame D_E D_(A⊗B), and last
pre-exterior frame D_I. Its new endpoints are

    (I,D_H D_E) = (I,D_I).

Both endpoint quotients remain D_I. In both stages the new first residual is

    D_(E+A_first⊗B),
    E+A_first⊗B = I−(I_h−A_first)⊗B,

and the final exterior becomes the identity. These are exactly PR96’s
creation-merged matrices, so its exact profile certificate can be reused
without altering the matrix formula.

For a non-output role, the last local cleanup and exterior have no intervening
gate or read. Their product is

    D_E D_((I_h−A_last)⊗B) = D_(I−A_last⊗B).

This is PR96’s retirement-merged matrix in both stages. A true output role
cannot use this replacement before its scatter or retained-center read.
The selection excludes all such roles. Creation and retirement choices are
mutually exclusive on each role because each uses its one exterior charge.

## Compatibility with deferred storage and selected coordinate flags

The endpoint argument depends on the actual first and last charged local
frames. Deferred clearing or reuse may change those frames, so they must be
reconstructed from the final serialized word. `endpoint_check.py` rebuilds
every role’s complete sequence of distinct frames from source incidences,
all literal XORs, and every output incidence. It compares those sequences
with the event log, checks all original envelope containments, validates the
selected endpoint edge and rank, and excludes output/scatter roles from
retirement merging. This includes clearing gates inserted late in the word.

The first and last local projectors are already expressed in the selected
coordinate flags. Simultaneous conjugation preserves idempotence and
orthogonality with E; the exact selected profiles must still be recomputed
in that fixed physical basis. No coordinate invariance of ordered profiles
is assumed.

## Independent finite checks and negative controls

The portable audit has no import from the production profile or arithmetic
checker. It verifies both stage identities using exact noncoordinate
rational projectors. It also runs a genuine common-frame XOR shear on every
address delta in each of three independent role streams, including arbitrary
dirty auxiliary data, in both stages and with both endpoint choices. There
are 8,748 complete basis runs.

Three negative controls are required:

1. Gauging only one endpoint changes the physical endpoint action.
2. Using D_(−E) literally gives the wrong endpoint action; it is not the
   operator D_E used above.
3. Adding an output role to the retirement selection is rejected by the
   explicit output/scatter eligibility rule, before any profile comparison.

The audit does not replace the original full word dirty replay, the exact
merged-profile certification, the complete paid ledger, or the finite
assembly inequalities. Those are separate required checks.
