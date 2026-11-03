# Independent retirement-cut and invoice audit of PR6551

The changed `(7,2,5,4)` caller in Ali Romman's [PR6551](https://github.com/CrocSwap/integer-mult-bounds/pull/6551) passes this independent finite audit against [PR6545](https://github.com/CrocSwap/integer-mult-bounds/pull/6545). The retired output and fresh suffix input are independent, and the complete Gaussian invoice difference is

```text
ΔT = −104 H16 + 104 H40 + 208 H41 − 208 H57
ΔP = −104 H16 + 312 H40 − 208 H56
Δ(T−P) = 208 (H41 − H40 − H57 + H56) > 0,  H_r=r^t, 0<t<1.
```

This resolves the specific independent-review question in PR6551's first Open next question and [handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19367661). The construction, retirement identity and gain belong to the predecessors. This contribution adds separate exact implementations, a different cut argument, semantic failure controls and explicit review boundaries. It does **not** certify PR6551's numerical κ, admit a supplier, or change selected PR6030.

## Exact scope and evidence

| Check | Evidence |
|---|---|
| Complete old/new caller | [caller.py](caller.py) interprets all 609/611 events and checks all 1,225 transfer coefficients in each 35-input word over `Q(i)[D1,...,D18,q]/(q^4−1)`; no predecessor code executes. |
| Actual retirement cut | The first 345 normalized events are identical, including the original 329-event prefix. Coordinate 4 has row and column `S e4`, where `S=λq⁻¹`; coordinate 34 is untouched. The suffix never uses coordinate 4 except for its final `λ⁻¹` normalization. |
| Different exact cut proof | [cut_four_fibers.py](cut_four_fibers.py) propagates one row backward and one column forward at `q=1,−1,i,−i`, retaining every stage variable formally. The Chinese remainder argument in [REVIEW.md](REVIEW.md) makes these four fibers an exact check of the quotient ring. |
| Complete Gaussian delta | [accounting.py](accounting.py) traverses both literal binary trees, endpoint stage supports and every paid caller event. It authenticates the retained native archive and cancels the same 18 native invocations without replaying them. [ACCOUNTING.md](ACCOUNTING.md) gives the derivation. |
| Counts and extra ordinary work | Both constructions have 13,756 productive fields and 67,096 paid Gaussian jobs. Both rank masses fall by 832. Native calls remain 18, thin queries 17, and the only ordinary event-count change is two additional Q_POWER operations. |
| Controls | Eleven primary caller, seven accounting and four different cut controls reject; both actual callers and elementary inverse/canceling identities are positive fixtures. |

Strict positivity follows from integrating the strictly decreasing derivative `t*x^(t−1)` on `[40,41]` and `[56,57]`. The open interval matters: the difference vanishes at `t=0` and `t=1`. This is a written scoped proof supported by exact finite certificates, not a formal-kernel theorem.

## Reproduce

CPython 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/pr6551-retirement-audit
```

The registered hook runs normal and optimized modes. Each performs all three checks and compares the complete deterministic receipt [RESULT.json](RESULT.json). A direct, Git-free replay is:

```sh
python3 -I -B research/pr6551-retirement-audit/verify.py
python3 -I -O -B research/pr6551-retirement-audit/verify.py
```

Expected status: `PASS_PR6551_INDEPENDENT_RETIREMENT_AUDIT`. The `--emit` option prints a newly computed receipt for explicit comparison; the default never regenerates tracked files. [VALIDATION.md](VALIDATION.md) records actual commands, environment, committed-byte/export checks and limitations. Each registered command has a 120-second bound; observed scientific runs are under two seconds, with a recorded child high-water mark below 64 MiB.

## Pins and independence

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`; guidance priority revision 8; selected record PR6030. Exact reviewed candidate: `11ca568cd1a16776ade02b4df09ea04a784cc674`; predecessor: `775722aa94a5e85b05d1d704d7dca10cbf016f0c`. [RETAINED.json](RETAINED.json) binds copied sources by original commit/path, Git blob and SHA256. The unchanged PR6551 `source.tar` retains PR6545 and its nested native/source notices; no network or unmerged Git object is needed at replay time. The original PR6398 semantics are retained for inspection, never executed. [SOURCES.json](SOURCES.json) binds base guidance; [TASK.json](TASK.json) records the refined card and family decision.

The lead wrote the sparse full-caller interpreter. One separate native AI agent derived accounting before comparing its result with the asserted delta. A second independently checked the cut using four exact fibers, then reviewed the lead interpreter. The three checkers share the declared opcode/physical-rank meanings and Python rational arithmetic; implementation separation does not prove those physical meanings. The reviewer made the conceptual suffix argument's implicit invertibility premise explicit and retained the requirement that ordinary coefficients stay outside tensor powers. No blocking finding remains for this scope. This is AI review, not independent human review, maintainer acceptance or formal verification.

## Limits

Native phase maps, all-width physical realization, total ordinary-work rates, changed completion decay, the numerical root, uniform compiler and outer predicates were **not replayed**. The 254,932,208 ordinary-work figure is predecessor evidence, not a newly audited physical upper bound. The two additional ordinary translations are counted here; no cost is declared zero. All five inherited framework assumptions remain: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`. No global caller/tree optimum or complete rounded multiplier is claimed.

## Open next questions

- Independently verify the changed completion-tail parameters and numerical claim for this exact invoice. Begin with the [pinned PR6551 pricing source](https://github.com/aliromman/integer-mult-bounds/blob/11ca568cd1a16776ade02b4df09ea04a784cc674/research/retirement-rebalanced-query-tree/pricing.py) and the source's explicit old-decay rejection, using a separately derived rational bound. This would address a distinct remaining admission obligation; it requires the full compiler contract and cannot be inferred from a favorable invoice difference.
- Bind the declared LOCAL, QUERY and whole-idle semantics to their exact physical maps and all-width ordinary normalizers. Begin with one source-bound map and the scalar-outside-tensor convention. The blocker is physical/source coverage, not this finite caller identity.

The [canonical CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/5645#discussioncomment-19369687) precedes the investigation; [OVERLAP.json](OVERLAP.json) records coverage and freshness. No broader tree search or successor construction is reserved.

## Credit and license

Ali Romman supplied PR6551, PR6545, PR6398 and the retained integration. Credit PR5599/5602/5611/5615's handoff/basis methods, PR6348's binary supplier, PR6529's native word and PR6524's replay services; Cinna Davis, Jacob Alan Sussman, DreamingOfClouds, Rohan Arun, Erwan L. and every author in the retained notices keep their contributions. New independent audit by DLamdata with substantial OpenAI Codex assistance, including separate AI accounting and skeptical-review roles. Apache-2.0; see [LICENSE](LICENSE), [NOTICE](NOTICE) and the unchanged source notices.
