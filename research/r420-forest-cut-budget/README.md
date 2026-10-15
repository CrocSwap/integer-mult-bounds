# R420 target forests with a checked coefficient budget

This finite bit-circuit construction saves **4,897 binary XORs** in eumemic's
PR543 R420 supplier: **26,916 → 22,019** for the complete local word. The
frame-zero dirt-compensation stage D falls **19,922 → 15,025**, including
every target preparation and restoration operation. It preserves arbitrary
initial helper and target contents, all 660 scalar columns, the 420 helpers,
nine retained copies, and the paid rank profile of mass 5,112.
**No new κ or practical multiplication speedup is claimed.**

During final validation, Oscar Fennell's
[#759](https://github.com/CrocSwap/integer-mult-bounds/pull/759)
independently published the same forest class and 14,921-XOR floor, with
a 15,138-XOR admissible D circuit. We credit that concurrent result and
claim no priority for forest factoring or the floor. This package adds
the exact coefficient-constrained cut optimization, **113 fewer XORs**
than that submitted circuit, an independent derivation/checker, and a
generic Lean compensation proof. Its distinct directory avoids a source
collision with #759's package.

The contribution includes two precisely scoped optimality results:

1. A dummy-root minimum spanning tree certifies **14,921** as the minimum
   XOR count among single-parent forest target-basis substitutions with
   direct residual helper injection. The particular seed-6 optimum needs
   **106 payload bits** and fails the unchanged 104-bit native admission
   check. It is retained as a failing calibration, not the selected circuit.
2. Cutting child-parent edges at target indices **5, 34, 39, 57, 78** gives
   the selected **15,025**-XOR D circuit. Independent dynamic programs prove
   that cost is optimal among **all 2^116 cut subsets of this fixed, oriented
   seed-6 tree**, under the unchanged local prefix allowance. They visit
   724 ancestor states. This does not optimize other trees, rerootings,
   arbitrary target bases, or all circuits subject to that allowance.

A scope-control test makes that limitation concrete: changing just
`parent[32]` from 37 to 34 gives **15,023** D XORs with the same payload
bound and valid exact scalar/frame replay. It is outside the certified
cut family and has not received a separate native or hosted replay.
The frozen 15,025 result is a reproducible restricted optimum, not a claim
to the best known R420 circuit.

| Exact quantity | Original R420 | Uncut calibration | Selected five-cut forest |
|---|---:|---:|---:|
| D binary XORs | 19,922 | 14,921 | 15,025 |
| Complete local binary XORs | 26,916 | 21,915 | 22,019 |
| Forward positive-prefix maximum F | 144,651 | 144,651 | 144,651 |
| Reverse positive-prefix maximum B | 2,270,064 | 20,395,400 | 9,800,790 |
| Bit length of 64 F³ B² | 100 | 106 | 104 |
| Strictly below 2^104 | yes | **no** | yes |

The selected exact payload is
`18606576056688220135806852422400 < 20282409603651670423947251286016 = 2^104`.
The 104-bit entry is therefore a strict pass, not a rounded comparison.

## Reproduce

From the repository root, with Python 3.10+ and its standard library:

```sh
python3 -B research/r420-forest-cut-budget/reproduce.py
```

Expected final line:

```text
PASS_R420_TARGET_FOREST D=19922->15025 ADDs=26916->22019 saved=4897 columns=660 payload_bits=104 cut_states=724; uncut_optimum=14921 rejected_at_106_bits
```

This reconstructs both words, compact recipes and the budget certificate,
compares canonical JSON rather than gzip container bytes, runs the independent
checker, and executes 37 adversarial and positive tests. These include an
independent exhaustive audit of 620 small ancestor states (7,904 cut choices),
the semantic-D substitution premises, and historical source-pin controls.
The checker imports no constructor
or budget implementation: it derives K from A/scatter/B, checks every input
column, exact frame spans and COPY/ERASE lifetimes, the 7,140 non-tree cycle
inequalities, both positive-prefix passes, and a separate budget recurrence.

Optional formal and native checks:

```sh
python3 -B research/r420-forest-cut-budget/reproduce.py --lean /path/to/lean-4.21.0/bin/lean
python3 -B research/r420-forest-cut-budget/native.py --out /absolute/fresh/output --boost /directory/containing/boost
```

Native replay needs a C++17 compiler and Boost headers. It compiles the
unchanged predecessor checkers and tests the original and selected words at
5, 9 and 11 stages: 900, 1,380 and 1,620 formal columns, with 6, 18 and 24
omitted-bridge controls. A deleted restoration ADD remains frame-legal but
fails each native formal-column check. The uncut failure can be reproduced
using `--candidate data/optimum.json.gz --recipe data/optimum-recipe.json
--expect-prefix-rejection`, with those artifact paths prefixed by this package.

The [dedicated CI workflow](../../.github/workflows/r420-forest-cut-budget.yml)
requires finite reconstruction, all controls, the pinned Lean proof and both
native replay modes in one Linux job. It checks the submitted PR head and
retains its file inventory, environment, logs and native receipts as artifacts.
[Review coverage](REVIEW.md) maps these checks to the complete submitted
package and records the local follow-up to PR #774.

## Why the transformation works

Let K_i be the helper support of target i's original compensation. Choose
a rooted forest and prepare `y_i ^= y_parent(i)` with children before
parents. Inject K_i at roots and K_i XOR K_parent(i) at other targets,
then reverse the preparation. If the preparation matrix is A, the full map is
`A^-1(Ay + AKs) = y + Ks`, for arbitrary y and s.

A root costs |K_i|; each forest edge costs |K_i XOR K_j| + 2, charging
both target XORs. Adding a graph-only dummy root converts this exact cost
to a minimum spanning tree. Long paths inflate the cancellation-free
coefficient bound; the second certificate optimally cuts this particular
tree to meet the existing limit. [PROOF.md](PROOF.md) gives the proofs,
counterexample to unrestricted XOR optimality, and exact claim boundaries.

All replacement gates operate at frame zero and the complete state at the
D boundary is identical to the original. The old helper-only H2 syntax and
its literal helper-name extractor reject target mixing; neither predecessor
checker is patched. The semantic replacement checks the actual D operator
and retains all other interface requirements. The native stream admits it
using existing common-frame XOR operations.

Following woklerx's [#1194](https://github.com/CrocSwap/integer-mult-bounds/pull/1194)
and Arham Tahir's [#1311](https://github.com/CrocSwap/integer-mult-bounds/pull/1311),
`test_semantic_bridge.py` now checks the chronological substitution argument:
restoring the original D makes the candidate exactly the original checked word;
the actual D supplies identical values and frames to that unchanged continuation.
This applies their conditional interface argument, without claiming supplier adoption.

## Formal scope and remaining work

[Forest.lean](Forest.lean), compiled with Lean 4.21.0, proves generic XOR
linearity, reverse-circuit inversion, children-before-parent forest execution,
and compensation preserving arbitrary helpers and arbitrary initial targets.
Its seven printed axiom reports contain only `propext` and `Quot.sound`.
There are no `sorry`, extra axioms or `native_decide` proofs.

Lean does **not** bind this R420 file, synthesize the middle helper gates,
prove the MST or budget optimum, or formalize frames, invoices or integer
multiplication. Those finite obligations have written derivations and
independent exact executable checks. The complete hosted parent, whole-owner
invoice and changed-word outer assembly have not been rebuilt; the scalar
saving does not change the recursive profile. Uniform compilation,
common-label/mutable-basis realization, hosting, precision/tape and analytic
assumptions remain inherited. Original local macOS execution is recorded in
[VALIDATION.json](VALIDATION.json); [REVIEW.md](REVIEW.md) records the subsequent
local and hosted Linux finite/formal coverage. No repository-wide suite pass
is claimed.

## Provenance and previous work

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
PR543 source head: `2065fe4f72a914d907f1046603f5a36f17018535`.
The historical selected frontier at this base was #626 with #543,
κ = `51110230636731/31250000000000000`. Source and comparison pins are in
[SOURCES.json](SOURCES.json); the local seed-6 bit-track claim, alternatives
and completed search scope are in [CLAIM.json](CLAIM.json).

The branch now incorporates canonical `main` at
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, whose selected result is #1094,
κ = `836330098538459/500000000000000000`, with the PR589/555 R439 bit supplier.
Our scientific baseline remains the pinned R420 word. The old selected-record
hash is checked against `certificates/checkpoints/k492626.json`, which retains
the identical #626 bytes; the live selection and all frozen certificates stay
unchanged. [REVIEW.md](REVIEW.md) records the upstream comparison and adopted ideas.

Concurrent [#713](https://github.com/CrocSwap/integer-mult-bounds/pull/713)
(Scott Woolsey Biggart) and
[#716](https://github.com/CrocSwap/integer-mult-bounds/pull/716)
(Sagar Thakrar) factor disjoint target pairs. The latter proves a 3,250-XOR
optimum in that narrower class. Our admitted forest saves 1,647 additional
XORs relative to that count. No priority for target factoring is claimed.
Earlier #450/#476/#478 and helper-basis #686/#694 supply related precedents;
their changed circuits are not imported or combined here.

The submission refresh also found
[#742](https://github.com/CrocSwap/integer-mult-bounds/pull/742) (@ellipsi2),
a 3,288-XOR saving using shared donors with disjoint donor/receiver sets.
That is a shallow forest precedent; this package adds arbitrary-depth
forest optimality, exact coefficient-constrained cuts and a generic Lean
proof. [#733](https://github.com/CrocSwap/integer-mult-bounds/pull/733)
(Scott Woolsey Biggart) combines helper and target bases for a larger
8,368-XOR saving. This package keeps helpers untouched during D and does
not supersede that broader construction or claim an overall saving record.

Tree-based XOR synthesis is established prior work. In particular,
[Vandaele, Martiel and Goubault de Brugière, §3.1](https://arxiv.org/pdf/2104.00934)
use successors-first row operations and a minimum-weight spanning
arborescence to optimize a parity table. This package specializes those
ideas to a fixed dirty-helper compensation shear, charges preparation and
restoration, and certifies the actual R420 circuit and its budget tradeoff.
It makes no literature-wide priority claim.

## Open next questions

- Can this exact R420 word receive a complete hosted-parent/whole-owner invoice?
  First bind its native receipts to a hosted exporter and account for every
  changed operation. Local semantic substitution is checked; full hosting,
  precision/tape and outer assembly remain blockers to supplier admission.
- Does the fixed-tree budget method answer a new precision question on R439?
  First compare Gareth Davidson's merged [#915](https://github.com/CrocSwap/integer-mult-bounds/pull/915)
  target compensation and existing invoices. A port needs a distinct question:
  reducing frame-zero ADDs alone preserves the paid profile and does not raise κ.

Prepared by Anthony (@anthonylei), with substantial OpenAI Codex assistance
across independent research, implementation, formalization and adversarial
review panels. This is AI-assisted work, not independent human peer review.
See [NOTICE.md](NOTICE.md) for the retained community attribution.
