# Complete two-qubit centre replay with the Python standard library

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped implementation-equivalence argument with exact finite
conformance. The complete fixed replay from MatShep's
[PR5675](https://github.com/CrocSwap/integer-mult-bounds/pull/5675) now has an
implementation requiring only CPython 3.12's standard library. Its original
command fails with `ModuleNotFoundError: No module named 'numpy'` when run
with `-S`. The new command runs with both `-I` and `-S`, including under `-O`.

The new implementation uses 32-integer tuples for scaled Gaussian matrices
and exact trace multiplicities for centre sums. It reconstructs every group
and conjugacy-class fingerprint, every reduced centre matrix at widths 1..12,
every spectral/projector identity and determinant moment, all 64 literal
tensor Gram entries and the seven predecessor rejection controls. Its complete
scientific result must equal the immutable predecessor RESULT.json. It neither
imports nor executes the predecessor verifier.

The threshold nine, Gram bounds, condition number and group classification
are MatShep's results. This contribution removes an environment dependency;
it does not audit those results or claim them anew. No runtime improvement,
new kappa, supplier admission or selected-frontier change is claimed.

## Reproduce

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -S -W error -B research/two-qubit-stdlib-replay/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -S -W error -O -B research/two-qubit-stdlib-replay/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-qubit-stdlib-replay
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-qubit-stdlib-replay --check-source-history
```

Another CPython 3.12 path can replace the local interpreter. Both registered
commands have a 180-second timeout. The final scientific marker is
`PASS_TWO_QUBIT_STDLIB_REPLAY`. The script writes only stdout, including a
generated SHA256 receipt bound to all six package files and four immutable
source inputs. Nothing is silently regenerated in the checkout.

The four declared source files must be available at their repository-relative
paths. A Git-free export works when it retains this layout; NumPy, Git, a solver,
network access and the predecessor Python program are not runtime dependencies.
The source Python file is authenticated as attribution and implementation
provenance, without being executed.

## Evidence and scope

[PROOF.md](PROOF.md) explains each representation change. All 2,718,720
representative/group trace pairs are enumerated. They yield 26,653 distinct
representative/class/trace buckets; multiplicities and imaginary parts remain
in every centre sum. These counts describe the new implementation's storage
and enumeration, not a new Clifford result.

The new arithmetic controls check all 256 matrix-unit products, 32 phase and
adjoint cases, twelve repeated-trace histogram cases and three rejecting
representation/orbit inputs. The complete command also retains every original
scientific predicate and the full output comparison. The fixed scientific
output is unchanged; the new receipt adds implementation evidence and hashes.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
[SOURCES.json](SOURCES.json) pins the exact predecessor files, historical card
and selected record. [TASK.json](TASK.json) records the refined portable-replay
scope and [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19373381).
The selected source-binding orientation passed. No selected scientific cold
replay, Lean or Docker run is required or claimed for this isolated change.

This fixed implementation does not generalize to larger groups or supply an
all-size mathematical proof. MatShep's all-width argument remains a cited
premise. The selected five framework assumptions, physical/native/compiler
realization, precision/tape/storage, dirty restoration and complete paid
supplier bill retain their status. Independent human and formal proof-kernel
review are unclaimed. The bounded loops, file limits and managed-runtime
Power of Ten deviations are documented in PROOF.md.

## Credit

Credit MatShep for PR5675's group enumeration, centre reduction, certificate,
finite predicates and mathematical results, and PR5549/5594's one-qubit work.
Credit Ali Romman / PR5526 for the general pointwise framework, DLamdata /
PR5547, josecarlosgonzalezroque-design / PR5570 and the retained source lineage.
Existing source notices and credit lines are unchanged. Gaussian arithmetic,
finite regrouping, tensor identities and integer matrix representations are
classical; no literature-priority claim is made. The new contribution is the
standard-library implementation and its stated equivalence argument.

## Open next questions

Can one integer matrix kernel reduce the complete replay cost while retaining
all predicates and source/result comparisons? Begin with a complete-command
profile, then change one bounded kernel and compare all outputs and controls.
No timing improvement or benchmark comparison is established here. The
structured question is in TASK.json. Development stopped at dependency removal.
