# B240 ASYMMETRY VERDICT (k8 word #1018 c2b29430; ship bar #1031 1.672167430672016e-3; no ship candidate)
VALID: YES. No verifier, SPEC or pin requires the 14 factory blocks to be uniform. The shipped word is already block-asymmetric (7 slots on 7 blocks, leaver cells only in K-blocks, fat/lean gates). Uniformity is required only ACROSS providers (calls), and that is a package-code convention.
COST: 0 to enable. Built word drop_439 (#1018 with slot X=439 removed, so one block differs): real audit_local PASS (fused + package, 704 cols), exact κ 1.671625560579741e-3, Δκ = -3.9722639029e-8 vs #1018. That is the value of one per-block rewrite, not a toll for asymmetry.
WINDOWS (ranked by exact priced bound; none legal ONLY because blocks differ, since every per-block move was already legal):
 1. Tail-gate split merges, all 78 mergeable early-cleanup splits: <= +1.3149e-5 (+0.787%). This is an upper bound, not a construction. All 116 gates are already lazy (minimal frame = span of operand frames), and gopt2 is an exact global frame optimum, so this window needs SCALAR changes.
 2. Fat/lean alignment, 20 gates (7,7->8 and 6,6->8): <= +2.685e-6 (+0.161%); the 8 (7,7->8) gates alone: +8.75e-7. The card target lives here, see "Mechanism".
 3. More per-block triangle-hybrid slots: +3.97e-8 each (exact, linear). #987's search on k8 found 7; 14 more would be <= 5.6e-7 (0.03%).
 4. Heterogeneous owner packing / per-call providers: κ is linear in provider mixing (B230: 1.5e-11 below linear), so the only gain is idle packing; #1018 -> #1031 T16 gave +5.0e-7. Needs same R/ports (see VALID).
 5. Per-block punctures: any dropped delivery must be re-delivered (all-column endpoint), and register mass is fixed by start/end frames (+1 mass ~ -2.8%). Bound 0 legal found; B235's census is invalid (see Warning).
 6. #1037 asymmetric fitting: min rank is exactly 9d = 9 per block, so asymmetric port labelling cannot reduce h=9. Window 0 (proven per profile; global 25/27 still open).
 7. #1023 width-7 bit residuals: "+17-23%" is bit-side c headroom (bit_lower), not κ. Complex binds (κ 1.6722e-3 vs bit cap 1.7304e-3), so the window is 0 until complex gains exceed +3.5%.
 8. #1032/#1033 factory coefficient work: floors already attained by PR924, and coefficient work is not in the paid profile. Window 0.

## VALID: every rule that touches uniformity (worktree wt = pr1031; research/gauge44-slots/ unless noted)
- Local audit (independent/audit_local.py) has no block concept. Its rules are: v,h=(112,9) :79; port set and ordered centre frames = parent :63,:69; no non-target reads a target :88; all-column forward+dual endpoint :106-112; monotone frames, both operands at e[-1] :121-122,:137-138; target levels and centre frames at B :129-131; cleanup only on FULL ends :143; profile/inventory = report :144-146; cones :150-153.
- Native locals (pr635 complex-571-cold14-st2/code/hpe_audit_and_transport.py) also have no block concept: h,v :111; cleanup = literal reversed inverse of A+B :141, unless the word carries refactored_cleanup :130-139 (it does), in which case any exact factorisation passes; ports = routing set :182.
- Global (cross-provider = per-call) uniformity. This is CONVENTION, not SPEC:
  - all providers share v,h,R,ports: code/audit_allcold.py:70; bind_providers_portable.py:29,:62; emit_allcold.py:43; assemble.py:65,:78
  - centre frames = parent: audit_allcold.py:76-78
  - 4 spot helpers have width 8/9: witness.py:16,:28-30; bind:32; assemble.py:84
  - per-provider widths may differ, owners follow them: emit_allcold.py:47,:59
  - dispatch = SPEC.dispatch: bind:24, witness.py:12
  - freeze_spec.py:26 hard-codes provider_counts {'gauge44':72}, so multi-provider needs a package-code edit
- Hash pins (CHAIN-PINS, SLOT-PINS, data/SPEC.json via discovery -> freeze_spec) are per-package expected values, regenerated for any new word.
- SPEC proper (the math) is exactness, monotone frames, ends, centres, cones, owner distinctness and pricing. None of it mentions blocks.
- Shipped precedent: slot recipes use source holders from other blocks as cleanup partners (X=444 hold 34/98; X=439 hold 10/74; RECIPE-SLOTS-k8.json variants), and leaver cells exist only in K-blocks. So leaver-coupled cross-block cleanup partners are ALREADY legal and shipped.

## COST (exact, real)
- Rebuilt from B232's jx word: hyb c836d892 -> frames db2c7cfb (#1005, work/w1005.json.gz) -> slots c2b29430 (#1018, work/w1018.json.gz), all shas match.
- Slot words: dropslot.py X builds #1018 minus one slot. All 7 give profile {1:2412,2:418,3:430,4:146,5:80,8:8} (mass-neutral).
- drop_439 (98937b47) and w1018: audit_local PASS on both the fused engine and the package's own audit. Negative control (one B coefficient flipped) is REJECTED.
- Prices: price.py (package price_profile, 72*local + frozen #1018 idle) reproduces 1.67166528321877e-3 exactly; drop_439 gives 1.671625560579741e-3.

## Mechanism of the card target (fat gate with a leaver partner): PROVEN-NO, scoped to fixed targets and ports
- The 7 slot tail gates ARE fat (7,7->8) gates with a leaver partner. Example: holder 74 (source) restores E=584 at frame 8, after 584 reads into target 122 at F7a ⊆ perp(p122) (B1170) and 74 reads into target 126 at F7b ⊆ perp(p126) (B1171).
- Any restore order forces the frame up to F7a+F7b (8). A frame-7 gate needs F7a = F7b = perp(p122)∩perp(p126), i.e. re-chosen target ladders. gopt2 (exact global frame optimum) rejects that.
- Exact moves on slot 439:
  - restore moved into B (675 positions): profile unchanged
  - E-read moved earlier: illegal (end cap)
- No register can stand in for the gate partner: the full state is invertible, so there are no exact full-row twins (stats/info).
- A relay leaver only moves the split onto itself, because per-register mass is fixed by start/end. The relay is free only if its frame chain already passes F_S then U (B234 telescoping test).
- mv.py: single long-range commuting moves, with the moved op and all tail gates at lazy (minimal) frames and the rest legalised. Exact price.
  - slot 439: all 15 ops in every commuting range (~8k moves) plus the tail restore moved into B. 0 improving moves.
  - job 00_B240_mv covered slot 444 (0 improving moves) and was then killed externally at 13:20 (exit 143). The other 28 pairs remain untested. To resume, edit mvjob.sh and rerun it.

## Warning for reviewers
B234 and B235 analysed research/gauge44-leaver8/evidence/local/*. That is #645's HISTORICAL word (R=492, profile {1:2514,...}; README "evidence/ except evidence/layers is #645"), NOT the k8 word (R=480). Their leaver/helper censuses must be rerun on work/w1018.json.gz (or work/w1005.json.gz).
B232 can take these words: they match the c2b29430 and db2c7cfb pins.
Files: prof.py (frame-only profile), price.py, dropslot.py, fat.py/fat2.py (window bounds), lazy.py, dumpg.py, mv.py, audits.sh, work/.
