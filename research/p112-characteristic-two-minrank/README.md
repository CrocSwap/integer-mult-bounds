# P111 and P112 block-rank and binary broadcast certificates

For both the selected 111-port graph and the pinned 112-port graph, every
fitting matrix with invertible d-by-d
diagonal blocks has rank at least **9d over every field**, for every positive
integer d. The existing binary labels attain 9d over every characteristic-two
field. In the corresponding side-information graph, even nonlinear zero-error
codes for d-bit messages require exactly **9d broadcast bits**.

The selected P111 corollary is checked directly against the PR589 native-word
input. It does not assume that P111 is a subset of this particular P112:
a coordinate reflection places the same 14-vertex witness inside P111.

A source-pinned induced graph on 14 vertices certifies these statements: in the
usual fitting/side-information convention it is four isolated vertices disjoint
from the Petersen graph. Petersen's broadcast rate five is known from
[Blasiak, Kleinberg and Lubetzky, Fact 5.6(1)](https://www.cs.cornell.edu/~ablasiak/papers/bkl-beta.pdf).
This package supplies the explicit embedding, an exact rational certificate for
that known bound, and a separate short characteristic-two proof. It makes no
novelty claim for the Petersen theorem or the inherited binary upper bound.

This closes scalar, block-linear and binary nonlinear rank/broadcast compression
of this fixed graph below nine. It supplies no new native circuit, helper
inventory, multiplication theorem or improved exponent. An abstract broadcast
code is not a legal reversible supplier word.

## Exact object and graph convention

Use root_lines[8:] and binary_ports[8:] from
[PROTOTYPE.json](../direct-delivery504-global/inputs/hamming/PROTOTYPE.json).
The removed eight roots are twice the coordinate vectors. The remaining 112
integer roots have squared norm four; distinct root dot products are -2, 0 or 2.
All vertex indices below are zero-based after removing the eight rows.

Let R be the required-zero graph: distinct i,j are adjacent when their root dot
product is nonzero. It has 2,912 unordered edges. A block matrix fits this
convention if M_ii is invertible and M_ij=M_ji=0 on every edge of R. Symmetry
of M is not assumed. Left multiplication by diag(M_ii inverse) normalizes
all diagonal blocks to I_d without changing rank or required zeros.

Let G be the complement of R. This is the usual Haemers fitting graph, with
zeros required on nonedges, and the side-information graph in which receiver i
knows x_j precisely for neighbors j in G. Thus G is the induced E8
orthogonality graph. The two graph conventions must not be interchanged.

The source commit is 0b1cccf86e2f5132ed286a26ef0a681a495740ea and input SHA256
is 327d2a868043e846381aa58a33053c24425e8cad522ff401b10ec8af1d649a3f.
[SOURCES.json](SOURCES.json) also pins the Git blob and historical catalogue
and selected record. No predecessor or selected-record file is modified.

## Four cliques and a 14-vertex embedding

These are eight-cliques in R:

~~~text
C1 = 2, 16, 57, 70, 78, 84, 100, 102
C2 = 10, 16, 57, 70, 78, 84, 108, 110
C3 = 2, 10, 16, 32, 34, 57, 70, 84
C4 = 16, 32, 57, 68, 70, 84, 100, 108
~~~

Their union has 14 vertices and 76 induced edges of R. Exactly
T={34,68,102,110} has odd incidence, and T itself is a four-clique in R.

Within this union, U={16,57,70,84} is adjacent in R to all other vertices.
Identify the remaining vertices with two-subsets of {0,1,2,3,4}:

~~~text
2:02   10:12   32:23   34:24   68:34
78:01  100:03  102:04  108:13  110:14
~~~

The checker verifies every pair: two of these vertices are adjacent in R
exactly when their subsets intersect. Consequently the induced graph in G is
four isolated vertices plus the Petersen graph, whose edges join disjoint
two-subsets. This is an explicit isomorphism, not a degree-sequence inference.

## Corollary for the selected P111 supplier

The current bit supplier uses the 111 labels in
[bitE8mut-p111-tuned.json.gz](../e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz),
SHA256 e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f.
Negate coordinate 1 (zero-based) of each of the fourteen P112 witness roots.
Up to the sign of a root line, the resulting P111 indices are:

~~~text
P112:   2  10  16  32  34  57  68  70  78  84 100 102 108 110
P111:  12  16  26  38  40  63  69  71  74  84  99  97 107 109
~~~

[p111_corollary.py](p111_corollary.py) reads both pinned inputs without importing
another verifier. It checks the reflection, every induced pair, the four
eight-cliques and odd-incidence four-clique directly. The same all-field rank
proof and nonlinear entropy proof therefore apply; the latter fixes 97
outside messages instead of 98. Matching the P111 root lines to the inherited
full 120-label binary construction verifies all 12,321 Gram entries, all
2,870 required-zero pairs, and exact rank nine. Thus both full graphs have
block rank exactly 9d in characteristic two and binary broadcast length
exactly 9d for every positive d. Only their all-field lower bound is asserted.

Six corruption controls and the finite source-bound receipt are recorded in
[P111-VERIFIED.json](P111-VERIFIED.json). This rules out below-nine fitting or
broadcast compression for the selected label graph, but gives no lower bound
on its complete paid supplier cost and no new native circuit.

## Short proof in characteristic two

Factor a normalized fitting block matrix as M_ij=U_i V_j with rank r,
where U_i is d-by-r and V_i is r-by-d. Then P_i=V_i U_i is a rank-d
idempotent. On a clique of R these idempotents mutually annihilate in both
orders. For each displayed eight-clique C, their sum S_C is therefore an
idempotent of rank 8d, and E_C=I_r-S_C has rank r-8d.

In characteristic two, summing the four equations for E_C cancels the four
identity matrices and all even incidences, leaving sum_C E_C=sum_T P_i.
The latter has rank 4d because T is a required-zero clique. Rank subadditivity
now gives

~~~text
4d <= 4(r-8d), so r >= 9d.
~~~

This argument applies to every characteristic-two field, finite or infinite,
and every positive d. It needs neither symmetry nor a Gram representation.
The finite checker verifies its clique/incidence inputs and exact coefficients;
the rank lemmas above are a human-readable proof, not a Lean formalization.

## Exact Petersen certificate and the all-field lower bound

[PETERSEN-LP-DUAL.json](PETERSEN-LP-DUAL.json) contains 113 rational terms in
functions F(S), indexed by all 1,024 subsets of the ten Petersen vertices.
[petersen_lp_verify.py](petersen_lp_verify.py) reconstructs each term from its
kind and vertex/subset indices; it never trusts a stored coefficient row.
It checks the exact identity

~~~text
F(empty)-5 = sum_t multiplier_t * expression_t(F).
~~~

There are 15 slope inequalities, 36 elementary submodular inequalities,
61 decoding equalities and one normalization equality. The allowed expressions
are

~~~text
monotone:   F(S+i)-F(S) >= 0
slope:      F(S)+1-F(S+i) >= 0
submodular: F(S+i)+F(S+j)-F(S)-F(S+i+j) >= 0
decode:     F(S+i)-F(S) = 0, when every neighbor of i lies in S
normalize:  F(V)-10 = 0
~~~

Added vertices must be absent from S, and i and j distinct. Inequality
multipliers are positive; equality multipliers may have either sign. Exact
Fraction arithmetic confirms coefficient one at F(empty), zero at the other
1,023 variables, and constant -5. Thus every function satisfying these
constraints has F(empty)>=5. Floating-point LP was used only to propose the
certificate; verification has no optimizer or third-party dependency.

To apply this over an arbitrary field, let Q be a normalized Petersen-fitting
block matrix and W its row space inside the 10d-dimensional coordinate space.
Write E_i for coordinate block i and set

~~~text
F(S) = dim(W + sum_(i in S) E_i) / d.
~~~

Dimension is monotone and submodular and each coordinate block raises it by
at most d. Normalization gives F(V)=10. The d rows belonging to receiver i
have identity in block i and zeros outside i and its neighbors. Hence
E_i is contained in W+sum_(j in N(i)) E_j, proving the decoding equalities.
The certificate gives rank(Q)>=5d, including over infinite fields.

The principal submatrix on the displayed 14 vertices is block diagonal
I_(4d) plus such a Q. Its rank is at least 9d, so the full matrix also has
rank at least 9d. A perfect matching of Petersen gives five independent
pair-sum rows over every field; adding the four isolated coordinates shows
that the 14-vertex graph has exact minimum block rank 9d over every field.
For the full 112-vertex graph, only the characteristic-two upper bound is
provided here.

## Nonlinear zero-error binary broadcast

Fix the 98 outside messages to arbitrary constants. In the induced 14-vertex
problem the four isolated messages Z have no side information, so Z is a
function of the broadcast B. Take all remaining messages independent and
uniform d-bit strings. Then

~~~text
H(B) = H(Z)+H(B|Z) = 4d+H(B|Z).
~~~

For each fixed z, set F(S)=H(B,X_S | Z=z)/d on the ten Petersen messages.
Entropy is monotone and submodular, each message adds at most d bits,
deterministic encoding gives F(V)=10, and zero-error decoding gives the listed
equalities. The exact certificate forces H(B|Z=z)>=5d. Thus H(B)>=9d,
and a fixed-length broadcast requires at least 9d bits. Fixing the outside
messages cannot increase the available broadcast length, so this is also a
lower bound for the full graph.

The same lower-bound argument works for independent uniform messages in any
finite alphabet, after normalizing entropy by their log cardinality. The
matching upper bound for the full graph asserted here is specifically binary.
No zero-error nonlinear binary block code of any block length beats nine.

## Known upper construction

Let b_i be the retained binary label in F_2^9. The checker verifies all
12,544 entries of

~~~text
b_i dot b_j = 1 + (root_i dot root_j)/2  (mod 2),
~~~

including odd diagonal entries and all required zeros. The resulting fitting
matrix has rank nine, as does its restriction to the 14 vertices. Tensoring
with I_d gives rank 9d over every characteristic-two field.

For a broadcast code transmit s=sum_j b_j x_j, with nine bitwise coordinates.
Receiver i computes b_i dot s. Its own coefficient is one; every other
nonzero coefficient is on a neighbor in G and can be subtracted using the
known message. This gives 9d broadcast bits for every positive d. Together
with the preceding lower bound it proves exactness at each block length,
not just an asymptotic infimum.

## Reproduce and coverage

From the repository root, with Python 3.12 and no external dependencies:

~~~sh
python3.12 scripts/research_package.py --package research/p112-characteristic-two-minrank --check-only
python3.12 scripts/research_package.py --package research/p112-characteristic-two-minrank
~~~

The registered replay runs all three verifiers with -I -B -O. Explicit exceptions
keep acceptance checks active with assertions disabled. The deterministic
receipts are [VERIFIED.json](VERIFIED.json) and
[PETERSEN-VERIFIED.json](PETERSEN-VERIFIED.json), and
[P111-VERIFIED.json](P111-VERIFIED.json).

The graph verifier imports no producer, search program or other verifier.
It checks the source hash and indexing, all 2,912 required-zero pairs, all
12,544 Gram entries, the four-clique certificate, the exact graph isomorphism
and rank-nine upper bounds. Ten corruption controls must be rejected.
The separate dual verifier checks all 1,024 rational coefficient sums and
rejects five corruptions, including a negative inequality multiplier and
an invalid decoding condition. Its perfect-matching positive fixture checks
all 21,760 elementary inequalities and all 640 decoding equalities.
The P111 checker independently checks its new input and reflected embedding,
the full binary Gram matrix, and six further corruption controls.

The reductions from rank and entropy to these finite certificates are the
proofs above. No formal proof assistant, full supplier replay or selected
frontier replay is claimed.

## Overlap, relevance and attribution

[Discussion 1713](https://github.com/CrocSwap/integer-mult-bounds/discussions/1713)
records the scoped result. The complete remote overlap refresh on
2026-10-14 at 10:16 UTC covered 460 open PRs and 435 Discussions, including
comments and replies. Sparse-checkout local coverage was limited.
[PR1471](https://github.com/CrocSwap/integer-mult-bounds/pull/1471), head
3695ad16e7bc4c0f6248a9e5a64fc069fa096733, audits odd-characteristic portability
of a particular P112 tensor proof. This package bounds every fitting matrix
and the corresponding binary broadcast problem. No priority claim is made.

Petersen's rate five is established in Anna Blasiak, Robert Kleinberg and
Eyal Lubetzky, [Index coding via linear programming](https://arxiv.org/abs/1004.1379),
Fact 5.6(1), printed page 28. The dual here is an exact replayable certificate
of that known result. The binary upper construction is also known: Debbie
Leung, Laura Mancinska, William Matthews, Maris Ozols and Aidan Roy,
[Entanglement can increase asymptotic rates of zero-error classical communication over classical channels](https://arxiv.org/abs/1009.1195),
Theorem 9 and section 4, explain the symplectic construction and E8 embedding,
crediting Peeters for the symplectic-graph result. The contribution here is
the pinned P112 and selected P111 embeddings, the four-clique certificate, and independent exact
checks of the resulting scoped obstructions; no literature-wide novelty claim
for the underlying parameters is asserted.

The input is retained from icekylinx's
[direct-delivery504-global](../direct-delivery504-global/README.md) package,
prepared with OpenAI GPT-6 Astra assistance. Its Hamming/root inputs descend
from the PR523/514/507/425/433 lineage credited in that package's
[NOTICE.md](../direct-delivery504-global/NOTICE.md). Inputs are referenced
without modification or re-vendoring.

The selected P111 input is the unchanged PR589 tuned word, built on eumemic's
PR555 word and the PR543/545 lineage, with substantial Anthropic Claude assistance credited in
[e8-bit-p111-tuned](../e8-bit-p111-tuned/README.md). Its native construction is
used only as a source of the exact live root labels here; its authors retain
credit for the word and its supplier results.

Prepared for Thiago with substantial OpenAI GPT-6 Astra and Codex assistance
for exploration, proof review, independent checking and packaging. New work
is Apache-2.0; retained source attribution and licenses remain applicable.

## Open next questions

Can a changed port graph or a native word that changes the fitting/broadcast
constraints improve a complete paid supplier budget? Merely using larger
blocks, asymmetric labels, extension fields, or nonlinear binary encoding
cannot lower this fixed graph's bound below nine. A useful first step is to
state the changed constraints and a complete optimistic paid budget before
building a circuit. Missing native words, restoration/phase proofs and global
owner invoices remain the blockers. [TASK.json](TASK.json) explicitly labels
this package as a side result of the helper-inventory investigation.
