# A conditional restored Tensor error guard with suffix contraction

DONE / scoped finding — the downstream error join requested after [PR #5295](https://github.com/CrocSwap/integer-mult-bounds/pull/5295) is complete at the conditional analytic level. The [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664#discussioncomment-19150254) is released. The source production accuracy, primitive and physical premises remain explicit. No policy, supplier or kappa is changed.

[PROOF.md](PROOF.md) states the quantified result, dependencies and limits.
[RESULT.json](RESULT.json) records the bounded exact replay.
[SOURCES.json](SOURCES.json) pins the input bytes at canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf.
This publishes the result from [its Discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/3664#discussioncomment-19150284); it is the same
contribution, with a committed proof and registered replay.

## Reproduce

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/tensor-restored-error-join
python3.12 -I -O -W error -B research/tensor-restored-error-join/verify.py
```

Both registered modes authenticate the declared input bytes and compare the
exact receipt. Source modules load from authenticated source bytes. The written
proof covers the quantified domain; finite fixtures do not replace it.
No full physical caller, native/compiler, Lean or selected-frontier replay ran.
The complete kappa calculation is unchanged.

## Open next questions

Apply the bound to one admitted production geometry while retaining the source precision and primitive gates.
The remaining contracts block caller admission. See TASK.json and PROOF.md.

## Credit

The proof retains the named predecessors and links their exact sources.
New theorem and checks: Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. This is author-checked evidence, not independent acceptance.
