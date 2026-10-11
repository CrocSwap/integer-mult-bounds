# Source attribution

This package is licensed under Apache-2.0, following the repository.
Prepared with substantial OpenAI Codex assistance.

The immediate source is the unchanged `pr364-kernel-extension` package
published in [PR369](https://github.com/CrocSwap/integer-mult-bounds/pull/369),
at package commit `dcb21903720bd2e30b1eadef680f39e4fc2d7232`. Its NOTICE,
PROOF and all preceding credits remain applicable.

The recursive raising/lowering propagation rule is Rohan Arun's existing
public cascade method; see
[casc.py at research-tools commit 4a57eb9b](https://github.com/rohanarun/integer-mult-bounds/blob/4a57eb9b2d450b87e9db5c514b5a088ec401d761/research/kappa-research-tools/casc.py).
This work adapts that rule to the existing p10b frame-chain and source-span
model. Chafik Boukhalfa supplies the inherited frame algebra, descent,
retiming emitter, shared-donor kernels and banking methods. Rohan Arun
supplies PR364 and PR366's retained 123-gate construction. Jacob Sussman
supplies E8, integrated by DaysSky. Earlier source notices are unchanged.

The new contribution is the ten selected gate frames, their source-bound
composition on PR369 and the resulting exact finite verification and price.
No invention of recursive propagation, frame descent, the moment engines,
finite bootstrap transfer or upstream construction is claimed. Discovery
was a bounded heuristic search, not a proof of global optimality.
