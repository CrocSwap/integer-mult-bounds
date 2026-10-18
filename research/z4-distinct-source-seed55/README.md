# Phase-indexed order-four echo across distinct sources

**Scoped recursive-interface construction; no new κ or supplier admission.** This package extends the order-four five-child interface of PR #1391 and the same-source, two-root composition of PR #1410. It composes two five-child calls on independent source banks while preserving an arbitrary dirty output and restoring both sources and workspace.

Research base: `4040a0f46d67b41c36a472a7cd4af791fd4c36cc`. Exact PR #1391 and PR #1410 dependency heads and content pins are recorded in [SOURCES.json](SOURCES.json).

The main construction indexes each child's output reader by the carried workspace phase. If the original child reads through `R_i` and advances workspace by `P`, define

```text
C_(i,t)(D,W) = (D + Q^(-t) R_i W, P W),    t in Z/4Z.
```

When `W = P^t w`, the child contributes the original `R_i w`, since `Q^(-t) R_i P^t = R_i`. The typed reader is an eight-row signed selector: it changes which output register each ADD targets while retaining the child's eight ADDs and its 24-coordinate `P` update. This is an explicit change to the child contract.

## Exact boundary recurrence

The pinned predecessor has 24 workspace coordinates. The complete `P^r` gate vectors are

| `r` | ADD | NEG | Total |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 |
| 1 | 54 | 6 | 60 |
| 2 | 36 | 12 | 48 |
| 3 | 54 | 6 | 60 |

Let `A(r)` be that vector. With starting workspace phase `t`, the entry charge is `A(t)`. After a child at phase `t`, the workspace has advanced once under `P`; reaching the next phase `s` costs `A((s-t-1) mod 4)`. The exact recurrence is

```text
F_0(t)       = A(t)
F_(j+1)(s)   = min_t [F_j(t) + A((s-t-1) mod 4)]
g(k)         = F_k(0)
```

The verifier compares this recurrence with every path for the two fixed sizes: all 1,024 five-child paths and all 1,048,576 ten-child paths. The exact minima are:

- `g(5) = (54,6)`, total 60, on phases `[0,0,1,2,3,0]`.
- `g(10) = (36,12)`, total 48, on phases `[0,1,0,1,2,3,0,1,2,3,0]`.

Let `T_i=(62,6)` be the complete forward cost of child `i`, including its eight data ADDs and 24-coordinate workspace update. The paired child body and literal inverse contribute `2 sum_i T_i`. For one source, the source copy and reset cost `2d` ADDs; for two sources, the entry copy, two-sided handoff, and exit reset cost `4d` ADDs, where `d=24`. The complete cost recurrences are

```text
E_1(k)       = 2 sum_(i=1..k) T_i       + (2d,0) + 2 g(k)
E_2(k1,k2)   = 2 sum_(i=1..k1+k2) T_i   + (4d,0) + 2 g(k1+k2)
```

The inverse uses the same exact phase word in reverse and has the same ADD/NEG vector. These equations include every child, source update, phase change, and restoration charged by this finite interface.

For the two-source call, the ten-child path is at phase 3 after the first five children. At that point the workspace contains `P^3(W+X)`. The handoff applies `P^3(Y-X)`, using two ADDs per each of 24 coordinates, for 48 ADDs. The second five children then read `Y`. The complete word is

```text
W += X
phase-typed 10-child forward body, with W += P^3(Y-X) after child 5
W -= Y
literal inverse of the no-handoff 10-child body
```

The resulting map is

```text
(D,X,Y,W) -> (D + sum_(i=0..4) R_i X + sum_(i=5..9) R_i Y, X, Y, W).
```

All 80 basis columns (8 output, 24 coordinates in each of `X`, `Y`, and `W`) are checked exactly. The two source banks are read-only, and arbitrary initial values in all four banks are allowed.

## Complete invoice

The joint typed invoice is

```text
20*(62,6) + (96,0) + 2*(36,12) = (1408,144)
```

for 1,552 primitives and 2,960 data reads. Two separate calls using the same typed child family cost

```text
2 * [10*(62,6) + (48,0) + 2*(54,6)] = (1552,144)
```

for 1,696 primitives and 3,248 reads. The joint typed call saves **144 primitives and 288 reads**. Its exact prefix row-L1 peak is 21, compared with 16 for the two separate typed calls; this is a coefficient-width cost that could affect fixed-precision admission.

For comparison, the unchanged-reader interface from PR #1410 also composes across two distinct sources when charged with the same 48-ADD handoff. Its exact joint invoice is 1,952 primitives versus 2,016 for two separate original calls, saving 64 primitives and 136 reads. Its prefix row-L1 peaks are 42 joint and 30 separate. This is a matched same-contract construction; it is not included in the typed-call saving above.

## Reproduction and evidence

From the repository root, with CPython 3.12:

```sh
python3.12 scripts/research_package.py --package research/z4-distinct-source-seed55
```

Expected verifier marker:

```text
PASS_Z4_DISTINCT_SOURCE_PHASE_TYPED_ECHO g5=60 g10=48 separate=1696 joint=1552 saved=144 reads_saved=288 paths=1024+1048576 basis=80 controls=5
```

The registered replay checks the base and predecessor pins, all twelve `(phase, reader)` identities, unchanged child ADD/NEG counts, both complete 80-column maps, every phase path at both sizes, exact ADD/NEG/read invoices, prefix row-L1 peaks, and five negative controls. The exact evidence is frozen in [RESULT.json](RESULT.json).

## Scope and limits

The phase recurrence is exact for the stated phase-indexed order-four child alphabet. It is not a lower bound for arbitrary ADD/NEG programs. Output-row reindexing is encoded by the static target of each ADD and costs no additional scalar ADD/NEG instruction in this word model. Address calculation, physical row routing, source hosting, tape travel, fixed-precision admission, recursive assembly into a selected supplier, and analytic transfer remain unproved. The row-L1 increase makes precision a live obligation. The selected result at the pinned base remains κ = `836330098538459/500000000000000000`; this package does not change it or claim a new κ.

## Overlap check

The live refresh found several adjacent connector results. PR #1158 gives an exact readout-price census for a four-source/four-output Hadamard connector. PR #1438 and Cinna Davis's Discussion #1412 study a second arbitrary-dirty root and paid full-row transfers for universal five-source masks. PR #1439 studies a persistent `z = z_initial + Bx` boundary across a paid source mutation `x += Cu`, correcting it by `z += BCu`; PR #1442 proves a weighted query optimum under chronological output-delivery cuts. Here the interface keeps one 24-coordinate dirty workspace and changes between two read-only source banks by the explicit 48-ADD delta `P^t(Y-X)` inside a fixed five-child echo. Its separate evidence is the order-four phase-indexed reader identity, exhaustive five- and ten-child recurrence, and complete arbitrary-dirty two-call map/invoice, not a four-source Hadamard census, two-root transfer bound, general mutable-source connector theorem, or delivery-cut optimum. We make no priority claim for those connector mechanisms and retain their distinct scopes.

## Open next questions

Does a named selected supplier realize all four phase-indexed signed target rows with the charged handoff and no binding routing or precision cost? This matters before the operation saving can alter a multiplication profile. First inspect one retained #1094 child matrix and test `Q^(-t) R_i P^t = R_i` for every phase, then price target routing and the prefix envelope. The blocker is that no physical host, tape schedule, or precision-admitted supplier for this paired interface has been identified.

## Credit and license

This work builds on Cinna Davis's PR #1391 order-four child family and PR #1410 same-source persistent boundary, and retains their attribution. Those results extend Ross Richardson's PR #1287 and Sagar Thakrar's PR #1227. The selected-result context is Rohan Arun's PR #1094 on Jeremy Kothe's #1087 construction. The exact PR #1391 certificate and verifier snapshots are preserved under `inputs/PR1391/`; the direct PR #1410 README snapshot is pinned under `inputs/`. See [NOTICE.md](NOTICE.md) for source heads and snapshot hashes.

The overlap review also credits Cinna Davis's PR #1158 for an adjacent four-source Hadamard connector census, woklerx's PRs #1438, #1439, and #1442, and Cinna Davis's concurrent Discussion #1412 for distinct two-root, mutable-source, and chronological-delivery models.

Prepared by **Cinna Davis** with substantial **OpenAI Codex assistance** in derivation, implementation, exact verification, source pinning, and prose. No independent human review or proof-assistant formalization is claimed. New material is Apache-2.0; the project license is retained.
