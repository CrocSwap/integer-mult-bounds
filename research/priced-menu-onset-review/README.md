# External audit of the priced-menu period and onset

This is a source-bound written proof and algorithm audit of SHIN09-git's [PR6689](https://github.com/CrocSwap/integer-mult-bounds/pull/6689), head `e90d4e3cb77ed31c259b902e7aad9598c89327b5`. The existing author owns the theorem: the least eventual period of the **total excess** is the least common multiple of `h_j/gcd(h_j,q_j)`, and the first positive replication of that periodic tail is the last unmasked exception plus one. This package checks those implications in PROOF sections 2–3 and their exact implementation in `pricing.py`; it adds external review evidence, not a new period, price instance or multiplication bound.

The domain is a nonempty finite collection of separate completed cuts, positive integer jobs and widths, nonempty finite menus and positive rational additive prices paid per whole invocation. Infinity denotes an infeasible exact fill. Shared setup, pooling cuts, lifetime discounts and unpriced physical movement are excluded by the source contract.

## Evidence and reproduction

Read [REVIEW.md](REVIEW.md) with the inert [source proof](inputs/PROOF.md) and [algorithm](inputs/pricing.py). [SOURCE-PINS.json](SOURCE-PINS.json) authenticates the five retained source files by immutable head, path, Git blob, byte length and SHA256. Retained Python is text for review; it was not imported or executed. No numerical census, native caller, proof assistant or original CI was replayed. There is deliberately no scientific `VERIFY.json` hook. Repository helper/byte checks, if successful, do not prove the mathematics. Code conclusions require a stable list/tuple of valid, unmodified Menu instances; low-level helper preconditions remain explicit.

Separate source-aware written derivation and code-boundary drafts are retained in [reviews](reviews/); their pre-cross-review seals and coordinator reconciliation are recorded in [VALIDATION.md](VALIDATION.md). This is AI-assisted review, not blind, human or kernel acceptance. [TASK.json](TASK.json) records the changed formal-interface card, whose original kernel gate remains unmet. [SOURCES.json](SOURCES.json) retains current-main guidance provenance; pending-source copies are authenticated separately rather than falsely claimed as canonical ancestry.

## Open next questions

- Can a separately budgeted proof-assistant development certify these exact extended-value period/onset statements and their algorithm binding? This would add kernel evidence. Start with the anchor attainment iff, then the nonnegative-defect and last-exception lemmas. No proof environment or formal theorem is supplied here.
- What is a complete physically justified price for the actual compatible programs? It determines whether the source arithmetic menu can be used by a caller. Begin with one literal native/ordinary program, exact endpoint and all movement, storage, ownership, precision and invocation charges. Those source contracts and bills remain missing from this audit; another abstract fee or larger finite census does not fill the gap.

## Credit and limits

SHIN09-git supplies the priced-menu theorem, onset/masking formula and implementation, with disclosed OpenAI Codex assistance. Nick Petalas/PR6658 supplies compatible menus and whole-replication arithmetic. Mihir Srivastava/PR4507 supplies chronological cuts on the retained Jacob Alan Sussman, zxv, codyw912, Cinna Davis and Ryanson Jonathan lineage. Apéry sets, numerical semigroups, equality knapsack and residue shortest paths are classical; the source credits Gilmore–Gomory and Nan Zhu. ToikY prepared this external audit with substantial source-aware OpenAI Codex assistance and separate written review roles. [NOTICE.md](NOTICE.md) and the exact [Apache-2.0 license](inputs/source/LICENSE) preserve source credit.

The full Pareto theorem and rank-12 invoices were not audited. All five selected framework assumptions and native inventory, adapters, owned lifetimes/erasure, compiler, precision/tape, analytic and outer budgets remain. Selected6030, κ `781451/250000000`, and the frontier are unchanged. No adoption or merge is requested.
