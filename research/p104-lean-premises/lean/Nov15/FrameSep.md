# FrameSep.lean: SPEC7 frame-separation law + SPEC8 corollary 
Kernel-only, no sorry/native_decide, ~3 s / 1.5 GB, imports Mathlib only (does not need TokenCancel/TCLemma/W0Cancel: the law is purely about frames). Axioms [propext, Classical.choice, Quot.sound] (two theorems: [propext, Quot.sound]).

**Model.** Frames = submodules of V. `Route`: frame sequence f, flag `owned t` for step t->t+1; non-owned (public) steps satisfy f t <= f (t+1); owned steps arbitrary. "Holds x_a content" = frame contains u_a.

**Theorems.**
- `Route.exit_owned`: u in f a, u not in f b (a<=b) => an OWNED step s with u in f s, u not in f (s+1). (public routes never drop u.)
- `X_Y_never_share`: X public with u in f 0, Y frames <= W, u not in W => X.f s != Y.f t for all s,t (SPEC7 core; "below V" is automatic since W != V).
- `reader_never_meets_Y_after`: public P co-present with X at t0 => P.f t != Y.f t' for all t >= t0.
- `owned_landing_then_ascent`, `delivery_needs_ferry`, `landing_ne_final` (SPEC8): all owned MOVE destinations in D, F = Y's final frame (F <= W), F not in D, a register that ever held u sits in F at t => it took an owned MOVE to some d in D and climbed publicly with d < F strictly, i.e. it is a ferrying register, never an owned register at its landing frame.

**Scope / correction (stated at once).** SPEC7's "any public that ever reads X_a can never meet Y_a" is true only AFTER the read (its parenthetical "later frames contain u_a"). `meet_before_read_possible` (over Q x Q): a public helper has frame W = Y's frame at time 0, then reads X at time 1. The paper statement is not false (it says later), but the unqualified reading is; use the `_after` form.
Modelling limits: content is tracked by "frame contained u" along one register's history (direct holders; multi-hop taint through u-free registers not modelled); owned steps are assumed to land in D (every owned step is a MOVE with destination in D); CLEAR of content is not modelled.
