# Exact bank representation theorem

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
All statements below use the contract in section 1, not an arbitrary supplier.
This is a written mathematical proof, not a proof-assistant formalization.

## 1. Contract

Let `V=C^d`, d>=1. For j=0,...,f-1 choose r_j>=0 and homomorphisms
`A_j,B_j : (F2^r_j,+) -> GL(V)`. Put `P_j(u,v)=B_j(v)A_j(u)`.
A chronological occurrence executes A then B. All u_j,v_j are independent,
fixed throughout the word. A paired word w contains each j exactly twice,
using the identical P_j at both occurrences. Its desired endpoint is

    product_chronological(w) = (-1)^(sum_j u_j dot v_j) I_d.      (1)

Equality is on every vector of V, not just a prepared or encoded subspace.
No additional bank operation is omitted. Correlations with the data are
allowed: equality on every label fibre and every bank vector extends linearly.

A and B map zero to identity. Their generators within a family commute and
square to I. No commutation between different columns, common coordinate
basis, tensor decomposition, unitarity or irreducibility is assumed.

Let G_w have edge ij exactly when their occurrences alternate (`i j i j`
or `j i j i`). Disjoint and nested pairs have no edge.

## 2. Exact crossing criterion

**Theorem 1.** Equation (1) holds if and only if:

(a) `A_j(u)B_j(v)=(-1)^(u dot v) B_j(v)A_j(u)` for each j,u,v;

(b) across each edge ij, every A_i commutes with every A_j and B_j,
and every B_i commutes with every A_j and B_j.

**Necessity.** Set all labels outside j to zero. Equation (1) becomes
`(B_j(v)A_j(u))^2=(-1)^(u dot v) I`. Multiplying by the involutions
A_j(u), B_j(v) gives (a).

For an edge ij, isolate one label generator in each column, selecting only
u or only v for that column and setting all other labels zero. The desired
phase is +1. The alternating subword consists of two involutions S,T and
equals I exactly when `(ST)^2=I`, equivalently `ST=TS`. Choosing A/A, A/B,
B/A and B/B proves (b) on generators, hence on all group elements.

**Sufficiency.** Choose a shortest interval between equal symbols in the
current paired word. Its interior contains no complete pair. Every interior
symbol thus has its other occurrence outside that interval and crosses the
chosen symbol. By (b) their P operators commute. Slide the two equal symbols
together and use (a) to replace their product by its scalar phase. Delete
them. Crossings among all other columns are unchanged. Induction to the empty
word gives precisely the product of the self phases in (1). In particular,
nested columns need not commute. This argument uses arbitrary matrices,
not a Pauli formula or a numerical census. QED.

## 3. Clique dimension

**Lemma 2.** For any crossing clique C, `2^(sum_{j in C} r_j)` divides d.

Let R=sum r_j on C. Theorem 1 gives R pairs of involutions Z_a,X_a with
commuting Z generators, commuting X generators, and
`Z_a X_b=(-1)^[a=b] X_b Z_a`. Commuting involutions over C simultaneously
diagonalize. Write `V=direct_sum_{s in F2^R} V_s`, where the Z eigenvalues
are `(-1)^s`. X_a maps V_s bijectively to V_(s+e_a). All 2^R eigenspaces
have the same dimension. At least one is nonzero, since V is nonzero, so
all are nonzero. Their direct sum gives divisibility. QED.

This is the standard exact finite-Heisenberg/eigenspace argument. PR2850
uses it for closed separable commutators; Theorem 1 supplies the missing
reason it applies to these crossing columns in an open schedule.

## 4. Weighted producer-prefix optimum

**Theorem 3.** Let `w=(0,...,f-1,pi[0],...,pi[f-1])`. Let W be the largest
sum of r_j along an increasing subsequence of pi. A representation satisfying
(1) exists in dimension d if and only if `2^W` divides d. In particular the
minimum is `2^W`. If every r_j=0, W=0 and identity maps work in every d.

Two columns cross exactly when their relative order in pi agrees with their
natural order. Thus cliques are increasing subsequences. A maximum-weight
one and Lemma 2 give necessity.

For sufficiency, scan pi. For current j define

    s_j=max({e_i: i already scanned and i<j} union {0}),
    e_j=s_j+r_j,       I_j={s_j,...,e_j-1}.

Induction identifies e_j as the maximum weight of an increasing subsequence
ending at j, so max_j e_j=W. If i<j cross, e_i<=s_j: their coordinate
intervals are disjoint. On W binary bank coordinates, let A_j be the Z action
with u_j on I_j and B_j the X translation with v_j on I_j. Each block has
its dot-product commutator, and crossing blocks act on disjoint coordinates.
Theorem 1 proves the endpoint. This gives dimension 2^W. Tensoring every
operator with identity on an arbitrary multiplicity space gives every
positive multiple of 2^W. QED.

Example: pi=(2,0,1), r=(1,2,1). The intervals for columns 0,1,2 are
(0), (1,2), (0), so W=3 and minimum d=8. The ordinary LIS length is two;
using it instead of the weighted chain would incorrectly predict d=4.
For reversal W=max r_j. For identical producer and consumer order W=sum r_j.

The unit-weight coordinate construction and LIS value are due here to
PR2859. The new scope is the necessity for arbitrary GL(V) encodings and
vector-label blocks; the weighted-poset argument itself is standard.

## 5. Interleaving: an odd-cycle obstruction beyond cliques

For scalar labels, write `A_j=A_j(1)`, `B_j=B_j(1)`.
An anticommuting involution pair has a basis in which

    A=diag(I,-I),       B=[[0,I],[I,0]].

Indeed B identifies A's two eigenspaces bijectively; choose bases using that
identification. The generated unital algebra is `M_2(C) tensor I_(d/2)`.
Its commutant is `I_2 tensor M_(d/2)(C)` (the block equations with A and B
force exactly these matrices).

**Lemma 4.** A scalar-column crossing graph with an odd cycle has no valid
dimension-four representation.

At d=4, the algebra generated by each pair has dimension four and so does its
commutant. By Theorem 1, the algebra of a neighboring column lies in that
commutant. It too is four-dimensional, hence equals the commutant. Along any
path the algebras alternate between one algebra and its commutant; the
commutant of the commutant is the original algebra in the displayed basis.
An odd cycle forces the original algebra to equal its commutant. It would
then commute with itself, contradicting its isomorphism with noncommutative
M_2(C). QED. This uses no unitary or Pauli-basis assumption.

**Corollary 5.** The scalar paired word

    0 1 4 0 3 4 2 3 1 2

has minimum bank dimension eight. Its edges are `01,12,23,34,40`, so its
maximum clique has size two. Lemma 2 requires 4|d, and Lemma 4 excludes d=4.
Assigning bank coordinates `(0,1,0,1,2)` to columns 0,...,4 gives disjoint
coordinates on every edge. Theorem 1 supplies a dimension-eight construction.
There is no claim here that every larger allowable d is divisible by eight,
or that a clique or coloring formula solves all paired schedules.

## 6. Scope controls and supplier consequence

If P_j may depend jointly on u and v, the one-dimensional scalar
`P_j(u,v)=i^(u dot v)` squares to the correct phase; all columns commute.
Every paired schedule then works at d=1. Thus omitting label separation
would make Theorem 3 false. This scalar primitive already computes the
quadratic phase; pricing and realizing it is the original missing task.

The fixed-label, repeated-word, full-state premises are also explicit.
Nothing here allows ignoring arbitrary bank lanes, changing the second
occurrence, or adding free cross-label operations. The bound counts bank
lanes, not coefficient bits, tape moves, recursive rank, or total child cost.
An attained abstract representation is not a supplier admission. All
encoding, A/B execution, physical movement, coefficient precision, callers,
restoration and outer inequalities remain separately payable.

The exact finite checks in RESULT.json and MATRICES.json test identities,
constructions and counterexamples. The proofs above, rather than those
bounded censuses, justify the universal statements. No formal-kernel proof
or independent human review is claimed.
