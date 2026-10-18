# Exact tri-plane pairing factorization for selected P112

**New algebraic decoder mechanism; no new supplier or kappa.** Submitted as [PR #2041](https://github.com/CrocSwap/integer-mult-bounds/pull/2041). This package replaces the matched rank-2 grouping with 37 mutually orthogonal 3-planes and one residual line for the exact 112 selected PR1094 labels. The resulting F2 factorization reproduces the complete selected pairing matrix. Its B14 copied-information invoice is 85, down from 126 for the known matched 2-plane factorization.

The construction does not meet the `a = 1/99` planning target even under the favorable three-unpaid-coordinate coverage law. Its exact fixed-word ceiling is `a = 0.010012347901`, just below `1/99`; the local `kappa` planning cap is `0.009913094550`. The screen assigns all idle mass optimistically at rank 51 and omits the physical tri-plane route, endpoint-translation multiplicity, hosting, frame/restoration schedule, precision and bit-side assembly. Those costs can only lower the attainable ceiling. No selected result, supplier or multiplication bound changes.

## Exact construction

The pinned source archive gives 112 distinct vectors `q_i` in `F2^9`, with weights 3 or 7. The bounded search enumerated 24,416 linearly independent triples that are pairwise orthogonal. With port 0 held as the residual line, deterministic MRV exact cover produced 37 disjoint triples. For each triple `t`, its columns form `A_t`; the residual line is `A_0`. The exact system

`sum_t A_t M_t A_t^T + A_0 M_0 A_0^T = I_9`

has rank 81 over 334 binary variables. The stored solution has 32 zero blocks and six nonzero blocks with rank histogram `{1:2, 2:3, 3:1}`. Factoring those six matrices into rank-one terms yields 11 terms. Recomputing the B14 support-pair ranks gives `{7:3, 8:8}`, for total copy charge 85. The verifier reconstructs both the 9-by-9 identity and the full 112-by-112 selected pairing matrix.

For each active block with orthogonal basis labels `q_i`, define `C_E` as the product of the commuting lifts `C_q`, where `C_q^2 = X_q`. The exact dirty endpoint is `C_E^2 = X_(xor_i q_i)`. The verifier checks this Gaussian-dyadic identity on all 512 address basis states for each of the six active blocks: 3,072 cases total. This proves the correction-operator identity for arbitrary superpositions by linearity. The source-to-target tri-plane call itself and its schedule across hosted families are not implemented here.

## Paid local screen

The exact local profile is `{1:2412, 2:418, 3:432, 4:142, 5:82, 7:3, 8:8}`. It retains the selected word's non-centre profile and charges all 85 copied-information ranks as recursive children. With `m=73`, `w=896/9`, nine stages, idle rank cap `R=51`, and three unpaid coordinates, the idle mass is `13022/9`. At `a=1/99`, the exact rational relaxation is greater than one (`1.0002651999055365`). The certified ceiling is below the target, so this candidate cannot deliver the target even before its unimplemented physical route and precision/interface costs.

This is an algebraic decoder invoice, not a complete supplier bill or a verified physical realization of the proposed source `E -> FULL` / target `0 -> E^perp` contract. The labels are read from the pinned selected archive; there are no added helpers or basis rotations inside each orthogonal triad. The correction translation is verified algebraically, while the full port operation, its application multiplicity, hosting, restoration, frame routing and precision remain outside this mechanism-level budget. The result is therefore evidence for a cheaper exact pairing factorization and an honest scoped miss, not an integrated construction.

## Search scope and stopping rule

`search.py` fixes residual port 0, enumerates triples in deterministic MRV/tuple order, and examines at most 10,000 exact covers. For each cover it uses the specified column-echelon solution (free coefficients zero), factors the resulting block matrices, recomputes every B14 support rank, and screens the exact local profile. The completed search examined 10,000 covers and found no candidate better than the first witness under that deterministic solver. It is **not** a lower bound over other residual ports, other coefficient solutions of the same linear systems, non-orthogonal subspaces, or other endpoint contracts. No universal impossibility claim is made.

## Reproduce

Run the exact certificate check (about 4 seconds on the recorded environment):

```sh
python3 -B research/tri-plane-port-p112-seeddb093026/verify.py
```

Expected marker:

```text
PASS_TRI_PLANE_FACTORIZATION_P112 triples=37 terms=11 copy=85 profile={1:2412,2:418,3:432,4:142,5:82,7:3,8:8} endpoint_cases=3072 moment_upper=1.000265199905537 a_cap=0.010012347901 target=FAIL controls=4
```

Reproduce the bounded search (about 15 minutes on the recorded environment) with:

```sh
python3 -B research/tri-plane-port-p112-seeddb093026/search.py --cover-limit 10000
```

Then run the package metadata check and registered Python 3.12 replay:

```sh
python3 scripts/research_package.py --package research/tri-plane-port-p112-seeddb093026 --check-only
python3.12 scripts/research_package.py --package research/tri-plane-port-p112-seeddb093026
```

The registered replay checks the saved exact factorization and controls; it does not rerun the 10,000-cover search. Exact selected source, predecessor and base pins are listed in `SOURCES.json`, `TASK.json` and this note.

## Predecessors, scope and credit

The proposed three-unpaid-coordinate contract is a refinement of the `coverage-law-change` card; its complete physical implementation remains open. Discussion [#1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587) established the exact 2-plane endpoint and framed the 2-plane decoder problem. Merged [PR #1825](https://github.com/CrocSwap/integer-mult-bounds/pull/1825) supplies the symmetric matched 2-plane P112 factorization and its copy invoice 126; this package changes the port dimension and the global block factorization. Open [PR #1900](https://github.com/CrocSwap/integer-mult-bounds/pull/1900) uses five planes on the different P111 bit decoder. The selected PR1094 labels and their authors retain attribution through the exact source pins.

Prepared with substantial OpenAI Codex assistance. No independent human review or proof-assistant verification is claimed. New work is Apache-2.0.

## Open next questions

- Can a different residual port or nonzero free-variable choice lower the exact tri-plane invoice enough to pass `a=1/99`? This matters because the completed 10,000-cover search misses by a small amount; first optimize the 334-variable F2 solution against the exact B14 support-rank objective. The current search's fixed zero-free-variable solver is the blocker.
- Can a physical selected-word schedule realize the six active tri-plane endpoint translations with charged hosting, restoration and precision? This matters for any supplier claim; first map the six active block endpoints to the pinned T16 frame trace. No such route is part of this package.
