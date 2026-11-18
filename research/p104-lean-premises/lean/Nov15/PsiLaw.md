# PsiLaw : rebuild RC8/RC9 psi findings in Lean
`Nov15/PsiLaw.lean`, imports HubSettle (olean). Kernel only, no sorry/native_decide; axioms within [propext, Classical.choice, Quot.sound]. 8 s, 2.0 GB.
Sources: internal notes lines 4-14, RC9.md lines 9-13 and 21-22.

## 1. One transform, one mix (RC8 l.4-6)
`mapRows_comp`: two hub prefixes compose into ONE coordinate change. `psi_two_conditions` (= HubSettle.valid_iff): hub-exact with prefix M iff (a) Rn0*M = Fn0 and (b) rowspan[Xn | X0 M] = rowspan[Rn | R0] (one invertible V mix, `vmixM_iff_span`). Gauge/GL(A) criterion: HubSettle.prefix_valid / prefix_formula (unchanged).

## 2. SPAN LAW (RC8 l.7-9, RC9 l.9-13)
- `span_strip_iff`: stripping w from one end row leaves the row span unchanged iff w in the OLD span AND in the NEW span. `span_law_necessary`: w in the span is necessary.
- `span_law_prefix` (prefix constraint): with a prefix M at which the native is exact, removing w=(w_n|w_0) from main r gives (w_n | w_0 M); a hub-only repair (same M, one V mix) exists iff that vector is in span(targets) = span(V-ending rows) and in the stripped span. `span_law_prefix_necessary`.
- **WORDING FIX (RC8 l.9 / the "iff" in the task)**: "repairable iff w in the G1 span" is only necessary. `span_law_not_sufficient`: one end row (1), w = (1): w in the span, stripped row is 0, no V settle. Corrected: iff w in old span and in stripped span (the main's own row must stay recoverable). RC8's own text says "only if", which is true.
- Carrier corollary (RC9 l.11-12): `unshed_forces_span`: a carrier whose V-end row is its target plus held content x forces x in span(targets). `unshed_inconsistent` / `shed_consistent` (Q, x outside span): unshed has no V settle, shed has one. `three_meetings`: a courier with content 0 at start and end delivering nonzero total contains, in order, pick, give (b != 0), pick/shed: >= 3 contacts. Consistent with TWO-STOP (Delivery.two_contacts_needed counts contacts with the main; here pick/shed are the x-holder meetings). Scope: abstract pick/give/shed model, content a scalar along x; legality (charts, co-presence) not modelled.

## 3. Exposed reads (RC8 l.10-11)
- `relation_obstruction`: right multiplication preserves row relations. `exposed_read_no_prefix` (TokenCancel model, 3 registers r,o,u, any field, q,a != 0): relocating `r += q*o` before a read `u += a*r` makes the end rows violate the relation a r - a q o - u = 0; no matrix M (invertible or not) maps old end rows to new.
- `add_swap` / `move_early`: the op commutes with later ADDs unless they READ r (j = r) or WRITE o (i = o); if all intervening events are such ADDs the relocated word has identical final state.
- **WORDING FIX (RC8 l.10)**: "pure G0-column operation ONLY if neither register is read between": reads of o (the source) are harmless (`add_swap` allows j = o); the obstruction is reads of r and writes to o. If the rc8e census counted reads of o as exposure it overcounts (not checkable here).
- Not formalised: the census (55/57, 1-31 reads), that the relocated op is a G0-only column op at {0}; the obstruction is shown at the end-row level for one reader, general lists would be induction of the same relation.
