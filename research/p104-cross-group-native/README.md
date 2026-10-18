# Native binding of the 90-helper P104 cross-group correction

The literal 90-helper word in [PR2521](https://github.com/CrocSwap/integer-mult-bounds/pull/2521)
has exact native frame transports at its stated ranks. **934 directed operators
cover all 1,689 transport occurrences**, including the 279 added occurrences.
All 208 intrinsic endpoint adapters are monomial, and all **136,900 logical
boundary coefficients** over 370 arbitrary inputs pass. The added rank mass is
**810**; the complete rank mass is **3,178**.

This closes PR2521's finite native-frame handoff. Its cross-group construction,
90 helpers and savings belong to ywz65/PR2521 and CubeJerry/PR2504. The
91-helper word certified in [PR2572](https://github.com/CrocSwap/integer-mult-bounds/pull/2572)
is a different input. No new helper saving, complete supplier or kappa is claimed.

## Scope and exact sources

Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The unchanged circuit is retained from PR2521 at
`78e7e4c1032a3f2bce8dae4f3f2bf30ac924b050`. The checker and compiler harness are
adapted, with credit, from PR2572 at
`fe4446d0f94578eec4d89af31f806a132f94ede3`; no predecessor circuit producer, package verifier or compiler is
imported during ordinary replay. The retained exact Gaussian interpreter from
PR1991 is imported only after authentication. [SOURCES.json](SOURCES.json)
records Git blobs, SHA256 values, code ancestry and immutable live inputs.
The scientific card and open questions are in [TASK.json](TASK.json).
The [claim is in discussion #2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18952899).

The combined word has 4,854 events, 208 original data registers, 72 original
dirty helpers and 90 new dirty helpers. Only Y0/Y1/Y2 become `y_t + x_t`;
the other 101 target rows remain `y_t + (Gx)_t/2`. Every persistent source and
dirty helper logical value is restored. Eight inherited private-copy lifetimes
still end in **nonzero disposal**. This package does not strengthen that storage
contract or prove a complete inverse-transpose program.

James Reed / @rcfc-jreed also completed a separate logical/frame/invoice audit
of PR2521 in [comment 6196274543](https://github.com/CrocSwap/integer-mult-bounds/pull/2521#issuecomment-6196274543).
That adjacent audit is credited; the new result here is the native operator and
phase binding, with a repeated endpoint check needed for its composition.

## Finite native binding

1. Reconstruct the 120 doubled E8 root lines and the 104 retained ports. Convert
   compressed labels with the pinned Gram isometry, and check all 14,400 physical
   binary pairings. Compressed labels are not treated as ordinary dot coordinates.
2. Insert PR2521's events at the exact original cuts 0, 669, 842 and 4058. Map
   every frame to its canonical physical basis. Replay all rational input columns,
   checking common frames, the actual source chronology, nested transports,
   private lifetimes and every final coefficient, including zeros.
3. For each actual directed transition A -> B, compile and verify a recipe for
   `Gamma_B Gamma_A^(-1)`. The recipe has one positive child of rank
   `abs(dim B - dim A)` between monomials. Signed-Pauli conjugation determines
   the Clifford operator up to scalar; exact Gaussian action on the zero basis
   state fixes its global phase. The interpreter imports no compiler code.
   The certificate binds each recipe to the complete list of event positions,
   so an equal histogram cannot substitute for occurrence coverage.
4. Check each source-entry and target-exit intrinsic adapter with the actual
   root normal and endpoint frame. All 208 have rank zero.

For a logical state z, maintain physical state `Gamma z`, with one canonical
chart per live register. A verified transition changes its chart and leaves z
unchanged. A common-chart scalar addition realizes the same logical addition.
The inherited private COPY and disposal obey their separately stated contract.
Induction over the literal events therefore gives the finite framed forward map
`Gamma_f S Gamma_i^(-1)`, where S is the fully checked logical endpoint above.
This argument does not price physical source delivery or scalar/address work.

The changed cross-group contacts are the C012_0 branch from the six-dimensional
triple intersection to the seven-dimensional {0,2} intersection, and C012_1's
corresponding {1,2} branch. The two-register shear `(b,t) -> (b+t,-b)` is retained
literally. Tests remove each cross shear and an actual late source capture; all
reject without changing the transport histogram.

## Invoice and evidence

The added profile is
`146 H1 + 36 H2 + 7 H3 + H4 + 8 H5 + 40 H6 + 41 H7`.
The full profile is
`1220 H1 + 94 H2 + 93 H3 + 105 H4 + 56 H5 + 64 H6 + 49 H7 + 8 H8`.
There are 517 added scalar ADDs (3,141 total). Native lowering adds no positive
rank to this finite profile. Boundary rank mass is not a hosted recursive
excess cost, and lifetimes are not simultaneous physical stock.

[RESULT.json](RESULT.json) records the full receipt and canonical native payload
hash. Eight semantic controls reject the two omitted cross shears, a phase-only
fault on the new branch, a missing occurrence, wrong child rank, wrong endpoint
normal, missing branch raise and missing late capture. Behavioral tests regenerate
the complete certificate, compare its decompressed canonical payload, accept
alternative bases for the same binary frames, and check a Git-free source export,
source-before-import rejection, missing pins/evidence, typed receipt drift and
exclusive output. Compression bytes are not mathematical equality criteria.

## Reproduce

Python 3.12, standard library only. Direct replay is read-only, Git-free and
network-free. `--out PATH` creates a new receipt and refuses to overwrite it.

```sh
python3 -I -O -Werror -B research/p104-cross-group-native/verify.py
python3 -I -B scripts/research_package.py --package research/p104-cross-group-native
```

Expected primary output:

```text
PASS_P104_CROSS_GROUP_NATIVE edges=934 occurrences=1689 endpoint_coefficients=136900 added_rank_mass=810 controls=8
```

`build.py --out NEW_PATH` regenerates the native packet; the registered tests
perform this in temporary storage. Validation uses CPython 3.12.3 on Linux.
No human independent review, proof assistant or hosted CI result is claimed.

## Open next questions

A complete backward physical interface remains open for this exact word.
First apply the PR2497/2551/2586 private-copy and boundary-conversion analysis;
edge adjoints alone do not provide that program. The eight nonzero private
disposals are a separate obligation.

To advance the supplier, extend the cross-group construction to all 104 targets
with explicit acquisitions, then price all owner, idle, residual and scalar/address
work. Native lowering does not establish a favorable completed moment. Physical
precision/tape, all-size admission and the selected cold replay were not checked.
These questions and blockers are also structured in TASK.json.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New work is Apache-2.0. No independent human review is claimed.

Credit ywz65/PR2521 for the 90-helper cross-group construction and ywz65/PR2572
for the adapted native verifier, builder and behavioral tests; Nick Petalas/PR2550
for their native-binding pattern; CubeJerry/PR2504 for the literal late-exclusive
component; ywz65/PR2460 and Ross Richardson/PR2445 for the preceding constructions;
commdata2338/PR2393, Hiroki Kumazaki/PR2353 and Philippe Van Velzen for the acquisition
model and bounds. Retain Chafik Boukhalfa/PR1991, Rohan Arun/PR1972, Adam Gall/PR1940,
Josie Elliston/PR1071, Ali Romman/PR1125 and the retained exact compiler/interpreter
and E8 lineage. Predecessor evidence and source notices remain unchanged.
