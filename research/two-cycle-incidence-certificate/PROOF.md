# Two-cycle incidence certificate

## Scope and exact sources

Use the formal model from
[PR #6012](https://github.com/CrocSwap/integer-mult-bounds/pull/6012):
two scalar roles over F2[GL_n(F2)], n>=3, with target [c]I_2.
Here c cycles address coordinates 0,1,2 and fixes all spectators.
A paid call is D(g,P)=I+([g]+[e])P, where g=I+e_i e_j^T,
i!=j, and P is a rank-one binary idempotent. Equality means equality
of every formal group coefficient.

Free scalar maps are normalized into the projectors. Augmentation of
the target forces the remaining terminal scalar map to be I. This
normalization is inherited from the credited formal-model sources.

The source
[two-write proof](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/research/two-write-spectator-projection/README.md)
proves that the two writer projectors of a restored coordinate are equal.
For a moved coordinate they are complementary. The moved-row conclusion
uses both the word and its inverse. Transposition gives the same rule for
reader pairs. Its selected middle labels and their g b h relabeling remain
required. We do not replace that proof by an augmented-matrix relaxation.

PR6012 reduces a possible word shorter than twelve to five address
coordinates. At length ten, each coordinate is read and written exactly
twice. The two-write equations therefore apply to all ten reader/writer
pairs. These source results are premises; their complete original
scientific suites are not replayed here. Their exact proof files and the
related commuting-method source are authenticated by SOURCES.json.

## 1. One ordinary 3-cycle still costs six with dirty spectators

A coordinate CNOT changes one row by adding another. Read matrix factors
in execution order, with the rightmost factor first. Build the undirected
interaction graph in that order. A gate that joins two previously
disconnected components cannot change a diagonal entry: the source row
has no coefficient at the destination coordinate. Initially all diagonal
entries are one.

Consider the final interaction component that contains the three target
coordinates. It contains all three, since their final cycle moves their
basis vectors among them. If this component contains s vertices, exactly
s-1 gates first join its components. Each of its three target diagonal
entries is zero at the endpoint. Each requires a gate that changes that
entry; that gate is not a join. A gate changes only one row, so at least
three other gates are required. If a spectator is in this component,
s>=4 and the component uses at least (s-1)+3>=6 gates.

If no spectator is in the component, its action is a word in GL_3(F2).
The complete 168-state breadth-first certificate gives distance six to
each of the two coordinate 3-cycles. The independent enumeration of all
512 binary 3x3 matrices finds exactly those 168 invertible matrices.
The BFS includes all six coordinate CNOTs at every reached state, so it
excludes every shorter word in this finite base case. Gates on other
components cannot change this action.

The usual six-gate construction on the three target coordinates attains
the bound and leaves every spectator unchanged. Thus the exact ordinary
cost is six for every n>=3.

This argument retains the connectivity/diagonal method credited to Alan
Bu, Evan Fan and Robert Joo in
[Minimum Synthesis Cost of CNOT Circuits](https://arxiv.org/abs/2408.07898).
Their permutation-circuit result is established prior work. The present
small proof and finite certificate make this source application explicit;
they are not a claim of a new ordinary CNOT lower bound.

## 2. Exact twelve-call minimum in the commuting two-role class

Let P be one rank-one idempotent. A rank-one idempotent Q that commutes
with P preserves both one-dimensional spaces im(P) and ker(P). In that
basis Q is diagonal, idempotent and has rank one. Hence Q=P or Q=I+P.
This holds for all six binary rank-one projectors, and is checked on all
36 ordered pairs.

If all call projectors commute, one fixed scalar basis puts them in the
two coordinate projections. Every call then acts in exactly one of two
scalar lanes. The complete formal endpoint is the pair of ordinary
address-group products in those lanes. The target [c]I is unchanged by
this scalar basis change, so both lane products must equal c. Section 1
requires at least six calls in each lane. Thus at least twelve paid calls
are necessary.

Conversely, put one six-CNOT construction in each lane. This realizes
[c]I with twelve calls in every n>=3. The bound is sharp in the stated
commuting class. It excludes neither noncommuting projectors nor larger
scalar-role models. The diagonalization method already appears in Aaron
Wang's [PR #2317](https://github.com/CrocSwap/integer-mult-bounds/pull/2317)
for a different SWAP endpoint and retains that credit.

## 3. The incidence obstruction

For a residual ten-call word, make one vertex per call. Join the two
writers of each address coordinate with a writer edge. Join its two
readers with a reader edge. Each vertex has one edge of each kind.
The graph is a disjoint union of alternating even cycles; parallel
writer/reader edges are allowed.

Give an edge parity zero for a spectator coordinate and one for a target
coordinate. By the source two-write lemma, its endpoints have equal
projectors at parity zero and complementary projectors at parity one.
An odd parity sum around a component would force P=I+P, which is
impossible. If all component parities are even, one root projector
determines every projector in that component.

In a connected graph all projectors therefore lie in one complementary
pair. Section 2 requires twelve calls, contradicting length ten.
This is JoyboyBrian's released connected-incidence reduction, now bound to
the source proofs and the complete finite certificate below.

A disconnected consistent graph with c components has exactly 6^c
projector assignments satisfying the pair equations. Exactly 3*2^c
assignments use a single common complementary pair: choose one of the
three unordered pairs and one orientation for each component. Those
assignments are also excluded. The other assignments are possible inputs
to the unresolved full formal equations; they are not valid endpoints.

## 4. Exact census domain and result

Fix writer positions 2i and 2i+1 for coordinate i, i=0,...,4. A reader
assignment is a length-ten sequence in which each coordinate occurs twice
and the reader differs from the writer at every position. Enumerate all
such sequences. Every actual ten-call incidence graph maps to this
domain by relabeling call vertices to group the writers.

This relabeling forgets chronology. It is used only for graph constraints.
It is not a legal reordering of a formal word. The counts below are
normalized assignments, not graph-isomorphism classes, chronological
programs or numbers of possible endpoints.

| Consistent pair equations | Components | Assignments |
|---|---:|---:|
| No | 2 | 3072 |
| No | 3 | 1920 |
| No | 4 | 432 |
| No | 5 | 42 |
| Yes | 1 | 4992 |
| Yes | 2 | 2688 |
| Yes | 3 | 560 |
| Yes | 4 | 48 |
| Yes | 5 | 2 |

All 13,756 assignments are accounted for. Pair parity rejects 5,466.
The connected obstruction rejects another 4,992. The remaining 3,298
disconnected assignments contain 247,296 noncommuting projector assignments
that satisfy these pair equations. No claim is made that any one realizes
the target.

Graph propagation agrees with a separate GF2 equation elimination on
every assignment. A separate coefficient-count dynamic program verifies
the total number of loop-free reader assignments. The source-domain
limits are thus explicit, and completeness has two different checks.

## 5. Formal endpoint controls

The released connected fixture uses labels (i,i+1 mod5), i=0,...,4,
followed by (i,i+2 mod5), i=0,...,4. Its consistent projector colors are

    0,0,1,0,1,1,1,0,0,1.

It passes all reader and writer pair equations. It is connected and puts
five calls in each lane. Its full formal product is not the target for
any of the six root projectors: each product has two distinct group
labels. This shows that pair parity alone is not sufficient.

The two exact engines use binary matrices and complete permutations as
group labels. Their scalar coefficient multiplication is also separate.
They compare every formal coefficient; neither accepts only a natural
matrix image. They agree on 36 twelve-call attainers and 216 mixed-lane
fixtures. All 432 single-call deletions from the attainers fail.

Additional controls detect a flipped incidence parity and the missing
middle-label relabeling in D(g,P)D(h,P)D(g,P). A four-term formal polynomial
with distinct labels has zero natural matrix image, which shows why that
quotient cannot replace formal equality. A five-component graph passes
the pair filter, and an explicit noncommuting pair stays outside the
commuting proof. Three copied predecessor files are changed one at a time
and each change is rejected by source authentication.

## Limits and credit

The unrestricted five-coordinate ten- and eleven-call cases remain open.
The next useful step is the full selected-middle/off-subgroup equations on
the disconnected noncommuting cases, with their original chronology.
This certificate does not create a native operator, physical tariff,
supplier, new kappa or selected-frontier change.

Credit JoyboyBrian for PR6090 and
[the released incidence handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/6075#discussioncomment-19234840);
Nick Petalas for PR6012; Mihir Srivastava for the formal model;
James Reed / @jwr404 for PR5005/PR5379; Aaron Wang / @navinor for the prior
commuting reduction; and Bu, Fan and Joo for the ordinary CNOT method.
All predecessor notices and sources remain unchanged.

The new contribution is this exact normalized incidence certificate and
source-bound completion with full formal controls. No priority is claimed
for the handoff lemma, commuting diagonalization or ordinary CNOT bound.
Independent human review, proof-kernel formalization, full source search,
selected cold replay, Lean and Docker are unrun. Prepared by Ali Romman
with substantial OpenAI Codex assistance. New work is Apache-2.0.
