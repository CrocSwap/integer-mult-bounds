# Two exact fusions in the historical complex coordinate-total factory

**Finite circuit construction. No new κ.** Two three-register identities reduce
Alluri's accepted PR681 coordinate-total circuit from **34 to 32 scalar
operations**. The same exact map appears in all fourteen raw PR622 factory
blocks. Replacing each window and its inverse cleanup saves **56 scalar
operations and 448 real-component primitives per complete raw invocation**,
in either orientation, beyond PR681's already counted savings.

This is a contribution to the historical raw factory, not an installed change
to the selected X4 supplier. The selected conditional κ remains
`1661634653669567/1000000000000000000 = 0.001661634653669567`.

## Reproduce

From the repository root, with Python 3.11+ and only the standard library:

```sh
python3 -I -O -B research/complex-factory-fused-seed23/verify.py
```

Expected:

```text
PASS_COMPLEX_FACTORY_FUSION windows=14 gates=34->32 saved_with_cleanup=56 primitives_saved=448 columns=716 controls=71 no_new_kappa
```

The command checks all 25 source pins, reconstructs the circuit from its two
fusion recipes, runs the unchanged constructor, binds all fourteen physical
windows, and freshly admits both the 34-gate and 32-gate raw words. The first
replay must reproduce every deterministic field of PR681's retained result.
Both complete words run the native auditor, emitter and local auditor. The
71 new rejection controls and four inherited controls per word also run.

Outputs are temporary. `--out /absolute/new-directory` retains generated words
and logs. `--write /absolute/new-receipt.json` generates a development receipt;
the default compares the entire computed receipt to `RESULT.json`. Existing
output directories and receipt files are rejected. All inherited subprocesses
run with assertions enabled, even when the top-level command uses `-O`.

Optional bounded-search reproduction and package controls:

```sh
python3 -I -O -B research/complex-factory-fused-seed23/search.py
python3 -I -O -B research/complex-factory-fused-seed23/test_package.py
```

Expected markers are `PASS_FACTORY_FUSION_SEARCH` and
`PASS_FACTORY_FUSION_PACKAGE relocation=1 payload_repack=1 rejections=7`.

## Exact identities

All indices below are zero-based coordinates in PR681's eight-register template.
The first three instructions are

```text
z3 += z0
z3 -= 2*z5
z5 -= z0/2
```

Replace them with

```text
z5 -= z0/2
z3 -= 2*z5
```

Both give `(z3,z5) = (old_z3 + z0 - 2*old_z5, old_z5 - z0/2)`.
No register is assumed zero. After that substitution, instructions 12, 13 and
16 are

```text
z6 -= z2
z5 -= z2/2
z6 -= 2*z5
```

The intervening instructions `z0 += z2; z0 *= 2` commute with the last of
these three and stay in their original relative order. Replace the triple by

```text
z6 -= 2*z5
z5 -= z2/2
```

Both give `(z6,z5) = (old_z6 - 2*old_z5, old_z5 - z2/2)`.
These are ordinary elementary-matrix identities, not newly claimed algebraic
rules. Their useful application here crosses noncommuting macro boundaries;
PR681's collection pass only collected equal generators across commuting gates.
`CIRCUIT.json` gives the complete 32-gate witness and the two exact splice sites.

The verifier checks equality of the entire ordered 8×8 map, including all
complementary coordinates, on every basis column over the rationals. Linearity
therefore gives equality for arbitrary complex register inputs, including
correlated source values and dirty helpers. It separately checks the main word,
inverse cleanup, inverse transpose, and inverse transpose of the cleanup.
This is a finite linear identity, not formal verification of multiplication.

## Complete local cost and frame interface

Each removed instruction is a signed unit ADD. The unchanged inherited Horner
lowering pays four primitives per real component: initialize coefficient work,
read the source, accumulate into the target, and clear work. There are two
removed ADDs in each forward window and two in its inverse cleanup, fourteen
windows, and two real components: `2 * 2 * 14 * 2 * 4 = 448` saved primitives.
Every remaining source read, coefficient operation and clear is still charged.
There is no additional helper, copy, restoration, frame change or recursive
child. This is a circuit count, not a measured multiplication speedup.

| Complete raw-word quantity | PR681 / 34 gates | Fused / 32 gates |
| --- | ---: | ---: |
| Compensated scalar operations | 15,488 | 15,432 |
| Emitted scalar macros, each orientation | 15,512 | 15,456 |
| Forward real-component primitives | 160,296 | 159,848 |
| Inverse-transpose real-component primitives | 160,344 | 159,896 |
| Forward conservative positive prefix bound | 68,417 | 39,090 |
| Inverse-transpose conservative positive prefix bound | 1,649,462 | 1,301,331 |
| Helpers / arbitrary native input columns | 492 / 716 | unchanged |
| Dirty-input compensation ADDs | 10,632 | unchanged |
| Paid rank mass / distinct directed phase edges | 6,284 / 3,110 | unchanged |

The local paid histogram is unchanged:
`{1:2024, 2:760, 3:300, 4:168, 5:168, 6:44, 8:8}`.
Each block's eight registers still move from their own rank-three entry frames
to the same rank-four frame, once per register. The reordered operations are
inside one contiguous factory window. No external observer occurs between
them. All fourteen frame boundaries and the complete native chronology are
checked, rather than extrapolated from the seed block. Cleanup remains the
literal full-frame inverse of the non-target computation.

For all four orientations the one-real-component window bill falls from
128 to 120. As a stronger comparator, applying Sagar Thakrar's accepted PR696
copy/unit lowering to both windows gives **81 to 77**, or a marginal saving of
**224** real-component primitives across main and cleanup of all fourteen
blocks. This is a local lowering comparison; its whole-program invoice is not
reissued here. The 448 and 224 savings are alternatives, not additive savings.

## Magnitude, grid and failure controls

The inherited PR681 validator proves, by exact computation, that each new
positive endpoint matrix is entrywise dominated by its predecessor and every
new positive prefix row is dominated by an actual old prefix row, for any
nonnegative incoming envelope. This includes the largest coefficient-Horner
intermediate, not only macro endpoints. The complete emitted programs also
recompute their conservative prefix bounds, listed above.

A supplementary dense primitive interpreter checks all eight local input
columns plus arbitrary incoming coefficient-work dirt. For main, cleanup,
inverse transpose and dual cleanup, respectively, maximum binary denominator
depths stay **1, 2, 2, 1**; exact prefix row-L1 maxima stay **12, 8, 10, 12**.
These are local scalar diagnostics on the declared basis. They are not a full
compiler grid, overflow or rounding certificate. The inherited precision
allocation is retained.

The 71 new controls reject deletion and sign reversal of each of the 32 gates
(64 controls), a wrong frame, a Boolean coefficient masquerading as an integer,
dropping the original gate without reordering, endpoint-neutral intermediate
growth, endpoint-neutral cost inflation, a wrong fusion order, and omitted
cleanup in the actual native checker. Rejections must occur for the expected
reason. The full inherited local auditor rejects four additional controls for
each of the two words. Package controls cover source and predecessor corruption,
Boolean coefficients, wrong second-fusion order, a one-primitive invoice
understatement, and preservation of existing output paths. A minimal relocated
checkout with spaces and a differently compressed identical input payload both
pass. Compressed source pins cover decompressed bytes; regenerated receipts use
canonical content identities, preserving all mathematical fields.

## Bounded search and provenance

The operating-system assignment seed was **23**, drawn once with
`secrets.randbelow(100)`. It selected the complex track and initial block
`23 mod 14 = 9`, support `(1,3,4,6)`, original A interval `[1263,1350)` and frame
`span_F2(390,67,37,24)`. Its eight pre-restriction registers are
`[389,384,387,385,394,87,84,85]`. Fresh constructor binding establishes the
common template in all fourteen blocks. `CLAIM.json` records three candidate
tasks, the local claim, scope refinement and overlap checks. No pinned sprint
coordination issue was available; no reservation issue or API request was made.

The search considers every ADD triple at each incumbent whose second and third
members can move left past the intervening commuting operations. It tests all
six ordered two-member subsets, retaining the same registers and coefficients,
exact local map and four-orientation admission. It takes the least tuple
`(primitive cost, indices, pair order)` and stops when no contraction passes,
or after eight accepted fusions. It completed **three passes**, considering
**8,801 ADD triples**, **325 movable triples** and **1,950 ordered pairs**
(pairs with different register support are rejected before matrix evaluation).
Two fusions were accepted; the final neighborhood was empty. This does not
exclude other coefficients, longer rewrites, alternative bases or circuits.
It is not an optimality certificate or a reopened fixed-frame/owner search.

Exact starting commit: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
`SOURCE-PINS.json` gives the SHA256 of every consumed source and receipt:

- PR681: `e536f6fc8aad65adef8ac4682d13625598a5c3f9`, consumed from the imported
  `research/complex-factory5-resynthesis` package in the starting tree.
- PR622: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`, raw K-triangle constructor.
- PR626: `660de893d27bb7abd1d5b01b1640207528a5c851`, retained native checker closure.
- PR696: `5a3f983715027c4fd83f50bc9001d4b18463bed1`, local lowering comparator.

[Rohan Guliani's PR802](https://github.com/CrocSwap/integer-mult-bounds/pull/802),
head `0957b70fc2ed1ac7592467e7a24d6d0788ff6758`, independently audited the existing
87→34 circuit and its PR696 composition. This work changes that circuit to 32;
it does not claim the predecessor's 1,484-operation saving as new. PR802 is
credited related evidence, not a code dependency. Recent PR883/901 concern
different X4 target-pair maps. No pending PR source is imported, and no priority
or compatibility claim is inferred from PR titles.

## Scope, verification and attribution

The historical raw factory is fully rebuilt and its two scalar orientations
are admitted. Transport through later gauge, prefix, frame and cold-end recipes
remains undone. Those recipes depend on the literal word and indices. Fresh
phase lowering, complete Clifford proofs, whole-owner hosting, selected global
invoices and the 47-constraint assembly are outside this package. Unchanged
phase-edge inventory is not presented as a new phase proof. All-size/compiler,
common-label/mutable-source, hosting, precision/tape, analytic-transfer and
bit-supplier assumptions remain inherited. Nothing changes `upstream/`, the
selected certificate, production generators or predecessor packages.

Validation on CPython 3.12.14/Linux: the full package replay passed normally
and under isolated optimized Python; bounded nomination and package controls
passed; `make selected-record-check` passed. The general `make verify`, selected
`make frontier799-verify`, full historical hosted replay, remote CI and Lean
were **not run**. They do not follow from the scoped checks reported here.

Prepared for **Jerry Chen / CubeJerry** with substantial **OpenAI Codex**
assistance in analysis, implementation, verification and writing. No delegated
agent, independent human review or formal proof assistant is claimed.
Apache-2.0 under the repository license. Credit **Alluri / alluri-ritual** for
PR681's exact-map resynthesis, extraction, all-block bindings and validators;
**Jeremy Kothe** for PR622; **icekylinx** for the coordinate-total factory,
scalar architecture and native replay; **Chafik Boukhalfa** for PR626;
**DreamingOfClouds**, **Dugongue**, **Rohan Arun** and the other contributors in
the preserved [source notice](../complex-k492-owner-repair/NOTICE.md) for the
retained emitter, independent replay and supplier lineage; and **Sagar Thakrar**
for PR696. Existing source notices and licenses remain unchanged.
