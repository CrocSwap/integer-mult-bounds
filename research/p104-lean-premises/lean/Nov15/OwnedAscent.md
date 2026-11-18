# OwnedAscent.lean: premise 6 (A6, owned ascent) narrowed. No sorry, 7 s / 1.9 GB RSS
Imports Nov15.FloorEndToEnd. 17 `#print axioms`, all [propext, Classical.choice, Quot.sound]. No sorry, no native_decide.

## Proved
1. **Cost symmetry.**
   - `rc T` = rank of the residual `T - 1` of a chart change. `rc_inv`: `rc T⁻¹ = rc T`, so a fall costs exactly what the rise between the same frames costs (`back_cost`). `rc_comp`: rank cost is subadditive under composition.
   - `price_symm`: if the compiled rank is `|dim b - dim a|` (hypothesis), the price of a→b and b→a coincide.
   - `mvCost` charges every MOVE `|Δdim|`; `cost_split`: charge = public share + owned share, an owned move is charged like a public one. `ownedCost_nonneg`: the owned share is never negative; `owned_ascent_charged`: an owned ascent costs ≥ 1 (given dim strictly monotone, true for nested spans).
2. **No credit.** `credit` is taken only for `r ∈ Pub` from endpoint dims (the pricer's rule: only public endpoints, `check.py`). `owned_no_credit`: owned register credit = 0, ascent or not. `invoice_eq`: invoice = (public paid - helper credit) + owned paid, with owned paid ≥ 0. So ascent only ever adds to the invoice.
3. **Conservativity.**
   - `LegalEvS` = strict verifier (owned moves must descend, public climb). `legal_of_S`: strict-legal ⇒ relaxed-legal. `AcceptedS.toAccepted`: strict-accepted ⇒ FloorEndToEnd `Accepted`. Hence EVERY FloorEndToEnd theorem (hOnce, class K, R1/α/β/u rows, `objective_le`) holds for strict words: the class-K floor proved on the relaxed class is also a floor for strict words (sample: `hOnce_strict`).
   - `public_unchanged`: the public-move clause is identical in both predicates; `legal_diff`: they differ only on owned ascents. FloorEndToEnd already used the relaxed predicate (l.51), so no floor in that file changes.

## Direction-based floors DO change (stated, not hidden)
`strict_no_owned_asc`: under strict legality the owned ascent charge is exactly 0. `W1_not_strict` / `W1_relaxed` / `W1_charge`: a 2-event word (INIT at the low frame, MOVE up) is relaxed-legal, strict-illegal, charge 1 with ascent charge 1. Floors that rest on "owned only descend" (owned-paid-56 #6315, eight-unit relay #6229, reader-497 #6257, surplus #6831, #6881 H6) do not transfer to the relaxed class. This is not a false statement; it is the scope those earlier notes already declared, now with a Lean witness. Nothing false found.

## What is narrowed and what stays assumed
Narrowed (now theorems, in the abstract model): rank cost is direction-free given invertible chart changes; owned ascents never earn credit and never lower the invoice; relaxed legality is a superset whose only extra words are owned ascents; relaxed-class floors imply strict-class floors.
Still assumed:
- **Admission** (premise scope note): the compiler/contract text (Theorem 1G, FINITE-PRECOMPILATION 258-268, 05-layers.tex:83) never mentions direction; whether the maintainer accepts owned rises on arbitrary contents, factorwise at every width, stays the declaration. The P112 precedent supports it, does not prove it.
- **Compiled rank = |Δdim|** for each chart pair: modelled as a hypothesis (`price_symm`); the Clifford compilation is not formalised (python: 2964 pairs, lowerup.py's 104 pairs + reverses). `rc` is a generic linear-algebra proxy (rank of `T - 1`), not the Pauli/Fourier rank.
- CLEAR at any frame under owned_erasure (premise 1, ClearCert).
- The dim function and nested spans are inputs; the 47 owned MOVEs of the word are not replayed here.
Net: the premise shrinks from "owned ascent is priced soundly and harmlessly" to "the contract admits owned ascent on arbitrary content" (a pure admission question). Pricing, credit and floor-compatibility are discharged.
