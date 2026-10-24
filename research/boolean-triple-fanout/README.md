# Exact tariffs for an incomparable Boolean demand triple

**Scoped written proof with exact finite corroboration; no new kappa.**
For three arbitrary dirty rows, the demand `((1,1,0),(1,0,1),(0,1,1))`
over `F_2^3` has an exact **twenty-two-term** optimum for every positive
source-insertion price and every positive destination-row ADD price.
All twenty-two aggregate count vectors are attained and indispensable.

This settles Open next question 1 of lee-phys's
[PR #5259](https://github.com/CrocSwap/integer-mult-bounds/pull/5259),
at `d2a7d88f011ca9c520333da8d4e03f1f22d23e91`. Its nineteen-term theorem
requires a nonprincipal demand ideal and does not apply here. The new step
is the exact one-insertion branch, whose three count vectors complete the
frontier. Ali Romman's
[Discussion #5266](https://github.com/CrocSwap/integer-mult-bounds/discussions/5266)
already proves one-insertion feasibility for principal ideals over finite
commutative rings with any number of rows; it does not price the shortest
restoring word. Both predecessors retain credit. The argument below is
self-contained and extends to arbitrary Boolean rings under stated hypotheses.

## Contract and optimum

Let R be a commutative unital Boolean ring, `1 != 0`: every element x satisfies
`x^2=x`. In particular `2x=0`, by expanding `(x+1)^2=x+1`. Exactly three
independent arbitrary dirty rows `a_0,a_1,a_2 in R^w`, w >= 1, and a disjoint
preserved source `p in R^w` are available. A fixed finite word must produce

    A_i = a_i + lambda_i p,  i=0,1,2,

for all input values. The only operations are

    P_i(beta):   A_i <- A_i + beta p,       price mu_i > 0;
    E_ij(alpha): A_i <- A_i + alpha A_j,    price c_i > 0, i != j.

All coefficients and directed row pairs are available. Prices are finite,
stationary, coefficient-independent complete abstract prices; all ADDs into
a given row have the same price. Every original dirt column must return.
There are no extra rows, clearing, observations, adaptive choices or free
basis changes. Any separate inverse execution is charged separately.
Positive prices allow zero-coefficient gates to be deleted.

**Theorem.** Suppose the three demands sum to zero and their principal ideals
are pairwise incomparable; equivalently,

    lambda_0 + lambda_1 + lambda_2 = 0,
    lambda_i not in (lambda_j) for every i != j.

For distinct i,j,k, define

    D   = mu_0 + mu_1 + mu_2,
    T_i = 2mu_i + 2c_j + 2c_k,
    B_k = mu_i + mu_j + 2c_k
          + min(mu_i,mu_j,2c_i,2c_j,2c_k),
    U_i = mu_i + 2(c_0+c_1+c_2).

The exact optimum over all allowed finite words is

    OPT = min(D,T_0,T_1,T_2,B_0,B_1,B_2,U_0,U_1,U_2).

Expanding the inner minima gives twenty-two linear terms. The value and an
attaining word can be selected with a constant number of comparisons once
the prices and algebraic hypotheses are given. This does not price testing
those hypotheses or physically implementing the gates.

For the requested `F_2^3` example, encode `(x_0,x_1,x_2)` as
`x_0+2x_1+4x_2`. Addition is XOR, multiplication is AND, identity is 7,
and the demand is `(3,5,6)`. The theorem applies because the three supports
have size two and none contains another. At mu=(10,100,100), c=(1,1,1),
the exact optimum is **16**, attaining the previous upper bound; excluding
the new U terms would incorrectly give 24.
The one-insertion witness for this example was already displayed in #5259.
Its sharp lower bound and the full price envelope are the new conclusions.

If every mu_i=mu and every c_i=c, the formula simplifies to

    OPT = min(3mu, mu+6c).

Indeed the B terms are at least `min(3mu,2mu+4c)`. For mu<=3c,
`2mu+4c>=3mu`; for mu>=3c, `2mu+4c>=mu+6c`. Thus three direct
insertions are optimal below the transition mu=3c, and one insertion with
six ADDs is optimal above it; both attain the value at equality.

## Boolean support algebra

The hypotheses imply that every demand is nonzero. Define

    a = lambda_0 lambda_1,
    b = lambda_0 lambda_2,
    c = lambda_1 lambda_2.

Using `lambda_2=lambda_0+lambda_1` and idempotence gives

    lambda_0=a+b,  lambda_1=a+c,  lambda_2=b+c,
    ab=ac=bc=0.

For example `ab=lambda_0^2 lambda_1(lambda_0+lambda_1)=0`;
the other products follow by permuting indices. Each of a,b,c is nonzero:
if a=0 then `lambda_0=lambda_0 lambda_2` belongs to `(lambda_2)`,
contradicting incomparability, and the other cases are symmetric.
Conversely, three nonzero pairwise orthogonal idempotents a,b,c give a
triple of this form with incomparable principal ideals: multiplying a
proposed membership by the missing atom yields a nonzero atom equal to zero.

Set

    g = a+b+c = lambda_0+lambda_1+lambda_0 lambda_1.

Then `I=(lambda_0,lambda_1,lambda_2)=(g)`: g is a combination of the
lambda_i, and `g lambda_i=lambda_i`. No lambda_i generates I, since that
would contain every other demand. For every pair of distinct indices,

    h_i = g+lambda_i != 0,    h_i lambda_j = h_i.

These identities are the only special algebra needed for the one-insertion construction.
They also allow g to be a proper idempotent, not necessarily the ring identity.
Finiteness and a global decomposition of R into fields are unnecessary.

## Lower bound for arbitrary words

Write P_i for the number of nonzero insertions into row i and K_i for the
number of all incoming nonzero ADDs. Prefixes act on the three original dirt
columns by an invertible matrix M: an ADD has its negated-coefficient inverse,
and an insertion does not change M. The all-input requirement forces the
final dirt matrix to be the identity, as seen by testing each original input
column separately.

**Incoming-row return lemma.** No row receives exactly one nonzero ADD.
Before its only `E_ij(alpha)`, dirt row i is e_i. After it the row is
`e_i+alpha m_j`, with m_j row j of the invertible prefix M. No later
operation changes that dirt row, so restoration requires `alpha m_j=0`.
Multiplication by `M^-1` gives `alpha e_j=0`, hence alpha=0, a contradiction.
Thus any used destination has K_i>=2. In particular a nonzero-demand row
with no insertion must have K_i>=2. This is the credited incoming-row
argument of #3063/#4916/#5163, not a universal per-edge count.

**Exactly one insertion.** Suppose the word has only `P_i(beta)`.
Its final source column is `L(beta e_i)`, where L is the invertible suffix
matrix. Every demand is a multiple of beta, and `L^-1 lambda=beta e_i`
expresses beta as a combination of the demands. Consequently `(beta)=I`,
the ideal invariant from #5139, also used in #5266. In a Boolean ring a
principal ideal has a unique generator: from `(beta)=(g)` we get
`beta g=beta` and `beta g=g`, so beta=g.

Each row other than i has no insertion and needs at least two ADDs. If row
i had no incoming ADD, its final coefficient would be beta=g, whereas
lambda_i does not generate I. Therefore row i also receives ADDs, and the
return lemma makes their number at least two. Every such word componentwise
dominates the U_i count vector. Zero insertions cannot supply nonzero demand.

**At least two insertions.** The remaining classification is inherited from
#5259; it needs only zero sum and pairwise incomparable principal ideals,
not nonprincipality of I. We include it to avoid a dependency on that pending
proof. Let S be the set of rows receiving insertions.

* If S contains all rows, the counts dominate D.
* If `S={i}`, then P_i>=2 and K_j,K_k>=2, so they dominate T_i.
* Suppose `S={i,j}`. Row k has K_k>=2. If P_i>=2 or P_j>=2, the
  counts dominate the corresponding R vector in the table below.
  Otherwise P_i=P_j=1. If either insertion row receives an ADD, it receives
  at least two, giving an M vector. The remaining case has K_i=K_j=0.

In that remaining case, parent rows i,j retain independent fixed dirt a_i,a_j
throughout. Their sole insertion coefficients must be lambda_i,lambda_j.
If only one of the two parent edges into k were used, its final source
coefficient would lie in that parent's principal ideal, contrary to
incomparability. Both edges are therefore used. Restoration of the independent
a_i and a_j requires the sum of the coefficients on each respective edge
to vanish. Each used edge needs at least two nonzero calls, so K_k>=4;
these counts dominate Q_k. This per-edge argument is valid here because
the parent dirt rows never change.

The cases exhaust every word, including cancellations, feedback and arbitrary
interleavings. Every attainable aggregate count vector dominates one of the
twenty-two vectors below; hence every bill is at least the displayed optimum.

## Matching constructions and irredundancy

All words below are chronological. Let u=1_R, and let i,j,k be distinct.
Because R has characteristic two, each primitive is its own inverse.
The nonzero entries of `(P_0,P_1,P_2,K_0,K_1,K_2)` are listed here.

| Family | Price | Nonzero counts | Number |
|---|---|---|---|
| D | `sum mu_i` | all P_i=1 | 1 |
| T_i | `2mu_i+2c_j+2c_k` | P_i=2, K_j=K_k=2 | 3 |
| R_(i,j;k) | `2mu_i+mu_j+2c_k` | P_i=2, P_j=1, K_k=2 | 6 |
| M_(i,j;k) | `mu_i+mu_j+2c_i+2c_k` | P_i=P_j=1, K_i=K_k=2 | 6 |
| Q_k | `mu_i+mu_j+4c_k` | P_i=P_j=1, K_k=4 | 3 |
| U_i | `mu_i+2 sum c_r` | P_i=1, all K_r=2 | 3 |

The first five families use the predecessor's words:

    D:   P_0(lambda_0), P_1(lambda_1), P_2(lambda_2).

    T_i: E_ji(u), P_i(lambda_j), E_ji(u),
         E_ki(u), P_i(lambda_k), E_ki(u).

    R_(i,j;k): E_ki(u), P_i(lambda_k), E_ki(u),
               P_i(lambda_j), P_j(lambda_j).

    M_(i,j;k): E_ij(u), E_ki(u), P_i(lambda_k), P_j(lambda_j),
               E_ki(u), E_ij(u).

    Q_k: E_ki(u), E_kj(u), P_i(lambda_i), P_j(lambda_j),
         E_kj(u), E_ki(u).

An echo `E_ji(u),P_i(t),E_ji(u)` restores dirt and gives t to both rows'
source coefficients. This proves T and R using `lambda_i=lambda_j+lambda_k`.
For M, immediately before the last two gates the rows are

    A_i=a_i+a_j+lambda_k p,  A_j=a_j+lambda_j p,
    A_k=a_k+a_i+a_j.

Those gates restore dirt and leave demands lambda_i,lambda_j,lambda_k.
For Q the last two gates add `lambda_i+lambda_j=lambda_k` to k's source
coefficient and restore its dirt. D is immediate.

**U_i: one insertion, two ADDs per row.** Let C be the chronological suffix

    E_ji(lambda_j), E_ki(lambda_k), E_ij(h_i),   h_i=g+lambda_i.

It sends the source column g e_i successively to a column with entries
`g,lambda_j,lambda_k` on i,j,k, and then to lambda: its last update replaces
g by `g+h_i lambda_j=g+h_i=lambda_i`. Execute

    C^-1, P_i(g), C.

The first word has zero source column and changes only dirt. The suffix C
undoes that dirt change and transports the inserted column to lambda.
Each destination occurs once in C and once in its inverse. All coefficients
are nonzero, giving exactly the U_i counts. For the requested instance U_0 is

    E_01(4), E_20(6), E_10(5), P_0(7),
    E_10(5), E_20(6), E_01(4).

Thus every listed vector is attained. They are pairwise incomparable, so
the lower-bound classification makes them the exact Pareto frontier.
For the stronger assertion that every linear price term is indispensable,
the following strictly positive prices uniquely expose one member per family.
Permuting row labels exposes all members; direct substitution verifies each
strict inequality against the table, and the verifier checks all permutations.

| Unique minimum | Prices `(mu_0,mu_1,mu_2,c_0,c_1,c_2)` | Value |
|---|---|---|
| D | `(1,1,1,1,1,1)` | 3 |
| T_0 | `(1,3,3,1,1,1)` | 6 |
| R_(0,1;2) | `(1,2,5,1,2,1)` | 6 |
| M_(0,1;2) | `(3,5,10,1,3,2)` | 14 |
| Q_2 | `(3,3,5,2,2,1)` | 10 |
| U_0 | `(3,9,9,1,1,1)` | 9 |

## Bounded verification and limitations

The standard-library verifier checks every zero-sum incomparable ordered
triple over `F_2^n` for n=3,4,5, including proper demand ideals when n>3.
It checks all twenty-two constructors and inverses on every formal input
column, and all scalar input assignments for the requested eight-element
instance. Separate controls check the uniform-price corollary, strict exposure,
omitted dirt preparation, wrong Boolean identity, essential hypotheses and
the failure of a universal per-edge two-call bound.

An independent packed-state bidirectional Dijkstra implementation permits
all 63 nonzero primitive gates on the full three-row affine state. It tracks
all nine dirt coefficients and three source coefficients, with the correct
heterogeneous price for each destination and operation type. There is no
length cutoff, formula-derived pruning or restriction to the proposed words.
The sum of the two queue minima is a lower bound on an uncompleted shortest
path; search stops once it reaches the best meeting length. Positive rational
prices are scaled exactly to integers. Returned paths are replayed and charged
by the separate coordinate-arithmetic ring interpreter. The seven cases
cover the six exposed families and a rational price vector; they do not
enumerate the entire affine graph or prove an all-price theorem.

```sh
python3.12 -B scripts/research_package.py --package research/boolean-triple-fanout --check-only
python3.12 -B scripts/research_package.py --package research/boolean-triple-fanout
python3.12 -I -W error -B research/boolean-triple-fanout/verify.py
```

The recorded check covers 456 demands, 10,032 words, 80,256 formal
forward/inverse column checks and 180,224 literal input checks. All 22 vectors
are strictly exposed, eleven controls pass, and seven shortest-path queries
settle 314,361 states in total, counted separately per direction and query.
Their exact optima are 3, 6, 6, 14, 10, 9 and 79/30. Normal and optimized
outputs agree. Three disposable optimized-mode mutations reject an underpriced
U term, omitted one-insertion preparation and ignored heterogeneous prices.

The verifier writes no files and needs neither Git nor network. Normal and
optimized warning-strict commands are registered; submission checks are
recorded in the PR. The general Boolean-ring and arbitrary-real-price conclusions rest on
the written proof. Independent human review and proof-kernel acceptance are
unclaimed. Independently priced directed edges, extra helpers, restricted
coefficients and non-Boolean rings are outside this theorem. Physical source
access, coefficient production, routing, precision, stock and supplier admission
remain separate obligations; the selected frontier is unchanged.

## Sources and coordination

The scientific base is canonical main
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`, priority revision 7.
TASK.json retains the original `bit-helper-contract` card and records the
explicit donor assignment as a changed algebraic side-result scope. The
SOURCES.json Git pins refer to this main ancestor. Exact bibliographic pins
for pending #5259 document adapted arguments, words and verifier infrastructure;
its files are not runtime inputs, and no unmerged Git object is needed by replay.
All proof steps and executable code needed for this result are included here.

The preceding survey paginated 347 open PRs and 4,548 Discussion records
on 2026-10-23, followed by entry-time all-state fanout PR searches and live
board/#1166/#5030 checks at 16:29 UTC. #5266 settles insertion count only;
#5269 concerns matrix-ring feasibility. Neither supplies this tariff. No
same-tariff resolution or overlapping active claim appeared in the inspected
records. Sparse local notes, arbitrary historical diffs and unpublished work
remain coverage limits. The
[canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5030#discussioncomment-19149863)
records the scoped claim and final artifact. Submission freshness is in the PR.
The submission refresh also read Ali Romman's new
[Discussion #5300](https://github.com/CrocSwap/integer-mult-bounds/discussions/5300):
its extension to all finite associative rings explicitly concerns insertion
count, with total tariffs left open, so it does not resolve this contribution.

## Open next questions

1. Determine the exact tariff for the same Boolean triple with independent
   positive prices on all six directed ADD edges. Start with cheap directed
   cycles and the seven-gate U witnesses. Aggregate destination counts discard
   parent identities, and the return lemma cannot charge each edge twice.
2. Determine the tariff for the incomparable Boolean triple `(1,2,4)` over
   `F_2^3`, which does not sum to zero. Single-insertion feasibility is already
   covered by #5266. Begin by finding a least-ADD conjugating suffix from a
   unit source column, then classify multi-insertion support. The zero-sum
   constructions and Boolean atom pattern proved here do not supply that bound.

The structured questions and blockers are in [TASK.json](TASK.json). These
are suggested obligations, not claims of reservation or exhaustive novelty.

## Credit

Prepared by lee-phys with substantial OpenAI Codex assistance in source
inspection, derivation, implementation, verification and writing; no subagents
or independent reviewers were used. Apache-2.0. The new result adds the sharp
single-insertion branch and proves its Boolean-ring scope. The nineteen
multi-insertion vectors, their words and portions of the verifier infrastructure
are adapted from lee-phys #5259 at the exact head cited above. Credit Ali Romman
#5266 for the many-row insertion-count theorem; lee-phys #5139/#5163 for
ideal invariance and the local-ring boundary; Nick Petalas #5208/#4916 for
equal-demand tariffs and the ring-valued contract; Krzysztof Wojt #5045 for
source-support classification and restoring words; Ross Richardson #3063/#3121
for tariffs and incoming-row restoration; and Cinna Davis, Anthony, Oscar
Fennell, Tekalign and the retained earlier fanout lineage.
