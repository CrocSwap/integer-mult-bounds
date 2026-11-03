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

Scientific commit: `fe9d549cadae2dc005880f8ff2728dcfe148d5e2`.
The ten-file committed-byte and owner-execute-mode check passed. The
official exporter and its offline integrity check also passed.

The export then passed both direct modes with no Git directory,
`PATH=/nonexistent`, read-only files and read-only directories. All eleven
exported files, including the export receipt, kept their hashes and modes.
The normal run took about 2.25 seconds; the optimized run took about 2.60
seconds. These are local check durations, not speed claims.

Before making the export read-only, two actual file mutations were tested.
Appending an executable failure to the interval source was rejected by its
hash check before execution. Replacing the first coordinate-clique index
with an off-support ray was rejected by the support check. Both files were
restored exactly before the two successful sealed replays.

The final documentation commit changes only this validation record after
the scientific replay. Scientific code, witnesses, expected values, and
source pins remain byte-identical to the scientific commit. The base is a
verified ancestor. Full-history preflight was not run because the checkout
is shallow. No cached unmerged commit is needed by the direct verifier.
Hosted CI remains separate and was not run before publication.
