# WFPort.lean: PORT LEMMA, Y-side theorem, hcount discharged
Kernel-only (axioms propext/Classical.choice/Quot.sound), no sorry, 6 s, 1.9 GB. Imports WFSlack, WFUp (build WFUp.olean, WFSlack.olean first).

## Proved
- `hcount_full`, `slack_full`: **slack_rank_model's hcount is discharged.** For a convex region D (hypothesis `hconv`; any single chart in a partial order),
  `#gens <= dim F + dim E + sigma`, sigma = `slack` = `slackS` (public entrants not ending in D = passers) + `slackO` (owned generators). F = finals of public residents (independent: data), E = units of public born-and-leave registers.
  Needs `pub_nodup` (public generators sit at distinct registers; convexity + ascent), `gens_birth'`.
- `charge`: pi(F+E) <= span{delta_r : r in Bs}, Q disjoint from Bs, delta_q in pi(I_D) for q in Q  =>  |Q| <= slack. (pure rank)
- `port_entry` (**Port lemma**): chart H = q^perp with slack 0, pi(F+E) <= span delta_q, births in H have pi = 0, y ends in H with pi(row y) = delta_q  =>  a PUBLIC register enters H from c0 < H strictly,
  carrying lam*delta_q (lam != 0), its row at that moment lying in I_{c0}. (Junk cleaned before entry: every entry row has pi in span delta_q; the feeding chart contains delta_q in pi(I_{c0}).)
- `y_side` (**Y-side theorem**): ports q, port charts Hc q (injective antichain), per-chart data  =>  #ports <= sum_{C in T} sigma_C. `forced_stops`: sum sigma >= n, sum o <= m  =>  #passers >= n - m.
- `y_side_sum`: the bare counting step. `antichain_needed`: explicit counterexample without the antichain clause.

## Said at once: paper statements corrected
1. **Y-side Theorem needs the H_q to be an antichain.** Without it one unit of slack at a chart C = H_{q0} < H_{q1} serves both q0's own slack and q1's feeding slack; Sum sigma = 1 < 2 (`antichain_needed`). True in the paper's geometry (distinct q^perp of equal dimension), but the note never states it. Also needs (a) q not born strictly below q^perp (odd weight) and (b) Bs(q^perp) <= {q} as hypotheses (paper has them as data).
2. **o_C must count owned births, not only owned MOVEs into C.** An owned register born in C is a generator of I_C. `forced_stops` therefore needs m = #owned MOVEs + #owned births in the charts concerned.
3. slack_rank_model's hcount is exactly: all public registers are never INIT-ed (not needed: INIT creates no generator), public entries distinct (convex region + ascending public moves), and independence of finals (data). The identity is an inequality here (`<=`), which is all the rank bound needs.

## Not covered
- Independence of finals / F-E disjointness / pi(F+E) = span{delta_r: born at C} (target data); ports-odd-weight; numerics.
- Sum over owned counts <= #owned MOVEs + births (per-event bookkeeping) is the hypothesis `hm` of `forced_stops`, not proved.
- X2 side (dual) not attempted.
