<!-- Verbatim from the mixing hand-off ($SP/mixpkg/handoff/BIT-LABEL-LEMMA.md). The construction does not depend on the stage count; see PROOF.md section 6 for the eleven-stage composition. -->
# Target-prefix mixing on the R740 bit word

## Construction

Input: PR443's R740 rank138 bit word `../e8-r740-replica32/data/word.json.gz`, which is the word of PR444.
In its B phase, targets only receive helper registers. Helpers are not modified in B. Each target t climbs a nested
chain of frames 0 ⊂ T1 ⊂ … ⊂ t^⊥ and receives registers at those frames.

A π-coset partner pair (t, w) of a Hamming block receives the same three registers D4(c^), M(p5) and N. They are
received at the same frames of dimensions 4, 5 and 6, and the dimension-6 frame is t^⊥ ∩ w^⊥.
`code/mixgen.py` selects a receiver u and a donor w with these properties:
- they share a frame G of w's chain;
- the F₂ sum of the registers u receives at frames inside G equals the F₂ sum that w receives there;
- u's later frames all contain G.

The selection is a deterministic greedy pass by climb-cost saving. Donors keep their own chains, and there are no cycles.
For each receiver the word is changed in three places:

1. **D phase (frame 0):** add y_u += y_w after w's own D gates. This is the frame-0 preconditioner.
2. **Centre scatter:** set scatter_u := scatter_u ⊕ scatter_w.
3. **B phase:**
   - drop u's deliveries at frames inside G;
   - add y_u += y_w at frame G, after w's deliveries inside G and before any of w's deliveries above G.

   B is re-listed by frame dimension. This is legal because helpers are constant during B.

Sources, helpers, R, every start and final frame, and the A and C phases are byte-identical to the parent. The result
has 46 receivers: 42 mix at dimension 6 and 4 at dimension 5. A receiver's climb 0 → 4 → 5 → 6 (or 0 → 5 → 6) becomes
the single step 0 → 6, so the local paid profile loses small children:
{1:2530, 2:1008, 3:280, 4:347, 5:118, 7:14, 8:9} → {1:2460, 2:1012, 3:276, 4:315, 5:108, 6:42, 7:14, 8:9}.
Rank mass is unchanged, since every target still climbs 0 → 7.

## Scalar identity

Write y_w(τ) for the content of y_w at the time τ of the mix. It is
y_w⁰ + D_w s + P_w + scatter_w(x) + X_w(G),
- y_w⁰ is the input;
- D_w s is w's frame-0 dirt compensation;
- P_w is w's own preconditioner, if w is itself a receiver;
- X_w(G) is the F₂ sum of the registers w receives at frames inside G.

The preconditioner adds y_w⁰ + D_w s + P_w to y_u at frame 0. The corrected scatter adds scatter_w. The mix adds
y_w(τ). Each of these terms then cancels in pairs, and X_w(G) = X_u(G) replaces exactly the deliveries u dropped. So
every receiver ends with the parent's value, y_u⁰ + x_u. All other registers are unaffected.

This is checked exactly, not inferred. `code/check_mix.py` replays all 980 F₂ columns (sources, target inputs and every
helper's dirt) with PR443's `e8core.replay`, and a second, independent identity replay. The parent word's own checkers
replay the same word again: PR266-lineage `legality` and `columns_h`/`columns_k4`, and PR443's global template and
audit. The checks reject four mutants:
- omitted preconditioners;
- omitted scatter correction;
- a mix at the full frame;
- omitted mix additions.

## Bit-label conjugation lemma (principal review point)

PR425 (§3, "Why the scalar argument lifts") argues as follows for complex labels.
- Fix a canonical label operator L(F) for each frame F.
- A climb A → B acts as L(B)L(A)⁻¹.
- A scalar addition between two registers that share the current label F commutes with their common L(F).

By induction through the stream, the whole program is the block-diagonal conjugation of its scalar matrix by the
current labels. The argument never uses the roles of the registers. PR425 applies it to target-to-target butterflies
with a frame-0 preconditioner.

**Lemma (bit labels).** Let the bit supplier's label at frame F act on every register stream by the same operator
Λ_F. This is the coordinate-projector form D_P of PR386/PR434, the form used for climbs and idle advances. Then an F₂
addition y_u += y_w between two target streams at a common frame G commutes with Λ_G ⊗ Λ_G. Hence the complete local
program equals the conjugation of its scalar matrix by the start and final labels. This holds exactly as for the
helper→helper and helper→target additions that the bit words already use.

*Proof sketch.* On the two streams the addition is the block matrix [[I, I], [0, I]] (target u's row gains w). Both
streams carry the same Λ_G, so (Λ_G ⊕ Λ_G)·[[I, I], [0, I]] = [[I, I], [0, I]]·(Λ_G ⊕ Λ_G). The induction over the
event stream is the inherited one. The frame-0 preconditioner is a common-label addition at frame 0. ∎

The lemma uses only that both operands are at the same frame. That is the condition every checker above enforces.
The new element for the bit supplier is a target used as an operand. The inherited bit checkers allow it:
- `e8core` exempts target operands from its source-span test;
- the PR266-lineage legality checker counts it as an ordinary common-frame ADD.

`check_mix.py` adds a stricter test: each operand target's integer x-support, from its deliveries, lies in the gate
frame. There are 0 violations.

What is not proved: that the physical bit label is a single operator per frame that acts identically on target
streams and helper streams. The parent's helper→target deliveries assume this, but it is stated nowhere for a target
used as an operand. This is the principal review point.

## Global composition

The R740 word keeps R, start frames and therefore every helper residual width. PR443's global template, bank
admission and residual isometries are regenerated freshly from the mixed word. PR444's idle-hosting selection is
reused unchanged: its windows depend only on the schedule, and its capacities only on the widths. Its independent
audit re-derives every window, owner and bank.

Target additions occur only inside the local invocation of the active pair. They therefore touch neither a hosted
family's untouched window (PR442 §2) nor the banks. Hosted stock (37,464 live families) and hosted residuals
(159,168) are unchanged.
