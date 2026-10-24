# Unequal cycle fitting rigidity boundary

`PROOF.md` proves that every odd-cycle fitting matrix of rank exactly half
the total port width is locally an integral edge-channel form, over any field.
It then gives the smallest positive unequal-width C5 exception to general
edge/private rigidity over Q: total width seven, optimum rank four. With zero
widths allowed the separate smallest boundary is three.

This answers the unequal-width question of Nick Petalas PR5180, using the
rank theorem of JoyboyBrian PR5023 and crediting PR3248's earlier C5 argument.
Finite exact checks corroborate the written proof; no physical decoder or
multiplication bound is claimed. Run `python3.12 -B verify.py` from this folder.

See `PROOF.md` for the complete contract, costs, limitations and Open next questions.

## Open next questions

Classify odd-total optima outside half-total equality, starting with all
total-seven C5 profiles. Any physical consumer still needs a complete paid
basis-change, query, copy and restoration schedule.
