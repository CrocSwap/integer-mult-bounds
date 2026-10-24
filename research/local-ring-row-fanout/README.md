# Exact destination-priced dirty fanout over local rings

**Scoped written proof and exact finite corroboration; no new κ.**
For three dirty rows over Z/4 with demand `(2,1,1)`, we determine the exact
optimum for every positive source price and every positive **destination-only**
ADD price. There are eight indispensable price terms. The proof extends to
any number of rows over any commutative local ring, provided at least one
demand is a unit; other demands may be nonunits or zero.

This takes the three-row question in Krzysztof Wójt's
[#5045](https://github.com/CrocSwap/integer-mult-bounds/pull/5045) and
[#5139](https://github.com/CrocSwap/integer-mult-bounds/pull/5139) to a complete
price family. Independently pricing all six directed ADD edges remains open.
The source-count method and two-row mixing/repeated-insertion words retain
#5045's credit. The additional argument charges the first necessary unit
insertion somewhere among rows with nonunit demands.

## Contract and the three-row answer

For q >= 1 arbitrary independent dirty rows `a_i in R^w`, w >= 1, and one
preserved disjoint source `p in R^w`, require `A_i=a_i+lambda_i p` for every i.
Only fixed finite straight-line words in the following gates are allowed:

    P_i(beta):    A_i <- A_i + beta p,        price mu_i > 0;
    E_ij(alpha):  A_i <- A_i + alpha A_j,     price c_i > 0, i != j.

All prices are finite, stationary, coefficient-independent complete abstract
prices. The ADD price depends on its **destination i**, equally for every
source j. Both directions, all nonzero coefficients and all ordered pairs
are available. All original dirt must return exactly. There are no extra
rows, clearing, free basis changes, observations or adaptive choices. An
inverse execution, when required, is separately charged. Delete any
zero-coefficient gates, since their prices are positive.

**Three-row theorem.** Over Z/4, for demand `(2,1,1)`, the optimum is the
minimum of the following eight linear expressions, for all positive real
`(mu_0,mu_1,mu_2,c_0,c_1,c_2)`:

| Name | Price | Counts `(P_0,P_1,P_2,K_0,K_1,K_2)` |
|---|---|---|
| D | `mu_0+mu_1+mu_2` | `(1,1,1,0,0,0)` |
| F01 | `mu_0+mu_1+2c_2` | `(1,1,0,0,0,2)` |
| F02 | `mu_0+mu_2+2c_1` | `(1,0,1,0,2,0)` |
| F12 | `mu_1+mu_2+2c_0` | `(0,1,1,2,0,0)` |
| F1 | `mu_1+2c_0+2c_2` | `(0,1,0,2,0,2)` |
| F2 | `mu_2+2c_0+2c_1` | `(0,0,1,2,2,0)` |
| T0 | `2mu_0+2c_1+2c_2` | `(2,0,0,0,2,2)` |
| S0 | `mu_0+2c_0+2c_1+2c_2` | `(1,0,0,2,2,2)` |

Here K_i counts **all** ADD calls into row i. These eight vectors form the
exact Pareto frontier for these six aggregate counts. In the table's price
order, each term is uniquely cheapest at the corresponding vector below:

    D:   (1,1,1,1,1,1)       F01: (1,1,20,10,10,1)
    F02: (1,20,1,10,1,10)    F12: (20,1,1,1,10,10)
    F1:  (20,1,20,1,10,1)   F2:  (20,20,1,1,1,10)
    T0:  (1,20,20,10,1,1)   S0:  (5,20,20,1,1,1).

For example, take mu=(1,9,9) and every directed
ADD price equal to one. The exact optimum is **6**, attained chronologically by

    E_10(-1), E_20(-1), P_0(1), E_20(1), E_10(1), P_0(1).

A unit-forest relaxation would incorrectly predict five. With mu=(100,1000,1000)
and all ADD prices one, the optimum instead is **106**, attained by

    E_21(-1), E_01(-1), E_10(-1), P_0(1),
    E_10(1), E_01(1), E_21(1).

The middle two-row word gives demands (2,1) on rows 0,1; the outer echo
restores row 2 with demand one. Every dirt column is retained throughout.

## Arbitrary-row local-ring theorem

Let R be a commutative local ring with `1 != 0`; finiteness is unnecessary.
Its nonunits form its unique maximal ideal m. Let

    U = {i : lambda_i is a unit},        N = {0,...,q-1} minus U.

Assume U is nonempty. Zero demands are allowed in N. Define

    a_i = 0                         if lambda_i = 0,
          min(mu_i,2c_i)            otherwise;
    A = sum_i a_i,
    B = 2 sum_(i in U) c_i + sum_(i in N) a_i.

For each r in U and each r in N, respectively, define

    F_r = A + mu_r - a_r,                         r in U;
    T_r = B + 2mu_r - a_r,                        r in N;
    S_r = B + mu_r + 2c_r - a_r,                  r in N.

**Theorem.** The exact optimum over every allowed finite word is

    OPT = min( min_(r in U) F_r,
               min_(r in N) T_r,
               min_(r in N) S_r ),

where a minimum over the empty set is +infinity. Every candidate has an
explicit attaining word. This needs only O(q) arithmetic/comparison operations
once the unit/zero statuses and gate prices are supplied; it does not price
computing that algebraic information or physically implementing the gates.

Equivalently, the last two minima combine as

    B + min_(r in N) [mu_r + min(mu_r,2c_r) - a_r].

If all demands are nonzero, this simplifies further to

    OPT = min(A + min_(r in U)(mu_r-a_r),
              B + min_(r in N) mu_r).

For all-unit demands, N is empty and this recovers the credited
Ross Richardson #3063 / Nick Petalas #4916 destination-price specialization.
At zero total demand, the empty word costs zero. A nonzero demand list with
U empty is outside this theorem, even if its generated ideal is principal.

## Proof of the all-word lower bound

### Incoming-row return lemma

Let M be the matrix of the q original dirt coefficients. It starts and ends
at I_q, and every prefix is invertible: each ADD has its negated-coefficient
inverse, while P calls leave M unchanged. The all-input contract implies
matrix equality by testing each original input coordinate in turn.

A row cannot receive exactly one nonzero ADD. Before its sole ADD into i,
its dirt row is e_i. Immediately after `E_ij(alpha)` it is `e_i+alpha m_j`,
where m_j is row j of the invertible prefix matrix. No later gate changes
row i's dirt, so restoration would force `alpha m_j=0`. Multiplying by the
prefix inverse gives `alpha e_j=0`, hence alpha=0, a contradiction. Thus
any used destination receives at least two ADDs. This is the singleton
free-module return argument underlying #3063/#4916, restated here.

Consequently, a nonzero-demand row with no P call must receive at least two
ADDs. Its source coefficient otherwise stays zero. For any other nonzero-demand
row, at least one P call or at least two incoming ADDs is needed. Its bill
is therefore at least a_i. A zero-demand row has the trivial bound zero.

This is **not** a per-edge statement for q >= 3. For example, the chronological
word

    E_01(1), E_12(1), E_01(-1), E_12(-1), E_02(1)

is the identity on dirt over Z/4. Edge 2 -> 0 occurs once. The verifier checks
this control; the proof above counts three total arrivals at row 0 instead.

### A necessary unit insertion and its extra price

First suppose some r in U receives a P call. Row r costs at least mu_r and
all other rows cost at least a_i. The total is at least `A+mu_r-a_r=F_r`.

Otherwise no row of U receives a P call. Some P coefficient must still be
a unit: if every inserted beta belonged to m, all source coefficients would
remain in m under additions and multiplication by arbitrary ring elements.
Their initial coefficients are zero, while the endpoint has a unit demand,
a contradiction. Choose a row r receiving a unit insertion; necessarily r is
in N. There are two possibilities:

* Row r receives at least two P calls, so its bill is at least 2mu_r.
* It receives exactly one P call, with unit coefficient beta. With no incoming
  ADD, its final source coefficient would equal beta, contradicting its
  nonunit demand lambda_r (including lambda_r=0). Thus it receives at least
  two ADDs, so its bill is at least `mu_r+2c_r`.

Every unit-demand row has no insertion and costs at least 2c_i. Every other
row of N costs at least a_i. Adding these disjoint row bills gives T_r in
the first case and S_r in the second. This exhausts all words, including
repeated insertions, cancellations, feedback and arbitrary interleavings,
and proves the displayed minimum is a lower bound.

## Constructions attaining every candidate

All words below are chronological. For any nonzero-demand row besides the
chosen r, select direct insertion when mu_i <= 2c_i if that row is allowed
as a direct recipient below; otherwise select an echo. Zero-demand rows
besides r are untouched. Direct recipients receive `P_i(lambda_i)` and are
not used by any of the displayed row gates.

**Unit root r: F_r.** Any other nonzero-demand row may be direct or echoed.
For each echoed i put `t_i=lambda_i lambda_r^(-1)`. Prepare all echoed rows
with `E_ir(-t_i)`, execute `P_r(lambda_r)`, then reverse the preparation with
negated coefficients. Each echoed row becomes

    (a_i-t_i a_r)+t_i(a_r+lambda_r p) = a_i+lambda_i p.

Add the independent direct calls. The exact price is F_r. This is the
credited dirty-echo construction with a unit root.

**Nonunit root r, repeated insertion: T_r.** Only other nonzero-demand rows
in N may be direct recipients; choose the cheaper direct/echo option for each.
All unit-demand rows are echoed. Prepare every echoed i with `E_ir(-lambda_i)`,
insert `P_r(1)`, undo preparation, then insert `P_r(lambda_r-1)`. The last
coefficient is nonzero since lambda_r is not a unit. Row r ends with its
own demand and every echoed row gets lambda_i p. Together with the direct
calls, the price is exactly T_r. This extends #5045's repeated-insertion word.

**Nonunit root r, one insertion with mixing: S_r.** Choose any unit-demand
row j, and use the same direct/echo choices on other rows of N. Set
`b=lambda_r lambda_j^(-1)`. For every echoed i other than j prepare
`E_ij(-lambda_i lambda_j^(-1))`. Then execute #5045's two-row word

    E_rj(1-b), E_jr(-1), P_r(lambda_j), E_jr(1), E_rj(b-1).

Its source column becomes `lambda_j e_r`, then
`lambda_j(e_r+e_j)`, then `lambda_r e_r+lambda_j e_j`.
The two pre-gates are the inverse of the two post-gates on dirt. Now undo
all earlier preparations in reverse order. Each echoed row uses the restored
unit-demand row j and ends correctly. Direct recipients are independent.

Here b is a nonunit, so b != 1 and all four core ADDs are nonzero. Each
nonzero echoed coefficient is nonzero because lambda_j is a unit. The exact
price is S_r: two arrivals at r, two at every unit-demand row, and the chosen
minimum bill on other N rows. This also covers lambda_r=0. The original dirt
of this temporary recipient returns. Literal inversion of any complete word
reverses its gates and negates coefficients, with the same tariff.

These constructions and the all-word lower bound prove the theorem.
Expanding it for q=3, lambda=(2,1,1) gives the eight-term table. More directly,
if a unit-demand row receives a source call, each of the six possible source
supports dominates its table vector. Otherwise only row 0 receives insertions:
two or more give T0, and a single unit insertion forces at least two arrivals
at all three rows, giving S0. Since every table vector is attained, they are
exactly the Pareto-minimal aggregate counts. The strict price witnesses above
show that no term can be removed from the positive-price envelope.

## Why locality matters: an exact nonlocal counterexample

Over Z/6 use demand `(2,3,1)`, mu=(10,10,100), c=(100,100,1). The two nonunit
source coefficients can combine to a unit, since `2*2+3=1 mod 6`. The word

    E_20(-2), E_21(-1), P_0(2), P_1(3), E_21(1), E_20(2)

costs **24** and restores every dirt column. Applying the local-ring formula
outside its hypotheses would predict **32**.

In fact 24 is optimal. A cheaper word cannot use a P at row 2 (price 100)
or an incoming ADD to row 0 or 1 (price 100). Thus each of rows 0,1 needs a
source call. Three such calls already cost 30, so a cheaper word must have
exactly one at each, with coefficients 2 and 3 respectively. To produce the
unit demand on row 2, both incoming edges must be used: either source alone
generates a proper ideal. Since rows 0,1 have unchanged dirt, each edge's
coefficients must separately sum to zero to restore row 2. Each used edge
therefore occurs at least twice. The bill is at least `10+10+4=24`.
This proves the counterexample without assuming a word-length bound.

## Verification and scope

The self-contained standard-library verifier checks the finite ring axioms,
locality, candidate prices, literal words and inverses on all formal input
columns. It includes prime-power residue rings and the non-chain local ring
`F2[e,h]/(e^2,eh,h^2)`. Zero-demand temporary recipients, all-unit boundaries,
all eight strict regimes, the five-ADD identity and the nonlocal example are
explicit controls. Wider row fixtures test the arbitrary-q construction.

A separately implemented packed-state bidirectional Dijkstra oracle searches
unrestricted three-row Z/4 words. Its state retains all nine dirt coefficients
and all three source coefficients. Every nonzero coefficient and directed
ADD edge is permitted; there is no depth cutoff, forest restriction or
formula-based pruning. Search ends only when the two Dijkstra frontier
bounds certify the best meeting distance. Returned paths are replayed by
the primary literal interpreter and charged exactly. This is an implicit
finite-state shortest-path search, not enumeration of the entire state graph.

The six local-ring fixtures cover 2,011 demand-list instances and 6,033 price
instances. All 25,179 candidate words pass 213,744 formal-column forward/inverse
executions; 6,688 additional literal forward/inverse executions cover the
eight three-row regimes and the Z/6 witness. Sixteen independent shortest-path
queries settle 154,814 entries in total (counting both directions and repeated
queries), alongside 15 explicit controls. Wider fixtures are deterministic
examples, not exhaustive arbitrary-row searches.

Normal and optimized warning-strict commands are registered, with no external
scientific inputs or third-party dependencies. In disposable optimized-mode
copies, removing the extra unit-arrival charge, deleting a dirt-preparation
gate, or replacing the oracle's heterogeneous prices by unit weights each
causes an explicit rejection. Run the registered checks with:

```sh
python3.12 -B scripts/research_package.py --package research/local-ring-row-fanout --check-only
python3.12 -B scripts/research_package.py --package research/local-ring-row-fanout
python3.12 -I -W error -B research/local-ring-row-fanout/verify.py
```

The all-ring-size, arbitrary-row and all-positive-price claims rest on the
written proof. Finite computations corroborate bounded cases. Independent
human review and proof-kernel acceptance are unclaimed. General directed-edge
prices, nonzero all-nonunit demand lists, nonlocal-ring tariffs and complete
physical caller costs remain open outside the stated cases. There is no new
supplier, precision/tape admission, selected-frontier change or κ.

## Task, sources and overlap

Scientific base: canonical main `a5df48c55ea806d7952b65acc9c76d878ff09b13`,
priority revision 7. [TASK.json](TASK.json) preserves the historical
`bit-helper-contract` card and marks this explicitly requested algebraic side
result as changed. [SOURCES.json](SOURCES.json) pins #4916's ring contract and
#5045's two-row proof/three-row handoff as historical provenance; no predecessor
executable is imported. #5139 motivates this next question but is not a proof
or runtime dependency. Its pending head is `ec44e8bec68b49a1ba7adaac8a0bba0192bd638c`.

Entry overlap pagination covered 312 open PRs at 11:04 UTC and 4,318 Discussion
records at 11:06 UTC on 2026-10-23. All-state targeted three-row/nonunit/fanout
searches and live #5030/#1166 reads found no resolving successor in that
coverage. Sparse historical notes, arbitrary diffs and unpublished work were
not exhaustively searched. Submission refresh is recorded in the PR.

## Open next questions

1. **Independently priced directed edges for (2,1,1) over Z/4.** This is the
   remaining part of the original three-row question. Start with one price
   matrix where the cheap edges form a cycle, then compare a restoring word
   against subset cuts plus the necessary unit-arrival charge. Counting only
   total arrivals at each row loses which sources supplied them.
2. **All-nonunit local-ring demands.** Start with `(2,2,2)` over Z/4, then
   `(e,h,e+h)` over the eight-element square-zero local ring. This tests shared
   source injection without a unit demand. The necessary unit insertion used
   here is absent, so this lower bound does not classify those cases.
3. **A physical caller.** Supply its complete stationary tariffs, including
   source access, coefficient preparation, routing, precision and restoration,
   and compare the full completed bill. That cost contract is missing here.

## Credit

Prepared by lee-phys with substantial OpenAI Codex assistance in derivation,
implementation, checking and writing. Apache-2.0. Credit Krzysztof Wójt #5045
for the nonunit two-row theorem, repeated/mixing words and three-row question;
Nick Petalas #4916 for the ring-valued contract and free-module cut reasoning;
Ross Richardson #3063/#3121 for destination/edge tariffs and dirt restoration;
Cinna Davis #1944/#1968, Anthony #774, Oscar Fennell #759, Tekalign #3130, and
the retained lineage. #5139 records the continued three-row question.
The local-ring ideal fact is classical. The new contribution is the unit-arrival
price bound, its matching arbitrary-row constructors, the exact eight-term
three-row frontier and the explicit nonlocal boundary.
