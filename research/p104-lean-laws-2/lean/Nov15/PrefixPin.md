# PrefixPin (LEAN-NEXT31, Nov 17): BEAUTY-NOV17B pinning fact [P] and multiplicity

File `Nov15/PrefixPin.lean`, Mathlib only, kernel-only, axioms [propext, Classical.choice, Quot.sound], no sorry, 5 s / 2.0 GB.

Verdict: the paper statement is TRUE as written, once its hypotheses are made explicit. No counterexample.

- Model: a fixed interior+V program is affine on the {0}-exit rows, `Final = A*Exit + B*Inj` (`Final` def); `Inj` = rows born later, fixed.
- `exit_unique` / `exit_formula`: A invertible => `Exit = A^-1 (Final - B Inj)`, so equal finals give equal exits (whole rows, hence the W0 block, `w0_block_unique`).
- `prefix_unique`: if the loaded G0 rows X0 have a left inverse (span G0), the prefix M itself is pinned.
- `free_mix_not_unique`: the pin needs V FIXED. With the V mix existential (HubSettle.Valid / prefix_gauge: U0*M = G*V0, G free) exits are not unique. Pinned only given V and the interior.
- Hypotheses the card should state: (1) A_rest invertible (true when every op is a row op/scale/swap, false with overwrites or clears); (2) ALL registers' finals are fixed targets, not just V-enders; (3) `Inj` fixed.
- Multiplicity: `rank_le_nnz` (rank <= number of nonzero entries); `loaded_pairs_ge_ports`: F0 = A*R0, rank F0 >= p => nnz R0 >= p (p = 104 as hypothesis). `nnz_can_exceed`: all-ones n x n has rank <= 1, nnz n^2.
- Caveat for §2 wording: what the terminal labels force is a RANK >= p of the W0 block, not an entry count of 104. The "134x" compares nnz (13,906 pairs) with rank, which is basis-dependent; nnz >= rank only. A rank-104 block could have far fewer nonzeros in another basis, but the pin (R0 = A^-1 F) fixes the basis once V and the interior are fixed. So 134x measures "excess over the best possible basis", not excess rank.
