# StayRemove.lean: stay-removability rule
Kernel-only, standard axioms, no sorry, 5 s. Imports TCLemma, WFCount.

## Proved
- `stay_removable_necessary`: split helper h at chart c (state `st`, h at c); any continuation `post` of the new word that is ascending-legal, ND, reads h only at charts <= c, ends e_h-free  =>  `Held h c st`: EVERY holder of e_h sits at a chart <= c at the split moment. (= `held_run`, the engine of TC_last_read, applied to the continuation only; no condition on the prefix.)
- `stay_removable`: stationary form (h never moves again, so every read is at c via `loc_stationary`).
- `stay_removable_last_read`: via `TC_last_read`, holders sit inside R = chart of the LAST read of h, at every prefix (sharper than "inside c" when the last read is below c).

## Said at once: the rule is false as worded
A contact-architecture note word it for "public holders". `CE` (Lean): base word fully ascending (LegalA), h at chart 1 for exactly one moment; the split word (legal under LegalW with owned j) has the owned j clean the public receiver r at chart 2 (r -= j), DESCEND 2 -> 1 and read h there. Valid, ND, clean, reads of h at <= 1, yet at the (only) moment of the stay the PUBLIC receiver r holds e_h at chart 2, not inside 1 (`not_held`).
Corrected statement: holders (public AND owned) sit inside c, **unless the continuation contains an owned descent**. The hypothesis is `LegalA` on the continuation (ascending moves for ALL registers after the split). Owned descents cost S (down and up), as the note says informally, but the rule is not a pure public-holder rule.
"At some moment of the stay": the theorem is at the split moment, which may be any moment of the stay; the quantifier is over the splitter's choice.

## Not covered
Separability of cargo (b); sufficiency (that holders inside c can always be converted); pricing.
