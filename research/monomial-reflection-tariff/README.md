# Exact tariffs for full monomial reflection words

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped written proof with exact finite corroboration.**
For G(m,1,n), allow every monomial rank-one reflection as a unit paid call,
including nonadjacent phase-weighted swaps and higher-order phase operations.
For arbitrary diagonal targets g_j, free scalar mixing, and any finite number
of restored arbitrary dirty registers, the exact minimum count is

    sum_j (n - b(g_j)),

where b(g) counts permutation cycles whose accumulated phase is one. The
coefficient field may be any field containing an element of exact order m.
Every target has a constructive attaining word, with no helper or scalar
preparation. [PROOF.md](PROOF.md) gives the full model and proof.

For example, with a primitive third root zeta, the two-coordinate map
`g e_0=zeta e_1, g e_1=e_0` has one unbalanced cycle. The endpoint
`diag([g],[g^-1])` costs exactly four calls, regardless of the number of
restored dirty spectators. Both phase and swap calls are charged.

The new contribution is this register-model tariff for a changed alphabet.
The ordinary reflection-length formula is classical, including
[Jian-yi Shi's formula](https://www.sciencedirect.com/science/article/pii/S0021869307003882)
and [Briana Foster-Greenwood's length/codimension treatment](https://arxiv.org/html/1202.0266v1#S3).
The proof restates the elementary cycle construction and uses the established
augmentation/displacement-rank method. No new reflection-length principle
or literature-wide priority is claimed.

## Evidence and reproduction

The standalone checker imports no predecessor executable and writes only to
standard output. Its generated receipt binds every package file by SHA256.
The fixed finite domains are G(1,1,4), G(2,1,4), G(3,1,3), G(3,1,4),
G(4,1,3), G(5,1,3) and G(6,1,3).

- An unpruned Cayley search visits all 4,944 group elements and 130,344
  directed transitions. Every distance equals n-b(g). Every constructed
  word has that length and the exact formal group label. Separate dense
  finite-field multiplication and displacement ranks agree, using primitive
  roots over F5, F7 or F11.
- All 324 ordered G(3,1,2) target pairs have complete rational group-algebra
  endpoints and inverse restoration with a genuinely mixed dirty spectator.
  The fixtures contain 972 paid events. Each of the 323 nonempty words fails
  when its first call is omitted. No basis-only endpoint test is used.
- Controls distinguish an unbalanced cycle, chronological order, a nonprimitive
  root and a formal dirty leak that vanishes in the natural representation.
  The nonzero eighteen-term group norm is retained by the formal oracle.

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/monomial-reflection-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/monomial-reflection-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/monomial-reflection-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/monomial-reflection-tariff --check-source-history
```

Other hosts may substitute their CPython 3.12 executable. Expected markers
are `PASS_MONOMIAL_REFLECTION_TARIFF`, `PASS_REGISTERED_RESEARCH_PACKAGE`
and `PASS_RESEARCH_COMMIT_BYTES`. Both registered commands run the same
finite coverage in normal and optimized Python. Each has a 60-second limit.
The written proof supplies the universal conclusion; the finite cases
corroborate it. No receipt is handwritten or regenerated during verification.

## Sources, overlap and limits

The source question is David Arias / DavidAriasC's
[PR2738](https://github.com/CrocSwap/integer-mult-bounds/pull/2738),
Open next question 2. That theorem covers simple Coxeter generators. This
package changes the paid alphabet to all monomial reflections, including
operations of order greater than two. Gareth Davidson / bitplane's
[PR1333](https://github.com/CrocSwap/integer-mult-bounds/pull/1333)
supplies augmentation normalization and the displacement-rank method,
retaining eumemic, Ali Romman / PR468, David Govea / PR720 and their credited
register-model lineage. Adam Gall and Ross Richardson's cut-method lineage
remains credited by PR2738. These results are cited, not audited or replayed.

Scientific base is canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected
PR6030. [SOURCES.json](SOURCES.json) pins the question and method statements.
[TASK.json](TASK.json) records the changed card scope. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19373434)
precedes the computation. Source-binding orientation passed. Cached overlap
covered 556 open PRs and 6,600 Discussion records with complete pagination;
only 123 local notes were materialized against 8,917 HEAD note paths.
Targeted all-main general-form searches and merged-PR searches supplement
that sparse local coverage. Arbitrary diffs and unpublished work are limits.

This closes a sharing route within an optimistic unit-reflection model.
It does not price higher-rank calls concavely, classify nonuniform generator
prices, or implement a native address instruction. Scalar work, routing,
ownership, storage, precision, stock, tape, hosting, complete recursive
invoices and outer use remain separate obligations. No supplier admission,
new kappa, selected-frontier change or complete multiplication theorem is
claimed. All five selected framework assumptions remain. Independent human
and formal proof-kernel review are unclaimed. Lean, Docker, predecessor
scientific replays and selected cold replay were not run.

## Verifier bounds

There is no recursion, network, subprocess, dynamic code or external callback.
Each fixed search has at most 1,944 group states and 33 generators. Matrix
rank checks have at most four rows. Formal fixtures have three registers,
eighteen possible group labels and rational coefficients. Every loop is
bounded by these fixed domains or by the finite collection it reads.
Every function is shorter than 60 physical lines. Explicit exceptions keep
checks active under optimized Python; warning-strict normal and optimized
execution are the available diagnostics. No separate static analyzer is
installed. Source reads authenticate the two fixed predecessor text inputs.

Power-of-ten rule 3 deviation: Python allocates tuples, integers, fractions,
sets and dictionaries dynamically. The fixed domains above bound live data;
Python offers no static allocation guarantee. A larger externally supplied
search is outside the executable contract. No repository-wide build settings
or predecessor code are changed.

## Open next questions

Can selected higher-rank monomial calls with concave prices beat this
unit-reflection invoice after their native implementation costs are included?
This changes the price contract and may admit sharing. Start with one
explicit primitive and complete formal endpoint, then compare its full
boundary bill. The present rank-one proof does not charge such a primitive
one unit or establish physical profitability. Without that changed contract,
further dirty-workspace searches in this alphabet are unnecessary.
