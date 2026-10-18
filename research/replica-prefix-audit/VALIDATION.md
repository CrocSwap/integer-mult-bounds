# Validation record

Local environment: Windows, CPython 3.10.6, standard library only.
Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.

Completed commands:

```sh
python -B research/replica-prefix-audit/verify.py
python -I -O -B research/replica-prefix-audit/verify.py
python -B research/replica-prefix-audit/test_package.py
python -B scripts/verify_selected_result.py
git diff --check
```

The scoped verifier prints `PASS_REPLICA_PREFIX_AUDIT`; normal and
isolated optimized execution agree with the complete `EXPECTED.json`.
All 13 byte-pinned text inputs were also compared with the base commit's
Git blobs and agree byte for byte, including line endings.
The receipt records 72 calls, 240 replica events, 35,424 helper roles,
12 rejected schedule/ownership mutations, eight exact signed dirty-helper
gadgets, 24 completed boundaries in six interleavings, 384 exact norm
sample comparisons, and six mathematical adverse controls.

All **five package tests pass**: minimal relocation to a path containing
spaces under isolated optimized Python; source byte corruption rejection;
expected-receipt corruption rejection; acceptance of an equivalent gzip
payload repackaged with different compression/header settings; and
refusal to overwrite an existing receipt. The package tests took about
50 seconds on this machine. This is not a performance benchmark.

The selected-record integrity check at the pinned base passed with unchanged
`51110230636731/31250000000000000`. The initial verification refresh still
pointed to that base; upstream adopted a newer frontier before publication.
This audit and its selected-record check concern the original #626 baseline.
Only this new research directory is added;
`upstream/`, production generators and the selected frontier are unchanged.

Separate Codex agents inspected the mathematical and source dependencies.
Review corrections explicitly distinguish scalar restoration from physical
unitary residuals, forbid uncharged cross-family mixing, handle the zero
input in the local bound, and retain compiler-prefix and chart-bijection
assumptions. The finite model was corrected before final validation to
use a separate norm for every `(replica, family)`, matching the proof.

The full repository-wide `make verify`, selected supplier cold rebuild,
47 outer inequalities, Lean, a second interpreter/platform and remote
CI were **not run** for this isolated research addition. Frozen source
receipts are inherited evidence, not fresh execution. All full-size
compiler/hosting/normalization/precision/tape/analytic obligations remain
conditional. No human peer review or full theorem formalization is claimed.
