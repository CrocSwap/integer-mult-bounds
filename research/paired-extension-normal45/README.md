# Four paired extractions at one hyperplane on PR #2917's words: conditional κ = 0.001722816319863214327996 − 10⁻⁴⁶ − 10⁻⁷⁰

```text
Status / UTC update / priority revision: DONE (conditional candidate) · 2026-10-16 · priority revision 5 · base main 914cd73f
Concrete question and changed premise: PR #2930 showed that the fill layer of PR #2917's words is exhausted (its allocation
    attains their exact packing cap), so a further gain must change the words. Every single further paired extraction on
    PR2917's final word is below break-even. Do several extractions sharing one hyperplane clear it jointly?
Established result and evidence status: yes. Four sequential paired input/output extractions at hyperplane normal 45 (helpers
    249, 267, 251, 265 restored at E_45, ten declared frame edits, 86 private buffers) clear four break-evens by 12,928 units.
    With a new literal T74 allocation of the changed inventory, the complete fresh-native admission and modern outer release
    pass: κ = 0.001722816319863214327996 − 10⁻⁴⁶ − 10⁻⁷⁰, exactly 316413419939763639/10²⁴ ≈ 3.1641e-7 above PR2930
    (head 81f3b5d1) and ≈ 1.2277e-6 above PR2917. Author-checked (AI-assisted); not maintainer-reviewed.
Public artifact URL + exact commit: this package (see the PR).
Next useful task: edits outside the paired-extraction lever (gate re-timing, earlier output gates, entering pivots).
Active claim / expiry: released.
```

## Result

| | κ (headline) | local profile per call | width inventory | private buffers | complete paid profile (T74) |
|---|---|---|---|---:|---|
| PR #2917 (Mason Hale) | 0.001721588647197801880605 − 10⁻⁴⁶ − 10⁻⁷⁰ | {1:2416, 2:640, 3:280, 4:110, 5:26, 8:8} | {4:26, 5:2, 7:62, 8:96, 9:222} | 82 | {1:1625724, 2:426240, 3:191980, 4:73260, 5:24951, 6:167, 7:45, 8:5328, 24:1, 32:207, 48:26958} |
| PR #2930 (cap fill) | 0.001722499906443274564357 − 10⁻⁴⁶ − 10⁻⁷⁰ | same words | same | 82 | {1:1626372, 2:426240, 3:192474, 4:73260, 5:24198, 8:5328, 48:27158} |
| **this package** | **0.001722816319863214327996 − 10⁻⁴⁶ − 10⁻⁷⁰** | **{1:2434, 2:632, 3:286, 4:104, 5:26, 8:8}** | **{4:26, 5:2, 7:62, 8:100, 9:218}** | **86** | **{1:1638360, 2:420912, 3:196337, 4:69264, 5:23531, 8:5328, 14:1, 48:27291}** |

The gain over PR2930 is exactly `316413419939763639/1000000000000000000000000` ≈ **3.1641e-7** (about 0.018%); over PR2917
it is `1227672665412447391/10²⁴` ≈ 1.2277e-6. Physical stock 66,304 + 408 + 8 + 86 + 2 = **66,808**; 632 independent inputs,
408 live helpers, 271,728 helper roles, PR2917's T74 chronology (ORDER/DISPATCH byte-identical).

## Why one extraction is not enough and four are

A paired extraction (PR2908's mechanism, `CONSTRUCTION.md` of PR2908/PR2917) restores one dirty helper `h` at a rank-8 hyperplane
`E_n` instead of rank 9: an input change `S` (dyadic gates at frame zero right after the prelude) and an output change `T`
(gates at frame `E_n` appended to restore) with `S e_h = v, u S = e_h^T, T y = e_h, e_h^T T = alpha`, where `alpha M = u`,
`M v = y`, `alpha y = 1` and `C v = 0`. Then the whole row and column of `h` in `T M S` are the identity, `h` ends at `E_n`
(width 9 → 8), compensation becomes `C S`, cleanup is regenerated and one more private zero buffer is charged. The support
of `alpha` and `y` must lie in registers whose terminal frames are inside `E_n`; registers outside must first be lowered
into `E_n` by frame edits, and every touched register pays.

Prices are the certified frame solver's integer local costs (units of 2⁻⁴⁰ at the base saving b ≈ 0.0017037;
c1 = 2,116,671, c2 = 4,228,346, c3 = 6,338,140, c4 = 8,446,713). An extraction whose pivot ends at rank 8 saves c1, but it
must also force every other register its output gates touch into E_n. It raises the fixed-capacity cap only if the local
bill falls by at least about 2,091,300 units (break-even), i.e. it may spend at most **25,371 units of overhead**.

**Exact cost identity.** The output gates sit at the end of restore at E_n and the input gates are free (frame zero on
zero-entry helpers), so the certified optimum of a composition at one hyperplane depends only on the set U of registers its
output gates touch and the pivot set P:

    total(U, P) = Δ_end(U ∪ P) + c1 · |U \ P|,

where Δ_end(X) is the certified frame-solver change when every register of X ends at E_n (non-pivots then climb back to
FULL, +c1 each). For the shipped composition U = U12 = {2, 61, 62, 63, 70, 71, 72, 94, 249, 251, 265, 267} and
P = {249, 251, 265, 267}: Δ_end(U12) = −25,311,496, plus 8 c1, gives −8,378,128, its certified cumulative change exactly.
The overhead of U12 is 88,556 units, so the margin is 4 × 25,371 − 88,556 = **+12,928**.

* **One extraction is not enough.** On PR2917's final word the best single direction (normals 7/42, U = {76, 233}) has
  margin −4,579; on existing terminal frames only normals 486/504 pair, at −29,645 (the seven-partner 459-block).
* **Four at normal 45 are.** Normal 45's admissible pairing has rank 4, and its 12-register support universe U12 has no free
  registers: a complete rank-4 composition must touch all of U12, whose only helpers are the four pivots. So every order,
  pivot assignment and first-step support gives a total of −8,378,128 or worse; three other orders run through the composer
  (certificate and audit at every step) all end at exactly −8,378,128. The first step alone is 20,801 short; the four
  pivots share one overhead.
* **No other normal helps.** With the same identity, the best unions of up to four minimal supports and each normal's full
  support universe were priced for every normal with a nonzero pairing, on PR2917's word and on the four-step word: no
  other normal has a positive margin (best −4,579 before, −29,645 after), and mixing hyperplanes cannot help (a register
  touched at E_7 and E_45 must lie in their intersection; the cheap 7/42 support uses normal 45's pivots). Within this
  cost model (output gates at the end of restore, the fixed gate order with exactly re-solved frames, zero-entry
  pivots), the four-step composition is the optimum of the paired-extraction lever on these words.

| step | pivot h | inputs / outputs | frame edits | alpha (support) | y | step Δ | cumulative | cumulative − k × (−2,091,300) (negative = above break-even) | local profile after | {8, 9} widths | buffers | fixed-capacity cap |
|---:|---:|---|---:|---|---|---:|---:|---:|---|---|---:|---|
| 1 | 249 | 28 / 10 | 1 | 249, 62, 70, 71, 72, 251, 267 | e62 | −2,070,499 | −2,070,499 | +20,801 | {1:2429, 2:634, 3:282, 4:108} | 97 / 221 | 83 | 0.0017220208645 |
| 2 | 267 | 29 / 11 | 5 | 267, 62, 63, 70, 71, 72, 251 | e63 | −2,100,475 | −4,170,974 | +11,626 | {1:2430, 2:634, 3:284, 4:106} | 98 / 220 | 84 | 0.0017222381993 |
| 3 | 251 | 28 / 11 | 1 | 251, 2, 61, 62, 70, 72, 265 | e61 | −2,098,581 | −6,269,555 | +4,345 | {1:2434, 2:632, 3:285, 4:105} | 99 / 219 | 85 | 0.0017224115901 |
| 4 | 265 | 37 / 9 | 3 | 265, 2, 61, 62, 94 | e94 | −2,108,573 | **−8,378,128** | **−12,928** | {1:2434, 2:632, 3:286, 4:104} | 100 / 218 | 86 | **0.0017228172707** |

(`5:26, 8:8` are unchanged throughout; PR2930's cap of PR2917's words is 0.0017224999064.) The cumulative local change is
`18H1 − 8H2 + 6H3 − 6H4` per call: 18c1 − 8c2 + 6c3 − 6c4 = −8,378,128. Only after the fourth step does the cap of the
changed inventory exceed PR2930's. These prices, the orders and the per-normal census are search-time evidence
(`construction/EXTRACTION-STEPS.json`); the claim rests on the checks below.

The ten declared frame edits are all inherited A gates after the prelude. In each step the last A touch of the step's `y`
register (step 1: `add 57 62`; 2: `add 92 63`; 3: `add 92 61`; 4: `add 57 94`) moves from a rank-8 frame outside E_45 to
the rank-7 frame F7 = ⟨256, 128, 64, 35, 16, 11, 5⟩ ⊂ E_45, which puts that register's terminal frame inside the
hyperplane. Six earlier gates in steps 2 and 4 (`scale 57`, `add 57 92`, `scale 62`, `add 62 63`, `scale 94`,
`add 94 61`) move from rank-4 frames to F7, which contains them, so that the frame chain stays monotone; three of them (the
scales) are individually cost-neutral. Each edit is recorded with its exact old and new frame and its index in that
step's parent word in `data/TRANSFORM-<h>.json`; `producer.refit` (PR2917's rule) checks the exact preimage.

## Packing the changed inventory

The fixed-capacity fractional relaxation of inventory {4:26, 5:2, 7:62, 8:100, 9:218} with local profile
{1:2434, 2:632, 3:286, 4:104, 5:26, 8:8} has the same nine optimal patterns as PR2930's, with moved counts per replica:
[8]×672, [7,9]×334, [8,8]×114, [7,7,9,9]×112, [5,9,9,9]×18, [9,9,9]×84, [4,9,9,9]×234, **[9⁵]×396/5, []×1844/5**;
cap ∈ [0.0017228172707428495209099, 0.00172281727074284952091]. Unlike PR2930's, this basic solution is fractional at T74
(74 × 396/5 = 29304/5), so it cannot be realized literally. The allocation in `allocation/` realizes the integer pattern mix
that a MILP over all 1,163 patterns at T74 reported as best (one [9,9] bin in cap 32, i.e. one idle rank-14 child; solver
optimality, not certified here), built with PR2857's chronological flow model directly on PR2917's T74 chronology (CP-SAT,
one worker, no hint, `construction/`) and edge colouring. Its root is **9.5088e-10 below the cap** (`check_cap.py`
records the exact gap). The coverage-law ceiling of `research/complex-local-word-ceiling` for the new local
profile is about 0.0017572465 (slightly below PR2917's 0.0017580218: the extra rank-1/3 local children cost more than the
idealized idle mass; the gain comes from the width inventory, which that relaxation does not see); the headline realizes
about 98.04% of it and is far above the selected word's ceiling 0.001690054.

## Verification

**Registered, bounded** (`run_registered.py`, standard library, about 20 s):
- complete package pins;
- `verify.py`: `producer.py` rebuilds both WORD files from PARENT (PR2917's words, byte-identical) and the four TRANSFORMs
  (complete decoded content); at every step and for both providers, PR2908/PR2917's unchanged `structure.py` checks the
  seven two-sided identities over the exact free operator algebra; PR2833's unchanged auditor replays both final words
  forward and dual over all 632 inputs (`PASS_INDEPENDENT_EXACT_BORROWING_WORD`, 86 restored endpoints and buffers, the
  profile and inventory above); `frame_report` equals each word's report; 40 semantic mutants are rejected (per step and
  provider: drop an input gate and flip an output coefficient, rejected by the auditor and by the certificate; the output
  change on the wrong hyperplane E_46, a stale cleanup without the new private buffer, and the step's frame edits omitted,
  rejected by the auditor); the overlay producer `tools/wordedit.py` round-trips PARENT → WORD;
- `check_allocation.py`: the vendored PR2839 owner engine on the new allocation (271,728 roles, windows, same-call families,
  capacities, complete profile, physical 66,808) with five rejection controls, and PR2917's exact dyadic moment auditor
  with its authenticated baseline re-pinned to the PR2930 headline (strict gain);
- `check_cap.py`: the Fractions-only cap certificate of the changed inventory (1,163 patterns, primal feasibility, dual
  signs), the literal profile's completeness and its exact gap to the cap, three controls;
- binding of the stored overlay, native, admission and release receipts in `evidence/` to the exact words, allocation and claim.

**Complete replay** (`reproduce.py`): exact Git exports of PR2908 (51309592), PR2917 (224bd5e5) and PR2930 (81f3b5d1), and
through them PR2894 (18d03c44) and PR2833 (e9307b48); fresh retained bootstrap by PR2894's `prepare_retained.py`; PR2857's
four-kernel stage, PR2894's preload stage, PR2908's paired stage and PR2917's extension stage, giving PR2917's derived source
(manifest 98d57c82, 632 files); then `tools/build_overlay.py` appends the stage `normal45-paired-extractions`: the exact edit
spec PR2917 word → this word (`tools/wordedit.py`, cleanup re-derived) is replayed by the source's own `rebuild_borrow.py`
after PR2917's `nine-additional-paired-extractions` stage, so every previous state stays in the audit chain (manifest
79956f19, 637 files); closed adapters for 86 buffers with the PR2917 and PR2930 headlines as pinned comparators; fresh
five-stage native chains for both providers; complete admission (owners, parent lift, rebind, discovery, block norm,
physical/prefix invoice, independent outer checks, and the release, which reruns the admitted source's own verify.py
and its 17-stage rebuild chain for both providers, ending with `normal45-paired-extractions`).

The recorded run (`evidence/`) is a single invocation of this package's `reproduce.py --jobs 2` on macOS arm64, CPython
3.12.13 (numpy 2.4.5, scipy 1.16.1, sympy 1.14.0, mpmath 1.3.0, gmpy2 2.3.2, psutil 7.2.1): fresh retained bootstrap 279 s,
source stages including the overlay 3 s, fresh native chains for both providers 25 s, complete admission 255 s (release 200
s), 562 s wall, ending `PASS_NORMAL45_COMPLETE_REPLAY`. The native receipt's "reused retained" fields refer to the retained
cache that the same run had just bootstrapped (`evidence/FULL-REPLAY-RESULT.json`: `fresh_retained_bootstrap: true`).
Hash-bound receipts are stored verbatim (they contain the run's absolute paths); logs under `evidence/logs/` have paths
replaced by placeholders.

```sh
# exact predecessor commits must be present locally (no network access during the replay)
git fetch https://github.com/CrocSwap/integer-mult-bounds.git \
  81f3b5d12977eba09e06fbff729167d59faabe90 224bd5e56041c40078ff6b5fa7393733a215de5c \
  51309592971e3b5be935599eed2a95404dc7781e 18d03c447886895ef9abf888398178e0428533ca \
  e9307b48d7d1b690939935ecef0f8e524e6d92f4
python3.12 scripts/research_package.py --package research/paired-extension-normal45
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3.12 -B research/paired-extension-normal45/reproduce.py --repo . --work /tmp/normal45-complete --jobs 2
```

The complete replay needs Python 3.12 with numpy, scipy, sympy, mpmath, gmpy2 and psutil (versions of the recorded run in
`evidence/ENVIRONMENT.json`). `--retained DIR` reuses an authenticated retained cache instead of the fresh bootstrap.
For the local checks alone: `python3.12 -B research/paired-extension-normal45/verify.py --work /tmp/n45-local`.

## Scope

Conditional finite supplier and modern outer certificate, exactly as inherited by PR2917/PR2930; all inherited all-size,
compiler, hosting, precision and analytic hypotheses remain. No selected-frontier change, no unconditional multiplication
theorem and no independent human review is claimed. The search and optimality statements are relative to the stated cost
model and census (511 normals; existing and exactly lowered terminal frames; exact at normal 45; at other normals the best
unions of up to four minimal supports and the full support universe), not impossibility results beyond it. No optimality of
the literal fill among integral allocations is claimed.

## Open next questions

1. **Lower the overhead of U12 by edits outside this lever.** The 88,556 units are the certified optimum for forcing U12
   into E_45 with the present gate order. Gate re-timing so that registers 62, 63, 2 and 94 reach E_45 more cheaply,
   output gates placed before the end of restore, or entering-helper (start_extra) pivots are not covered by the
   identity above and could raise the margin or make other normals profitable.
2. **Integral packing at the cap.** The cap basis of the changed inventory is fractional at T74; other chronologies or
   PR2863-style lockstep copies might close the remaining 9.5e-10.
3. **The same joint test on other words.** The identity prices a whole composition with one solver call per (normal,
   support universe); applied to other frontier words it finds every hyperplane whose shared overhead fits under
   k × 25,371 without synthesizing any gates first.

Details are in `TASK.json`.

## Credit

Jeremy Diviney (PR #2908) for the paired input/output extraction method, its compensation rule and `structure.py` (vendored
unchanged); Mason Hale (PR #2917) for the parent words, the refit/compose producer model this `producer.py` follows, the T74
chronology, owner/moment checks, extension stage and adapter derivation; Jeremy Kothe (PR #2894/#2833) for the supplier,
frame accounting and inverse cleanup (`vendor/preload_move.py`) and the source tools; Yiyang Lu (PR #2857/#2848) for the
flow model and realization used to build the allocation; Dugongue (PR #2863/#2839) for the owner-engine lineage; Tekalign
for the independent owner checker; icekylinx for the exact auditor (`vendor/audit_local.py`). See `CREDITS.md` and
`NOTICE`. New work by Marius-Paul Dumitrean, prepared with substantial AI assistance (Anthropic Claude, via Claude Code).
Apache-2.0.
