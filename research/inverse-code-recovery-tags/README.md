# Exact recovery tags with a sharp state bound for the rounded inverse code

FINDING — the rounded inverse-code kernel has a sharp recovery-state bound: 13^8 states, or 30 packed bits, per real scalar coordinate of its 112 owners. Eight separate four-bit quotient tags give a simple 32-bit implementation of the injective output interface. This answers part of the ownership question left by [PR #5035](https://github.com/CrocSwap/integer-mult-bounds/pull/5035); it is not a reversible circuit, a free cleanup rule, or a new kappa.

[PROOF.md](PROOF.md) states the quantified result, dependencies and limits.
[RESULT.json](RESULT.json) records the bounded exact replay.
[SOURCES.json](SOURCES.json) pins the input bytes at canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf.
This publishes the result from [its Discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/5303); it is the same
contribution, with a committed proof and registered replay.

## Reproduce

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/inverse-code-recovery-tags
python3.12 -I -O -W error -B research/inverse-code-recovery-tags/verify.py
```

Both registered modes authenticate the declared input bytes and compare the
exact receipt. Source modules load from authenticated source bytes. The written
proof covers the quantified domain; finite fixtures do not replace it.
No full physical caller, native/compiler, Lean or selected-frontier replay ran.
The complete kappa calculation is unchanged.

## Open next questions

Price a reversible implementation and assign an owner to the retained tags in one complete caller.
The remaining contracts block caller admission. See TASK.json and PROOF.md.

## Credit

The proof retains the named predecessors and links their exact sources.
New theorem and checks: Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. This is author-checked evidence, not independent acceptance.
