# Exact local error cancellation and a sharper inverse-pair precision guard

FINDING — exact local rounding transfer for the physical inverse-coded pair. This closes one part of the precision question in [PR #5069](https://github.com/CrocSwap/integer-mult-bounds/pull/5069). It supplies a precision guard for the two inverse recodings. It does not admit a complete caller or increase kappa.

[PROOF.md](PROOF.md) states the quantified result, dependencies and limits.
[RESULT.json](RESULT.json) records the bounded exact replay.
[SOURCES.json](SOURCES.json) pins the input bytes at canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf.
This publishes the result from [its Discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/5302); it is the same
contribution, with a committed proof and registered replay.

## Reproduce

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/physical-pair-error-transfer
python3.12 -I -O -W error -B research/physical-pair-error-transfer/verify.py
```

Both registered modes authenticate the declared input bytes and compare the
exact receipt. Source modules load from authenticated source bytes. The written
proof covers the quantified domain; finite fixtures do not replace it.
No full physical caller, native/compiler, Lean or selected-frontier replay ran.
The complete kappa calculation is unchanged.

## Open next questions

Bind the local residual guard to an affordable complete caller and include Gaussian and native residuals.
The remaining contracts block caller admission. See TASK.json and PROOF.md.

## Credit

The proof retains the named predecessors and links their exact sources.
New theorem and checks: Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. This is author-checked evidence, not independent acceptance.
