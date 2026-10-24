# Exact dirty-fanout tariffs over unital rings

This contribution is produced by Nick Petalas. Apache-2.0.

**Scoped proof with exact finite corroboration; no new kappa.** Ross
Richardson's [PR3121](https://github.com/CrocSwap/integer-mult-bounds/pull/3121)
proves the stationary directed-tariff optimum for a common XOR value. Here
the same optimum holds over every nonzero unital ring, including
noncommutative rings, with different unit target coefficients. The new
step is a free-module dirt-cut argument and an ordered coefficient ratio.
The predecessor's binary result and graph optimization are credited methods,
rather than new results or replay deliverables.

## Contract and result

Let R be any ring with 1 != 0. There are exactly q >= 1 dirty rows, initially
arbitrary independent a_i in R^w, w >= 1. A preserved disjoint source supplies
arbitrary p in R^w. Multiplication of coefficients is on the left. A fixed
finite straight-line word may use

```text
ADD(i,j,alpha): A_i <- A_i + alpha A_j, i != j, alpha in R,
P(i,beta):     A_i <- A_i + beta p, beta in R.
```

Every ADD on j -> i costs c_ij > 0 and every P at i costs mu_i > 0. These
are finite stationary complete prices, independent of the coefficient.
The endpoint must be A_i = a_i + lambda_i p for specified two-sided units
lambda_i in R. All q rows are required outputs. There are no other helpers,
free basis changes, CLEAR, COPY, adaptive control or intermediate observers.
The word must work for all entry dirt and all p. Scalar applications and
their inverses must already be included in the declared complete tariffs.

The exact optimum over all allowed words, including arbitrary interleavings,
repeated calls and nonunit gate coefficients, is

```text
min over directed rooted spanning forests F:
    sum_(roots i) mu_i + 2 sum_(arcs j -> i in F) c_ij.
```

Thus unequal unit demands, zero divisors and noncommutativity do not add a
source insertion or edge occurrence under this coefficient-independent
contract. Over a field this covers every list of nonzero scalar demands.
A separately required inverse has the same tariff and must be paid again.

## Proof

Project each row onto its q entry-dirt symbols. Its coefficient matrix M
starts at I_q. An ADD left-multiplies M by I_q + alpha E_ij, with inverse
I_q - alpha E_ij. A source call leaves M unchanged. Therefore every prefix
matrix is invertible over R, and its rows form a free left-module basis of
R^q. This uses neither division nor a field rank argument. Equality of
coefficient matrices follows from the all-input contract by setting one
dirty symbol to 1 and the others and p to zero.

Let O be the set of rows receiving at least one source insertion. It is
nonempty. Fix a nonempty S disjoint from O. With no incoming ADD to S,
its p coefficients remain zero. This contradicts the nonzero target
coefficient on every row in S.

There also cannot be exactly one incoming ADD. Before that gate, internal
ADDs preserve the S-row module W_S = span_R{e_i : i in S}; outgoing ADDs
leave S unchanged. Suppose the sole incoming gate is j -> i with coefficient
alpha. If alpha = 0, it cannot deliver p, as in the zero-incoming case.
Otherwise its source row m_j belongs to the full free basis and is outside
the S subset of that basis. In that basis, alpha m_j has coefficient alpha
on m_j, so it cannot belong to W_S, even if alpha is a zero divisor.
Replacing m_i by m_i + alpha m_j therefore changes the S-row module.
All subsequent internal ADDs preserve the changed module and outgoing
gates leave it unchanged. The final dirt matrix I_q would restore W_S,
which is impossible. Every such S needs at least two incoming occurrences.

Apply Edmonds' finite prescribed-root disjoint-branching theorem to the
directed ADD occurrence multigraph, with two identical root sets O. Its
cut condition is exactly the preceding statement for S disjoint from O;
for S meeting O it asks for zero incoming arcs. It supplies two
occurrence-disjoint spanning forests rooted at O. If f(O) is the cheapest
such forest, the ADD bill is at least 2 f(O). Every row in O costs at least
one source insertion, proving the claimed lower bound. Parallel occurrences
count separately. This external graph theorem is the same dependency used
by PR3121; no new graph-theorem proof or formal-kernel verification is claimed.
Its precise finite statement is retained in the pinned
[predecessor proof](../dirty-anchor-edge-tariffs/PROOF.md#lemma-2-cuts-force-two-paid-directed-forests).

For attainment choose a forest and set

```text
r_ij = lambda_i lambda_j^(-1), for each parent arc j -> i.
```

In children-before-parents order, subtract r_ij A_j from A_i. Each parent
still contains its original dirt when used, so the prepared nonroot row is
a_i - r_ij a_j. Insert lambda_i p at each root. Undo preparation in literal
reverse order, adding r_ij times the restored parent. Induction gives

```text
(a_i - r_ij a_j) + r_ij (a_j + lambda_j p)
    = a_i + lambda_i p.
```

The order lambda_i lambda_j^(-1) is essential. Every edge costs twice and
every root once. Negating coefficients and reversing the entire word gives
its inverse, with the same prices. Minimizing over forests proves equality.

## Finite evidence and boundaries

The first working example is a three-row chain over Z/4 with demands
(3,1,3). Five paid gates realize the endpoint for arbitrary entry dirt.
The verifier evaluates symbolic ring coefficients, so each checked word
covers every payload width and every value of its independent input symbols
in that ring. This does not turn the finite word census into the universal
proof above.

The fixed checks enumerate every rooted forest on q = 1,...,5. For each
forest they test cyclic shifts of the ordered unit list as demands, with
both the forward map and its literal inverse. There are 2,882 words per
ring Z/3, Z/4 and Z/6, and 8,646 over M2(F2). These demand lists are declared
fixtures, not an exhaustive enumeration of all heterogeneous unit lists.

A separately implemented modular affine-state search permits every nonzero
ADD and insertion coefficient, arbitrary order and arbitrary multiplicity.
It exhausts 48 two-row tariff instances over Z/3, Z/4 and Z/6, with all four
prices in {1,4}. It checks all four unit-demand pairs per instance, 192
comparisons total, visiting 98,688 states across the instances. This search
does not assume a forest form. Its arithmetic uses direct modular integers,
independently of the ring-table word interpreter.

Five boundary groups check reversed noncommutative coefficient order,
missing dirt restoration, the nonunit-demand boundary, nonunit rejection
by the constructor, and cyclic parent rejection. The nonunit boundary is
an exact finite counterexample to dropping the unit hypothesis. Over Z/4,
with demands (2,1), mu = (1,9) and both directed ADD prices 1, unrestricted
shortest paths give optimum 4; the unit formula would give 3. The word

```text
A_1 -= A_0; P(0,1); A_1 += A_0; P(0,1)
```

attains 4. No all-ring nonunit-demand formula is claimed. In M2(F2), encoded
row-major matrices 6 and 7 give correct ratio 11 and reversed ratio 13.
The latter fails the required arbitrary-dirt endpoint.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py \
  --package research/unit-ring-dirty-fanout
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B \
  research/unit-ring-dirty-fanout/verify.py
```

Expected marker: PASS_UNIT_RING_DIRTY_FANOUT. The manifest runs normal and
optimized warning-strict checks. RESULT.json is generated by the verifier
and binds the proof, metadata and verifier hashes. Normal checking writes
nothing. `--output PATH` creates an absent external receipt and refuses to
overwrite an existing file. Provenance documents are pinned historical
references; no predecessor executable or network access is needed by the
direct scientific checker. Package metadata checks require Git history.

## Scope and credit

Credit Ross Richardson #3121 and #3063 for the XOR tariff, dirt-cut method
and destination-only boundary; Cinna Davis #1944 for dirty-output anchors
and #1968 for separate several-term accumulation; Anthony #774 and Oscar
Fennell #759 for forest compensation and their retained synthesis lineage.
Tekalign #3130 supplies the direct cut-certificate and classical optimizer
application. Edmonds supplies disjoint branching. These results are cited,
not rechecked deliverables. Exact retained document pins and predecessor
heads are in SOURCES.json and TASK.json. No priority for forest synthesis
or general graph optimization is claimed.

This is an algebraic interface extension. Complete tariffs must include
coefficient application, source access, routing, frames, precision, scratch
cleanup and physical head return when applicable. No actual caller,
physical supplier, all-size tape realization, complete moment invoice or
selected-frontier change is supplied. The selected kappa stays 0.00302015.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

The nonunit-demand optimum and a physical caller with coefficient-independent
complete prices remain open. Start with the displayed Z/4 demand and a
declared price matrix for the first; start with one actual caller's full
bill for the second. The unit-ratio obstruction and the absent physical
tariffs are the respective blockers. TASK.json records the concrete first
steps and relevance. Stop this construction round at the proved extension.

## Engineering constraints

Power-of-Ten rule 3 has a managed-runtime deviation: Python exact objects,
heaps and JSON allocate dynamically. Ring size is at most 16; word tests
have at most five rows and nine gates; forest enumeration has at most
5^5 candidate parent functions. A two-row modular search stores at most
6^6 states, with at most 20 outgoing gates per state. Its heap-pop bound
is 1 + 20*6^6, and successful relaxation bounds heap pushes by the same
quantity. There is no recursion, service, background process or dynamic
code evaluation. Standard-library allocation internals are not audited.
The verifier's standard-library dataclass and argparse dispatch have fixed
targets. A larger ring, row count or external input format must add new
explicit capacity and arithmetic limits before expanding these bounds.
