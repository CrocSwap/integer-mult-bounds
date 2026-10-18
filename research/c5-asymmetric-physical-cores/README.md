# Sharp arbitrary-term asymmetric cost on eighteen physical C5s

This scoped proof extends the single physical-core result in thakrarsagar's
[PR3256](https://github.com/CrocSwap/integer-mult-bounds/pull/3256) to seventeen
additional physical C5 cores. On all eighteen listed in [RESULT.json](RESULT.json),
every finite strict-scalar decomposition over Q, R or C has complete-plane
binary pairing cost at least 20, and five explicit terms attain 20.
Arbitrary asymmetric factors, signs, denominators and finite term counts
are allowed. The transpose is ordinary transpose.

The initial task tested all other 22 cores. Actual tariffs support this
certificate on seventeen of them. The remaining five are explicitly open:
`(3,10,4,6,13)`, `(3,10,12,23,13)`, `(6,13,23,54,26)`,
`(10,12,23,35,16)` and `(14,24,47,18,55)`. Failure of this certificate does
not supply a cheaper decoder.

[PROOF.md](PROOF.md) gives the complete weighted-rank, equality-trace and
finite count argument. The new part checks each actual 1,024-entry
rectangular tariff table, chooses a valid physical cycle orientation and
excludes cost18 and all ten cost19 slack cases. It also checks the complete
cost20 fitted matrix on each accepted orientation. No graph-only transfer
or pending executable is used.

## Reproduce

From the repository root, with an external session-owned TMPDIR:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/c5-asymmetric-physical-cores
```

The registered replay runs the primary checker, a separate reconstruction
and six behavioral control groups. The separate implementation enumerates
all 3,819,816 five-subsets of the 56-plane graph, computes dense binary
ranks, solves rational trace systems and enumerates count states by cost.
It imports neither the primary nor a predecessor executable.

Both geometry inputs are canonical-main blobs declared in VERIFY.json and
pinned in SOURCES.json. An ordinary package export contains their exact
bytes. Direct scripts need only those inputs, this package and the Python
standard library; there is no runtime Git, network or pending-fork dependency.
CHECKS.json records the actual environment and replay/export results.

## Scope and family decision

This closes part of PR3256's explicit other-core handoff. It is a changed
scope from the coverage-law card, a local decoder obstruction rather than
a new coverage identity. The card's working positive control passed.
Priority revision6 and scientific baseline are canonical main
`463113d675af7410ac91d53a4fed51ec6494eb9a`.

The family decision is narrow and complete at this result. No construction
campaign follows. Native payload, legal access, dirty restoration, physical
hosting, precision and the complete supplier bill remain unknown here.
There is no global112-port floor, complete multiplication theorem, supplier
admission, selected-frontier change or new kappa. The scalar proof is written,
not proof-kernel formalized. No independent human review is claimed.

## Verification design

Separate Before Serializing Shared State gave this package its own branch,
cache and exact semantic claim. Shared Git writes use the batch OS lock.
Prove It Works requires the actual physical matrices, exact fitted entries
and a Git-free read-only export before publication. Power of Ten bounds
source files at2MB, decompression at2MB, inventories at32KB, factors at10
coordinates, support tables at1,024 entries, orientations at10 and every
count traversal by its explicit finite domain. Functions stay under60 lines.

Python allocates managed objects during arithmetic, a deviation from fixed
allocation. Fixed physical/source domains and bounded count-state sets bound
live data; no service or unbounded input loop is introduced. Library memory
allocation internals are not audited. Unit-test dispatch is a bounded standard
unittest callback mechanism. Ruff diagnostics and optimized replay check the
touched scripts. No Lean, Docker or unrelated historical replay is needed.

## Open next questions

Can the five named residual cores be settled by a different valid weighted
cover, stronger coefficient constraints or a complete lower-cost identity?
First inspect a failed physical tariff inequality or a surviving count state.
The blocker is the necessary-condition gap, not an observed cheaper fit.
Do not infer a decoder from supports without exact coefficients.

Can a changed endpoint or geometry evade the local floor? Supply a complete
strict fitting identity and independently charge every full source/target
plane pairing. Any construction expansion also needs its native and complete
physical bill. Local floors cannot be added across overlapping cores.

## Sources and credit

The proof method and single-core control are thakrarsagar's
[PR3256 at1ea98246dabb46fc7bedf6127eff63f008414a39](https://github.com/CrocSwap/integer-mult-bounds/tree/1ea98246dabb46fc7bedf6127eff63f008414a39/research/c5-asymmetric-cost-floor).
This package supplies changed physical-table certificates and reproduces the
source core. Its proof is self-contained, with no pending source-object
assumption in fresh CI.

Credit Tekalign/PR2782 for the physical inputs, complete-plane tariffs and
asymmetric handoff; Arham Tahir/PR2879 for the principal-block method;
Sagar Thakrar/PR2484 for the named C5; Cinna Davis/PR1825 for the matching;
Adam Gall/PR1889 for the strict scalar mask; PR3232 for the all-cycle Gram
floor; Nick Petalas/PR3248 at96e3ccd00c62f73d30a23f8d774eea59bfe3b97c
for the complementary all-cycle five-term theorem. Retain ctoth, Philippe
Van Velzen and the E8/P112 and selected geometry lineage. Apache-2.0.

[Canonical investigation and scope correction](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19003538).
