# Exact cleanup envelope for R420 quad 4

**Research note: a finite secondary-cost enumeration. No new \(\kappa\) claim.**

This package enumerates the reverse-positive cleanup maps of every minimum-length positive-addition factorization of the fixed six-register transfer improved in PR1058. The predecessor minimizes gate count (11) and provides a complete inverse-subtraction DAG. This note asks a different question: among those 11-gate words, what is the exact range of worst-case cleanup amplification?

The existing word has maximum cleanup row sum 11. Two other shortest words attain 9, the minimum in the shortest-word class. Thus the best unit-bound local cleanup envelope falls from 11 to 9, with all six inputs still represented by the same exact integer matrix and with the same 11 ADDs.

## Reproduce

From the repository root, with Python 3.9 or later and only its standard library:

```sh
python3 -B research/r420-quad4-cleanup-frontier/analyze.py
```

The command recomputes the DAG and all shortest paths, checks the complete state-distance digest and counts against the pinned PR1058 receipt, replays all 1,768 forward witnesses and their cleanup matrices, checks the entrywise inverse lower bound and two malformed-word controls, and prints the complete five-matrix envelope. Its summary includes:

```text
PASS_R420_QUAD4_SHORTEST_CLEANUP_ENUMERATION
DAG: 165828 states, 917020 legal edges, digest 4e95faed51dc4f9477e488a665f9afed983dc5d2d4156812096aca3e1b222211
shortest paths: 1768; distinct cleanup matrices: 5
maximum-row-sum counts: 9 -> 2 matrices, 11 -> 1, 15 -> 2
```

`RESULT.json` is the captured deterministic output. `SOURCES.json` records the base, predecessor head and SHA-256 pins for every frozen source input. `analyze.py` checks those pins before using the inputs. No installed package, network access, solver or random search is used.

## Object and method

The ordered registers are the six listed in the pinned `PR1058-CIRCUIT.json`. Each forward gate has the form `r[dst] += r[src]`, with `dst != src`; arithmetic is over the nonnegative integers. There are no extra registers, permutations or subtraction operations. The target is the exact forward integer matrix in the predecessor receipt.

For a cleanup matrix \(Q\), its row sum \(\sum_j Q_{ij}\) bounds output register \(i\) when each entering dirty-register magnitude is at most one. The maximum row sum is therefore the induced infinity norm and the worst local coordinate amplification for a unit bound. The code derives the inverse-subtraction distances for every reachable matrix, checks all 165,828 states and 917,020 edges against the predecessor's committed histogram and digest, and follows every edge that decreases distance by one. This yields all 1,768 shortest factorizations. It groups them by exact reverse-positive matrix; no paths are sampled or pruned.

For every shortest word, the entrywise absolute inverse of the target is also checked to be no larger than its positive cleanup matrix. This gives a universal lower bound for the broader positive-factorization class, but its maximum row sum is 7, so it does not prove that 9 is optimal among longer words. The exact optimum of 9 is only over the 11-gate shortest-word class.

## Complete envelope

The columns below are cleanup row sums in the original six-register order. Multiplicity counts distinct shortest operation words, not just different matrices.

| Maximum row sum | Cleanup row sums | Shortest words with matrix |
|---:|---|---:|
| 9 | `[2, 9, 3, 7, 5, 2]` | 630 |
| 9 | `[2, 9, 5, 7, 3, 2]` | 630 |
| 11 | `[2, 11, 3, 9, 3, 2]` | 504 |
| 15 | `[2, 15, 3, 13, 7, 2]` | 2 |
| 15 | `[2, 15, 7, 13, 3, 2]` | 2 |

The full six-by-six matrices and one forward word for each matrix are in `RESULT.json`. The selected best witness uses seed 16 to break the tie between the two maximum-9 row-sum profiles by checking registers in order `[4, 5, 0, 1, 2, 3]`. Its forward word in zero-based register indices is `[(1,3), (3,4), (2,5), (3,2), (0,3), (1,0), (5,1), (4,5), (4,3), (2,3), (2,1)]`. It keeps the same 11-operation length and exact forward transfer. The negative controls remove the last gate or change the first source; neither reaches the target.

## Scope and unresolved obligations

This is a finite exact statement about one local transfer and positive ADD words of minimum length. The code verifies the integer transfer, not the bit circuit's full frame schedule or whole-word native accounting. It does not show that replacing the word lowers a selected certificate's paid bill or changes \(\kappa\). The absolute-inverse lower bound leaves open whether a longer positive word can attain maximum row sum 7 or 8; signed circuits, extra workspace and alternate integer lifts are outside the search. The selected frontier and all inherited supplier and assembly assumptions are unchanged.

## Provenance and attribution

Base commit: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`. The fixed circuit and its complete minimum-length DAG come from PR1058, head `d148d200f2d64c90504fa3a9608e455aaa4c0c21`. The package preserves those inputs as byte-pinned copies; it does not modify the predecessor files. The PR1058 quad construction and its attribution remain with Chris Barber (@cbarber1), with substantial OpenAI Codex assistance, as recorded in the predecessor notice. This secondary enumeration is also by Cinna Davis with substantial OpenAI Codex assistance; no independent human review is claimed. The repository's Apache-2.0 license is included.
