# Shadow : the SHADOW lemma of whole-floor R7 in Lean

`Nov15/Shadow.lean`, Lean 4.33.0-rc1 + Mathlib, kernel only: no `sorry`, no `native_decide`; every theorem prints
`[propext, Classical.choice, Quot.sound]` (or fewer). Builds in 7 s / 2.9 GB (the memory-guarded build script guard). Imports FibreK (Theorem K,
`nativeInv`, `Table`, `Helper`, `K_word`), CallerCost.

## What is formalised
* Part A, gates (`swapIn_eq`, `swapOut_eq`, `final_rows`): the 4-gate birth swap (g += r, r -= g, g += r, SCALE r -1) and the end swap-back
  (r += g, g -= r, r += g, SCALE g -1) are exact swaps of the pair of rows, in any module. So: r holds e_g after the birth swap, g runs the
  main's old program and ends at rho, and the swap-back gives r = rho (old final row), g = e_g (its own unit row). ADD/SCALE are not in the table.
* Part B, invoice. A `Word` = ends `E`, mains, helpers, final data `fin`; registers are FibreK `Helper`s (birth, end, steps).
  `shadow` replaces each main m by the single-jump main `<b,e,[(b,e)]>` plus the twin helper g = m itself (born b, ends e, same steps).
  `Fi_native`: F of a native = F(E) + sum over registers of (T-term of the climb - P-terms of its steps) (register-by-register form of Theorem K).
  Hypothesis `Sym` (P0 symmetry on the mains): b <= e and `tT (e-b) = tP (e-b)` (a climb d on T and a MOVE of gap d on P carry the same histogram;
  true for `d0Table`, and the price checker charges rank d to both).
  - `shadow_F`: F(t) of the twin = F(t) of the word, all t. `shadow_invoice_F`, `shadow_root`: the same for the caller invoice and for kappa (every root).
  - `shadow_D0`: Dinv equal for the D0 table (needs only b <= e).
  - `shadow_net`: the signed histogram cnt T r - cnt P r is equal at EVERY rank r (hence S, F, D0, kappa).
  - `shadow_T_raw`: the RAW T histogram of the twin is the original's T ++ `mains.flatMap (tT (e-b))`.
* Part C, `shadow_stops` (twin mains have 0 interior stops) and `no_law_forces_main_stop`: let M be any family of words closed under the twin.
  A law that sees only the net histogram, F, and the final data cannot force a main stop on a word of M with symmetric mains: if every word of M
  satisfying the law had >= 1 main stop, no word of M with `Sym` satisfies the law.

## Wording corrections (paper statement vs Lean)
1. R7 sec. 2 says the twin has "the same invoice T, P". Literally false: the raw T and P histograms each GAIN the common summand
   `mains.flatMap (tT (e-b))` (resp. the same list in tP; `shadow_T_raw`). What is equal is the NET: cnt T r - cnt P r at every rank,
   hence S, F(t), D0, kappa (`shadow_net`, `shadow_F`, `shadow_D0`). R7's own phrase "T[8], P[8] cancel in T - P" is the right statement.
   Consequently the corollary holds for laws that factor through net invoice / F / finals, NOT for laws that read the raw T or P counts. That is
   exactly the AUDIT7 caveat: the interval gate counts invoiced T events (sum T 22,461 -> 29,261, delta .99995 > 31/32).
2. The cancellation needs the P0 symmetry hypothesis `Sym` (T and P rank for a climb / jump of the same d). It is an explicit hypothesis here (FibreK's
   `Table` is abstract); in `d0Table` it is by definition.
3. AUDIT7 caveat (stated, not formalised): the twin is in model M as defined by price/replay/ascent, but the FULL twin FAILS the interval gate
   (`validate.py full` -> interval_gate; delta .99995 vs 31/32). R8.md: that gate is a fixed-constant instance of a free-parameter theorem, not SPEC
   (pinned sha 60a743d1); pinned gate admits at most 248 of the 400 mains on S22 (AUDIT7's rough scaling said ~90; the exact binary search in R8 gives
   248). So "forced main stops = 0" is a statement over M (price/replay/ascent), not over the gated verifier model.
4. Not formalised (hypothesis `hM : M w -> M w.shadow`): replay legality of the twin (public ascent, nesting, ledger and slot counts, other registers
   reading r now read g). That part is [C] (r7shadow.py, AUDIT7 re-run, validate.py PASS pricekit/replay/official/primes) and is exactly what `hM` abstracts.
   AUDIT7 claims 2-3 (one stop per register; f(d)-f(d-k) for k stops) are pricing arithmetic, not touched here.
