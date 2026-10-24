# Batch-sensitive integer widths for the finite mixed compiler

This package proves a scoped integer-replication and bit-length lemma for the finite Theorem 1G flow. It supplies exact symbolic recurrences for productive arrays, paid rank-one calls and fully expanded unit-instance multiplicity. The calibration unit is explicitly **toy algebraic data**, `W={3:1,4:1}` with ordered paid ranks `(1,2,2)`; no native implementation is claimed.

For each fixed complement or ordered exit batch of t jobs using a smaller program of width B_q, the least clearing factor is `B_q/gcd(B_q,t)`. Taking the lcm of those factors is necessary and sufficient for that fixed batch partition. The inherited sufficient `lcm(B_q)` can over-replicate: in the actual toy N=22 flow it gives 40, while the batch-sensitive recurrence gives **a=20, B=80, O=229**. At N=25 the largest required individual factor is 16 but the lcm is **80**, so replacing lcm by max fails. Repeated equal-rank exits cannot be merged: at the actual N=12 exit phase that would incorrectly reduce the clearing factor from 2 to 1.

[PROOF.md](PROOF.md) gives the exact missing-demand source formula, minimality, integrality, owned-instance recurrence and uniform upper bounds on integer bit length. The inherited Section-3 flow has one unit per deepest class, so each ordered exit batch has t=1; source-complement multiplicity is the source of the demonstrated reduction. This is a finite size result, not a new ambient-rank certificate, κ, physical allocator or complete multiplication theorem. The selected conditional κ=0.00302015 is unchanged.

## Evidence

[RESULT.json](RESULT.json) records every rank N=4,...,25. First non-base fixtures give `(B,P,O)=(2,6,1)` at N=4 and `(2,8,1)` at N=5. N=12 has sources `{4:1,8:2,9:1,12:1}`, a nonzero complement, distinct child widths 1,2,4 and nine ordered exits. A second independent construction enumerates literal target-role words and actual parent-to-child slots; its complete source counts, ordered exits and unit counts agree. A target multiplicity W_3=2 fixture exercises the Pascal role factors independently of the primary toy.

The verifier checks all batch divisibilities, the normalized leaf identity, literal allocated-instance counts and recursive/closed bit bounds. Semantic controls reject an omitted complement at N=7, max in place of lcm at N=25, coalesced chronological exits in the N=12 exit phase, violated separation and an excessive fixture rank. No check relies on Python `assert`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/symbolic-integer-batch-width/verify.py
python3.12 -O -B research/symbolic-integer-batch-width/verify.py
python3.12 scripts/research_package.py --package research/symbolic-integer-batch-width
```

[SOURCES.json](SOURCES.json) pins the actual owning source note and net-tax proof at canonical base `4c0a359d88f22f05189d51f48387750b801a45d4`. The verifier checks their byte hashes; the registered runner additionally checks catalogue provenance. All finite experiments used Python 3.12 through the shared serial runner. No Lean, Docker, full suite, selected native replay, astronomical-rank evaluation or physical timing was run. Arithmetic-operation counts are distinguished from integer bit complexity; the loose bound is not a wall-time forecast.

## Scope and proof obligations

[TASK.json](TASK.json) preserves the assignment and change of premise. Only this new package changes; there are no existing callers, exports or configurations to update. This work retains the all-column native word, arbitrary-input/spectator, whole-job adapter, chronological restoration, owned erasure and finite-closure assumptions. Counting unit instances does not prove a per-instance bank budget, address extent, field precision or fixed-tape movement cost. The raw toy rank invoice is separated but has no admitted native word, and no tau-root or saving is asserted for it. The full coefficient/storage/precision substitution and outer multiplication theorem remain open.

The new verifier's contract is batch integrality and the finite flow's source/chronological inventory. Its credible regressions are omitted complements, illegal rank-wise exit pooling and incorrect lcm reduction. Existing source prose does not check this batch-sensitive width recurrence; the independent role-word oracle is its primary finite check. No production API, flag or export was introduced for tests.

## Open next questions

Bind the same recurrence to one actual small admitted separated native unit and an explicit per-instance owned-bank inventory. That would turn the toy calibration into a source-specific finite width/bank bound. Start with its exact ordered paid rounds and native target roles; the missing blocker is an independently established tiny native supplier, not more numerical precision on these fixtures. Full details are in `TASK.json`.

## Credit

Jacob Alan Sussman supplies Theorem 1G and its finite integer flow. zxv supplies the higher-moment and net-tax compiler lineage; Cinna Davis and the native contributors supply chronological product and completion work. Mark/Matarener's ownership audit and JoyboyBrian's source-binding work identify separate physical obligations; this package does not repeat or claim to discharge them. New proof and code: JoyboyBrian with substantial OpenAI Codex assistance, Apache-2.0. The original source files and notices remain unchanged.
