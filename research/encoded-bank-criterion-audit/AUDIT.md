# Independent proof audit of PR2872

DLamdata with substantial OpenAI Codex assistance, including a separate
verifier agent. Apache-2.0.

Audited commit: `cc5c2398505447a321fb9f9826163825e3b269fd`.
[Original proof](https://github.com/tekuuu/integer-mult-bounds/blob/cc5c2398505447a321fb9f9826163825e3b269fd/research/encoded-phase-bank/PROOF.md),
SHA256 `154cf967411b93da3a5c56c84c4f8a62f62192448c14c08e510e830054897bf9`.
The lead authenticated the frozen tree against Git; the verifier agent derived
these arguments from the model statement before opening the source proof,
then compared them. Both share the stated contract. This is a separate AI
review, not an independent human review or formal-kernel verification.

**Verdict:** no substantive gap found in Theorem 1, Lemma 2, Theorem 3,
Lemma 4 or Corollary 5 under the stated contract. All mathematical claims
remain credited to Tekalign and the predecessors named in the source.
No new supplier, native cost result or exponent improvement is claimed.

## Derivation before source inspection

Write `epsilon_j=(-1)^(u_j dot v_j)` and `P_j=B_j(v_j)A_j(u_j)`.
Homomorphisms from a binary vector group give involutions, identity at zero,
and commuting generators within each A or B family.

### 1. Exact paired-word criterion

Setting every other label to zero leaves `P_j^2=epsilon_j I`.
Since A and B are involutions, this is equivalent to
`A_j(u)B_j(v)=epsilon_j B_j(v)A_j(u)`. Thus the within-column
Weyl relation is necessary for every u and v.

If the occurrences of i and j alternate, isolate one A or B label
generator in each column and set all other labels to zero. The desired
phase is one, and the two surviving operators S,T are involutions. The
endpoint is `(ST)^2=I` or `(TS)^2=I`, according to multiplication convention.
Either equation is equivalent to ST=TS. The four choices A/A, A/B, B/A,
B/B therefore force all four crossing commutations. Generator commutation
extends to the full homomorphic families. This uses independence of labels;
a cancellation among correlated labels could not justify the same step.

Conversely, among the pairs remaining in the word choose one with the
shortest distance between its two occurrences. Its interior contains no
complete pair, since such a pair would have smaller distance. Each interior
symbol has its other occurrence outside, so it alternates with the chosen
pair and its P commutes with the chosen P. Move the chosen P through this
interior, replace its square by epsilon, and delete the pair. The relative
order of every other pair is unchanged; hence every crossing in the reduced
word was already a crossing. Induction yields the product of all epsilon_j.
This does not impose commutation on nested or disjoint columns.

This derivation establishes the exact criterion for arbitrary invertible
complex matrices, not just signed permutations, Paulis, or unitary matrices.
Reversing matrix multiplication to account for chronological action changes
none of the conclusions.

### 2. Producer-prefix dimensions

Define a partial order by `i < j` in the natural producer order and i
preceding j in the consumer permutation. Crossings are precisely comparable
pairs, and cliques are increasing subsequences.

For a clique with total rank R, collect all its binary-coordinate A and B
generators as Z_a and X_a. All Z's commute; each satisfies `Z_a^2=I`.
Over C these generators are diagonalizable because their minimal polynomials
divide `(t-1)(t+1)`, which has distinct roots. Commuting diagonalizable
operators have a simultaneous eigenspace decomposition
`V = direct_sum_s V_s` for s in `F2^R`. No normality or inner-product
argument is needed. X_a is invertible and sends V_s bijectively to
V_(s+e_a), because it anticommutes with Z_a and commutes with the other
Z's. These translations act transitively on the indices. At least one
eigenspace is nonzero, so all 2^R eigenspaces have equal positive dimension.
Consequently `2^R | d`. A maximum-weight chain gives `2^W | d`.

For the upper bound, process columns in consumer order. Set the start of
column j to the largest endpoint of an earlier smaller column, or zero;
give j the next r_j integer slots. Its endpoint is the maximum weight of
an increasing subsequence ending at j. Thus no slot exceeds W-1, and
comparable columns receive disjoint slots. On W binary coordinates,
use the standard Z/X pair at these slots for A_j/B_j. Each column has
the right dot-product relation and crossing columns commute, so the paired
word criterion applies. The dimension is `2^W`. Taking a direct sum of
any positive number of identical representations realizes every positive
multiple of `2^W`.

Zero ranks cause no difficulty: their label groups and slot intervals are
empty, and they contribute zero to every clique weight. In the eigenspace
proof R=0 gives one eigenspace and the vacuous divisibility `1 | d`.
If every rank is zero, all operators are identities and every d>=1 works.
The nonempty-bank requirement is essential to the step that some eigenspace
is nonzero.

### 3. The C5 minimum

The occurrence positions of the word `0 1 4 0 3 4 2 3 1 2` are:

| Column | Positions (zero based) |
| --- | --- |
| 0 | 0, 3 |
| 1 | 1, 8 |
| 2 | 6, 9 |
| 3 | 4, 7 |
| 4 | 2, 5 |

The alternating pairs are exactly `01,12,23,34,40`. Each scalar column
generates an algebra isomorphic to M2(C). To see this without a unitary
assumption, diagonalize its A; B bijects its plus and minus eigenspaces.
Choose a basis in the plus eigenspace and use its B image in the minus
eigenspace. Then A is `diag(I,-I)` and B swaps the two blocks. The generated
algebra is `M2 tensor I_m` and its commutant is `I_2 tensor M_m`, with
`d=2m`.

An edge already forces `4 | d`. At d=4, the algebra of column 0 and the
commuting algebra of its neighbor 1 are complementary copies of M2. Each
has a four-dimensional commutant. Column 2 commutes with column 1; its
four-dimensional algebra is contained in that commutant and must equal
column 0's algebra. Similarly column 4's algebra equals column 1's.
Column 3 commutes with both 2 and 4, so its algebra would be in the common
commutant of the two complementary M2's, namely the scalars. That contradicts
its anticommuting involution pair. Thus d=4 is impossible. Together with
`4 | d`, this leaves d>=8. Assigning the coordinate colors `(0,1,0,1,2)`
to columns gives an explicit d=8 representation.

This proves the stated minimum. It does not assert that every possible
larger dimension is a multiple of eight, or that clique/coloring formulas
classify every paired schedule.

## Comparison with the frozen proof and existing checks

The frozen proof agrees with each derivation above. Its sparse-label
necessity is sufficient because the labels are independent. Its shortest
interval argument remains valid after deletions. Its simultaneous
diagonalization needs no omitted unitary assumption. Its d=4 commutant
inclusion becomes equality because both spaces have dimension four; the
displayed block form also proves the double-commutant identity it uses.
The proof's stronger odd-cycle statement follows by repeatedly alternating
an algebra with its commutant along a path.

Existing `verify.py` already tests Pauli phase polynomials, weighted
permutations including ranks zero, and the two-qubit symplectic-plane
commutant graph. Existing `independent.py` already tests exact dense
nonunitary endpoint fixtures. Existing `test_package.py` already isolates
all four crossing relations. Repeating those checks would not create a
new independent mathematical implication, and this subtask did not rerun
the existing suite.

The source package’s `verify.py` rejects an empty schedule. The proof's mathematical
extension to zero columns is trivial with W=0, but executable coverage should
not be described as including f=0. This is a scope observation, not a defect
in the claims reviewed here.

## Additional exact witness

`commutant.py` is a new, standalone Fraction/RREF computation. It
imports no candidate or predecessor implementation. Starting with two local
M2 factors on C4, it conjugates them by an explicit nonorthogonal rational
basis change and solves unrestricted matrix equations `MG-GM=0` in all
16 unknown entries. The check verifies a nonunitary generator, both
four-dimensional algebras, their four-dimensional complementary commutants,
the double commutant, a one-dimensional common commutant, and the full
16-dimensional joint algebra. This directly checks the exact linear-algebra
step behind the d=4 obstruction in a nonunitary fixture; the existing
symplectic-plane census does not perform this unrestricted centralizer solve.

The result is `PASS_EXACT_NONUNITARY_D4_COMMUTANT` in
`COMMUTANT.json`. Boundary controls verify that dropping B leaves
an eight-dimensional centralizer, dropping the second neighboring algebra
leaves a four-dimensional one, and changing a single pair's multiplicity
to three in C6 gives a nine-dimensional centralizer. The last control
guards against generalizing the d=4 equal-dimension step to other d; it
does not claim a valid d=6 crossing-edge representation.

This finite rational witness is corroboration, not an exhaustive check of
complex representations. Universal validity rests on the derivation above.
