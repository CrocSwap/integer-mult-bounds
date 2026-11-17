# WFCount.lean / WFUp.lean / WFSlack.lean: whole-floor counting lemmas
No sorry; each file 4-6 s, ≤ 1.9 GB. Axioms [propext, Classical.choice, Quot.sound]. Build order WFCount (olean) → WFUp, WFSlack.

**Model.** TokenCancel ops; `LegalEvW Own`: co-presence, births/INITs of absent registers, public (`¬Own i`) MOVEs go to a chart `≥` the old one, owned MOVEs go anywhere. Generators for a chart region `D`: `gens P B` = unit rows of births at charts with `B c` + the row (at the moment) of every register MOVEd across a pair `P c0 c`. `Gen.entry` tags entries.

**WFCount.lean.**
- `cov_step`, `cov_run`, `CS_run` ("Chart span CS"): if `P` ⊇ (outside→D), `B` ⊇ D, every row ever at a chart in `D` lies in `gspan (gens P B)`. No order or ownership used. ADD/SCALE/COPY inside one chart, INIT zero, CLEAR only removes.
- `born_mem_gens`, `gens_birth`, `entry_gen_own`: generator bookkeeping; entries are owned when `P` excludes ascents.
- `descent_count` (down-set descent lemma, abstract count form): regions `D q` (q ∈ ι, Fintype), linear `π` killing every birth row born inside any `D q`, and for each q a register finally at `D q` with `π(row) = δ_q`. Then `#entries ≥ |ι|` (rank argument: the δ_q lie in `span π(entry rows)`). `descent_entries_owned`: for down-closed `D q` with ascending public moves every such entry is OWNED. With the clique of 8 pairwise-odd ports this is the "≥ 8 descents".

**WFUp.lean (up-set entry lemma UE).** `stay_step/stay_run`: a public register in an up-closed U stays in U. `pub_gens`: public generators (births in U, entries into U) are at distinct registers, each absent from U before and in U at the end. `up_entry`: with F = span of the final rows of the public residents (assumed linearly independent: "the target is invertible") and Bsp = span of the unit rows of registers born in U, `dim(F + Bsp) ≤ dim F + #owned generators`, i.e. `#owned (births in U + entries into U) ≥ def(U)`.

**WFSlack.lean (slack rank).** `slack_decomp` (pure linear algebra): `F, E ≤ I`, `F ∩ E = 0` ⇒ ∃ Kc, `I = F ⊕ E ⊕ Kc`, `dim Kc + dim F + dim E = dim I`. `slack_rank_model`: with `I = gspan(gens)` (CS: contains every row ever at D), F ≤ final rows at D, E ≤ birth rows, and `#gens ≤ dim F + dim E + σ`, `dim Kc ≤ σ`.

**NOT covered.** (1) The count identity `#gens = dim(F⊕E) + s_C + o_C` (passers) enters `slack_rank_model` as the hypothesis `hcount` (needs "each public enters a chart at most once", i.e. a PartialOrder plus strict ascent). (2) Independence of finals/E_BL (a fact about the target: data). (3) The Port lemma / Y-side theorem Σσ ≥ 104 (needs the port/ODD structure; not attempted). (4) κ ceilings, D0 floors, the numerics. (5) In `up_entry` owned births in U count as owned generators; the paper counts only owned MOVE-entries, so the paper's bound needs "no owned register is born in U" (not stated there). (6) `up_entry` uses non-strict ascent (a superset of the paper's strict MOVEs). No statement of the notes proved here was found false.
