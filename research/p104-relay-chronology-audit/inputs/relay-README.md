# P104 side correction: a complete 104-target relay word (2,185 lifetimes) and the line fan-out floor

FINDING, no κ claim. Card `p104-side-correction`, priority revision 4, base main `0fdd7d82`. Follow-up to
`research/p104-correction-screen/window-bill/` (#2245 comment 18949693). Local only.

**Model.** The X-only correction model of PR2353/PR2393/PR2445:
- New helper lifetimes start at ZERO with independent dirty values and move only up nested frames.
- Helpers mix by rational ADDs only within equal frames.
- They read immutable X only in X's retained frame at that cut, and write Y only additively in Y's frame
  at that cut.
- They never read original G/Q/D/C helpers or Y.
- Inputs: witness `0f541bef…`, fixture `516c06f6…`.

## Results

1. **A complete 104-target correction with 2,185 lifetimes (21.0 per target).**
   - `WORD.json` (sha256 `eb1ee572…145c`) is a literal word. Inserted at cut 0 are the dirty compensation
     at ZERO, the line reads, and the pool mixing. Inserted at cut 4058 are 208 arrivals (2 per target)
     into H_t, the writes, the moves to FULL, the inverse shears, and the X cleanup at FULL.
   - The replay checks the exact identity: every Y_t receives exactly row t of I − G/2, which covers all
     4,992 needed entries and zero elsewhere, with no dirty residue.
   - It also checks the legality of every move (strictly nested), shear (equal frames), read (X's
     retained frame at that cut) and write (Y's frame at that cut). Every helper ends at FULL with its
     dirty value restored.
   - Counts: 8,711 moves, 6,042 shears, 2,646 reads, 6,699 writes.
   - Profile: 4789 H1 + 1464 H2 + 659 H3 + 487 H4 + 325 H5 + 511 H6 + 476 H7, rank mass 19,665
     (9 per lifetime).
   - All 2,185 lifetimes are live from cut 0 to 4058. That satisfies the ≥104 window floor, but it is a
     large hosting burden.
   - Comparison: about half of what the published per-pair sharing implies (39 × 104 = 4,056, #2445),
     and below the no-relay cover minimum of 4,580 (#2392).
   - It is **4.5× over** the allowance at #2526 (482 lifetimes for {1,1,7}; 322 for nine rank-1 steps).
     So it is **not** a supplier and the route is **not** shown viable.
2. **Allowance recomputed against #2526** (κ 0.0017037130392579, rounded up at 1e-30). The bit cap from
   the #2526 ledger is 0.0017334270395898, unchanged. The allowance equals the #2474 numbers:

   | per-lifetime steps | max lifetimes (at κ #2526) | max lifetimes (at bit cap) |
   |---|---:|---:|
   | {1,1,7} | 482 (idle-mass cap) | 482 |
   | {1,1,1,6} | 464 | 449 |
   | {1,1,1,1,5} | 418 | 404 |
   | nine rank-1 steps | 322 | 312 |

3. **Line fan-out floor = 208 (exact; not above 482).**
   - A line read of X_s can reach target t only through a lifetime that leaves the line ℓ_s for a frame
     inside H_t, and every such frame contains a plane ⟨q_s, w⟩ ⊂ H_t. So the lifetimes visiting ℓ_s must
     have next frames covering T_s.
   - κ_s is the least number of planes through q_s that cover T_s. A lifetime visits at most one line.
     Therefore L ≥ Σ_s κ_s.
   - The checker verifies κ_s = 2 for all 104 sources: no single plane works and a covering pair exists.
     This holds even with the 336 later-frame entries granted. So L ≥ 208, the same as #2353 (proved here
     by a different cut).
   - **No floor above 482 is proved.** Route closure remains open.
4. **Exact accounting identity (new, simple).** In any network of this model, if pools are the frames
   where lifetimes meet:

   **L = A + Σ_V (e_V − r_V)**

   - A is the number of arrival lifetimes (≥ 208).
   - e_V is the number of lifetimes entering pool V from below.
   - r_V is the rank of the forms that leave V usefully.
   - Births at a pool equal useful exits minus their rank. Copies are free in this count; every
     non-arrival lifetime is a merge loss.

   So beating #2526 needs total merge loss ≤ 274 (≤ 114 with nine-step lifetimes).
   - This word has A = 208 and loss 1,977: about one per pool over 2,054 pools of dims 2–7. Most pools
     merge two children into a rank-1 demand.
5. **Geometry that any better construction should use (exact facts, in `generate/stats*.py`).**
   - All 104 source labels lie in one affine hyperplane {⟨u*,v⟩ = 1}, so the problem is AG(8,2):
     104 points against 104 affine hyperplanes. Each H_t's 48 sources avoid H_t ∩ u*^⊥. As a result,
     every hyperplane K of H_t other than that one splits the support exactly, giving 127 valid
     two-arrival covers per target.
   - No three targets share a 7-dim K. Of the 5,356 pairwise K = H_t ∩ H_a:
     - 384 have fully proportional restrictions (rank 1);
     - 2,112 differ in exactly one source;
     - 240 split by ratio into two 6-dim-spanned halves.
   - So top-level sharing is cheap. The loss sits in the lower merge tree.

## Evidence status

- The construction and identity checks are exact finite replays (standard library, about 1 s).
- Six fault controls all reject:
  - shear coefficient;
  - wrong-source read;
  - dropped compensation;
  - non-nested move;
  - dropped restoration;
  - early target write.
- The floor in (3) is a short written argument plus an exact finite κ_s check.
- The identity in (4) is a counting argument, checked on this word (208 + 1977 = 2185).
- The design was found by a greedy heuristic (`generate/design.py`, CP-SAT top-level pairing) and is
  **not optimized**. No optimality is claimed, and there is no lower bound between 208 and 2,185 beyond (3).
- Author-checked with AI assistance (Claude Code). Not independently reviewed. Hosting, native lowering
  and precision are not checked.

## Run

```sh
python3 -I -B check_p104_relay_construction.py /path/to/main WORD.json --ledger /path/to/pr2526/.../outer/LEDGER.json
# PASS_P104_RELAY_CONSTRUCTION lifetimes=2185 per_target=21.01 line_floor=208 idle_cap=482
python3 -I -B controls.py /path/to/main WORD.json /tmp/somedir   # CONTROLS_PASS
```

To regenerate:
1. `generate/geo.py` dumps the geometry.
2. `generate/design.py SEED ilp` builds the pool design. CP-SAT is nondeterministic: two runs gave
   2,068 and 2,185 lifetimes.
3. `generate/build.py` turns the design into the word.
4. `generate/recount.py` gives the loss breakdown.
5. `generate/allow.py` computes the allowance.

## Next

- Lower the merge loss: lower-level pools must serve several targets with independent demands, so that
  r_V ≈ e_V.
- Or prove that the loss has to exceed 274. A natural route is to bound e_V − r_V on the pools that
  feed each K, using the rank ≤ min(8, #targets ⊇ V) cap.
