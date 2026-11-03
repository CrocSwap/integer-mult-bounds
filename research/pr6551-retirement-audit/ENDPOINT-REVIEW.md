# Independent full-endpoint extension after external review

**Result:** both frozen callers pass independent full 35-by-35 endpoint verification in all four exact central fibers, with every stage variable formal. The previous retirement-cut and input-lifetime checks remain. The four requested changed-suffix controls all pass those previous checks but fail the new endpoint calculation with explicit coefficient counterexamples.

This extends the review coverage; it does not change either caller, source claim, invoice, source pin or selected frontier. No predecessor constructor, source checker, lead checker or pricing routine is imported or executed. The new engine reuses only this reviewer's own Gaussian-rational, formal-stage vector interpreter.

## Exact scope

The retained inputs remain PR6545 `775722aa94a5e85b05d1d704d7dca10cbf016f0c` and PR6551 `11ca568cd1a16776ade02b4df09ea04a784cc674`, reviewed through contribution snapshot `13e880a734cc03f2a52c82a412a9a0e6ac2b1f0c`:

- Old controller SHA256: `e5c873568b52aab82fc01670de3037b1ba4bedbcb15366f0e5fb38cd786714ed`.
- New controller SHA256: `419566fe8d8e84a21a14b8efbdac83df5cf1892b0de55f4f256287e9031d74da`.
- Extended checker SHA256: `3b15f6c17d2e7a941c97a29cd4269388cd07f824a4d8df16fc22a62c1515fcf8`.
- Deterministic receipt SHA256: `ff7621c206e1a553c95e41db7a13cd70877aaf4646ccab2d9f603620adcfb5a9`.

The standalone checker reports controller hashes but does not check their expected values itself. The integrated wrapper retains its source-integrity checks before launching this checker; independent source provenance requires the optional Git-object comparison.

## Complete endpoint argument

For each q in `1,-1,i,-i`, the checker starts with each of the 35 unit output rows and propagates it backward through every event (609 old, 611 new). Every one of the 35 resulting input coefficients is compared with its prescribed diagonal coefficient. This is 1,225 formal coefficient positions per fiber, 4,900 per caller, and 9,800 across the two actual callers. The coefficient representation is independent of the lead's complete transfer matrix: each row is processed separately after exact q specialization, with Gaussian rational coefficients and 19-component formal stage-exponent tuples. D0 is retained explicitly and required to be zero in target signatures; D1 through D18 are never numerically specialized.

The existing Chinese remainder argument applies to the full matrices: over `A=Q(i)[D0,...,D18]`, the four factors of `q^4-1` are pairwise comaximal, so evaluation gives an injection `A[q]/(q^4-1) -> A^4`. Exact equality in all four fibers therefore establishes each complete endpoint identity in the claimed formal quotient ring. This is not random testing or a specialization of the stage operators. The written CRT argument is not a formal-kernel proof.

The matrices still use the declared LOCAL, QUERY, IDLE, LAMBDA and ordinary scalar contracts. Physical native maps, all-width substitution, scalar-outside-tensor convention, ordinary work, numerical moments, compiler and outer obligations remain separate. Agreement with the primary replay is implementation corroboration under shared semantic and Python Fraction assumptions, not independent physical admission.

## Independently identified changed region

A maximal literal comparison gives exactly 358 common initial events and 67 common final events. The changed half-open slices are old `[358:542]` and new `[358:544]`. Changed diagonal roles are `20,21,22,23,24,25,26,27,34`. The 345-event retirement prefix is inside the unchanged prefix; this explains why the earlier cut-only checker alone could not detect the requested suffix errors. Identical trailing instructions do not imply identical incoming states, so the extension checks the complete end-to-end map.

## Requested failure controls

Each control first passes the existing cut and lifetime checks, then must raise the specifically typed `EndpointMismatch`. An input-validation or cut-marker failure is not accepted as evidence of suffix coverage. The receipt records the first exact mismatch, including its full formal polynomial, expected polynomial, q fiber and matrix coordinates.

| Invalid change | First mismatch at q=1 | Detection |
|---|---|---|
| Flip event363 `ADD 1 22 1` to coefficient -1 | output23, input20 | Actual coefficient is `2 D10 D11`, expected zero. |
| Remove D11 from event358's five-stage IDLE | output0, input0 | Actual stage monomial differs from the full target. |
| Swap event371 LOCAL source and destination | output0, input0 | Actual diagonal coefficient differs from the required one. |
| Remove D11 from fresh coordinate34's target | output34, input34 | Literal caller retains D11; declared target omits it. |

These four controls preserve the first345 events and pass the original retirement-cut checks. Their endpoint failures are thus direct evidence for the added scientific coverage. The controls stop at the first disagreement; they do not claim a replay of every later mismatch.

Both actual source callers are positive fixtures. A second new positive fixture inserts an inverse half-ADD pair on arbitrary fresh input34 into the changed suffix after event371; all 4,900 endpoint coefficient positions still pass. This tests a semantically valid suffix edit instead of simply rejecting every deviation from the pinned word. The previous canceling-ADD prefix fixture and four previous cut/lifetime rejection controls remain. An additional artificial pivot-column failure was unnecessary: the retained column check remains, and all complete coefficient positions now receive independent coverage.

## Actual commands and results

From the intended checkout after environment activation:

```sh
python -I -B /workspace/work/research-assignment/claude-followup/fibers/cut_four_fibers.py /workspace/work/research-assignment/checkout/research/pr6551-retirement-audit/source/pr6545/CONTROLLER.json /workspace/work/research-assignment/checkout/research/pr6551-retirement-audit/source/pr6551/CONTROLLER.json
python -I -O -B /workspace/work/research-assignment/claude-followup/fibers/cut_four_fibers.py /workspace/work/research-assignment/checkout/research/pr6551-retirement-audit/source/pr6545/CONTROLLER.json /workspace/work/research-assignment/checkout/research/pr6551-retirement-audit/source/pr6551/CONTROLLER.json
```

Both exit0 with `PASS_FOUR_FIBER_RETIREMENT_CUT_AND_ENDPOINTS`; normal and optimized receipts are byte-identical. CPython 3.12.14, standard library only. Normal run: 1.099399 seconds, 11904 KiB child high-water RSS. Optimized run: 1.157566 seconds, 14788 KiB. The measurement wrappers used a 120-second timeout and Python `time.monotonic`/`resource.getrusage`. Full executed interpreter paths, arguments, exit status, stderr and measurements are in [fiber-normal-run.json](evidence/followup/fiber-normal-run.json) and [fiber-optimized-run.json](evidence/followup/fiber-optimized-run.json). No scientific run failed.

The extension was developed and run only in the assigned separate output directory. No project file, Git ref, public message or PR was changed by this agent. The lead integrated the new script/receipt; [FOLLOWUP-VALIDATION.md](FOLLOWUP-VALIDATION.md) records the serial registered package, export and publication-byte checks. The previous reviewed source/caller snapshot is unchanged, while this expanded checker snapshot requires its own evidence.

Prepared for DLamdata with substantial GPT-6 Astra assistance through OpenAI Codex in the independent review role; Apache-2.0. Ali Romman and the retained predecessor contributors keep construction, retirement and native-interface credit. This is AI review, not human or maintainer acceptance.
