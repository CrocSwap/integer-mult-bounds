# Verification record

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

Both registered modes passed with Python 3.12.13 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/spd-inverse-circuit-witness
```

The expected package marker is
`PASS_REGISTERED_RESEARCH_PACKAGE research/spd-inverse-circuit-witness outcome=completed`.
Each scientific command ends with `PASS_SPD_INVERSE_CIRCUIT_WITNESS`.
The committed receipt is deterministic; it contains no elapsed-time claim.

The full run checks 160 small programs against a separate reduced-group-word
oracle: 40 equivalent and 120 different. There are 137 full literal endpoint
comparisons against separately constructed dense matrices and pivoted dense
inverses. All eight deletions from the source dirty sandwich are detected.
There are 154 exact basis-vector inverse residual checks and fourteen
rejecting controls. Constant identities, self-source queries, final dirty
roles, and a cap of 2^(-40) are included.

Four grid examples force the final trial, at grid sizes 2,3,5,8. The inverse
commutator gives dimension 3 and discrepancy -1/35 at epsilon=1/4. The
stress endpoint has 2^32 lowest-degree words, 66 realization states and a
dimension-33 witness. Its numerator bound is 2112, so the permitted grid
has 2113 points; the first point succeeds.

Four code mutations were made in separate temporary copies: replace true
inverse action by forward action, use only the first grid point, replace
a query source with its destination, and discard final dirty roles. All
four fail in both normal and optimized modes with `--small`. This mode
runs the mathematical checks before source-byte or stored-receipt checks,
so these failures are not hash mismatches. The working source is unchanged.

A preliminary ascending-grid stress run exceeded CPython's 4300-digit
integer-to-decimal conversion limit. The final grid starts at the cap and
passes the same stress depth. The root proof allows either order. No
polynomial bound on rational bit growth is claimed. Larger inputs remain
subject to time, memory and runtime integer-text limits.

The runtime source, source proof, source notices and two consumed fixtures
are retained byte-exact at preparatory commit
`f4c7f3f39311a723989845b394275de876345b81`. Each declared source commit is an
ancestor of this branch. The separate upstream fields preserve the
original pending PR source without requiring its unmerged Git object in
CI. The committed-byte check and read-only Git-free export commands are:

```sh
python3 -B scripts/check_research_commit.py --package research/spd-inverse-circuit-witness
python3 -B scripts/export_research_package.py export --package research/spd-inverse-circuit-witness --output /tmp/spd-inverse-package.tar.gz
python3 -B scripts/export_research_package.py check /tmp/spd-inverse-package.tar.gz
```

The publication handoff records the final archive and its replay results.
The optional full-history wrapper is not claimed: the local checkout is
shallow. Direct checks cover each declared pin, not a complete history
traversal. No proof-kernel, independent human review, native caller,
physical invoice, selected cold replay or complete multiplication theorem
was checked. The selected frontier and complete kappa remain unchanged.
