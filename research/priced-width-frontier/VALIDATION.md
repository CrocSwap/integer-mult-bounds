# Reproduction and evidence

The universal result is the written proof. The finite corroboration uses exact integer or rational arithmetic throughout. Commands below were exercised with CPython 3.12.10. All scientific inputs travel inside the package. No network or Git process is needed by the scientific entry points.

| Check | Domain | Result |
| --- | --- | --- |
| Single-cut prices | All 1,023 nonempty menus on widths 1–5, each present width priced at 1, 2 or 3 | 50,127 target prices agreed with a separate integer amount oracle, including 996 infeasible targets and 1,329 early exceptions in eventually reachable classes |
| Literal multiplicities | Same menus, targets 0–12 | All 107,403 count vectors within the target cap were visited and the 13,299 minima agreed |
| Heterogeneous cuts | 108 two- or three-cut combinations with different gcds, quantities, rational prices and parents | 5,818 positive replications checked against independent bills |
| Exhaustive pairs | 255 nonempty menus on widths 1–4, invocation prices 1–3, job multiplicities 1–3, unordered pairs with replacement | 292,995 pairs and 17,579,700 positive pair/replication observations. In 5,319 pairs the joint onset precedes the larger separate onset. In 456 pairs the first floor occurs after the least period |
| Fixed-fee families | All parameters 2–48 | 39,198 replications of the long family and all 763 records agreed with the closed form. The priced #6658 family contributed 94 records |
| Tied-price onset family | All parameters 2–48 | 38,023 direct positive targets checked the quadratic solo onset and the masked joint onset |
| Literal endpoint | Execute the 12 records of the two displayed N=12 fixed-fee families on the direct-sum shear of #6658 | 2,082 individual additions and 199 dispatches. Every output and dirty coordinate agreed. An invocation spanning two different cuts was rejected |
| Large common period | 12 prime-width menus, 197 anchor classes | Period and first floor 7,420,738,134,810. Fourteen large targets were checked using quotient-and-remainder schedules without enumerating the whole period |
| Retained rank-12 compiler | Both compiled widths on each positive child cut | Two independent billing methods agree through all 3,920 feasible replications and on the two exact records. Five rank-eight fee pairs exercise both sides of the price threshold and equality |
| Recursive unit fees | Positive program invocations in both historical libraries | The literal rank-eight traversals visited 3,639 and 13,928,545 invocations. The full child bills at the rank-12 parent agreed through all 3,920 feasible replications |

## How the checks differ

[pricing.py](pricing.py) uses lexicographic residue labels and reconstructs explicit invocation counts. [oracles.py](oracles.py) fills amounts one width at a time and independently enumerates short literal count vectors. [checks.py](checks.py) verifies each label's witness and all outgoing Bellman inequalities. [execution.py](execution.py) executes a compatible finite shear, checks cut endpoints and meters the additions and dispatches separately.

[census.py](census.py) computes integer bills directly before comparing with the solver. It observes every positive replication through 60. In this grid all anchor widths and all other widths are at most four. A least simple path has size at most 12, so all cut tails hold by replication 12. Each pair period divides 12 and a common single-width cheapest witness exists by 12. These bounds make the comparison of three disjoint 12-term blocks and the backward search for the last mismatch sufficient to determine the genuine period, onset and complete frontier throughout this finite grid. The stored digest encodes the period, onset, first floor, record count and record coordinates in lexicographic pair order. Price equality is also checked at every record. [Census output](CENSUS.json)

The source-bound rank-12 check regenerates the frozen compiler's widths, leaf counts and chronological cuts. Its second price calculation counts the exact nested and smaller calls by integer division. For complete fixed trees, a bottom-up recurrence is checked against a depth-first traversal of every rank-eight invocation. The general menu solver uses no predecessor optimization code. The methods have one assisted author. Independent human review and a proof-kernel formalization are open.

## Commands

From the repository root:

```sh
python3.12 -I -W error -B research/priced-width-frontier/verify.py
python3.12 -I -O -W error -B research/priced-width-frontier/verify.py
python3.12 -I -W error -B research/priced-width-frontier/census.py
python3.12 -I -W error -B research/priced-width-frontier/audit_mutations.py
python3.12 -B scripts/research_package.py --package research/priced-width-frontier
```

The expected markers are `PASS_PRICED_WIDTH_FRONTIER`, `PASS_PRICED_WIDTH_CENSUS`, `PASS_PRICED_WIDTH_MUTATIONS` and `PASS_REGISTERED_RESEARCH_PACKAGE`. The first two scientific commands emit identical full receipts. The fault audit first requires an unchanged private copy to pass in both modes, then changes one input or implementation decision at a time and requires its named failure under both Python modes. Faults include accepting price ties as records, applying a tail formula before its cutoff, ignoring a parent width, treating gcd reachability as cheap fill, pooling rank-12 cuts and dropping actual charges. All temporary copies are separate from the published input tree.

The package checker also provides a full-history publication check:

```sh
python3.12 -B scripts/check_research_commit.py --package research/priced-width-frontier --check-source-history
```

The full-history check authenticates declared source provenance. Code correctness and the theorem are checked separately.
