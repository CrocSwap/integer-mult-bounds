# Independent algebraic audit of radix-9 coefficient certificates

**Result:** PR628's 54 radix-9 kernel coefficient enclosures are independently
corroborated for all six primitive embeddings. Both submitted radix-9 factor
certificates meet their inherited `2^-128` error target. All 15 mathematical
negative controls are rejected. No defect or new kappa is claimed.

The new checker isolates an algebraic cubic root and works in
`Q[X]/(X^6+X^3+1)`. It uses neither pi nor Taylor/trigonometric approximation
to obtain its independent coefficients. The predecessor's interval engine
is retained solely as the audit subject. See [PROOF.md](PROOF.md).

From the repository root, with Python 3.10+ and no third-party dependencies:

```sh
python -B -I -O research/radix9-algebraic-audit/verify.py
```

Expected:

```text
PASS_RADIX9_ALGEBRAIC_AUDIT: 6 embeddings; 54 coefficient enclosures; 2 submitted factor certificates; 15 rejected controls
```

The command verifies source hashes and byte-compares its deterministic result
with [EXPECTED.json](EXPECTED.json). An optional `--output fresh-file.json`
writes a new receipt without overwriting an existing file. `--generate` is
an explicit authoring mode that skips the expected-receipt comparison.

Run the failure-detection and portability checks with:

```sh
python -B -I -O research/radix9-algebraic-audit/test_verify.py
```

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Audited PR628 head: `0768f97d06c623b8211e651543c66135796b62bf`.
[SOURCE.json](SOURCE.json) pins original input bytes and paths.
[CLAIM.md](CLAIM.md) records the seed-73 assignment, selection and overlap.
[NOTICE.md](NOTICE.md) retains predecessor credit and AI disclosure.

This package adds finite evidence at one coefficient interface. The operator
and scan error analysis is inherited from PR628; the audit does not replay its
scan, root finder, phase oracle, dirty restoration, or full transform. It does
not prove the all-radix or full multiplication theorem. The selected frontier
and `upstream/` are unchanged.

Contributor: **William Lawyer**, with substantial OpenAI Codex assistance.
