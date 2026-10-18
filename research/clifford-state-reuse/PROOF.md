# Saved-state equality

The exact baseline compiler is SHA256
`2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962`.
Its only generated edit is:

```diff
-assert out.zero_state()==op.zero_state()
+assert out.zero_state()==(vec,den)
```

The generated compiler is SHA256
`6fac2848d3a0c0dfa92f83c8636beb903083cce1b01bda8ef582514071429221`.
The tool verifies both hashes and exactly one occurrence before executing it.
It verifies the generated compiler and unchanged copied driver/wrapper again
before and after each complete replay. Original input and source bytes are
also rechecked. No old phase receipt is accepted instead of a new execution.

Immediately before this equality, the original function calls
`vec,den = op.zero_state()`. This literal evaluator allocates its state vector,
applies the P/X/D/C/global-phase gates, and reduces the integer Gaussian vector
and its dyadic denominator. It reads `op.n` and `op.circuit`; it does not mutate
them, the tableau or any caller-owned object. For identical literal input and
default basis0 its output is deterministic.

Between these two calls, `monomial()` checks the exact denominator and monomial
support, extracts the global phase from `vec[b]`, then composes a new `out` with
that phase. It never modifies `op` or the saved `vec`. `Op.then()` creates a new
operator with a newly concatenated circuit; `out.zero_state()` also creates a
fresh vector. Consequently the second original `op.zero_state()` is exactly
`(vec,den)`, including the normalized denominator and absolute global phase.
The replacement leaves this equality's truth value unchanged for every input
that reaches it, including malformed inputs and assertion failures. All earlier
checks and the final `lower_child()` equality remain executed.

This proof relies on the pinned evaluator's pure deterministic implementation.
It is not a claim about arbitrary overridden/stateful methods or a future
changed compiler. It introduces no persistent cache or cross-operator reuse.
Both source copies must be executed with assertions enabled. Optimized Python
is rejected by the entry points and the retained portable wrapper.

Complete phase comparison covers the same finite word through the unchanged
driver: every canonical frame, every used edge and center transition, every
endpoint adapter, tableau/rank equality, and every absolute phase equality.
The full pinned recipe byte hash prevents a partial or reordered recipe from
passing. Proof-relevant review fields must also agree; only elapsed time may
differ. The separate small-circuit oracle is additional evidence, not a formal
proof of the complete inherited Clifford compiler or multiplication theorem.

Default construction integration would require explicit source-routing and
source-guard changes followed by the full cold construction chain. This package
does not make that integration and does not change kappa.
