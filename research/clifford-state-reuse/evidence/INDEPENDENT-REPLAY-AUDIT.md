Retained source report SHA256: `d9a04e54f5f213213c1f16a98aad8cb20663395875571b0cf523002748420dad`. Local path prefixes are redacted; this is a review derivative.

# Independent saved full-phase artifact audit

Auditor: `/root/frontier_publication_audit`. This audit reads saved artifacts and current source bytes; it executes no supplier, compiler, verifier, semantic oracle or benchmark. The coordinator's run is the execution evidence. Independent source implementation/review is not external human acceptance.

## Final result

**PASS_INDEPENDENT_SAVED_FULL_PHASE_ARTIFACT_AUDIT: 197/197 checks, 74 files.** Final JSON receipt SHA256: `77e332ba7828418054f1fdf0f9d855d03415761922f42a36c3d656462e22ec31`. The preserved launch source at `orientation/run_allocated.v1.py` independently hashes to `41176c51133889d1f9899e28679ad2c75b92cb1386884ff6e4e5d9bca0e3ee6a`, exactly matching both historical allocations. This resolves the initial current-versus-launch mismatch without relabeling the newer controller as the launch source. All 73 initially inspected artifact files remained byte-identical during resolution.

The final JSON embeds the complete initial audit object and its reproducible byte hash, then separately records the historical controller resolution. The coordinator reports that v1 was archived after the original trials closed, before intentional v2 revisions for future portable allocations. This lane verifies the historical source bytes/pins; it does not independently establish that filesystem-event timing. V2's additional post-leader budget, self-source and signal-cleanup checks are not credited retroactively. The actual completed v1-run duration remains independently within its allocation.

## Preserved initial finding

The first artifact pass completed 193 of 195 checks across 73 files. All phase-output, source-binding, transformation, control, log, command and timing checks passed. Two additional private-controller provenance comparisons failed: both full-phase and driver-control allocations bind controller SHA256 `41176c51133889d1f9899e28679ad2c75b92cb1386884ff6e4e5d9bca0e3ee6a`, while the current `run_allocated.py` is `a99073e0f32b31392639ddec5f519f3aa0659a92e8bdac54a9f9b344ab7891cf`. The historical copy had not been located at this first inspection. The discrepancy was reported promptly and subsequently resolved against actual preserved v1 bytes, as recorded above.

Initial JSON receipt SHA256: `6bc0c1f3f3fce808eea5bec3a2b069d84afb24ee7625da104e196dbd44c6525d`. The embedded historical snapshot retains its initial failure status and both comparisons. The final audit has no unresolved failure.

## Verified payload and execution receipts

The saved outer receipt is `FINISHED_EXIT0`, exit 0, duration 669.357963 seconds within its 3,600-second allocation. The internal result is `PASS_EXACT_SOURCE_BOUND_PHASE_REUSE`, duration 669.091028 seconds, three alternating baseline/candidate pairs. The allocation's exact argv, working directory, source hashes and outer log match the terminal receipt. All six child receipts record exit 0 and match their actual saved logs/reviews by hash. The aggregate log contains the six corresponding PASS lines and final PASS status.

| Artifact | Independently computed SHA256 |
|---|---|
| `FULL-PHASE-RUN-1.json` | `3d8c4aad4870df253e830e58fd6a5667b3e5512b26b2cb058651379427f0fa59` |
| `full-phase-1/RESULT.json` | `c74cd9ad444c4bc8e72e52ea03715ace56adb365d0ea2559396db43f8695f50b` |
| `full-phase-1/SEMANTIC-CONTROLS.json` | `5f16940ba441fae681505b7da5baec0dae0954484050e7ea6957ed851d54fe1e` |
| `driver-controls-1/CONTROLS.json` | `3954670f20a5e0776337ba8f8406431c45d2d73364472540fb5ba9daf74f0a46` |

The exact three retained sources match launch/current/copy hashes: compiler `2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962`, driver `a273c325ffd6793d5b63b79a289a9d2bbc9292e6940fb5a926924f3708627af4`, portable wrapper `322d29d43dbee8130cde15d4bf05396698b5e3dfe3735813899db91cc0ba7955`. The generated compiler is exactly one replacement of `assert out.zero_state()==op.zero_state()` with `assert out.zero_state()==(vec,den)` and has candidate hash `6fac2848d3a0c0dfa92f83c8636beb903083cce1b01bda8ef582514071429221`.

All six complete recipe files are byte-identical and hash to `4629507dcbdd516457c001ff8f9dbe750d1a0cbfa5cfa3c6be003d45804ba0c5`. The committed gzip and decompressed word both match their exact pins. From the saved input JSON, the audit independently enumerated 1,005 frames, 2,949 directed edge/center pairs and 224 endpoint adapters, then matched every recipe's edge/port/role/frame inventory. Each recipe has its absolute phases present, and each review asserts every child equality includes global phase. All proof-relevant review fields agree across six outputs after removing only `seconds`. This checks saved inventory/evidence consistency; it does not reexecute the underlying equalities.

The corrected oracle source is `c7f1b612c720904448d2112721d56bd130ed393ae460a7b30a8a5852c76646e6`. Full replay preflight, positive integrated driver preflight and hostile-environment control carry identical successful semantic receipts: 107 fixtures, 552 basis columns, 14,288 matrix entries, 214 input/compiled/immutability checks, 107 exact output pairs, six mathematical negative controls, six positive guard-reaching runs and three separate CLI rejections. Recorded monomial state counts isolate the actual phase/support/denominator stages and reflect baseline repeated evaluation versus candidate reuse. The positive cases are repeated reachability runs of the same valid circuit, not six distinct fixtures.

All nine driver rejection domains, actual failure log hashes/error markers and isolated argv flags match. Existing-work sentinel bytes/inventory are preserved; the rejected inside-checkout directory is absent; saved input/compiler/driver/oracle/generated-source mutation bytes match their intended faults. The budget control reached an actual phase child and produced a failed timeout receipt without complete recipes. The generated-source rejection is in-process and has no separate subprocess log. Semantic CLI guard raw logs were ephemeral; their outcomes are bound by the exact source, fresh parent success and detailed receipt.

## Timings and claim boundary

| Pair | Baseline phase seconds | Candidate phase seconds | Order |
|---|---:|---:|---|
| 0 | 152.592162 | 97.223542 | baseline, candidate |
| 1 | 112.370569 | 83.853586 | candidate, baseline |
| 2 | 137.070395 | 84.986872 | baseline, candidate |

Independently recomputed medians are 137.070395 and 84.986872 seconds: ratio 1.6128419747621576, or 37.997645% lower candidate median duration. Candidate range 83.853586–97.223542 seconds is below baseline range 112.370569–152.592162 seconds. The outer allocation records the original PR1005 foundation job in the second slot; the coordinator reports overlap during part of the earlier pairs. This lane did not independently audit that other job's exact end time. No quiet or exclusive host claim is supported.

This is supplementary exact-source, same-input U8 **local phase** replay evidence and a host-specific timing observation. The default selected checker and kappa are unchanged. It supplies no transported coverage for PR1004/1005 changed words, class-wide or all-input theorem, all-size realization, physical hosting, global multiplication proof or external human acceptance. Source-only review notes are separately hashed in the JSON and remain source inspection evidence. Final archive and relocated replay remain separate packaging work.
