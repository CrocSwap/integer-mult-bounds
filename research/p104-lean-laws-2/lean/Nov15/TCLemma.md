# TCLemma.lean: LEMMA TC (a cancel-bus note) in the TokenCancel op model
No sorry. ~5 s, 1.6 GB. Axioms [propext, Classical.choice, Quot.sound].

**Model.** TokenCancel's `Ev`/`St`/`step`/`run` (rows in initial-row coordinates). Charts carry a `Preorder` (`c ≤ R` = "c ⊆ R"). `LegalEvA`: co-presence; births/INITs of absent registers; EVERY move goes to a chart `≥` the old one (all registers public, i.e. "no owned register in the chain"); SCALE by a nonzero scalar. `NDEv`/`ND`: an event that overwrites a register `i ≠ h` (born, init, clear, copy into i) only does so when row_i[h] = 0 ("no CLEAR escape"). `Held h R s`: every `r ≠ h` with row_r[h] ≠ 0 sits at a chart `≤ R`.

**Theorems.**
- `held_back`: one-step backward invariant. Cases: add (the only non-trivial one: a support member enters only through a co-present partner already in the support, or through a read of h at chart ≤ R), move (ascent), scale (nonzero), born/init/clear/copy (ND).
- `held_run`, `TC_prefix`: if the run is `LegalA` + `ND`, every ADD with source `h` is at a chart `≤ R`, and the final rows of all `r ≠ h` have e_h-coefficient 0, then at EVERY prefix every register holding e_h is at a chart `≤ R`.
- `reads_le_last`, `TC_last_read`: with `R` = the chart of the last read of h (`pre ++ add i0 h a0 R :: post`, `post` free of reads of h), the read-bound hypothesis is automatic (h's chart only ascends: `loc_mono`), so the conclusion holds at every time step `k` of the run.
- `cancel_only_by_read`: an event driving row_r[h] from nonzero to zero is `add r j a c` with `j = h` or row_j[h] ≠ 0 (junk is cancelled only by reading h or a register already holding e_h content).

**Hypotheses, exactly.** (1) Final cleanliness (v = 0 off h): this is what makes the proof backward. (2) ND: needed; without it a CLEAR/COPY of a holder is the escape (the paper's "owned descents and CLEARs"). (3) All registers public (moves ascend) rather than "owned registers not in the chain"; an owned register is covered only if it never holds e_h. (4) Non-strict ascent suffices.

**NOT covered.** The census claim (0 violations in 30.8M checks) is data. Registers `r = h` (h's own row) are outside the support. Hubs z/V legality of TokenCancel is not used. Owned registers that DO carry e_h. The paper's corollary "a bus can only replace h by taking over its role" is prose (no formal notion of bus).

No paper statement was false here; the only implicit hypotheses made explicit are (1) and (2).
