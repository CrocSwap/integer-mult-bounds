# Navigation receipt: pinterbanget's 37 PRs of 2026-10-22 (#4513–#4591)

**Task:** overlap-receipt (consolidation). **Base:** canonical main `f626db5c`. **No new κ. No closures recommended.**

This maps the 37 open PRs I opened in one donated session (03:03–11:03 UTC) up to 08:45 UTC. It gives each PR's subject, type and head, and the edges that matter when merging. Exact heads and packages are in `RECEIPT.json`. Every PR is a single-purpose `research/` addition, except the #4547 repair.

## Merge-relevant edges

- **Rank chain for #4535 (same κ).** #4563 (13× smaller frozen rank) → #4564 (outer slack `d = 10^−12`, 34×) → #4565 (retuned majorant, 85×). #4565's verifier reproduces #4563's and #4564's ranks as controls, and #4564 reproduces #4563's. If only one is wanted, #4565 carries all three numbers.
- **#4568 (hexapode, κ = 0.00302016597)** builds on #4564. #4570 checks #4568's arithmetic and uses #4565's witness for a 6.9× smaller rank at #4568's κ.
- **#4554 (Dugongue).** Every constructive component has an independent check: #4556, #4557, #4558, #4559, #4560, #4561, #4562 and #4566.
- **#4567 and #4581 (mihir-s-05).** They agree exactly. #4581's all-length terminal profile sets equal #4567's length-≤6 sets in all 128 windows. #4567 additionally covers nonadjacent pairs, coefficients up to ±3 and retiming.
- **#4532.** #4537 (finite figures) and #4569 (written proof, §1.1, §2.2–2.3, §3) are complementary. #4591 checks the #4483 Chernoff layer that #4532 inherits.

## All PRs

| PR | type | subject group | what |
|---|---|---|---|
| #4529 | check | #4483 adaptive-height compiler (zxv) | finite gates and arbitrary-height flow |
| #4533 | extension | #4483 adaptive-height compiler (zxv) | sharper certified witnesses, same kappa |
| #4551 | check | #4483 adaptive-height compiler (zxv) | of #4544's audit of #4483's cancellation step |
| #4591 | check | #4483 adaptive-height compiler (zxv) | identity (2) and Chernoff bounds (7)-(9) on actual flows |
| #4537 | check | #4532 critical-root theorem (Dillon) | finite figures |
| #4569 | check | #4532 critical-root theorem (Dillon) | written proof of sections 1.1, 2.2-2.3, 3 |
| #4536 | check | #4535 / #4568 conditional kappa (hexapode) | #4535 arithmetic |
| #4563 | rank | #4535 / #4568 conditional kappa (hexapode) | 13x smaller frozen rank, same parameters |
| #4564 | rank | #4535 / #4568 conditional kappa (hexapode) | outer slack d=1e-12, 34x smaller rank |
| #4565 | rank | #4535 / #4568 conditional kappa (hexapode) | retuned majorant, 85x smaller rank; controls reproduce #4563/#4564 |
| #4570 | check | #4535 / #4568 conditional kappa (hexapode) | #4568 arithmetic; 6.9x smaller rank with #4565 |
| #4516 | check | #4470 p16 supplier (Cinna Davis) | controller replay |
| #4567 | negative | #4470 p16 supplier (Cinna Davis) | local improvements closed: 128 windows, 88 nonadjacent, |c|<=3, retiming; agrees with #4581 |
| #4539 | check | #4534 noncommuting controller (Dugongue) | free-algebra replay |
| #4540 | extension | #4534 noncommuting controller (Dugongue) | all p <= 14 via support-injectivity lemma |
| #4549 | extension | #4534 noncommuting controller (Dugongue) | all-p descending-support invariant |
| #4556 | check | #4554 native Gaussian adapters (Dugongue) | banded inverse |
| #4557 | check | #4554 native Gaussian adapters (Dugongue) | native FFT multiplier |
| #4558 | check | #4554 native Gaussian adapters (Dugongue) | root seeds and recovery |
| #4559 | check | #4554 native Gaussian adapters (Dugongue) | phase and exp tables |
| #4560 | check | #4554 native Gaussian adapters (Dugongue) | Gaussian chirp blocks |
| #4561 | check | #4554 native Gaussian adapters (Dugongue) | outer assembly and recount |
| #4562 | check | #4554 native Gaussian adapters (Dugongue) | native stability lowering |
| #4566 | check | #4554 native Gaussian adapters (Dugongue) | linear-program lowering |
| #4552 | check | #4538 / #4541 Word RAM transfer (Dugongue) | #4541 parameters and macro steps |
| #4553 | check | #4538 / #4541 Word RAM transfer (Dugongue) | #4541 packed IO codec |
| #4555 | check | #4538 / #4541 Word RAM transfer (Dugongue) | #4538 cost theorems 1-4 |
| #4513 | check | #4505 / #4510 / #4518 native splices and gauges (Dugongue) | #4505 adapter recount |
| #4514 | check | #4505 / #4510 / #4518 native splices and gauges (Dugongue) | #4510 suffix bounds |
| #4522 | check | #4505 / #4510 / #4518 native splices and gauges (Dugongue) | #4518 Levi gauges |
| #4519 | check | #4507 / #4586 batch widths (mihir-s-05) | #4507 widths |
| #4588 | check | #4507 / #4586 batch widths (mihir-s-05) | #4586 growth lemmas |
| #4589 | check | Other independent checks | #4580 p3 H-branch budget (Matarener) |
| #4590 | check | Other independent checks | #4583 union header (mihir-s-05) |
| #4517 | extension | HALO chain | core-row operator lift answering #4515 |
| #4550 | receipt | HALO chain | jwr404's 13-PR chain |
| #4547 | repair | Repairs | portable replay of 21 earlier packages |

## Verify

```text
python3 -B research/session-receipt-20261022/verify.py
```

The verifier checks internal consistency only:
- full-SHA heads and distinct PRs;
- distinct packages across PRs;
- a fixed type vocabulary;
- internal edges among listed PRs, pointing back in the rank chain;
- the #4554 coverage set equal to its group.

It makes no working-tree or network checks, so it replays after any of these PRs merges.

## Limitations

- This is navigation only. It does not re-review any listed PR's mathematics; each PR's own package does that.
- Heads are recorded at 08:45 UTC. Later pushes to a PR supersede the recorded head, and PRs opened after that time are not listed.

## Open next questions

- None. Each listed PR records its own open questions.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
