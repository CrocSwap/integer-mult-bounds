# Verification boundaries

The deliverable includes a deterministic constructor and a separate finite
predicate checker. Literal inverse, sum and native error checks exercise the
actual integer map. No predecessor replay or shared verification code is changed.

All new functions are under 60 physical lines. No recursion or dynamic code
loading is used. The augmenting path uses at most 64 sources, 4,096 graph edges
and 64 backtracking steps. The candidate generator visits at most 65,536 offsets
per key; there are 64 keys. Each offset and payload has exactly sixteen real
coordinates. The semantic fixture count is fixed at 4,164, with two directions.
Every validator raises ValueError in ordinary and optimized Python.

Power of Ten deviation, rules 3 and 9. Python allocates managed integers,
tuples, dictionaries and iterators, and the control harness uses ten bounded
callables. These language mechanisms prevent a literal allocation-free runtime
or a ban on all indirect calls. Bounds above fix all collection cardinalities;
public data have at most 4,096 bits per component. Tables are local arguments,
not a mutable global cache. The maximum live candidate set is one sixteen-value
offset and one graph with at most 4,096 offsets, not the candidate enumeration.
No files, network or subprocesses are opened by the mathematical kernel.
The verifier reads its own package files only for source-bound stdout receipts.
Follow-up is a fixed-capacity native implementation if physical costing is pursued.

The packing format is checked rather than assumed: all offsets must fit signed
bytes, and the packed key/forward/inverse payload must be exactly 3,072 bytes.
Warning-strict normal and optimized execution are registered. The dense Walsh
reference is deliberately simple. Its ordinary arithmetic, table lookup, setup,
Boolean lowering, tape movement and cleanup are not assigned a physical tariff.
