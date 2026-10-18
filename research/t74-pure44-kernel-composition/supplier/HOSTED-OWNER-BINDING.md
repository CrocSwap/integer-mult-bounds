# Complete emitted owner-map binding

PR1959 (Josie Elliston) identified missing hosted role-time and owner-map hash
comparisons in the selected predecessor. PR2301 (Aaron Wang, with opencode
assistance) executes accepted counterexamples at that boundary. The retained
emitter in this successor already validates its input role times, but the
retained audit does not independently compare those two emitted fields.

The grand entrypoint now runs `hosted_owner_binding.py` on the actual emitted
template, actual admitted owner archive and final strict assembly receipt.
It first requires the runtime owner archive bytes to hash to the immutable
uploaded OWNERS input. It binds the emitted template payload to the assembly's
template digest, then compares every complete role dictionary, including time,
against the admitted owner map and requires the naming archive digest to agree.
All checks remain active under Python optimization.

Two controls exchange the times of equal-width roles in distinct invocations
and corrupt the naming digest. Each must fail its intended predicate. The
original complete records remain unchanged. The independent owner feasibility,
native operations, physical invoice and modern outer checks remain separate.
The final grand receipt requires this positive binding and both rejections;
running an inherited narrower verifier alone does not include this new guard.
No selected predecessor archive or selected project certificate is modified.
