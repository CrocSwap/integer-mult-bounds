# PR113 cyclic h24 deferred complex readout certificate

This package reproduces a partial-frame deferred-readout witness on the PR113
cyclic-strip, dual-suffix pair-star producer. Its frozen JSON schedule selects
9,356 scratch roles and 3,309 distinct binary frames. `verify.py` rebuilds
the producer, recompiles the pinned matcher with a binary matching export,
reconstructs the 38,506-role scalar word, and checks its exact rational
adjoint, repaired retained-event closure, every physical role-frame path,
retained and ordinary root reads, arbitrary dirty-scratch side map, binary
phase-frame geometry, charged histogram, and strict moment gap.

Run with Python 3 and a C++17 compiler:

```sh
python3 research/partial-complex-stopped/schedule/verify.py \
  --source-root /path/to/pinned/pr104 \
  --assembly-inputs research/partial-complex-stopped/inputs
```

To cross-check the assembled certificate's histogram, closure size, full
adjoint support of every selected role, and finite scalar toll, add
`--assembly-inputs /path/to/assembly/inputs`. Assertions must remain enabled;
the verifier rejects Python's `-O` mode.

`--source-root` must be the #104 dependency checkout at commit
`948ce1510df750f4c18b96bdaef436a86f8bf834`; critical source files are
checked by SHA-256. `cyclic_producer.py` is an exact byte copy from PR113
commit `0eee4d507092a96bde88de703f07574ba17401a8`, pinned separately by
hash. No pickle files or workspace-specific paths are read. The schedule
stores canonical binary bases and role-to-frame IDs in `selection.json`.

Each matched node gate is split into scalar accumulator and fan-copy events.
The retained closure includes every preceding access on every role, including
read-after-read accesses. This preserves the order of all 209,340 accesses
along each role after the closure-first partition. The verifier checks these
paths and inserts 24 retained-center reads at the closure boundary and 8,096
ordinary root reads at the end. Every selected role is untouched by the
retained closure, and its first write has its original birth label.

The direct initial readout uses all nonselected coefficients of `C=JL`.
Selected coefficients are read later at nested σ frames. For each selected
source frame σ, the first producer edge is the orthogonal residual of its
exact owner label by σ; its last auxiliary edge is the orthogonal sum of σ
and the rank-552 exterior block. Target readouts are sorted by `(dim σ, role)`
and form nested chains to the target hyperplane. The reverse stage uses the
reverse order. The phase exponent is `q_U(k)=wt(P_U k) mod 4`, where `P_U`
is orthogonal projection onto any nondegenerate binary subspace U. This
handles alternating residuals using the pinned
`notes/endpoint-gauge-complex.tex` Gauss normal form. All 4,096,576 copied-output
rank-one corrections remain charged.

The 11,678,073 nonzero direct adjoint coefficients per invocation have largest
absolute integer numerator 42 over the common denominator 42. The finite
scalar ledger charges 16 elementary operations per coefficient use, plus the
cyclic producer's grouped scalar base toll, giving G=758,385,205,952. The
common 21-adic denominator is handled by the pinned rational-center grid.

This verifies finite algebraic and combinatorial evidence for this single h24
witness under the recursive child and machine contracts stated in the pinned
repository. Negative controls exercise owner/frame containment, retained-touch
exclusion, chain nesting, endpoint phase signs, and omission of a copied-output
child.
