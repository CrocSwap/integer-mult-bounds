# Independent checks on the phase-interface experiments

Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.

TL;DR: these checks strengthen the claim boundaries for the PR4610 phase
experiments. They do not increase kappa or prove a complete recursive supplier.

`PhasePreprocess.lean` proves, for positive g,h and 0<t<1,

```
(g+h)^t - g^t < h^t.
```

It also proves the version with a helper gain d satisfying 0<=d<=h, and
strict negativity after multiplying the corresponding loss by any positive
controller multiplicity. This uses strict concavity independently of the
negative-exponent proof in the scalar-contract package. A phase change whose
only effect is preprocessing one independent helper cannot improve the
moment by counting its increased rank as new output. The exact native graph
classification needed to apply this lemma remains a separate Python claim;
the lemma does not assert that arbitrary changed words have that structure.

The fresh Lean receipt binds the three exported axiom reports, exact source,
log, object, compiler and replay hashes. It uses Lean 4.21.0, pinned mathlib
and only the standard `propext`, `Classical.choice`, `Quot.sound` axioms. No
native amplitude evaluator, physical machine bound or multiplication theorem
is formalized by this module. Run `replay_lean.py` with the global Python 3.14
interpreter and the inherited pinned Lean setup to reproduce it.

`route_overlap.py` preserves a small counterfactual against the earlier
unchecked route model. At K=6,G=2, targets [0,1], sources [2,3], and dirty
state (u,t,y,b)=(1,1,32,0), the intended map leaves the state unchanged but
the twelve-swap/ten-rotation word changes t to 9. Both guards pass separately;
their target windows overlap. A byte-identical frozen model is retained in
`sources/`, with its source hash in `ROUTE-OVERLAP.json`.

This input is outside the final grouped interface's stated same-offset,
distinct-chunk contract. It is retained as an explicit rejection control,
not a counterexample to that narrower admitted input. The corrected physical
embedding keeps all selected positions at the same offset in distinct
K-bit chunks, and its route model rejects the overlapping input. The
all-size tape argument and its exceptional repair remain written inherited
proof obligations, distinct from finite controls and Lean address algebra.

Neither the finite route checks nor the preprocessing inequality establishes
a global optimum for PR4610. Multiple paid phase defects, changed subspaces,
maps, scalar order or recursive topology remain outside the one-edge screen.
