# INTERLEAVE (Nov 20, Opus, theory). Code: cc1.py (exact Fraction replay of t7669 + rank mod 2 primes), q1.py (rung ceilings via rg1).
How this differs from what came before: FEWSTOPS and GAPMAP measured t7669's own algebra. LANDSPAN's out-tree rows were left
void ("newborns copy hub content for free"). Here the question is a SPEC-level law about what can enter a chart.

## 0. Why HS/Net cannot see helpers [P]
In BankNC0.Net a helper is a field whose O-row is its own token. It has no partner, so cut_extras never gives it an extra. The only
extras come from main partner pairs, and every height-cut floor stops at 208·sep = 104h. A helper floor above that must use
register identity (one row per register, a chain of charts) and the lattice of subspaces. Lemma CC below does that.

## 1. Lemma CC (chart-clean) [P]
Setting: trace model (public registers start at their initial chart holding their own token, ascend strictly, ADD/SCALE need
co-location). Fix a chart F. Hypotheses:
(S) no public register has F as an intermediate stop;
(O) no owned register is ever at a chart ⊇ F;
(B) the final row of a register that arrives at F has no coordinate on the token of a register initial at F (true for P104:
    partner rows of mains, own tokens for helpers);
(I) public final rows are linearly independent (caller hminor).
Let A_F = the registers that MOVE into F. Then span{rows of A_F at arrival} = span{final rows of A_F}.
In particular every arrival row already lies in W_F := span(finals of the registers ending at F).
Proof. (a) Confinement: a register gains a coordinate on token e_B only through an ADD with a carrier at the same chart. Publics
ascend, and under (O) no owned register carries e_B below F. By induction every e_B-carrier sits at a chart ⊇ A_B. So rows
arriving into F (which come from charts strictly below F) have zero e_B-coordinate for every B initial at F.
(b) Induction over time: the row of any register currently at F lies in span(arrival rows so far ∪ tokens of F-initial
registers). ADD and SCALE at F act inside F, a MOVE in adds an arrival row, a MOVE out removes a register, and (O) rules out
owned registers. By (S), every register in A_F stays at F, so its final row is in that span. Projecting out the e_B coordinates
(zero on arrivals by (a), zero on these finals by (B)) gives finals(A_F) ⊆ span(arrivals). Each register arrives once, by strict
ascent. So |A_F| independent finals (I) lie in the span of |A_F| vectors, and the two spans are equal. ∎
[C] t7669 (cc1.py): 974 charts receive arrivals. 973 of them host an intermediate stop. The only stop-free one is V (dim 9,
1052 arrivals, owned registers visit but make no ADD there), and the identity holds there exactly.

## 2. Corollaries [P, under the hypotheses of §1 at the chart named]
- C1 (no free copy-couriers; this answers LANDSPAN's void O1/O2 rows): a helper K that copies hub content g (row e_K + g) and
  moves to a stop-free target chart F can deliver only if g ∈ W_F + span(e_K). Since W_F is spanned by the finals of the
  registers ending at F, g must carry those targets' own tokens. A target token leaves its target only at the target's earlier
  charts, and a carrier entering a stop-free chart cannot bring it in (CC again). So **every chart that receives new content
  hosts a stop** (a target stop, a stop at F, or a stop by the token carrier at the hub). "Births are not stops" no longer makes
  out-tree edges free.
- C2 (no cleanup at the top): V is never a stop, so if no owned ADD happens at V, every register arriving at V already holds a
  row in W_V = span(x-finals, helper tokens). Every x main must take its partner content below V, and every helper ending at V
  must finish its non-W_V cleanup before its last jump.
- C3 (per-port stop, even ports): for each s with q_s ∈ q_s^⊥ there is a stop on x_s, a stop on y_s, or a stop at some chart c
  with span(q_s) ⊆ c ⊆ q_s^⊥. This follows from C1/C2 by tracing the e_{y_s}/e_{x_s} carriers. The cheapest stop costs
  2−2^s (a climb-2 register), so this route alone gives 104(2−2^s) = 1.437 < 104h = 3.093 at s=.99. **No gain over HS by
  itself.**
- C4 (CONJ: interleave forced by cleanup): the strong per-helper form is NOT proved. The minimal no-stop-target courier is the
  SWAP-COURIER: it swaps with target T at T's lower chart (taking T's token), meets the source at a chart that holds the source
  port, exchanges, then swaps back at T's final chart. Order T, then source, then T. Exactly 1 stop (at the source chart), and
  no cleanup inside q_s^⊥ after x-gathering, because the target's own register is the clean carrier. So FEWSTOPS's [CONJ] is
  false as a law: cleanup does not force an x-then-y interleave. CC forces only a target-first, source, target-final order.
  DESIGN HINT: a swap-courier serves every target with the same final chart and every source on its chain at 1 stop. t7669's
  climb-9 helpers pay 4 stops.

## 3. Quantification (q1.py, rung formulas, #7113 caller, X=112)
| native floor | κ ceiling |
|---|---|
| 104h only (word_rung) | .0093453741 |
| CC per-port (C3) | no change (below HS) |
| S 865.58 + HS (LANDSPAN, premised; additive is CONJ) / max form | .0075768 / .0078006 |
| S 1029.6 (R8-mode in-tree) + HS / max | .0073154 / .0075236 |
| S 1189 (c5 out-charges) + HS / max | .0070783 / .0072729 |
CC is a SPEC-level replacement candidate for the false R8 premise ("births at {0}") in the out-tree rows. If the LANDSPAN DP is
rerun with the rule "every out-tree node hosts a stop" (C1), the premised S moves from 865.58 toward 1029.6–1189. Not yet
computed.

## Verdict
[P] Lemma CC plus corollaries C1–C3. [C] t7669 check. A word-universal helper floor above 104h is NOT proved. The conjecture's
strong form is refuted by the swap-courier (§2 C4).
Next: put C1 into ls5's in-tree/out-tree DP as a node-stop row (replacing R8), and price the out-tree nodes. Formalise CC in
Lean (short: span induction plus projection).
