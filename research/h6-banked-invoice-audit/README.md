# H6 conditional banked-invoice audit

For the fixed H6 model in PR1590, this audit certifies the largest integer helper allowance for five distinct target inputs at L = 3, 5, 7. It uses Dominik Scholz's unchanged PR606 banked invoice. The original twelve cases remain intact; the three full-title PR1424 cases are a separate appendix.

| Exact target | L = 3 | L = 5 | L = 7 |
|---|---:|---:|---:|
| Quoted PR890: `0.001661957775` | 80,558 | 89,683 | 80,753 |
| Retained PR890: `0.001661957774647029` | 80,558 | 89,683 | 80,753 |
| Pinned selected: `0.001672660197076918` | 79,880 | 88,765 | 79,778 |
| Quoted PR1424: `0.001676855229071321` | 79,617 | 88,409 | 79,399 |
| Full PR1424 title: `0.001676855229071321886206381217337893` | 79,617 | 88,409 | 79,399 |

The frozen inputs are `n=30960`, `h=17`, `hist={17:256,15:560}`, data path `[16]`, helper path `[1,7,8,1]`, `virtual=False`, and `bad=False`. Historical PR592 is the source's internal default, not one of these targets. The selected target is pinned historical provenance; PR1424 is a comparison input, not the selected result.

At every reported R, exact outward bounds prove `lower(R) > target > upper(R+1)` and an open real pressure boundary between R and R+1. The written proofs use monotonicity of the true pressure root to exclude every larger count. They do not assume monotonicity of floating nomination or rounded program output. Synthetic controls distinguish the invoice's rounded endpoint criterion from the true-root criterion, and binary64 comparison from exact rational comparison; these distinctions do not change the reported boundaries.

## Evidence and replay

Read the unchanged [original model and proof](h6_banked_invoice_audit/MODEL_NOTE.md), its [source register](h6_banked_invoice_audit/SOURCES.md), and the [full-title appendix](h6_full_pr1424_appendix/APPENDIX.md). The new audit reconstruction is checked against the authenticated invoice. Source and rational modes share `model.py`; they are not independently authored or code-disjoint verifiers. The separate GPT-6 Pro review found no substantive mathematical flaw and requested execution hardening. The exact Pro-authored hardening and its 22 execution controls passed locally normally and optimized. This review is supported here by the recorded textual verdict and hardening excerpt; the full peer report and mathematical review checker were not recovered or locally replayed. No independent human or formal review is claimed.

From the repository root:

```sh
python3.12 scripts/research_package.py --package research/h6-banked-invoice-audit
```

The registered commands require `authenticated_run.py`, use only the standard library, run with `-I -O -B`, require no network, and read package-local files. The launcher authenticates the complete application source closure before execution and compiles the retained source bytes, including nested explicit-path imports; application bytecode caches are not used. They check all fifteen cases, four source guards, seventeen original certificate controls, ten appendix rejection controls and three positive-control groups. The four arithmetic commands have 30-second caps and took under one second locally. A fifth registered command runs 22 execution-hygiene controls with a 120-second process-group cap; local normal/optimized runs took 0.97/3.12 seconds. It first binds the active launcher and appendix bytes to the exact fixed-hash control fixtures. The control fixtures use a synthetic import closure and explicit doubles for the real appendix entrypoint; they do not add mathematical cases or certify invoice arithmetic.

Local CPython 3.12.14 normal and optimized replays passed. Regenerated original evidence (58,405 bytes, SHA256 `37c44122652782b05e43b13383d19d41f9eadfaa5f2fab59ed330cc57c0b18f9`) and appendix evidence (16,238 bytes, SHA256 `a64701a8d2187604b74f939bbba00b3ea9afc0d3b84a22136c4027f2d2180325`) match the canonical receipts exactly. [REPLAY.json](REPLAY.json) preserves those historical receipts and adds twelve local hardening runs: the four registered modes normally and optimized, plus both evidence regenerations in both modes. All passed in under one second per command and reproduced both canonical evidence hashes.

For authenticated regeneration from this package directory, use `python3.12 -I -B authenticated_run.py audit --output PATH` or `python3.12 -I -B authenticated_run.py appendix --source --output PATH`, with an unused output path. Both refuse to overwrite existing files. The patched appendix finishes all requested checks and final source reauthentication before writing. Output writes are not atomic: an I/O error can leave a partial file, and a later controls-output failure can leave the evidence file. File existence alone is not a success receipt; require exit zero and exact evidence comparison. The appendix's `--source` mode adds actual invoice/threshold and native float comparisons. The author's `price_h6.py` is hash-checked and parsed only by registered replay; its separate local producer replay reproduced the author's saved output in both modes, but is not a substitute for these explicit-guard checks.

## Scope and attribution

The final bounded overlap check at 06:57:59 UTC read four relevant Discussions with complete comment/reply pages and the latest 100 open PRs, supplemented by the earlier complete cache; it is not an all-history novelty claim. PR1590 and PR1424 heads were unchanged. The [PR1424 review comment](https://github.com/CrocSwap/integer-mult-bounds/pull/1424#issuecomment-6162623622) leaves parent regenerated-container binding and controller/invoice/geometry obligations outstanding. Its full title remains only a comparison target here.

These are conditional arithmetic allowances. Encoder extras, compensation chronology and arbitrary-dirt restoration, frame-zero precompensation, target cap-15/FULL restrictions, spectators beyond the model, inter-stage sharing, and physical helper loading remain unpriced or unproved. Neither `30960/R` nor the author's `1.538281` ratio establishes helper capacity. The latter is the ratio of printed zero-helper paper values `0.006945535353 / 0.004515128332`. No complete paid profile, 5% gate, supplier admission, new kappa or selected-record change follows.

Credit [PR606](https://github.com/CrocSwap/integer-mult-bounds/pull/606)/Dominik Scholz and the retained Niemeier/Leech notices for the model and inherited interval engine; [PR1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590)/DreamingOfClouds, with Claude Opus 5.5 via Claude Code, for the H6 interpretation and [published pricing script](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/b496aed769dd724cd1ff6b921cade626562be27b/research/h6-banked-breakeven/price_h6.py). New arithmetic research and checker authorship are by Andrey Mas with GPT-6 Pro through ChatGPT. Codex performed source coordination, execution audit, mechanical replay and packaging, without mathematical derivation or proof repair. Coordination: [Discussion1635](https://github.com/CrocSwap/integer-mult-bounds/discussions/1635).

The proof notes, arithmetic, vendor source and scientific evidence retain their authenticated producer bytes. The appendix has only the supplied output-order hardening, and the new launcher is the exact authenticated Pro source. The original direct entrypoints remain available as historical source; running them directly does not provide the launcher's bytecode-cache guarantee. The guarantee assumes a trusted interpreter/standard library, stable package layout and a fresh single-threaded isolated process. The authenticated launcher's embedded model label is retained as producer text; the observed research/review model is recorded here as GPT-6 Pro. Their source-acquisition limitations, Python 3.13.5 statements, host-log references and archive inventories describe the original Pro execution. Omitted duplicate views and host logs are not required by replay. The package adds a separate local Python 3.12 receipt and exact upstream [license](h6_banked_invoice_audit/LICENSE) and [notices](h6_banked_invoice_audit/notices/). [SOURCES.json](SOURCES.json) records the notice blank-line normalization difference and historical source pins. No structure/Walsh program or geometry census was run.

## Open next questions

Can a concrete compensation and helper-loading chronology realize a complete paid physical invoice within one of these allowances? First specify all physical roles, paths, pending factors, restoration, encoder and spectator charges, then screen the whole invoice. The missing construction and interfaces, rather than the arithmetic threshold, block that conclusion. [TASK.json](TASK.json) records the current revision-3 audit card, the session's scope change and this precise handoff.
