# Exact dirty-fanout tariff for a nonprincipal zero-sum triple

**Scoped written proof with exact finite corroboration; no new kappa.**
For three arbitrary dirty rows over
`R=F2[e,h]/(e^2,eh,h^2)` with demand `(e,h,e+h)`, the exact
positive-price envelope has **19 indispensable terms**. All 19 aggregate
count vectors are attained and form the complete Pareto frontier.

This resolves the unequal all-nonunit example in lee-phys
[#5163](https://github.com/CrocSwap/integer-mult-bounds/pull/5163) and Nick Petalas
[#5208](https://github.com/CrocSwap/integer-mult-bounds/pull/5208).
The proof also applies over every commutative unital ring to every zero-sum
triple generating a nonprincipal ideal. Finiteness, locality and a square-zero
radical are unnecessary for this extension.

## Contract and price formula

Let R be a commutative ring with `1 != 0`. There are exactly three independent
arbitrary dirty rows `a_0,a_1,a_2 in R^w`, w >= 1, and one disjoint preserved
source p. A fixed finite straight-line word must produce

    A_i = a_i + lambda_i p,  i=0,1,2,

while retaining all original dirt. The only gates are

    P_i(beta):   A_i <- A_i + beta p,       price mu_i > 0;
    E_ij(alpha): A_i <- A_i + alpha A_j,    price c_i > 0, i != j.

Every coefficient and ordered pair is available. Prices are finite,
stationary, coefficient-independent complete abstract prices; an ADD price
depends only on its receiving row. Zero-coefficient gates may be deleted.
There are no extra rows, clearing, observations, adaptive choices or free
basis changes. A separate inverse execution has a separate bill.

**Theorem.** Suppose

    lambda_0 + lambda_1 + lambda_2 = 0,
    I = (lambda_0,lambda_1,lambda_2) is not a principal ideal.

For `{i,j,k}={0,1,2}` define

    D   = mu_0 + mu_1 + mu_2,
    T_i = 2mu_i + 2c_j + 2c_k,
    B_k = mu_i + mu_j + 2c_k
          + min(mu_i,mu_j,2c_i,2c_j,2c_k).

Then the exact optimum over all allowed words is

    OPT = min(D,T_0,T_1,T_2,B_0,B_1,B_2).

Expanding each B_k gives nineteen linear terms. Every term is necessary for
some strictly positive price vector. The formula requires a constant number
of arithmetic/comparison operations once prices and the algebraic hypotheses
are supplied. It does not price determining ideal structure or implementing
the abstract gates physically.

For the requested eight-element ring, `I=(e,h)={0,e,h,e+h}` is nonprincipal:
a nonunit generator x has `(x)={0,x}`, whereas a unit generates R. The
zero-sum identity holds in characteristic two. Thus the theorem applies.
At mu=(1,9,9), c=(1,1,1), the exact optimum is **6**, attained by

    E_10(1), P_0(h), E_10(1),
    E_20(1), P_0(e+h), E_20(1).

The first echo gives row 1 its demand h, the second gives row 2 its demand
e+h, and the two insertions leave e in row 0. In contrast, the equal-demand
example `(e,e,e)` has cost five at these prices, as covered by #5208. Equality
of the demands is an essential distinction.

## Lower bound for arbitrary interleavings

### Two necessary facts

First, the hypotheses imply every lambda_i is nonzero and
`lambda_i not in (lambda_j)` whenever i != j. Indeed, if
`lambda_i in (lambda_j)`, the zero-sum relation puts the third demand in
`(lambda_j)` as well, making I principal. If a demand is zero, the remaining
two are negatives and again generate a principal ideal.

At least two nonzero P calls are necessary. With exactly one call P_r(beta),
the final source coefficient column is `beta v`, where v is column r of the
invertible suffix dirt matrix L. Its entries generate exactly `(beta)`:
one inclusion is immediate, and row r of `L^-1` expresses beta as a linear
combination of the final source coefficients. This contradicts nonprincipality
of I. With no P calls the source column is zero. This is the ideal-invariance
necessity from #5139, applied to three rows; no sufficiency claim is used.

Second, a row cannot receive exactly one nonzero ADD while its original dirt
returns. Let M be the invertible dirt matrix immediately before that sole
`E_ij(alpha)`. Row i has remained e_i, and the update changes it to
`e_i+alpha m_j`. No later gate changes this dirt row. Restoration would give
`alpha m_j=0`; multiplying by `M^-1` gives `alpha e_j=0`, hence alpha=0.
Consequently every row with no P call must receive at least two ADDs, since
its nonzero final source coefficient otherwise remains zero. This is the
credited incoming-row return argument of #3063/#4916/#5163.

The argument concerns total incoming calls, not each individual edge. The
verifier retains the three-row five-ADD identity from #5163 as a control
against that invalid stronger interpretation.

### Classify by insertion support

Let S be the set of rows receiving at least one nonzero P call. Charge each
gate to its destination, and write K_i for the total number of incoming ADDs.

If S contains all three rows, the bill is at least D. If `S={i}`, at least
two P_i calls and two ADDs into each other row are needed. The bill is at
least T_i, regardless of coefficients or interleavings.

It remains to consider `S={i,j}`, with k the row without insertions. In all
cases `K_k>=2`.

* If either i or j receives a second P call, the bill is at least
  `mu_i+mu_j+2c_k+min(mu_i,mu_j)`.
* Otherwise there is exactly one insertion in each of i,j. If either of these
  rows receives any ADD, it receives at least two, giving the lower bound
  `mu_i+mu_j+2c_k+min(2c_i,2c_j)`.
* Otherwise neither insertion row receives an ADD. Their dirt rows stay
  a_i,a_j throughout, and their single inserted coefficients are respectively
  lambda_i,lambda_j. To produce lambda_k, row k must use both incoming
  edges: either parent alone could produce only an element of its principal
  ideal. On each used edge, the sum of its coefficients must be zero to
  restore that parent's independent dirt. A single nonzero call cannot have
  zero sum, so each edge occurs at least twice. Thus `K_k>=4`, giving
  `mu_i+mu_j+4c_k`.

The last per-edge count is used only when both parent dirt rows are unchanged.
Taking the minimum of these exhaustive cases gives B_k. Together the cases
prove the stated all-word lower bound. Repeated insertions, unit insertions
with cancellations, feedback and arbitrary finite interleavings are included.

## Matching words and the nineteen count vectors

All words are chronological. Indices i,j,k below are distinct. Signed
coefficients are retained so the same constructions work in odd characteristic.
Let a count vector record `(P_0,P_1,P_2,K_0,K_1,K_2)`.

| Family | Price | Nonzero counts | Number |
|---|---|---|---|
| D | `sum mu_i` | `P_i=1` for all i | 1 |
| T_i | `2mu_i+2c_j+2c_k` | `P_i=2, K_j=K_k=2` | 3 |
| R_(i,j;k) | `2mu_i+mu_j+2c_k` | `P_i=2,P_j=1,K_k=2` | 6 |
| M_(i,j;k) | `mu_i+mu_j+2c_i+2c_k` | `P_i=P_j=1,K_i=K_k=2` | 6 |
| Q_k | `mu_i+mu_j+4c_k` | `P_i=P_j=1,K_k=4` | 3 |

**D: direct insertion.** Use `P_i(lambda_i)` on all three rows.

**T_i: two successive echoes from one insertion row.** Use

    E_ji(1), P_i(-lambda_j), E_ji(-1),
    E_ki(1), P_i(-lambda_k), E_ki(-1).

Each echo transfers the increment between its two row gates. The second
preparation includes the source coefficient already present in row i; that
coefficient cancels on undoing the preparation. Row i ends with
`-lambda_j-lambda_k=lambda_i`, and each other row receives its own demand.

**R_(i,j;k): repeat one root and insert directly into the other.** Use

    E_ki(1), P_i(-lambda_k), E_ki(-1),
    P_i(-lambda_j), P_j(lambda_j).

The echo gives lambda_k to k. The two P_i calls sum to lambda_i; the direct
P_j call supplies lambda_j. No dirt remains mixed.

**M_(i,j;k): prepare a two-edge chain.** Use

    E_ij(1), E_ki(1), P_i(-lambda_k), P_j(lambda_j),
    E_ki(-1), E_ij(-1).

Just before undoing the preparation, the three relevant rows are

    A_i = a_i+a_j-lambda_k p,
    A_j = a_j+lambda_j p,
    A_k = a_k+a_i+a_j.

The last two gates give A_k its required increment lambda_k p and give A_i
`(-lambda_k-lambda_j)p=lambda_i p`, restoring all dirt.

**Q_k: combine two independent source rows.** Use

    E_ki(1), E_kj(1), P_i(lambda_i), P_j(lambda_j),
    E_kj(-1), E_ki(-1).

The final increment at k is `(-lambda_i-lambda_j)p=lambda_k p`.
All gates above have nonzero coefficients. Their exact counts match the table.
Literal inversion reverses the word and negates every coefficient.

The lower-bound classification proves that every achievable count vector
componentwise dominates at least one table vector. These nineteen vectors
are pairwise incomparable and all attained, so they are exactly the Pareto
frontier. To show each is also indispensable for strictly positive prices,
it suffices to expose one representative of each family; permute row labels
for the other cases. Prices below are in `(mu_0,mu_1,mu_2,c_0,c_1,c_2)` order:

| Unique minimum | Positive price vector | Optimum |
|---|---|---|
| D | `(1,1,1,1,1,1)` | 3 |
| T_0 | `(1,3,3,1,1,1)` | 6 |
| R_(0,1;2) | `(1,2,5,1,2,1)` | 6 |
| M_(0,1;2) | `(3,5,10,1,3,2)` | 14 |
| Q_2 | `(3,3,5,2,2,1)` | 10 |

## Hypotheses and verification

Nonprincipality is substantive. In the Boolean product ring `F2 x F2 x F2`,
write elements as bit masks, with identity 7. Demand `(3,5,6)` has sum zero
and pairwise incomparable principal ideals, but generates the principal unit
ideal. Set

    L = E_10(5), E_20(6), E_01(4).

Starting from column `(7,0,0)`, L produces `(3,5,6)`. Therefore the chronological
word `L^-1, P_0(7), L` meets the dirty endpoint. It costs 16 at
mu=(10,100,100), c=(1,1,1), below the inapplicable formula's value 24.
The verifier checks this strict discriminator. It is not a claim of the full
Boolean-ring optimum. Nonzero demand lists failing the zero-sum condition
are also outside the theorem.

The self-contained standard-library verifier checks all nineteen words and
inverses on every formal input column over four finite rings: the requested
ring, its odd-characteristic F3 counterpart, `Z/4[t]/t^2`, and the nonlocal
product of the requested ring with F2. It enumerates all zero-sum demand
triples generating nonprincipal ideals in those fixtures. Literal scalar
checks cover every input assignment for all nineteen requested-ring words.
Exact count vectors, strict positive-price exposure and hypothesis-removal
controls are checked separately.

A separate packed-state bidirectional Dijkstra oracle searches unrestricted
three-row words over the requested eight-element ring. It tracks all nine
dirt and three source coefficients, permits every nonzero gate coefficient
and every directed edge, and uses no word-length cutoff or formula pruning.
Its two frontier lower bounds certify the best meeting distance. Returned
words are replayed and charged by the primary ring interpreter. The search
explores implicit finite states; it does not enumerate the entire affine graph.
The verifier prints exact coverage and search counts.

The recorded run covers 102 demand triples and 1,938 words, with 15,504
formal forward/inverse column checks and 155,648 literal scalar checks.
Seven oracle queries settle 129,443 states in total (counted separately in
each search direction and query). The five family witnesses have exact costs
3, 6, 6, 14 and 10; the asymmetric example costs 6, and the rational-price
case costs 79/30. Normal and optimized isolated Python runs have identical
complete output. Three disposable optimized-mode mutations are rejected:
undercharging the two-insertion term, omitting a chain's dirt preparation,
and replacing heterogeneous oracle prices by unit weights.

```sh
python3.12 -B scripts/research_package.py --package research/square-zero-triple-fanout --check-only
python3.12 -B scripts/research_package.py --package research/square-zero-triple-fanout
python3.12 -I -W error -B research/square-zero-triple-fanout/verify.py
```

The arbitrary-ring and all-positive-price statements rest on the written proof;
finite checks corroborate bounded cases. Independent human review and
proof-kernel acceptance are unclaimed. Physical source access, coefficient
preparation, routing, precision, stock and complete supplier admission remain
outside this complete abstract-price contract. No selected-frontier change
or new kappa follows.

## Sources and overlap

Scientific base: canonical main `ff3cc58e370d0f678e529246f8c73e8094e18fcf`,
priority revision 7. TASK.json preserves the historical `bit-helper-contract`
card and records the explicit donor's algebraic side-result scope change.
SOURCES.json pins the predecessor proof texts as provenance; no predecessor
executable is imported.

The immediately preceding survey covered 311 open PRs at 13:54 UTC and 4,490
Discussion records at 13:58 UTC on 2026-10-23, with complete reported remote
pagination. New all-state targeted PR searches and live #5030/#1166 reads at
entry found no resolving successor. Sparse historical notes, arbitrary diffs
and unpublished work were not exhaustively searched. Submission refresh and
hosted CI are recorded in the PR.

## Open next questions

1. Price a zero-sum triple with a principal demand ideal and incomparable
   component ideals, beginning with `(3,5,6)` over the Boolean product ring.
   One-insertion words can now compete, so the source-support lower bound
   needs a new one-insertion branch; the cost-16 discriminator is only an upper
   bound for that case.
2. Determine independently directed-edge-priced tariffs for the requested
   `(e,h,e+h)` triple. Start with a cheap directed cycle. Destination totals
   discard the identities of incoming parents and do not provide its lower bound.
3. Classify nonprincipal triples without the zero-sum relation, beginning with
   `(e,h,e+h+z)` in `F2[e,h,z]/(e,h,z)^2`. Its demand ideal needs three generators, and the zero-sum constructions
   no longer supply the target. Cancelling unit insertions must still be
   considered when seeking a lower bound.

## Credit

Prepared by lee-phys with substantial OpenAI Codex assistance in derivation,
implementation, checking and writing; no subagents or independent reviewers.
Apache-2.0. Credit Nick Petalas #5208 for the equal-demand theorem and explicit
unequal-demand handoff, lee-phys #5139/#5163 for ideal invariance and the local-ring
boundary, Krzysztof Wojt #5045 for source-count classification and two-row
restoring words, Nick Petalas #4916 for the ring-valued contract, Ross Richardson
#3063/#3121 for tariff and dirt-restoration arguments, and Cinna Davis, Anthony,
Oscar Fennell, Tekalign and the retained lineage. The new step is the exhaustive
two-recipient surcharge and its matching nineteen-vector zero-sum frontier.
