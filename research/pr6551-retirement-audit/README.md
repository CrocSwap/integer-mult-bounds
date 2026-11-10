# Independent retirement-cut and invoice audit of #6551

The changed `(7,2,5,4)` caller in Ali Romman's [PR6551](https://github.com/CrocSwap/integer-mult-bounds/pull/6551) passes this independent finite audit against [PR6545](https://github.com/CrocSwap/integer-mult-bounds/pull/6545). The retired output and fresh suffix input are independent, and the complete Gaussian invoice difference is

```text
ΔT = −104 H16 + 104 H40 + 208 H41 − 208 H57
ΔP = −104 H16 + 312 H40 − 208 H56
Δ(T−P) = 208 (H41 − H40 − H57 + H56) > 0,  H_r=r^t, 0<t<1.
```

This resolves the specific independent-review question in PR6551's first Open next question and [handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19367661). The construction, retirement identity and gain belong to the predecessors. This contribution adds separate exact implementations, a different full-endpoint and cut argument, semantic failure controls and explicit review boundaries. It does **not** certify PR6551's numerical κ, admit a supplier, or change selected PR6030.

## Exact scope and evidence

| Check | Evidence |
|---|---|
| Complete old/new caller | [caller.py](caller.py) interprets all 609/611 events and checks all 1,225 transfer coefficients in each 35-input word over `Q(i)[D1,...,D18,q]/(q^4−1)`; no predecessor code executes. |
| Actual retirement cut | The first 345 normalized events are identical, including the original 329-event prefix. Coordinate 4 has row and column `S e4`, where `S=λq⁻¹`; coordinate 34 is untouched. The suffix never uses coordinate 4 except for its final `λ⁻¹` normalization. |
| Different exact endpoint and cut proof | [cut_four_fibers.py](cut_four_fibers.py) propagates all 35 output rows backward through each entire word at `q=1,−1,i,−i`, retaining every stage variable formally: 4,900 coefficient positions per caller. It also checks the retirement row and column. The Chinese remainder argument makes these four fibers exact; [ENDPOINT-REVIEW.md](ENDPOINT-REVIEW.md) records coverage and mutation witnesses. |
| Complete Gaussian delta | [accounting.py](accounting.py) traverses both literal binary trees, endpoint stage supports and every paid caller event. It checks the retained native archive identity and cancels the same 18 native invocations without replaying them. [ACCOUNTING.md](ACCOUNTING.md) gives the derivation. |
| Counts and extra ordinary work | Both constructions have 13,756 productive fields and 67,096 paid Gaussian jobs. Both rank masses fall by 832. Native calls remain 18, thin queries 17, and the only ordinary event-count change is two additional Q_POWER operations. |
| Controls | Eleven primary caller, seven accounting, four cut and four changed-suffix controls reject (26 semantic controls). All four suffix mutants pass the original cut checks and fail the new endpoint calculation. Both actual callers and inverse/canceling identities are positive fixtures. Three further controls check pricing-source pins and clauses. |
| Source tariff binding | Both exact `pricing.py` sources are retained. [PRICING-SOURCE-MAP.md](PRICING-SOURCE-MAP.md) relates the independently derived counts to their declared tariffs; [pricing_binding.py](pricing_binding.py) checks source bytes and reviewed AST clauses without executing them. |

Strict positivity follows from integrating the strictly decreasing derivative `t*x^(t−1)` on `[40,41]` and `[56,57]`. The open interval matters: the difference vanishes at `t=0` and `t=1`. This is a written scoped proof supported by exact finite certificates, not a formal-kernel theorem.

## Reproduce

CPython 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/pr6551-retirement-audit
```

The registered hook runs normal and optimized modes. Each performs both endpoint engines, the cut, accounting and source-tariff binding and compares the complete deterministic receipt [RESULT.json](RESULT.json). A direct, Git-free replay is:

```sh
python3 -I -B research/pr6551-retirement-audit/verify.py
python3 -I -O -B research/pr6551-retirement-audit/verify.py
```

Expected status: `PASS_PR6551_INDEPENDENT_RETIREMENT_AUDIT`. The `--emit` option prints a newly computed receipt for explicit comparison; the default never regenerates tracked files. [VALIDATION.md](VALIDATION.md) records actual commands, environment, committed-byte/export checks and limitations. Each registered command has a 120-second bound; the expanded checks use only the standard library. Fresh measurements and the exact tested snapshots are recorded in [FOLLOWUP-VALIDATION.md](FOLLOWUP-VALIDATION.md).

## Pins and independence

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`; guidance priority revision 8; selected record PR6030. Exact reviewed candidate: `11ca568cd1a16776ade02b4df09ea04a784cc674`; predecessor: `775722aa94a5e85b05d1d704d7dca10cbf016f0c`. [RETAINED.json](RETAINED.json) records 22 copied sources by original commit/path, Git blob and SHA256. The portable replay checks integrity relative to that local manifest, not independent provenance. All 22 sources were also compared directly with their original Git objects, including the four #6398 files and both pricing files. The optional [check_source_objects.py](check_source_objects.py) requires an externally obtained full publication commit and compares its frozen manifest and source objects; see [EXTERNAL-REVIEW.md](EXTERNAL-REVIEW.md#source-integrity-and-provenance). The unchanged PR6551 `source.tar` retains PR6545 and its nested native/source notices; no network or unmerged Git object is needed at replay time. The original PR6398 semantics are retained for inspection, never executed. [SOURCES.json](SOURCES.json) binds base guidance; [TASK.json](TASK.json) records the refined card and family decision.

The lead wrote the sparse full-caller interpreter. One separate native AI agent derived accounting before comparing its result with the asserted delta. A second independently checked the cut using four exact fibers, then reviewed the lead interpreter. The checkers share the declared opcode/physical-rank meanings, cost contract and Python rational arithmetic; implementation separation does not prove those physical meanings. The predecessor discloses Codex assistance, and the lead plus both internal review roles here use GPT-6 Astra through Codex, so shared model blind spots remain. Claude Code / Claude Opus 5.5 separately reviewed snapshot `13e880a734cc03f2a52c82a412a9a0e6ac2b1f0c` and reported no scientific error, including an additional full-endpoint check. Its scripts were not supplied or replayed here. Its findings motivated this expanded coverage and source/receipt corrections; [EXTERNAL-REVIEW.md](EXTERNAL-REVIEW.md) records the reported evidence and our response. That external review does not cover the later checker changes. The internal skeptical reviewer made the conceptual suffix argument's implicit invertibility premise explicit and retained the requirement that ordinary coefficients stay outside tensor powers. No blocking finding remains for this scope. This is AI review, not independent human review, maintainer acceptance or formal verification.

## Limits

Native phase maps, all-width physical realization, total ordinary-work rates, changed completion decay, the numerical root, uniform compiler and outer predicates were **not replayed**. The exact retained ordinary formula now evaluates independently to 254,699,248 for the predecessor and 254,932,208 for the candidate: the two additional translations cost 232,960 under that formula. The formula's physical per-operation rates remain inherited, so these arithmetic checks are not a newly audited physical upper bound; no cost is declared zero. All five inherited framework assumptions remain: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`. No global caller/tree optimum or complete rounded multiplier is claimed.

## Open next questions

- Independently verify the changed completion-tail parameters and numerical claim for this exact invoice. Begin with the [pinned PR6551 pricing source](https://github.com/aliromman/integer-mult-bounds/blob/11ca568cd1a16776ade02b4df09ea04a784cc674/research/retirement-rebalanced-query-tree/pricing.py) and the source's explicit old-decay rejection, using a separately derived rational bound. This would address a distinct remaining admission obligation; it requires the full compiler contract and cannot be inferred from a favorable invoice difference.
- Bind the declared LOCAL, QUERY and whole-idle semantics to their exact physical maps and all-width ordinary normalizers. Begin with one source-bound map and the scalar-outside-tensor convention. The blocker is physical/source coverage, not this finite caller identity.

The [canonical coordination comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/5645#discussioncomment-19369687) precedes the investigation; [OVERLAP.json](OVERLAP.json) records coverage and freshness. No broader tree search or successor construction is reserved.

## Credit and license

Ali Romman supplied PR6551, PR6545, PR6398 and the retained integration. Credit PR5599/5602/5611/5615's handoff/basis methods, PR6348's binary supplier, PR6529's native word and PR6524's replay services; Cinna Davis, Jacob Alan Sussman, DreamingOfClouds, Rohan Arun, Erwan L. and every author in the retained notices keep their contributions. New independent audit by DLamdata with substantial GPT-6 Astra assistance through OpenAI Codex, including separate AI accounting and skeptical-review roles. Claude Code / Claude Opus 5.5 contributed the external audit, suffix-coverage findings, provenance and receipt critique, tariff-source analysis, and shared-assumption clarification; the follow-up implementations are Codex work responding to that review. Apache-2.0; see [LICENSE](LICENSE), [NOTICE](NOTICE) and the unchanged source notices.
