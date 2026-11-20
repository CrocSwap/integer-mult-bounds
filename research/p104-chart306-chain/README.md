# P104 chart-306 paid-chain contraction

The mixed-rank BIT supplier gives conditional κ ≥ 0.00387992803556 when paired with the #7830 rational word. Its two paid cutoffs reduce the tensor from 832 to 480 factors compared with #7835. The separate package contains the complete application and an independent replay. [Mixed-rank supplier and review](../p104-mixed-rank-supplier/README.md)

**Combined continuation:** [DOUBLE.md](DOUBLE.md) records a second exact contraction and conditional finite lower 0.00387990740712, above the round target under the inherited premises. The original first-contraction evidence below is retained for reproducibility.

The saved finite application gives **conditional κ ≥ 0.00387978824626** on the 48-call rational and unchanged 36-call binary supplier, under the five inherited premises. This is 0.00000034813558 above the previous #7786 finite lower of 0.00387944011068, and 0.00000034813549 above its directed upper 0.00387944011077. The enrolled goal of 0.00387981257853 remains 0.00000002433227 above the new lower. These are conditional finite comparisons, not maintainer selection or a proof of the five premises.

## Exact change

The source is PR #7786 head `89a67c404226d51028e135de2b9169e9020d57af`, canonical word SHA-256 `c447b6d5ba956fbe40834fe3c1bc69af2f225736f1b97ecd84b57bab9dd283cb`, layout SHA-256 `f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7`. In the forward representation, paid slots 94318 and 87 route through charts 2 → 304 → 306 with grades 2 and 1. Remove 94318 and send the 87 value directly from chart 2 to 306 at grade 3. Its new source is `-1/4` times address `-1255`. At the nine old 87 readers, restore the old value using `-1/4` times 94028 and `-2` times 90122. Their causal availability and the exact arbitrary-input stock identity are checked in `verify_delta.py`. All other forms, movements and ordering are checked literally against the source. The candidate's canonical word SHA-256 is `320847d42f2655c3cc0fd29fe670ae77277e9c2f377c1c92f33d7df050872f54`.

Across 48 calls the signed paid histogram changes by P1 −48, P2 −48, P3 +48; productive targets are unchanged. The old layout and caller stream are unchanged. `EXACT-LIFT.json` records the exact rational directed improvement interval and remaining target shortfall. A price benefit alone is not a construction qualification.

## Evidence and limitations

`APPLICATION.json` is the saved #7786 bounded-scalar application replay on the frozen candidate. It checks the shared caller, exact native source columns, addressed retirement, guarded scalar conversion, paid and target histograms, ordinary cost, the common root envelope and the outer predicates under the inherited assumptions. The recorded run used CPython 3.12, 32.87 CPU seconds and about 197 MiB peak RSS. `evidence/AUDIT.json` is the separate expanded application audit, including the actual-grid fixture, source and invoice recount and width/depth checks. `evidence/EXACT.json` and `evidence/FROZEN-REVIEW.json` preserve independent source-stock and literal-delta reviews. Separate AI checks are not human review or formal verification. This first candidate does not reach the round target; see the combined continuation. Independent human/maintainer review remains open.

## Reproduction

This is a source-bound archive with an explicitly external executable predecessor, not a registered self-contained package. Obtain the public #7786 repository at the exact head below, verify it, and prepare its pinned public source cache. The commands use distinct writable directories and do not replace the original source files:

```sh
git clone https://github.com/Clear1nsight/integer-mult-bounds.git /tmp/p104-predecessor
git -C /tmp/p104-predecessor checkout --detach 89a67c404226d51028e135de2b9169e9020d57af
test "$(git -C /tmp/p104-predecessor rev-parse HEAD)" = 89a67c404226d51028e135de2b9169e9020d57af
pred=/tmp/p104-predecessor/research/p104-iterated-returns
pkg=research/p104-chart306-chain
python3.12 -IB "$pkg/verify_delta.py" --source-word "$pred/continuation/WORD.json.gz"
python3.12 -IB "$pred/prepare_sources.py" /tmp/p104-sources --fetch
python3.12 -IB "$pred/continuation/qualify.py" --cache /tmp/p104-sources --package "$pred" --word "$pkg/CANDIDATE.json.gz" --word-sha 320847d42f2655c3cc0fd29fe670ae77277e9c2f377c1c92f33d7df050872f54 --layout "$pred/continuation/LAYOUT.json.gz" --layout-sha f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7 --out /tmp/p104-chain-application.json
```

The predecessor source preparer checks its locked bytes. The candidate application command independently binds the candidate and layout hashes and locked supplier inputs. The original local execution used the equivalent already prepared source cache; the dedicated hosted workflow also fetched and authenticated the pinned supplier sources for the earlier exact-head scientific replay. The qualifier authenticates its historical source receipt and binary inputs as described by the predecessor. Compare the semantic outputs, not incidental runtime fields. See the predecessor's continuation README for the expanded audit and premises.

## Credit

Clear1nsight prepared this continuation with substantial OpenAI Codex assistance, including separate AI reviews. The predecessor words and finite application are from #7786 and #7781; Ali Romman supplied the #7776 carrier, tariff and caller, and #7774 the restored chain. Their notices, source licenses and framework contributor credits remain in the pinned predecessor. New material is Apache-2.0; see `LICENSE`.
