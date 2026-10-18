# Ternary dirty echoes under a fixed scratch budget

**Independent mathematical verification; no new kappa.**

At 127 factors and nine borrowed arrays, an unbalanced ternary echo uses
**7,488 leaf calls**, compared with **8,800** for PR689's optimal balanced tree.
The saving is `41/275`, about **14.91%**, with the same data-array budget.
The complete tree and all restoration calls are supplied and replayed.

The audit computes the exact minimum in one defined class: consecutive ordered
splits, three children at every node with at least three factors, and two leaf
children at a two-factor node. All leaves have unit cost. It allows unbalanced
sizes, unlike PR689. Other fanouts, general binary splits, unequal leaf prices
and other dirty algorithms are outside this class.

| Factors | Array cap | Exact minimum calls | Root split | PR689 balanced calls / arrays |
|---|---:|---:|---|---|
| 5 | 3 | 20 | 2,1,2 | 20 / 3 |
| 71 | 8 | 2,688 | 25,20,26 | 2,944 / 8 |
| 127 | 9 | 7,488 | 47,33,47 | 8,800 / 9 |
| 127 | 10 | 6,784 | 44,29,54 | 8,800 / 9 |
| 243 | 10 | 32,768 | 81,81,81 | 32,768 / 10 |

The ten-array 127-factor row spends an extra array. At the maximum capacity
of ten arrays, the 243-factor tree is forced, so unbalanced splitting gives
no improvement. These are scoped finite results, not a new asymptotic exponent.

## Reproduce

Python 3.10+ and the standard library are sufficient. No network, Git history,
third-party package or external solver is needed after checkout.

```sh
python3 -I -B research/dirty-echo-space-audit/verify.py
```

Expected final line:

```text
PASS_TERNARY_ECHO_SPACE_AUDIT 2673 cells; 606 literal witnesses; 11 controls
```

The command also passes with `-O`. It checks retained source hashes, regenerates
all evidence, and compares the complete result with `CERTIFICATE.json`.
The comparison preserves JSON types; a boolean cannot replace an integer.
`--write NEW_PATH` writes a new receipt without replacing an existing file.

## Proof and completed coverage

The [proof](PROOF.md) gives the optimality recurrence, its lower-bound and
attainability arguments, exact capacity boundary, full instruction identity,
restoration contract and cost bill. `trees.py` groups a finite minimum into two
pairwise minima. The verifier uses independent enumeration of all triples.

- All `1 <= n <= 243`, `0 <= s <= 10`: **2,673 states**. Exactly 606 are
  feasible and 2,067 are infeasible. The independent recurrence evaluates
  715,401 feasible ordered triples and agrees at every state.
- Every feasible tree is rebuilt. The checker streams all **3,019,051** leaf
  instructions across these witnesses and checks exact call count, maximum
  array index, factor indices, and the inherited lower call bill.
- An independent enumeration covers all **105,980 ordered trees** through
  14 factors and compares minima at all 11 scratch budgets.
- **78** free noncommutative algebra replays check both orientations of 39
  selected trees, including the 127-factor and maximum-capacity witnesses.
  Every initial dirty symbol is retained. Separate nonlinear tests check
  exact restoration, inverse execution and target independence on those trees.
- **40** executions use PR628's actual rounded leaves and dense exact inverse
  oracle, at 5, 8, 17, 23 and 31 factors. The complete new call count determines
  precision. All three array
  scans per leaf are charged. Source and scratch restoration are exact.
- **11** negative controls cover impossible scratch budgets, omitted
  restoration, factor reordering, a false inverse, an understated bill, phase
  aliasing, insufficient scratch and a missing factor.

The finite search stops after this whole rectangular domain and the explicit
small-tree enumeration. There is no random search or unchecked solver output.
Seed 71 controls only the nonlinear test data. The result is not a proof that
no other algorithm can use fewer calls. The written induction, rather than
finite replay alone, establishes the recurrence for the admitted class.

## Complete price and inherited obligations

Planning costs `O(s n^2)` arithmetic operations and `O(s n)` scalar table
entries. It is paid explicitly. The resulting tree has `O(n)` scalar records;
the instruction generator streams its calls. A finite call reduction does
not remove that planning cost or establish a faster all-size algorithm.

Every primitive retains its source access, three array scans, phase and
coefficient preparation, arithmetic scratch, routing and inverse work.
The complete error budget is `N a (D+1) 2^-w G^(N-1)` with the actual new `N`.
Rounded outputs may differ between schedules. Their equality is not claimed;
the inherited error and exact restoration contracts are checked instead.

The factor lists are valid leaf-interface fixtures. They are not claimed as
prime-power inversion instances or measured supplier costs.

This package supplies no current multiplication supplier or new kappa. It does
not overcome PR673's later unfavorable integration bill. Common-label
realization, reversible bit arithmetic, physical hosting, all-size compilation,
transform layout, full-transform composition, tape bounds, precision recovery
and analytic transfer remain open or inherited assumptions. No selected
frontier, existing generator, or `upstream/` file changes.

## Sources, overlap and attribution

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The accepted conditional kappa at this base is unchanged:
`51110230636731/31250000000000000`.

- [PR673](https://github.com/CrocSwap/integer-mult-bounds/pull/673), androolloyd,
  at `0e35f56cab3cae1eb0a99447135569d687c5695a`: multiway echo, its identity,
  rounded error argument and phase-alias guard.
- [PR689](https://github.com/CrocSwap/integer-mult-bounds/pull/689), Dillon
  Amburgey, at `0dedef12f05f9a06faf9d4e1c8b1462c0e3bff3a`: optimal balanced
  ternary baseline and independent symbolic/rounded evidence. Its actual
  resource function is used for the comparison. It explicitly excludes
  unbalanced splits, which are the new search class here.
- [PR628](https://github.com/CrocSwap/integer-mult-bounds/pull/628), Chafik
  Boukhalfa / chafreaky, at `0768f97d06c623b8211e651543c66135796b62bf`:
  rounded leaves, dirty composition, dense oracle, and retained source notices.
- PR663 independently audits binary counts. PR621 supplies the underlying
  cyclic-kernel work. Their attribution and the classical-source lineage
  remain in the predecessor notices.

`SOURCES.json` binds every vendored file. `CLAIM.json` records OS-random
assignment seed 71, the candidate tasks, and the single evidence-driven pivot.
The first balanced-placement investigation overlapped with the newly published
PR689. It is archived locally and is not submitted as a new discovery. This
submission concerns the fixed-space optimum over unbalanced trees.

There was no pinned sprint coordination issue. The claim and result are local.
The source PR673 later gained a separate integration audit; this package pins
its original echo code and does not claim to verify that later addition.
The final overlap check through PR734 also distinguishes
[PR714](https://github.com/CrocSwap/integer-mult-bounds/pull/714), at
`efad8a40094ab453c0525efef0b0eff2a5d8b850`. That work spends a clean root array
and retains binary children. This audit permits arbitrary dirt in every
borrowed array and uses the stated ternary tree class. No PR714 code is used.

Concurrent [PR730](https://github.com/CrocSwap/integer-mult-bounds/pull/730),
Sagar Thakrar, at `d222e348179cc02a54d6d26dbd2838944f62c6e5`, appeared before
submission. It allows general binary and ternary nodes and unequal prices.
That class is broader than this audit's class. For example, its pinned
optimizer gives 464 calls at 27 factors and six arrays; this audit's exact
ternary minimum is 512. The smaller mixed-tree value was reproduced locally.
No broader optimality or priority for unbalanced trees is claimed here.
The additional evidence here is the full 2,673-state ternary table, all 606
literal resource witnesses, enumeration of 105,980 small trees, and 40 actual
PR628 rounded-leaf executions. PR730 does not supply those numerical leaf
executions. No PR730 code is included or required by this package.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Predecessor notices remain byte-exact. No human peer review, proof-assistant
formalization, or literature-priority claim is made.
