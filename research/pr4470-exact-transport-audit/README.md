# Exact physical transport audit of PR4470

This source-bound audit checks all 423 declared transport/helper-boundary pairs in PR4470 at `b9a13c1673e0e9697de410de16e8bbf3207a7363`. It claims no new kappa. The selected result and frozen scientific predecessor files are unchanged.

The separately written checker reconstructs the reference frame catalogue and compares every entry of each 512 by 512 lowered matrix against the literal Gaussian-dyadic reference operator, in both orientations. It uses int64 Gaussian numerators and explicit powers-of-two denominators, not floating-point tolerances, predecessor interpreters, Clifford tableaux, or a zero-column-only phase comparison. A 28-Gaussian-gate cap keeps all arithmetic and squared magnitudes within int64.

## Verification and reproduction

The first complete hosted scientific replay passed in [run 39712725621](https://github.com/Clear1nsight/integer-mult-bounds/actions/runs/39712725621) at `f4657a0ad4c11a56646c8c6c422f09335b0c73ba`, with Python 3.12 and numpy==2.2.6. RESULT.json is the byte-exact downloaded receipt, SHA256 `53bdd869ebeee0980b139e422043922c87585bef90c2989969532ccb7b289a00`. It records 433,152 basis columns and 221,773,824 complex matrix entries compared, 196 positive self-checks, seven rejection controls, a tensor-phase control, and an actual-source phase mutation that preserves rank but fails equality.

The earlier shared package plan failed four stale status/navigation assertions. The focused scientific pass was not a shared-CI pass. The separate [CI repair note](../../docs/research/pr14-ci-repair.md) records their correction without changing mathematical tests, selected records or frozen receipts. Exact-head hosted results must still be read from the PR checks.

From a full checkout with Python 3.12:

```sh
python -m pip install numpy==2.2.6
python -B scripts/research_package.py --package research/pr4470-exact-transport-audit --check-only
python -B scripts/research_package.py --package research/pr4470-exact-transport-audit
python -B scripts/check_research_commit.py --package research/pr4470-exact-transport-audit --check-source-history
```

The registered replay freshly runs the unchanged scientific engine and compares every receipt field, then runs optimised scientific controls and five receipt-binding tests in normal and optimised modes. No runtime metadata is part of the scientific receipt. The source/receipt comparison rejects extra and missing fields and distinguishes booleans from integers. The five new wrapper tests passed locally on Python 3.13.5; registered Python 3.12 coverage is provided by the actual hosted job.

A Git-free scientific replay is also available:

```sh
python -I -B research/pr4470-exact-transport-audit/replay.py
python -I -O -B research/pr4470-exact-transport-audit/verify.py --self-test
```

SOURCES.json pins the four source exports to this fork's existing ancestor commit, so no unmerged foreign commit is needed. The original upstream identifiers and contributor notices remain in vendor/NOTICE.md. TASK.json preserves the original catalogue card and declares the narrowed scope.

## Scope boundaries

A passing full replay verifies the listed physical normal forms and their declared ranks/phases. It does not prove that the 423-pair list is exhaustive for the chronological word, replay the 632 persistent-field endpoint, admit the p16 controller, price physical movement, or establish precision, storage, and the outer multiplication theorem. Tensoring a checked operator identity preserves that identity for each positive column multiplicity; it does not by itself price the lifted implementation.

## Task and overlap

The scientific base remains canonical main `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7. Current main was refreshed to `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc` during the workflow repair. The assigned PR4470 native audit refines independent-moment to physical operators rather than another root enclosure. PR4478 covers arithmetic, compiler and outer rows. PR4457 audits predecessor operators. PR4464/4466 cover stage-zero commutation. PR4504 independently reconstructs chronological frames and local billing, but leaves physical operators separate. This is targeted overlap coverage, not exhaustive novelty. The newer PR4483 compiler does not discharge this physical premise.

## Open next questions

First bind every chronological transition and helper endpoint from PR4504's independent reconstruction to the audited pair set, using canonical subspaces and orientation rather than raw frame IDs. Reject an omitted pair, a wrong orientation, and an unpriced transition. Then replay all 632 arbitrary persistent inputs and the owned centre under the assembled physical contract. A separate follow-up checks the actual p16 query/owner/erasure protocol. TASK.json gives the relevance, first step and blockers for both tasks. No new agent is claimed to have run these follow-ups.

## Credit

Prepared for Chris / Clear1nsight with substantial OpenAI assistance, Apache-2.0. This is separately implemented AI-assisted checking, not independent human or proof-kernel verification. Credit Cinna Davis for PR4470; zxv for receiver sharing, native/controller/compiler work and the reused PR4436 navigation repair; Jacob Alan Sussman for mixed-target recursion; Mark / Matarener for PR4457; Mihir Srivastava for PR4504; Ryanson Jonathan for PR4478; and the full retained notices in vendor/NOTICE.md. The historical CI adapter preserves James Reed's PR3563 result and the existing locale checker rather than silently updating their evidence.
