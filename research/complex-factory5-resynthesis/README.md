# Smaller exact coordinate-total circuits across the complex factory

**Finite local circuit improvement; no new κ.** All fourteen eight-register
coordinate-total windows in Jeremy Kothe's PR622 raw K-triangle constructor
have the same scalar map after register relabeling. A common replacement
reduces **each window from 87 to 34 operations**. Replacing their inverse
cleanups saves **1,484 scalar operations and 10,192 real-component primitives
per raw invocation**, in either orientation. Arithmetic certificates are exact
rationals; every block's distinct physical boundary is checked separately.

The exact repository base remains `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Its selected result is PR626/PR543, κ = `51110230636731/31250000000000000`.
This package changes no existing supplier or selected frontier. Sixteen source
pins bind the actual constructor, inputs, inherited auditors, proof and review.

## Reproduce

From the repository root, Python 3.11+ and the standard library suffice:

```sh
python3 -B research/complex-factory5-resynthesis/verify.py
```

Expected:

```text
PASS_COMPLEX_FACTORY_RESYNTHESIS windows=14 gates=1218->476 saved_with_cleanup=1484 columns=716 controls=14
```

This takes about six seconds on the development macOS/Python 3.14 environment.
It freshly executes the **unchanged** pinned constructor, observes all fourteen
windows, verifies their common scalar template and separate physical frames,
rebuilds both complete raw words and runs the inherited native audit, emitter
and independent local auditor. It compares every deterministic receipt field
with `RESULT.json`. Temporary outputs are removed. To retain words and logs,
add `--out /path/to/new-directory`; the directory must not already exist.
`--write PATH` generates a development receipt instead of comparing the frozen
one. Inherited subprocesses always run without optimization, even if this
verifier is called with `-I -O`. New validation uses explicit exceptions.

Reproduce the search and test package integrity separately:

```sh
python3 -B research/complex-factory5-resynthesis/search.py
python3 -B research/complex-factory5-resynthesis/test_package.py
```

Expected markers: `PASS_SEARCH_FACTORY trials=1024+512 gates=87->34 primitives=310->128`
and `PASS_PACKAGE_CONTROLS relocation=1 rejections=5`. Search code is not imported
by the certificate verifier. No network, external solver, NumPy or SymPy is required.

## Exact objects and accounting

The operating-system assignment seed was **33**, selecting the complex track
and initial block `33 mod 14 = 5`. The package path retains that initial name.
The continuation starts from PR681 commit
`80d4edbc2d53f058787cb5c43bd0fc22c7e7fdff`, which simplified only block 5 to 35
gates. A different synthesis class now finds a 34-gate, lower-primitive-cost
word. Fresh constructor observation establishes the same original 87-gate
scalar template in **every** block, allowing one certified replacement to
cover all fourteen without further search or extrapolation.

`CIRCUIT.json` contains the 8×8 matrix, original 87-gate template, previous
35-gate witness, new 34-gate witness and search receipt. `BLOCKS.json` gives
all fourteen ordered register lists, original section-A intervals and binary
entry/exit frames. The verifier checks the exact inventory 0 through 13,
nonoverlapping intervals and pairwise-disjoint sets of eight registers.

Each window normalizes eight retired donors to a source basis and then puts
the four coordinate totals first. Resynthesis preserves the **entire**
ordered map, including the four complementary coordinates. No helper is
assumed clean and no alternative complement or dirty-input map is introduced.

For the seed block, support `(0,3,4,7)`, the ordered pre-restriction registers
are `[325,320,323,321,330,79,76,77]`. After the constructor's 112-port restriction
they are `[309,304,307,305,314,71,68,69]`, five helpers and three source registers.
The original section-A slice is `[723,810)`, zero-based and half-open. Its gates
are at `span_F2(390,74,44,30)`. Each block uses its own pinned rank-four frame;
each of its eight registers climbs once from its own rank-three entry frame.

| Raw-word quantity | Original | All fourteen replaced |
|---|---:|---:|
| Scalar operations per window | 87 | 34 |
| Scalar operations in fourteen forward windows | 1,218 | 476 |
| Full compensated scalar program | 16,972 | 15,488 |
| Emitted scalar macros, each orientation | 16,996 | 15,512 |
| Forward real-component primitives | 170,488 | 160,296 |
| Inverse-transpose real-component primitives | 170,536 | 160,344 |
| Forward positive prefix bound | 86,491,024,246 | 68,417 |
| Inverse-transpose positive prefix bound | 2,028,759,644,357 / 2 | 1,649,462 |
| Forward / inverse-transpose prefix bits | 37 / 40 | 17 / 21 |
| Helpers / arbitrary input columns | 492 / 716 | same |
| Dirty-input compensation additions | 10,632 | same |
| Paid rank mass / distinct directed phase edges | 6,284 / 3,110 | same |

The paid histogram stays `{1:2024, 2:760, 3:300, 4:168, 5:168, 6:44, 8:8}`.
These quantities refer to the raw constructor, **not** the selected optimized
provider or its global invoice. Prefix bits are conservative arithmetic bounds;
no reduction of the selected payload allowance or practical runtime is claimed.

## Cost, checks and limits

A fixed-frame exact-map substitution can reduce scalar work but cannot improve
the recurrence exponent when all child widths remain unchanged. The complete
bill includes every source read, Horner initialization, doubling, halving,
signed accumulation, binary scale and private-work clear. Each of the main,
inverse and two inverse-transpose windows falls from 310 to 128 real primitives.
Thus the total saving is `14 × 2 windows × 2 components × (310−128) = 10,192`.
The independent emitted-program counts must reproduce this exact difference.
There is no extra helper, persistent copy, route, frame or recursive child.

`PROOF.md` gives exact substitution, composition, scale conjugation and positive
envelope arguments. The full replay covers all 716 arbitrary source, target
and helper input columns, private center clearing and both orientations.
Every new positive endpoint map is entrywise dominated by the original; every
new intermediate/Horner bound is dominated by an actual old intermediate
bound, for any nonnegative incoming envelope. The whole word's bounds are also
freshly recomputed, not inferred from gate counts.

Fourteen new controls reject an omitted gate, wrong sign/source/frame,
non-dyadic addition, non-binary scale, exact-map-neutral endpoint growth,
endpoint-envelope-neutral prefix growth, exact-map-neutral cost inflation,
missing cleanup, missing block, duplicate block, wrong block register and
wrong block frame. Four inherited local controls also run for each full word.

This package does **not** transport the edits through the later prefix, gauge,
frame-regroup or cold-end recipes. Those depend on scalar words and indices
and require separate reconstruction. It does not rerun phase lowering,
residual wrappers, whole-owner hosting, the 47-inequality assembly, the full
repository suite or Lean. An unchanged phase-edge inventory is checked; it is
not represented as a fresh Clifford proof. All-size/compiler/common-label/
mutable-basis, precision/tape, analytic-transfer and bit-supplier assumptions
remain inherited. No gate minimum, larger κ or multiplication theorem follows.

## Bounded research and overlap

`CLAIM.json` records the original three candidates and the continuation scope.
No pinned coordination issue existed. The follow-up keeps assignment seed 33
and updates the existing PR instead of opening another. The retired-row map
remains fixed throughout; this does not reopen decoder or owner-map searches.

The historical 1,024 one-sided Gaussian trials reproduce the previous 35-gate
word. The new domain uses **512 two-sided row/column sparse reductions** with
exact dyadic coefficients and rational seeded score perturbations. Each step
strictly reduces matrix nonzeros. Each trial tests eight middle Gaussian
orders: **4,096 completed orders and 7,137 sparse-reduction steps** in total.
Equal generators are collected only across commuting operations. Nomination
minimizes the fully lowered real primitive cost first, then gate count.

Improvements at zero-based trials 46, 96 and 308 cost 142, 136 and 133 real
primitives, with 38, 35 and 34 gates respectively. Subsequent exact scale
conjugations reduce 133 to 131, 129 and finally **128**, without changing the
34-gate count. This pass stops when no strictly cheaper single-scale relocation
exists, or after sixteen passes; it stopped after three accepted moves.

These are bounded searches, not optimality certificates. Search acceptance uses
exact maps and endpoint envelopes; the separate verifier checks full prefix,
primitive, frame, dual, cleanup and all-block composition obligations. The
other thirteen windows required no search: their literal scalar templates
match exactly under their recorded register relabelings.

PR645 changes the factory's arbitrary-helper-input map and complementary basis;
this preserves both. Concurrent #670/#674 and #688/#691/#694 simplify or compose
**F2 bit-supplier** circuits; this work concerns the distinct rational complex
coordinate-total factory and signed/Horner accounting. Those are related work,
not code or certificate dependencies. Older target-prefix resynthesis (#411)
changes delivery prefixes rather than this exact retired-row map. Current
open heads and overlap checks are retained in `OVERLAP.json`.

Concurrent [PR696](https://github.com/CrocSwap/integer-mult-bounds/pull/696),
reviewed at `5a3f983715027c4fd83f50bc9001d4b18463bed1`, reduces primitive
expansion costs while leaving the selected CK/JP8 scalar macro words unchanged.
This package changes the raw factory macro words under the unchanged inherited
lowering. These are distinct layers; neither combined savings nor compatibility
with that lowering is claimed. Its code and certificates are not dependencies.

## Attribution and license

Prepared for **alluri-ritual (Alluri)** with substantial **OpenAI Codex**
assistance in task selection, implementation, mathematical analysis,
verification and writing. No delegated agent or independent human review is
claimed. Apache-2.0, under the repository [LICENSE](../../LICENSE).

The construction and source material are credited to:

- **Jeremy Kothe / jeremykothe2, PR622**: K-triangle constructor and schedule;
  its notices credit AtomScout, Port480, GlobalR, Stack492 and ColdBeyond, with
  Claude Code assistance. Reviewed source head:
  `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
- **icekylinx, PR531 and PR425/433/523 lineage**: same-partition factory,
  retired-row coordinate totals, scalar architecture and native replay; these
  sources disclose OpenAI assistance.
- **DreamingOfClouds, PR484/604 and predecessors**: gauge/paid-wrapper interfaces,
  emitter and independent local verification, with Anthropic Claude assistance.
- **Dugongue, PR514/522, and the credited PR507 ancestry**: Hamming/scalar
  modules and coordinate-total rank-sector work.
- **Chafik Boukhalfa / chafreaky, PR626**, reviewed head
  `660de893d27bb7abd1d5b01b1640207528a5c851`: the retained owner-repair package
  hosting the unchanged constructor/checkers consumed here.
- **eumemic, PR543**, and the contributors in the selected review: the accepted
  bit supplier and cumulative selected-result lineage, used as context only.

Original files and their notices are read in place, never rewritten or copied
without attribution. See the pinned [full predecessor notice](../complex-k492-owner-repair/NOTICE.md),
[PR531 construction](../direct-delivery504-global/proof/LOCAL-CONSTRUCTION.md)
and [maintainer review](../../docs/research/community-k492-review.md).
