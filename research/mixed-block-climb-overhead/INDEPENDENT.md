# Independent internal check

An independently tasked OpenAI Codex mathematical specialist rederived the
full invoice and the isolated-versus-aggregate distinction, reviewed the
parent proof and checker, and implemented `independent.py` without importing
the parent or retained arithmetic engine. This is internal AI review, not
independent human review or formal verification.

The standalone checker uses positive atanh logarithm series with an explicit
geometric tail, range reduction to `[1,2)`, and positive exponential Taylor
series with another explicit tail. It uses exact rational operations and
rounds interval bounds outward on a `2^-200` grid at stage boundaries.
It imports no project code and can run outside Git.
The methods are standard and also occur in Douglas Colkitt's PR1240 engine;
the implementation is separate rather than copied from that source.

Its 175 checks include 73 rational zero-saving and 73 square-root oracles,
all seven paid masses, all seven target signs, all seven failures at 1/99,
the unchanged baseline rejection, a uniformly charged rejection, and the
false pass caused by refunding transport mass from old idle. It certifies

```text
P1: [0.998883185907233421083005024184,
     0.998883185907233421083005024185]
P5: [0.999994967530944867096344001447,
     0.999994967530944867096344001448]
P6: [1.000271925593698224749804918076,
     1.000271925593698224749804918077].
```

The specialist found no material mathematical or accounting error in the
submitted argument. A suggested tightening was applied: the parent now checks
every member at 1/99 rather than checking only P5. An initial incomplete
worktree lacked the parent's pinned engine; that source-availability gate was
resolved by materializing the exact sparse inputs before final replay.

The written monotonicity proof covers all `0<a<1`; numerical acceptance is
claimed only at the one rational target. The native identity, arbitrary-dirty
restoration construction, physical stock/hosting, precision and joint outer
transfer are outside this check. No physical realization or kappa follows.

Prepared for Ross Richardson with substantial OpenAI Codex assistance.
New work Apache-2.0.
