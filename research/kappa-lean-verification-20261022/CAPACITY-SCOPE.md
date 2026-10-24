# Scope of CompilerCapacity.lean

This module closes two explicit real-power inequalities used by the finite
compiler certificate at the tested saving `c = 302153 / 100000000`, with
`t = 1 - c` and `v = 1024`:

```
(63/64)^1000 < t * 145^(-v*c)
145^(v*c) < 2^1000.
```

It does not trust decimal or rational interval evaluations of a transcendental
function. From `145 < 2^8`, Lean proves `145^(1/8) < 2`. Since `v*c < 3+1/8`,
it then obtains the coarse upper bound `145^(v*c) < 2*145^3 = 6097250`.
Reciprocation and multiplication by positive t give the eta lower bound. The
remaining comparison `(63/64)^1000 < t/6097250` is an exact closed rational
inequality proved by the kernel-checked `norm_num` tactic. The initial-range
bound follows from `6097250 < 2^1000`.

The module has five `#print axioms` commands and uses no `sorry`, `admit`, or
custom axiom. Toolchain and successful command logs belong to the parent
verification receipt. This scalar theorem does not formalize the finite
compiler construction or establish the paid-versus-target moment margin.

Substantial OpenAI Codex assistance; Apache-2.0, matching the repository.
