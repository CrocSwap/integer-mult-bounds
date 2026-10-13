# Restored signed target forests for CK compensation

**Finite complex-supplier circuit construction with a scoped cost optimum;
no new kappa.** The #626 checkpoint's CK frame-zero compensation can
use six rooted, signed target trees instead of 8,704 independent additions.
The complete replacement has 3,342 additions: 106 preparation, 3,130 residual,
and 106 restoration gates. The unchanged binary-Horner lowering saves
**66,520 real-component scalar primitives in each orientation**.

| Complete CK local program | Selected source | Replacement |
|---|---:|---:|
| Scalar macros, either orientation | 21,936 | 16,574 |
| Forward real primitives | 224,938 | 158,418 |
| Backward real primitives | 224,986 | 158,466 |
| Forward positive prefix bits | 40 | 40 |
| Backward positive prefix bits | 62 | 65 |

The 492 helper registers, native frames, ordered cold/entrance wrappers and
all paid recursive children are unchanged. The chosen circuit fits the
inherited 192-bit local allowance. These are exact circuit counts, not runtime
measurements. Production integration and changed-word global admission are
separate obligations.

## Reproduce

From the repository root, using Python 3.10 or later and only its standard
library:

```sh
python3 -I -B research/complex-ck-target-forest/verify.py
```

Expected final line:

```text
PASS_CK_SIGNED_TARGET_FOREST compensation=8704->3342 saved=66520/66520 forest_floor=16364 columns=716 controls=11+25 kappa=unchanged
```

The command freshly reconstructs the seeded forest, checks the committed
recipe and certificate, prices every macro, and invokes the unchanged native
emitter and scalar/frame/wrapper auditor in a temporary directory. Native
subprocesses use `-I` without `-O`, keeping inherited assertions enabled even
when the parent verifier is optimized. The repository is not modified. Explicit
`--record` regenerates only this package's recipe and expected certificate.

An additional standalone implementation uses dense quarter-grid integers,
column-by-column replay, repeated-division coefficient prices, and Prim's
algorithm rather than the constructor's sparse rational replay and Kruskal:

```sh
python3 -I -B research/complex-ck-target-forest/independent.py
```

It checks both orientations on 366 active columns; the other 350 columns are
identities because no panel gate touches their registers. The primary panel
replay and inherited complete local checker each cover all 716 columns.
Both new implementations were written by the same AI agent; this is algorithmic
crosschecking, not an independent human review or a formal proof assistant.

## Exact finite scope

The domain consists of all 12,432 signed target-pair edges and 112 root edges.
The forest has maximum target depth nine. Every target has either one original
target row as parent, with multiplier `+1` or `-1`, or is a root. Each resulting
nonzero coefficient is implemented separately using the retained lowering.
Both basis changes are fully charged. A superroot minimum-spanning-tree
reduction gives the exact minimum in this class: **16,364 complex primitives**
for the complete compensation panel, compared with 49,624 in the source.
All 12,544 fundamental-cycle inequalities are checked, including both signs.

The class excludes non-unit parent coefficients, helper-basis changes,
cross-macro coefficient sharing, general linear resynthesis, and changes to
the frame schedule. No global circuit optimum or stronger exponent follows.
This is one complete finite enumeration, with seed 39 only breaking equal-cost
ties; there is no timeout, incomplete coverage, or unrecorded restart. No pivot
was necessary. See [the proof](PROOF.md), [recipe](RECIPE.json),
[certificate](EXPECTED.json), and [local sprint claim](CLAIM.md).

Eleven new controls reject missing preparation/restoration, incorrect tree
ordering, a residual sign error, frame changes, source aliasing, a nonminimal
forest, a cyclic/disconnected recipe and omitted coefficient-work clearing.
The missing-preparation mutant deliberately passes helper-only replay: testing
arbitrary target dirt is essential. All 206 distinct addition coefficients in
the original and replacement programs receive a literal primitive replay with
independent target, source and initial coefficient-work symbols.

## Provenance, credit and remaining obligations

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. At assignment, the
accepted selected record was #626/#543 at `51110230636731/31250000000000000`.
During verification, main advanced to `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`
and selected #741/#589/#555 at `0.001661202643272239`. This contribution stays
scoped to #626; no transport to #741 is claimed. All seven runtime source pins
are unchanged on that updated main. The original selection record is preserved
byte-for-byte as `certificates/checkpoints/k492626.json` there; its hash and
historical locations are recorded without depending on the moving selection
pointer. [SOURCES.json](SOURCES.json) binds every consumed input by exact bytes
or decompressed gzip payload and checks the canonical word/programs against
the #626 SPEC. Principal source heads are:

- #626, Chafik Boukhalfa: `660de893d27bb7abd1d5b01b1640207528a5c851`.
- #622, Jeremy Kothe and the K-triangle contributors:
  `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
- Retained #543 bit supplier, eumemic:
  `2065fe4f72a914d907f1046603f5a36f17018535`.

Credit the full retained supplier lineage, especially icekylinx's
direct-delivery/emitter work, DreamingOfClouds' cold-helper/native checks,
Dominik Scholz, jon314159, Dugongue, Rohan Arun and eumemic. The original notices
and licenses remain in their source packages.

This extends [#749](https://github.com/CrocSwap/integer-mult-bounds/pull/749)
(Sricharan Vagvala, rational JP8 target pairs) and
[#759](https://github.com/CrocSwap/integer-mult-bounds/pull/759)
(Oscar Fennell, binary rooted forests and their MST reduction). It supplies
CK coverage, signed rational coefficient-dependent edge prices, an attained
forest-class floor and full CK native replay. No priority is claimed for
restored target bases or the superroot reduction.

Concurrent [#807](https://github.com/CrocSwap/integer-mult-bounds/pull/807)
(David Awad) changes CK helper pairs; this package keeps every helper fixed
during forward compensation. #696/#734/#787 lower/compose coefficient work;
#769 changes CK dyadic runs; #793 reorders JP8 compensation. These are distinct
rewrite classes. Their exact inspected heads are retained in the manifest;
none of their implementation is imported and savings are not assumed additive.
The fixed-middle obstruction in #719 and fixed-order frame obstruction in
#776 are not reopened by this different compensation mechanism.

A typed alternative-compensation construction step, refreshed provider
bindings, and global owner/invoice/outer assembly receipts remain necessary
before production integration. The existing all-size compiler,
common-label/mutable-basis realization, pooled hosting, normalized residual,
precision/tape/exact recovery, analytic-transfer and bit-supplier assumptions
remain inherited. Exact finite replay is not a proof of the full multiplication
theorem. The selected frontier and `upstream/` are unchanged.

Contributed for **@dd-hemant (Hemant)** with substantial **OpenAI Codex
assistance** in the research, code, proof, verification and writing. New files
are under the repository's Apache-2.0 license. See [validation](VALIDATION.md)
for the precise executed checks and exclusions.
