# Native local admission of the 400-helper PR2339 words

Both immutable PR2339 words lower through the existing PR2269 native compiler
with **no additional positive-rank child**. This closes the local native gap
listed in PR2339. It does not supply a hosted owner fill, a global program,
an outer certificate, or a new kappa.

Construction: Sagar Thakrar's PR2339 at
`bf1742aee4d855efb8bbd44a8419eddb33a679e5`.
Native chain: Jeremy Kothe's PR2269 at
`b479fc5567bc09ab9185bffe89b62594f36d74e5`.
The original compiler files are byte copies with Git-blob and SHA256 pins in
`pr2269/FETCH.json`; the construction's source inventory remains beside its
vendored words. No source file in that package was changed.

## Exact local result

| Quantity | base | extra |
|---|---:|---:|
| Helpers / arbitrary input columns | 400 / 624 | 400 / 624 |
| Paid profile | {1:2303,2:527,3:386,4:125,5:37,8:8} | {1:2287,2:535,3:386,4:125,5:37,8:8} |
| Paid rank mass / helper width | 5264 / 3408 | 5264 / 3408 |
| Native directed child edges | 2885 | 2884 |
| Distinct rank-zero warp classes | 224 | 224 |
| Simultaneous private zero buffers | 44 | 44 |

The width inventory is `{4:4,5:4,7:36,8:84,9:272}`. The identity
`paid mass - helper width = 1856` survives the complete native replay.
The parent can therefore use these exact local histograms when pricing its
own controller; successful local admission does not establish a feasible fill.

The 64 anticipatory corrections use 32 distinct frame-zero helper inputs.
Each `target += c K_G source` lowers to a monomial warp of the source,
a scalar addition, and the inverse monomial warp of that source. All three
operations occur at frame zero and the source is restored before the next
term. The local recursive rank charge is zero. The emitted streams contain
128 such warp events, 80 handoff warp events in B and 80 inverse warp events
in FULL cleanup: 288 warp events in each orientation. These are still paid
ordinary coordinate work. `LOCAL-CHECKS.json` records the scalar primitive
bound separately; it is not a count of the monomial coordinate scans.

The five new source-field lenders are X fields **1, 4, 6, 12 and 31**, each
handed off at rank four. The existing X-field lender 73 has rank five.
Both arbitrary-input maps restore every source, including those six fields.
The owner/controller must keep those source fields available through their
whole local invocation. Likewise the 32 anticipatory helper lenders must be
owned before the zero-frame precondition begins, not merely from their first
later B event. Exact original IDs are listed in `RESULT.json`.

The 44 zero buffers are distinct private FULL-frame fields allocated during
FULL cleanup and freed at zero. They add no recursive child, but require
**44 simultaneous physical fields** distinct from the restored helper fields.
They cannot be identified with those fields: the native negative controls
reject that substitution. Scalar coefficient workspace and private center
workspace remain the inherited requirements. A global physical reservation
and precision ledger must cover all this ordinary work and storage; neither
is silently discarded by the local profile.

## Orientation and phase coverage

The forward stream realizes the target update; the inverse-transpose stream
realizes its dual. The canonical warp symbol in the backward stream denotes
the inverse-transpose operator, rather than a reversal of the scalar event
order. A unitary monomial's inverse-transpose is its entrywise conjugate.
`orientation_contract.py` emits explicit forward and backward monomial
recipes, independently decodes them, and compares each with the appropriate
exact Gaussian product on all 512 columns. There are 448 recipes and 448
rejecting global-phase mutations per word. The source compiler also lowers
every used regular child edge and every warp with exact phases.

Every word passed 44 independent local controls, 25 wrapper controls,
13 independent recipe controls and 13 raw-word tamper controls. The extra
word additionally passed five file-level tamper controls, including forged
phase/G recipes and a missing inverse warp. Both orientations passed the
strict and permissive Lemma G label checks and the adapter rule; six adapter
mutants and fourteen borrowing mutants were rejected in total.

One test selector required adaptation. The historical Lemma G harness chose
the first non-FULL warp for its deletion mutant. Here the first such warp is
a compensation `0 -> 0` monomial, whose deletion is invisible to frame labels.
`lemmag_stage.py` selects the first *frame-changing* handoff instead. The
unmodified algebra checks reject dropped/changed compensation terms, and the
phase checks cover the frame-zero operators. The exact small diff is
`LEMMAG-ADAPTATION.patch`. No mathematical rule or coverage requirement was
weakened; a frame-label test is not claimed to detect phase-only changes.

## Reproduce

With Python and NumPy, from the repository root:

```sh
python3 -B research/complex-structure-seed39/anticipatory-stage-evidence/interface/replay.py --out /tmp/pr2339-native-fresh
```

The output directory must not exist. Expected final line:
`PASS_PR2339_FINITE_NATIVE_INTERFACE_BOTH_WORDS`.
The stored stages ran separately on CPython 3.14.7 / NumPy 2.5.4. This is
disclosed in `RESULT.json`; no second single-process cold run is claimed.
The combined runner performs those same stages and writes per-stage logs.
Do not use `python -O`: the inherited compiler uses assertions, and the new
runner rejects optimized execution.

The fast evidence-binding command is:

```sh
python3 -B research/complex-structure-seed39/anticipatory-stage-evidence/interface/make_receipt.py
```

It expects `PASS_PR2339_LOCAL_NATIVE_ADMISSION_WITHOUT_GLOBAL_BOUND`.
This binds the retained output files and does not substitute for cold replay.
Source corruption, word corruption and optimized execution controls are
recorded in `VALIDATION.json`.

The aggregator requires the six proof-stage success statuses, binds the
orientation report's canonical content hash and paid profile, and requires
literal `true` for the phase review's rank-zero, exact 512-column product and
global-phase assertions. A follow-on audit had found that the earlier
aggregator accepted a forged orientation hash and a false global-phase flag;
these were receipt-binding gaps, not counterexamples to the cold local
replays. The repaired predicates reject both changes. Reproduce all 52
isolated receipt mutations with:

```sh
python3 -B research/complex-structure-seed39/anticipatory-stage-evidence/interface/validate_receipt.py
```

Expected: `PASS_PR2339_RECEIPT_BINDINGS_52_MUTATIONS_REJECTED`. The follow-on
receipt is `VALIDATION-BINDINGS.json`. Every added predicate is exercised for
both words, including absent fields and truthy non-boolean proof flags. An
honest baseline passes, and changing timing/descriptive metadata also passes.
All mutations run in temporary copies; retained cold artifacts remain byte
identical. This tests receipt acceptance and does not repeat the cold stages.

## Scope and credit

These are finite local certificates, including actual native Clifford
lowering, not a formal verification of the all-size multiplication theorem.
Owner geometry, full-call source access, physical stock, precision, complete
outer admission, analytic transfer and the repository's inherited hypotheses
remain separate obligations. No selected frontier was changed.

The mechanisms and construction belong to Cinna Davis / PR2226
(anticipatory dirty borrowing), Jeremy Kothe / PR2269 (T74 words and native
lowering), and Sagar Thakrar / PR2339 (32 low and five additional high aliases).
Vlado Vojdanovski / PR2322 independently used retired X fields for coherent
high-role handoffs; that PR informed the source-interface review here, but
none of its source was imported. The native chain retains icekylinx's
PR425/433/514 scalar and wrapper machinery, DreamingOfClouds' hyperplane/cold
extensions and Lemma G work, and the attributed Clifford compiler. See the
retained notices. This replay, explicit dual-recipe contract and harness
adaptation were prepared with substantial OpenAI Codex assistance under
Apache-2.0; no independent human review is claimed.
