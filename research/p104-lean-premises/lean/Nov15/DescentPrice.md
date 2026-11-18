# DescentPrice.lean: rebuild r6 descent price, paid − credit = 2·(descent ranks). No sorry, ~4 s, 1.5 GB RSS
Source: internal notes §2. Self-contained. Axioms: [propext, Classical.choice, Quot.sound].

**Invoice model (abstract).**
- A path is the list of chart dimensions a register visits. paid = Σ|Δ|, both directions paid.
- A helper with fixed endpoints S ⊊ F is credited dim F − dim S. An owned register INITs anywhere for free and is credited nothing.
- S = S₀ − w·(paid − credit), with w = 17 on P104.

**Results.**
- `paid_eq`: paid = ascents + descents. `tele`: ascents − descents = last − first.
- `helper_identity` (the card's identity): paid − credit = 2·(descent ranks). `helper_price`: a rank-e helper descent costs 2e·w in S.
- `owned_identity` / `owned_ge`: for an owned register, paid − credit = ascents + descents ≥ descents.
  - `owned_pure_descent` / `owned_price`: INIT at the top and descend, and the price is exactly e·w.
- Data (`decide` / `norm_num`, kernel only):
  - 1424 − 2·1·17 = 1390 (w_desc1, one rank-1 helper descent);
  - the 24 owned descent ranks of #7623 sum to 56, and 56·17 = 952.

Nothing false. The κ exchange rates (546.09e, 273.04e D0/call) are first-order [C] and are not formalized. The SPEC/verifier legality reading (§1) is prose.
