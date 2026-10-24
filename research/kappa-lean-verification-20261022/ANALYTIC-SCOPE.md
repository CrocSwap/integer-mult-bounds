# Scope of AnalyticGain.lean

The Lean module states the exact old and new local paid moment polynomials and
their identity `oldPaidMoment(t) - newPaidMoment(t) = 12 * gain(t)`, where
`gain(t) = 3 + 4^t - 2*2^t - 3^t` uses real powers. It proves strict positivity
for all real `t < 1`, hence the required interval `0 < t < 1`. The module also
states the global identity and strict improvement for 18 full native calls.

The proof bounds the derivative using `(4/3)^t <= 4/3` and
`2/3 <= (2/3)^t` when `t <= 1`. The strict log bound follows from
`log(16) < log(27)`. A derivative monotonicity theorem then compares with the
exact zero at `t = 1`. This does not depend on numerical differentiation,
decimal approximations, interval experiments, or a finite sample of t values.

This is an analytic paid-profile theorem. The formal statement does not assert
that the profiles were extracted correctly from the native word, that a native
warp satisfies its phase contract, or that the full integer multiplication
compiler follows. Those obligations remain in the independently replayed
finite certificates and retained predecessor proofs.

The module contains five `#print axioms` commands. A successful Lean run must
report only standard mathlib logical axioms (`propext`, `Classical.choice`,
`Quot.sound`). No `sorry`, `admit`, or custom axiom is used. Actual checking and
toolchain details are recorded by the parent verification package; the presence
of a source file by itself is not a verification receipt.

Substantial OpenAI Codex assistance; Apache-2.0, matching the repository.
