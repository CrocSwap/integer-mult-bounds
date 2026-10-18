# Validation scope and controller replays

I use Python 3.12.15 on macOS arm64. Each registered command authenticates the
97 frozen files and PR2753's transitive repository inputs before execution.
The verifier compares a SHA256 receipt over the complete canonical JSON result
of each suite, including event counts, restoration outcomes and operation meters.
I retain the expected receipts in RESULT.json.

| Suite | Evidence |
| --- | --- |
| frame | Actual selected IDLE source 27825, widths 256→168→84, two repeated frozen-prefix records, exact projected extents, same Word objects/slots/bytes/heads after return. Controlled 23-bit bodies. |
| frame failures | Constructor failure after PARK and a deeper child failure; initiating error and parent state survive cleanup. |
| continuation | 36 good/fallback traces, 16362 compared events and 180 reconstructed return cursors. Width quotients 1,2,3,63,64,65,127,128,129. |
| role parking | 1500 nested frames, four permanent stream roles, three allocated index slots, 1501 protected output symbols. Exact composed table charge 1051500 steps. |
| controls | Nine complete-result transfers; short/out-of-range/overlong finite-control records and a dirty child role reject. |
| nested | Complete 9216-address GL2 payload, 12 shared-bank child calls/returns, 156 residuals, 12 root-stock and 144 child-stock checks. Independent address provenance oracle. |

For the generated-controller implementation I add:

| Suite | Evidence |
| --- | --- |
| macro_nested | Complete 9216-bit recursive GL2(F2) caller through 483/63 emitted instructions and 5859 macros; 12 serialized child calls/returns and 156 residuals. Same complete payload as the pinned logical replay. |
| macro_local | Complete 31104-bit, four-family GL2(F3) caller through 25415 instructions; 192 MOVE, 96 COPY, 384 IDLE, bridge and exchange. Independent projector checks for all 96 private COPY results before cancelling XORs, plus both intermediate sweeps. |
| macro_selected | Actual selected native rank-42 adapter/child coefficients 0/2, width 256→168, exact descriptor/gap, repeated prefixes, saved successor PC and parent restoration. Controlled 23-bit body and reduced role inventory. |
| ownership | Reject stale reads, pool exhaustion and new physical Tape/Arena construction; stale cleanup preserves a newer borrower. |
| primitive reuse | Complete 1458-bit nonzero remainder peel and 2430-bit two-digit modulus-9 swap, preserving their independent spectator coordinates. |

I disable the source recursive Invocation constructor during both complete
controller replays. I also forbid physical Tape and Arena construction inside
the completed source blocks. The q2 run uses at most 20 scratch leases from 132
fixed roles; the q3 run uses at most 25 from 137. Both erase the root's owned
markers/templates and leave no parent frames on the parking tape.

The q2 fixture uses one family, cutoff 2 and root coordinate projectors; its
children execute all twelve conjugated GL2 good/fallback forms. The q3 fixture
uses n=2, w=1, weights (2,1), all 48 lows and external gap 2. I precompile its
finite coordinate-zero coefficient table and validate each runtime source/view
and zero high field. Production instead calls the retained selected coefficient
implementation, which the selected junction suite also exercises.

I completed all seven registered commands with exit code 0 on 2026-10-16 under
Python 3.12.15/macOS arm64, after the parent-identity correction. The launcher
reported `PASS_REGISTERED_RESEARCH_PACKAGE`. The recursive controller took
104.67 seconds and the complete four-family controller took 321.60 seconds.
These timings describe the local simulator; I infer no asymptotic saving from
them. RESULT.json pins the complete JSON receipts, not wall-clock timings.

I reproduced starship-s's [wrong-parent audit](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18960884)
against the old checker: 86 ENTER, 42 INVOKE and 86 RETURN mutations retained its
positive digest. I corrected both comparison paths before signature projection.
The current controls reject None and foreign parents for each boundary kind on
both paths, and the generated selected gate rejects missing/foreign parents and
the wrong source code before capsule preparation. I keep object addresses out
of deterministic receipts.

The auditor also reported a 300-second timeout in the old registered logical
nested suite, followed by a separate 281.28-second pass on Linux/CPython 3.12.13.
I preserve that portability limitation. The current controller delegates lease
loops to the same literal Tape methods to reduce simulator overhead; exact API
traffic controls cover that change. I have not run the current package on Linux.

At the 02:44 UTC submission checkpoint I fetched canonical main
`c719a5e0b3a6760a6fdf5d5af82d6ff2399329e5`. The maintainer changed one entry
in selected-result.json after making the HPE Lean verifier read UTF-8 explicitly
in commit `2dfb25cd3c762a2b24ba732a28bb21e4d331687a`. I checked that exact
one-field difference; the selected parameters and our ten other runtime inputs
remain unchanged. The loader accepts either complete selected record by exact
SHA256 and Git blob, then passes an in-memory manifest to the frozen verifier.
I preserve the 97 exports and their original manifests byte for byte. Each
suite also rejects unrecognized parameter and proof-manifest mutations.
The first refreshed registered replay exceeded the 30-second continuation
limit; I then passed that suite alone in 48.08 seconds. An experimental budget
of 45/45/75/75/240/600/120 seconds passed both Frame and both continuation
commands, then timed out in macro_nested. I restored the original manifest
budget, under which I had completed the seven-suite run above. I claim no
complete registered pass after the submission refresh. The new authentication
and mutation controls passed normally and with assertions disabled; the
controller, primitives and payload oracles have no changes from the complete
pass at implementation commit `61f4d7ce`. These timeout observations concern
the local simulator and remain a reproducibility limitation.

For the original proof/adapter submission I completed all five registered
commands with exit code 0 on 2026-10-15. The
launcher reported `PASS_REGISTERED_RESEARCH_PACKAGE`; the complete nested
payload took 150.31 seconds under Python 3.12.15. The frame and continuation
commands also passed with `-O`; their acceptance checks use explicit exceptions.
I ran the pinned GL2 oracle with ordinary Python.

I then fast-forwarded the isolated branch to canonical main
`28f54620ff770dd051d5df35882bd84303d13c6f` and authenticated the complete source
inventory again. The registered runner, declared runtime inputs, guidance and
selected record had no changes. I did not repeat the unchanged payload suite
after that refresh. The source selection/provenance base remains
`31452ecd309f32a97e2e84214719b21297a59018`.

The registered manifest now replaces the old logical `nested` replay with
`macro_nested`, which checks the same complete payload through the generated
controller and additionally enforces fixed allocation and root erasure. I retain
the historical suite, receipt and optional command:

```sh
python3.12 -I -B research/selected-bit-physical-caller/verify.py --suite nested
```

The seven registered commands have a combined maximum of 1200 seconds. Frame and
continuation suites run normally and with `-O`; the complete generated fixtures
and selected/ownership controls use explicit `need` checks. I have not expanded
the whole selected controller to a microtransition table or executed its GL64
payload. The source-level proof carries that parametric refinement obligation;
these reduced fixtures do not instantiate the selected stock multiple or prime.

I ran the task card's historical owner-boundary positive control and the current
baseline binding check. Those checks establish orientation and source bindings;
they are not new mathematical results or the selected complete cold replay.
This package changes no selected construction file, parameter or certificate.
