# #5392 actual oracle case

This standalone folder applies the exact unmodified published #5391 oracle to the new independently evidenced #5392 case. The proposed policy yields **FUNDED_CONDITIONAL, κ .00302725**, subject to its separately required root/auditor policy review. It confers no public or selected authority.

Run from this directory:

```sh
python3 -B verify.py
python3 -O -B verify.py
```

Each invocation takes under one second, reads only local immutable bytes, and executes no author or scientific engine. `POLICY-BASIS.md` explains authority, source/domain coverage, formal-row erratum and explicit raw-cold metadata correction. `case-v1/` is self-contained: candidate, proposed reviewer policy, result, origins and 39 SHA-addressed artifacts. The original #5391 library code/docstring is preserved exactly.

Construction credit remains Ali Romman; library and new consumer work by Chris R / Clear1nsight with substantial OpenAI Codex assistance. Preserve all original native/controller/compiler/precision/Clifford/BIT/analytic notices in the frozen evidence. `build_case.py` is source-specific development glue, not a registered replay dependency; the offline verifier does not run it.
