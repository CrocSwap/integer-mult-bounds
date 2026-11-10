# Conditional κ = 0.00363216151: retime and split helper 1123

This construction changes the complete invoice of [#7004](https://github.com/CrocSwap/integer-mult-bounds/pull/7004), raising its conditional claim from **0.00363206219** to **0.00363216151**, a gain of **0.00000009932**. It retimes one paid helper transition and splits the resulting independent rank-nine helper into ranks eight and one. The caller and BIT source stay byte-for-byte those of #7004. This is an author-checked conditional construction, not supplier admission or a new unconditional multiplication theorem. The selected frontier is unchanged.

## Exact edit and arbitrary-input argument

The scientific baseline is ToikY's #7004 at `2ee11a4460f23abf06d16b12f18c8ef9aca889f1`, canonical word SHA256 `311069e5faeef999a0b3f2fd8ae9c256b67b40a368998c5c31cd38a500f385e3`. All indices are zero-based. Canonical main was refreshed at `17469fff78c22941280f04d39dc5a1faee09c840`, priority revision 8.

Helper 1123 has no scalar contact between the source indices 37910 and 56194; its only event there is `MOVE(1123,242,127,false)` at 44017. The spaces at frames 242, 245 and 127 strictly nest, with dimensions 4, 8 and 9. Replace this MOVE by 242→245→127 at cut 43057, immediately before source event 43057. This replaces one rank-five payment by ranks four and one. Frame transports preserve normalized scalar coordinates, and there are no intervening contacts with helper 1123, so this retiming preserves the entire normalized map.

At this cut the exact prefix row of role 1123 is the independent input `x1123`. The exact suffix sends the cut direction `e1123 + e843` to final direction `e1123`, with no other public or owned output. Roles 1123 and 843 are both physically at frame 245 after the retiming. These are complete rational row/column equalities, not sampled tests.

Insert `ADD(843,1123,-1,245)` followed by `ADD(843,1480,+1,245)`. The new independent public helper 1480 starts at frame 245. Relabel every later use of1123 as1480. Helper 1123 now stops at245, and 1480 finishes at127. Replacing the old cut coordinate by the fresh input changes the suffix input by `(x1480−x1123)(e1123+e843)`, hence changes only the renamed successor output by `x1480−x1123`. All other outputs are unchanged, helper 1123 returns its old input, and 1480 returns its own arbitrary input. No boundary basis change is needed. The exact generic split checker also verifies both unit pairings and the nested productive targets.

`construct.py` uses Ali Romman's split constructor as adapted by CubeJerry, with the pivot chosen to be the retimed helper itself. `split.py` preserves predecessor attribution and additionally excludes the second main plane from the helper group. Owned labels shift by one to accommodate the new public helper; their logical lifetimes, ascent inventory and peak remain fixed.

## Complete accounting and evidence

Per LOCAL the paid delta is `{1:+1,4:+1,5:−1}` and the target delta is `{1:+1,8:+1,9:−1}`. Across the unchanged eighteen LOCALs these counts multiply by eighteen. Rank surplus stays 1520 and no empty-root target is credited. For `p=1−κ`, the net margin gain is

```
18 (8^p + 5^p − 9^p − 4^p) > 0,   0 < p < 1.
```

Strict concavity proves the inequality: the increment from4 to5 exceeds that from8 to9. The rank-one target and payment cancel; neither is omitted. This is a new complete paid/target profile, rather than more digits of the predecessor root.

The emitted word has71,258 events and1,481 public fields:400 main fields and1,081 independent helpers. It adds exactly one MOVE and two ADDs. The source caller remains3,095 events with76 roles. Owned labels51, lifetimes54, peak43, rises23 and rise mass56 remain fixed. The conservative ordinary bill is826,738,944 < 10^9. The second rational engine certifies the raw crossing in `(0.00363216151546863865247146187645487, 0.00363216151546863865247146187645488)`. The primary separately certifies a containing bracket. The claim leaves about5.47e-12 fixed-invoice headroom; extra decimal digits of this root are not a construction gain. Tested price is0.00363216151007, compiler gap10^-14 and written logarithm power2229. Full counts, the exact compiler threshold and all margins are in `RESULT.json`. The raw fixed-invoice ceiling is certified by two rational interval engines and a negative derivative bound; this changed hosted/owned-ascent model is outside the historical nine-local-word packing-cap model.

The checker authenticates all source members by size, SHA256 and Git blob; rebuilds #7004 and the candidate; checks the exact cut prefix/suffix; runs an exact all-input adjoint and a separate integer-grid forward replay; checks every introduced chart pair and four named boundary pairs, including absolute phase and every one of512 columns; replays the unchanged formal caller; reconstructs both complete invoices; checks the ordinary tariff, E-free paired BIT binding, common grid and source precision envelopes, strictification, compiler and 54+4 outer predicates; and runs the full width 512 physical control. Mutations of the cut direction, contact window, corrections and successor frame reject. The source invoice rejects the new claim.

The two interval and endpoint implementations are distinct, but their reuse here is source-aware attribution, **not independent human or proof-kernel review**. Finite physical replay is finite evidence. No baseline all-history, Lean or Docker suites were run.

## Reproduce

The scientific verifier is standalone and needs only Python and the committed package; it extracts authenticated source code into temporary storage and does not need Git or network.

```sh
python3 -I -B research/p104-causal-retimed-step/verify.py
python3.12 -B scripts/research_package.py --package research/p104-causal-retimed-step
```

The generic registered command targets Python 3.12. Local evidence records the interpreter actually used; a registered 3.12 execution must not be inferred from a direct3.14 replay. Optimized mode is deliberately rejected because retained source engines use assertions. `--out UNUSED_PATH` emits a new receipt; ordinary replay compares every retained result field. Gzip equality compares the complete decompressed JSON bytes.

To reproduce the optional finite discovery screen:

```sh
python3 research/p104-causal-retimed-step/source.py --output /tmp/base7004.json.gz
python3 research/p104-causal-retimed-step/discover.py /tmp/base7004.json.gz /tmp/screen7004.json
```

`SCREEN-HITS.json` and `SCREEN-LOG.txt` retain three nominations, all using the same paid carrier; they are not three independent gains. The certificate uses one nomination with pivot1123 to remove unnecessary basis swaps. The earlier #6931 screen is retained as exploratory round-one evidence, not the baseline of the new claim.

## Scope and remaining obligations

All five framework assumptions remain: `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`. Also retain #7004's exact odd-scalar child returns, owned ascent, hosted/per-port and one-field-idle caller, LAMBDA/ordinary tariff and paired BIT contracts. The new edit itself adds only integer ADDs and no owned rise. Full fixed-tape/rounded provider admission and the #6998 physical-tariff bridge remain open. The large uniform word and rounded multiplier are not materialized.

The base source archive includes the exact #7004/#7003/#7000 files and all their notices; `INPUTS.json` binds every member to its original Git blob. `SOURCES.json` separately records current-main task and selected-record provenance. Existing frozen packages and the selected record are unchanged.

## Credit

New source-bound paid-retiming/split composition, simplified pivot, packaging and checks: prepared for dillona with substantial OpenAI Codex assistance; no subagents. Apache-2.0.

Ali Romman supplied independent-helper split and basis methods (#5599); Jerry Chen/CubeJerry supplied paid retiming (#6805/#6916), shared wires, the #7000 composition and paired QUERY-only BIT source; DreamingOfClouds supplied #6931/#6936/#6937 and the native-word chain; ToikY supplied #7003 five fusions and #7004 peer retiming. Retain the original notices and credit to Pierre-Loic Doulcet, Cinna Davis, Mason Hale, Jacob Alan Sussman, zxv, thu-nmrc and all other native/compiler/precision/analytic predecessors named there. No predecessor mechanism is claimed as newly invented.

## Open next questions

- Can the other two screened cuts compose without paying this carrier repeatedly? First construct a joint exact prefix/suffix certificate and full invoice. They share role 1123, so independent gains cannot be assumed.
- Can the actual rounded providers be admitted under one physical tariff? Continue #6998 with this exact word; the inherited provider and framework obligations remain open.

Structured questions and blockers are in `TASK.json`. Live overlap covered398 open and6,175 closed/merged PR bodies plus7,013 Discussion records. This coverage is not a novelty certificate. The canonical claim and final artifact link are maintained on [the handoff board](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19519779).
