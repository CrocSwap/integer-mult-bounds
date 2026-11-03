# Binding the independent counts to the declared source tariff

**Verdict:** the independent accounting uses the exact recursive tariff declared in both pinned pricing sources, on the domain that the audit enforces. Retaining those sources, checking their local integrity, and comparing them with pinned Git objects plus this explicit contract map is sufficient for a source-bound accounting claim. The accompanying AST checker adds a useful fail-closed guard against silently reusing this reviewed contract after a tariff edit. Neither a source hash nor an AST match proves physical validity of that contract.

Sources are #6545 `775722aa94a5e85b05d1d704d7dca10cbf016f0c`, `research/gaussian-root-retirement/pricing.py`, and #6551 `11ca568cd1a16776ade02b4df09ea04a784cc674`, `research/retirement-rebalanced-query-tree/pricing.py`. Source SHA256 values are recorded in `evidence/followup/pricing-binding.json`. No source pricing, native, controller or compiler module was imported or executed for this review.

## Exact source map

Line references below are to these exact copied files; their one-line offset is intentional.

| Declared contract | #6545 source | #6551 source | Independent check and boundary |
|---|---|---|---|
| LOCAL adds the local paid profile and productive helper profile once | `assemble`, lines 35–37 | `assemble`, lines 36–38 | `accounting.inspect_caller` requires each stage 1…18 exactly once. The retained native archive and exact native word are identical, so these common terms cancel. This is cancellation under a common declared local-call contract, not a new native replay. |
| QUERY pays 104 rank-one jobs | `assemble`, lines 38–39 | `assemble`, lines 39–40 | One job per port; the native word has 104 distinct ports. All seventeen thin queries are counted. |
| IDLE pays 208 jobs of rank `8*len(stages)`; IDLE_ONE pays 104 | `assemble`, lines 40–44 | `assemble`, lines 41–45 | The independent code counts two or one jobs per port and verifies every actual binary-node stage set and both additional root idles. |
| Main target rank is `q%2 + 8*sum(stage exponents)`, with multiplicity 104 | `assemble`, lines 45–48 | `assemble`, lines 46–49 | The independent code enforces q∈{−1,0,1}, binary stage exponents, and stage-zero exponent 0. Thus its `abs(q)+8*sum(fresh exponents)` is identical on the audited domain. Outside that domain the independent code fails rather than extrapolating. |
| Actual main/idles must agree with native physical-map census | `assemble`, lines 49–50 | `assemble`, lines 50–51 | These are source checks, not re-executed by this audit. They explain the physical premise that remains. The independent full caller establishes the formal endpoint, while phase/rank realization still belongs to the retained native contract. |
| Retirement target substitution | `assemble`, line 52 | `assemble`, line 53 | Old adds `{1:104,16:104,17:−104}`; new adds `{1:104,40:104,41:−104}`. Independent traversal derives these changes from actual root masks, leaf sets, and endpoints; it does not call `formula_invoice`. |
| All source helper targets have native maps | `assemble`, line 32 | `assemble`, line 33 | Source assertion is retained; independent accounting checks the native archive identity and counts its structure but does not prove the asserted native maps. |
| Ordinary local route allowance | `run`, lines 134–136 | `run`, lines 136–138 | `(sum(local paid)+helper_normalizers+main_adapters+4*104+4*owned_lifetimes)*1000`, added to `real_scalar_allowance`, must fit `10^7`. This local physical rate is inherited, not recomputed by the independent audit. |
| Complete ordinary upper bound | `run`, line 137; budget line 143 | `run`, line 139; budget line 145 | The same declared expression includes every literal caller event; the two extra translations therefore receive a nonzero allowance. Exact arithmetic is below. |

ADD, SWAP, SCALE, LAMBDA and Q_POWER have no direct Gaussian tariff branch in `assemble`. That does **not** mean they cost zero. They belong to the ordinary allowance in `run`. The audit separately recognizes all event kinds, requires Q_POWER exponents ±2, and records every ordinary event. For q⁴=1 those exponents are the inherited q² translation. The ordinary nature of its physical realization is a source premise, rather than a consequence of merely classifying its opcode.

The candidate's `verify.py` `Extension.run` passes the same `local`, `native` and `L` to the predecessor invocation at line 88 and the new price calculation at line 136; it passes `native_word` to the new physical check at line 131. It changes the tree/caller, not those native profiles. The retained #6545 `physical.py` separately spells out Q² translation at lines 49–58, target rank/phase interpretation at lines 59–66, and whole-idle ranks and multiplicities at lines 67–85; those functions were read, not executed. This data flow supports cancellation; the immutable native archive separately binds the word bytes. It does not turn the shared local tariff into an independent physical theorem.

## Exact ordinary arithmetic under the retained tariff

Both sources declare

```text
raw = 18·10^7 + 17·1664 + 32·35·104·number_of_events + 35·104·(26+1000).
```

Literal caller lengths are 609 and 611. The resulting breakdown is:

| Term | #6545 | #6551 |
|---|---:|---:|
| Eighteen local allowances | 180,000,000 | 180,000,000 |
| Seventeen query allowances | 28,288 | 28,288 |
| All caller events | 70,936,320 | 71,169,280 |
| Final field allowance | 3,734,640 | 3,734,640 |
| Declared total upper bound | **254,699,248** | **254,932,208** |

The difference is exactly `2·32·35·104 = 232,960`, and both are below the source's `10^9` allowance. These are evaluations of the pinned declared tariff. The constants 1000, 1664, 32 and 26 and the physical meaning of an ordinary primitive have not been independently justified here. In particular, “the extra translations are funded under the same declared allowance” is supported; “this proves the physical bound” is not.

## Minimal fail-closed binding

`pricing_binding.py` reads and hashes both source files, parses them with `ast`, and compares the reviewed `assemble` prefix and ordinary-formula/budget statements with explicitly labelled source-contract fragments. It never imports, evaluates or executes source code. Whole-file source pins prevent hidden edits outside those fragments from being silently accepted. AST comparison only identifies the reviewed clauses; the separate accounting algorithm continues to derive the invoice from actual tree and caller data.

Three controls reject:

1. A changed QUERY tariff fails the immutable source pin.
2. The same changed QUERY tariff also fails direct clause comparison when the pin boundary is deliberately skipped for that control.
3. Changing the per-event ordinary factor 32 to 31 fails direct clause comparison.

The second and third controls show that regenerating a source pin alone cannot make the unchanged reviewed contract accept a changed tariff. They do not certify either old or new tariff mathematically. A changed source requires a new source review, explicit contract update, and rerun of affected evidence. Keep the fragments labelled as copied source clauses with predecessor credit; do not describe them as an independent physical semantics implementation.

Normal and optimized Python 3.12.14 runs pass with byte-identical reports. Reproduction:

```sh
python -I -B pricing_binding.py PATH/pr6545/pricing.py PATH/pr6551/pricing.py
python -I -O -B pricing_binding.py PATH/pr6545/pricing.py PATH/pr6551/pricing.py
```

The source-binding report is `evidence/followup/pricing-binding.json`, the exact integer arithmetic is `evidence/followup/ordinary-arithmetic.json`, and the observed optimized command/status is `evidence/followup/pricing-run.json`. The check is under one second and uses only the standard library. The integration retains both pricing files as immutable inputs in the package's source manifest; no full native or price replay is justified by this narrow source-binding addition.

## Limits and wording

This resolves the ambiguity between an arbitrary hardcoded accounting model and the actual declared source billing model. It does not close physical native admission, all-width implementation, numerical κ, completion decay, compiler, precision, or analytic recovery. The exact finite caller identity, strict concave invoice gain, source tariff binding and physical assumptions should remain separate evidence statements.

Suggested concise result wording: “The complete formal callers and independent retirement cut pass, and the independently counted Gaussian invoice delta is positive throughout 0<t<1 under the exact pinned source tariff. The same declared ordinary formula charges the extra two translations and evaluates to 254,932,208<10^9; its physical rates remain inherited.”

Credit Ali Romman and all native/ordinary/compiler predecessors retained in the source notices. New source-map review and non-executing binding prepared for DLamdata with substantial GPT-6 Astra assistance through OpenAI Codex, Apache-2.0. No independent human or proof-kernel review is claimed.
