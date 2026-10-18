# Native replay of the deferred R439 target basis

The exact deferred PR1188 candidate in Sagar Thakrar's [PR2115](https://github.com/CrocSwap/integer-mult-bounds/pull/2115), head `b56dceffad83c88e8ad39ffd82a1bdd55c4130da`, passes the unchanged native legality and 5/9/11-stage formal-column engines. This completes its README **Open next questions, item 4**, for one committed candidate. It verifies an implementation boundary; the circuit, replacement H5 lemma and 430-ADD saving belong to PR2115.

The selected supplier and exponent are unchanged. This is a finite native integration check, not hosted admission or a proof of the full multiplication theorem.

## Exact object and boundary

The baseline is Gareth Davidson's retained PR1188 word, `research/r439-gl5-shortest/candidate.json.gz`. The candidate is PR2115's unchanged `candidate-1188.json.gz`, canonical payload SHA256 `e7dd976535977adb327cfe03847324eef05f0d76b38bf120a17a79facac495bf`. Its 306 target-basis undo gates move from zero-frame D (exporter phase 1) to the beginning of B (phase 4), before any target climbs. The scatter is expressed in the prepared target basis.

A new reconstruction reads the baseline's two inverse 306-gate blocks, moves the literal undo, applies the preparation to all nine scatter columns, and compares the **entire** resulting JSON payload with the pinned candidate. It imports no PR2115 generator. The full dirty COPY/ADD/ERASE interpreter and native harness are adapted from PR1188 and credited, not offered as newly independent algorithms. The original exporter, stage wrapper, owner checker and C++ engines execute from pinned, unchanged source bytes.

For both words, exact symbolic execution checks all 661 source, target and arbitrary dirty-helper columns in both directions. It requires the boundary `(x,y,h) -> (x,y+x,h)`, clean copied storage at every reuse and equality with its original source at ERASE. The inherited owner checker still reports H2/K false on the baseline, and H2/K/**H5** false on the deferred word. Those flags are retained. PR2115's argued `VR=I` bridge is the proposed replacement; native success does not turn the old H5 flag true.

## Complete local and staged bills

| Quantity | PR1188 baseline | Exact deferred candidate |
|---|---:|---:|
| D / A / scatter / B / C ADDs | 5548 / 1626 / 527 / 800 / 1991 | 5242 / 1626 / 97 / 1106 / 1991 |
| Total ADDs | 10,492 | 10,062 |
| Native records | 13,421 | 12,991 |
| Native MOVEs | 2,911 | 2,911 |
| COPY / ERASE | 9 / 9 | 9 / 9 |
| Rank mass | 5,129 | 5,129 |
| Positive forward bound F | 13,667 | 13,667 |
| Positive reverse bound B | 3,758,418 | 2,825,146 |
| Local / nine-stage guard bits | 91 / 175 | 91 / 173 |

All 306 undo gates remain charged. The native and literal bounds agree exactly; `64 F^3 B^2 < 2^104` and `2^18 F^5 B^4 < 2^192` hold. The paid profile remains `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`. Per-register ordered MOVE paths and COPY/ERASE records are compared across the words.

The freshly compiled engines check 883, 1327 and 1549 independent global formal columns at 5, 9 and 11 stages. Candidate scalar ADD totals are 50,310, 90,558 and 110,682, plus respectively 666, 1998 and 2664 bridge ADDs. There are 45, 81 and 99 fresh COPYs; each corresponding reverse stage also executes its recorded lifecycle. All 96 inherited omitted-bridge controls across the two words reject. Eleven-stage column success is not an assertion of a separate eleven-stage precision cap.

Even granting scalar work for free leaves the recursive profile unchanged. No improved moment or kappa follows from this result.

## What the failure controls establish

Four finite controls reject a missing undo gate, the old scatter, reversed undo order, and undo after a target's first climb. Three of these are also executed through the actual native tools: the first two fail the local full formal-column boundary; late undo fails MOVE legality.

A fourth native probe changes only the 306 undo ADD phase labels from 4 to 1. **Both unchanged native engines accept it.** Inspection confirms they use the literal records' order, geometry and coefficients, not ADD phase labels. This is a scope limit of those engines, not an alleged failure of their stated mathematical checks. The new replay separately checks the exported phase counts and the complete raw-record SHA256 against PR2115's pinned exporter receipts. It rejects the relabeling. A fifth probe swaps two phase labels while preserving every phase count; only the complete record binding rejects it.

The correct record hashes are `2df55087c71725651b7fc531323a371810f6c8c6d49d84d2c397bdc2d1862133` (baseline) and `9732a8373b845d090615a39a693dc3c1fdb165777aa9b136f4f86aaac8f90e0c` (candidate). They bind exact deterministic binary instruction traces, not regenerated gzip containers. Source gzip files stay byte-pinned; newly emitted gzip words are compared through complete decoded payloads.

## Reproduce

Python 3.12, C++17 and Boost headers are sufficient. From the repository root:

```sh
python3.12 scripts/research_package.py --package research/r439-deferred-native
BOOST_INCLUDE=/path/to/boost/include python3.12 -I -B research/r439-deferred-native/verify.py --native --output /absolute/new/output
```

Omit `BOOST_INCLUDE` for system headers; `CXX` selects the compiler. `--native` recompiles all four binaries and compares the complete deterministic result with `NATIVE.json`. Output must be a new directory, and all generated data stay outside the source package. Omitting `--output` uses temporary storage. Explicit `--write` regenerates receipts during development. Child exporter assertions stay enabled even when the wrapper runs with `-O` and inherited `PYTHONOPTIMIZE=2`.

The generic registered replay checks the finite contract and the real entry point in a Git-free read-only export, including source and typed-receipt corruption. **It does not run C++.** The separate `r439-deferred-native.yml` workflow runs the native command with Boost and uploads its output. A metadata or generic-replay pass must not be reported as a native run. Expected native marker:

```text
PASS_R439_DEFERRED_NATIVE words=2 stages=5,9,11 controls=96+5 no_new_kappa
```

`VALIDATION.json` records the actual local environment and executed commands. Source bytes, historical assignment, predecessor provenance and mathematical receipts are in SOURCES, SELECTION, TASK, PREDECESSOR, FINITE and NATIVE. No hosted CI success is inferred from local execution.

## Scope and overlap

The fresh random draw `f0fe3489369e5f7a530effe408323d98` chose `bit-helper-contract`, priority revision 4, on canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Its prescribed PR1062 baseline passed. The scope is **changed**: PR1194/PR1311/PR1806 already cover the original H2/K route; this takes the explicit native handoff for PR2115's target-basis/H5 extension. PR2279 proves the best undo-ideal scatter count, and PR2356 concerns interleaved taps in two undo orders. Neither covers this native two-word replay. The claim and final overlap checkpoint are linked in TASK.json.

Only the exact full-deferral PR1188 candidate is checked. The 94-scatter-ADD order-ideal refinement and PR1868 twisted-helper variants are not inferred from it. Full hosted emission/invoice, physical projector routing, recursive scratch allocation, all-size compilation, common-label realization, precision/tape and outer analytic assembly remain outside this replay. No Lean kernel proof is claimed. Supplier adoption is separate maintainer work.

## Open next questions

Can this exact word pass a complete changed-word hosted emission and invoice? Start from the PR1806 route, bind its actual owner/routing and phase records to this exact deferred payload, and charge recursive child output plus scratch. This matters because local formal columns and native MOVE legality do not establish the physical hosting/allocator contract. Changed-word hosted emission and inherited compiler/common-label/precision/tape obligations remain blockers. TASK.json gives the structured handoff.

## Credit

Sagar Thakrar / PR2115 supplies the target-basis deferral, replacement H5 proof and all circuit savings. Gareth Davidson / PR1188 supplies the baseline, literal interpreter and native harness, following his PR1122/980/926 and Sagar Thakrar's PR837 and Sricharan Vagvala's PR967 harnesses. The retained lineage includes PR915/PR794 target compensation, Sagar Thakrar PR1062, Aaron Wang PR1015, Ross Richardson PR923/936, Sricharan Vagvala PR967, DreamingOfClouds PR589 and eumemic PR555/543; Dylan Crow supplies the exporter. Credit the scalar-interface and checker authors retained in their notices. PR1194 (woklerx), PR1311 (Arham Tahir), PR1806 (mtpsl) and Hanson Sun's PR1902 establish the semantic and replay context.

PR2115's README and proof are preserved verbatim under vendor/pr2115. The upstream native, owner and lineage notices remain unchanged; NOTICE.md links them. Prepared by **Gareth Davidson (@bitplane)** with substantial **OpenAI Codex assistance** in research, implementation, validation and writing. No subagents or independent human review. Apache-2.0.
