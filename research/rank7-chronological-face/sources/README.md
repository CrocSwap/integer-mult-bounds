# Joint rank-7 end frames, five more paired extractions and PR #2957's rewrites on PR #2942's words: conditional κ = 0.001729033982646513517717 − 10⁻⁴⁶ − 10⁻⁷⁰

```text
Status / UTC update / priority revision: DONE (conditional candidate) · 2026-10-16 · priority revision 5 · base main 484a8ade
Concrete question and changed premise: the fill layer of PR2942's words with PR2957's rewrites is exhausted (PR2969 attains
    their packing cap), so a gain must change the words. Paired extraction restores helpers at rank-8 hyperplanes, and every
    further extraction on PR2942's words is below break-even. Can restored helpers end one dimension lower (at shared rank-7
    subspaces), and does that make further extractions profitable?
Established result and evidence status: yes. Lowering the end frames of 22 restored helpers jointly, in five groups that
    each share one rank-7 subspace (frame-only), pays where every single lowering loses; it makes five further paired
    extractions profitable (normal 42: 226, 228, 230; normal 7: 363, 395); Jeremy Kothe's fourteen PR2957 rewrites compose
    exactly on top. With a new literal T74 allocation, the complete fresh-native admission and modern outer release pass:
    κ = 0.001729033982646513517717 − 10⁻⁴⁶ − 10⁻⁷⁰, exactly 4998757898408639167/10²⁴ ≈ 4.9988e-6 above PR2969
    (Dugongue, head e2ca469b) and ≈ 4.9997e-6 above PR2966. Author-checked (AI-assisted); not maintainer-reviewed.
Public artifact URL + exact commit: this package (see the PR).
Next useful task: census of one-dimension lowerings of the five new pivots and their partners; normals 25/52 with other pivots.
Active claim / expiry: released.
```

## Result

| | κ (headline; each − 10⁻⁴⁶ − 10⁻⁷⁰) | local profile per call | width inventory | private buffers |
|---|---|---|---|---:|
| PR #2942 (our four normal-45 extractions) | 0.001722816319863214327996 | {1:2434, 2:632, 3:286, 4:104, 5:26, 8:8} | {4:26, 5:2, 7:62, 8:100, 9:218} | 86 |
| PR #2957 (Jeremy Kothe; PR2917 words + 14 rewrites) | 0.001723717415070738170971 | {1:2412, 2:636, 3:276, 4:116, 5:26, 8:8} | {4:26, 5:2, 7:62, 8:96, 9:222} | 82 |
| PR #2966 (Jeremy Kothe; PR2942 words + 14 rewrites) | 0.001724034272523452177412 | {1:2430, 2:628, 3:282, 4:110, 5:26, 8:8} | {4:26, 5:2, 7:62, 8:100, 9:218} | 86 |
| PR #2969 (Dugongue; same words at T370, outer release pending) | 0.00172403522474810487855 | same as PR2966 | same | 86 |
| **this package** | **0.001729033982646513517717** | **{1:2445, 2:706, 3:232, 4:108, 5:18, 8:8}** | **{4:26, 5:2, 6:16, 7:52, 8:99, 9:213}** | **91** |

Exact gains of the headline: over PR2969 `4998757898408639167/10²⁴` ≈ **4.9988e-6** (0.290%); over PR2966
`999942024612268061/(2·10²³)` ≈ 4.9997e-6; over PR2957 `2658283787887673373/(5·10²³)` ≈ 5.3166e-6; over PR2942
`6217662783299189721/10²⁴` ≈ 6.2177e-6 (`check_cap.py` recomputes all four from the pinned CLAIM.json files). The complete
paid profile (T74, PR2917's chronology, ORDER/DISPATCH byte-identical) is {1:1645680, 2:470196, 3:159468, 4:71928,
5:13716, 8:5328, 48:28190}. Physical stock 66,304 + 408 + 8 + 91 + 2 = **66,813**; 632 independent inputs, 408 live helpers,
271,728 helper roles. PR2969's kappa is a moment nomination whose outer release is pending; this package's admission uses
it as the pinned comparator and its T370 ORDER/PROFILE as the moment baseline, and passes the complete release itself.

## The three stages

| stage | change (both providers, one declared record each) | local profile after | inventory after | buffers | literal price (units) | freed width units | margin | fixed-capacity cap |
|---|---|---|---|---:|---:|---:|---:|---|
| parent | PR2942's words | {1:2434, 2:632, 3:286, 4:104, 5:26, 8:8} | {7:62, 8:100, 9:218} | 86 | | | | 0.0017228172707 |
| 1 | 22 end frames lowered to five shared rank-7 subspaces; 139 gate frames (B 60, restore 79), each one dimension lower | {1:2430, 2:722, 3:236, 4:102, 5:18, 8:8} | {6:16, 7:52, 8:94, 9:218} | 86 | −46,150,994 | 22 | +142,394 | 0.0017262265796 |
| 2 | five paired extractions (normal 42: 226, 228, 230; normal 7: 363, 395), one declared frame change | {1:2449, 2:710, 3:236, 4:102, 5:18, 8:8} | {6:16, 7:52, 8:99, 9:213} | 91 | −10,523,403 | 5 | +66,903 | 0.0017278107473 |
| 3 | Jeremy Kothe's fourteen PR2957 rewrites, re-addressed with exact preimages | {1:2445, 2:706, 3:232, 4:108, 5:18, 8:8} | unchanged | 91 | −52,350 | 0 | +52,350 | 0.0017290357649 |

(`4:26, 5:2` are unchanged throughout.) Prices are the certified frame solver's integer local costs in units of 2⁻⁴⁰ at the
base saving b ≈ 0.0017037 (c1 = 2,116,671, c2 = 4,228,346, c3 = 6,338,140, c4 = 8,446,713, c5 = 10,554,378); `verify.py`
recomputes every literal stage price from the frame-report profiles. Each lowered or extracted helper saves c1 locally (one
rank less in its end climb) and frees one width unit, which costs about 2,091,300 units of idle rank in the packing at
fixed capacity (the break-even); margins are −price − k × 2,091,300, so each helper may spend at most about **25,371
units** on its partners. The caps are exact (`check_cap.py`, fixed-capacity
fractional relaxation, Fractions-only certificates for the parent and every stage).

### Stage 1: why single rank-7 lowerings lose and joint lowering pays

A restored helper `h` (one whose end frame is a declared `helper_final`, with its own private cleanup buffer) can end at
a smaller subspace W if every gate touching `h` has its frame inside W. Lowering `h` by one dimension saves one rank of its
end climb, but the gates touching `h` are mostly restore gates that it shares with other registers (its *partners*); their
frames must drop into W too, and the partners pay to climb back. A necessary condition is that W contain `L_h`, the solver's
lower bound at `h`'s last vertex; over all 86 restored helpers exactly 20 (end dimension 8, `L_h` of dimension 7, so
W = `L_h`) plus PR2942's four normal-45 pivots qualify, and no helper has room for two dimensions.

Priced alone, every one of the 24 candidates is below break-even. But helpers whose `L_h` coincide share their partners,
and the partners drop into W **once** for the whole group: the overhead is paid once and the saving k times. Five groups
pay (helpers 586 and 588, each alone at its own W, stay at −3,345 and are not used):

| group | shared rank-7 subspace W | helpers (width change) | single lowerings, margin each | joint price | joint margin |
|---|---|---|---|---:|---:|
| V45 | ⟨256, 128, 64, 35, 16, 11, 5⟩ = E_7 ∩ E_42 ∩ E_45 | 249, 251, 265, 267 (PR2942's pivots, 8 → 7) | −53,141 each | −8,388,172 | **+22,972** |
| A | ⟨256, 128, 64, 38, 20, 10, 1⟩ ⊂ E_30 | 331 (PR2917's step 4, 8 → 7); 450, 451, 508, 509 (entering, 7 → 6) | 331: −58,943; 450: −19,901; 451: −14,905; 508, 509: −21,782 | −10,499,041 | **+42,541** |
| B | ⟨256, 128, 64, 34, 17, 11, 4⟩ ⊂ E_51 | 299 (PR2917's step 5, 8 → 7); 448, 449, 484, 485 (7 → 6) | 299: −58,943; 448, 449: −14,905; 484, 485: −21,782 | −10,499,041 | **+42,541** |
| C | ⟨256, 128, 64, 32, 19, 11, 6⟩ | 452, 453, 532, 533 (entering, 7 → 6) | 453: −14,905; 452, 532, 533: −16,786 | −8,382,370 | **+17,170** |
| D | ⟨256, 128, 64, 37, 21, 8, 3⟩ | 454, 455, 556, 557 (entering, 7 → 6) | 454: −14,905; 455, 556, 557: −16,786 | −8,382,370 | **+17,170** |

The groups are independent (every pairwise union prices exactly as the sum), the four V45 subsets climb monotonically
(−53,141 / −27,770 / −2,399 / +22,972 for one to four helpers), and leaving any one helper out of its group costs
23,490 to 25,371 units, so every member contributes. The stage changes no gate, scalar, operator, entrance or cleanup:
only 22 `helper_final` entries (each new end frame a hyperplane of the old one, all equal to their group's W) and 139 gate
frames (each a hyperplane of the old frame). These prices are search-time evidence (`construction/STAGE-PRICES.json`);
`verify.py` checks them against the literal words: the five joint prices sum exactly to the literal stage-1 price
−46,150,994, and one control per group keeps a single helper lowered on top of the group's partner frames, which is a valid
word but fails the joint claim (margins −53,141 for V45 and −58,943 for A–D against the joint +22,972 … +42,541).

### Stage 2: how the lowered partners make five more extractions profitable

On PR2942's words no rank-8 paired extraction clears break-even (best −29,645 at normals 486/504; normals 7 and 42 at
−68,935 and −86,879). Stage 1 moves the U12 partners of normal 45 into V45 ⊂ E_7 ∩ E_42 and the group partners into the
W's, so they become cheap or free partners for new rank-8 directions: on the stage-1 word the exact composition pricing
gives normal 7 +30,758 (k = 2, pivots 363, 395), normal 42 +26,153 (k = 3; realized +36,145), and normals 25 and 52
+20,766 each (25 reuses pivot 363 and 52 pivot 395). The shipped composition is normal 42 three times, then normal 7 twice, each step a
PR2908/PR2917 paired extraction (input gates at frame zero after the prelude, output gates at E_n appended to restore,
compensation C·S, one more private zero buffer) with PR2908's exact two-sided certificate:

| step | normal | pivot | inputs / outputs | frame changes | price | margin vs break-even |
|---:|---:|---:|---|---:|---:|---:|
| 1 | 42 | 226 | 20 / 6 | 0 | −2,101,683 | +10,383 |
| 2 | 42 | 228 | 16 / 7 | 1 (its first output gate drops from E_42 into group A's W) | −2,106,679 | +15,379 |
| 3 | 42 | 230 | 54 / 15 | 0 | −2,101,683 | +10,383 |
| 4 | 7 | 363 | 28 / 6 | 0 | −2,106,679 | +15,379 |
| 5 | 7 | 395 | 21 / 7 | 0 | −2,106,679 | +15,379 |

After stage 2, normals 7, 42 and 52 have pairing rank 0 and normal 25's best is −34,529: the lever is exhausted for these
normals on the final word.

### Stage 3: PR2957's rewrites, composed exactly

Jeremy Kothe's fourteen declared rewrites (R-retime ×4, A3779-cut-start-read, PM-carrier-lender-entry ×2,
B-carrier-retime ×2, A-commuting-swap ×5) all apply to the stage-2 word with exact preimages after re-addressing A indices
by +261 versus PR2917 (our 122-gate and 139-gate input blocks; the A84 insertion lands after both); stage 1's B and
restore frame refits touch none of their preimages. `data/REWRITES-2957.json` is that re-addressed list (each entry keeps
its credit), applied by PR2957's own pure applier, vendored byte-identical (`vendor/declared_rewrites.py`, called with
`check_declared=False` because its declared profile is PR2917's). The certified delta is −52,350 = the sum of the singles,
exactly as on PR2917's and PR2942's words: no interaction with stages 1 and 2. PR2966 and PR2969 composed the same
fourteen rewrites with PR2942's words; here they are composed with the stage-2 word.

### The fresh 9 → 7 route is an exact negative

A 7-dimensional V ⊂ F₂⁹ lies in exactly three hyperplanes E_n1, E_n2, E_n1⊕n2 (its annihilator is {0, n1, n2, n1⊕n2}), and
the admissible pairing at V restricts the pairing at each of them, so a fresh helper can pair at V only if all three
normals pair. Over all 43,435 rank-7 subspaces: on PR2942's words (and on the stage-1 word) no pairing triple closes under
xor, so no fresh rank-7 extraction exists; on PR2917's words the single live V is V45 itself, with prank 4, which is
exactly normal 45's structure (realized here as PR2942 plus the V45 group: −8,378,128 − 8,388,172 = −16,766,300, the 9 → 7
identity's prediction). On the PR2894 parent the census reproduces RossRichardson's PR2918 obstruction exactly
(at E7 = ⟨256, 128, 66, 36, 22, 8, 1⟩: R = {105, 307, 309, 314, 369, 371, 373, 378, 408, 572, 573}, |H| = 226,
dimA = dimB = 0). Rank-7 ends are therefore reachable only by lowering already restored helpers, which is stage 1.

## Packing the changed inventory

The fixed-capacity fractional relaxation of {4:26, 5:2, 6:16, 7:52, 8:99, 9:213} with local profile {1:2445, 2:706, 3:232,
4:108, 5:18, 8:8} has a 10-pattern optimal basis over all 2,551 patterns: per replica [8]×672, [7,9]×1757/4,
[7,8,8,9]×115/4, [8,8]×35/4, [6,8,9,9]×144, [4,9,9,9]×234, [9⁵]×1341/20, [9,9,9]×93/4, [5,9,9,9]×18 and []×7619/20;
cap ∈ [0.001729035764875516181444, 0.0017290357648755161814441]. The basis is fractional at T74, and the cap-level integer
mixes are not schedulable on the chronology: over calls 45..332 of the T37 chronology that PR2917's T74 order interleaves
twice, the width-7 roles (52 × 288 = 14,976) need distinct cap-16 bins in those mixes but only 13,440 cap-16 bins are open
(an interval Hall condition), so at least 1,536 width-7 roles must sit in cap-32 bins. A moment-preserving swap on a
degenerate face of the optimum, [7,8,8,9]@32 + [7,9]@16 → [8,8]@16 + [7,7,9,9]@32, applied 1,063 times to the T37
all-pattern integer mix, satisfies that condition at no moment cost (building on themilkman216's observation about the T
at which these caps become integral and on PR2930's flow fill). PR2857's chronological flow model (CP-SAT, one worker, seed
1, optimal in 153 s; `construction/allocation/`) realizes the mix on the T37 chronology, and PR2917's exact interleaving
doubles it onto its T74 order. The literal root is **1.782e-9 below the cap** (integrality only); `check_cap.py` records
the exact gap. No optimality of the literal fill among integral allocations is claimed.

Provenance (not entry points): `construction/STAGE-PRICES.json` holds the search-time prices quoted above;
`construction/search/` the census and realization scripts as executed (they import the round's certified frame-solver
harness, which is not shipped); `construction/records/` the derivation of `data/` from the realized words (per-step frame
changes, re-addressed rewrites); `construction/allocation/` the flow model run and the face-move mix. Scratch paths are
replaced by placeholders.

## Verification

**Registered, bounded** (`run_registered.py`, standard library, about one minute):
- complete package pins;
- `verify.py`: `producer.py` rebuilds both WORD files and every intermediate stage word from PARENT (PR2942's words,
  byte-identical) and the declared records; stage 1: every lowered end frame is a hyperplane of the old one and equals its
  group's W, every gate touching a lowered helper lies in W (326 gates), no gate or scalar changes, the cleanup is
  unchanged; stage 2: PR2908/PR2917's unchanged `structure.py` checks the seven two-sided identities over the exact free
  operator algebra at every step and for both providers; stage 3: PR2957's vendored applier with report and cleanup
  re-derived and compared; PR2833's unchanged auditor replays every stage word and both final words forward and dual over
  all 632 inputs (`PASS_INDEPENDENT_EXACT_BORROWING_WORD`, 91 restored endpoints and buffers at the end); `frame_report`
  equals each word's report; **86 semantic controls** are rejected (stage 1, per provider: one helper of each group lowered
  alone (fails the joint claim, priced below break-even), a wrong rank-7 subspace, an omitted gate frame edit, an omitted
  partner frame edit, a stale report, a widened end frame; stage 2, per step and provider: drop an input gate and flip an
  output coefficient (rejected by the auditor and by the certificate), the output change on a wrong hyperplane, a stale
  cleanup, a stale compensation, and the omitted frame change of step 2; stage 3, per provider: a rewrite's deletion
  removed, its insertion dropped, a transported coefficient flipped, a stale preimage (rejected by the applier), unshifted
  warp positions, a stale cleanup, an unresolved swap frame); the overlay producer `tools/wordedit.py` round-trips
  PARENT → WORD;
- `check_allocation.py`: the vendored PR2839 owner engine on the new allocation (271,728 roles, six width classes, windows,
  same-call families, capacities, complete profile, physical 66,813) with five rejection controls, and PR2917's exact dyadic
  moment auditor with its authenticated baseline re-pinned to the PR2969 headline (strict gain);
- `check_cap.py`: Fractions-only cap certificates of the parent and of every stage (each stage raises the cap), the literal
  profile's completeness and its exact gap to the final cap, four controls, and exact gains over PR2969, PR2966, PR2957
  and PR2942;
- binding of the stored overlay, native, admission and release receipts in `evidence/` to the exact words, allocation and claim.

**Complete replay** (`reproduce.py`): exact Git exports of PR2908 (51309592), PR2917 (224bd5e5), PR2942 (a027b0f6), PR2957
(b74b25f3), PR2966 (e62d3eb9) and PR2969 (e2ca469b), and through them PR2894 (18d03c44) and PR2833 (e9307b48); fresh retained
bootstrap; PR2857's four-kernel stage, PR2894's preload stage, PR2908's paired stage and PR2917's extension stage, giving
PR2917's derived source (manifest 98d57c82, 632 files); then `tools/build_overlay.py` appends the stage
`rank7-joint-endframes`: the exact edit spec PR2917 word → this word (`tools/wordedit.py`, cleanup re-derived) is replayed
by the source's own `rebuild_borrow.py`, whose patched block now accepts inherited endpoints lowered to a subspace and warps
whose B positions move (both are new here), so every previous state stays in the audit chain (manifest 751b4636, 637
files); closed adapters for 91 buffers whose admission control count is derived from the providers' width classes (139
for six classes instead of PR2917's pinned 119 for five), with the PR2917, PR2966 and PR2969 headlines as pinned
comparators; fresh five-stage native chains for both providers; complete admission (owners, parent lift, rebind,
discovery, block norm, physical/prefix invoice, independent outer checks, and the release, which reruns the admitted
source's own verify.py and its 17-stage rebuild chain for both providers, ending with `rank7-joint-endframes`).

The recorded run (`evidence/`) is a single invocation of this package's `reproduce.py --jobs 2` on macOS arm64, CPython
3.12.13 (numpy 2.4.5, scipy 1.16.1, sympy 1.14.0, mpmath 1.3.0, gmpy2 2.3.2, psutil 7.2.1): fresh retained bootstrap 311 s,
source stages including the overlay 3 s, fresh native chains for both providers 32 s, complete admission 287 s (release 221
s), 635 s wall, ending `PASS_RANK7_JOINT_ENDFRAMES_COMPLETE_REPLAY`. The native receipt's "reused retained" fields refer to
the retained cache that the same run had just bootstrapped (`evidence/FULL-REPLAY-RESULT.json`: `fresh_retained_bootstrap:
true`). Hash-bound receipts are stored verbatim (they contain the run's absolute paths); logs under `evidence/logs/` have
paths replaced by placeholders. The run used a frozen copy of the package that is byte-identical to this one on every file
the replay executes or binds; only documentation was refined afterwards.

```sh
# exact predecessor commits must be present locally (no network access during the replay)
git fetch https://github.com/CrocSwap/integer-mult-bounds.git \
  e2ca469b08385d3d5e29a918d66dbefaf889e9f3 e62d3eb9005117d82a9babcfa937ecc53237c490 \
  b74b25f3ccc84c16e1a801d73b2f47e5ea764c78 a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf \
  224bd5e56041c40078ff6b5fa7393733a215de5c 51309592971e3b5be935599eed2a95404dc7781e \
  18d03c447886895ef9abf888398178e0428533ca e9307b48d7d1b690939935ecef0f8e524e6d92f4
python3.12 scripts/research_package.py --package research/rank7-joint-endframes
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3.12 -B research/rank7-joint-endframes/reproduce.py --repo . --work /tmp/rank7-complete --jobs 2
```

The complete replay needs Python 3.12 with numpy, scipy, sympy, mpmath, gmpy2 and psutil (versions of the recorded run in
`evidence/ENVIRONMENT.json`). `--retained DIR` reuses an authenticated retained cache instead of the fresh bootstrap.
For the local checks alone: `python3.12 -B research/rank7-joint-endframes/verify.py --work /tmp/rank7-local`.

## Scope

Conditional finite supplier and modern outer certificate, exactly as inherited by PR2917/PR2942; all inherited all-size,
compiler, hosting, precision and analytic hypotheses remain. No selected-frontier change, no unconditional multiplication
theorem and no independent human review is claimed. Stage 1 alone is a fixed-word change of helper terminal subspaces and
monotone frames, the class whose relaxation Gareth Davidson's #1995/#2013 bound on the selected k8 word; here it is applied
to restored paired-extraction helpers of a different word and composed with a changed scalar word (stages 2 and 3), and
the whole is admitted with its changed inventory, buffers and cleanup contract. Lowering helper ends to rank seven is not
new as such (`research/complex-rank7-end-pair`, `research/k8-rank7-composition` and the PR1090/PR1104 lineage do it on
other words); what is new here is the joint, shared-subspace lowering of restored paired-extraction helpers and its
effect on further extractions. The search and optimality statements are relative to the stated cost model and census
(lower-bound candidates for one-dimension lowerings; all 43,435 rank-7 subspaces for fresh extractions; the exact
composition pricing per normal), not impossibility results beyond it. No optimality of the literal fill among integral
allocations is claimed.

## Open next questions

Checked after packaging on the final word (local exact runs with the certified frame solver and #2833's auditor on both
providers; not part of this package's gates):

- **The lowering/extraction iteration is at a fixed point.** A one-dimension lowering census over all 91 restored endpoints
  (the five new pivots and every changed partner included) leaves slack only at 586 and 588, with different target
  subspaces at -3,345 units each; no endpoint has two dimensions of slack. Normals 7, 42, 45 and 52 now have pairing rank 0;
  the best rank-8 block at 25, 76, 82, 97, 127, 486 or 504 is -29,645 units against break-even; no rank-7 subspace has all
  three normals paired.
- **Other stage-2 orders tie at best.** On the stage-1 word, the orders 42 then 7, 7 then 42, and 42 then 25 then 52 each
  realize five extractions at +66,903; orders that start with normal 25 give +61,907 or +46,919.
- **Earlier levers re-checked on this word.** No hidden compensation quartet narrows (the 502-517 family is certified
  infeasible at #2917's restore outputs and at the new normal-7 output `96 -= 4*395`); entering helpers can enter v but
  not u or the pivot (best direction 2,137 units short); renaming the output carriers bounds at 16,196 units, but every
  pivot's output support is unique and every transfer placement is infeasible or non-negative. A census of #2957's rewrite
  classes (retimes, commuting moves, cut-start reads, restore-to-B and cross-cut moves, read merges and splits) on the new
  input block, the new output gates, the stage-1 refits and every gate touching a lowered helper prices 5,893 candidates
  per provider with no negative delta.

Still open:

1. **Re-pairing the B phase** around the normal-7 pivots (363 with 73, 395 with 5) so the output map can use free carriers.
2. **Input changes placed later in A** instead of right after the prelude (identities as in #2908, new compensation).
3. **Integral packing at the cap.** The cap basis is fractional at T74 (denominators 4 and 20); a direct T74 solve of the
   1.552e-9 mix ended UNKNOWN at 900 s twice, so a T at which the basic counts are integral (keeping the interval Hall
   condition for width-7 roles) may close part of the remaining 1.8e-9.

Details are in `TASK.json`.

## Credit

Jeremy Diviney (PR #2908) for the paired input/output extraction method, its compensation rule and `structure.py`
(vendored unchanged); Mason Hale (PR #2917) for the words under PR2942, the producer model stage 2 follows, the T74
chronology, owner/moment checks, extension stage and adapter derivation; **Jeremy Kothe (PR #2957/#2948/#2966) for the
fourteen declared rewrites of stage 3 and their applier (`vendor/declared_rewrites.py`, vendored unchanged), composed here
exactly, as PR2966 did with our PR2942 words**, and for the supplier, frame accounting and inverse cleanup
(`vendor/preload_move.py`, PR #2894/#2833); Dugongue (PR #2969) for the PR2942 + PR2957 composition at T370 that is this
package's comparator and moment baseline, and for the PR2863/PR2839 owner-engine lineage; RossRichardson (PR #2918) for the
rank-seven isolation boundary our census reproduces; Yiyang Lu (PR #2857/#2848) for the flow model and realization used to
build the allocation; Tekalign for the independent owner checker; icekylinx for the exact auditor
(`vendor/audit_local.py`); themilkman216 for the cap/T observation the allocation builds on. See `CREDITS.md` and
`NOTICE`. New work by Marius-Paul Dumitrean, prepared with substantial AI assistance (Anthropic Claude, via Claude Code).
Apache-2.0.
