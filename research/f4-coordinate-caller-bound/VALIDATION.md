# Validation

The registered normal and optimized checks pass on CPython 3.12.14 on
macOS. Both use the standard library and print
`PASS_F4_COORDINATE_ALL_P_BOUND`. They check the same exact scientific
receipt. No assertion is used to enforce a scientific condition.

The checks cover four forced I5 minors, all 5,050 declared splits for
p=1 through 100, a separate histogram calculation for 100 balanced cases,
and exact outward bounds for the tail value and derivative at p=100.
Six controls reject a ray outside the query support, a repeated ray, an
orthogonal pair, a missing diagonal, a forbidden off-diagonal entry, and
changed interval-source bytes. The source is authenticated before execution.

```sh
python3.12 -B scripts/research_package.py --package research/f4-coordinate-caller-bound
```

The system `python3` is Python 3.15.2 on this host. It can run the direct
verifier, but the registered launcher correctly refuses that version for
this Python-3.12 manifest. The declared Python-3.12 replay then passed.
The first metadata check also rejected a list-valued evidence field. That
field was changed to the required string before replay. Neither correction
changed the witnesses or mathematical result.

The universal ambient-rank, balancing, and concave-tail steps are written
proofs. No independent human or proof-kernel review is claimed. No full
native word, physical caller, compiler, BIT, outer multiplier, solver
exhaustion, Lean, Docker, or predecessor scientific suite was run. Those
checks are not needed to reject the explicitly declared optimistic bill,
but this rejection does not admit a supplier or prove a global ceiling.

Committed-byte and standalone export results are recorded below after
their checks finish. Hosted CI is separate from these author-side checks.
