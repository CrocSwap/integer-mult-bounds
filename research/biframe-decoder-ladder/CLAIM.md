# Local sprint claim and result

No pinned coordination issue existed when this work started (checked 2026-10-13 00:48 EDT), so the claim was
recorded locally.

- **Track / seed:** 40–49, structural decoder research. OS-random seed **47**, drawn 2026-10-13 00:47:13 EDT
  with `secrets.randbelow(100)`.
- **Base:** `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Rebased onto main `7ee02b7c` before submission; there were no shared files.
- **Object:** the complex E8 unit's decoders on punctured port sets, in particular #717 D3's cst-56 P104
  decoders, and whether the copy-cost ladder continues past P104.
- **Method:**
  - exact linear algebra (bi-frame lemma);
  - an exhaustive label-span threshold census over the 255 W(E8) classes of supports;
  - an exhaustive census of root bi-frames over the 1260 second frames;
  - a Dilworth chain-cover bound on delivery copies;
  - optimistic pricing on the certified ceiling and cited invoice rates.
- **Claimed:** 2026-10-13 01:12 EDT (local note). **Expected finish then:** about 03:00 EDT.

**Result (2026-10-13 01:51 EDT):**

- All 11 #717 D3 decoders are exact bi-frames.
- For 8-term decoders exact on all pairs, cst ≥ max(v − 48, 56) on P120 minus ≤ 24 lines. Equivalently,
  cst ≥ 72 − |Π| for |Π| ≤ 15 and cst ≥ 56 for |Π| ≤ 24.
- P104 is the largest unit at 56, and 896 of the 1260 second frames reach it.
- The P104 cut is not common. Delivery needs ≥ 144 extra copies at a single cut and ≥ 47 with staggered reads
  (exhaustive over all 40,320 global read orders).
- Priced first on #717's linearization at #626: −4.8% b (single cut, w9) and +2.0% b (staggered, w9 no
  merge). These are now replaced by the comparison against #968's T37 budget: the single cut costs ≥ 10.1% b
  at w9, above the 5.51% budget, and staggered delivery costs ≥ 3.3%, inside it.
- No κ claim.

**Overlap found before submission (2026-10-13 13:33 EDT):**

- #968 (themilkman216), which drew the same seed 47, was opened at 2026-10-13 11:17 EDT and merged at
  11:57 EDT. It has the same frame-pair floor, the same 896 family and a T37 budget.
- This package's floor, census and delivery bounds were committed locally at 01:53 EDT (the author date
  of its commit). It was not submitted until after #968 had merged.
- The package was therefore reframed around what #968 leaves open: delivery lower bounds priced against
  #968's budget. The floor is kept as an independent re-derivation, credited to #968.
