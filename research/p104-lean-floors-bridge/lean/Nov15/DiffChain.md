# DiffChain.lean: REBUILD-V2 stage C difference chaining. No sorry, ~5 s
Lane LEAN-NEXT11, Nov 16. Source: ROUNDLOG "V2:" stage C. Axioms [propext, Classical.choice, Quot.sound]. Op model: TokenCancel's; delivery = `add j h q` (j += q·h).

- `run_recv`: if h is written only by ADDs in a window (`AddOnly`), then row_h(end) = row_h(start) + recv. Here recv = Σ a·row_source(read time) over the ADDs into h. "Pickable" means recv can be made to equal the wanted vector.
- `diff_chain`:
  - Hypotheses:
    - h ≠ j, k; q_j, q_k ≠ 0;
    - h holds v_j/q_j at the j-delivery (j's alpha-chain);
    - the window is AddOnly for h;
    - recv = v_k/q_k − v_j/q_j.
  - Conclusions:
    - j receives v_j;
    - k receives v_k (on top of whatever k holds);
    - h ends holding v_k/q_k, exactly the row k's dedicated helper would hold, so k's beta-chain runs unchanged;
    - every other row equals the window run's.
- G_k ⊇ G_j is a route/frame (cost and legality) condition. Row correctness does not need it; co-presence legality of the two deliveries is assumed as usual.

**Finding (prose too strong): `scale_breaks`.** A SCALE of h in the window breaks the rule. Example: h = e_2, deliver to j, h *= 2, pick e_3 − e_2 (the literal difference), deliver to k; k receives e_3 + e_2, not e_3.
Minimal fix: h is written only by ADDs between the deliveries (no SCALE/CLEAR/COPY into h). Alternatively, with SCALEs u, require recv = v_k/q_k − (Π u)·v_j/q_j.
