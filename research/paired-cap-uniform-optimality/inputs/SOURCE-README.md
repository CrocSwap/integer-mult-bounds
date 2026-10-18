# A cap-attaining allocation of PR #2917's words: conditional κ = 0.001722499906443274564357 − 10⁻⁴⁶ − 10⁻⁷⁰

```text
Status / UTC update / priority revision: DONE (conditional candidate) · 2026-10-16 · priority revision 5 · base main 8c8bcecb
Concrete question and changed premise: PR #2917 ships a literal T74 fill 9.11e-7 below the exact fixed-capacity packing
    optimum of its own inventory. Can PR2917's UNCHANGED words be packed at that optimum and admitted?
Established result and evidence status: yes. A literal allocation whose complete paid profile EQUALS the fractional optimum
    passes the owner engine, PR2917's moment auditor, and the complete fresh-native admission and modern outer release:
    κ = 0.001722499906443274564357 − 10⁻⁴⁶ − 10⁻⁷⁰, exactly 113907405684085469/125000000000000000000000 ≈ 9.1126e-7 above
    PR2917 (head 224bd5e5). Author-checked (AI-assisted); not maintainer-reviewed.
Public artifact URL + exact commit: this package (see the PR).
Next useful task: change the words (further paired extractions on the final 82-endpoint word); the fill layer of these
    words is exhausted by this allocation.
Active claim / expiry: released.
```

## Result

| | κ (headline) | complete paid profile |
|---|---|---|
| PR #2917 (Mason Hale) | 0.001721588647197801880605 − 10⁻⁴⁶ − 10⁻⁷⁰ | {1:1625724, 2:426240, 3:191980, 4:73260, 5:24951, 6:167, 7:45, 8:5328, 24:1, 32:207, 48:26958} |
| **this package** | **0.001722499906443274564357 − 10⁻⁴⁶ − 10⁻⁷⁰** | **{1:1626372, 2:426240, 3:192474, 4:73260, 5:24198, 8:5328, 48:27158}** |

The gain is exactly `113907405684085469/125000000000000000000000` ≈ **9.1126e-7** (about 0.053%). The two provider words, the call
order, the dispatch, the per-helper widths, the owner engine and its plan/template are PR2917's, byte for byte. Only the literal
allocation changes: `allocation/FILL.json.gz`, `allocation/PROFILE.json` and `allocation/SEARCH.json`. Same words, same
82 private buffers, same physical stock 66,304 + 408 + 8 + 82 + 2 = 66,804, same 271,728 helper roles.

## Why PR2917's fill was below its cap, and why this one is optimal

The fixed-capacity fractional relaxation (bins 672/448/448/448 per replica of capacity 8/16/32/48, all 1,163 count-vector
patterns, one idle child per bin, the complete local profile paid) of PR2917's inventory {4:26, 5:2, 7:62, 8:96, 9:222} with
local profile {1:2416, 2:640, 3:280, 4:110, 5:26, 8:8} has optimum

`cap ∈ [0.001722499906443274564357, 0.0017224999064432745643571]`, 11 tight patterns, and an **integral** optimal basis per replica:
[8]×672, [7,9]×352, [8,8]×96, [7,7,9,9]×103, [5,9,9,9]×18, [9,9,9]×93, [4,9,9,9]×234, [9⁵]×81, []×367, i.e. idle children
{1:234, 3:81, 5:93, 48:367} per replica.

PR2917's literal fill pays 207 empty cap-32 bins, one rank-24 and 212 rank-6/7 idle children, and parks 5,378 width-8 roles in
cap-32/48 bins instead of [8,8] cap-16 bins. Every single whole-role relocation from it is uphill (a single-move fixed point:
the first move of a width-9 role out of a [9⁵] bin costs +0.021 H-units before the drain completes), which is why bounded
exchange/relocation repair stops there.

Because the optimal basis is integral, an allocation with exactly the optimal pattern mix has **no rounding residue**: its
complete profile is 666 × local + 74 × idle_per_replica, which is the profile above. `check_cap.py` verifies, with exact
rationals only, the basis' primal feasibility, the sign of every one of the 1,163 reduced costs at the upper end of the root
bracket (weak duality), that the literal profile equals the optimum's, and that its exact root bracket is the cap bracket.
So no allocation of these words, under these bin capacities and this relaxation, has a larger complex endpoint. This is a
statement about the packing of fixed words only; changed words, templates or coverage laws are outside it. For reference, the
coverage-law local-word ceiling of `research/complex-local-word-ceiling` for this local profile is about 0.00175802181; the
headline realizes about 97.98% of it.

## Construction

1. `tools/relax.py` (exact relaxation, scipy/HiGHS only to locate the basis) gives the integral pattern mix above.
2. `construction/fill17.py`: PR2857's chronological flow model (PR2843 lineage) on PR2833's T37 owner chronology with the
   integral mix as global pattern targets and PR2917's exact per-helper widths; CP-SAT (OR-Tools 9.15, one worker; several
   workers deadlock on our machine) finds a feasible flow, realized as literal bins by regular-bipartite edge colouring.
   The recorded run used seed 7 with PR2857's flow as a hint (`construction/T37-SOLVER.json`); an unhinted run is faster.
3. `construction/double.py`: PR2917's T74 order is exactly two interleaved copies of the PR2833 T37 chronology
   (order74[2k] = order37[k], order74[2k+1] = (stage, replica+37), dispatch copied), so each T37 row (t,h,o,c,p,z) maps to
   (2t,h,o,c,p,z) and (2t+1,h,o+37,c,p,z): a T74 allocation on PR2917's own chronology.
4. `construction/controls.py`: fresh engine load, claimed-profile check, five rejection controls, 82-buffer stock and
   PR2917's exact moment auditor. The flow, model and pattern targets of the recorded run are in `construction/` (scratch
   paths replaced by placeholders; provenance, not a portable entry point).

## Verification

**Registered, bounded** (`run_registered.py`, standard library, about a minute):
- complete package pins; the vendored owner engine on the new allocation (271,728 roles, compact prefixes, windows,
  same-call family distinctness, capacities, complete profile, rank mass, physical 66,804) and five rejection controls
  (missing role, duplicate helper, same-call family collision, capacity overflow, changed profile);
- PR2917's exact dyadic moment auditor with its authenticated baseline re-pinned to the PR2917 headline (strict gain);
- the Fractions-only cap certificate and literal-profile equality (`check_cap.py`), with two rejection controls;
- binding of the stored complete native/admission/release receipts in `evidence/` to the exact words, allocation and claim.

**Complete replay** (`reproduce.py`): exact Git exports of PR2908 (51309592) and PR2917 (224bd5e5), through them PR2894
(18d03c44) and PR2833 (e9307b48); fresh retained bootstrap by PR2894's `prepare_retained.py`; PR2857's four-kernel stage,
PR2894's preload stage, PR2908's paired stage and PR2917's extension stage, giving PR2917's derived source (manifest
98d57c82, 632 files); closed adapters with the PR2917 headline as comparator; fresh five-stage native chains for both
providers; complete admission (owners, parent lift, rebind, discovery, block-norm, physical/prefix invoice, independent
outer checks, release).

The recorded run (`evidence/`) is a single invocation of this package's `reproduce.py --jobs 2` on macOS arm64,
CPython 3.12.13 (numpy 2.4.5, scipy 1.16.1, sympy 1.14.0, mpmath 1.3.0, gmpy2 2.3.2, psutil 7.2.1): fresh retained bootstrap
279 s, source stages 2 s, fresh native chains for both providers 25 s, complete admission 256 s (release 201 s), 563 s wall,
ending `PASS_CAP_FILL_COMPLETE_REPLAY`. The native receipt's "reused retained" fields refer to the retained cache that the
same run had just bootstrapped (`evidence/FULL-REPLAY-RESULT.json`: `fresh_retained_bootstrap: true`). Hash-bound receipts
are stored verbatim (they contain the run's absolute paths); logs under `evidence/logs/` have paths replaced by placeholders.

```sh
# exact predecessor commits must be present locally (no network access during the replay)
git fetch https://github.com/CrocSwap/integer-mult-bounds.git \
  224bd5e56041c40078ff6b5fa7393733a215de5c 51309592971e3b5be935599eed2a95404dc7781e \
  18d03c447886895ef9abf888398178e0428533ca e9307b48d7d1b690939935ecef0f8e524e6d92f4
python3.12 scripts/research_package.py --package research/paired-extension-cap-fill
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3.12 -B research/paired-extension-cap-fill/reproduce.py --repo . --work /tmp/cap-fill-complete
```

The complete replay needs Python 3.12 with numpy, scipy, sympy, mpmath, gmpy2 and psutil (versions of the recorded run in
`evidence/ENVIRONMENT.json`). `--retained DIR` reuses an authenticated retained cache instead of the fresh bootstrap.

## Scope

Conditional finite supplier and modern outer certificate, exactly as inherited by PR2917; all inherited all-size, compiler,
hosting, precision and analytic hypotheses remain. No selected-frontier change, no unconditional multiplication theorem and
no independent human review is claimed. The optimality statement is for the fixed words and the stated packing relaxation.

## Open next questions

1. **Change the words.** This allocation exhausts the fill layer of PR2917's words, so further gains must lower the paid
   local profile or the width inventory, e.g. further paired extractions on the final 82-endpoint word (PR2917 stopped
   searching once its nine-step word was frozen). One more 9→8 extraction at PR2917-step-1 cost ({1:+3, 2:−2}) is worth
   about +3.6e-7 after a cap-attaining re-pack. First step: recompute the paired nullspaces on the final word and price
   each nominee with a relaxation certificate for the changed inventory before synthesis.
2. **A general constructor.** The cap basis was integral per replica here; inventories with fractional optimal
   multiplicities additionally need PR2863-style lockstep copies and vacancy relays.

Details are in `TASK.json`.

## Credit

Mason Hale (PR #2917) for the words, chronology and admission tooling reused unchanged; Jeremy Diviney (PR #2908) for the
paired extraction and adapter chain; Jeremy Kothe (PR #2894/#2833) for the supplier, frame accounting and source tools;
Yiyang Lu (PR #2857/#2848) for the flow model and realization; Dugongue (PR #2863/#2839) for the cap-attainment precedent
and engine lineage; Tekalign for the independent owner checker. See `CREDITS.md` and `NOTICE`. New work by Marius-Paul
Dumitrean, prepared with substantial AI assistance (Anthropic Claude, via Claude Code). Apache-2.0.
