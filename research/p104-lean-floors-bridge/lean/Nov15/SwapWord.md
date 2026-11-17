# SwapWord.lean: the SWAPBUILD two-swap edit (h457 → 242, h461 → X10). No sorry, ~5 s, 2.1 GB RSS
Lane LEAN-NEXT10, Nov 16. Imports the RankLawC olean. Axioms: [propext, Classical.choice, Quot.sound].
Source: cards/WILD/BIG/SWAPBUILD (build.py), BIG/TOKENRANK THEORY TR2 and verify.py.

**The edit (data).** After rebirth (h = e_h at its first chart), the edit injects `j += −1·h` just before the native's own `h += j`. Together they are the swap.
- 457 → 242 at index 11392 of the hub-deleted mid program; 461 → X10 at index 11498.
- h = e_h holds at both points; the second is checked in the once-edited word (Nov15/swapword_data.py).

**General lemmas** (TokenCancel's op model, any field):
- `run_diff`: two runs of the same events from states with equal locations differ by the run of the difference state, with births read as INITs.
- `rows_in_run`: with no births, all rows stay in any subspace P that contains them initially.
- **`inject`**: if h's row is e_h after prefix p, injecting `add j h c` changes every final row by δ r • e_h only.
  - `inject_col`: every row, non-V-enders included, is unchanged on every column k ≠ h.
- `inject_two`, `inject_two_col`: the same for two injections (h1 = e_h1 in the unedited prefix, h2 = e_h2 in the once-edited one). The change is δ1 e_h1 + δ2 e_h2.
- **`absorb`** (the debt is absorbed by the V mix). Hypotheses:
  - the edited rows = X0 + δ e_h;
  - non-V-enders on target (TR2);
  - X0[G1] ⊆ B;
  - e_h ∈ B;
  - B ⊓ N = ⊥.

  Then: V mix for the edited run ⟺ edited run is loss-free (via RankLawC.rank_law_indep).

**Data (exact, swapword_data.py).**
- Debt support is exactly column {h}.
- Non-V-enders changed: 157/160/210/219 for 457 (column 457: −1/2 → 0) and 120/179/192/207 for 461 (column 461: +1 → 0).
- Every non-G0 mismatch vs native Rf on non-V-enders: 4 → 0.
- V-enders absorb the debt; 457 and 461 are themselves V-enders with Rf h = e_h, so e_h ∈ B.
- Loss-freeness/joint feasibility is the JointG + exact replay data (SWAPBUILD: final rows == native rows).

**Scope.**
- `absorb` is stated for rows after the z-prefix. HubSettle's [X_n | X_0·M] acts only on G0 columns, and after rebirth h ∉ G0, so the e_h debt commutes with it.

**Finding (prose false as written).** "The swap preserves every non-V-ender row exactly" is false against the unswapped (rebirth-only) word: it changes 4 non-V-ender rows per swap.
- True form: the swap changes final rows only in column e_h (`inject_col`). On non-V-enders the change is exactly the TR2 canceller, which zeroes their column h (now non-G0 after rebirth, so the z-hub can no longer clean it).
- Minimal fix: "preserves every row off column h; on non-V-enders it cancels column h (TR2), and the remaining e_h debt sits on V-enders, absorbed by the V mix because e_h ∈ span V targets (h is a V-ender)".
- Without e_h ∈ B and with B ⊓ N = ⊥, a nonzero V-ender debt can never be absorbed.
